class TaskError(Exception):
    """Base exception for task-related errors."""


class TaskNotFoundError(TaskError):
    """Raised when a task with the specified ID cannot be found."""


class TaskAlreadyInProgressError(TaskError):
    """Raised when attempting to start a task that is already in progress."""


class TaskAlreadyDoneError(TaskError):
    """Raised when attempting to modify a task that is already completed."""
