from uuid import UUID

from dqt.analytical.analytical_model import AnalyticalModel
from dqt.runtime.dq_run import DQRun


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
    def from_run(cls, run: DQRun) -> "list[DimTestBind]":
        suite = run.suite
        binds = suite.test_binds

        return [
            cls(
                bind_uuid=bind.uuid,
                suite_uuid=suite.uuid,
                test_uuid=bind.definition.uuid,
                severity=bind.severity.value,
                threshold_pct=bind.threshold_pct,
                ordinal=bind.ordinal,
            )
            for bind in binds
        ]
