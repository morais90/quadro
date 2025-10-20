from collections.abc import Callable
from functools import wraps
from typing import Any

import click
from rich.console import Console

from quadro.command import add_task
from quadro.command import complete_task
from quadro.command import delete_task
from quadro.command import get_task_markdown
from quadro.command import list_milestones
from quadro.command import list_tasks as get_all_tasks
from quadro.command import move_task
from quadro.command import show_task
from quadro.command import start_task
from quadro.command import update_task_from_markdown
from quadro.exceptions import TaskAlreadyDoneError
from quadro.exceptions import TaskAlreadyInProgressError
from quadro.exceptions import TaskNotFoundError
from quadro.models import TaskStatus
from quadro.renderer import Renderer


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
    """Quadro task management CLI.

    When invoked without a subcommand, defaults to listing all tasks.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_tasks)


@main.command("add")
@click.argument("title")
@click.option("--description", "-d", default=None, help="Task description")
@click.option("--milestone", default=None, help="Milestone name for the task")
@handle_exceptions
def add(title: str, description: str | None, milestone: str | None) -> None:
    """Create a new task with the specified title.

    Creates a new task in TODO status and saves it as a markdown file.
    Tasks can optionally be assigned to a milestone for organization and
    include a description for additional context.

    Examples
    --------
    ```bash
    $ quadro add "Implement login feature"
    $ quadro add "Add user authentication" --milestone mvp
    $ quadro add "Fix bug in parser" --description "Parser fails on edge case"
    $ quadro add "Add tests" -d "Write unit tests for auth module" --milestone mvp
    ```
    """
    console = Console()

    task = add_task(title, description, milestone)

    console.print(f"[green]✓[/green] Created task #{task.id}")


@main.command("list")
@click.option("--milestone", default=None, help="Filter tasks by milestone")
@click.option("--todo", is_flag=True, help="Show only TODO tasks")
@click.option("--progress", is_flag=True, help="Show only tasks in PROGRESS")
@click.option("--done", is_flag=True, help="Show only DONE tasks")
@handle_exceptions
def list_tasks(
    milestone: str | None,
    todo: bool,  # noqa: FBT001
    progress: bool,  # noqa: FBT001
    done: bool,  # noqa: FBT001
) -> None:
    """List all tasks with their status and details.

    Displays a formatted table of tasks showing ID, status, title, and
    milestone. Tasks can be filtered by milestone and status.

    Status filters can be combined to show multiple statuses. If no status
    filters are provided, all tasks are shown.

    This is the default command when running 'quadro' without arguments.

    Examples
    --------
    ```bash
    $ quadro list
    $ quadro list --milestone mvp
    $ quadro list --todo
    $ quadro list --todo --progress
    $ quadro list --done --milestone mvp
    ```
    """
    console = Console()
    renderer = Renderer(console)

    status_filters = []
    if todo:
        status_filters.append(TaskStatus.TODO)
    if progress:
        status_filters.append(TaskStatus.PROGRESS)
    if done:
        status_filters.append(TaskStatus.DONE)

    tasks = get_all_tasks(milestone=milestone, statuses=status_filters or None)

    if not tasks:
        console.print("[yellow]No tasks found. Create one with 'quadro add <title>'[/yellow]")
        return

    renderer.render_task_list(tasks)


@main.command("start")
@click.argument("task_id", type=int)
@handle_exceptions
def start(task_id: int) -> None:
    """Mark a task as in progress.

    Changes the status of a task from TODO to PROGRESS, indicating that
    work has begun on the task.

    If the task is already in progress or completed, a warning is displayed
    but the command exits successfully.

    Examples
    --------
    ```bash
    $ quadro start 1
    ```
    """
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
    """Mark a task as completed.

    Changes the status of a task to DONE and records the completion timestamp.
    This indicates that work on the task has been successfully finished.

    If the task is already completed, a warning is displayed but the command
    exits successfully.

    Examples
    --------
    ```bash
    $ quadro done 1
    ```
    """
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
    """Display detailed information about a specific task.

    Shows the complete details of a task including its ID, title, status,
    description, milestone, creation date, and completion date (if applicable).

    The task details are rendered in a formatted, color-coded display.

    Examples
    --------
    ```bash
    $ quadro show 1
    ```
    """
    console = Console()
    renderer = Renderer(console)

    try:
        task = show_task(task_id)
        renderer.render_task_detail(task)
    except TaskNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        raise SystemExit(1) from None


@main.command("milestones")
@handle_exceptions
def milestones() -> None:
    """Display a summary of all milestones and their tasks.

    Shows a grouped view of tasks organized by milestone, with counts of
    tasks in each status (TODO, PROGRESS, DONE) per milestone. Useful for
    tracking progress across different project phases or releases.

    Only tasks that have been assigned to a milestone are included in this
    view. Tasks without a milestone are not shown.

    Examples
    --------
    ```bash
    $ quadro milestones
    ```
    """
    console = Console()
    renderer = Renderer(console)

    try:
        milestone_tasks = list_milestones()
    except TaskNotFoundError:
        console.print("[yellow]No tasks found. Create one with 'quadro add <title>'[/yellow]")
        return

    if not milestone_tasks:
        console.print("[yellow]No milestones found. Add tasks with '--milestone <name>'[/yellow]")
        return

    renderer.render_milestones(milestone_tasks)


@main.command("move")
@click.argument("task_id", type=int)
@click.option("--to", required=True, help="Target milestone name (use 'root' for no milestone)")
@handle_exceptions
def move(task_id: int, to: str) -> None:
    """Move a task to a different milestone.

    Relocates a task's file from one milestone directory to another, or
    between the root directory and a milestone. The task's milestone field
    is updated accordingly.

    Use 'root' as the target to move a task out of any milestone to the
    root directory.

    Examples
    --------
    ```bash
    $ quadro move 1 --to mvp
    $ quadro move 5 --to root
    $ quadro move 3 --to v2.0
    ```
    """
    console = Console()

    try:
        old_milestone, new_milestone, new_path = move_task(task_id, to)
        console.print(
            f"[green]✓[/green] Moved task #{task_id} from {old_milestone} to {new_milestone}"
        )
        console.print(f"[dim]New location: {new_path}[/dim]")
    except TaskNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        raise SystemExit(1) from None


@main.command("edit")
@click.argument("task_id", type=int)
@handle_exceptions
def edit(task_id: int) -> None:
    """Edit a task's details in your default text editor.

    Opens the task's markdown file in the system's default editor (determined
    by the EDITOR environment variable). You can modify the title, description,
    status, and milestone. Changes are validated and saved upon editor exit.

    The task file is opened in markdown format with frontmatter containing
    metadata (status, milestone, created date) and the task body containing
    the title and description. If you exit the editor without saving or if
    no changes are made, the task remains unmodified.

    Invalid modifications (e.g., invalid status values) will be rejected with
    an error message.

    Examples
    --------
    ```bash
    $ quadro edit 1
    ```
    """
    console = Console()

    try:
        original_content = get_task_markdown(task_id)
    except TaskNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        raise SystemExit(1) from None

    edited_content = click.edit(original_content, extension=".md")

    if edited_content is None:
        console.print("[yellow]![/yellow] Edit cancelled, no changes made")
        return

    if edited_content.strip() == original_content.strip():
        console.print("[yellow]![/yellow] No changes made")
        return

    update_task_from_markdown(task_id, edited_content)
    console.print(f"[green]✓[/green] Updated task #{task_id}")


@main.command("delete")
@click.argument("task_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@handle_exceptions
def delete(task_id: int, yes: bool) -> None:  # noqa: FBT001
    """Delete a task permanently.

    Removes a task and its associated file from the filesystem. By default,
    displays the task details and prompts for confirmation before deletion
    to prevent accidental data loss.

    WARNING: This operation is irreversible. Once deleted, the task file is
    permanently removed from the filesystem and cannot be recovered.

    The confirmation prompt shows the full task details before deletion,
    allowing you to verify you're deleting the correct task. The confirmation
    defaults to 'No' for safety.

    Examples
    --------
    ```bash
    $ quadro delete 1
    $ quadro delete 1 --yes
    $ quadro delete 1 -y
    ```
    """
    console = Console()
    renderer = Renderer(console)

    try:
        task = show_task(task_id)
    except TaskNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        raise SystemExit(1) from None

    if not yes:
        console.print("[yellow]Task to be deleted:[/yellow]\n")
        renderer.render_task_detail(task)
        console.print()

        if not click.confirm("Are you sure you want to delete this task?", default=False):
            console.print("[yellow]![/yellow] Deletion cancelled")
            return

    try:
        _, file_path = delete_task(task_id)
    except TaskNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        raise SystemExit(1) from None

    console.print(f"[green]✓[/green] Deleted task #{task_id}: {task.title}")
    console.print(f"[dim]Removed: {file_path}[/dim]")
