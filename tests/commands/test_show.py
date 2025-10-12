from datetime import UTC
from datetime import datetime
from textwrap import dedent

import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from quadro.cli import main
from quadro.command import add_task
from quadro.command import show_task
from quadro.exceptions import TaskNotFoundError
from quadro.models import Task
from quadro.models import TaskStatus


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestShowTask:
    @freeze_time("2025-10-06 12:00:00")
    def test_show_task_valid(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Test task", milestone="mvp")

            task = show_task(1)

            assert task == Task(
                id=1,
                title="Test task",
                description="",
                status=TaskStatus.TODO,
                milestone="mvp",
                created=datetime(2025, 10, 6, 12, 0, 0, tzinfo=UTC),
                completed=None,
            )

    def test_show_task_not_found(self, runner: CliRunner) -> None:
        with (
            runner.isolated_filesystem(),
            pytest.raises(TaskNotFoundError, match="Task #999 not found"),
        ):
            show_task(999)


class TestShowCommandCLI:
    @freeze_time("2025-10-06 12:00:00")
    def test_show_command_valid_case(self, runner: CliRunner) -> None:
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

    def test_show_command_task_not_found(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["show", "999"])

            assert result.exit_code == 1
            assert result.output == "✗ Task #999 not found\n"
