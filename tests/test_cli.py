import pytest
from click.testing import CliRunner

from quadro.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_main_without_command_invokes_list(runner: CliRunner) -> None:
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "List command not yet implemented" in result.output


def test_list_command(runner: CliRunner) -> None:
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "List command not yet implemented" in result.output
