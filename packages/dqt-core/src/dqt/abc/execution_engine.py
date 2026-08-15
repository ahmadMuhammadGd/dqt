from abc import ABC, abstractmethod
from typing import ClassVar, Dict, Generic, List, Set, TypeVar
from dqt.enums import DQExecutionMode, DQTestScope
from dqt.execution.dq_execution_result import DQExecutionResult
from dqt.types import Bind

FrameT = TypeVar("T")


class ExecutionEngine(ABC, Generic[FrameT]):
    run_uuid_column_name: str = "dq_run_uid"

    @abstractmethod
    def run(
        self,
        scope: DQTestScope | None = None,
        execution_mode: DQExecutionMode | None = None,
    ) -> DQExecutionResult:
        raise NotImplementedError

    @abstractmethod
    def get_run_ids(self, df: FrameT) -> Set[str]:
        raise NotImplementedError

    @abstractmethod
    def explain(self, df: FrameT, run_id_bind_map: Dict[str, List[Bind]]) -> FrameT:
        raise NotImplementedError
