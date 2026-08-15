from dqt.config.execution_engine import ExecutionEngineConfig
from pydantic import ConfigDict, Field, computed_field
from pyspark.sql import SparkSession
from pyspark import StorageLevel

_EXECUTOR_NAME = "spark35"


class SparkExecutionBackend(ExecutionEngineConfig):
    executor_name = _EXECUTOR_NAME

    model_config = ConfigDict(arbitrary_types_allowed=True)

    spark: SparkSession = Field(exclude=True)
    cache_storage_level: StorageLevel | None = Field(
        exclude=True, default=StorageLevel.MEMORY_AND_DISK
    )

    @computed_field
    @property
    def spark_config(self) -> dict[str, str]:
        return dict(self.spark.sparkContext.getConf().getAll())

    @computed_field
    @property
    def storage_level(self) -> dict[str, str]:
        sl = self.cache_storage_level

        return {
            "use_disk": sl.useDisk,
            "use_memory": sl.useMemory,
            "use_off_heap": sl.useOffHeap,
            "deserialized": sl.deserialized,
            "replication": sl.replication,
        }
