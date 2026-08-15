from pyspark.sql import SparkSession
import os


def get_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("benchmark-nyc-taxi-2015")
        .master("local[*]")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.ui.showConsoleProgress", "false")
        .config(
            "spark.serializer",
            "org.apache.spark.serializer.KryoSerializer",
        )
        .config("spark.driver.memory", "6g")
        .getOrCreate()
    )


def get_dataset(limit: int = 10_000):
    from pyspark.sql import functions as f

    from pyspark.sql.types import (
        StructType,
        StructField,
        IntegerType,
        DoubleType,
        StringType,
        TimestampType,
    )

    schema = StructType(
        [
            StructField("VendorID", IntegerType(), True),
            StructField("tpep_pickup_datetime", TimestampType(), True),
            StructField("tpep_dropoff_datetime", TimestampType(), True),
            StructField("passenger_count", IntegerType(), True),
            StructField("trip_distance", DoubleType(), True),
            StructField("pickup_longitude", DoubleType(), True),
            StructField("pickup_latitude", DoubleType(), True),
            StructField("RateCodeID", IntegerType(), True),
            StructField("store_and_fwd_flag", StringType(), True),
            StructField("dropoff_longitude", DoubleType(), True),
            StructField("dropoff_latitude", DoubleType(), True),
            StructField("payment_type", IntegerType(), True),
            StructField("fare_amount", DoubleType(), True),
            StructField("extra", DoubleType(), True),
            StructField("mta_tax", DoubleType(), True),
            StructField("tip_amount", DoubleType(), True),
            StructField("tolls_amount", DoubleType(), True),
            StructField("improvement_surcharge", DoubleType(), True),
            StructField("total_amount", DoubleType(), True),
        ]
    )

    spark = get_spark_session()
    dataset_path = os.environ["YELLOW_TAXI_2015_CSV"]

    return spark.read.csv(dataset_path, header=True, schema=schema).limit(limit)
