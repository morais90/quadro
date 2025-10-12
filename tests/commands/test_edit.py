from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quadro.cli import main
from quadro.command import add_task
from quadro.command import get_task_markdown
from quadro.command import update_task_from_markdown
from quadro.exceptions import TaskNotFoundError


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestGetTaskMarkdown:
    def test_get_task_markdown_success(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task", milestone="mvp")

            markdown = get_task_markdown(1)

            assert "Test task" in markdown
            assert "status: todo" in markdown
            assert "milestone: mvp" in markdown

    def test_get_task_markdown_not_found(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            pytest.raises(TaskNotFoundError, match="Task #999 not found"),
        ):
            get_task_markdown(999)


class TestUpdateTaskFromMarkdown:
    def test_update_task_from_markdown_success(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Original task", milestone="mvp")

            task_file = Path("tasks/mvp/1.md")
            original_content = task_file.read_text()
            edited_content = original_content.replace("Original task", "Edited task")

            task = update_task_from_markdown(1, edited_content)

            assert task.title == "Edited task"
            updated_content = task_file.read_text()
            assert "Edited task" in updated_content

    def test_update_task_from_markdown_not_found(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            pytest.raises(TaskNotFoundError, match="Task #999 not found"),
        ):
            update_task_from_markdown(999, "---\nstatus: todo\n---\nTest")

    def test_update_task_from_markdown_invalid(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task")

            invalid_content = (
                "---\nstatus: invalid\ncreated: 2025-10-03T09:30:15+00:00\n---\nNo title"
            )

            with pytest.raises(ValueError, match="'invalid' is not a valid TaskStatus"):
                update_task_from_markdown(1, invalid_content)


class TestEditCommandCLI:
    def test_edit_command_success(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Original task", "--milestone", "mvp"])

            task_file = Path("tasks/mvp/1.md")
            original_content = task_file.read_text()

            edited_content = original_content.replace("Original task", "Edited task")

            with patch("click.edit", return_value=edited_content):
                result = runner.invoke(main, ["edit", "1"])

            assert result.exit_code == 0
            assert result.output == "✓ Updated task #1\n"

            updated_content = task_file.read_text()
            assert "Edited task" in updated_content

    def test_edit_command_cancelled(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            with patch("click.edit", return_value=None):
                result = runner.invoke(main, ["edit", "1"])

            assert result.exit_code == 0
            assert result.output == "! Edit cancelled, no changes made\n"

    def test_edit_command_no_changes(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            task_file = Path("tasks/1.md")
            original_content = task_file.read_text()

            with patch("click.edit", return_value=original_content):
                result = runner.invoke(main, ["edit", "1"])

            assert result.exit_code == 0
            assert result.output == "! No changes made\n"

    def test_edit_command_task_not_found(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["edit", "999"])

            assert result.exit_code == 1
            assert result.output == "✗ Task #999 not found\n"

    def test_edit_command_invalid_markdown(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            invalid_content = "---\nstatus: invalid\n---\nNo title"

            with patch("click.edit", return_value=invalid_content):
                result = runner.invoke(main, ["edit", "1"])

                assert result.exit_code == 1
                assert "✗ Invalid data" in result.output

    def test_edit_command_permission_error(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Test task"])

            task_file = Path("tasks/1.md")
            edited_content = task_file.read_text().replace("Test task", "Edited task")

            with (
                patch("click.edit", return_value=edited_content),
                patch("quadro.storage.TaskStorage.save_task") as mock_save,
            ):
                mock_save.side_effect = PermissionError()
                result = runner.invoke(main, ["edit", "1"])

                assert result.exit_code == 1
                assert result.output == dedent("""\
                    ✗ Permission denied
                    Cannot access: tasks directory
                    Check that you have read/write permissions for the tasks directory.
                    """)
