import json
from datetime import UTC
from datetime import datetime

import pytest
from click.testing import CliRunner
from fastmcp.client import Client
from freezegun import freeze_time

from quadro.commands.add import add_task
from quadro.mcp import mcp
from quadro.models import TaskStatus
from quadro.storage import TaskStorage


FROZEN_TIME = "2025-10-06 12:00:00"
FROZEN_TIME_ISO = "2025-10-06T12:00:00Z"


def build_task_json(
    task_id: int,
    title: str,
    status: str = "todo",
    milestone: str | None = None,
    completed: str | None = None,
) -> dict[str, str | int | None]:
    return {
        "id": task_id,
        "title": title,
        "description": "",
        "status": status,
        "milestone": milestone,
        "created": FROZEN_TIME_ISO,
        "completed": completed,
    }


def to_compact_json(data: list[dict[str, str | int | None]]) -> str:
    return json.dumps(data, separators=(",", ":"))


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestListTasksMCPTool:
    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                result = await client.call_tool("list_tasks", {})
                assert result.content == []

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_list_tasks_returns_all_tasks(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1", milestone="mvp")
            add_task("Task 2")
            add_task("Task 3", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool("list_tasks", {})

                expected = to_compact_json(
                    [
                        build_task_json(1, "Task 1", milestone="mvp"),
                        build_task_json(2, "Task 2"),
                        build_task_json(3, "Task 3", milestone="mvp"),
                    ]
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_list_tasks_filters_by_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1", milestone="mvp")
            add_task("Task 2", milestone="v2")
            add_task("Task 3", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool("list_tasks", {"milestone": "mvp"})

                expected = to_compact_json(
                    [
                        build_task_json(1, "Task 1", milestone="mvp"),
                        build_task_json(3, "Task 3", milestone="mvp"),
                    ]
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_list_tasks_filters_by_status(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1")
            task_id_2, _ = add_task("Task 2")
            task_id_3, _ = add_task("Task 3")

            storage = TaskStorage()
            task2 = storage.load_task(task_id_2)
            task3 = storage.load_task(task_id_3)
            assert task2 is not None
            assert task3 is not None

            task2.status = TaskStatus.PROGRESS
            storage.save_task(task2)

            task3.status = TaskStatus.DONE
            task3.completed = datetime.now(UTC)
            storage.save_task(task3)

            async with Client(mcp) as client:
                result = await client.call_tool("list_tasks", {"status": TaskStatus.TODO})

                expected = to_compact_json([build_task_json(1, "Task 1")])

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_list_tasks_filters_by_milestone_and_status(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            task_id_1, _ = add_task("Task 1", milestone="mvp")
            task_id_2, _ = add_task("Task 2", milestone="mvp")
            add_task("Task 3", milestone="v2")

            storage = TaskStorage()
            task1 = storage.load_task(task_id_1)
            task2 = storage.load_task(task_id_2)
            assert task1 is not None
            assert task2 is not None

            task1.status = TaskStatus.DONE
            task1.completed = datetime.now(UTC)
            storage.save_task(task1)

            task2.status = TaskStatus.PROGRESS
            storage.save_task(task2)

            async with Client(mcp) as client:
                result = await client.call_tool(
                    "list_tasks",
                    {"milestone": "mvp", "status": TaskStatus.DONE},
                )

                expected = to_compact_json(
                    [
                        build_task_json(
                            1,
                            "Task 1",
                            status="done",
                            milestone="mvp",
                            completed=FROZEN_TIME_ISO,
                        ),
                    ]
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_list_tasks_raises_error_for_invalid_status(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1")

            async with Client(mcp) as client:
                with pytest.raises(Exception, match="is not one of"):
                    await client.call_tool("list_tasks", {"status": "invalid"})


class TestGetTaskMCPTool:
    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_get_task_returns_task(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task_id, _ = add_task("Test Task", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool("get_task", {"task_id": task_id})

                expected = json.dumps(
                    build_task_json(task_id, "Test Task", milestone="mvp"),
                    separators=(",", ":"),
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    async def test_get_task_raises_error_for_nonexistent_task(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                with pytest.raises(Exception, match="Task #999 not found"):
                    await client.call_tool("get_task", {"task_id": 999})
