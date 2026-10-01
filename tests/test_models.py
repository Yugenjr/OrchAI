import pytest
from pydantic import ValidationError
from orchai.core.models import (
    Task, TaskState, AgentEvent, AgentEventType,
    VerificationResult
)

def test_task_model_validation():
    task = Task(
        id="t-1",
        title="Test Task",
        description="A test task"
    )
    assert task.status == TaskState.PENDING
    assert task.risk_level == 0
    
    with pytest.raises(ValidationError):
        Task(id="t-2", title="Missing description")

def test_agent_event_validation():
    event = AgentEvent(
        event_type=AgentEventType.TASK_STARTED,
        source="System"
    )
    assert event.event_type == AgentEventType.TASK_STARTED
    
    with pytest.raises(ValidationError):
        AgentEvent(event_type="INVALID_TYPE", source="System")

def test_verification_result_validation():
    vr = VerificationResult(
        passed=True,
        tests_run=5,
        tests_passed=5,
        summary="All tests passed"
    )
    assert vr.passed is True
    assert vr.tests_failed == 0
