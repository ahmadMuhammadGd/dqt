# DQT Documentation

DQT is an open-source data quality framework for validating data directly where it is processed. It provides a unified API for defining data quality rules and executing them against data using engines such as PySpark, without requiring users to move data into a separate validation system.

Unlike traditional validation approaches that primarily report whether a dataset passed or failed a collection of checks, DQT is designed to preserve row-level failure information. Each row can carry a compact representation of the tests it violated, allowing users to identify failed records, calculate test-level metrics, and later explain exactly which rules failed for a particular row.

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
