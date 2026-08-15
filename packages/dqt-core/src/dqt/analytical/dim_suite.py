from uuid import UUID

from dqt.analytical.analytical_model import AnalyticalModel
from dqt.runtime.dq_run import DQRun


class DimSuite(AnalyticalModel):
    table_name = "dim_suite"
    primary_key = ["suite_uuid"]

    suite_uuid: str
    name: str

    @classmethod
    def from_run(cls, run: DQRun) -> "list[DimSuite]":
        suite = run.suite

        return [
            cls(
                suite_uuid=str(suite.uuid),
                name=suite.name,
            )
        ]
