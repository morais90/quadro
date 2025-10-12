from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quadro.cli import main
from quadro.command import add_task
from quadro.command import start_task
from quadro.exceptions import TaskAlreadyDoneError
from quadro.exceptions import TaskAlreadyInProgressError
from quadro.exceptions import TaskNotFoundError
from quadro.models import TaskStatus


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestStartTask:
    def test_start_task_valid(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task")

            task = start_task(1)

            assert task.id == 1
            assert task.status == TaskStatus.PROGRESS
            assert task.title == "Test task"

    def test_start_task_not_found(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            pytest.raises(TaskNotFoundError, match="Task #999 not found"),
        ):
            start_task(999)

    def test_start_task_already_in_progress(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task")
            start_task(1)

            with pytest.raises(TaskAlreadyInProgressError, match="Task #1 is already in progress"):
                start_task(1)

    def test_start_task_already_done(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task")

            task_file = Path("tasks/1.md")
            content = task_file.read_text()
            content = content.replace("status: todo", "status: done")
            task_file.write_text(content)

            with pytest.raises(TaskAlreadyDoneError, match="Task #1 is already done"):
                start_task(1)


class TestStartCommandCLI:
    def test_start_command_valid_case(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            result = runner.invoke(main, ["start", "1"])

            assert result.exit_code == 0
            assert result.output == "✓ Started task #1: Test task\n"

            task_file = Path("tasks/1.md")
            content = task_file.read_text()
            assert "status: progress" in content

    def test_start_command_task_not_found(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["start", "999"])

            assert result.exit_code == 1
            assert result.output == "✗ Task #999 not found\n"

    def test_start_command_already_in_progress(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])
            runner.invoke(main, ["start", "1"])

            result = runner.invoke(main, ["start", "1"])

            assert result.exit_code == 0
            assert result.output == "! Task #1 is already in progress\n"

    def test_start_command_already_done(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            task_file = Path("tasks/1.md")
            content = task_file.read_text()
            content = content.replace("status: todo", "status: done")
            task_file.write_text(content)

            result = runner.invoke(main, ["start", "1"])

            assert result.exit_code == 0
            assert result.output == "! Task #1 is already done\n"

    def test_start_command_permission_error(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            with patch("quadro.storage.TaskStorage.save_task") as mock_save:
                mock_save.side_effect = PermissionError()
                result = runner.invoke(main, ["start", "1"])

                assert result.exit_code == 1
                assert result.output == dedent("""\
                    ✗ Permission denied
                    Cannot access: tasks directory
                    Check that you have read/write permissions for the tasks directory.
                    """)
