from datetime import UTC
from datetime import datetime
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from quadro.cli import main
from quadro.command import add_task
from quadro.command import list_tasks
from quadro.models import Task
from quadro.models import TaskStatus


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestListTasks:
    def test_list_tasks_empty(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            tasks = list_tasks()

            assert tasks == []

    @freeze_time("2025-10-06 12:00:00")
    def test_list_tasks_with_tasks(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1", milestone="mvp")
            add_task("Task 2")
            add_task("Task 3", milestone="mvp")

            tasks = list_tasks()

            assert len(tasks) == 3
            assert tasks[0] == Task(
                id=1,
                title="Task 1",
                description="",
                status=TaskStatus.TODO,
                milestone="mvp",
                created=datetime(2025, 10, 6, 12, 0, 0, tzinfo=UTC),
                completed=None,
            )
            assert tasks[1] == Task(
                id=2,
                title="Task 2",
                description="",
                status=TaskStatus.TODO,
                milestone=None,
                created=datetime(2025, 10, 6, 12, 0, 0, tzinfo=UTC),
                completed=None,
            )
            assert tasks[2] == Task(
                id=3,
                title="Task 3",
                description="",
                status=TaskStatus.TODO,
                milestone="mvp",
                created=datetime(2025, 10, 6, 12, 0, 0, tzinfo=UTC),
                completed=None,
            )

    def test_list_tasks_returns_all_tasks(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1", milestone="mvp")
            add_task("Task 2")
            add_task("Task 3", milestone="v2.0")

            tasks = list_tasks()

            assert len(tasks) == 3


class TestListCommandCLI:
    def test_list_command_with_no_tasks(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["list"])
            assert result.exit_code == 0
            assert result.output == "No tasks found. Create one with 'quadro add <title>'\n"

    def test_list_command_with_tasks(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1", "--milestone", "mvp"])
            runner.invoke(main, ["add", "Task 2"])
            runner.invoke(main, ["add", "Task 3", "--milestone", "mvp"])

            result = runner.invoke(main, ["list"])

            expected = dedent("""
                ┏━━━━━━━━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━┓
                ┃ Milestone ┃ ID ┃ Title  ┃ Status ┃
                ┡━━━━━━━━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━┩
                │ mvp       │ 1  │ Task 1 │ ○ todo │
                │ -         │ 2  │ Task 2 │ ○ todo │
                │ mvp       │ 3  │ Task 3 │ ○ todo │
                └───────────┴────┴────────┴────────┘

                3 tasks • 0 done • 0 in progress • 3 todo
            """)

            assert result.exit_code == 0
            assert result.output.strip() == expected.strip()

    def test_list_command_with_milestone_filter(self, runner: CliRunner) -> None:
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

    def test_list_command_permission_error(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            patch("quadro.storage.TaskStorage.load_all_tasks") as mock_load,
        ):
            perm_error = PermissionError("tasks")
            perm_error.filename = "tasks"
            mock_load.side_effect = perm_error
            result = runner.invoke(main, ["list"])

            assert result.exit_code == 1
            assert result.output == dedent("""\
                ✗ Permission denied
                Cannot access: tasks
                Check that you have read/write permissions for the tasks directory.
                """)

    def test_list_command_with_todo_filter(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1"])
            runner.invoke(main, ["add", "Task 2"])
            runner.invoke(main, ["add", "Task 3"])
            runner.invoke(main, ["start", "2"])
            runner.invoke(main, ["done", "3"])

            result = runner.invoke(main, ["list", "--todo"])

            expected = dedent("""
                ┏━━━━━━━━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━┓
                ┃ Milestone ┃ ID ┃ Title  ┃ Status ┃
                ┡━━━━━━━━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━┩
                │ -         │ 1  │ Task 1 │ ○ todo │
                └───────────┴────┴────────┴────────┘

                1 tasks • 0 done • 0 in progress • 1 todo
            """)

            assert result.exit_code == 0
            assert result.output.strip() == expected.strip()

    def test_list_command_with_progress_filter(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1"])
            runner.invoke(main, ["add", "Task 2"])
            runner.invoke(main, ["add", "Task 3"])
            runner.invoke(main, ["start", "2"])
            runner.invoke(main, ["done", "3"])

            result = runner.invoke(main, ["list", "--progress"])

            expected = dedent("""
                ┏━━━━━━━━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━━━━━┓
                ┃ Milestone ┃ ID ┃ Title  ┃ Status     ┃
                ┡━━━━━━━━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━━━━━┩
                │ -         │ 2  │ Task 2 │ ▶ progress │
                └───────────┴────┴────────┴────────────┘

                1 tasks • 0 done • 1 in progress • 0 todo
            """)

            assert result.exit_code == 0
            assert result.output.strip() == expected.strip()

    def test_list_command_with_done_filter(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1"])
            runner.invoke(main, ["add", "Task 2"])
            runner.invoke(main, ["add", "Task 3"])
            runner.invoke(main, ["start", "2"])
            runner.invoke(main, ["done", "3"])

            result = runner.invoke(main, ["list", "--done"])

            expected = dedent("""
                ┏━━━━━━━━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━┓
                ┃ Milestone ┃ ID ┃ Title  ┃ Status ┃
                ┡━━━━━━━━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━┩
                │ -         │ 3  │ Task 3 │ ✓ done │
                └───────────┴────┴────────┴────────┘

                1 tasks • 1 done • 0 in progress • 0 todo
            """)

            assert result.exit_code == 0
            assert result.output.strip() == expected.strip()

    def test_list_command_with_multiple_status_filters(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1"])
            runner.invoke(main, ["add", "Task 2"])
            runner.invoke(main, ["add", "Task 3"])
            runner.invoke(main, ["add", "Task 4"])
            runner.invoke(main, ["start", "2"])
            runner.invoke(main, ["done", "3"])

            result = runner.invoke(main, ["list", "--todo", "--progress"])

            expected = dedent("""
                ┏━━━━━━━━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━━━━━┓
                ┃ Milestone ┃ ID ┃ Title  ┃ Status     ┃
                ┡━━━━━━━━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━━━━━┩
                │ -         │ 1  │ Task 1 │ ○ todo     │
                │ -         │ 2  │ Task 2 │ ▶ progress │
                │ -         │ 4  │ Task 4 │ ○ todo     │
                └───────────┴────┴────────┴────────────┘

                3 tasks • 0 done • 1 in progress • 2 todo
            """)

            assert result.exit_code == 0
            assert result.output.strip() == expected.strip()

    def test_list_command_with_status_and_milestone_filters(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1", "--milestone", "mvp"])
            runner.invoke(main, ["add", "Task 2", "--milestone", "mvp"])
            runner.invoke(main, ["add", "Task 3", "--milestone", "v2"])
            runner.invoke(main, ["start", "1"])
            runner.invoke(main, ["done", "2"])

            result = runner.invoke(main, ["list", "--done", "--milestone", "mvp"])

            expected = dedent("""
                ┏━━━━━━━━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━┓
                ┃ Milestone ┃ ID ┃ Title  ┃ Status ┃
                ┡━━━━━━━━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━┩
                │ mvp       │ 2  │ Task 2 │ ✓ done │
                └───────────┴────┴────────┴────────┘

                1 tasks • 1 done • 0 in progress • 0 todo
            """)

            assert result.exit_code == 0
            assert result.output.strip() == expected.strip()

    def test_list_command_with_no_matching_tasks(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task 1"])
            runner.invoke(main, ["add", "Task 2"])

            result = runner.invoke(main, ["list", "--done"])

            assert result.exit_code == 0
            assert result.output == "No tasks found. Create one with 'quadro add <title>'\n"
