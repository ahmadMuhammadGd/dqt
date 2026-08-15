from abc import ABC, abstractmethod
from dqt.execution import DQExecutionResult


class ArtifactStorePersist(ABC):

    @abstractmethod
    def persist(
        self,
        result: DQExecutionResult,
    ) -> None:
        raise NotImplementedError
