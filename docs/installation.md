# Installation

Minimum installation to run the repository examples (editable installs for local packages):

```
uv pip install -e packages/dqt-artifact-iceberg packages/dqt-executor-spark35
```

If the leading `uv` is not part of your environment, run the equivalent:

```bash
pip install -e packages/dqt-artifact-iceberg packages/dqt-executor-spark35
```

What the command does:

- Installs the local `dqt-artifact-iceberg` and `dqt-executor-spark35` packages in editable mode so the examples can import them directly from this checkout.

Additional dependencies (repository sources):

- `dqt` (core) — requires `pydantic>=2.13.4` (declared in packages/dqt-core/pyproject.toml).
- `dqt-executor-spark35` — requires `pyspark>=3.4` (packages/dqt-executor-spark35/pyproject.toml).
- `dqt-artifact-iceberg` — requires `pyiceberg[sql-sqlite]>=0.11.1` and `pyarrow>=25.0.0` (packages/dqt-artifact-iceberg/pyproject.toml).

Optional (used by benchmarks or examples):

- `great_expectations` (benchmark comparisons) — see `benchmark/spark/NYC_Taxi_2015/run_gx.py`.
- `matplotlib` (benchmark plotting) — used by `run_benchmark.py` to produce `benchmark.png`.

Environment and dataset configuration for benchmarking:

- The NYC Taxi benchmark reads a CSV path from the environment variable `YELLOW_TAXI_2015_CSV`. See: [benchmark/spark/NYC_Taxi_2015/dataset.py](../benchmark/spark/NYC_Taxi_2015/dataset.py)

Notes:

- The editable install above only installs the two packages explicitly. The `dqt` core package is declared in `packages/dqt-core/pyproject.toml`; you may want to `pip install -e packages/dqt-core` too if you need an editable dqt core install in your environment.
- Installing `pyspark` can be heavyweight; use your system's preferred installation method (conda, pip) and ensure Java is available for Spark.
