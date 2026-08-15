from pyspark.sql import functions as f
from dqt_executor_spark35.decorator import dqtest_column_level_spark


@dqtest_column_level_spark
def not_null(x):
    "check for not null values"
    return f.col(x).isNotNull()


@dqtest_column_level_spark
def gender_must_be_f_or_m(x):
    "checks if value f or m for gender columns"
    return f.col(x).isin("F", "M") & not_null.fn(x)


@dqtest_column_level_spark
def greater_than(x, num: int):
    "checks if value x > num"
    return f.col(x) > num
