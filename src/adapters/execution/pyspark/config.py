from core.models.config.execution_engine import ExecutionEngineConfig
from pydantic import ConfigDict, Field, computed_field
from pyspark.sql import SparkSession
from pyspark import StorageLevel


class SparkExecutionConfig(ExecutionEngineConfig):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    spark: SparkSession = Field(exclude=True)
    persist__storage_level: StorageLevel = Field(
        exclude=True, default=StorageLevel.MEMORY_AND_DISK
    )

    @computed_field
    @property
    def spark_config(self) -> dict[str, str]:
        return dict(self.spark.sparkContext.getConf().getAll())

    @computed_field
    @property
    def storage_level(self) -> dict[str, str]:
        sl = self.persist__storage_level

        return {
            "use_disk": sl.useDisk,
            "use_memory": sl.useMemory,
            "use_off_heap": sl.useOffHeap,
            "deserialized": sl.deserialized,
            "replication": sl.replication,
        }
