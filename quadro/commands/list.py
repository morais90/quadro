from quadro.models import Task
from quadro.storage import TaskStorage


def list_tasks() -> list[Task]:
    """
    List all tasks.

    Returns
    -------
    list[Task]
        A list of tasks sorted by ID. May be empty if no tasks exist.
    """
    storage = TaskStorage()
    return storage.load_all_tasks()
