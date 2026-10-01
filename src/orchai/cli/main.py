import os
import subprocess
import json
import uuid
import typer
from pathlib import Path
from orchai import __version__
from orchai.core.config import OrchAIConfig
from orchai.core.models import Task, TaskState
from orchai.core.repository import TaskRepository
from orchai.core.state import TaskStateMachine, InvalidStateTransitionError
from orchai.context.git import GitService

app = typer.Typer(help="OrchAI: The orchestration layer for AI coding agents.", no_args_is_help=True)
task_app = typer.Typer(help="Manage OrchAI tasks.")
git_app = typer.Typer(help="Observe Git repository state.")

app.add_typer(task_app, name="task")
app.add_typer(git_app, name="git")

ORCHAI_DIR = ".orchai"

@app.command()
def init():
    """Initialize a new OrchAI project in the current directory."""
    orchai_path = Path(ORCHAI_DIR)
    
    # Detect Git
    try:
        result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
        if result.returncode != 0:
            typer.echo("Error: Current directory is not a Git repository. Git is required for OrchAI.", err=True)
            raise typer.Exit(code=1)
    except FileNotFoundError:
        typer.echo("Error: Git executable not found.", err=True)
        raise typer.Exit(code=1)

    if orchai_path.exists():
        typer.echo("Error: .orchai directory already exists. Project already initialized.", err=True)
        raise typer.Exit(code=1)

    # Create directories
    (orchai_path / "tasks").mkdir(parents=True)
    (orchai_path / "memory").mkdir(parents=True)
    (orchai_path / "logs").mkdir(parents=True)

    # Create config
    config = OrchAIConfig(
        project_name=Path.cwd().name,
        project_root=str(Path.cwd()),
        policy={
            "allowed_paths": ["src/**", "tests/**"],
            "forbidden_paths": [".env", ".git/**"],
            "approval_required_paths": []
        }
    )

    with open(orchai_path / "config.json", "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    typer.echo("Initialized OrchAI project.")
    typer.echo("Created .orchai/ with config.json, tasks/, memory/, and logs/.")

@app.command()
def version():
    """Print the version of OrchAI."""
    typer.echo(f"OrchAI version: {__version__}")

@git_app.command("status")
def git_status():
    """Observe current Git repository state."""
    service = GitService(str(Path.cwd()))
    if not service.is_repository():
        typer.echo("Not a Git repository.", err=True)
        raise typer.Exit(1)
        
    typer.echo("Repository")
    typer.echo("-" * 20)
    typer.echo(f"Branch: {service.current_branch()}")
    typer.echo(f"HEAD:   {service.head_sha()[:7]}")
    clean_str = "yes" if service.working_tree_clean() else "no"
    typer.echo(f"Clean:  {clean_str}")
    typer.echo(f"\nTracked files:\n{len(service.tracked_files())}")
    if not service.working_tree_clean():
        typer.echo(f"\nChanged files:\n{len(service.changed_files())}")

@git_app.command("snapshot")
def git_snapshot():
    """Generate a pre-execution Git snapshot."""
    service = GitService(str(Path.cwd()))
    if not service.is_repository():
        typer.echo("Not a Git repository.", err=True)
        raise typer.Exit(1)
    snapshot = service.snapshot()
    typer.echo(snapshot.model_dump_json(indent=2))

@task_app.command("create")
def task_create(objective: str):
    """Create a new task."""
    if not Path(ORCHAI_DIR).exists():
        typer.echo("Error: Not an OrchAI project. Run 'orchai init' first.", err=True)
        raise typer.Exit(code=1)
        
    repo = TaskRepository()
    task_id = f"tsk_{uuid.uuid4().hex[:8]}"
    
    task = Task(
        id=task_id,
        title=objective,
        description=f"Automated task for: {objective}"
    )
    repo.create(task)
    
    typer.echo("Task created.")
    typer.echo(f"ID: {task_id}")
    typer.echo(f"Status: {task.status.value}")

@task_app.command("list")
def task_list():
    """List all tasks."""
    repo = TaskRepository()
    tasks = repo.list()
    if not tasks:
        typer.echo("No tasks found.")
        return
    for t in tasks:
        typer.echo(f"[{t.status.value}] {t.id} - {t.title}")

@task_app.command("show")
def task_show(task_id: str):
    """Show details of a specific task."""
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        typer.echo(f"Task {task_id} not found.", err=True)
        raise typer.Exit(code=1)
    
    typer.echo(f"ID: {task.id}")
    typer.echo(f"Title: {task.title}")
    typer.echo(f"Status: {task.status.value}")
    typer.echo(f"Expected Scope: {task.expected_scope}")

@task_app.command("inspect")
def task_inspect(task_id: str):
    """Inspect task execution state and snapshots."""
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        typer.echo(f"Task {task_id} not found.", err=True)
        raise typer.Exit(code=1)
    
    typer.echo(f"Task ID: {task.id} [{task.status.value}]")
    if task.pre_execution_snapshot:
        typer.echo(f"Pre-execution HEAD: {task.pre_execution_snapshot.head_sha[:7]}")
    else:
        typer.echo("No pre-execution snapshot captured.")

@task_app.command("status")
def task_status(task_id: str):
    """Show status of a specific task."""
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        typer.echo(f"Task {task_id} not found.", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Task {task_id} is {task.status.value}")

@task_app.command("plan")
def task_plan(task_id: str):
    """Plan a task (deterministic rule-based MVP)."""
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        typer.echo(f"Task {task_id} not found.", err=True)
        raise typer.Exit(code=1)
        
    sm = TaskStateMachine()
    try:
        sm.validate_transition(task.status, TaskState.ANALYZING)
        task.status = TaskState.ANALYZING
        repo.update(task)
        
        sm.validate_transition(task.status, TaskState.PLANNED)
        task.status = TaskState.PLANNED
        # Deterministic dummy planning
        task.expected_scope = ["src/**", "tests/**"]
        task.approval_required = True
        repo.update(task)
        
        # Automatically move to AWAITING_APPROVAL if required
        if task.approval_required:
            sm.validate_transition(task.status, TaskState.AWAITING_APPROVAL)
            task.status = TaskState.AWAITING_APPROVAL
            repo.update(task)
            
    except InvalidStateTransitionError as e:
        typer.echo(f"Error transitioning state: {e}", err=True)
        raise typer.Exit(code=1)
        
    typer.echo("Note: Planning is currently rule-based.")
    typer.echo(f"Task {task.id} planned.")
    typer.echo(f"Expected scope: {task.expected_scope}")
    typer.echo(f"New status: {task.status.value}")

@task_app.command("approve")
def task_approve(task_id: str):
    """Approve a task for execution."""
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        typer.echo(f"Task {task_id} not found.", err=True)
        raise typer.Exit(code=1)
        
    sm = TaskStateMachine()
    git_service = GitService(str(Path.cwd()))
    
    try:
        # Assuming AWAITING_APPROVAL or AWAITING_REVIEW
        if task.status == TaskState.AWAITING_APPROVAL:
            sm.validate_transition(task.status, TaskState.APPROVED)
            task.status = TaskState.APPROVED
            repo.update(task)
        elif task.status == TaskState.AWAITING_REVIEW:
            sm.validate_transition(task.status, TaskState.APPROVED)
            task.status = TaskState.APPROVED
            repo.update(task)
        elif task.status != TaskState.APPROVED:
            typer.echo(f"Task is in {task.status.value}, cannot approve.", err=True)
            raise typer.Exit(code=1)
            
        # Move to READY_FOR_EXECUTION
        if not git_service.is_repository():
            typer.echo("Error: Execution requires a Git repository.", err=True)
            raise typer.Exit(code=1)
            
        if not git_service.working_tree_clean():
            typer.echo("Working tree contains uncommitted changes. Please commit or stash them before executing.", err=True)
            raise typer.Exit(code=1)
            
        sm.validate_transition(task.status, TaskState.READY_FOR_EXECUTION)
        task.status = TaskState.READY_FOR_EXECUTION
        task.pre_execution_snapshot = git_service.snapshot()
        repo.update(task)
        
        typer.echo(f"Task {task_id} approved. Pre-execution snapshot captured.")
        typer.echo(f"Status is now {task.status.value}. Ready for agent adapter.")
    except InvalidStateTransitionError as e:
        typer.echo(f"Error: {e}", err=True)

@task_app.command("reject")
def task_reject(task_id: str):
    """Reject a task."""
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        typer.echo(f"Task {task_id} not found.", err=True)
        raise typer.Exit(code=1)
        
    sm = TaskStateMachine()
    try:
        if task.status in [TaskState.AWAITING_APPROVAL, TaskState.AWAITING_REVIEW]:
            sm.validate_transition(task.status, TaskState.REJECTED)
            task.status = TaskState.REJECTED
            repo.update(task)
            typer.echo(f"Task {task_id} rejected. Status is now {task.status.value}.")
        else:
            typer.echo(f"Task is in {task.status.value}, cannot reject.", err=True)
    except InvalidStateTransitionError as e:
        typer.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    app()
