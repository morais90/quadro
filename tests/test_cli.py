from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from quadro.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_main_without_command_invokes_list(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert result.output == "No tasks found. Create one with 'quadro add <title>'\n"


def test_list_command_with_no_tasks(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert result.output == "No tasks found. Create one with 'quadro add <title>'\n"


def test_list_command_with_tasks(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Task 1", "--milestone", "mvp"])
        runner.invoke(main, ["add", "Task 2"])
        runner.invoke(main, ["add", "Task 3", "--milestone", "mvp"])

        result = runner.invoke(main, ["list"])

        expected = dedent("""
            ┏━━━━━━━━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━┓
            ┃ Milestone ┃ ID ┃ Title  ┃ Status ┃
            ┡━━━━━━━━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━┩
            │ -         │ 2  │ Task 2 │ ○ todo │
            │ mvp       │ 1  │ Task 1 │ ○ todo │
            │ mvp       │ 3  │ Task 3 │ ○ todo │
            └───────────┴────┴────────┴────────┘

            3 tasks • 0 done • 0 in progress • 3 todo
        """)

        assert result.exit_code == 0
        assert result.output.strip() == expected.strip()


def test_list_command_with_milestone_filter(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Task 1", "--milestone", "mvp"])
        runner.invoke(main, ["add", "Task 2"])
        runner.invoke(main, ["add", "Task 3", "--milestone", "mvp"])

        result = runner.invoke(main, ["list", "--milestone", "mvp"])

        expected = dedent("""
            ┏━━━━━━━━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━┓
            ┃ Milestone ┃ ID ┃ Title  ┃ Status ┃
            ┡━━━━━━━━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━┩
            │ mvp       │ 1  │ Task 1 │ ○ todo │
            │ mvp       │ 3  │ Task 3 │ ○ todo │
            └───────────┴────┴────────┴────────┘

            2 tasks • 0 done • 0 in progress • 2 todo
        """)

        assert result.exit_code == 0
        assert result.output.strip() == expected.strip()


def test_add_command(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["add", "Test task"])

        assert result.exit_code == 0
        assert result.output == "✓ Created task #1\nFile: tasks/1.md\n"

        task_file = Path("tasks/1.md")
        assert task_file.exists()

        content = task_file.read_text()
        assert "# Test task" in content
        assert "status: todo" in content


def test_add_command_with_milestone(runner: CliRunner) -> None:
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


def test_start_command_valid_case(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])

        result = runner.invoke(main, ["start", "1"])

        assert result.exit_code == 0
        assert result.output == "✓ Started task #1: Test task\n"

        task_file = Path("tasks/1.md")
        content = task_file.read_text()
        assert "status: progress" in content


def test_start_command_task_not_found(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["start", "999"])

        assert result.exit_code == 1
        assert result.output == "✗ Task #999 not found\n"


def test_start_command_already_in_progress(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])
        runner.invoke(main, ["start", "1"])

        result = runner.invoke(main, ["start", "1"])

        assert result.exit_code == 0
        assert result.output == "! Task #1 is already in progress\n"


def test_start_command_already_done(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])

        task_file = Path("tasks/1.md")
        content = task_file.read_text()
        content = content.replace("status: todo", "status: done")
        task_file.write_text(content)

        result = runner.invoke(main, ["start", "1"])

        assert result.exit_code == 0
        assert result.output == "! Task #1 is already done\n"


def test_done_command_valid_case(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])

        result = runner.invoke(main, ["done", "1"])

        assert result.exit_code == 0
        assert result.output == "✓ Completed task #1: Test task\n"

        task_file = Path("tasks/1.md")
        content = task_file.read_text()
        assert "status: done" in content
        assert "completed:" in content


def test_done_command_task_not_found(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["done", "999"])

        assert result.exit_code == 1
        assert result.output == "✗ Task #999 not found\n"


def test_done_command_already_done(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])
        runner.invoke(main, ["done", "1"])

        result = runner.invoke(main, ["done", "1"])

        assert result.exit_code == 0
        assert result.output == "! Task #1 is already done\n"


