from pathlib import Path
from textwrap import dedent

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
