from pathlib import Path

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
