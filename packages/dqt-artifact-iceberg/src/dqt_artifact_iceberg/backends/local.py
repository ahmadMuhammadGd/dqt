from pathlib import Path
from dqt_artifact_iceberg.backends.base import IcebergArtifactBackend


class LocalIcebergArtifactBackend(IcebergArtifactBackend):
    name: str = "local"
    warehouse: str = f"file://{Path.cwd() / 'warehouse'}"
    catalog_uri: str = f"sqlite:///{Path.cwd() / 'catalog.db'}"
    catalog_type: str = "sql"
