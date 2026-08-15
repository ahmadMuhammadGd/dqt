from abc import abstractmethod
from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from dqt.execution import DQExecutionResult


class AnalyticalModel(BaseModel):
    table_name: ClassVar[str]
    partition_columns: ClassVar[list[str]] = []
    primary_key: ClassVar[list[str]] = []

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    @classmethod
    @abstractmethod
    def from_run(cls, result: DQExecutionResult) -> list["AnalyticalModel"]:
        raise NotImplementedError
