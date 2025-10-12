from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from quadro.command import add_task
from quadro.command import list_tasks as get_tasks
from quadro.command import show_task
from quadro.models import Task
from quadro.models import TaskStatus


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

__version__ = "0.1.0"
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
    return get_tasks(milestone=milestone, statuses=statuses)


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
    return show_task(task_id)


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
    return add_task(title=title, description=description, milestone=milestone)


if __name__ == "__main__":
    mcp.run()
