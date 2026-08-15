from typing import List

from dqt_executor_spark35 import dqtest_column_level_spark
from pyspark.sql import functions as f


@dqtest_column_level_spark
def not_null(column_name: str):
    """
    Validate that a column does not contain null values.

    Args:
        column_name: Name of the column to validate.

    Returns:
        A Spark Column containing the data-quality condition. The condition
        is True when the column value is not null.
    """
    return f.col(column_name).isNotNull()


@dqtest_column_level_spark
def valid_latitude(column_name: str):
    """
    Validate that latitude values fall within the valid geographic range.

    Valid latitude values are between -90 and 90 degrees.

    Args:
        column_name: Name of the latitude column to validate.

    Returns:
        A Spark Column containing the data-quality condition. The condition
        is True when the latitude value is within the valid range.
    """
    return (f.col(column_name) >= -90) & (f.col(column_name) <= 90)


@dqtest_column_level_spark
def valid_longitude(column_name: str):
    """
    Validate that longitude values fall within the valid geographic range.

    Valid longitude values are between -180 and 180 degrees.

    Args:
        column_name: Name of the longitude column to validate.

    Returns:
        A Spark Column containing the data-quality condition. The condition
        is True when the longitude value is within the valid range.
    """
    return (f.col(column_name) >= -180) & (f.col(column_name) <= 180)


@dqtest_column_level_spark
def positive(column_name: str):
    """
    Validate that a numeric column contains strictly positive values.

    Args:
        column_name: Name of the numeric column to validate.

    Returns:
        A Spark Column containing the data-quality condition. The condition
        is True when the column value is greater than zero.
    """
    return f.col(column_name) > 0


@dqtest_column_level_spark
def in_range(
    column_name: str,
    min: int | float,
    max: int | float,
):
    """
    Validate that values fall strictly between a minimum and maximum.

    Args:
        column_name: Name of the numeric column to validate.
        min: Exclusive lower bound.
        max: Exclusive upper bound.

    Returns:
        A Spark Column containing the data-quality condition. The condition
        is True when the column value is greater than min and less than max.
    """
    return (min < f.col(column_name)) & (f.col(column_name) < max)


@dqtest_column_level_spark
def is_in_list(
    column_name: str,
    values: List[str],
):
    """
    Validate that column values belong to a predefined list of values.

    Args:
        column_name: Name of the column to validate.
        values: List of allowed values.

    Returns:
        A Spark Column containing the data-quality condition. The condition
        is True when the column value matches one of the allowed values.
    """
    return f.col(column_name).isin(values)
