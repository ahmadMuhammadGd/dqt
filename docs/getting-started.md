# Getting Started

This quickstart uses the smallest example under `examples/spark/simple` to show how to define tests, create a suite, run DQT and inspect results.

- Example files:
  - [examples/spark/simple/tests.py](../examples/spark/simple/tests.py)
  - [examples/spark/simple/suite.py](../examples/spark/simple/suite.py)
  - [examples/spark/simple/run.py](../examples/spark/simple/run.py)

1) Define tests

Tests are standard Python callables decorated by executor-specific decorators. In the simple Spark example the tests are defined with `dqtest_column_level_spark` in [examples/spark/simple/tests.py](../examples/spark/simple/tests.py). Example (excerpt):

```py
@dqtest_column_level_spark
def not_null(x):
    "check for not null values"
    return f.col(x).isNotNull()
```

The decorator wraps the function into a `DQTest` definition (see `packages/dqt-core/src/dqt/definitions/dq_test.py`).

2) Create a suite

Bind tests to columns using `DQSuite.bind_test`. The example suite is in [examples/spark/simple/suite.py](../examples/spark/simple/suite.py):

```py
my_suite = (
    DQSuite(name="my_test_suite")
    .bind_test(definition=gender_must_be_f_or_m, columns=("gender"))
    .bind_test(definition=not_null, columns=("age"))
)
```

3) Run DQT

The `DQRun` object ties together the suite, dataset, executor backend and optional artifact backend. The example runner at [examples/spark/simple/run.py](../examples/spark/simple/run.py) shows a complete runnable example using a local Spark session and the local Iceberg artifact backend:

```py
dq_run = DQRun(
    suite=my_suite,
    dataset=dataset,  # SparkDQDataset(uri, df=DataFrame)
    executor_backend=SparkExecutionBackend(spark=spark),
    artifact_store_backend=LocalIcebergArtifactBackend(),
    options=DQRunOptions(representation=Representation.INLINE),
)

result = dq_run.run()
dq_run.persist()
```

4) Inspect validation results

- `result` is a `DQSparkExecutionResults` (`DQExecutionResult`). Use:
  - `result.get_inline_results()` — the inline validation dataframe (if representation is INLINE/BOTH)
  - `result.get_external_results()` — external representation (if representation is EXTERNAL/BOTH)
  - `result.get_passed_rows()` / `result.get_failed_rows()` — Spark DataFrames of passed/failed rows
  - `result.get_json_summary()` — JSON summary of test results

In the example runner the following calls print the inline/external dataframes and summary:

```py
if external := result.get_external_results():
    external.show()

if inline := result.get_inline_results():
    inline.show()

print(result.get_json_summary(indent=4))

result.get_passed_rows().show()
result.get_failed_rows().show()
```

5) Row-level failures

When using the Spark executor, the inline/external result frames include an integer column (a bitmask) that encodes which bound tests failed for each row. The Spark executor uses `_dq_violations` to store the bitmask and `_dq_run_uuid` to record the run identifier. The `explain` helper (see Explainability) converts the bitmask back to test names for rows.
