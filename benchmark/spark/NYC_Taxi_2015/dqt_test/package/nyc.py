from dqt_executor_spark35 import dqtest_column_level_spark
from pyspark.sql import functions as f

from dqt_test.package.test_utils import calculate_distance
from dqt_test.package.generic import positive, is_in_list


@dqtest_column_level_spark
def check_valid_distance(
    drop_off_lat: str,
    drop_off_lon: str,
    pickup_lat: str,
    pickup_lon: str,
    expected_distance: str,
    allowed_error: float = 0.5,
):
    """
    Validate the reported trip distance against the distance calculated
    from pickup and drop-off coordinates using the Haversine formula.

    Args:
        drop_off_lat: Name of the drop-off latitude column.
        drop_off_lon: Name of the drop-off longitude column.
        pickup_lat: Name of the pickup latitude column.
        pickup_lon: Name of the pickup longitude column.
        expected_distance: Name of the dataset's reported trip-distance column.
        allowed_error: Maximum allowed difference between the calculated
            and reported distances, in the same unit as the distances.

    Returns:
        A Spark Column containing the data-quality condition. The condition
        is True when the difference between the calculated and reported
        distances exceeds the allowed error.
    """
    calculated_distance = calculate_distance(
        lat_a=drop_off_lat,
        lat_b=pickup_lat,
        long_a=drop_off_lon,
        long_b=pickup_lon,
    )

    valid_condition = (
        f.abs(calculated_distance - f.col(expected_distance)) <= allowed_error
    )

    return valid_condition


@dqtest_column_level_spark
def pickup_time_must_be_before_drop_off_time(
    drop_off_ts: str,
    pickup_ts: str,
):
    """
    Validate that the pickup timestamp occurs before the drop-off timestamp.

    Args:
        drop_off_ts: Name of the drop-off timestamp column.
        pickup_ts: Name of the pickup timestamp column.

    Returns:
        A Spark Column containing the data-quality condition. The condition
        is True when the drop-off timestamp is later than the pickup timestamp.
    """
    return f.col(drop_off_ts) > f.col(pickup_ts)


@dqtest_column_level_spark
def distance_must_be_greater_than_zero_if_trip_duration_is_greater_than_zero(
    distance: str,
    drop_off_ts: str,
    pickup_ts: str,
):
    """
    Validate that a trip with a positive duration has a positive distance.

    Args:
        distance: Name of the trip-distance column.
        drop_off_ts: Name of the drop-off timestamp column.
        pickup_ts: Name of the pickup timestamp column.

    Returns:
        A Spark Column containing the data-quality condition. The condition
        is True when the pickup occurs before drop-off and the trip distance
        is positive.
    """
    valid_trip_duration = pickup_time_must_be_before_drop_off_time.fn(
        drop_off_ts=drop_off_ts,
        pickup_ts=pickup_ts,
    )

    return valid_trip_duration & positive.fn(column_name=distance)


@dqtest_column_level_spark
def valid_vendor_id(column_name: str):
    """
    Validate the TPEP vendor identifier for the 2015 Yellow Taxi dataset.

    For the 2015 dataset, VendorID values are expected to be 1 or 2.

    Args:
        column_name: Name of the VendorID column.

    Returns:
        True when VendorID is 1 or 2.
    """
    return is_in_list.fn(column_name=column_name, values=[1, 2])


@dqtest_column_level_spark
def valid_rate_code_id(column_name: str):
    """
    Validate the NYC Yellow Taxi rate code.

    The standard Yellow Taxi rate codes are:
        1 = Standard rate
        2 = JFK
        3 = Newark
        4 = Nassau or Westchester
        5 = Negotiated fare
        6 = Group ride

    Args:
        column_name: Name of the RateCodeID column.

    Returns:
        True when the rate code is one of the supported values.
    """
    return is_in_list.fn(column_name=column_name, values=[1, 2, 3, 4, 5, 6])


@dqtest_column_level_spark
def valid_payment_type(column_name: str):
    """
    Validate the payment type code.

    Supported values are:
        1 = Credit card
        2 = Cash
        3 = No charge
        4 = Dispute
        5 = Unknown
        6 = Voided trip

    Args:
        column_name: Name of the payment_type column.

    Returns:
        True when payment_type is one of the supported values.
    """
    return is_in_list.fn(column_name=column_name, values=[1, 2, 3, 4, 5, 6])


@dqtest_column_level_spark
def valid_store_and_forward_flag(column_name: str):
    """
    Validate the store-and-forward flag.

    Expected values are Y and N.

    Args:
        column_name: Name of the store_and_fwd_flag column.

    Returns:
        True when the value is Y or N.
    """
    return is_in_list.fn(column_name=column_name, values=["Y", "N"])


@dqtest_column_level_spark
def trip_duration_below_maximum(
    drop_off_ts: str,
    pickup_ts: str,
    max_duration_minutes: int = 1440,
):
    """
    Validate that a trip does not exceed a maximum duration.

    Args:
        drop_off_ts: Name of the drop-off timestamp column.
        pickup_ts: Name of the pickup timestamp column.
        max_duration_minutes: Maximum allowed trip duration in minutes.

    Returns:
        True when the trip duration is within the configured limit.
    """
    duration_seconds = f.unix_timestamp(drop_off_ts) - f.unix_timestamp(pickup_ts)

    return duration_seconds <= max_duration_minutes * 60


@dqtest_column_level_spark
def total_amount_matches_components(
    total_amount: str,
    fare_amount: str,
    extra: str,
    mta_tax: str,
    tip_amount: str,
    tolls_amount: str,
    improvement_surcharge: str,
    allowed_error: float = 0.01,
):
    """
    Validate that total_amount matches the sum of its fare components.

    Args:
        total_amount: Name of the total_amount column.
        fare_amount: Name of the fare_amount column.
        extra: Name of the extra column.
        mta_tax: Name of the mta_tax column.
        tip_amount: Name of the tip_amount column.
        tolls_amount: Name of the tolls_amount column.
        improvement_surcharge: Name of the improvement_surcharge column.
        allowed_error: Maximum allowed rounding difference.

    Returns:
        True when the reported total is within allowed_error of the
        calculated total.
    """
    calculated_total = (
        f.col(fare_amount)
        + f.col(extra)
        + f.col(mta_tax)
        + f.col(tip_amount)
        + f.col(tolls_amount)
        + f.col(improvement_surcharge)
    )

    return f.abs(f.col(total_amount) - calculated_total) <= allowed_error
