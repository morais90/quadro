from datetime import UTC
from datetime import datetime

import pytest

from quadro.models import Task
from quadro.models import TaskStatus


@pytest.fixture
def valid_markdown() -> str:
    return """---
milestone: mvp
status: todo
created: 2025-10-03T09:30:15
---

# Task Title

Task description goes here. Can be multi-line and include
any markdown formatting.
"""


@pytest.fixture
def completed_markdown() -> str:
    return """---
status: done
created: 2025-10-03T09:30:15
completed: 2025-10-03T10:45:22
---

# Completed Task

This task is done.
"""


@pytest.fixture
def no_milestone_markdown() -> str:
    return """---
status: progress
created: 2025-10-03T09:30:15
---

# Task Without Milestone

Description here.
"""


@pytest.fixture
def empty_description_markdown() -> str:
    return """---
status: todo
created: 2025-10-03T09:30:15
---

# Task With Empty Description
"""


@pytest.fixture
def missing_status_markdown() -> str:
    return """---
created: 2025-10-03T09:30:15
---

# Task Title

Description.
"""


@pytest.fixture
def missing_created_markdown() -> str:
    return """---
status: todo
---

# Task Title

Description.
"""


@pytest.fixture
def missing_title_markdown() -> str:
    return """---
status: todo
created: 2025-10-03T09:30:15
---

No title here, just description.
"""


@pytest.fixture
def markdown_with_formatting() -> str:
    return """---
milestone: mvp
status: todo
created: 2025-10-03T09:30:15
---

# Task With Markdown Formatting

This task has **bold text**, *italic text*, and `code blocks`.

It also has:
- Bullet points
- Multiple lines
- With various formatting

## Subheading

And some code:

```python
def hello():
    print("world")
```

Links like [example](https://example.com) should be preserved.
"""


def test_task_creation() -> None:
    task = Task(
        id=1,
        title="Test Task",
        description="This is a test task",
        status=TaskStatus.TODO,
        milestone="mvp",
        created=datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC),
        completed=None,
    )

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "This is a test task"
    assert task.status == TaskStatus.TODO
    assert task.milestone == "mvp"
    assert task.created == datetime(2025, 10, 3, 10, 0, 0, tzinfo=UTC)
    assert task.completed is None


def test_task_status_enum() -> None:
    assert TaskStatus.TODO.value == "todo"
    assert TaskStatus.PROGRESS.value == "progress"
    assert TaskStatus.DONE.value == "done"


def test_from_markdown(valid_markdown: str) -> None:
    task = Task.from_markdown(valid_markdown, task_id=42, file_path="tasks/mvp/42.md")

    assert task.id == 42
    assert task.title == "Task Title"
    assert (
        task.description
        == "Task description goes here. Can be multi-line and include\nany markdown formatting."
    )
    assert task.status == TaskStatus.TODO
    assert task.milestone == "mvp"
    assert task.created == datetime(2025, 10, 3, 9, 30, 15, tzinfo=UTC)
    assert task.completed is None


def test_from_markdown_completed_task(completed_markdown: str) -> None:
    task = Task.from_markdown(completed_markdown, task_id=1, file_path="tasks/1.md")

    assert task.status == TaskStatus.DONE
    assert task.completed == datetime(2025, 10, 3, 10, 45, 22, tzinfo=UTC)
    assert task.milestone is None


def test_from_markdown_no_milestone(no_milestone_markdown: str) -> None:
    task = Task.from_markdown(no_milestone_markdown, task_id=5, file_path="tasks/5.md")

    assert task.milestone is None
    assert task.status == TaskStatus.PROGRESS


def test_from_markdown_empty_description(empty_description_markdown: str) -> None:
    task = Task.from_markdown(empty_description_markdown, task_id=10, file_path="tasks/10.md")

    assert task.title == "Task With Empty Description"
    assert task.description == ""


def test_from_markdown_missing_status(missing_status_markdown: str) -> None:
    with pytest.raises(ValueError, match="Missing 'status' in frontmatter"):
        Task.from_markdown(missing_status_markdown, task_id=1, file_path="tasks/1.md")


def test_from_markdown_missing_created(missing_created_markdown: str) -> None:
    with pytest.raises(ValueError, match="Missing 'created' in frontmatter"):
        Task.from_markdown(missing_created_markdown, task_id=1, file_path="tasks/1.md")


def test_from_markdown_missing_title(missing_title_markdown: str) -> None:
    with pytest.raises(ValueError, match="Missing title \\(H1\\) in markdown content"):
        Task.from_markdown(missing_title_markdown, task_id=1, file_path="tasks/1.md")


def test_from_markdown_with_formatting(markdown_with_formatting: str) -> None:
    task = Task.from_markdown(markdown_with_formatting, task_id=99, file_path="tasks/mvp/99.md")

    expected_description = """This task has **bold text**, *italic text*, and `code blocks`.

It also has:
- Bullet points
- Multiple lines
- With various formatting

## Subheading

And some code:

```python
def hello():
    print("world")
```

Links like [example](https://example.com) should be preserved."""

    assert task.title == "Task With Markdown Formatting"
    assert task.description == expected_description
