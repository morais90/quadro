from datetime import UTC
from datetime import datetime

from quadro.models import Task
from quadro.models import TaskStatus
from quadro.storage import TaskStorage


def add_task(
    title: str, description: str | None = None, milestone: str | None = None
) -> tuple[int, str]:
    """
    Add a new task.

    Parameters
    ----------
    title : str
        The task title
    description : str | None, optional
        The task description, by default None
    milestone : str | None, optional
        Milestone name for the task, by default None

    Returns
    -------
    tuple[int, str]
        A tuple of (task_id, file_path) where task_id is the ID of the created task
        and file_path is the path to the saved task file
    """
    storage = TaskStorage()

    task_id = storage.get_next_id()
    task = Task(
        id=task_id,
        title=title,
        description=description or "",
        status=TaskStatus.TODO,
        milestone=milestone,
        created=datetime.now(UTC),
        completed=None,
    )

    file_path = storage.save_task(task)

    return task_id, str(file_path)
