# Execution Backends

This repository contains at least one execution backend implementation: Spark 3.5.

Spark 3.5 executor

- Implementation: `packages/dqt-executor-spark35/src/dqt_executor_spark35/executor.py` (class `SparkExecutionEngine`).
- The executor is registered via `entry_points` in `packages/dqt-executor-spark35/pyproject.toml` as `dqt.executors` with the name `spark35`.

How to select an executor

- Provide an instance of the executor's config class to `DQRun.executor_backend`. For Spark use `SparkExecutionBackend(spark=your_spark_session)` from `dqt_executor_spark35.config`.

Execution modes supported

- The Spark executor compiles tests tagged as `execution_mode=PYTHON` into pyspark Column expressions and tests tagged as `execution_mode=SQL` into a SQL expression and then combines them.
- `run(scope=None, execution_mode=None)` on the executor allows limiting by scope and/or forcing a particular execution mode. See `SparkExecutionEngine._execute` for behavior.

Result materialization

- The executor supports three `Representation` options in `DQRun.options`: `INLINE`, `EXTERNAL`, `BOTH` (`packages/dqt-core/src/dqt/enums/dq_run_options_representation.py`).
  - `INLINE`: validation result is materialized inline with the input frame.
  - `EXTERNAL`: validation result is materialized in a separate external frame (unique keys required).
  - `BOTH`: both inline and external are returned.

Spark-specific details

- The Spark executor creates generated columns on the working DataFrame:
  - `_dq_row_id` (internal row id during execution)
  - `_dq_violations` (bitmask of failing bounds per row)
  - `_dq_run_uuid` (run id string)
  - `_dq_violations_sql` / `_dq_violations_py` (intermediate columns used during compilation)
- The bitmask uses the bind ordinal as the bit position (1<<ordinal) so multiple failing binds are combined into the integer mask.

Selecting a different executor

- Loaders use Python `entry_points` to find executors (see `packages/dqt-core/src/dqt/loaders.py`). If you install another executor package that exposes a `dqt.executors` entry point, it can be selected by setting `executor_backend` accordingly.
