from pyspark import StorageLevel
from pyspark.sql import functions as f
from pyspark.sql import SparkSession

from adapters.execution.pyspark.adapter import (
    SparkExecutionConfig,
    SparkDQExecutionEngine,
)

from adapters.execution.pyspark.types import SparkDQDataset
from adapters.execution.pyspark.decorator import dqtest_column_level_spark
from core.models.config.run import DQRunOptions
from core.models.definitions import DQSuite
from core.models.enums import DQExecutionEngine
from core.models.enums.dq_run_options_representation import Representation
from core.models.execution import DQRun


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


suite = (
    DQSuite(
        name="test",
        engine=DQExecutionEngine.SPARK,
    )
    .bind_test(definition=gender_must_be_f_or_m, columns=("gender"))
    .bind_test(definition=not_null, columns=("age"))
    .bind_test(definition=greater_than, columns=("age"), test_kwargs={"num": 24})
)


# artifacts
from adapters.artifact.iceberg import IcebergArtifactStore, IcebergArtifactStoreConfig

artifact_adapter_2 = IcebergArtifactStore(IcebergArtifactStoreConfig())

# application
spark = SparkSession.builder.appName("test").master("local[*]").getOrCreate()

dataset = SparkDQDataset(
    uri="demo.silver.dataset",
    df=spark.createDataFrame(
        [
            {
                "deptId": 1,
                "age": 40,
                "name": "Hyukjin Kwon",
                "gender": "M",
                "salary": 50,
            },
            {
                "deptId": 1,
                "age": None,
                "name": "Takuya Ueshin",
                "gender": None,
                "salary": 100,
            },
            {
                "deptId": 2,
                "age": 60,
                "name": "Xinrong Meng",
                "gender": "F",
                "salary": 150,
            },
            {
                "deptId": 3,
                "age": 20,
                "name": "Haejoon Lee",
                "gender": "X",
                "salary": 200,
            },
        ]
    ),
)

# run
run = DQRun(
    suite=suite,
    dataset=dataset,
    execution_backend_config=SparkExecutionConfig(
        spark=spark, persist__storage_level=StorageLevel.MEMORY_ONLY
    ),
    options=DQRunOptions(representation=Representation.INLINE),
)


result = SparkDQExecutionEngine(run).run()
artifact_adapter_2.save(result)

print(result.model_dump_json(indent=4))

if external := result.get_external_results():
    external.show()

if inline := result.get_inline_results():
    inline.show()
