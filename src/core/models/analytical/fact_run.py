from datetime import datetime

from core.models.analytical.analytical_model import AnalyticalModel
from core.models.execution import DQExecutionResult


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
    def from_execution_result(cls, result: DQExecutionResult):

        run = result.run

        return [
            cls(
                run_uuid=run.uuid,
                suite_uuid=run.suite.uuid,
                dataset_uuid=run.dataset.uuid,
                started_at=run.started_at,
                finished_at=run.finished_at,
                elapsed_ms=(
                    run.elapsed.total_seconds() * 1000 if run.elapsed else None
                ),
            )
        ]
