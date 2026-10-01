import pytest
from orchai.core.models import TaskState
from orchai.core.state import TaskStateMachine, InvalidStateTransitionError

def test_valid_state_transitions():
    sm = TaskStateMachine()
    # PENDING -> ANALYZING is valid
    sm.validate_transition(TaskState.PENDING, TaskState.ANALYZING)
    # EXECUTING -> VERIFYING is valid
    sm.validate_transition(TaskState.EXECUTING, TaskState.VERIFYING)

def test_invalid_state_transitions():
    sm = TaskStateMachine()
    
    with pytest.raises(InvalidStateTransitionError):
        # PENDING -> COMPLETED is invalid
        sm.validate_transition(TaskState.PENDING, TaskState.COMPLETED)
        
    with pytest.raises(InvalidStateTransitionError):
        # COMPLETED -> EXECUTING is invalid
        sm.validate_transition(TaskState.COMPLETED, TaskState.EXECUTING)
