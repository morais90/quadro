from datetime import UTC
from datetime import datetime

import click
from rich.console import Console

from quadro.models import Task
from quadro.models import TaskStatus
from quadro.renderer import Renderer
from quadro.storage import TaskStorage


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_tasks)


@main.command("add")
@click.argument("title")
@click.option("--milestone", default=None, help="Milestone name for the task")
def add(title: str, milestone: str | None) -> None:
    console = Console()
    storage = TaskStorage()

    task_id = storage.get_next_id()
    task = Task(
        id=task_id,
        title=title,
        description="",
        status=TaskStatus.TODO,
        milestone=milestone,
        created=datetime.now(UTC),
        completed=None,
    )

    file_path = storage.save_task(task)

    console.print(f"[green]✓[/green] Created task #{task_id}")
    console.print(f"[dim]File: {file_path}[/dim]")


@main.command("list")
@click.option("--milestone", default=None, help="Filter tasks by milestone")
def list_tasks(milestone: str | None) -> None:
    console = Console()
    storage = TaskStorage()
    renderer = Renderer(console)

    tasks = storage.load_all_tasks()

    if not tasks:
        console.print("[yellow]No tasks found. Create one with 'quadro add <title>'[/yellow]")
        return

    renderer.render_task_list(tasks, milestone_filter=milestone)


@main.command("start")
@click.argument("task_id", type=int)
def start(task_id: int) -> None:
    console = Console()
    storage = TaskStorage()

    task = storage.load_task(task_id)

    if task is None:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        raise SystemExit(1)

    if task.status == TaskStatus.PROGRESS:
        console.print(f"[yellow]![/yellow] Task #{task_id} is already in progress")
        return

    if task.status == TaskStatus.DONE:
        console.print(f"[yellow]![/yellow] Task #{task_id} is already done")
        return

    task.status = TaskStatus.PROGRESS
    storage.save_task(task)

    console.print(f"[green]✓[/green] Started task #{task_id}: {task.title}")


@main.command("done")
@click.argument("task_id", type=int)
def done(task_id: int) -> None:
    console = Console()
    storage = TaskStorage()

    task = storage.load_task(task_id)

    if task is None:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        raise SystemExit(1)

    if task.status == TaskStatus.DONE:
        console.print(f"[yellow]![/yellow] Task #{task_id} is already done")
        return

    task.status = TaskStatus.DONE
    task.completed = datetime.now(UTC)
    storage.save_task(task)

    console.print(f"[green]✓[/green] Completed task #{task_id}: {task.title}")


@main.command("show")
@click.argument("task_id", type=int)
def show(task_id: int) -> None:
    console = Console()
    storage = TaskStorage()
    renderer = Renderer(console)

    task = storage.load_task(task_id)

    if task is None:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        raise SystemExit(1)

    renderer.render_task_detail(task)
