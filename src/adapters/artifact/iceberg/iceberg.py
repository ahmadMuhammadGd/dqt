import pyarrow as pa
from pyiceberg.catalog import load_catalog

from adapters.artifact.iceberg.utils import iceberg_schema_from_pydantic
from core.models.analytical import AnalyticalMart, AnalyticalModel
from core.models.execution import DQExecutionResult
from core.ports.artifact_store import ArtifactStore
from adapters.artifact.iceberg.config import IcebergArtifactStoreConfig


class IcebergArtifactStore(ArtifactStore):

    def __init__(self, config: IcebergArtifactStoreConfig | None = None):

        if not config:
            config = IcebergArtifactStoreConfig()

        self.namespace = config.namespace
        self.catalog = config.pyiceberg_catalog

        self._init()

    def save(self, execution_result: DQExecutionResult):

        mart = AnalyticalMart.from_execution_result(execution_result)

        self._append(mart.datasets)

        self._append(mart.suites)
        self._append(mart.tests)

        self._append(mart.binds)

        self._append(mart.runs)
        self._append(mart.results)

    def _append(self, rows: list[AnalyticalModel]):

        if not rows:
            return

        model = type(rows[0])

        table_identifier = (self.namespace, model.table_name)

        self.catalog.create_table_if_not_exists(
            identifier=table_identifier, schema=iceberg_schema_from_pydantic(model)
        )

        table = self.catalog.load_table(identifier=table_identifier)

        arrow = pa.Table.from_pylist(
            [r.model_dump(mode="python") for r in rows],
            schema=table.schema().as_arrow(),
        )

        if model.primary_key:
            table.upsert(df=arrow, join_cols=model.primary_key)
            return

        with table.transaction() as transaction:
            transaction.append(df=arrow)

    def _init(self):
        self.catalog.create_namespace_if_not_exists(namespace=self.namespace)
