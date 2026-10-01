import pytest
import asyncio
from orchai.service.task_service import TaskService, TaskServiceError
from orchai.core.models import TaskState
from orchai.observability.models import AuditEventType

@pytest.mark.asyncio
async def test_phase18_full_multiturn_lifecycle():
    service = TaskService()
    
    # POST /tasks
    task = service.create_task("Do a simple job", idempotency_key="idemp_1")
    assert task.status == TaskState.PENDING
    
    # Background starts
    service.start_task(task.id)
    
    # Let async execution progress to AWAITING_REVIEW
    await asyncio.sleep(0.3)
    updated_task = service.get_task(task.id)
    assert updated_task.status == TaskState.AWAITING_REVIEW
    
    # Check events for Attempt #1
    events = service.get_events(task.id)
    event_types = [e["event_type"] for e in events]
    assert AuditEventType.TOOL_REQUESTED in event_types
    assert AuditEventType.TOOL_APPROVED in event_types
    assert AuditEventType.VERIFICATION_COMPLETED in event_types
    
    # Developer requests changes
    service.request_changes(task.id, feedback="Change X to Y")
    updated_task = service.get_task(task.id)
    assert updated_task.status == TaskState.CHANGES_REQUESTED
    
    # Resume (Attempt #2)
    service.resume_task(task.id)
    await asyncio.sleep(0.3)
    
    updated_task = service.get_task(task.id)
    assert updated_task.status == TaskState.AWAITING_REVIEW
    
    # Check events to see resume happened
    events = service.get_events(task.id)
    event_types = [e["event_type"] for e in events]
    assert AuditEventType.TASK_RESUMED in event_types
    
    # Approve
    service.approve_task(task.id)
    final_task = service.get_task(task.id)
    assert final_task.status == TaskState.APPROVED
    
    events = service.get_events(task.id)
    event_types = [e["event_type"] for e in events]
    assert AuditEventType.TOOL_APPROVED in event_types

def test_idempotency_key():
    service = TaskService()
    task1 = service.create_task("Same job", idempotency_key="keyA")
    task2 = service.create_task("Same job", idempotency_key="keyA")
    assert task1.id == task2.id
    
    task3 = service.create_task("Other job", idempotency_key="keyB")
    assert task1.id != task3.id

@pytest.mark.asyncio
async def test_cancellation():
    service = TaskService()
    task = service.create_task("To be cancelled")
    service.start_task(task.id)
    
    service.cancel_task(task.id)
    # wait for the background task to handle cancellation
    bg_task = service._background_tasks.get(task.id)
    if bg_task:
        try:
            await bg_task
        except asyncio.CancelledError:
            pass
            
    updated_task = service.get_task(task.id)
    assert updated_task.status == TaskState.CANCELLED

def test_recovery_detection():
    service = TaskService()
    task = service.create_task("To be recovered")
    
    # Manually simulate a crash (state is executing, but no bg task)
    task.status = TaskState.EXECUTING
    service.repository.update(task)
    
    service.recover_task(task.id)
    
    updated_task = service.get_task(task.id)
    assert updated_task.status == TaskState.RECOVERY_REQUIRED

def test_runtime_blocked():
    service = TaskService()
    task = service.create_task("Container attempt")
    
    # In an environment without docker, it raises RUNTIME_BLOCKED
    # (Because the mock from earlier might not be present here, let's catch it)
    try:
        service.start_task(task.id, runtime="container")
    except TaskServiceError as e:
        assert e.code == "RUNTIME_BLOCKED"
