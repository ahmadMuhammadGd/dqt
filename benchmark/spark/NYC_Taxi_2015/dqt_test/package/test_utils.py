from pyspark.sql import functions as f
from pyspark.sql.column import Column


def calculate_distance(
    lat_a: str,
    long_a: str,
    lat_b: str,
    long_b: str,
    R: float = 6371.0,
) -> Column:
    lat_a = f.col(lat_a)
    long_a = f.col(long_a)
    lat_b = f.col(lat_b)
    long_b = f.col(long_b)

    delta_lat = f.radians(lat_b - lat_a)
    delta_long = f.radians(long_b - long_a)

    haversine = f.pow(f.sin(delta_lat / 2), 2) + f.cos(f.radians(lat_a)) * f.cos(
        f.radians(lat_b)
    ) * f.pow(f.sin(delta_long / 2), 2)

    return 2 * R * f.asin(f.sqrt(haversine))
