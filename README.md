# DQT Documentation

DQT is an open-source data quality framework for validating data directly where it is processed. It provides a unified API for defining data quality rules and executing them against data using engines such as PySpark, without requiring users to move data into a separate validation system.

Unlike traditional validation approaches that primarily report whether a dataset passed or failed a collection of checks, DQT is designed to preserve row-level failure information. Each row can carry a compact representation of the tests it violated, allowing users to identify failed records, calculate test-level metrics, and later explain exactly which rules failed for a particular row.

DQT follows an open philosophy around data quality. It is designed to be reporting-agnostic: validation should produce facts about the data rather than force those facts into a particular reporting, observability, or storage system. Test execution produces structured results that can be consumed by downstream systems, persisted as artifacts, or used to build custom reporting and remediation workflows.

DQT also favors native tests. A data quality rule should execute using the capabilities of the underlying data engine rather than requiring data to be extracted into a separate validation environment. For example, when validating a Spark DataFrame, DQT can express the test as Spark-native operations and allow Spark to execute them. This keeps validation close to the data and allows quality checks to benefit from the execution engine's optimization and scalability.

This documentation covers installation, getting started, core concepts, execution backends, results, artifact storage, explainability, examples and benchmarking for the DQT repository in this workspace.

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
- [Benchmark Results (NYC Taxi)](docs/benchmark-results.md)
