from datetime import UTC
from datetime import datetime
from pathlib import Path

import pytest

from quadro.models import Task
from quadro.models import TaskStatus
from quadro.storage import TaskStorage


def test_get_next_id_empty_directory(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    assert storage.get_next_id() == 1


def test_get_next_id_nonexistent_directory(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path / "nonexistent")
    assert storage.get_next_id() == 1


def test_get_next_id_with_tasks(tmp_path: Path) -> None:
    (tmp_path / "1.md").write_text("# Task 1")
    (tmp_path / "3.md").write_text("# Task 3")
    (tmp_path / "5.md").write_text("# Task 5")

    storage = TaskStorage(base_path=tmp_path)
    assert storage.get_next_id() == 6


def test_get_next_id_with_milestone_folders(tmp_path: Path) -> None:
    milestone_dir = tmp_path / "mvp"
    milestone_dir.mkdir()

    (tmp_path / "1.md").write_text("# Task 1")
    (milestone_dir / "2.md").write_text("# Task 2")
    (milestone_dir / "4.md").write_text("# Task 4")

    storage = TaskStorage(base_path=tmp_path)
    assert storage.get_next_id() == 5


def test_get_next_id_ignores_non_numeric_files(tmp_path: Path) -> None:
    (tmp_path / "1.md").write_text("# Task 1")
    (tmp_path / "README.md").write_text("# README")
    (tmp_path / "notes.md").write_text("# Notes")

    storage = TaskStorage(base_path=tmp_path)
    assert storage.get_next_id() == 2


def test_save_task_to_root(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=1,
        title="Test Task",
        description="Test description",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 30, 15, tzinfo=UTC),
    )

    file_path = storage.save_task(task)

    assert file_path == tmp_path / "1.md"
    assert file_path.exists()
    assert "# Test Task" in file_path.read_text()


def test_save_task_to_milestone(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=2,
        title="MVP Task",
        description="Task in milestone",
        status=TaskStatus.PROGRESS,
        milestone="mvp",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    file_path = storage.save_task(task)

    assert file_path == tmp_path / "mvp" / "2.md"
    assert file_path.exists()
    assert "milestone: mvp" in file_path.read_text()
    assert "# MVP Task" in file_path.read_text()


def test_save_task_creates_milestone_directory(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=3,
        title="New Milestone Task",
        description="Create new milestone",
        status=TaskStatus.TODO,
        milestone="v2",
        created=datetime(2025, 10, 3, 11, 0, 0, tzinfo=UTC),
    )

    file_path = storage.save_task(task)

    assert (tmp_path / "v2").is_dir()
    assert file_path == tmp_path / "v2" / "3.md"
    assert file_path.exists()


def test_save_task_overwrites_existing(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=1,
        title="Original Task",
        description="Original",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task)

    updated_task = Task(
        id=1,
        title="Updated Task",
        description="Updated",
        status=TaskStatus.DONE,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
        completed=datetime(2025, 10, 3, 12, 0, 0, tzinfo=UTC),
    )

    file_path = storage.save_task(updated_task)

    assert file_path.exists()
    content = file_path.read_text()
    assert "# Updated Task" in content
    assert "status: done" in content
    assert "# Original Task" not in content


def test_load_task_from_root(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=1,
        title="Test Task",
        description="Test description",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 30, 15, tzinfo=UTC),
    )

    storage.save_task(task)
    loaded_task = storage.load_task(1)

    assert loaded_task is not None
    assert loaded_task.id == 1
    assert loaded_task.title == "Test Task"
    assert loaded_task.description == "Test description"
    assert loaded_task.status == TaskStatus.TODO


def test_load_task_from_milestone(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=5,
        title="Milestone Task",
        description="In milestone",
        status=TaskStatus.PROGRESS,
        milestone="mvp",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task)
    loaded_task = storage.load_task(5)

    assert loaded_task is not None
    assert loaded_task.id == 5
    assert loaded_task.title == "Milestone Task"
    assert loaded_task.milestone == "mvp"


