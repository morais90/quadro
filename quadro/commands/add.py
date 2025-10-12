from datetime import UTC
from datetime import datetime

from quadro.models import Task
from quadro.models import TaskStatus
from quadro.storage import TaskStorage


def add_task(title: str, description: str | None = None, milestone: str | None = None) -> Task:
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
    Task
        The newly created Task object
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

    storage.save_task(task)

    return task
