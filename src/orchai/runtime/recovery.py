from typing import List
from orchai.core.repository import TaskRepository
from orchai.runtime.ledger import ExecutionLedger
from orchai.core.models import TaskState, ExecutionStatus

class RecoveryManager:
    def __init__(self, task_repo: TaskRepository, ledger: ExecutionLedger):
        self.task_repo = task_repo
        self.ledger = ledger

    def scan_for_stale_executions(self) -> List[str]:
        stale_tasks = []
        tasks = self.task_repo.list()
        for task in tasks:
            if task.status == TaskState.EXECUTING:
                # Need to verify if the process is actually running
                # For this implementation, if OrchAI restarted, the process tracking is lost.
                # So any EXECUTING task upon startup is considered stale.
                task.status = TaskState.RECOVERY_REQUIRED
                self.task_repo.update(task)
                stale_tasks.append(task.id)
        return stale_tasks

    def mark_recovery(self, task_id: str):
        task = self.task_repo.get(task_id)
        if task and task.status == TaskState.EXECUTING:
            task.status = TaskState.RECOVERY_REQUIRED
            self.task_repo.update(task)
