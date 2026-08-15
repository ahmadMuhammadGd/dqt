# Benchmarking

Location: `benchmark/spark/NYC_Taxi_2015` — see files in that directory.

What is being benchmarked

- `run_benchmark.py` measures end-to-end validation execution time for two frameworks on the same Spark DataFrame:
  - DQT (`run_dqt.py` / `prepare_dqt` / `run_dqt`)
  - Great Expectations (`run_gx.py` / `prepare_gx` / `run_gx`)

Benchmark dataset

- The harness reads the real NYC Yellow Taxi CSV from the path provided by the environment variable `YELLOW_TAXI_2015_CSV` (see `dataset.py`) and limits the number of rows via `.limit(limit)` for the experiment sizes.

Workload and methodology

- The benchmark uses a list of row-count limits (see `LIMITS` in `run_benchmark.py`) from 10k to several million rows.
- Warm-ups and iterations:
  - `WARMUPS = 1` (a small number of warm-up runs)
  - `ITERATIONS = 5` (measured iterations per limit)

Key measurement differences

- DQT measurement: the DQT validator/run object is prepared once per limit and reused across measurement iterations — this represents repeated execution of the same `DQRun` instance.
- Great Expectations (GX) measurement: a fresh validator is created for every iteration (the code intentionally recreates the GX validator to avoid reuse of GX internal caches between iterations). Preparation is not timed; validation is.

What the benchmark measures

- The harness measures wall-clock seconds for the validation phase and writes summary statistics (`min`, `median`, `mean`) per framework and limit to `results.csv` and produces a plot `benchmark.png`.

How to run

```bash
export YELLOW_TAXI_2015_CSV=/path/to/yellow_tripdata_2015.csv
python benchmark/spark/NYC_Taxi_2015/run_benchmark.py
```

Interpretation and limitations

- The benchmark is a workload-specific measurement. It is not a comprehensive performance claim tool. Differences in measured time can come from:
  - how validators/executors compile and cache intermediate state
  - how each framework expresses validations (SQL vs native function calls)
  - dataset materialization and Spark caching
  - configuration such as `spark.sql.shuffle.partitions`, driver memory, and storage levels

- The harness documents two important differences in measurement methodology (reusing the same DQT run instance vs recreating the GX validator per iteration). The difference affects measured times and should be considered when interpreting results.
