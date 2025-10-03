import re
from pathlib import Path

from quadro.models import Task


class TaskStorage:
    def __init__(self, base_path: Path = Path("tasks")) -> None:
        self.base_path = base_path

    def get_next_id(self) -> int:
        if not self.base_path.exists():
            return 1

        max_id = 0
        pattern = re.compile(r"^(\d+)\.md$")

        for file_path in self.base_path.rglob("*.md"):
            match = pattern.match(file_path.name)
            if match:
                task_id = int(match.group(1))
                max_id = max(max_id, task_id)

        return max_id + 1

    def save_task(self, task: Task) -> Path:
        if task.milestone is not None:
            task_dir = self.base_path / task.milestone
            task_dir.mkdir(parents=True, exist_ok=True)
        else:
            task_dir = self.base_path
            task_dir.mkdir(parents=True, exist_ok=True)

        file_path = task_dir / f"{task.id}.md"
        file_path.write_text(task.to_markdown())

        return file_path

    def load_task(self, task_id: int) -> Task | None:
        if not self.base_path.exists():
            return None

        pattern = re.compile(r"^(\d+)\.md$")

        for file_path in self.base_path.rglob("*.md"):
            match = pattern.match(file_path.name)
            if match and int(match.group(1)) == task_id:
                content = file_path.read_text()
                return Task.from_markdown(content, task_id, str(file_path))

        return None
