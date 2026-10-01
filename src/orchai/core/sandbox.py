from abc import ABC, abstractmethod

class ExecutionSandbox(ABC):
    """
    Abstract interface for execution isolation.
    NOTE: Currently an abstraction only. Does NOT provide security isolation.
    """
    @abstractmethod
    def prepare(self) -> None:
        pass

    @abstractmethod
    def execute(self, command: str) -> None:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
