from quadro.exceptions import TaskNotFoundError
from quadro.models import Task
from quadro.storage import TaskStorage


def list_milestones() -> list[Task]:
    """
    List all tasks that belong to milestones.

    Returns
    -------
    list[Task]
        A list of tasks that have a milestone assigned, sorted by ID.
        May be empty if no tasks have milestones.

    Raises
    ------
    TaskNotFoundError
        If no tasks exist in the system
    """
    storage = TaskStorage()
    tasks = storage.load_all_tasks()

    if not tasks:
        msg = "No tasks found"
        raise TaskNotFoundError(msg)

    return [t for t in tasks if t.milestone is not None]
