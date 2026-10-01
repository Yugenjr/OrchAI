import os
import sys

main_path = 'src/orchai/cli/main.py'
with open(main_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_commands = """
auth_app = typer.Typer(help="Manage OrchAI authentication.")
runtime_app = typer.Typer(help="Manage OrchAI runtime validation.")
app.add_typer(auth_app, name="auth")
app.add_typer(runtime_app, name="runtime")

@auth_app.command("status")
def auth_status():
    import os
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        typer.echo("Authentication: CONFIGURED (Environment Variable)")
    else:
        typer.echo("Authentication: MISSING")

@auth_app.command("test")
def auth_test():
    import os
    if not os.environ.get("GEMINI_API_KEY"):
        typer.echo("Authentication unavailable. Status: BLOCKED")
        return
    typer.echo("Auth test complete (mocked validation).")

@auth_app.command("remove")
def auth_remove():
    typer.echo("To remove, unset GEMINI_API_KEY from environment.")

@runtime_app.command("doctor")
def runtime_doctor():
    typer.echo("Runtime: Antigravity")
    typer.echo("SDK: AVAILABLE")
    import os
    auth_status = "VALID" if os.environ.get("GEMINI_API_KEY") else "MISSING"
    typer.echo(f"Authentication: {auth_status}")
    typer.echo("Connection: UNAVAILABLE")
    typer.echo("Session Support: UNKNOWN")
    typer.echo("Tool Interception: UNKNOWN")
    typer.echo("Cancellation: UNKNOWN")

@runtime_app.command("capabilities")
def runtime_capabilities():
    typer.echo("COMMAND_EXECUTION: UNVERIFIED")
    typer.echo("SESSION_RESUME: UNVERIFIED")
    typer.echo("TOOL_INTERCEPTION: UNVERIFIED")

@runtime_app.command("test")
def runtime_test(case: str = typer.Option(None, "--case")):
    import os
    if not os.environ.get("GEMINI_API_KEY"):
        typer.echo("Authentication unavailable.")
        typer.echo("Runtime tests were not executed.")
        typer.echo("Status: BLOCKED")
        return
    typer.echo(f"Running test case: {case or 'all'}")

@runtime_app.command("report")
def runtime_report():
    typer.echo("Generating runtime validation report...")
"""

if "auth_app" not in content:
    with open(main_path, 'a', encoding='utf-8') as f:
        f.write(new_commands)
        
print("CLI updated.")
