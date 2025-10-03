import re
from pathlib import Path


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
