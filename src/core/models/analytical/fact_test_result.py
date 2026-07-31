from core.models.analytical.analytical_model import AnalyticalModel
from core.models.execution import DQExecutionResult


class FactTestResult(AnalyticalModel):
    table_name = "fact_test_results"
    primary_key = ["run_uuid", "bind_uuid"]

    run_uuid: str
    bind_uuid: str
    status: str
    failed_rows: int
    total_rows: int

    @classmethod
    def from_execution_result(
        cls,
        result: DQExecutionResult,
    ) -> list["FactTestResult"]:

        return [
            cls(
                run_uuid=result.run.uuid,
                bind_uuid=r.bind_uuid,
                status=r.status.value,
                failed_rows=r.failed_rows,
                total_rows=r.total_rows,
            )
            for r in result.test_results
        ]
