from typing import Any

from core.models.analytical.analytical_model import AnalyticalModel
from core.models.execution import DQExecutionResult


class DimDataset(AnalyticalModel):
    table_name = "dim_dataset"
    primary_key = ["dataset_uuid"]

    dataset_uuid: str
    uri: str
    format: str | None = None
    version: str | None = None

    @classmethod
    def from_execution_result(
        cls,
        result: DQExecutionResult,
    ) -> list["DimDataset"]:

        return [
            cls(
                dataset_uuid=result.run.dataset.uuid,
                uri=result.run.dataset.uri,
                format=result.run.dataset.format,
                version=result.run.dataset.version,
            )
        ]
