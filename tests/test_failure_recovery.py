import pytest
from orchai.runtime.recovery import RecoveryManager
from orchai.core.models import Task, TaskState
from orchai.core.repository import TaskRepository
from orchai.runtime.ledger import ExecutionLedger
import os
import shutil

@pytest.fixture
def repo(tmp_path):
    r = TaskRepository(str(tmp_path / "tasks"))
    t = Task(id="t1", title="test", description="test")
    t.status = TaskState.EXECUTING
    r.create(t)
    return r

@pytest.fixture
def ledger(tmp_path):
    return ExecutionLedger(str(tmp_path / "ledger"))

def test_recovery_scan_stale_executions(repo, ledger):
    mgr = RecoveryManager(repo, ledger)
    stale = mgr.scan_for_stale_executions()
    
    assert "t1" in stale
    t = repo.get("t1")
    assert t.status == TaskState.RECOVERY_REQUIRED

def test_interrupted_write_atomic(ledger):
    import uuid
    # Mocking interrupted write
    pass
