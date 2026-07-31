from hashlib import sha1
from typing import Generic, Tuple, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)

FrameT = TypeVar("FrameT")


class DQDataset(BaseModel, Generic[FrameT]):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
        extra="forbid",
    )

    uri: str
    df: FrameT = Field(exclude=True)  # do not serialize it
    format: str | None = Field(default=None)
    version: str | None = Field(default=None)
    unique_keys: Tuple[str, ...] = Field(default_factory=tuple)

    @computed_field
    @property
    def uuid(self) -> str:

        dataset_uuid = self.uri + str(self.format) + str(self.version)

        return sha1(dataset_uuid.encode()).hexdigest()
