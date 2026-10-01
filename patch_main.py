import sys

main_path = 'src/orchai/cli/main.py'
with open(main_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_imports = """
from orchai.memory.store import MemoryStore
from orchai.memory.manager import MemoryManager
from orchai.core.models import MemoryCategory, MemoryStatus

memory_app = typer.Typer(help="Manage OrchAI engineering memory.")
app.add_typer(memory_app, name="memory")
"""
if "memory_app" not in content:
    content = content.replace('app.add_typer(agent_app, name="agent")', 'app.add_typer(agent_app, name="agent")' + new_imports)

commands = """
@memory_app.command("add")
def memory_add(title: str, content: str, category: str = "ARCHITECTURE_DECISION"):
    store = MemoryStore()
    manager = MemoryManager(store)
    try:
        cat = MemoryCategory(category.upper())
    except ValueError:
        typer.echo(f"Invalid category: {category}", err=True)
        raise typer.Exit(1)
    
    entry = manager.add_decision(title, content, cat, [])
    typer.echo(f"Added memory: {entry.id}")
    if entry.status == MemoryStatus.CONFLICT:
        typer.echo("Warning: Conflict detected with existing memory.")

@memory_app.command("list")
def memory_list():
    store = MemoryStore()
    for e in store.list_all():
        typer.echo(f"[{e.type.value}] {e.id}: {e.title} ({e.status.value})")

@memory_app.command("search")
def memory_search(query: str):
    store = MemoryStore()
    manager = MemoryManager(store)
    results = manager.search(query)
    for e in results:
        typer.echo(f"[{e.type.value}] {e.id}: {e.title}")

@task_app.command("review")
def task_review(task_id: str):
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        raise typer.Exit(1)
    typer.echo(f"Task: {task.id} [{task.status.value}]")
    typer.echo("Review ready.")

@task_app.command("request-changes")
def task_request_changes(task_id: str, feedback: str):
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        raise typer.Exit(1)
    sm = TaskStateMachine()
    try:
        sm.validate_transition(task.status, TaskState.CHANGES_REQUESTED)
        task.status = TaskState.CHANGES_REQUESTED
        repo.update(task)
        typer.echo(f"Changes requested for task {task_id}.")
        
        # Add developer feedback memory
        store = MemoryStore()
        manager = MemoryManager(store)
        manager.add_decision(f"Feedback for {task_id}", feedback, MemoryCategory.DEVELOPER_FEEDBACK, [task_id])
    except InvalidStateTransitionError as e:
        typer.echo(str(e), err=True)

@task_app.command("approve-review")
def task_approve_review(task_id: str):
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        raise typer.Exit(1)
    sm = TaskStateMachine()
    try:
        if task.status == TaskState.AWAITING_REVIEW:
            task.status = TaskState.COMPLETED
            repo.update(task)
            typer.echo(f"Task {task_id} approved and COMPLETED.")
        else:
            typer.echo("Task not in AWAITING_REVIEW")
    except InvalidStateTransitionError as e:
        typer.echo(str(e), err=True)

@task_app.command("context")
def task_context(task_id: str):
    typer.echo("Context report would be displayed here.")
"""
if "memory_add" not in content:
    content = content + commands

with open(main_path, 'w', encoding='utf-8') as f:
    f.write(content)
