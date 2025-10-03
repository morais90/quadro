from rich.console import Console

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
