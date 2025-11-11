from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from quadro.cli import main
from quadro.command import add_task
from quadro.command import update_task
from quadro.exceptions import TaskNotFoundError


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestUpdateTask:
    @freeze_time("2024-01-15 10:30:00")
    def test_update_task_title(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Original title", description="Original description")

            updated = update_task(task.id, title="Updated title")

            assert updated.id == 1
            assert updated.title == "Updated title"
            assert updated.description == "Original description"
            assert updated.milestone is None

            task_file = Path("tasks/1.md")
            content = task_file.read_text()
            expected = dedent("""\
                ---
                created: '2024-01-15T10:30:00+00:00'
                status: todo
                ---

                # Updated title

                Original description
                """)
            assert content == expected

    @freeze_time("2024-01-15 10:30:00")
    def test_update_task_description(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Task title", description="Original description")

            updated = update_task(task.id, description="Updated description")

            assert updated.title == "Task title"
            assert updated.description == "Updated description"

            task_file = Path("tasks/1.md")
            content = task_file.read_text()
            expected = dedent("""\
                ---
                created: '2024-01-15T10:30:00+00:00'
                status: todo
                ---

                # Task title

                Updated description
                """)
            assert content == expected

    @freeze_time("2024-01-15 10:30:00")
    def test_update_multiple_fields(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Original title", description="Original description")

            updated = update_task(task.id, title="New title", description="New description")

            assert updated.title == "New title"
            assert updated.description == "New description"

            task_file = Path("tasks/1.md")
            content = task_file.read_text()
            expected = dedent("""\
                ---
                created: '2024-01-15T10:30:00+00:00'
                status: todo
                ---

                # New title

                New description
                """)
            assert content == expected

    def test_update_task_not_found(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            pytest.raises(TaskNotFoundError, match="Task #999 not found"),
        ):
            update_task(999, title="New title")


class TestUpdateCommandCLI:
    @freeze_time("2024-01-15 10:30:00")
    def test_update_command_title(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Original title"])

            result = runner.invoke(main, ["update", "1", "--title", "Updated title"])

            assert result.exit_code == 0
            assert result.output == "✓ Updated task #1: Updated title\n"

    @freeze_time("2024-01-15 10:30:00")
    def test_update_command_description(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task title", "-d", "Original description"])

            result = runner.invoke(main, ["update", "1", "--description", "Updated description"])

            assert result.exit_code == 0
            assert result.output == "✓ Updated task #1: Task title\n"

    @freeze_time("2024-01-15 10:30:00")
    def test_update_command_description_shorthand(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task title", "-d", "Original description"])

            result = runner.invoke(main, ["update", "1", "-d", "Updated with shorthand"])

            assert result.exit_code == 0
            assert result.output == "✓ Updated task #1: Task title\n"

    @freeze_time("2024-01-15 10:30:00")
    def test_update_command_multiple_fields(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Original title", "-d", "Original description"])

            result = runner.invoke(
                main,
                ["update", "1", "--title", "New title", "--description", "New description"],
            )

            assert result.exit_code == 0
            assert result.output == "✓ Updated task #1: New title\n"

    def test_update_command_no_fields(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task title"])

            result = runner.invoke(main, ["update", "1"])

            assert result.exit_code == 1
            expected = dedent("""\
                ✗ At least one field must be specified
                Use --title or --description to update the task
                """)
            assert result.output == expected

    def test_update_command_task_not_found(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["update", "999", "--title", "New title"])

            assert result.exit_code == 1
            assert result.output == "✗ Task #999 not found\n"

    def test_update_command_permission_error(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task title"])

            with patch("quadro.storage.TaskStorage.save_task") as mock_save:
                mock_save.side_effect = PermissionError()
                result = runner.invoke(main, ["update", "1", "--title", "New title"])

                assert result.exit_code == 1
                expected = dedent("""\
                    ✗ Permission denied
                    Cannot access: tasks directory
                    Check that you have read/write permissions for the tasks directory.
                    """)
                assert result.output == expected
