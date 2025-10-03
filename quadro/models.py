from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    PROGRESS = "progress"
    DONE = "done"


@dataclass
class Task:
    id: int
    title: str
    description: str
    status: TaskStatus
    milestone: str | None
    created: datetime
    completed: datetime | None
