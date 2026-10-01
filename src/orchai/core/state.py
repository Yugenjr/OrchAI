from typing import Dict, List, Set
from orchai.core.models import TaskState

class InvalidStateTransitionError(Exception):
    pass

class TaskStateMachine:
    def __init__(self):
        self._valid_transitions: Dict[TaskState, Set[TaskState]] = {
            TaskState.PENDING: {TaskState.ANALYZING, TaskState.CANCELLED, TaskState.READY_FOR_EXECUTION},
            TaskState.ANALYZING: {TaskState.PLANNED, TaskState.FAILED},
            TaskState.PLANNED: {TaskState.AWAITING_APPROVAL, TaskState.APPROVED, TaskState.FAILED},
            TaskState.AWAITING_APPROVAL: {TaskState.APPROVED, TaskState.REJECTED},
            TaskState.APPROVED: {TaskState.READY_FOR_EXECUTION},
            TaskState.READY_FOR_EXECUTION: {TaskState.EXECUTING, TaskState.FAILED, TaskState.CANCELLED},
            TaskState.EXECUTING: {TaskState.VERIFYING, TaskState.FAILED, TaskState.CANCELLED},
            TaskState.VERIFYING: {TaskState.COMPLETED, TaskState.FAILED, TaskState.RETRYING, TaskState.AWAITING_REVIEW, TaskState.CANCELLED},
            TaskState.FAILED: set(),
            TaskState.RETRYING: {TaskState.READY_FOR_EXECUTION, TaskState.FAILED},
            TaskState.AWAITING_REVIEW: {TaskState.APPROVED, TaskState.REJECTED, TaskState.CHANGES_REQUESTED},
            TaskState.REJECTED: {TaskState.ROLLED_BACK},
            TaskState.ROLLED_BACK: set(),
            TaskState.CHANGES_REQUESTED: {TaskState.READY_FOR_EXECUTION, TaskState.EXECUTING, TaskState.REJECTED, TaskState.CANCELLED},
            TaskState.COMPLETED: set(),
            TaskState.CANCELLED: set()
        }
        
    def validate_transition(self, current_state: TaskState, new_state: TaskState) -> None:
        """Validate if a transition from current_state to new_state is allowed."""
        if new_state not in self._valid_transitions.get(current_state, set()):
            raise InvalidStateTransitionError(
                f"Invalid transition from {current_state.value} to {new_state.value}"
            )
