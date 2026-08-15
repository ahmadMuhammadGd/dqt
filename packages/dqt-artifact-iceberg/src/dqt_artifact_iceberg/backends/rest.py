from pyiceberg.catalog import Catalog, load_catalog
from dqt_artifact_iceberg.backends.base import IcebergArtifactBackend


class RestIcebergArtifactBackend(IcebergArtifactBackend):
    name: str = "rest"
    catalog_type: str = "rest"

    warehouse: str = "s3://dqt"
    catalog_uri: str

    token: str | None = None

    @property
    def pyiceberg_catalog(self) -> Catalog:
        properties = {
            "uri": self.catalog_uri,
            "warehouse": self.warehouse,
        }

        if self.token:
            properties["token"] = self.token

        return load_catalog(
            name=self.name,
            type=self.catalog_type,
            **properties,
        )
