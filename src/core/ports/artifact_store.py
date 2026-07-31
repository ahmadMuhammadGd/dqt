from abc import ABC, abstractmethod

from core.models.execution import DQExecutionResult


class ArtifactStore(ABC):

    @abstractmethod
    def save(
        self,
        result: DQExecutionResult,
    ) -> None:
        raise NotImplementedError
