from quadro.exceptions import TaskNotFoundError
from quadro.storage import TaskStorage


def move_task(task_id: int, to_milestone: str) -> tuple[str, str, str]:
    """
    Move a task to a different milestone.

    Parameters
    ----------
    task_id : int
        The ID of the task to move
    to_milestone : str
        Target milestone name, or "root" for no milestone

    Returns
    -------
    tuple[str, str, str]
        A tuple of (old_milestone, new_milestone, new_path) where milestones
        are displayed as "root" when None, and new_path is the file location

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

    old_milestone = task.milestone or "root"
    target_milestone = None if to_milestone == "root" else to_milestone

    new_path = storage.move_task(task_id, target_milestone)
    new_milestone = target_milestone or "root"

    return old_milestone, new_milestone, str(new_path)
