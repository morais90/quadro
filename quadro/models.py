from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    PROGRESS = "progress"
    DONE = "done"
