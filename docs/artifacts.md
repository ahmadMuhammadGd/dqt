# Artifact Storage (Iceberg backend)

Why artifact storage exists

- Artifact storage persists analytical metadata and run results so you can query historical runs, build dashboards and perform explainability that ties a run's failing-bitmask back to test names and binds.

Iceberg artifact backend implementation

- Implementation lives in `packages/dqt-artifact-iceberg`.
  - Persist class: `dqt_artifact_iceberg.persist:IcebergArtifactBackendPersist` (registered as `dqt.artifacts` in `pyproject.toml`).
  - Backend config classes: `dqt_artifact_iceberg.backends` (local, s3, nessie, rest stubs).

What gets persisted

- The persister creates an `AnalyticalMart` from a `DQRun` and appends rows for the following logical tables (see `packages/dqt-core/src/dqt/analytical`):
  - `dim_dataset`
  - `dim_suite`
  - `dim_test`
  - `dim_test_bind`
  - `fact_run`
  - `fact_test_results`

How it's configured

- Example in [examples/spark/simple/run.py](../examples/spark/simple/run.py):

```py
dq_run = DQRun(
    suite=my_suite,
    dataset=dataset,
    executor_backend=SparkExecutionBackend(spark=spark),
    artifact_store_backend=LocalIcebergArtifactBackend(),
)

dq_run.run()
dq_run.persist()
```

- `LocalIcebergArtifactBackend` is a convenience backend that uses a `file://` warehouse in the current working directory and a sqlite catalog file (see `packages/dqt-artifact-iceberg/src/dqt_artifact_iceberg/backends/local.py`).

Reading persisted artifacts

- The `IcebergArtifactBackendPersist.persist` method writes pyspark/pyarrow rows into pyiceberg tables (creating namespace and tables if necessary). Once persisted, you can query those tables using pyiceberg APIs or any tool that can read Iceberg tables from the configured catalog/warehouse.

Limitations / Notes

- The repository-provided `IcebergArtifactBackendPersist` implements `persist(run)` and writes analytical tables but does not provide a high-level `get_binding()` method. Some helper code (e.g., `DQExplainer`) expects an artifact store interface that can return bindings; to perform explainability from persisted artifacts you must query the persisted tables and build a run-id → bind mapping yourself (see Explainability doc).
