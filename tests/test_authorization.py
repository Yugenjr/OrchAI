import pytest
from orchai.service.task_service import TaskService, TaskServiceError
from orchai.auth.models import AuthContext, Role, Permission

def test_authorization_permission_denial():
    service = TaskService()
    
    # AuthContext without TASK_CREATE
    auth_viewer = AuthContext(user_id="v1", tenant_id="t1", roles=[Role.VIEWER], permissions=[Permission.TASK_READ])
    
    with pytest.raises(TaskServiceError) as exc:
        service.create_task("Test", auth=auth_viewer)
    assert exc.value.code == "FORBIDDEN"

def test_task_ownership_assignment():
    service = TaskService()
    auth = AuthContext(user_id="u1", tenant_id="t1", roles=[Role.DEVELOPER], permissions=[Permission.TASK_CREATE, Permission.TASK_READ])
    
    task = service.create_task("Test", auth=auth)
    
    assert task.tenant_id == "t1"
    assert task.created_by == "u1"

def test_audit_event_attribution():
    service = TaskService()
    auth = AuthContext(user_id="u1", tenant_id="t1", roles=[Role.DEVELOPER], permissions=[Permission.TASK_CREATE, Permission.AUDIT_READ])
    
    task = service.create_task("Test", auth=auth)
    events = service.get_events(task.id, auth=auth)
    
    assert len(events) > 0
    event = events[0]
    assert event["actor_type"] == "USER"
    assert event["actor_id"] == "u1"
    assert event["tenant_id"] == "t1"
