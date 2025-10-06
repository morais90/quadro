from quadro.exceptions import TaskAlreadyDoneError
from quadro.exceptions import TaskAlreadyInProgressError
from quadro.exceptions import TaskNotFoundError
from quadro.models import Task
from quadro.models import TaskStatus
from quadro.storage import TaskStorage


def start_task(task_id: int) -> Task:
    """
    Start a task by changing its status to in progress.

    Parameters
    ----------
    task_id : int
        The ID of the task to start

    Returns
    -------
    Task
        The updated task with PROGRESS status

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist
    TaskAlreadyInProgressError
        If task is already in progress
    TaskAlreadyDoneError
        If task is already completed
    """
    storage = TaskStorage()
    task = storage.load_task(task_id)

    if task is None:
        msg = f"Task #{task_id} not found"
        raise TaskNotFoundError(msg)

    if task.status == TaskStatus.PROGRESS:
        msg = f"Task #{task_id} is already in progress"
        raise TaskAlreadyInProgressError(msg)

    if task.status == TaskStatus.DONE:
        msg = f"Task #{task_id} is already done"
        raise TaskAlreadyDoneError(msg)

    task.status = TaskStatus.PROGRESS
    storage.save_task(task)

    return task