def test_load_task_not_found(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    loaded_task = storage.load_task(999)

    assert loaded_task is None


def test_load_task_nonexistent_directory(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path / "nonexistent")
    loaded_task = storage.load_task(1)

    assert loaded_task is None


def test_load_all_tasks_empty_directory(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    tasks = storage.load_all_tasks()

    assert tasks == []


def test_load_all_tasks_nonexistent_directory(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path / "nonexistent")
    tasks = storage.load_all_tasks()

    assert tasks == []


def test_load_all_tasks_with_multiple_tasks(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task1 = Task(
        id=1,
        title="Task 1",
        description="First task",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    task2 = Task(
        id=2,
        title="Task 2",
        description="Second task",
        status=TaskStatus.PROGRESS,
        milestone="mvp",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    task3 = Task(
        id=3,
        title="Task 3",
        description="Third task",
        status=TaskStatus.DONE,
        milestone="mvp",
        created=datetime(2025, 10, 3, 11, 0, 0, tzinfo=UTC),
        completed=datetime(2025, 10, 3, 12, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task1)
    storage.save_task(task2)
    storage.save_task(task3)

    tasks = storage.load_all_tasks()

    assert len(tasks) == 3
    assert {task.id for task in tasks} == {1, 2, 3}
    assert {task.title for task in tasks} == {"Task 1", "Task 2", "Task 3"}


def test_load_all_tasks_ignores_non_numeric_files(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task = Task(
        id=1,
        title="Task 1",
        description="Valid task",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task)
    (tmp_path / "README.md").write_text("# README")
    (tmp_path / "notes.md").write_text("# Notes")

    tasks = storage.load_all_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == 1


def test_load_all_tasks_with_milestone_filter(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task1 = Task(
        id=1,
        title="Root Task",
        description="Task in root",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    task2 = Task(
        id=2,
        title="MVP Task 1",
        description="First MVP task",
        status=TaskStatus.PROGRESS,
        milestone="mvp",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    task3 = Task(
        id=3,
        title="MVP Task 2",
        description="Second MVP task",
        status=TaskStatus.DONE,
        milestone="mvp",
        created=datetime(2025, 10, 3, 11, 0, 0, tzinfo=UTC),
        completed=datetime(2025, 10, 3, 12, 0, 0, tzinfo=UTC),
    )

    task4 = Task(
        id=4,
        title="V2 Task",
        description="Task in v2",
        status=TaskStatus.TODO,
        milestone="v2",
        created=datetime(2025, 10, 3, 13, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task1)
    storage.save_task(task2)
    storage.save_task(task3)
    storage.save_task(task4)

    mvp_tasks = storage.load_all_tasks(milestone="mvp")

    assert len(mvp_tasks) == 2
    assert {task.id for task in mvp_tasks} == {2, 3}
    assert all(task.milestone == "mvp" for task in mvp_tasks)


def test_load_all_tasks_with_nonexistent_milestone(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task = Task(
        id=1,
        title="Task 1",
        description="A task",
        status=TaskStatus.TODO,
        milestone="mvp",
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task)

    tasks = storage.load_all_tasks(milestone="nonexistent")

    assert tasks == []


def test_move_task_from_root_to_milestone(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=1,
        title="Task to Move",
        description="Moving to milestone",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task)
    assert (tmp_path / "1.md").exists()

    new_path = storage.move_task(1, "mvp")

    assert new_path == tmp_path / "mvp" / "1.md"
    assert new_path.exists()
    assert not (tmp_path / "1.md").exists()

    moved_task = storage.load_task(1)
    assert moved_task is not None
    assert moved_task.milestone == "mvp"


def test_move_task_from_milestone_to_root(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=2,
        title="Milestone Task",
        description="Moving to root",
        status=TaskStatus.PROGRESS,
        milestone="mvp",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task)
    assert (tmp_path / "mvp" / "2.md").exists()

    new_path = storage.move_task(2, None)

    assert new_path == tmp_path / "2.md"
    assert new_path.exists()
    assert not (tmp_path / "mvp" / "2.md").exists()

    moved_task = storage.load_task(2)
    assert moved_task is not None
    assert moved_task.milestone is None


def test_move_task_between_milestones(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=3,
        title="Moving Task",
        description="Between milestones",
        status=TaskStatus.TODO,
        milestone="mvp",
        created=datetime(2025, 10, 3, 11, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task)
    assert (tmp_path / "mvp" / "3.md").exists()

    new_path = storage.move_task(3, "v2")

    assert new_path == tmp_path / "v2" / "3.md"
    assert new_path.exists()
    assert not (tmp_path / "mvp" / "3.md").exists()

    moved_task = storage.load_task(3)
    assert moved_task is not None
    assert moved_task.milestone == "v2"


def test_move_task_not_found(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    with pytest.raises(ValueError, match="Task 999 not found"):
        storage.move_task(999, "mvp")


def test_get_milestones_empty_directory(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    milestones = storage.get_milestones()

    assert milestones == []


def test_get_milestones_nonexistent_directory(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path / "nonexistent")
    milestones = storage.get_milestones()

    assert milestones == []


def test_get_milestones_with_multiple_milestones(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task1 = Task(
        id=1,
        title="MVP Task",
        description="Task 1",
        status=TaskStatus.TODO,
        milestone="mvp",
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    task2 = Task(
        id=2,
        title="V2 Task",
        description="Task 2",
        status=TaskStatus.TODO,
        milestone="v2",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    task3 = Task(
        id=3,
        title="Beta Task",
        description="Task 3",
        status=TaskStatus.TODO,
        milestone="beta",
        created=datetime(2025, 10, 3, 11, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task1)
    storage.save_task(task2)
    storage.save_task(task3)

    milestones = storage.get_milestones()

    assert milestones == ["beta", "mvp", "v2"]


def test_get_milestones_ignores_files_in_root(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task1 = Task(
        id=1,
        title="Root Task",
        description="In root",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    task2 = Task(
        id=2,
        title="Milestone Task",
        description="In milestone",
        status=TaskStatus.TODO,
        milestone="mvp",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task1)
    storage.save_task(task2)

    milestones = storage.get_milestones()

    assert milestones == ["mvp"]


def test_delete_task_existing(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=1,
        title="Task to Delete",
        description="This will be deleted",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    file_path = storage.save_task(task)
    assert file_path.exists()

    deleted_path = storage.delete_task(1)

    assert deleted_path == tmp_path / "1.md"
    assert not file_path.exists()
    assert storage.load_task(1) is None


def test_delete_task_from_milestone(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)
    task = Task(
        id=5,
        title="Milestone Task to Delete",
        description="This will be deleted",
        status=TaskStatus.PROGRESS,
        milestone="mvp",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    file_path = storage.save_task(task)
    assert file_path.exists()

    deleted_path = storage.delete_task(5)

    assert deleted_path == tmp_path / "mvp" / "5.md"
    assert not file_path.exists()
    assert storage.load_task(5) is None


def test_delete_task_not_found(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    deleted_path = storage.delete_task(999)

    assert deleted_path is None


def test_delete_task_nonexistent_directory(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path / "nonexistent")

    deleted_path = storage.delete_task(1)

    assert deleted_path is None


def test_filter_by_status_single_status(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task1 = Task(
        id=1,
        title="Todo Task",
        description="First todo task",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    task2 = Task(
        id=2,
        title="Progress Task",
        description="Task in progress",
        status=TaskStatus.PROGRESS,
        milestone=None,
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    task3 = Task(
        id=3,
        title="Done Task",
        description="Completed task",
        status=TaskStatus.DONE,
        milestone=None,
        created=datetime(2025, 10, 3, 11, 0, 0, tzinfo=UTC),
        completed=datetime(2025, 10, 3, 12, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task1)
    storage.save_task(task2)
    storage.save_task(task3)

    all_tasks = storage.load_all_tasks()

    todo_tasks = storage.filter_by_status(all_tasks, [TaskStatus.TODO])
    assert len(todo_tasks) == 1
    assert todo_tasks[0].id == 1
    assert todo_tasks[0].status == TaskStatus.TODO


def test_filter_by_status_multiple_statuses(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task1 = Task(
        id=1,
        title="Todo Task",
        description="First todo task",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    task2 = Task(
        id=2,
        title="Progress Task",
        description="Task in progress",
        status=TaskStatus.PROGRESS,
        milestone=None,
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    task3 = Task(
        id=3,
        title="Done Task",
        description="Completed task",
        status=TaskStatus.DONE,
        milestone=None,
        created=datetime(2025, 10, 3, 11, 0, 0, tzinfo=UTC),
        completed=datetime(2025, 10, 3, 12, 0, 0, tzinfo=UTC),
    )

    task4 = Task(
        id=4,
        title="Another Todo Task",
        description="Second todo task",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 13, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task1)
    storage.save_task(task2)
    storage.save_task(task3)
    storage.save_task(task4)

    all_tasks = storage.load_all_tasks()

    done_and_progress = storage.filter_by_status(all_tasks, [TaskStatus.DONE, TaskStatus.PROGRESS])
    assert len(done_and_progress) == 2
    assert {task.id for task in done_and_progress} == {2, 3}
    assert {task.status for task in done_and_progress} == {
        TaskStatus.DONE,
        TaskStatus.PROGRESS,
    }


def test_filter_by_status_empty_list_returns_all(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task1 = Task(
        id=1,
        title="Todo Task",
        description="First todo task",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    task2 = Task(
        id=2,
        title="Progress Task",
        description="Task in progress",
        status=TaskStatus.PROGRESS,
        milestone=None,
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    task3 = Task(
        id=3,
        title="Done Task",
        description="Completed task",
        status=TaskStatus.DONE,
        milestone=None,
        created=datetime(2025, 10, 3, 11, 0, 0, tzinfo=UTC),
        completed=datetime(2025, 10, 3, 12, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task1)
    storage.save_task(task2)
    storage.save_task(task3)

    all_tasks = storage.load_all_tasks()

    filtered_tasks = storage.filter_by_status(all_tasks, [])
    assert len(filtered_tasks) == 3
    assert filtered_tasks == all_tasks


def test_filter_by_status_no_matching_tasks(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    task1 = Task(
        id=1,
        title="Todo Task",
        description="First todo task",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 9, 0, 0, tzinfo=UTC),
    )

    task2 = Task(
        id=2,
        title="Another Todo Task",
        description="Second todo task",
        status=TaskStatus.TODO,
        milestone=None,
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
    )

    storage.save_task(task1)
    storage.save_task(task2)

    all_tasks = storage.load_all_tasks()

    done_tasks = storage.filter_by_status(all_tasks, [TaskStatus.DONE])
    assert len(done_tasks) == 0
    assert done_tasks == []


def test_filter_by_status_with_empty_task_list(tmp_path: Path) -> None:
    storage = TaskStorage(base_path=tmp_path)

    filtered_tasks = storage.filter_by_status([], [TaskStatus.TODO])
    assert len(filtered_tasks) == 0
    assert filtered_tasks == []
