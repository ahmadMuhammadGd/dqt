from uuid import UUID

from dqt.analytical.analytical_model import AnalyticalModel
from dqt.runtime.dq_run import DQRun


class DimDataset(AnalyticalModel):
    table_name = "dim_dataset"
    primary_key = ["dataset_uuid"]

    dataset_uuid: str
    uri: str
    format: str | None = None
    version: str | None = None

    @classmethod
    def from_run(
        cls,
        run: DQRun,
    ) -> list["DimDataset"]:

        return [
            cls(
                dataset_uuid=str(run.dataset.uuid),
                uri=run.dataset.uri,
                format=run.dataset.format,
                version=run.dataset.version,
            )
        ]
