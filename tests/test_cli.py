from pathlib import Path

import pytest
from click.testing import CliRunner

from quadro.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_main_without_command_invokes_list(runner: CliRunner) -> None:
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert result.output == "List command not yet implemented\n"


def test_list_command(runner: CliRunner) -> None:
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert result.output == "List command not yet implemented\n"


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
