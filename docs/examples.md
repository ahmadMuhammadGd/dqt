# Examples Index

This repository contains a small set of examples and a benchmark harness. Below is a short description of each example and how to run it.

- `examples/spark/simple` — minimal Spark-based example demonstrating:
  - defining column-level pyspark tests: [examples/spark/simple/tests.py](../examples/spark/simple/tests.py)
  - binding tests into a suite: [examples/spark/simple/suite.py](../examples/spark/simple/suite.py)
  - running a `DQRun` with `SparkExecutionBackend` and `LocalIcebergArtifactBackend`: [examples/spark/simple/run.py](../examples/spark/simple/run.py)

  How to run:

  ```bash
  python examples/spark/simple/run.py
  ```

  Requirements: `pyspark` installed and a working Java runtime for Spark.

- `benchmark/spark/NYC_Taxi_2015` — benchmark harness comparing DQT and Great Expectations on a configurable subset of the NYC taxi dataset. Files include:
  - `dataset.py` — builds a Spark session and reads CSV from `YELLOW_TAXI_2015_CSV` environment variable.
  - `run_dqt.py` — prepares DQT suite/runner for the dataset.
  - `run_gx.py` — prepares a Great Expectations validator for the dataset.
  - `run_benchmark.py` — orchestrates warmups, iterations, collects timings, writes `results.csv` and `benchmark.png`.

  How to run:

  ```bash
  export YELLOW_TAXI_2015_CSV=/path/to/yellow_tripdata_2015.csv
  python benchmark/spark/NYC_Taxi_2015/run_benchmark.py
  ```

  Requirements: `pyspark`, `great_expectations` (for the GX side), and `matplotlib` for plotting.

Notes:

- Examples are intentionally small and runnable from a local Spark context. The benchmark expects a large CSV and tuned Spark driver settings (see `dataset.py`).
