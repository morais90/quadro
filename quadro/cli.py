from collections.abc import Callable
from functools import wraps
from typing import Any

import click
from rich.console import Console

from quadro.commands.add import add_task
from quadro.commands.done import complete_task
from quadro.commands.list import list_tasks as get_all_tasks
from quadro.commands.start import start_task
from quadro.exceptions import TaskAlreadyDoneError
from quadro.exceptions import TaskAlreadyInProgressError
from quadro.exceptions import TaskNotFoundError
from quadro.models import Task
from quadro.renderer import Renderer
from quadro.storage import TaskStorage


def handle_exceptions(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to handle common exceptions with user-friendly messages."""

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        console = Console()
        try:
            return f(*args, **kwargs)
        except PermissionError as e:
            console.print("[red]✗[/red] Permission denied")
            console.print(f"Cannot access: {e.filename or 'tasks directory'}")
            console.print("Check that you have read/write permissions for the tasks directory.")
            raise SystemExit(1) from e
        except FileNotFoundError as e:
            console.print("[red]✗[/red] File not found")
            console.print(f"Missing file: {e.filename or 'unknown'}")
            console.print("The task file may have been deleted or moved.")
            raise SystemExit(1) from e
        except OSError as e:
            console.print("[red]✗[/red] System error")
            console.print(f"{e}")
            console.print("Check disk space and file permissions.")
            raise SystemExit(1) from e
        except ValueError as e:
            console.print("[red]✗[/red] Invalid data")
            console.print(f"{e}")
            raise SystemExit(1) from e
        except Exception as e:
            console.print("[red]✗[/red] Unexpected error")
            console.print(f"{type(e).__name__}: {e}")
            console.print("Please report this issue if it persists.")
            raise SystemExit(1) from e

    return wrapper


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_tasks)


@main.command("add")
@click.argument("title")
@click.option("--milestone", default=None, help="Milestone name for the task")
@handle_exceptions
def add(title: str, milestone: str | None) -> None:
    console = Console()

    task_id, file_path = add_task(title, milestone)

    console.print(f"[green]✓[/green] Created task #{task_id}")
    console.print(f"[dim]File: {file_path}[/dim]")


@main.command("list")
@click.option("--milestone", default=None, help="Filter tasks by milestone")
@handle_exceptions
def list_tasks(milestone: str | None) -> None:
    console = Console()
    renderer = Renderer(console)

    tasks = get_all_tasks()

    if not tasks:
        console.print("[yellow]No tasks found. Create one with 'quadro add <title>'[/yellow]")
        return

    renderer.render_task_list(tasks, milestone_filter=milestone)


@main.command("start")
@click.argument("task_id", type=int)
@handle_exceptions
def start(task_id: int) -> None:
    console = Console()

    try:
        task = start_task(task_id)
        console.print(f"[green]✓[/green] Started task #{task_id}: {task.title}")
    except TaskNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        raise SystemExit(1) from None
    except (TaskAlreadyInProgressError, TaskAlreadyDoneError) as e:
        console.print(f"[yellow]![/yellow] {e}")


@main.command("done")
@click.argument("task_id", type=int)
@handle_exceptions
def done(task_id: int) -> None:
    console = Console()

    try:
        task = complete_task(task_id)
        console.print(f"[green]✓[/green] Completed task #{task_id}: {task.title}")
    except TaskNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        raise SystemExit(1) from None
    except TaskAlreadyDoneError as e:
        console.print(f"[yellow]![/yellow] {e}")


@main.command("show")
@click.argument("task_id", type=int)
@handle_exceptions
def show(task_id: int) -> None:
    console = Console()
    storage = TaskStorage()
    renderer = Renderer(console)

    task = storage.load_task(task_id)

    if task is None:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        raise SystemExit(1)

    renderer.render_task_detail(task)


@main.command("milestones")
@handle_exceptions
def milestones() -> None:
    console = Console()
    storage = TaskStorage()
    renderer = Renderer(console)

    tasks = storage.load_all_tasks()

    if not tasks:
        console.print("[yellow]No tasks found. Create one with 'quadro add <title>'[/yellow]")
        return

    milestone_tasks = [t for t in tasks if t.milestone is not None]
    if not milestone_tasks:
        console.print("[yellow]No milestones found. Add tasks with '--milestone <name>'[/yellow]")
        return

    renderer.render_milestones(tasks)


@main.command("move")
@click.argument("task_id", type=int)
@click.option("--to", required=True, help="Target milestone name (use 'root' for no milestone)")
@handle_exceptions
def move(task_id: int, to: str) -> None:
    console = Console()
    storage = TaskStorage()

    task = storage.load_task(task_id)

    if task is None:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        raise SystemExit(1)

    old_milestone = task.milestone or "root"
    to_milestone = None if to == "root" else to

    new_path = storage.move_task(task_id, to_milestone)
    new_milestone = to_milestone or "root"

    console.print(f"[green]✓[/green] Moved task #{task_id} from {old_milestone} to {new_milestone}")
    console.print(f"[dim]New location: {new_path}[/dim]")


@main.command("edit")
@click.argument("task_id", type=int)
@handle_exceptions
def edit(task_id: int) -> None:
    console = Console()
    storage = TaskStorage()

    task = storage.load_task(task_id)

    if task is None:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        raise SystemExit(1)

    original_content = task.to_markdown()

    edited_content = click.edit(original_content, extension=".md")

    if edited_content is None:
        console.print("[yellow]![/yellow] Edit cancelled, no changes made")
        return

    if edited_content.strip() == original_content.strip():
        console.print("[yellow]![/yellow] No changes made")
        return

    updated_task = Task.from_markdown(edited_content, task_id, "edited")
    storage.save_task(updated_task)
    console.print(f"[green]✓[/green] Updated task #{task_id}")
