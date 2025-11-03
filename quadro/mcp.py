from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from quadro import command
from quadro.models import Task
from quadro.models import TaskStatus
from quadro.storage import TaskStorage


mcp = FastMCP(
    "Quadro Task Manager",
    instructions="""
    Quadro is a task management system with the following capabilities:

    - List tasks with optional filtering by milestone and status
    - Create new tasks with title, description, and milestone
    - View detailed information about specific tasks
    - Update task status (todo → progress → done)
    - Edit task details (title, description, milestone)
    - Move tasks between milestones
    - Delete tasks permanently
    - View milestone summaries

    Tasks have three statuses: todo, progress, and done.
    Tasks can be organized into milestones for better project management.
    """,
)

__version__ = "1.0.1"
__description__ = "Manage your tasks directly from the terminal using markdown"


@mcp.tool(description="List tasks with optional milestone and status filters")
def list_tasks(
    milestone: Annotated[
        str | None,
        Field(description="Filter by milestone name (case-sensitive)"),
    ] = None,
    status: Annotated[TaskStatus | None, Field(description="Filter by status")] = None,
) -> list[Task]:
    """
    List all tasks with optional filtering by milestone and status.

    Parameters
    ----------
    milestone : str | None
        Filter tasks by milestone name. If None, returns tasks from all milestones.
    status : TaskStatus | None
        Filter tasks by status (todo, progress, or done). If None, returns tasks with any status.

    Returns
    -------
    list[Task]
        List of Task objects.
    """
    statuses = [status] if status is not None else None
    return command.list_tasks(milestone=milestone, statuses=statuses)


@mcp.tool(description="Get a specific task by ID")
def get_task(
    task_id: Annotated[int, Field(description="The ID of the task to retrieve")],
) -> Task:
    """
    Retrieve a task by its ID.

    Parameters
    ----------
    task_id : int
        The ID of the task to retrieve.

    Returns
    -------
    Task
        The task with the specified ID.

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist.
    """
    return command.show_task(task_id)


@mcp.tool(description="Create a new task with title, description, and optional milestone")
def create_task(
    title: Annotated[str, Field(description="The title of the task")],
    description: Annotated[str, Field(description="The description of the task")] = "",
    milestone: Annotated[
        str | None,
        Field(description="The milestone to assign the task to"),
    ] = None,
) -> Task:
    """
    Create a new task.

    Parameters
    ----------
    title : str
        The title of the task.
    description : str
        The description of the task. Defaults to empty string.
    milestone : str | None
        The milestone to assign the task to. If None, task is not assigned to any milestone.

    Returns
    -------
    Task
        The newly created Task object.
    """
    return command.add_task(title=title, description=description, milestone=milestone)


@mcp.tool(description="Start a task by changing its status to in progress")
def start_task(
    task_id: Annotated[int, Field(description="The ID of the task to start")],
) -> Task:
    """
    Start a task by changing its status to in progress.

    Parameters
    ----------
    task_id : int
        The ID of the task to start.

    Returns
    -------
    Task
        The updated task with PROGRESS status.

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist.
    TaskAlreadyInProgressError
        If task is already in progress.
    TaskAlreadyDoneError
        If task is already completed.
    """
    return command.start_task(task_id)


@mcp.tool(description="Mark a task as completed")
def complete_task(
    task_id: Annotated[int, Field(description="The ID of the task to complete")],
) -> Task:
    """
    Mark a task as completed.

    Parameters
    ----------
    task_id : int
        The ID of the task to complete.

    Returns
    -------
    Task
        The updated task with DONE status and completion timestamp.

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist.
    TaskAlreadyDoneError
        If task is already completed.
    """
    return command.complete_task(task_id)


@mcp.tool(description="Move a task to a different milestone")
def move_task(
    task_id: Annotated[int, Field(description="The ID of the task to move")],
    to_milestone: Annotated[
        str,
        Field(description="Target milestone or 'root' for no milestone"),
    ],
) -> Task:
    """
    Move a task to a different milestone.

    Parameters
    ----------
    task_id : int
        The ID of the task to move.
    to_milestone : str
        Target milestone name, or "root" for no milestone.

    Returns
    -------
    Task
        The moved task object.

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist.
    """
    command.move_task(task_id, to_milestone)
    return command.show_task(task_id)


@mcp.tool(description="Delete a task permanently")
def delete_task(
    task_id: Annotated[int, Field(description="The ID of the task to delete")],
) -> Task:
    """
    Delete a task permanently.

    Parameters
    ----------
    task_id : int
        The ID of the task to delete.

    Returns
    -------
    Task
        The deleted task object (before deletion).

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist.
    """
    task, _ = command.delete_task(task_id)
    return task


@mcp.tool(description="List all tasks that belong to milestones")
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
        If no tasks exist in the system.
    """
    return command.list_milestones()


@mcp.resource("quadro://task/{task_id}")
def get_task_resource(task_id: int) -> str:
    """
    Get the full markdown content of a task.

    Parameters
    ----------
    task_id : int
        The ID of the task to retrieve.

    Returns
    -------
    str
        The task's markdown content including frontmatter.

    Raises
    ------
    TaskNotFoundError
        If task with the specified ID does not exist.
    """
    storage = TaskStorage()
    task = storage.load_task(task_id)

    if task is None:
        msg = f"Task {task_id} not found"
        raise ValueError(msg)

    return task.to_markdown()


if __name__ == "__main__":
    mcp.run()
