# Explainability

is not implemented yet.

<!-- The repository includes a small `DQExplainer` helper (`packages/dqt-core/src/dqt/explaine/dq_explainer.py`) that bridges persisted artifact metadata and an execution engine's explanation functionality.

How `DQExplainer` works (source)

- `DQExplainer.__init__(artifact_store, execution_engine)` accepts an artifact-store object and an execution-engine instance.
- `DQExplainer.explain(df, run_id_col_name=None)` does the following:
  - determines the run id column name (default is the execution engine's `run_uuid_column_name`)
  - asks the execution engine to extract run ids present in the provided frame (`execution_engine.get_run_ids(df)`)
  - asks the artifact store for bindings for those run ids (`artifact_store.get_binding(run_ids)`) — a mapping of run_id -> list of `(test_name, bit_position)`
  - calls `execution_engine.explain(run_id_test_bind_map)` to obtain a frame with human-readable explanations added.

Practical notes for this repository

- The example Iceberg artifact persister (`packages/dqt-artifact-iceberg/src/dqt_artifact_iceberg/persist.py`) writes analytical tables but does not expose a `get_binding()` retrieval method. That means `DQExplainer` cannot directly use the provided Iceberg persister without a small adapter that reads the persisted tables and returns the required mapping.

How to get from persisted results to explanations

1. Query the persisted tables (e.g., `dim_test`, `dim_test_bind`, `fact_test_results`). These tables contain:
   - `dim_test` — tests with `test_uuid` and `name`
   - `dim_test_bind` — binds with `bind_uuid`, `test_uuid`, and `ordinal`
   - `fact_test_results` — run results with `run_uuid` and `bind_uuid`

2. Build a mapping of `run_uuid` -> list of `(test_name, ordinal)` by joining `fact_test_results` ➜ `dim_test_bind` ➜ `dim_test` and mapping ordinal (bit position) back to test name.

3. Pass the mapping into `execution_engine.explain(df, run_id_bind_map)` (Spark executor implements `explain`) to add an explanation column. For the Spark executor the `explain` method produces a `dq_explain` column containing an array of failing test names.

Example (conceptual):

- Use pyiceberg or another Iceberg client to query the persisted analytical tables for a specific `run_uuid` and construct the mapping. Then call the executor's `explain`.

Limitations

- This repository's iceberg persister writes the tables required for explainability but does not provide a one-call retrieval API. A small adapter that implements `get_binding(run_ids)` by querying the persisted tables will enable `DQExplainer` without further changes to the engine. -->
