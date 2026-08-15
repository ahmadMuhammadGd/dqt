from uuid import UUID

from dqt.analytical.analytical_model import AnalyticalModel
from dqt.runtime.dq_run import DQRun


class FactTestResult(AnalyticalModel):
    table_name = "fact_test_results"
    primary_key = ["run_uuid", "bind_uuid"]

    run_uuid: str
    bind_uuid: str
    status: str
    failed_rows: int
    total_rows: int

    @classmethod
    def from_run(
        cls,
        run: DQRun,
    ) -> list["FactTestResult"]:

        return [
            cls(
                run_uuid=str(run.uuid),
                bind_uuid=str(r.bind_uuid),
                status=r.status.value,
                failed_rows=r.failed_rows,
                total_rows=r.total_rows,
            )
            for r in run.results.test_results
        ]
