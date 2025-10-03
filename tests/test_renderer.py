from datetime import UTC
from datetime import datetime
from io import StringIO
from textwrap import dedent

from rich.console import Console

from quadro.models import Task
from quadro.models import TaskStatus
from quadro.renderer import Renderer


def test_status_symbol() -> None:
    assert Renderer.status_symbol(TaskStatus.DONE) == "✓"
    assert Renderer.status_symbol(TaskStatus.PROGRESS) == "▶"
    assert Renderer.status_symbol(TaskStatus.TODO) == "○"


def test_render_task_list() -> None:
    output = StringIO()
    console = Console(file=output)
    renderer = Renderer(console=console)

    tasks = [
        Task(
            id=1,
            title="Test task 1",
            description="Description 1",
            status=TaskStatus.TODO,
            milestone="mvp",
            created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
            completed=None,
        ),
        Task(
            id=2,
            title="Test task 2",
            description="Description 2",
            status=TaskStatus.PROGRESS,
            milestone="mvp",
            created=datetime(2025, 10, 3, 11, 0, 0, tzinfo=UTC),
            completed=None,
        ),
        Task(
            id=3,
            title="Test task 3",
            description="Description 3",
            status=TaskStatus.DONE,
            milestone=None,
            created=datetime(2025, 10, 3, 12, 0, 0, tzinfo=UTC),
            completed=datetime(2025, 10, 3, 13, 0, 0, tzinfo=UTC),
        ),
    ]

    renderer.render_task_list(tasks)

    result = output.getvalue()

    expected = dedent("""
        ┏━━━━━━━━━━━┳━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
        ┃ Milestone ┃ ID ┃ Title       ┃ Status     ┃
        ┡━━━━━━━━━━━╇━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
        │ mvp       │ 1  │ Test task 1 │ ○ todo     │
        │ mvp       │ 2  │ Test task 2 │ ▶ progress │
        │ -         │ 3  │ Test task 3 │ ✓ done     │
        └───────────┴────┴─────────────┴────────────┘

        3 tasks • 1 done • 1 in progress • 1 todo
    """)

    assert result.strip() == expected.strip()
