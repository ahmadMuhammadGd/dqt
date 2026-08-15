import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.expectations import (
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeInSet,
    ExpectColumnValuesToBeBetween,
)

from gx_test.custom import (
    ExpectColumnValuesToBeValidHaversineDistance,
    ExpectPickupToBeBeforeDropoff,
    ExpectPositiveDistanceIfPositiveDuration,
    ExpectTotalAmountMatchesComponents,
    ExpectTripDurationBelowMax,
)
from pyspark.sql import DataFrame
from great_expectations.validator.validator import Validator


def prepare_gx(spark, df: DataFrame) -> Validator:
    context = gx.get_context()

    data_source = context.data_sources.add_spark(
        name="nyc_taxi",
        force_reuse_spark_context=True,
    )

    data_asset = data_source.add_dataframe_asset(
        name="nyc_taxi_2015",
    )

    batch_definition = data_asset.add_batch_definition_whole_dataframe("full_dataframe")

    batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

    assert spark.sparkContext is df.sparkSession.sparkContext

    suite = ExpectationSuite(name="nyc_taxi_2015")

    # ================================================================
    # Vendor
    # ================================================================

    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="VendorID"))

    suite.add_expectation(
        ExpectColumnValuesToBeInSet(
            column="VendorID",
            value_set=[1, 2],
        )
    )

    # ================================================================
    # Pickup / Drop-off timestamps
    # ================================================================

    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="tpep_pickup_datetime"))

    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="tpep_dropoff_datetime"))

    # ================================================================
    # Passenger count
    # ================================================================

    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="passenger_count"))

    suite.add_expectation(
        ExpectColumnValuesToBeBetween(
            column="passenger_count",
            min_value=0,
            max_value=10,
            strict_min=True,
            strict_max=True,
        )
    )

    # ================================================================
    # Trip distance
    # ================================================================

    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="trip_distance"))

    suite.add_expectation(
        ExpectColumnValuesToBeBetween(
            column="trip_distance",
            min_value=0,
            strict_min=True,
        )
    )

    # ================================================================
    # Pickup coordinates
    # ================================================================

    for column in [
        "pickup_latitude",
        "pickup_longitude",
    ]:
        suite.add_expectation(ExpectColumnValuesToNotBeNull(column=column))

    suite.add_expectation(
        ExpectColumnValuesToBeBetween(
            column="pickup_latitude",
            min_value=-90,
            max_value=90,
        )
    )

    suite.add_expectation(
        ExpectColumnValuesToBeBetween(
            column="pickup_longitude",
            min_value=-180,
            max_value=180,
        )
    )

    # ================================================================
    # Drop-off coordinates
    # ================================================================

    for column in [
        "dropoff_latitude",
        "dropoff_longitude",
    ]:
        suite.add_expectation(ExpectColumnValuesToNotBeNull(column=column))

    suite.add_expectation(
        ExpectColumnValuesToBeBetween(
            column="dropoff_latitude",
            min_value=-90,
            max_value=90,
        )
    )

    suite.add_expectation(
        ExpectColumnValuesToBeBetween(
            column="dropoff_longitude",
            min_value=-180,
            max_value=180,
        )
    )

    # ================================================================
    # Rate code
    # ================================================================

    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="RateCodeID"))

    suite.add_expectation(
        ExpectColumnValuesToBeInSet(
            column="RateCodeID",
            value_set=[1, 2, 3, 4, 5, 6],
        )
    )

    # ================================================================
    # Store and forward
    # ================================================================

    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="store_and_fwd_flag"))

    suite.add_expectation(
        ExpectColumnValuesToBeInSet(
            column="store_and_fwd_flag",
            value_set=["Y", "N"],
        )
    )

    # ================================================================
    # Payment type
    # ================================================================

    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="payment_type"))

    suite.add_expectation(
        ExpectColumnValuesToBeInSet(
            column="payment_type",
            value_set=[1, 2, 3, 4, 5, 6],
        )
    )

    # ================================================================
    # Fare amounts
    # ================================================================

    for column in [
        "fare_amount",
        "total_amount",
        "tip_amount",
        "tolls_amount",
        "mta_tax",
        "extra",
        "improvement_surcharge",
    ]:
        suite.add_expectation(ExpectColumnValuesToNotBeNull(column=column))

    # Custom tests
    suite.add_expectation(
        ExpectPickupToBeBeforeDropoff(
            column="tpep_pickup_datetime",
        )
    )

    suite.add_expectation(
        ExpectTripDurationBelowMax(
            column="tpep_pickup_datetime",
        )
    )

    suite.add_expectation(
        ExpectPositiveDistanceIfPositiveDuration(
            column="trip_distance",
        )
    )

    suite.add_expectation(
        ExpectColumnValuesToBeValidHaversineDistance(
            column="trip_distance",
        )
    )

    suite.add_expectation(
        ExpectTotalAmountMatchesComponents(
            column="total_amount",
        )
    )

    return context.get_validator(
        batch=batch,
        expectation_suite=suite,
    )


def run_gx(validator):
    return validator.validate()
