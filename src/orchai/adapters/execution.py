from abc import ABC, abstractmethod
from typing import Optional
from orchai.core.models import Task, ExecutionRecord, ExecutionStatus

class ExecutionBoundary(ABC):
    """
    Abstract boundary for safely isolating agent execution.
    It does NOT assume the underlying executor is Antigravity.
    """
    @abstractmethod
    def prepare(self, task: Task) -> None:
        pass

    @abstractmethod
    def start(self, task: Task) -> ExecutionRecord:
        pass

    @abstractmethod
    def status(self, task: Task) -> ExecutionStatus:
        pass

    @abstractmethod
    def cancel(self, task: Task) -> None:
        pass

    @abstractmethod
    def collect_result(self, task: Task) -> ExecutionRecord:
        pass

    @abstractmethod
    def cleanup(self, task: Task) -> None:
        pass

class DryRunExecutionBoundary(ExecutionBoundary):
    """
    A safe placeholder implementation for Phase 3.
    It simulates an execution result without modifying the repository.
    """
    def prepare(self, task: Task) -> None:
        pass

    def start(self, task: Task) -> ExecutionRecord:
        # Returns a simulated running state. Real modifications should happen in tests via test fixtures.
        import uuid
        from datetime import datetime
        return ExecutionRecord(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            task_id=task.id,
            started_at=datetime.utcnow(),
            status=ExecutionStatus.COMPLETED
        )

    def status(self, task: Task) -> ExecutionStatus:
        return ExecutionStatus.COMPLETED

    def cancel(self, task: Task) -> None:
        pass

    def collect_result(self, task: Task) -> ExecutionRecord:
        return self.start(task)

    def cleanup(self, task: Task) -> None:
        pass
