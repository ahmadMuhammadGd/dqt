from dqt.config.artifact_store import ArtifactBackend
from pyiceberg.catalog import Catalog, load_catalog


class IcebergArtifactBackend(ArtifactBackend):
    artifact_store_name = "iceberg"

    warehouse: str
    catalog_type: str
    catalog_uri: str
    namespace: str = "dqt"

    @property
    def pyiceberg_catalog(self) -> Catalog:
        return load_catalog(
            name=self.catalog_type,
            type=self.catalog_type,
            uri=self.catalog_uri,
            warehouse=self.warehouse,
        )
