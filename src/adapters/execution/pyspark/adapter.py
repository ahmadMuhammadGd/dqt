try:
    from pyspark.sql import DataFrame
    from pyspark.sql import functions as f
except ImportError as e:
    raise RuntimeError("Spark support requires pyspark") from e

from datetime import datetime, timezone
from typing import Literal

from pyspark.sql.functions import monotonically_increasing_id

from adapters.execution.pyspark.config import SparkExecutionConfig
from adapters.execution.pyspark.types import DQSparkExecutionResults
from core.models.enums import DQExecutionMode, DQTestScope, DQTestStatus
from core.models.enums.dq_run_options_representation import Representation
from core.models.execution import DQRun, DQTestResult
from core.models.definitions.dq_test_bind import DQTestBind
from core.ports import ExecutionEngine
from core.utils import filter_by_execution_mode, filter_by_scope


class SparkDQExecutionEngine(ExecutionEngine):
    def __init__(self, run: DQRun[SparkExecutionConfig, DataFrame]):

        # generated column names
        self._VIOLATIONS = "_dq_violations"
        self._VIOLATION_COUNT = "_dq_violation_count"
        self._ROW_ID = "_dq_row_id"
        self._SUITE_UUID = "_dq_suite_uuid"
        self._SQL = "_dq_violations_sql"
        self._PY = "_dq_violations_py"

        # violations dtype
        self._VIOLATIONS_DTYPE = "long"

        self.dq_run = run
        self.suite = run.suite
        self.spark = run.execution_backend_config.spark
        self.storage_level = run.execution_backend_config.persist__storage_level
        self.df: DataFrame = self._preprocess_df(run.dataset.df)

    def _preprocess_df(self, df):
        return df.withColumns(
            {
                self._ROW_ID: monotonically_increasing_id(),
                self._PY: f.lit(0).cast(self._VIOLATIONS_DTYPE),
                self._SQL: f.lit(0).cast(self._VIOLATIONS_DTYPE),
                self._SUITE_UUID: f.lit(self.suite.uuid),
            }
        )

    def _compile_pyspark_plan(self, test_binds: list[DQTestBind]):
        _test_binds = filter_by_execution_mode(test_binds, DQExecutionMode.PYTHON)
        if not _test_binds:
            return self._df

        _violations = f.lit(0).cast(self._VIOLATIONS_DTYPE)

        for test_bind in _test_binds:
            _col = test_bind.definition.fn(*test_bind.columns, **test_bind.test_kwargs)
            _violation = ~_col
            idx = test_bind.ordinal
            mask = f.lit(1 << idx).cast(self._VIOLATIONS_DTYPE)

            _violations = _violations.bitwiseOR(
                f.when(_violation, mask).otherwise(f.lit(0))
            )

        return self.df.withColumn(self._PY, _violations)

    def _compile_sparksql_plan(self, test_binds: list[DQTestBind]):
        _test_binds = filter_by_execution_mode(test_binds, DQExecutionMode.SQL)

        if not _test_binds:
            return self.df

        exprs = []

        for test_bind in _test_binds:
            idx = test_bind.ordinal
            mask = 1 << idx

            exprs.append(f"""
                CASE
                    WHEN NOT ({test_bind.fn(*test_bind.columns, **test_bind.test_kwargs)}) THEN CAST({mask} AS BIGINT)
                    ELSE CAST(0 AS BIGINT)
                END
            """)

        violation_expr = " + ".join(exprs) if exprs else "CAST(0 AS BIGINT)"

        sql = f"""
        SELECT *,
            ({violation_expr}) AS {self._SQL}
        FROM _df
        """

        self.df.createOrReplaceGlobalTempView("_df")
        return self.spark.sql(sql)

    def _run(self, py_df: DataFrame, sql_df: DataFrame):
        joined = py_df.select(*[c for c in py_df.columns if c != self._SQL]).join(
            sql_df.select(self._ROW_ID, self._SQL),
            on=self._ROW_ID,
            how="left",
        )

        return (
            joined.fillna({self._PY: 0, self._SQL: 0})
            .withColumn(self._VIOLATIONS, f.col(self._PY).bitwiseOR(f.col(self._SQL)))
            .drop(self._PY, self._SQL, self._ROW_ID)
        )

    def _calculate_test_results(self, df: DataFrame):
        try:
            _df = df.persist(storageLevel=self.storage_level)
            total_count = _df.count()
            result = []

            agg_exprs = []

            for test_bind in self.suite.test_binds:
                idx = test_bind.ordinal
                mask = 1 << idx

                agg_exprs.append(
                    f.sum(
                        f.when(
                            f.col(self._VIOLATIONS).bitwiseAND(
                                f.lit(mask).cast(self._VIOLATIONS_DTYPE)
                            )
                            != 0,
                            1,
                        ).otherwise(0)
                    ).alias(str(idx))
                )

            _agg = _df.agg(*agg_exprs).first()

            # only one row
            for test_bind in self.suite.test_binds:
                idx = test_bind.ordinal

                violation_count = _agg[str(idx)]

                if total_count == 0:
                    fail_percentage = 0.0

                else:
                    fail_percentage = violation_count * 100 / total_count

                status = (
                    DQTestStatus.PASS
                    if fail_percentage < test_bind.error_threshold_pct
                    else DQTestStatus.FAILED
                )

                result.append(
                    DQTestResult(
                        bind_uuid=test_bind.uuid,
                        status=status,
                        failed_rows=violation_count,
                        total_rows=total_count,
                    )
                )

            return result

        finally:
            _df.unpersist()

    def execute(
        self,
        scope: DQTestScope | None = None,
        execution_mode: DQExecutionMode | None = None,
    ):
        test_binds = filter_by_scope(self.suite.test_binds, scope=scope)

        if execution_mode == DQExecutionMode.PYTHON:
            df = self._compile_pyspark_plan(test_binds)

        if execution_mode == DQExecutionMode.SQL:
            df = self._compile_sparksql_plan(test_binds)

        if not execution_mode:
            py = self._compile_pyspark_plan(test_binds)
            sql = self._compile_sparksql_plan(test_binds)
            df = self._run(py, sql)

        df = df.withColumn(self._SUITE_UUID, f.lit(self.suite.uuid))

        return df

    def _materialize(self, df):
        external = df.select(
            *(
                f.col(c)
                for c in (
                    *self.dq_run.dataset.unique_keys,
                    self._SUITE_UUID,
                    self._VIOLATIONS,
                )
            )
        )

        match self.dq_run.options.representation:
            case Representation.INLINE:
                return df, None

            case Representation.EXTERNAL:
                return None, external

            case Representation.BOTH:
                return df, external

    def run(
        self,
        scope: DQTestScope | None = None,
        execution_mode: DQExecutionMode | None = None,
    ):
        df = self.execute(scope, execution_mode)

        test_results = self._calculate_test_results(df)

        inline, external = self._materialize(df)

        self.dq_run.set_finished_at()

        return (
            DQSparkExecutionResults(test_results=test_results, run=self.dq_run)
            .set_inline_results(inline)
            .set_external_results(external)
        )
