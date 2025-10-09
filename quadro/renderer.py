from rich.console import Console
from rich.markdown import Markdown
from rich.progress_bar import ProgressBar
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

    def render_task_list(self, tasks: list[Task]) -> None:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Milestone", style="cyan")
        table.add_column("ID", style="yellow")
        table.add_column("Title", style="white")
        table.add_column("Status", style="green")

        for task in tasks:
            milestone_display = task.milestone or "-"
            status_display = f"{self.status_symbol(task.status)} {task.status.value}"
            table.add_row(milestone_display, str(task.id), task.title, status_display)

        self.console.print(table)

        total = len(tasks)
        done_count = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        progress_count = sum(1 for t in tasks if t.status == TaskStatus.PROGRESS)
        todo_count = sum(1 for t in tasks if t.status == TaskStatus.TODO)

        summary = (
            f"{total} tasks • {done_count} done • {progress_count} in progress • {todo_count} todo"
        )
        self.console.print(f"\n[dim]{summary}[/dim]")

    def render_task_detail(self, task: Task) -> None:
        self.console.print()
        self.console.print(f"[bold cyan]#{task.id}[/bold cyan]")

        status_text = f"{self.status_symbol(task.status)} {task.status.value}"
        self.console.print(f"[dim]Status:[/dim] {status_text}")

        if task.milestone:
            self.console.print(f"[dim]Milestone:[/dim] {task.milestone}")

        self.console.print(f"[dim]Created:[/dim] {task.created}")

        if task.completed:
            self.console.print(f"[dim]Completed:[/dim] {task.completed}")

        self.console.print()
        self.console.print(f"[bold]{task.title}[/bold]")

        self.console.print()
        self.console.print(Markdown(task.description))
        self.console.print()

    def render_milestones(self, tasks: list[Task]) -> None:
        milestone_data: dict[str, dict[str, int]] = {}
        for task in tasks:
            milestone_name = task.milestone or "No Milestone"
            if milestone_name not in milestone_data:
                milestone_data[milestone_name] = {"total": 0, "done": 0}
            milestone_data[milestone_name]["total"] += 1
            if task.status == TaskStatus.DONE:
                milestone_data[milestone_name]["done"] += 1

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Milestone", style="cyan")
        table.add_column("Tasks", style="yellow")
        table.add_column("Done", style="green")
        table.add_column("Progress", style="white")
        table.add_column("Completion", style="white")

        for milestone_name in sorted(milestone_data.keys()):
            data = milestone_data[milestone_name]
            total = data["total"]
            done = data["done"]
            completion_pct = (done / total * 100) if total > 0 else 0

            progress_bar = ProgressBar(total=total, completed=done, width=40)

            table.add_row(
                milestone_name,
                str(total),
                str(done),
                progress_bar,
                f"{completion_pct:.1f}%",
            )

        self.console.print(table)
