from datetime import UTC
from datetime import datetime

from quadro.exceptions import TaskAlreadyDoneError
from quadro.exceptions import TaskNotFoundError
from quadro.models import Task
from quadro.models import TaskStatus
from quadro.storage import TaskStorage


def complete_task(task_id: int) -> Task:
    """
    Mark a task as completed.

    Parameters
    ----------
    task_id : int
        The ID of the task to complete

    Returns
    -------
    Task
        The updated task with DONE status and completion timestamp

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist
    TaskAlreadyDoneError
        If task is already completed
    """
    storage = TaskStorage()
    task = storage.load_task(task_id)

    if task is None:
        msg = f"Task #{task_id} not found"
        raise TaskNotFoundError(msg)

    if task.status == TaskStatus.DONE:
        msg = f"Task #{task_id} is already done"
        raise TaskAlreadyDoneError(msg)

    task.status = TaskStatus.DONE
    task.completed = datetime.now(UTC)
    storage.save_task(task)

    return task
