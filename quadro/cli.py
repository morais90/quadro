from datetime import UTC
from datetime import datetime

import click
from rich.console import Console

from quadro.models import Task
from quadro.models import TaskStatus
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
def list_tasks() -> None:
    console = Console()
    console.print("List command not yet implemented")
