from datetime import datetime
from uuid import UUID

from dqt.analytical.analytical_model import AnalyticalModel
from dqt.runtime.dq_run import DQRun


class FactRun(AnalyticalModel):
    table_name = "fact_run"
    partition_columns = ["dataset_uri"]
    primary_key = ["run_uuid"]

    run_uuid: str
    suite_uuid: str

    dataset_uuid: str

    started_at: datetime
    finished_at: datetime | None

    elapsed_ms: float | None

    @classmethod
    def from_run(cls, run: DQRun):

        return [
            cls(
                run_uuid=str(run.uuid),
                suite_uuid=str(run.suite.uuid),
                dataset_uuid=str(run.dataset.uuid),
                started_at=run.started_at,
                finished_at=run.finished_at,
                elapsed_ms=(
                    run.elapsed.total_seconds() * 1000 if run.elapsed else None
                ),
            )
        ]
