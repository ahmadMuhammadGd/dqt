from dqt_executor_spark35.config import SparkExecutionBackend
from dqt.definitions.dq_dataset import DQDataset
from dqt.execution.dq_execution_result import DQExecutionResult

from pyspark.sql import DataFrame

SparkDQDataset = DQDataset[DataFrame]
DQSparkExecutionResults = DQExecutionResult[SparkExecutionBackend, DataFrame]
