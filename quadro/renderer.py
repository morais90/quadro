from rich.console import Console
from rich.table import Table

from quadro.models import Task
from quadro.models import TaskStatus


class Renderer:
    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    @staticmethod
    def status_symbol(status: TaskStatus) -> str:
        if status == TaskStatus.DONE:
            return "✓"
        if status == TaskStatus.PROGRESS:
            return "▶"
        return "○"

    def render_task_list(self, tasks: list[Task], milestone_filter: str | None = None) -> None:
        filtered_tasks = tasks
        if milestone_filter is not None:
            filtered_tasks = [t for t in tasks if t.milestone == milestone_filter]

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Milestone", style="cyan")
        table.add_column("ID", style="yellow")
        table.add_column("Title", style="white")
        table.add_column("Status", style="green")

        for task in filtered_tasks:
            milestone_display = task.milestone or "-"
            status_display = f"{self.status_symbol(task.status)} {task.status.value}"
            table.add_row(milestone_display, str(task.id), task.title, status_display)

        self.console.print(table)

        total = len(filtered_tasks)
        done_count = sum(1 for t in filtered_tasks if t.status == TaskStatus.DONE)
        progress_count = sum(1 for t in filtered_tasks if t.status == TaskStatus.PROGRESS)
        todo_count = sum(1 for t in filtered_tasks if t.status == TaskStatus.TODO)

        summary = (
            f"{total} tasks • {done_count} done • {progress_count} in progress • {todo_count} todo"
        )
        self.console.print(f"\n[dim]{summary}[/dim]")
