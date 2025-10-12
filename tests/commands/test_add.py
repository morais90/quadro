from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from quadro.cli import main
from quadro.command import add_task


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestAddTask:
    def test_add_task_basic(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test task")

            assert task.id == 1
            assert task.title == "Test task"
            assert task.milestone is None

            task_file = Path("tasks/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            assert "# Test task" in content
            assert "status: todo" in content
            assert "milestone:" not in content

    def test_add_task_with_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Task with milestone", milestone="mvp")

            assert task.id == 1
            assert task.title == "Task with milestone"
            assert task.milestone == "mvp"

            task_file = Path("tasks/mvp/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            assert "# Task with milestone" in content
            assert "milestone: mvp" in content
            assert "status: todo" in content

    def test_add_task_increments_id(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task1 = add_task("First task")
            task2 = add_task("Second task")
            task3 = add_task("Third task")

            assert task1.id == 1
            assert task2.id == 2
            assert task3.id == 3

    @freeze_time("2024-01-15 10:30:00")
    def test_add_task_with_description(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Task with description", description="This is a detailed description")

            assert task.id == 1
            assert task.description == "This is a detailed description"

            task_file = Path("tasks/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            expected = dedent("""\
                ---
                created: '2024-01-15T10:30:00+00:00'
                status: todo
                ---

                # Task with description

                This is a detailed description
                """)

            assert content == expected

    @freeze_time("2024-01-15 10:30:00")
    def test_add_task_with_description_and_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task(
                "Complex task", description="Detailed explanation of the task", milestone="v2.0"
            )

            assert task.id == 1
            assert task.description == "Detailed explanation of the task"
            assert task.milestone == "v2.0"

            task_file = Path("tasks/v2.0/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            expected = dedent("""\
                ---
                created: '2024-01-15T10:30:00+00:00'
                milestone: v2.0
                status: todo
                ---

                # Complex task

                Detailed explanation of the task
                """)

            assert content == expected


class TestAddCommandCLI:
    def test_add_command(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["add", "Test task"])

            assert result.exit_code == 0
            assert result.output == "✓ Created task #1\n"

            task_file = Path("tasks/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            assert "# Test task" in content
            assert "status: todo" in content

    def test_add_command_with_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["add", "Task with milestone", "--milestone", "mvp"])

            assert result.exit_code == 0
            assert result.output == "✓ Created task #1\n"

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
            assert result.output == dedent("""\
                ✗ Permission denied
                Cannot access: tasks directory
                Check that you have read/write permissions for the tasks directory.
                """)

    def test_add_command_os_error(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            patch("quadro.storage.TaskStorage.save_task") as mock_save,
        ):
            mock_save.side_effect = OSError("No space left on device")
            result = runner.invoke(main, ["add", "Test task"])

            assert result.exit_code == 1
            assert result.output == dedent("""\
                ✗ System error
                No space left on device
                Check disk space and file permissions.
                """)

    @freeze_time("2024-01-15 10:30:00")
    def test_add_command_with_description(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(
                main,
                ["add", "Task with description", "--description", "This is a detailed description"],
            )

            assert result.exit_code == 0
            assert result.output == "✓ Created task #1\n"

            task_file = Path("tasks/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            expected = dedent("""\
                ---
                created: '2024-01-15T10:30:00+00:00'
                status: todo
                ---

                # Task with description

                This is a detailed description
                """)

            assert content == expected

    @freeze_time("2024-01-15 10:30:00")
    def test_add_command_with_description_shorthand(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(
                main, ["add", "Task with description", "-d", "Using shorthand flag"]
            )

            assert result.exit_code == 0
            assert result.output == "✓ Created task #1\n"

            task_file = Path("tasks/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            expected = dedent("""\
                ---
                created: '2024-01-15T10:30:00+00:00'
                status: todo
                ---

                # Task with description

                Using shorthand flag
                """)

            assert content == expected

    @freeze_time("2024-01-15 10:30:00")
    def test_add_command_with_description_and_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(
                main, ["add", "Complex task", "-d", "Detailed explanation", "--milestone", "v2.0"]
            )

            assert result.exit_code == 0
            assert result.output == "✓ Created task #1\n"

            task_file = Path("tasks/v2.0/1.md")
            assert task_file.exists()

            content = task_file.read_text()
            expected = dedent("""\
                ---
                created: '2024-01-15T10:30:00+00:00'
                milestone: v2.0
                status: todo
                ---

                # Complex task

                Detailed explanation
                """)

            assert content == expected
