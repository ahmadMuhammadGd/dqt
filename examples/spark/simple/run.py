from pyspark.sql import SparkSession
from dqt_artifact_iceberg.backends.local import LocalIcebergArtifactBackend
from dqt_executor_spark35 import SparkExecutionBackend, SparkDQDataset
from dqt import DQRunOptions, DQRun, Representation
from examples.spark.simple.suite import my_suite

spark = SparkSession.builder.appName("test").master("local[*]").getOrCreate()

dataset = spark.createDataFrame(
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
)

dataset = SparkDQDataset(uri="demo.silver.dataset", df=dataset)

dq_run = DQRun(
    suite=my_suite,
    dataset=dataset,
    executor_backend=SparkExecutionBackend(spark=spark),
    artifact_store_backend=LocalIcebergArtifactBackend(),
    options=DQRunOptions(representation=Representation.INLINE),
)

result = dq_run.run()
dq_run.persist()

if external := result.get_external_results():
    external.show()

if inline := result.get_inline_results():
    inline.show()

print("success")
result.get_passed_rows().show()

print("failed")
result.get_failed_rows().show()

print("results summary")
print(result.get_json_summary(indent=4))
