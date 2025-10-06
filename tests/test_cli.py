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
