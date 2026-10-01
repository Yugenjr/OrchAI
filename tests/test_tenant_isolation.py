import pytest
from orchai.service.task_service import TaskService, TaskServiceError
from orchai.auth.models import AuthContext, Role, Permission

def test_tenant_isolation_task_read():
    service = TaskService()
    
    # Setup Contexts
    auth_a = AuthContext(user_id="u1", tenant_id="tenant_a", roles=[Role.DEVELOPER], permissions=[Permission.TASK_CREATE, Permission.TASK_READ])
    auth_b = AuthContext(user_id="u2", tenant_id="tenant_b", roles=[Role.DEVELOPER], permissions=[Permission.TASK_CREATE, Permission.TASK_READ])
    
    # Tenant A creates a task
    task_a = service.create_task("Task A", auth=auth_a)
    
    # Tenant A can read it
    read_a = service.get_task(task_a.id, auth=auth_a)
    assert read_a is not None
    
    # Tenant B cannot read it
    with pytest.raises(TaskServiceError) as exc:
        service.get_task(task_a.id, auth=auth_b)
    assert exc.value.code == "FORBIDDEN"

def test_tenant_isolation_audit_read():
    service = TaskService()
    auth_a = AuthContext(user_id="u1", tenant_id="tenant_a", roles=[Role.DEVELOPER], permissions=[Permission.TASK_CREATE, Permission.AUDIT_READ])
    auth_b = AuthContext(user_id="u2", tenant_id="tenant_b", roles=[Role.DEVELOPER], permissions=[Permission.TASK_CREATE, Permission.AUDIT_READ])
    
    task_a = service.create_task("Task A", auth=auth_a)
    
    events = service.get_events(task_a.id, auth=auth_a)
    assert len(events) > 0
    
    with pytest.raises(TaskServiceError) as exc:
        service.get_events(task_a.id, auth=auth_b)
    assert exc.value.code == "FORBIDDEN"

def test_admin_cross_tenant_access():
    service = TaskService()
    auth_a = AuthContext(user_id="u1", tenant_id="tenant_a", roles=[Role.DEVELOPER], permissions=[Permission.TASK_CREATE, Permission.TASK_READ])
    auth_admin = AuthContext(user_id="admin", tenant_id="global", roles=[Role.ADMIN], permissions=[Permission.TASK_READ, Permission.TENANT_CROSS_READ])
    
    task_a = service.create_task("Task A", auth=auth_a)
    
    # Admin can read Tenant A's task
    read_admin = service.get_task(task_a.id, auth=auth_admin)
    assert read_admin is not None
