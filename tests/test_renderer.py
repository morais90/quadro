from quadro.models import TaskStatus
from quadro.renderer import Renderer


def test_status_symbol() -> None:
    assert Renderer.status_symbol(TaskStatus.DONE) == "✓"
    assert Renderer.status_symbol(TaskStatus.PROGRESS) == "▶"
    assert Renderer.status_symbol(TaskStatus.TODO) == "○"
