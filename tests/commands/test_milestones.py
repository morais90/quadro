from datetime import UTC
from datetime import datetime
from textwrap import dedent
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from quadro.cli import main
from quadro.command import add_task
from quadro.command import list_milestones
from quadro.exceptions import TaskNotFoundError
from quadro.models import Task
from quadro.models import TaskStatus


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestListMilestones:
    def test_list_milestones_no_tasks(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            pytest.raises(TaskNotFoundError, match="No tasks found"),
        ):
            list_milestones()

    def test_list_milestones_no_milestones(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task without milestone")

            tasks = list_milestones()

            assert tasks == []

    @freeze_time("2025-10-06 12:00:00")
    def test_list_milestones_filters_only_milestone_tasks(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1", milestone="mvp")
            add_task("Task 2")
            add_task("Task 3", milestone="v2.0")

            tasks = list_milestones()

            assert len(tasks) == 2
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
                id=3,
                title="Task 3",
                description="",
                status=TaskStatus.TODO,
                milestone="v2.0",
                created=datetime(2025, 10, 6, 12, 0, 0, tzinfo=UTC),
                completed=None,
            )


class TestMilestonesCommandCLI:
    def test_milestones_command_with_no_tasks(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["milestones"])

            assert result.exit_code == 0
            assert result.output == "No tasks found. Create one with 'quadro add <title>'\n"

    def test_milestones_command_with_no_milestones(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            runner.invoke(main, ["add", "Task without milestone"])

            result = runner.invoke(main, ["milestones"])

            assert result.exit_code == 0
            assert result.output == "No milestones found. Add tasks with '--milestone <name>'\n"

    def test_milestones_command_with_milestones(self, runner: CliRunner) -> None:
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

    def test_milestones_command_permission_error(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            patch("quadro.storage.TaskStorage.load_all_tasks") as mock_load,
        ):
            mock_load.side_effect = PermissionError("tasks")
            result = runner.invoke(main, ["milestones"])

            assert result.exit_code == 1
            assert "✗ Permission denied" in result.output
