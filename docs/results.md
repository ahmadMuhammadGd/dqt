# Results & Row-Level Failures

Result objects

- Individual test results are represented by `DQTestResult` (`packages/dqt-core/src/dqt/execution/dq_test_result.py`). Key fields:
  - `bind_uuid` — uuid of the bound test
  - `test_definition_name` — name of the test definition
  - `status` — `PASS` or `FAILED`
  - `failed_rows`, `total_rows` — counts
  - computed properties: `is_passed`, `failed_pct`, `success_pct`, `success_rows`

- The top-level run result is a `DQExecutionResult` (`packages/dqt-core/src/dqt/execution/dq_execution_result.py`). It contains:
  - `test_results: list[DQTestResult]`
  - getters and setters for inline/external frames and passed/failed row frames:
    - `set_inline_results()`, `get_inline_results()`
    - `set_external_results()`, `get_external_results()`
    - `set_passed_rows()`, `get_passed_rows()`
    - `set_failed_rows()`, `get_failed_rows()`
  - `get_json_summary(indent=4)` — JSON summary of the execution result

Row-level failure representation (Spark executor)

- The Spark executor encodes per-row failures in an integer bitmask stored in `_dq_violations`.
  - Each bound test has an ordinal (0-based) and the executor uses `(1 << ordinal)` to set bits for failed binds.
  - To find rows that failed any tests: filter on `_dq_violations != 0` (see `SparkExecutionEngine.run`).
- The run identifier is available on each row in `_dq_run_uuid` — this is used by explainability helpers to join persisted bindings to rows.

Accessing passed/failed rows

- For Spark runs the `DQSparkExecutionResults` contains `get_passed_rows()` and `get_failed_rows()` which return Spark DataFrames already filtered by failure mask (see `packages/dqt-executor-spark35/src/dqt_executor_spark35/executor.py`).

Interpreting the bitmask

- To get human-readable explanations use the executor's `explain(df, run_id_bind_map)` helper (Spark executor implements `explain`) which converts bitmask values into arrays of failing test names (see Explainability doc).
