# DQT Documentation

> **Data quality should run where your data runs.**

DQT is an open-source data quality framework for validating data directly where it is processed. It provides a unified API for defining data quality rules and executing them against data using engines such as PySpark, without requiring users to move data into a separate validation system.

## Why DQT?

Most data quality tools answer a simple question:

> **Did this dataset pass validation?**

DQT is designed to answer a more useful set of questions:

> Which rules failed?
> Which rows failed?
> How many rows failed each rule?
> Why did a particular row fail?
> What happened during previous executions?

DQT preserves row-level failure information using a compact violation representation. This allows a validation run to produce both aggregate test results and information that can later be used to identify and explain invalid records.

For example, given:

```python
@dqtest_column_level_spark
def positive_distance():
    return f.col("trip_distance") > 0
```

and a dataset containing:

```text
trip_id    trip_distance
-------    -------------
1          12.4
2          -3.2
3          7.1
```

DQT can retain the fact that row `2` violated `positive_distance`, while still producing an aggregate result such as:

```text
positive_distance
------------------
status: FAILED
failed_rows: 1
total_rows: 3
```

This distinction is central to DQT: **validation results are not only a report; they can also become data.**

## Open Philosophy

DQT is built around two principles: **reporting-agnostic validation** and **native tests**.

### Reporting-agnostic

DQT does not dictate where or how data quality results should ultimately be consumed.

A validation engine produces structured facts about the execution:

```text
test → status → failed rows → total rows
```

Those results can then be:

* displayed in a custom dashboard
* stored as data quality artifacts
* consumed by a pipeline
* used to quarantine invalid records
* integrated into an existing observability platform
* analyzed historically

The framework should not require users to adopt a particular UI, database, observability platform, or reporting model.

### Native tests

DQT aims to execute tests using the native capabilities of the underlying data engine.

For a Spark DataFrame, a test should become a Spark expression or Spark operation rather than requiring the entire dataset to be extracted into Python for validation.

Conceptually:

```text
DQT test definition
        │
        ▼
Execution backend
        │
        ▼
Native engine operation
        │
        ▼
Spark / Pandas / DuckDB / ...
```

This keeps data quality close to the data and allows the underlying engine to perform the work it is designed to perform.

## Row-Level Quality Information

One of DQT's distinguishing features is its row-level representation of validation failures.

Instead of producing only:

```text
Dataset: FAILED
```

DQT can retain something closer to:

```text
row 1001 → test_2, test_7
row 1002 → test_4
row 1003 → no violations
```

Internally, multiple test failures can be represented compactly as a bitmap. The representation is an implementation detail, but the user-facing result is simple: **a row can be associated with the tests it violated.**

This enables workflows such as:

```text
Validate
   │
   ├── Test-level metrics
   │
   ├── Passed rows
   │
   ├── Failed rows
   │
   └── Explain failures
```

## A Simple Example

A DQT workflow can look conceptually like this:

```python
suite = (
  DQSuite(name="nyc-taxi-2015-01")
  .bind_test(
      definition=valid_vendor_id,
      columns="VendorID",
  )
  .bind_test(
      definition=not_null,
      columns="VendorID",
  )
)

run = DQRun(
    suite=suite,
    executor_backend=SparkExecutionBackend(spark=spark),
    dataset=SparkDQDataset(uri="demo.nyc.taxi-2015", df=df),
)

result = run.run()
```

The exact API depends on the configured execution backend; the examples in this repository show the concrete usage.

The resulting validation can provide both aggregate information and row-level information.

## Architecture

DQT separates the definition of a quality rule from its execution and its persistence.

```text
                  DQT
                   │
          ┌────────┴────────┐
          │                 │
     Test Definitions    Test Suites
          │                 │
          └────────┬────────┘
                   │
             Execution Engine
                   │
        ┌──────────┼──────────┐
        │          │          │
      Spark      Pandas     DuckDB
        │
        ▼
   Validation Results
        │
   ┌────┴─────┐
   │          │
Metrics    Row-level
          violations
        │
        ▼
 Artifact / Reporting Layer
```

This separation allows execution and reporting/storage to evolve independently.

Start here:

- [Installation](docs/installation.md)
- [Getting Started](docs/getting-started.md)
- [Tests & Definitions](docs/tests.md)
- [Execution Backends](docs/execution.md)
- [Results & Row-Level Failures](docs/results.md)
- [Artifacts / Iceberg backend](docs/artifacts.md)
- [Explainability](docs/explainability.md)
- [Examples Index](docs/examples.md)
- [Benchmarking](docs/benchmarking.md)
- [Benchmark Results (NYC Taxi - DQT vs GX)](docs/benchmark-results.md)
