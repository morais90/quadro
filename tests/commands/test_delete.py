from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quadro.cli import main
from quadro.command import add_task
from quadro.command import delete_task
from quadro.exceptions import TaskNotFoundError


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestDeleteTask:
    def test_delete_task_valid(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task")

            task, file_path = delete_task(1)

            assert task.id == 1
            assert task.title == "Test task"
            assert file_path == Path("tasks/1.md")
            assert not Path("tasks/1.md").exists()

    def test_delete_task_from_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task", milestone="mvp")

            task, file_path = delete_task(1)

            assert task.id == 1
            assert task.milestone == "mvp"
            assert file_path == Path("tasks/mvp/1.md")
            assert not Path("tasks/mvp/1.md").exists()

    def test_delete_task_not_found(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            pytest.raises(TaskNotFoundError, match="Task #999 not found"),
        ):
            delete_task(999)


class TestDeleteCommandCLI:
    def test_delete_command_with_confirmation(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            result = runner.invoke(main, ["delete", "1"], input="y\n")

            assert result.exit_code == 0
            assert "Task to be deleted:" in result.output
            assert "Test task" in result.output
            assert "Are you sure you want to delete this task?" in result.output
            assert "✓ Deleted task #1: Test task" in result.output
            assert "Removed: tasks/1.md" in result.output
            assert not Path("tasks/1.md").exists()

    def test_delete_command_cancelled(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            result = runner.invoke(main, ["delete", "1"], input="n\n")

            assert result.exit_code == 0
            assert "Task to be deleted:" in result.output
            assert "Are you sure you want to delete this task?" in result.output
            assert "! Deletion cancelled" in result.output
            assert Path("tasks/1.md").exists()

    def test_delete_command_with_yes_flag(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            result = runner.invoke(main, ["delete", "1", "--yes"])

            assert result.exit_code == 0
            assert result.output == dedent("""\
                ✓ Deleted task #1: Test task
                Removed: tasks/1.md
                """)
            assert not Path("tasks/1.md").exists()

    def test_delete_command_with_y_flag(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            result = runner.invoke(main, ["delete", "1", "-y"])

            assert result.exit_code == 0
            assert result.output == dedent("""\
                ✓ Deleted task #1: Test task
                Removed: tasks/1.md
                """)
            assert not Path("tasks/1.md").exists()

    def test_delete_command_task_not_found(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["delete", "999", "--yes"])

            assert result.exit_code == 1
            assert result.output == "✗ Task #999 not found\n"

    def test_delete_command_permission_error(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            with patch("quadro.storage.TaskStorage.delete_task") as mock_delete:
                mock_delete.side_effect = PermissionError()
                result = runner.invoke(main, ["delete", "1", "--yes"])

                assert result.exit_code == 1
                assert "✗ Permission denied" in result.output
                assert "read/write permissions" in result.output