@freeze_time("2025-10-06 12:00:00")
def test_show_command_valid_case(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task with description", "--milestone", "mvp"])

        result = runner.invoke(main, ["show", "1"])

        expected = dedent("""
            #1
            Status: ○ todo
            Milestone: mvp
            Created: 2025-10-06 12:00:00+00:00

            Test task with description
        """)

        assert result.exit_code == 0
        assert result.output.strip() == expected.strip()


def test_show_command_task_not_found(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["show", "999"])

        assert result.exit_code == 1
        assert result.output == "✗ Task #999 not found\n"


def test_milestones_command_with_no_tasks(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["milestones"])

        assert result.exit_code == 0
        assert result.output == "No tasks found. Create one with 'quadro add <title>'\n"


def test_milestones_command_with_no_milestones(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Task without milestone"])

        result = runner.invoke(main, ["milestones"])

        assert result.exit_code == 0
        assert result.output == "No milestones found. Add tasks with '--milestone <name>'\n"


def test_milestones_command_with_milestones(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Task 1", "--milestone", "mvp"])
        runner.invoke(main, ["add", "Task 2", "--milestone", "mvp"])
        runner.invoke(main, ["add", "Task 3", "--milestone", "v2.0"])
        runner.invoke(main, ["done", "1"])

        result = runner.invoke(main, ["milestones"])

        expected = dedent("""
            ┏━━━━━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
            ┃ Milestone ┃ Tasks ┃ Done ┃ Progress                             ┃ Completion ┃
            ┡━━━━━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
            │ mvp       │ 2     │ 1    │ ━━━━━━━━━━━━━━━━━━                   │ 50.0%      │
            │ v2.0      │ 1     │ 0    │                                      │ 0.0%       │
            └───────────┴───────┴──────┴──────────────────────────────────────┴────────────┘
        """)

        assert result.exit_code == 0
        assert result.output.strip() == expected.strip()


def test_move_command_to_milestone(runner: CliRunner) -> None:
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


def test_move_command_to_root(runner: CliRunner) -> None:
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


def test_move_command_between_milestones(runner: CliRunner) -> None:
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


def test_move_command_task_not_found(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["move", "999", "--to", "mvp"])

        assert result.exit_code == 1
        assert result.output == "✗ Task #999 not found\n"


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


def test_add_command_permission_error(runner: CliRunner) -> None:
    with runner.isolated_filesystem(), patch("quadro.storage.TaskStorage.save_task") as mock_save:
        mock_save.side_effect = PermissionError()
        result = runner.invoke(main, ["add", "Test task"])

        assert result.exit_code == 1
        assert "✗ Permission denied" in result.output
        assert "read/write permissions" in result.output


def test_add_command_os_error(runner: CliRunner) -> None:
    with runner.isolated_filesystem(), patch("quadro.storage.TaskStorage.save_task") as mock_save:
        mock_save.side_effect = OSError("No space left on device")
        result = runner.invoke(main, ["add", "Test task"])

        assert result.exit_code == 1
        assert "✗ System error" in result.output
        assert "No space left on device" in result.output
        assert "disk space" in result.output


def test_list_command_permission_error(runner: CliRunner) -> None:
    with (
        runner.isolated_filesystem(),
        patch("quadro.storage.TaskStorage.load_all_tasks") as mock_load,
    ):
        mock_load.side_effect = PermissionError("tasks")
        result = runner.invoke(main, ["list"])

        assert result.exit_code == 1
        assert "✗ Permission denied" in result.output
        assert "Cannot access: tasks" in result.output


def test_start_command_permission_error(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])

        with patch("quadro.storage.TaskStorage.save_task") as mock_save:
            mock_save.side_effect = PermissionError()
            result = runner.invoke(main, ["start", "1"])

            assert result.exit_code == 1
            assert "✗ Permission denied" in result.output
            assert "read/write permissions" in result.output


def test_done_command_permission_error(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])

        with patch("quadro.storage.TaskStorage.save_task") as mock_save:
            mock_save.side_effect = PermissionError()
            result = runner.invoke(main, ["done", "1"])

            assert result.exit_code == 1
            assert "✗ Permission denied" in result.output
            assert "read/write permissions" in result.output


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


def test_move_command_permission_error(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        runner.invoke(main, ["add", "Test task"])

        with patch("quadro.storage.TaskStorage.move_task") as mock_move:
            mock_move.side_effect = PermissionError()
            result = runner.invoke(main, ["move", "1", "--to", "mvp"])

            assert result.exit_code == 1
            assert "✗ Permission denied" in result.output
            assert "read/write permissions" in result.output


def test_milestones_command_permission_error(runner: CliRunner) -> None:
    with (
        runner.isolated_filesystem(),
        patch("quadro.storage.TaskStorage.load_all_tasks") as mock_load,
    ):
        mock_load.side_effect = PermissionError("tasks")
        result = runner.invoke(main, ["milestones"])

        assert result.exit_code == 1
        assert "✗ Permission denied" in result.output


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
