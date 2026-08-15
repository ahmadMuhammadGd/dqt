import pyarrow as pa
from dqt.runtime.dq_run import DQRun
from dqt_artifact_iceberg.utils import iceberg_schema_from_pydantic
from dqt.analytical import AnalyticalMart, AnalyticalModel
from dqt.abc.artifact_store import ArtifactStorePersist
from dqt_artifact_iceberg.backends.local import IcebergArtifactBackend


class IcebergArtifactBackendPersist(ArtifactStorePersist):

    def __init__(self, config: IcebergArtifactBackend | None = None):

        if not config:
            config = IcebergArtifactBackend()

        self.namespace = config.namespace
        self.catalog = config.pyiceberg_catalog

        self._init()

    def persist(self, run: DQRun):

        mart = AnalyticalMart.from_run(run)

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
