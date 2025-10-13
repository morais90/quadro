import json
from datetime import UTC
from datetime import datetime
from textwrap import dedent

import pytest
from click.testing import CliRunner
from fastmcp.client import Client
from freezegun import freeze_time

from quadro.command import add_task
from quadro.mcp import mcp
from quadro.models import TaskStatus
from quadro.storage import TaskStorage


FROZEN_TIME = "2025-10-06 12:00:00"
FROZEN_TIME_ISO = "2025-10-06T12:00:00Z"
FROZEN_TIME_ISO_WITH_TZ = "2025-10-06T12:00:00+00:00"


def build_task_json(  # noqa: PLR0913
    task_id: int,
    title: str,
    status: str = "todo",
    milestone: str | None = None,
    completed: str | None = None,
    description: str = "",
) -> dict[str, str | int | None]:
    return {
        "id": task_id,
        "title": title,
        "description": description,
        "status": status,
        "milestone": milestone,
        "created": FROZEN_TIME_ISO,
        "completed": completed,
    }


def to_compact_json(data: list[dict[str, str | int | None]] | dict[str, str | int | None]) -> str:
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
            task2 = add_task("Task 2")
            task3 = add_task("Task 3")

            storage = TaskStorage()
            task2_loaded = storage.load_task(task2.id)
            task3_loaded = storage.load_task(task3.id)
            assert task2_loaded is not None
            assert task3_loaded is not None

            task2_loaded.status = TaskStatus.PROGRESS
            storage.save_task(task2_loaded)

            task3_loaded.status = TaskStatus.DONE
            task3_loaded.completed = datetime.now(UTC)
            storage.save_task(task3_loaded)

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
            task1 = add_task("Task 1", milestone="mvp")
            task2 = add_task("Task 2", milestone="mvp")
            add_task("Task 3", milestone="v2")

            storage = TaskStorage()
            task1_loaded = storage.load_task(task1.id)
            task2_loaded = storage.load_task(task2.id)
            assert task1_loaded is not None
            assert task2_loaded is not None

            task1_loaded.status = TaskStatus.DONE
            task1_loaded.completed = datetime.now(UTC)
            storage.save_task(task1_loaded)

            task2_loaded.status = TaskStatus.PROGRESS
            storage.save_task(task2_loaded)

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
            task = add_task("Test Task", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool("get_task", {"task_id": task.id})

                expected = to_compact_json(build_task_json(task.id, "Test Task", milestone="mvp"))

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


class TestCreateTaskMCPTool:
    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_create_task_with_title_only(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                result = await client.call_tool("create_task", {"title": "New Task"})

                expected = to_compact_json(build_task_json(1, "New Task"))

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_create_task_with_description(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "create_task",
                    {"title": "New Task", "description": "Task description"},
                )

                expected = to_compact_json(
                    build_task_json(1, "New Task", description="Task description")
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_create_task_with_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "create_task",
                    {"title": "New Task", "milestone": "mvp"},
                )

                expected = to_compact_json(build_task_json(1, "New Task", milestone="mvp"))

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_create_task_with_all_parameters(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "create_task",
                    {
                        "title": "New Task",
                        "description": "Task description",
                        "milestone": "mvp",
                    },
                )

                expected = to_compact_json(
                    build_task_json(1, "New Task", milestone="mvp", description="Task description")
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_create_task_increments_id(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            add_task("Existing Task")

            async with Client(mcp) as client:
                result = await client.call_tool("create_task", {"title": "New Task"})

                expected = to_compact_json(build_task_json(2, "New Task"))

                assert result.content[0].text == expected


class TestStartTaskMCPTool:
    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_start_task_changes_status_to_progress(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool("start_task", {"task_id": task.id})

                expected = to_compact_json(
                    build_task_json(task.id, "Test Task", status="progress", milestone="mvp")
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    async def test_start_task_raises_error_for_nonexistent_task(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                with pytest.raises(Exception, match="Task #999 not found"):
                    await client.call_tool("start_task", {"task_id": 999})

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_start_task_raises_error_for_already_in_progress_task(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task")
            storage = TaskStorage()
            task_loaded = storage.load_task(task.id)
            assert task_loaded is not None

            task_loaded.status = TaskStatus.PROGRESS
            storage.save_task(task_loaded)

            async with Client(mcp) as client:
                with pytest.raises(Exception, match="is already in progress"):
                    await client.call_tool("start_task", {"task_id": task.id})

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_start_task_raises_error_for_already_done_task(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task")
            storage = TaskStorage()
            task_loaded = storage.load_task(task.id)
            assert task_loaded is not None

            task_loaded.status = TaskStatus.DONE
            task_loaded.completed = datetime.now(UTC)
            storage.save_task(task_loaded)

            async with Client(mcp) as client:
                with pytest.raises(Exception, match="is already done"):
                    await client.call_tool("start_task", {"task_id": task.id})


class TestCompleteTaskMCPTool:
    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_complete_task_changes_status_to_done(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool("complete_task", {"task_id": task.id})

                expected = to_compact_json(
                    build_task_json(
                        task.id,
                        "Test Task",
                        status="done",
                        milestone="mvp",
                        completed=FROZEN_TIME_ISO,
                    )
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_complete_task_from_progress_status(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task")
            storage = TaskStorage()
            task_loaded = storage.load_task(task.id)
            assert task_loaded is not None

            task_loaded.status = TaskStatus.PROGRESS
            storage.save_task(task_loaded)

            async with Client(mcp) as client:
                result = await client.call_tool("complete_task", {"task_id": task.id})

                expected = to_compact_json(
                    build_task_json(task.id, "Test Task", status="done", completed=FROZEN_TIME_ISO)
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    async def test_complete_task_raises_error_for_nonexistent_task(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                with pytest.raises(Exception, match="Task #999 not found"):
                    await client.call_tool("complete_task", {"task_id": 999})

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_complete_task_raises_error_for_already_done_task(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task")
            storage = TaskStorage()
            task_loaded = storage.load_task(task.id)
            assert task_loaded is not None

            task_loaded.status = TaskStatus.DONE
            task_loaded.completed = datetime.now(UTC)
            storage.save_task(task_loaded)

            async with Client(mcp) as client:
                with pytest.raises(Exception, match="is already done"):
                    await client.call_tool("complete_task", {"task_id": task.id})


class TestMoveTaskMCPTool:
    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_move_task_from_root_to_milestone(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task")

            async with Client(mcp) as client:
                result = await client.call_tool(
                    "move_task",
                    {"task_id": task.id, "to_milestone": "mvp"},
                )

                expected = to_compact_json(build_task_json(task.id, "Test Task", milestone="mvp"))

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_move_task_from_milestone_to_another_milestone(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool(
                    "move_task",
                    {"task_id": task.id, "to_milestone": "v2"},
                )

                expected = to_compact_json(build_task_json(task.id, "Test Task", milestone="v2"))

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_move_task_from_milestone_to_root(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool(
                    "move_task",
                    {"task_id": task.id, "to_milestone": "root"},
                )

                expected = to_compact_json(build_task_json(task.id, "Test Task"))

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    async def test_move_task_raises_error_for_nonexistent_task(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                with pytest.raises(Exception, match="Task #999 not found"):
                    await client.call_tool("move_task", {"task_id": 999, "to_milestone": "mvp"})


class TestDeleteTaskMCPTool:
    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_delete_task_returns_deleted_task(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task", description="Test description", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool("delete_task", {"task_id": task.id})

                expected = to_compact_json(
                    build_task_json(
                        task.id,
                        "Test Task",
                        description="Test description",
                        milestone="mvp",
                    )
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    async def test_delete_task_raises_error_for_nonexistent_task(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                with pytest.raises(Exception, match="Task #999 not found"):
                    await client.call_tool("delete_task", {"task_id": 999})


class TestListMilestonesMCPTool:
    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_list_milestones_returns_tasks_with_milestones(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1", milestone="mvp")
            add_task("Task 2")
            add_task("Task 3", milestone="v2")
            add_task("Task 4", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.call_tool("list_milestones", {})

                expected = to_compact_json(
                    [
                        build_task_json(1, "Task 1", milestone="mvp"),
                        build_task_json(3, "Task 3", milestone="v2"),
                        build_task_json(4, "Task 4", milestone="mvp"),
                    ]
                )

                assert result.content[0].text == expected

    @pytest.mark.asyncio
    async def test_list_milestones_raises_error_when_no_tasks_exist(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                with pytest.raises(Exception, match="No tasks found"):
                    await client.call_tool("list_milestones", {})

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_list_milestones_returns_empty_when_no_milestones_assigned(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            add_task("Task 1")
            add_task("Task 2")

            async with Client(mcp) as client:
                result = await client.call_tool("list_milestones", {})

                assert result.content == []


class TestGetTaskResourceMCP:
    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_get_task_resource_returns_markdown(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task", description="Task description", milestone="mvp")

            async with Client(mcp) as client:
                result = await client.read_resource(f"quadro://task/{task.id}")

                expected_markdown = dedent(f"""\
                    ---
                    created: '{FROZEN_TIME_ISO_WITH_TZ}'
                    milestone: mvp
                    status: todo
                    ---

                    # Test Task

                    Task description
                    """)

                assert result[0].text == expected_markdown

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_get_task_resource_without_description(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task")

            async with Client(mcp) as client:
                result = await client.read_resource(f"quadro://task/{task.id}")

                expected_markdown = dedent(f"""\
                    ---
                    created: '{FROZEN_TIME_ISO_WITH_TZ}'
                    status: todo
                    ---

                    # Test Task
                    """)

                assert result[0].text == expected_markdown

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_get_task_resource_completed_task(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            task = add_task("Test Task", milestone="mvp")
            storage = TaskStorage()
            task_loaded = storage.load_task(task.id)
            assert task_loaded is not None

            task_loaded.status = TaskStatus.DONE
            task_loaded.completed = datetime.now(UTC)
            storage.save_task(task_loaded)

            async with Client(mcp) as client:
                result = await client.read_resource(f"quadro://task/{task.id}")

                expected_markdown = dedent(f"""\
                    ---
                    completed: '{FROZEN_TIME_ISO_WITH_TZ}'
                    created: '{FROZEN_TIME_ISO_WITH_TZ}'
                    milestone: mvp
                    status: done
                    ---

                    # Test Task
                    """)

                assert result[0].text == expected_markdown

    @pytest.mark.asyncio
    @freeze_time(FROZEN_TIME)
    async def test_get_task_resource_with_complex_markdown(self, runner: CliRunner) -> None:
        with runner.isolated_filesystem():
            description = dedent("""\
                ## Implementation Details

                - [ ] Create resource for each task
                - [ ] Resource contains full task markdown content
                - [x] Allows AI to read task files directly

                ### Code Example

                ```python
                def get_task(task_id: int) -> Task:
                    return storage.load_task(task_id)
                ```

                **Important**: This needs to be tested thoroughly.

                > Note: Auto-updates when tasks change.""")

            task = add_task("Complex Task", description=description, milestone="v2")

            async with Client(mcp) as client:
                result = await client.read_resource(f"quadro://task/{task.id}")

                expected_markdown = f"""---
created: '{FROZEN_TIME_ISO_WITH_TZ}'
milestone: v2
status: todo
---

# Complex Task

{description}
"""

                assert result[0].text == expected_markdown

    @pytest.mark.asyncio
    async def test_get_task_resource_raises_error_for_nonexistent_task(
        self,
        runner: CliRunner,
    ) -> None:
        with runner.isolated_filesystem():
            async with Client(mcp) as client:
                with pytest.raises(Exception, match="Task 999 not found"):
                    await client.read_resource("quadro://task/999")
