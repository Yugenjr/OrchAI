import pytest
import subprocess
from pathlib import Path
from orchai.context.git import GitService

@pytest.fixture
def temp_git_repo(tmp_path):
    # Initialize a temporary git repository
    subprocess.run(["git", "init"], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(tmp_path), check=True, capture_output=True)
    
    # Create initial commit
    file_path = tmp_path / "README.md"
    file_path.write_text("Hello World")
    subprocess.run(["git", "add", "README.md"], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(tmp_path), check=True, capture_output=True)
    
    return tmp_path

def test_git_service_clean_repo(temp_git_repo):
    service = GitService(str(temp_git_repo))
    assert service.is_repository() is True
    assert service.working_tree_clean() is True
    snapshot = service.snapshot()
    assert snapshot.working_tree_clean is True
    assert "README.md" in snapshot.tracked_files

def test_git_service_modified_file(temp_git_repo):
    # Modify the tracked file
    (temp_git_repo / "README.md").write_text("Modified")
    service = GitService(str(temp_git_repo))
    assert service.working_tree_clean() is False
    assert "README.md" in service.changed_files()
    assert "README.md" in service.unstaged_files()

def test_git_service_untracked_file(temp_git_repo):
    # Add an untracked file
    (temp_git_repo / "new_file.py").write_text("print('hello')")
    service = GitService(str(temp_git_repo))
    assert service.working_tree_clean() is False
    assert "new_file.py" in service.untracked_files()
    assert "new_file.py" in service.changed_files()

def test_git_service_non_repo(tmp_path):
    service = GitService(str(tmp_path))
    assert service.is_repository() is False
    with pytest.raises(RuntimeError):
        service.snapshot()
