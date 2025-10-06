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

    def load_all_tasks(self) -> list[Task]:
        if not self.base_path.exists():
            return []

        tasks = []
        pattern = re.compile(r"^(\d+)\.md$")

        for file_path in self.base_path.rglob("*.md"):
            match = pattern.match(file_path.name)
            if match:
                task_id = int(match.group(1))
                content = file_path.read_text()
                task = Task.from_markdown(content, task_id, str(file_path))
                tasks.append(task)

        return sorted(tasks, key=lambda t: t.id)

    def move_task(self, task_id: int, to_milestone: str | None) -> Path:
        task = self.load_task(task_id)
        if task is None:
            msg = f"Task {task_id} not found"
            raise ValueError(msg)

        pattern = re.compile(r"^(\d+)\.md$")
        old_file_path = None

        for file_path in self.base_path.rglob("*.md"):
            match = pattern.match(file_path.name)
            if match and int(match.group(1)) == task_id:
                old_file_path = file_path
                break

        if old_file_path is None:
            msg = f"Task file for {task_id} not found"
            raise ValueError(msg)

        task.milestone = to_milestone
        new_file_path = self.save_task(task)

        if old_file_path != new_file_path:
            old_file_path.unlink()

        return new_file_path

    def get_milestones(self) -> list[str]:
        if not self.base_path.exists():
            return []

        milestones = [item.name for item in self.base_path.iterdir() if item.is_dir()]

        return sorted(milestones)
