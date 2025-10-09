import re
from pathlib import Path

from quadro.models import Task
from quadro.models import TaskStatus


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

    def load_all_tasks(self, milestone: str | None = None) -> list[Task]:
        if not self.base_path.exists():
            return []

        tasks = []
        pattern = re.compile(r"^(\d+)\.md$")

        if milestone is not None:
            search_path = self.base_path / milestone
            if not search_path.exists():
                return []
            file_paths = search_path.glob("*.md")
        else:
            file_paths = self.base_path.rglob("*.md")

        for file_path in file_paths:
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

    def delete_task(self, task_id: int) -> Path | None:
        """
        Delete a task file by its ID.

        Parameters
        ----------
        task_id : int
            The unique identifier of the task to delete.

        Returns
        -------
        Path | None
            The path of the deleted task file if found and deleted,
            None if the task was not found or base directory doesn't exist.

        Examples
        --------
        >>> storage = TaskStorage()
        >>> deleted_path = storage.delete_task(1)
        >>> if deleted_path:
        ...     print(f"Deleted: {deleted_path}")
        """
        if not self.base_path.exists():
            return None

        pattern = re.compile(r"^(\d+)\.md$")

        for file_path in self.base_path.rglob("*.md"):
            match = pattern.match(file_path.name)
            if match and int(match.group(1)) == task_id:
                file_path.unlink()
                return file_path

        return None

    def get_milestones(self) -> list[str]:
        if not self.base_path.exists():
            return []

        milestones = [item.name for item in self.base_path.iterdir() if item.is_dir()]

        return sorted(milestones)

    def filter_by_status(self, tasks: list[Task], statuses: list[TaskStatus]) -> list[Task]:
        """
        Filter tasks by status.

        Parameters
        ----------
        tasks : list[Task]
            The list of tasks to filter.
        statuses : list[TaskStatus]
            The list of statuses to filter by. Tasks matching any status in
            this list will be included. If empty, all tasks are returned.

        Returns
        -------
        list[Task]
            The filtered list of tasks.

        Examples
        --------
        >>> storage = TaskStorage()
        >>> tasks = storage.load_all_tasks()
        >>> todo_tasks = storage.filter_by_status(tasks, [TaskStatus.TODO])
        >>> done_and_progress = storage.filter_by_status(
        ...     tasks, [TaskStatus.DONE, TaskStatus.PROGRESS]
        ... )
        """
        if not statuses:
            return tasks

        return [task for task in tasks if task.status in statuses]
