from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quadro.cli import main
from quadro.command import add_task
from quadro.command import move_task
from quadro.exceptions import TaskNotFoundError


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestMoveTask:
    def test_move_task_to_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1")

            old_milestone, new_milestone, new_path = move_task(1, "mvp")

            assert (old_milestone, new_milestone, new_path) == ("root", "mvp", "tasks/mvp/1.md")

    def test_move_task_to_root(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1", milestone="mvp")

            old_milestone, new_milestone, new_path = move_task(1, "root")

            assert (old_milestone, new_milestone, new_path) == ("mvp", "root", "tasks/1.md")

    def test_move_task_between_milestones(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1", milestone="mvp")

            old_milestone, new_milestone, new_path = move_task(1, "v2.0")

            assert (old_milestone, new_milestone, new_path) == ("mvp", "v2.0", "tasks/v2.0/1.md")

    def test_move_task_not_found(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            pytest.raises(TaskNotFoundError, match="Task #999 not found"),
        ):
            move_task(999, "mvp")


class TestMoveCommandCLI:
    def test_move_command_to_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1"])

            result = runner.invoke(main, ["move", "1", "--to", "mvp"])

            assert result.exit_code == 0
            assert "✓ Moved task #1 from root to mvp" in result.output
            assert "New location: tasks/mvp/1.md" in result.output

            task_file = Path("tasks/mvp/1.md")
            assert task_file.exists()
            content = task_file.read_text()
            assert "milestone: mvp" in content

    def test_move_command_to_root(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1", "--milestone", "mvp"])

            result = runner.invoke(main, ["move", "1", "--to", "root"])

            assert result.exit_code == 0
            assert "✓ Moved task #1 from mvp to root" in result.output
            assert "New location: tasks/1.md" in result.output

            task_file = Path("tasks/1.md")
            assert task_file.exists()
            content = task_file.read_text()
            assert "milestone:" not in content

    def test_move_command_between_milestones(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1", "--milestone", "mvp"])

            result = runner.invoke(main, ["move", "1", "--to", "v2.0"])

            assert result.exit_code == 0
            assert "✓ Moved task #1 from mvp to v2.0" in result.output
            assert "New location: tasks/v2.0/1.md" in result.output

            task_file = Path("tasks/v2.0/1.md")
            assert task_file.exists()
            content = task_file.read_text()
            assert "milestone: v2.0" in content

    def test_move_command_task_not_found(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["move", "999", "--to", "mvp"])

            assert result.exit_code == 1
            assert result.output == "✗ Task #999 not found\n"

    def test_move_command_permission_error(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            with patch("quadro.storage.TaskStorage.move_task") as mock_move:
                mock_move.side_effect = PermissionError()
                result = runner.invoke(main, ["move", "1", "--to", "mvp"])

                assert result.exit_code == 1
                assert result.output == dedent("""\
                    ✗ Permission denied
                    Cannot access: tasks directory
                    Check that you have read/write permissions for the tasks directory.
                    """)
