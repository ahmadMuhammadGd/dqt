from core.models.analytical.analytical_model import AnalyticalModel
from core.models.execution import DQExecutionResult


class DimTestBind(AnalyticalModel):
    table_name = "dim_test_bind"
    primary_key = ["bind_uuid"]

    bind_uuid: str
    suite_uuid: str
    test_uuid: str
    severity: str
    threshold_pct: float
    ordinal: int

    @classmethod
    def from_execution_result(cls, result: DQExecutionResult) -> "list[DimTestBind]":
        suite = result.run.suite
        binds = suite.test_binds

        return [
            cls(
                bind_uuid=bind.uuid,
                suite_uuid=suite.uuid,
                test_uuid=bind.definition.uuid,
                severity=bind.severity.value,
                threshold_pct=bind.error_threshold_pct,
                ordinal=bind.ordinal,
            )
            for bind in binds
        ]
