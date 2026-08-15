# Tests & Definitions

This document describes the test-definition API actually implemented in the repository.

Core classes (see source):

- `DQTest` — `packages/dqt-core/src/dqt/definitions/dq_test.py`.
  - `name`, `fn` (callable), `scope` (row or column), `engine` (optional string), `execution_mode` (PYTHON or SQL).
  - Computed properties: `test_implementation`, `description`, `uuid`.

- `DQTestBind` — `packages/dqt-core/src/dqt/definitions/dq_test_bind.py`.
  - Binds a `DQTest` to columns with `threshold_pct`, `columns`, `ordinal`, `severity`, and `test_kwargs`.
  - Computed `uuid` for the bind includes definition uuid, threshold, columns and ordinal.

- `DQSuite` — `packages/dqt-core/src/dqt/definitions/dq_suite.py`.
  - Holds `test_binds` and provides `bind_test(definition, columns, threshold_pct=0, test_kwargs={})` which appends a `DQTestBind` and returns the suite for fluent chaining.

Decorators and test creation

- The package exposes convenience decorators which wrap a Python callable into a `DQTest` instance. For example `dqtest_column_level_spark` is provided by `dqt_executor_spark35.decorator` and ultimately uses `dqt.decorators.dqtest` to create a `DQTest`.

Execution modes and scopes

- Execution mode values (source): `packages/dqt-core/src/dqt/enums/dq_execution_mode.py` — `PYTHON`, `SQL`.
- Test scope values (source): `packages/dqt-core/src/dqt/enums/dq_test_scope.py` — `ROW_LEVEL`, `COLUMN_LEVEL`.

Test parameters and thresholds

- `DQTestBind.threshold_pct` controls pass/fail decision in the executor (compare failed_pct against threshold).
- `test_kwargs` are forwarded to the test definition callable when the executor compiles/executes the plan.

Notes

- Only behaviors implemented in the code above are documented here. For example, decorators in the executor packages (`dqt_executor_spark35`) expose executor-specific wrappers (SQL vs Python test creation) — see `packages/dqt-executor-spark35/src/dqt_executor_spark35/decorator.py`.
