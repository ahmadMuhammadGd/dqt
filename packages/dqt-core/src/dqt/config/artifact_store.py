from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class ArtifactBackend(BaseModel):
    artifact_store_name: ClassVar[str]

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
