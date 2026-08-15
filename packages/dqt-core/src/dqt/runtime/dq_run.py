from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Generic, Optional, TypeVar
from uuid import UUID, uuid4

from dqt.abc.execution_engine import ExecutionEngine
from dqt.execution.dq_execution_result import DQExecutionResult
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from dqt.config.execution_engine import ExecutionEngineConfig
from dqt.execution import DQExecutionResult
from dqt.config.artifact_store import ArtifactBackend
from dqt.definitions.dq_dataset import DQDataset
from dqt.definitions.dq_suite import DQSuite
from dqt.config.run import DQRunOptions
from dqt.enums.dq_run_options_representation import Representation
from dqt.abc import ArtifactStorePersist, ExecutionEngine
from pydantic import BaseModel

ConfigT = TypeVar("ConfigT", bound=ExecutionEngineConfig)
FrameT = TypeVar("FrameT")
ResultT = TypeVar("ResultT", bound="DQExecutionResult")


class DQRun(BaseModel, Generic[ConfigT, FrameT, ResultT]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    uuid: str = Field(default_factory=uuid4)

    suite: DQSuite

    executor_backend: ConfigT

    dataset: DQDataset[FrameT]

    options: DQRunOptions = Field(default_factory=DQRunOptions)

    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    artifact_store_backend: ArtifactBackend | None = None
    results: ResultT | None = None

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

    @model_validator(mode="after")
    def _validate(self):
        self._get_executor_cls()
        self._get_artifact_store_persist_cls()
        return self

    @property
    def _executor(self):
        return self.executor_backend.executor_name

    @property
    def _artifact_store(self):
        return self.artifact_store_backend.artifact_store_name

    def _get_executor_cls(self):
        if not self.executor_backend:
            raise ValueError("user must specify executor backend")

        from dqt.loaders import get_executor

        return get_executor(self._executor)

    def _get_artifact_store_persist_cls(self):
        if not self.artifact_store_backend:
            print("Warning: User haven't specify any artifact store backend")
            return None

        from dqt.loaders import get_artifact_store

        return get_artifact_store(self._artifact_store)

    def _bind_results(self, results: ResultT):
        self.results = results

    def run(self, *args, **kwargs) -> DQExecutionResult:
        executor_cls: ExecutionEngine = self._get_executor_cls()
        executor = executor_cls(self)
        results = executor.run(*args, **kwargs)
        self._bind_results(results)
        return results

    def persist(self, *args, **kwargs) -> None:
        store_cls: ArtifactStorePersist = self._get_artifact_store_persist_cls()
        if not store_cls:
            raise ValueError("user haven't specify any artifact store backend")

        store = store_cls(self.artifact_store_backend)
        return store.persist(self, *args, **kwargs)

    def set_finished_at(self, ts: datetime | None = None):
        _ts = ts if ts else datetime.now(timezone.utc)
        self.finished_at = _ts
