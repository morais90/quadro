from datetime import UTC
from datetime import datetime
from pathlib import Path

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
