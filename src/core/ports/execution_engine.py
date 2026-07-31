from abc import ABC, abstractmethod

from core.models.enums import DQExecutionMode, DQTestScope


class ExecutionEngine(ABC):
    @abstractmethod
    def run(
        self,
        scope: DQTestScope | None = None,
        execution_mode: DQExecutionMode | None = None,
    ):
        raise NotImplementedError
