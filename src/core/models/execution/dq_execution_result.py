from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, computed_field

from core.models.config.execution_engine import ExecutionEngineConfig
from core.models.execution.dq_run import DQRun
from core.models.execution.dq_test_result import DQTestResult

ConfigT = TypeVar("ConfigT", bound=ExecutionEngineConfig)
FrameT = TypeVar("FrameT")


class DQExecutionResult(BaseModel, Generic[ConfigT, FrameT]):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    test_results: list[DQTestResult]
    run: DQRun[ConfigT, FrameT]

    _inline_results: FrameT | None = PrivateAttr(default=None)
    _external_results: FrameT | None = PrivateAttr(default=None)

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

    def get_inline_results(self):
        return self._inline_results

    def get_external_results(self):
        return self._external_results
