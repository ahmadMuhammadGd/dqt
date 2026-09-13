from pyspark.sql import DataFrame
from pyspark.sql import functions as f

from dqt.definitions import DQSuite
from dqt.resolvers import (
    bitmap_size,
    test_bind_to_bitmap_position,
)
from dqt_executor_spark35.config import (
    SparkExecutionBackend,
    _EXECUTOR_NAME,
)
from dqt_executor_spark35.types import DQSparkExecutionResults

from dqt.enums import (
    DQExecutionMode,
    DQTestScope,
    DQTestStatus,
)
from dqt.enums.dq_run_options_representation import Representation
from dqt.execution import DQTestResult
from dqt.runtime import DQRun
from dqt.definitions.dq_test_bind import DQTestBind
from dqt.abc import ExecutionEngine
from dqt.utils import filter_by_execution_mode, filter_by_scope

TYPE_TO_BITS: dict[str, int] = {
    "boolean": 1,
    "byte": 8,
    "short": 16,
    "int": 32,
    "long": 64,
    "float": 32,
    "double": 64,
    "char": 16,
}


class SparkExecutionEngine(ExecutionEngine[DataFrame]):
    executor_name = _EXECUTOR_NAME

    def __init__(
        self,
        run: DQRun[
            SparkExecutionBackend,
            DataFrame,
            DQSparkExecutionResults,
        ],
    ):
        self._VIOLATIONS_DTYPE = "long"

        self.dq_run = run
        self.suite = run.suite

        self._bits_per_element = TYPE_TO_BITS[self._VIOLATIONS_DTYPE]
        self._array_size = bitmap_size(
            self.suite,
            self._bits_per_element,
        )

        self._VIOLATIONS = "_dq_violations"
        self._VIOLATION_COUNT = "_dq_violation_count"
        self._RUN_UUID = "_dq_run_uuid"

        self._SQL = "_dq_violations_sql"
        self._PY = "_dq_violations_py"

        self.spark = run.executor_backend.spark
        self.cache_storage_level = run.executor_backend.cache_storage_level

        self.df: DataFrame = self._preprocess_df(run.dataset.df)

    def _zero_bitmap(self):
        return f.array_repeat(
            f.lit(0).cast(self._VIOLATIONS_DTYPE),
            self._array_size,
        )

    def _preprocess_df(self, df: DataFrame) -> DataFrame:
        return df.withColumns(
            {
                self._PY: self._zero_bitmap(),
                self._SQL: self._zero_bitmap(),
                self._RUN_UUID: f.lit(str(self.dq_run.uuid)),
            }
        )

    def _bitmap_with_violation(
        self,
        bitmap_col,
        ordinal: int,
        violation,
    ):
        """
        Set the bit corresponding to `ordinal` when `violation` is true.

        Spark arrays are immutable, so this creates a new array with exactly
        one element updated.
        """
        array_loc, element_loc = test_bind_to_bitmap_position(
            ordinal,
            self._bits_per_element,
        )

        mask = f.lit(1 << element_loc).cast(self._VIOLATIONS_DTYPE)

        current = f.element_at(
            bitmap_col,
            array_loc + 1,  # Spark arrays are 1-based
        )

        updated = current.bitwiseOR(
            f.when(
                violation,
                mask,
            ).otherwise(f.lit(0).cast(self._VIOLATIONS_DTYPE))
        )

        return f.transform(
            f.sequence(
                f.lit(0),
                f.lit(self._array_size - 1),
            ),
            lambda i: f.when(
                i == array_loc,
                updated,
            ).otherwise(f.element_at(bitmap_col, i + 1)),
        )

    def _compile_pyspark_plan(
        self,
        test_binds: list[DQTestBind],
    ):
        test_binds = filter_by_execution_mode(
            test_binds,
            DQExecutionMode.PYTHON,
        )

        if not test_binds:
            return self.df

        violations = self._zero_bitmap()

        for test_bind in test_binds:
            if isinstance(test_bind.columns, tuple):
                test = test_bind.definition.fn(
                    *test_bind.columns,
                    **test_bind.test_kwargs,
                )
            elif isinstance(test_bind.columns, dict):
                test = test_bind.definition.fn(
                    **test_bind.columns,
                    **test_bind.test_kwargs,
                )
            else:
                raise TypeError(
                    f"Unsupported columns type: " f"{type(test_bind.columns)!r}"
                )

            violation = ~test

            violations = self._bitmap_with_violation(
                violations,
                test_bind.ordinal,
                violation,
            )

        return self.df.withColumn(
            self._PY,
            violations,
        )

    def _compile_sparksql_plan(
        self,
        test_binds: list[DQTestBind],
    ):
        test_binds = filter_by_execution_mode(
            test_binds,
            DQExecutionMode.SQL,
        )

        if not test_binds:
            return self.df

        self.df.createOrReplaceGlobalTempView("_df")

        bitmap_exprs = []

        for array_loc in range(self._array_size):
            element_exprs = []

            for test_bind in test_binds:
                bind_array_loc, element_loc = test_bind_to_bitmap_position(
                    test_bind.ordinal,
                    self._bits_per_element,
                )

                if bind_array_loc != array_loc:
                    continue

                mask = 1 << element_loc

                if isinstance(test_bind.columns, tuple):
                    test_expr = test_bind.definition.fn(
                        *test_bind.columns,
                        **test_bind.test_kwargs,
                    )
                elif isinstance(test_bind.columns, dict):
                    test_expr = test_bind.definition.fn(
                        **test_bind.columns,
                        **test_bind.test_kwargs,
                    )
                else:
                    raise TypeError(
                        f"Unsupported columns type: " f"{type(test_bind.columns)!r}"
                    )

                element_exprs.append(f"""
                    CASE
                        WHEN NOT ({test_expr})
                        THEN CAST({mask} AS BIGINT)
                        ELSE CAST(0 AS BIGINT)
                    END
                    """)

            if element_exprs:
                bitmap_exprs.append("(" + " | ".join(element_exprs) + ")")
            else:
                bitmap_exprs.append("CAST(0 AS BIGINT)")

        bitmap_sql = ", ".join(bitmap_exprs)

        sql = f"""
        SELECT *,
            array({bitmap_sql}) AS {self._SQL}
        FROM global_temp._df
        """

        return self.spark.sql(sql)

    def _or_bitmaps(self, left, right):
        """
        Element-wise bitwise OR of two violation bitmaps.
        """
        return f.zip_with(
            left,
            right,
            lambda x, y: x.bitwiseOR(y),
        )

    def _run(
        self,
        py_df: DataFrame,
        sql_df: DataFrame,
    ):
        """
        Combine Python and SparkSQL violation bitmaps.

        Both plans operate on the same original rows, so no row-id join
        is necessary.
        """
        return py_df.withColumn(
            self._VIOLATIONS,
            self._or_bitmaps(
                f.col(self._PY),
                f.col(self._SQL),
            ),
        ).drop(
            self._PY,
            self._SQL,
        )

    def _calculate_test_results(
        self,
        df: DataFrame,
    ):
        try:
            if self.cache_storage_level:
                _df = df.persist(
                    storageLevel=self.cache_storage_level,
                )
            else:
                _df = df

            total_count = _df.count()

            agg_exprs = []

            for test_bind in self.suite.test_binds:
                array_loc, element_loc = test_bind_to_bitmap_position(
                    test_bind.ordinal,
                    self._bits_per_element,
                )

                mask = 1 << element_loc

                element = f.element_at(
                    f.col(self._VIOLATIONS),
                    array_loc + 1,
                )

                agg_exprs.append(
                    f.sum(
                        f.when(
                            element.bitwiseAND(f.lit(mask).cast(self._VIOLATIONS_DTYPE))
                            != 0,
                            1,
                        ).otherwise(0)
                    ).alias(str(test_bind.ordinal))
                )

            _agg = _df.agg(*agg_exprs).first()

            result = []

            for test_bind in self.suite.test_binds:
                violation_count = _agg[str(test_bind.ordinal)] or 0

                if total_count == 0:
                    fail_percentage = 0.0
                else:
                    fail_percentage = violation_count * 100 / total_count

                status = (
                    DQTestStatus.PASS
                    if float(fail_percentage) <= float(test_bind.threshold_pct)
                    else DQTestStatus.FAILED
                )

                result.append(
                    DQTestResult(
                        bind_uuid=test_bind.uuid,
                        test_definition_name=test_bind.definition.name,
                        status=status,
                        failed_rows=violation_count,
                        total_rows=total_count,
                    )
                )

            return result

        finally:
            if self.cache_storage_level:
                _df.unpersist()

    def _execute(
        self,
        scope: DQTestScope | None = None,
        execution_mode: DQExecutionMode | None = None,
    ):
        test_binds = filter_by_scope(
            self.suite.test_binds,
            scope=scope,
        )

        if execution_mode == DQExecutionMode.PYTHON:
            return self._compile_pyspark_plan(test_binds)

        if execution_mode == DQExecutionMode.SQL:
            return self._compile_sparksql_plan(test_binds)

        py = self._compile_pyspark_plan(test_binds)
        sql = self._compile_sparksql_plan(test_binds)

        return self._run(py, sql)

    def _materialize(self, df):
        external = df.select(
            *(
                f.col(c)
                for c in (
                    *self.dq_run.dataset.unique_keys,
                    self._RUN_UUID,
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
        df = self._execute(
            scope,
            execution_mode,
        )

        test_results = self._calculate_test_results(df)

        inline, external = self._materialize(df)

        self.dq_run.set_finished_at()

        return (
            DQSparkExecutionResults(
                test_results=test_results,
            )
            .set_inline_results(inline)
            .set_external_results(external)
            .set_passed_rows(
                df.filter(
                    f.aggregate(
                        f.col(self._VIOLATIONS),
                        f.lit(True),
                        lambda acc, x: acc & (x == 0),
                    )
                )
            )
            .set_failed_rows(
                df.filter(
                    f.aggregate(
                        f.col(self._VIOLATIONS),
                        f.lit(False),
                        lambda acc, x: acc | (x != 0),
                    )
                )
            )
        )

    def explain(
        self,
        df,
        run_id_bind_map,
    ):
        bind_data = [
            (
                run_id,
                test_name,
                *test_bind_to_bitmap_position(
                    bit_position,
                    self._bits_per_element,
                ),
            )
            for run_id, test_name_bind in run_id_bind_map.items()
            for test_name, bit_position in test_name_bind
        ]

        expr = f.array(
            f.when(
                (f.col(self._RUN_UUID) == run_id)
                & (
                    f.element_at(
                        f.col(self._VIOLATIONS),
                        array_loc + 1,
                    ).bitwiseAND(f.lit(1 << element_loc).cast(self._VIOLATIONS_DTYPE))
                    != 0
                ),
                f.lit(name),
            )
            for run_id, name, array_loc, element_loc in bind_data
        )

        return df.withColumn(
            "dq_explain",
            f.filter(
                expr,
                lambda x: x.isNotNull(),
            ),
        )

    def get_run_ids(self, df):
        return {
            row[self._RUN_UUID]
            for row in (df.select(self._RUN_UUID).distinct().collect())
        }
