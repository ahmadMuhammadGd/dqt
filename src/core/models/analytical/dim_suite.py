from core.models.analytical.analytical_model import AnalyticalModel
from core.models.execution import DQExecutionResult


class DimSuite(AnalyticalModel):
    table_name = "dim_suite"
    primary_key = ["suite_uuid"]

    suite_uuid: str
    name: str
    engine: str

    @classmethod
    def from_execution_result(cls, result: DQExecutionResult) -> "list[DimSuite]":
        suite = result.run.suite

        return [
            cls(
                suite_uuid=suite.uuid,
                name=suite.name,
                engine=suite.engine.value,
            )
        ]
