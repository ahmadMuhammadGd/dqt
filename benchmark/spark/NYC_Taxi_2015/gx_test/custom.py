# custom_expectations.py

from pyspark.sql import functions as F

from great_expectations.execution_engine import SparkDFExecutionEngine
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.expectations.metrics.map_metric_provider import (
    ColumnMapMetricProvider,
    column_condition_partial,
)


class ColumnValuesPickupBeforeDropoff(ColumnMapMetricProvider):
    condition_metric_name = "column_values.pickup_before_dropoff"

    @column_condition_partial(engine=SparkDFExecutionEngine)
    def _spark(cls, column, **kwargs):
        return column < F.col("tpep_dropoff_datetime")


class ExpectPickupToBeBeforeDropoff(ColumnMapExpectation):
    map_metric = "column_values.pickup_before_dropoff"
    success_keys = ()


class ColumnValuesDurationBelowMax(ColumnMapMetricProvider):
    condition_metric_name = "column_values.duration_below_max"

    @column_condition_partial(engine=SparkDFExecutionEngine)
    def _spark(cls, column, **kwargs):
        duration_seconds = F.unix_timestamp(
            F.col("tpep_dropoff_datetime")
        ) - F.unix_timestamp(column)

        return duration_seconds <= 1440 * 60


class ExpectTripDurationBelowMax(ColumnMapExpectation):
    map_metric = "column_values.duration_below_max"
    success_keys = ()


class ColumnValuesPositiveDistanceIfPositiveDuration(ColumnMapMetricProvider):
    condition_metric_name = "column_values.positive_distance_if_positive_duration"

    @column_condition_partial(engine=SparkDFExecutionEngine)
    def _spark(cls, column, **kwargs):
        positive_duration = F.col("tpep_dropoff_datetime") > F.col(
            "tpep_pickup_datetime"
        )

        positive_distance = column > 0

        return ~positive_duration | positive_distance


class ExpectPositiveDistanceIfPositiveDuration(ColumnMapExpectation):
    map_metric = "column_values.positive_distance_if_positive_duration"
    success_keys = ()


class ColumnValuesHaversineValid(ColumnMapMetricProvider):
    condition_metric_name = "column_values.haversine_valid"

    @column_condition_partial(engine=SparkDFExecutionEngine)
    def _spark(cls, column, **kwargs):
        pickup_lat = F.col("pickup_latitude")
        pickup_lon = F.col("pickup_longitude")
        dropoff_lat = F.col("dropoff_latitude")
        dropoff_lon = F.col("dropoff_longitude")

        delta_lat = F.radians(dropoff_lat - pickup_lat)
        delta_lon = F.radians(dropoff_lon - pickup_lon)

        a = F.pow(F.sin(delta_lat / 2), 2) + F.cos(F.radians(pickup_lat)) * F.cos(
            F.radians(dropoff_lat)
        ) * F.pow(F.sin(delta_lon / 2), 2)

        calculated_distance = 2 * 3958.8 * F.asin(F.sqrt(a))

        return F.abs(calculated_distance - column) <= 0.5


class ExpectColumnValuesToBeValidHaversineDistance(ColumnMapExpectation):
    map_metric = "column_values.haversine_valid"
    success_keys = ()


class ColumnValuesTotalMatchesComponents(ColumnMapMetricProvider):
    condition_metric_name = "column_values.total_matches_components"

    @column_condition_partial(engine=SparkDFExecutionEngine)
    def _spark(cls, column, **kwargs):
        calculated_total = (
            F.col("fare_amount")
            + F.col("extra")
            + F.col("mta_tax")
            + F.col("tip_amount")
            + F.col("tolls_amount")
            + F.col("improvement_surcharge")
        )

        return F.abs(column - calculated_total) <= 0.01


class ExpectTotalAmountMatchesComponents(ColumnMapExpectation):
    map_metric = "column_values.total_matches_components"
    success_keys = ()
