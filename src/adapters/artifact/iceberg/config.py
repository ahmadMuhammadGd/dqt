from pydantic import Field

from core.models.config.artifact_store import ArtifactStoreConfig
from pyiceberg.catalog import Catalog, load_catalog

from pathlib import Path


class IcebergArtifactStoreConfig(ArtifactStoreConfig):

    pyiceberg_catalog: Catalog = Field(
        default=load_catalog(
            "local",
            type="sql",
            uri=f"sqlite:////{ str(Path.cwd() / 'catalog.db' ) }",
            warehouse=f"file://{ str(Path.cwd() / 'warehouse' ) }",
        )
    )

    namespace: str = Field(default="dqt")
