from pyiceberg.catalog import Catalog, load_catalog
from dqt_artifact_iceberg.backends.base import IcebergArtifactBackend


class S3IcebergArtifactBackend(IcebergArtifactBackend):
    name: str = "s3"
    warehouse: str = "s3://dqt"
    catalog_uri: str = "postgresql+psycopg2://..."
    catalog_type: str = "sql"
    endpoint_url: str | None = None
    s3_region: str = "us-east-1"

    @property
    def pyiceberg_catalog(self) -> Catalog:
        properties = {
            "s3.region": self.s3_region,
        }

        if self.s3_endpoint:
            properties["s3.endpoint"] = self.s3_endpoint

        return load_catalog(
            name=self.name,
            type=self.catalog_type,
            uri=self.catalog_uri,
            warehouse=self.warehouse,
            **properties,
        )
