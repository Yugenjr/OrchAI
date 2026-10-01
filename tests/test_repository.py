import pytest
import os
import shutil
from pathlib import Path
from orchai.core.models import Task, TaskState
from orchai.core.repository import TaskRepository

@pytest.fixture
def repo(tmp_path):
    r = TaskRepository(root_dir=str(tmp_path))
    yield r
    
def test_create_and_get_task(repo):
    task = Task(id="t-1", title="test task", description="")
    repo.create(task)
    
    t = repo.get("t-1")
    assert t is not None
    assert t.title == "test task"

def test_update_task(repo):
    task = Task(id="t-2", title="test task", description="")
    repo.create(task)
    
    task.status = TaskState.EXECUTING
    repo.update(task)
    
    t = repo.get("t-2")
    assert t.status == TaskState.EXECUTING

def test_list_tasks(repo):
    repo.create(Task(id="t-3", title="3", description=""))
    repo.create(Task(id="t-4", title="4", description=""))
    
    tasks = repo.list()
    assert len(tasks) == 2
