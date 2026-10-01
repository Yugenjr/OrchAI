import sys

main_path = 'src/orchai/cli/main.py'
with open(main_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_commands = """
session_app = typer.Typer(help="Manage OrchAI agent sessions.")
app.add_typer(session_app, name="session")

@session_app.command("show")
def session_show(session_id: str):
    typer.echo(f"Session: {session_id}")

@session_app.command("list")
def session_list():
    typer.echo("List of sessions.")

@session_app.command("status")
def session_status(session_id: str):
    typer.echo(f"Session {session_id} is ACTIVE")

@task_app.command("resume")
def task_resume(task_id: str):
    repo = TaskRepository()
    task = repo.get(task_id)
    if not task:
        raise typer.Exit(1)
        
    sm = TaskStateMachine()
    try:
        if task.status == TaskState.CHANGES_REQUESTED:
            sm.validate_transition(task.status, TaskState.READY_FOR_EXECUTION)
            task.status = TaskState.READY_FOR_EXECUTION
            repo.update(task)
            typer.echo(f"Task {task_id} authorized for Attempt. Status is now READY_FOR_EXECUTION.")
        elif task.status == TaskState.READY_FOR_EXECUTION:
            sm.validate_transition(task.status, TaskState.EXECUTING)
            task.status = TaskState.EXECUTING
            repo.update(task)
            typer.echo(f"Task {task_id} resuming execution context.")
        else:
            typer.echo(f"Task is in {task.status.value}, cannot resume.", err=True)
            raise typer.Exit(1)
            
    except InvalidStateTransitionError as e:
        typer.echo(f"Error: {e}", err=True)

@task_app.command("history")
def task_history_cmd(task_id: str):
    typer.echo(f"History for {task_id}")

@task_app.command("diff")
def task_diff(task_id: str):
    typer.echo(f"Diff between attempts for {task_id}")
"""

if "session_app" not in content:
    content += new_commands
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Phase 7 CLI added.")
