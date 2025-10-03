from datetime import UTC
from datetime import datetime

from quadro.models import Task
from quadro.models import TaskStatus


def test_task_creation() -> None:
    task = Task(
        id=1,
        title="Test Task",
        description="This is a test task",
        status=TaskStatus.TODO,
        milestone="mvp",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
        completed=None,
    )

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "This is a test task"
    assert task.status == TaskStatus.TODO
    assert task.milestone == "mvp"
    assert task.created == datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC)
    assert task.completed is None


def test_task_status_enum() -> None:
    assert TaskStatus.TODO.value == "todo"
    assert TaskStatus.PROGRESS.value == "progress"
    assert TaskStatus.DONE.value == "done"
