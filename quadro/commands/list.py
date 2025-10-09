from quadro.models import Task
from quadro.models import TaskStatus
from quadro.storage import TaskStorage


def list_tasks(
    milestone: str | None = None,
    statuses: list[TaskStatus] | None = None,
) -> list[Task]:
    """
    List all tasks with optional filters.

    Parameters
    ----------
    milestone : str | None
        Filter tasks by milestone. If None, tasks from all milestones are included.
    statuses : list[TaskStatus] | None
        Filter tasks by status. If None or empty, all statuses are included.

    Returns
    -------
    list[Task]
        A list of filtered tasks sorted by ID. May be empty if no tasks match.
    """
    storage = TaskStorage()
    tasks = storage.load_all_tasks(milestone=milestone)

    if statuses:
        tasks = storage.filter_by_status(tasks, statuses)

    return tasks
