from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from enum import Enum
from pathlib import Path

import frontmatter


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

    @classmethod
    def from_markdown(cls, content: str, task_id: int, file_path: str | Path) -> "Task":
        doc = frontmatter.loads(content)

        if "status" not in doc.metadata:
            msg = f"Missing 'status' in frontmatter: {file_path}"
            raise ValueError(msg)
        if "created" not in doc.metadata:
            msg = f"Missing 'created' in frontmatter: {file_path}"
            raise ValueError(msg)

        milestone = doc.get("milestone")
        status = TaskStatus(doc["status"])
        created_raw = doc["created"]
        created = (
            created_raw
            if isinstance(created_raw, datetime)
            else datetime.fromisoformat(created_raw)
        )
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)

        completed_raw = doc.get("completed")
        completed = (
            completed_raw
            if isinstance(completed_raw, datetime)
            else datetime.fromisoformat(completed_raw)
            if completed_raw
            else None
        )
        if completed and completed.tzinfo is None:
            completed = completed.replace(tzinfo=UTC)

        lines = doc.content.strip().split("\n")
        title = ""
        description_lines = []
        found_title = False

        for line in lines:
            if line.startswith("# ") and not found_title:
                title = line[2:].strip()
                found_title = True
            elif found_title:
                description_lines.append(line)

        if not title:
            msg = f"Missing title (H1) in markdown content: {file_path}"
            raise ValueError(msg)

        description = "\n".join(description_lines).strip()

        return cls(
            id=task_id,
            title=title,
            description=description,
            status=status,
            milestone=milestone,
            created=created,
            completed=completed,
        )
