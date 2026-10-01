import pytest
from orchai.service.task_service import TaskService, TaskServiceError
from orchai.auth.models import AuthContext, Role, Permission

def test_approval_authorization():
    service = TaskService()
    
    # Needs TASK_APPROVE
    auth_approver = AuthContext(user_id="u1", tenant_id="t1", roles=[Role.DEVELOPER], permissions=[Permission.TASK_CREATE, Permission.TASK_READ, Permission.TASK_APPROVE])
    auth_viewer = AuthContext(user_id="u2", tenant_id="t1", roles=[Role.VIEWER], permissions=[Permission.TASK_READ])
    auth_other_tenant = AuthContext(user_id="u3", tenant_id="t2", roles=[Role.DEVELOPER], permissions=[Permission.TASK_CREATE, Permission.TASK_READ, Permission.TASK_APPROVE])
    
    task = service.create_task("Test", auth=auth_approver)
    
    # Fast forward to AWAITING_REVIEW
    # We bypass start_task to directly test the state
    from orchai.core.models import TaskState
    task.status = TaskState.AWAITING_REVIEW
    service.repository.update(task)
    
    # Viewer cannot approve
    with pytest.raises(TaskServiceError) as exc:
        service.approve_task(task.id, auth=auth_viewer)
    assert exc.value.code == "FORBIDDEN"
    
    # Other tenant cannot approve
    with pytest.raises(TaskServiceError) as exc:
        service.approve_task(task.id, auth=auth_other_tenant)
    assert exc.value.code == "TASK_NOT_FOUND"
    
    # Authorized approver can
    service.approve_task(task.id, auth=auth_approver)
    
    updated_task = service.get_task(task.id, auth=auth_approver)
    assert updated_task.status == TaskState.APPROVED
