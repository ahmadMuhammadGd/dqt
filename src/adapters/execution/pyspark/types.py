from adapters.execution.pyspark.config import SparkExecutionConfig
from core.models.definitions.dq_dataset import DQDataset
from pyspark.sql import DataFrame
from core.models.execution.dq_execution_result import DQExecutionResult

SparkDQDataset = DQDataset[DataFrame]
DQSparkExecutionResults = DQExecutionResult[SparkExecutionConfig, DataFrame]
