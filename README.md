DQT is an open-source data quality framework designed for modern data platforms. It enables developers to define reusable data quality rules as code and execute them consistently across multiple execution engines, including PySpark. Rather than treating data quality as a reporting layer, DQT produces structured validation artifacts that can be stored, versioned, and analyzed alongside the data itself. The framework separates test definitions, execution, and artifact storage through a modular architecture, making it easy to integrate into existing ETL/ELT pipelines while remaining independent of any specific storage technology or orchestration platform.

----

# Running a Data Quality Suite with PySpark

This example demonstrates how to define data quality tests, execute them on a Spark DataFrame, and persist the execution results.

## 1. Define Tests

Tests are regular Python functions decorated with `@dqtest_column_level_spark`.

```python
@dqtest_column_level_spark
def not_null(x):
    return f.col(x).isNotNull()
```

A test may also compose other tests:

```python
@dqtest_column_level_spark
def gender_must_be_f_or_m(x):
    return f.col(x).isin("F", "M") & not_null.fn(x)
```

or accept parameters:

```python
@dqtest_column_level_spark
def greater_than(x, num: int):
    return f.col(x) > num
```

---

## 2. Create a Suite

A `DQSuite` groups related tests.

```python
suite = (
    DQSuite(
        name="test",
        engine=DQExecutionEngine.SPARK,
    )
    .bind_test(definition=gender_must_be_f_or_m, columns=("gender",))
    .bind_test(definition=not_null, columns=("age",))
    .bind_test(
        definition=greater_than,
        columns=("age",),
        test_kwargs={"num": 24},
    )
)
```

Each `bind_test()` associates a test with one or more columns and optionally supplies test parameters.

---

## 3. Create the Dataset

Wrap your Spark DataFrame in a `SparkDQDataset`.

```python
dataset = SparkDQDataset(
    uri="demo.silver.dataset",
    df=df,
    unique_keys=tuple() # there is no unique keys, defaults to dict()
)
```

The dataset URI uniquely identifies the dataset in artifact storage.

---

## 4. Configure the Run

A `DQRun` contains everything required for a single execution.

```python
run = DQRun(
    suite=suite,
    dataset=dataset,
    execution_backend_config=SparkExecutionConfig(
        spark=spark,
        persist__storage_level=StorageLevel.MEMORY_ONLY,
    ),
    options=DQRunOptions(
        representation=Representation.INLINE,
    ),
)
```

The execution configuration specifies the Spark session and execution settings.

`DQRunOptions` controls how validation results are materialized.

Available representations are:

* `Representation.INLINE` – appends validation metadata to the original dataset.
* `Representation.EXTERNAL` – produces a separate validation dataset.
* `Representation.BOTH` – returns both inline and external validation datasets.

When using `EXTERNAL` or `BOTH`, `DQDataset` object must define one or more `unique_keys`.

---

## 5. Execute the Suite

Run the suite using the Spark execution engine.

```python
result = SparkDQExecutionEngine(run).run()
```

---

## 6. Persist Artifacts

Execution artifacts can be stored using an artifact adapter.

```python
artifact_adapter.save(result)
```

Artifact adapters are independent from execution engines, allowing the same execution to be stored in different backends.

---

## 7. Access the Results

Execution metadata can be serialized:

```python
print(result.model_dump_json(indent=4))
```

Retrieve the external validation dataset:

```python
if external := result.get_external_results():
    external.show()
```

Retrieve the inline dataset:

```python
if inline := result.get_inline_results():
    inline.show()
```

Depending on the selected representation, one or both datasets may be available.
