from pathlib import Path

from quadro.exceptions import TaskNotFoundError
from quadro.models import Task
from quadro.storage import TaskStorage


def delete_task(task_id: int) -> tuple[Task, Path]:
    """
    Delete a task by ID.

    Parameters
    ----------
    task_id : int
        The ID of the task to delete

    Returns
    -------
    tuple[Task, Path]
        A tuple containing the deleted task and its file path

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

    deleted_path = storage.delete_task(task_id)

    if deleted_path is None:
        msg = f"Failed to delete task #{task_id}"
        raise TaskNotFoundError(msg)

    return task, deleted_path
