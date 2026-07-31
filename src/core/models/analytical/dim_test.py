from core.models.analytical.analytical_model import AnalyticalModel
from core.models.execution import DQExecutionResult


class DimTest(AnalyticalModel):
    table_name = "dim_test"
    primary_key = ["test_uuid"]

    test_uuid: str
    suite_uuid: str

    name: str
    description: str | None

    scope: str
    engine: str
    execution_mode: str

    test_implementation: str

    @classmethod
    def from_execution_result(
        cls,
        result: DQExecutionResult,
    ) -> list["DimTest"]:

        suite = result.run.suite

        return [
            cls(
                test_uuid=bind.definition.uuid,
                suite_uuid=suite.uuid,
                name=bind.definition.name,
                description=bind.definition.description,
                scope=bind.definition.scope.value,
                engine=bind.definition.engine.value,
                execution_mode=bind.definition.execution_mode.value,
                test_implementation=bind.definition.test_implementation,
            )
            for bind in suite.test_binds
        ]
