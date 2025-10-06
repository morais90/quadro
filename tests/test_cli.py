from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quadro.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_main_without_command_invokes_list(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert result.output == "No tasks found. Create one with 'quadro add <title>'\n"


def test_edit_command_success(runner: CliRunner) -> None:
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


def test_edit_command_cancelled(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])

        with patch("click.edit", return_value=None):
            result = runner.invoke(main, ["edit", "1"])

        assert result.exit_code == 0
        assert result.output == "! Edit cancelled, no changes made\n"


def test_edit_command_no_changes(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])

        task_file = Path("tasks/1.md")
        original_content = task_file.read_text()

        with patch("click.edit", return_value=original_content):
            result = runner.invoke(main, ["edit", "1"])

        assert result.exit_code == 0
        assert result.output == "! No changes made\n"


def test_edit_command_task_not_found(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["edit", "999"])

        assert result.exit_code == 1
        assert result.output == "✗ Task #999 not found\n"


def test_edit_command_invalid_markdown(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])

        invalid_content = "---\nstatus: invalid\n---\nNo title"

        with patch("click.edit", return_value=invalid_content):
            result = runner.invoke(main, ["edit", "1"])

            assert result.exit_code == 1
            assert "✗ Invalid data" in result.output


def test_edit_command_permission_error(runner: CliRunner) -> None:
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
            assert "✗ Permission denied" in result.output
            assert "read/write permissions" in result.output


def test_unexpected_error_handling(runner: CliRunner) -> None:
    with (
        runner.isolated_filesystem(),
        patch("quadro.storage.TaskStorage.get_next_id") as mock_get_id,
    ):
        mock_get_id.side_effect = RuntimeError("Unexpected error occurred")
        result = runner.invoke(main, ["add", "Test task"])

        assert result.exit_code == 1
        assert "✗ Unexpected error" in result.output
        assert "RuntimeError" in result.output
        assert "Unexpected error occurred" in result.output
        assert "report this issue" in result.output
