from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quadro.cli import main
from quadro.command import add_task
from quadro.command import complete_task
from quadro.exceptions import TaskAlreadyDoneError
from quadro.exceptions import TaskNotFoundError
from quadro.models import TaskStatus


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestCompleteTask:
    def test_complete_task_valid(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task")

            task = complete_task(1)

            assert task.id == 1
            assert task.status == TaskStatus.DONE
            assert task.title == "Test task"
            assert task.completed is not None

    def test_complete_task_not_found(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            pytest.raises(TaskNotFoundError, match="Task #999 not found"),
        ):
            complete_task(999)

    def test_complete_task_already_done(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task")
            complete_task(1)

            with pytest.raises(TaskAlreadyDoneError, match="Task #1 is already done"):
                complete_task(1)


class TestDoneCommandCLI:
    def test_done_command_valid_case(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            result = runner.invoke(main, ["done", "1"])

            assert result.exit_code == 0
            assert result.output == "✓ Completed task #1: Test task\n"

            task_file = Path("tasks/1.md")
            content = task_file.read_text()
            assert "status: done" in content
            assert "completed:" in content

    def test_done_command_task_not_found(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["done", "999"])

            assert result.exit_code == 1
            assert result.output == "✗ Task #999 not found\n"

    def test_done_command_already_done(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])
            runner.invoke(main, ["done", "1"])

            result = runner.invoke(main, ["done", "1"])

            assert result.exit_code == 0
            assert result.output == "! Task #1 is already done\n"

    def test_done_command_permission_error(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            with patch("quadro.storage.TaskStorage.save_task") as mock_save:
                mock_save.side_effect = PermissionError()
                result = runner.invoke(main, ["done", "1"])

                assert result.exit_code == 1
                assert result.output == dedent("""\
                    ✗ Permission denied
                    Cannot access: tasks directory
                    Check that you have read/write permissions for the tasks directory.
                    """)
