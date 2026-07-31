from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from core.models.config.execution_engine import ExecutionEngineConfig
from core.models.definitions.dq_dataset import DQDataset
from core.models.definitions.dq_suite import DQSuite
from core.models.config.run import DQRunOptions
from core.models.enums.dq_run_options_representation import Representation

ConfigT = TypeVar("ConfigT", bound=ExecutionEngineConfig)
FrameT = TypeVar("FrameT")


class DQRun(BaseModel, Generic[ConfigT, FrameT]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    uuid: str = Field(default_factory=uuid4)

    suite: DQSuite

    execution_backend_config: ConfigT
    dataset: DQDataset[FrameT]

    options: DQRunOptions = Field(default_factory=DQRunOptions)

    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None

    @computed_field
    @property
    def elapsed(self) -> timedelta | None:
        if self.finished_at is None:
            return None
        return self.finished_at - self.started_at

    @field_validator("uuid", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    def set_finished_at(self, ts: datetime | None = None):
        _ts = ts if ts else datetime.now(timezone.utc)
        self.finished_at = _ts

    @model_validator(mode="after")
    def validate_dataset_with_run_options(self):

        unique_keys_needed = self.options.representation in {
            Representation.EXTERNAL,
            Representation.BOTH,
        }
        have_unique_keys = len(self.dataset.unique_keys) > 0

        if unique_keys_needed and not have_unique_keys:
            raise ValueError(
                "`DQDataset.unique_keys` must be defined when "
                '`representation` is "external" or "both".'
            )

        return self
