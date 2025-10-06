from quadro.exceptions import TaskNotFoundError
from quadro.models import Task
from quadro.storage import TaskStorage


def show_task(task_id: int) -> Task:
    """
    Retrieve a task by ID.

    Parameters
    ----------
    task_id : int
        The ID of the task to retrieve

    Returns
    -------
    Task
        The task with the specified ID

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist
    """
    storage = TaskStorage()
    task = storage.load_task(task_id)

    if task is None:
        msg = f"Task #{task_id} not found"
        raise TaskNotFoundError(msg)

    return task
