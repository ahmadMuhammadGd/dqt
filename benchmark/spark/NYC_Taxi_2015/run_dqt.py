from pathlib import Path
import sys

print(Path(__file__).parent.__str__())
sys.path.append(Path(__file__).parent.__str__())

from dqt import DQSuite, DQRun
from dqt_executor_spark35 import SparkDQDataset, SparkExecutionBackend

from dqt_test.package.generic import *
from dqt_test.package.nyc import *
from dataset import get_dataset, get_spark_session
from pyspark.sql import SparkSession, DataFrame


def prepare_dqt(spark: SparkSession, df: DataFrame) -> DQRun:
    suite = (
        DQSuite(name="nyc-taxi-2015-01")
        # ------------------------------------------------------------------
        # Vendor
        # ------------------------------------------------------------------
        .bind_test(
            definition=valid_vendor_id,
            columns="VendorID",
        )
        .bind_test(
            definition=not_null,
            columns="VendorID",
        )
        # ------------------------------------------------------------------
        # Pickup / Drop-off timestamps
        # ------------------------------------------------------------------
        .bind_test(
            definition=not_null,
            columns="tpep_pickup_datetime",
        )
        .bind_test(
            definition=not_null,
            columns="tpep_dropoff_datetime",
        )
        .bind_test(
            definition=pickup_time_must_be_before_drop_off_time,
            columns={
                "drop_off_ts": "tpep_dropoff_datetime",
                "pickup_ts": "tpep_pickup_datetime",
            },
        )
        .bind_test(
            definition=trip_duration_below_maximum,
            columns={
                "drop_off_ts": "tpep_dropoff_datetime",
                "pickup_ts": "tpep_pickup_datetime",
            },
        )
        # ------------------------------------------------------------------
        # Passenger count
        # ------------------------------------------------------------------
        .bind_test(
            definition=not_null,
            columns="passenger_count",
        )
        .bind_test(
            definition=in_range,
            columns="passenger_count",
            test_kwargs={"min": 0, "max": 10},
        )
        # ------------------------------------------------------------------
        # Trip distance
        # ------------------------------------------------------------------
        .bind_test(
            definition=not_null,
            columns="trip_distance",
        )
        .bind_test(
            definition=positive,
            columns="trip_distance",
        )
        .bind_test(
            definition=distance_must_be_greater_than_zero_if_trip_duration_is_greater_than_zero,
            columns={
                "distance": "trip_distance",
                "drop_off_ts": "tpep_dropoff_datetime",
                "pickup_ts": "tpep_pickup_datetime",
            },
        )
        # ------------------------------------------------------------------
        # Pickup coordinates
        # ------------------------------------------------------------------
        .bind_test(
            definition=not_null,
            columns="pickup_latitude",
        )
        .bind_test(
            definition=not_null,
            columns="pickup_longitude",
        )
        .bind_test(
            definition=valid_latitude,
            columns="pickup_latitude",
        )
        .bind_test(
            definition=valid_longitude,
            columns="pickup_longitude",
        )
        # ------------------------------------------------------------------
        # Drop-off coordinates
        # ------------------------------------------------------------------
        .bind_test(
            definition=not_null,
            columns="dropoff_latitude",
        )
        .bind_test(
            definition=not_null,
            columns="dropoff_longitude",
        )
        .bind_test(
            definition=valid_latitude,
            columns="dropoff_latitude",
        )
        .bind_test(
            definition=valid_longitude,
            columns="dropoff_longitude",
        )
        # ------------------------------------------------------------------
        # Geographic distance validation
        # ------------------------------------------------------------------
        .bind_test(
            definition=check_valid_distance,
            columns={
                "drop_off_lat": "dropoff_latitude",
                "drop_off_lon": "dropoff_longitude",
                "pickup_lat": "pickup_latitude",
                "pickup_lon": "pickup_longitude",
                "expected_distance": "trip_distance",
            },
        )
        # ------------------------------------------------------------------
        # Rate code
        # ------------------------------------------------------------------
        .bind_test(
            definition=not_null,
            columns="RateCodeID",
        )
        .bind_test(
            definition=valid_rate_code_id,
            columns="RateCodeID",
        )
        # ------------------------------------------------------------------
        # Store and forward flag
        # ------------------------------------------------------------------
        .bind_test(
            definition=not_null,
            columns="store_and_fwd_flag",
        )
        .bind_test(
            definition=valid_store_and_forward_flag,
            columns="store_and_fwd_flag",
        )
        # ------------------------------------------------------------------
        # Payment type
        # ------------------------------------------------------------------
        .bind_test(
            definition=not_null,
            columns="payment_type",
        )
        .bind_test(
            definition=valid_payment_type,
            columns="payment_type",
        )
        # ------------------------------------------------------------------
        # Fare amounts
        # ------------------------------------------------------------------
        .bind_test(
            definition=not_null,
            columns="fare_amount",
        )
        .bind_test(
            definition=not_null,
            columns="total_amount",
        )
        .bind_test(
            definition=not_null,
            columns="tip_amount",
        )
        .bind_test(
            definition=not_null,
            columns="tolls_amount",
        )
        .bind_test(
            definition=not_null,
            columns="mta_tax",
        )
        .bind_test(
            definition=not_null,
            columns="extra",
        )
        .bind_test(
            definition=not_null,
            columns="improvement_surcharge",
        )
        # ------------------------------------------------------------------
        # Total amount consistency
        # ------------------------------------------------------------------
        .bind_test(
            definition=total_amount_matches_components,
            columns={
                "total_amount": "total_amount",
                "fare_amount": "fare_amount",
                "extra": "extra",
                "mta_tax": "mta_tax",
                "tip_amount": "tip_amount",
                "tolls_amount": "tolls_amount",
                "improvement_surcharge": "improvement_surcharge",
            },
        )
    )

    return DQRun(
        suite=suite,
        executor_backend=SparkExecutionBackend(spark=spark, cache_storage_level=None),
        dataset=SparkDQDataset(uri="demo.nyc.taxi-2015", df=df),
    )


def run_dqt(dq_run: DQRun):
    return dq_run.run()
