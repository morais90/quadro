from datetime import UTC
from datetime import datetime
from pathlib import Path

from quadro.exceptions import TaskAlreadyDoneError
from quadro.exceptions import TaskAlreadyInProgressError
from quadro.exceptions import TaskNotFoundError
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
