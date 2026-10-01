from abc import ABC, abstractmethod
from typing import Iterator, List
from orchai.core.models import (
    TaskRequest,
    AgentCapability,
    AgentEvent,
    AgentResult
)

class TaskContext(ABC):
    """Abstract representation of task context."""
    pass

class AgentAdapter(ABC):
    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def capabilities(self) -> List[AgentCapability]:
        pass

    @abstractmethod
    def prepare_task(self, request: TaskRequest, context: TaskContext) -> None:
        pass

    @abstractmethod
    def execute(self) -> AgentResult:
        pass

    @abstractmethod
    def stream_events(self) -> Iterator[AgentEvent]:
        pass

    @abstractmethod
    def collect_result(self) -> AgentResult:
        pass

    @abstractmethod
    def cancel(self) -> None:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
