from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

import csv
import gc
import statistics
import time

from dataset import get_dataset, get_spark_session
from run_dqt import prepare_dqt, run_dqt
from run_gx import prepare_gx, run_gx

LIMITS = [
    10_000,
    50_000,
    100_000,
    250_000,
    500_000,
    750_000,
    1_000_000,
    1_250_000,
    1_500_000,
    1_750_000,
    2_000_000,
    3_000_000,
    4_000_000,
    5_000_000,
]

RESULTS_FILE = Path(__file__).parent / "results.csv"

WARMUPS = 1
ITERATIONS = 5

# ----------------------------------------------------------------------
# DQT
#
# Validator/run object is prepared once and reused.
# This represents repeated execution of the same DQ run.
# ----------------------------------------------------------------------


def benchmark_dqt(
    df,
    spark,
    row_count,
):
    print("\nDQT")

    state = prepare_dqt(
        df=df,
        spark=spark,
    )

    # Warm-up
    for _ in range(WARMUPS):
        run_dqt(state)

    timings = []

    for iteration in range(ITERATIONS):
        start = time.perf_counter()

        run_dqt(state)

        elapsed = time.perf_counter() - start
        timings.append(elapsed)

        print(f"  iteration {iteration + 1}: " f"{elapsed:.3f}s")

    return {
        "framework": "DQT",
        "limit": row_count,
        "min_seconds": min(timings),
        "median_seconds": statistics.median(timings),
        "mean_seconds": statistics.mean(timings),
    }


# ----------------------------------------------------------------------
# GX
#
# IMPORTANT:
#
# A fresh validator is created for EVERY iteration.
#
# This prevents GX metric state/cache from being reused between
# measurements.
#
# Preparation itself is NOT timed. We are measuring validate().
# ----------------------------------------------------------------------


def benchmark_gx(
    df,
    spark,
    row_count,
):
    print("\nGX")

    # --------------------------------------------------------------
    # Warm-up with a completely fresh validator.
    # --------------------------------------------------------------

    validator = prepare_gx(
        df=df,
        spark=spark,
    )

    run_gx(validator)

    # --------------------------------------------------------------
    # Actual measurements.
    #
    # Fresh validator every time.
    # --------------------------------------------------------------

    timings = []

    for iteration in range(ITERATIONS):
        validator = prepare_gx(
            df=df,
            spark=spark,
        )

        start = time.perf_counter()

        run_gx(validator)

        elapsed = time.perf_counter() - start
        timings.append(elapsed)

        print(f"  iteration {iteration + 1}: " f"{elapsed:.3f}s")

    return {
        "framework": "GX",
        "limit": row_count,
        "min_seconds": min(timings),
        "median_seconds": statistics.median(timings),
        "mean_seconds": statistics.mean(timings),
    }


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


def main():
    spark = get_spark_session()

    results = []

    try:
        for limit in LIMITS:
            print()
            print("=" * 70)
            print(f"LIMIT: {limit:,}")
            print("=" * 70)

            df = get_dataset(limit=limit)

            # ----------------------------------------------------------
            # Materialize/cache dataset BEFORE benchmarking.
            # ----------------------------------------------------------

            start = time.perf_counter()

            row_count = df.count()

            materialization_time = time.perf_counter() - start

            print(
                f"Rows: {row_count:,} "
                f"(materialization: "
                f"{materialization_time:.3f}s)"
            )

            # ----------------------------------------------------------
            # Spark baseline
            # ----------------------------------------------------------

            df.cache()

            # ----------------------------------------------------------
            # DQT
            # ----------------------------------------------------------

            result = benchmark_dqt(
                df=df,
                spark=spark,
                row_count=row_count,
            )

            results.append(result)

            # ----------------------------------------------------------
            # GX
            # ----------------------------------------------------------

            result = benchmark_gx(
                df=df,
                spark=spark,
                row_count=row_count,
            )

            results.append(result)

            # ----------------------------------------------------------
            # Cleanup
            # ----------------------------------------------------------

            df.unpersist()

            gc.collect()

        write_results(results)
        plot_results(results)

    finally:
        spark.stop()


# ----------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------
def plot_results(results):
    import matplotlib.pyplot as plt

    frameworks = sorted({result["framework"] for result in results})

    plt.figure(figsize=(10, 6))

    for framework in frameworks:
        framework_results = [
            result for result in results if result["framework"] == framework
        ]

        framework_results.sort(key=lambda x: x["limit"])

        rows = [result["limit"] for result in framework_results]

        times = [result["median_seconds"] for result in framework_results]

        plt.plot(
            rows,
            times,
            marker="o",
            label=framework,
        )

    plt.xscale("log")
    plt.xlabel("Rows")
    plt.ylabel("Median execution time (seconds)")
    plt.title("DQT vs GX — Execution Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    output_file = Path(__file__).parent / "benchmark.png"

    plt.savefig(
        output_file,
        dpi=150,
    )

    plt.close()

    print(f"\nPlot written to: {output_file}")


def write_results(results):
    with RESULTS_FILE.open(
        "w",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "framework",
                "limit",
                "min_seconds",
                "median_seconds",
                "mean_seconds",
            ],
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print(f"Results written to: {RESULTS_FILE}")

    print()
    print(
        f"{'Framework':<15}"
        f"{'Rows':>12}"
        f"{'Min':>12}"
        f"{'Median':>12}"
        f"{'Mean':>12}"
    )

    print("-" * 61)

    for result in results:
        print(
            f"{result['framework']:<15}"
            f"{result['limit']:>12,}"
            f"{result['min_seconds']:>12.3f}"
            f"{result['median_seconds']:>12.3f}"
            f"{result['mean_seconds']:>12.3f}"
        )


if __name__ == "__main__":
    main()
