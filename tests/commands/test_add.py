from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quadro.cli import main
from quadro.commands.add import add_task


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestAddTask:
    def test_add_task_basic(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task_id, file_path = add_task("Test task")

            assert task_id == 1
            assert file_path == "tasks/1.md"

            task_file = Path(file_path)
            assert task_file.exists()

            content = task_file.read_text()
            assert "# Test task" in content
            assert "status: todo" in content
            assert "milestone:" not in content

    def test_add_task_with_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task_id, file_path = add_task("Task with milestone", milestone="mvp")

            assert task_id == 1
            assert file_path == "tasks/mvp/1.md"

            task_file = Path(file_path)
            assert task_file.exists()

            content = task_file.read_text()
            assert "# Task with milestone" in content
            assert "milestone: mvp" in content
            assert "status: todo" in content

    def test_add_task_increments_id(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task_id_1, _ = add_task("First task")
            task_id_2, _ = add_task("Second task")
            task_id_3, _ = add_task("Third task")

            assert task_id_1 == 1
            assert task_id_2 == 2
            assert task_id_3 == 3


class TestAddCommandCLI:
    def test_add_command(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["add", "Test task"])

            assert result.exit_code == 0
            assert result.output == "✓ Created task #1\nFile: tasks/1.md\n"

            task_file = Path("tasks/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            assert "# Test task" in content
            assert "status: todo" in content

    def test_add_command_with_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["add", "Task with milestone", "--milestone", "mvp"])

            assert result.exit_code == 0
            assert result.output == "✓ Created task #1\nFile: tasks/mvp/1.md\n"

            task_file = Path("tasks/mvp/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            assert "# Task with milestone" in content
            assert "milestone: mvp" in content
            assert "status: todo" in content

    def test_add_command_permission_error(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            patch("quadro.storage.TaskStorage.save_task") as mock_save,
        ):
            mock_save.side_effect = PermissionError()
            result = runner.invoke(main, ["add", "Test task"])

            assert result.exit_code == 1
            assert "✗ Permission denied" in result.output
            assert "read/write permissions" in result.output

    def test_add_command_os_error(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            patch("quadro.storage.TaskStorage.save_task") as mock_save,
        ):
            mock_save.side_effect = OSError("No space left on device")
            result = runner.invoke(main, ["add", "Test task"])

            assert result.exit_code == 1
            assert "✗ System error" in result.output
            assert "No space left on device" in result.output
            assert "disk space" in result.output
