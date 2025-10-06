from quadro.exceptions import TaskNotFoundError
from quadro.models import Task
from quadro.storage import TaskStorage


def get_task_markdown(task_id: int) -> str:
    """
    Get the markdown representation of a task for editing.

    Parameters
    ----------
    task_id : int
        The ID of the task to retrieve

    Returns
    -------
    str
        The markdown representation of the task

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

    return task.to_markdown()


def update_task_from_markdown(task_id: int, markdown_content: str) -> Task:
    """
    Update a task from its markdown representation.

    Parameters
    ----------
    task_id : int
        The ID of the task to update
    markdown_content : str
        The new markdown content for the task

    Returns
    -------
    Task
        The updated task object

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist
    ValueError
        If the markdown content is invalid or malformed
    """
    storage = TaskStorage()
    task = storage.load_task(task_id)

    if task is None:
        msg = f"Task #{task_id} not found"
        raise TaskNotFoundError(msg)

    updated_task = Task.from_markdown(markdown_content, task_id, "edited")
    storage.save_task(updated_task)

    return updated_task
