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


def test_render_task_detail() -> None:
    output = StringIO()
    console = Console(file=output)
    renderer = Renderer(console=console)

    task = Task(
        id=42,
        title="Fix authentication bug",
        description="Users cannot log in with **SSO credentials**",
        status=TaskStatus.PROGRESS,
        milestone="v1.0",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
        completed=None,
    )

    renderer.render_task_detail(task)

    result = output.getvalue()

    expected = dedent("""
        #42
        Status: ▶ progress
        Milestone: v1.0
        Created: 2025-10-03 10:00:00+00:00

        Fix authentication bug

        Users cannot log in with SSO credentials
    """)

    assert result.strip() == expected.strip()


def test_render_task_detail_completed() -> None:
    output = StringIO()
    console = Console(file=output)
    renderer = Renderer(console=console)

    task = Task(
        id=99,
        title="Add user authentication",
        description="Implement **OAuth 2.0** authentication with Google provider",
        status=TaskStatus.DONE,
        milestone="v1.0",
        created=datetime(2025, 10, 1, 9, 0, 0, tzinfo=UTC),
        completed=datetime(2025, 10, 3, 15, 30, 0, tzinfo=UTC),
    )

    renderer.render_task_detail(task)

    result = output.getvalue()

    expected = dedent("""
        #99
        Status: ✓ done
        Milestone: v1.0
        Created: 2025-10-01 09:00:00+00:00
        Completed: 2025-10-03 15:30:00+00:00

        Add user authentication

        Implement OAuth 2.0 authentication with Google provider
    """)

    assert result.strip() == expected.strip()


def test_render_milestones() -> None:
    output = StringIO()
    console = Console(file=output, width=100)
    renderer = Renderer(console=console)

    tasks = [
        Task(
            id=1,
            title="Task 1",
            description="Description 1",
            status=TaskStatus.DONE,
            milestone="mvp",
            created=datetime(2025, 10, 1, 9, 0, 0, tzinfo=UTC),
            completed=datetime(2025, 10, 2, 10, 0, 0, tzinfo=UTC),
        ),
        Task(
            id=2,
            title="Task 2",
            description="Description 2",
            status=TaskStatus.DONE,
            milestone="mvp",
            created=datetime(2025, 10, 1, 10, 0, 0, tzinfo=UTC),
            completed=datetime(2025, 10, 2, 11, 0, 0, tzinfo=UTC),
        ),
        Task(
            id=3,
            title="Task 3",
            description="Description 3",
            status=TaskStatus.PROGRESS,
            milestone="mvp",
            created=datetime(2025, 10, 1, 11, 0, 0, tzinfo=UTC),
            completed=None,
        ),
        Task(
            id=4,
            title="Task 4",
            description="Description 4",
            status=TaskStatus.TODO,
            milestone="v2.0",
            created=datetime(2025, 10, 1, 12, 0, 0, tzinfo=UTC),
            completed=None,
        ),
        Task(
            id=5,
            title="Task 5",
            description="Description 5",
            status=TaskStatus.DONE,
            milestone=None,
            created=datetime(2025, 10, 1, 13, 0, 0, tzinfo=UTC),
            completed=datetime(2025, 10, 2, 14, 0, 0, tzinfo=UTC),
        ),
    ]

    renderer.render_milestones(tasks)

    result = output.getvalue()

    expected = dedent("""
        ┏━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
        ┃ Milestone    ┃ Tasks ┃ Done ┃ Progress                                 ┃ Completion ┃
        ┡━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
        │ No Milestone │ 1     │ 1    │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ 100.0%     │
        │ mvp          │ 3     │ 2    │ ━━━━━━━━━━━━━━━━━━━━━━━━━━╸              │ 66.7%      │
        │ v2.0         │ 1     │ 0    │                                          │ 0.0%       │
        └──────────────┴───────┴──────┴──────────────────────────────────────────┴────────────┘
    """)

    assert result.strip() == expected.strip()
