from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, PrivateAttr, computed_field

from dqt.config.execution_engine import ExecutionEngineConfig
from dqt.execution.dq_test_result import DQTestResult

ConfigT = TypeVar("ConfigT", bound=ExecutionEngineConfig)
FrameT = TypeVar("FrameT")


class DQExecutionResult(BaseModel, Generic[ConfigT, FrameT]):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    test_results: list[DQTestResult]

    _inline_results: FrameT | None = PrivateAttr(default=None)
    _external_results: FrameT | None = PrivateAttr(default=None)
    _passed_rows: FrameT | None = PrivateAttr(default=None)
    _failed_rows: FrameT | None = PrivateAttr(default=None)

    @computed_field
    @property
    def total_tests(self) -> int:
        return len(self.test_results)

    @computed_field
    @property
    def total_passed(self) -> int:
        return len([t for t in self.test_results if t.is_passed])

    @computed_field
    @property
    def total_failed(self) -> int:
        return self.total_tests - self.total_passed

    def set_inline_results(self, df: FrameT):
        self._inline_results = df
        return self

    def set_external_results(self, df: FrameT):
        self._external_results = df
        return self

    def set_passed_rows(self, df: FrameT):
        self._passed_rows = df
        return self

    def set_failed_rows(self, df: FrameT):
        self._failed_rows = df
        return self

    def get_inline_results(self):
        return self._inline_results

    def get_external_results(self):
        return self._external_results

    def get_passed_rows(self) -> FrameT:
        return self._passed_rows

    def get_failed_rows(self) -> FrameT:
        return self._failed_rows

    def get_json_summary(self, indent: int = 4) -> str:
        return self.model_dump_json(indent=indent)
