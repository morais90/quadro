# Quadro - Terminal Task Manager

> Manage your tasks directly from the terminal using markdown

## Overview

Quadro is a CLI task manager that organizes tasks in markdown files with a folder-based structure. Built with Python, Click, and Rich for a beautiful terminal experience.

---

## Tech Stack

- **Python 3.12+** - Modern Python features
- **uv** - Fast Python package manager
- **Click** - CLI framework
- **Rich** - Beautiful terminal output
- **python-frontmatter** - YAML frontmatter parsing

### Development Tools

- **Ruff** - Linting & formatting (strict, all rules)
- **Mypy** - Type checking (strict mode)
- **Bandit** - Security scanning
- **Pytest** - Testing with 80% coverage
- **Pre-commit** - Git hooks for quality gates
- **GitHub Actions** - CI/CD pipeline

---

## Project Structure

```
quadro/
├── pyproject.toml              # Python project configuration
├── roadmap.md                  # This file - project roadmap
├── quadro/
│   ├── __init__.py            # Package initialization
│   ├── cli.py                 # Click CLI entry point & commands
│   ├── task.py                # Task data model & parsing
│   ├── storage.py             # File system operations
│   └── renderer.py            # Rich terminal rendering
└── tasks/                      # Auto-created task storage
    ├── [milestone]/           # Milestone folders
    │   └── [id].md           # Task files
    └── [id].md               # Root tasks (no milestone)
```

---

## Task File Format

```markdown
---
milestone: mvp              # Optional: milestone name
status: todo               # todo, progress, done
created: 2025-10-03T09:30:15
completed: 2025-10-03T10:45:22  # Only when status=done
---

# Task Title

Task description goes here. Can be multi-line and include
any markdown formatting.
```

---

## Commands

### Core Commands

| Command | Description | Status |
|---------|-------------|--------|
| `quadro add <title> [--milestone <name>]` | Add new task | ⏳ Todo |
| `quadro list [milestone]` | Show all tasks or filter by milestone | ⏳ Todo |
| `quadro start <id>` | Mark task as in progress | ⏳ Todo |
| `quadro done <id>` | Mark task as complete | ⏳ Todo |
| `quadro show <id>` | View task details | ⏳ Todo |
| `quadro milestones` | Show all milestones with progress | ⏳ Todo |
| `quadro move <id> --to <milestone>` | Move task to different milestone | ⏳ Todo |
| `quadro edit <id>` | Open task in $EDITOR | ⏳ Todo |

### Default Behavior

- `quadro` (no command) → defaults to `quadro list`

---

## Implementation Roadmap

### Validation Pipeline (Applied to Every Task)

After each atomic task, run:
1. **Ruff** - `uv run ruff check quadro/ && uv run ruff format --check quadro/` - Linting & formatting
2. **Mypy** - `uv run mypy quadro/` - Type checking (strict mode)
3. **Bandit** - `uv run bandit -c pyproject.toml -r quadro/` - Security scanning
4. **Pytest** - `uv run pytest tests/` - Unit tests with 80% coverage

Or simply run: `uv run pre-commit run --all-files`

Only proceed to next task when all checks pass ✓

---

### Phase 1: MVP - Core Functionality ⏳

**Goal:** Build a fully functional task manager with all essential commands

#### Task 1.1: Project Bootstrap ⏳
**Deliverable:** Working Python package with dependencies

- [x] **1.1.1** Create `pyproject.toml` with uv
  - **[project]**
    - `name = "quadro"`
    - `version = "0.1.0"`
    - `description = "Manage your tasks directly from the terminal using markdown"`
    - `requires-python = ">=3.12"`
    - `dependencies = ["click>=8.1.7", "rich>=13.7.0", "python-frontmatter>=1.1.0"]`
    - `[project.scripts]`: `quadro = "quadro.cli:main"`
  - **[build-system]**
    - `requires = ["hatchling"]`
    - `build-backend = "hatchling.build"`
  - **[tool.uv]**
    - `dev-dependencies = ["ruff>=0.1.0", "mypy>=1.7.0", "pytest>=7.4.0", "pytest-cov>=4.1.0", "bandit>=1.7.5", "pre-commit>=3.5.0", "types-python-frontmatter>=1.0.0"]`
  - **Validation:** `uv sync` succeeds

- [x] **1.1.2** Create `quadro/__init__.py`
  - Content: `__version__ = "0.1.0"`
  - **Validation:** `python -c "import quadro; print(quadro.__version__)"` prints `0.1.0`

- [ ] **1.1.3** Create `.gitignore`
  - Include: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `dist/`, `*.egg-info/`, `tasks/`, `.coverage`, `htmlcov/`, `.venv/`, `uv.lock`
  - **Validation:** Manual review

- [ ] **1.1.3a** Create `uv.lock` file
  - Run: `uv lock`
  - **Validation:** `uv.lock` file exists

- [ ] **1.1.4** Setup strict ruff configuration in `pyproject.toml`
  - **[tool.ruff]**
    - `line-length = 100`
    - `target-version = "py312"`
    - `exclude = [".git", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"]`
  - **[tool.ruff.lint]**
    - `select = ["ALL"]` (enable all rules)
    - `ignore = ["D", "ANN101", "ANN102", "COM812", "ISC001"]` (disable: docstrings for now, self/cls annotations, trailing comma conflicts)
  - **[tool.ruff.lint.per-file-ignores]**
    - `"tests/*" = ["S101", "PLR2004", "SLF001"]` (allow assert, magic values, private access in tests)
  - **[tool.ruff.lint.isort]**
    - `force-single-line = true`
    - `lines-after-imports = 2`
  - **[tool.ruff.format]**
    - `quote-style = "double"`
    - `indent-style = "space"`
  - **Validation:** `ruff check quadro/` runs without errors

- [ ] **1.1.5** Setup strict mypy configuration in `pyproject.toml`
  - **[tool.mypy]**
    - `python_version = "3.12"`
    - `strict = true`
    - `warn_return_any = true`
    - `warn_unused_configs = true`
    - `disallow_untyped_defs = true`
    - `disallow_any_unimported = true`
    - `no_implicit_optional = true`
    - `warn_redundant_casts = true`
    - `warn_unused_ignores = true`
    - `warn_unreachable = true`
    - `strict_equality = true`
    - `extra_checks = true`
  - **Validation:** `mypy quadro/` passes (no files yet, should succeed)

- [ ] **1.1.6** Setup bandit configuration in `pyproject.toml`
  - **[tool.bandit]**
    - `targets = ["quadro"]`
    - `exclude_dirs = ["tests", ".venv"]`
    - `skips = []` (no skips - all security checks enabled)
    - `severity = "medium"` (medium and high severity issues)
  - **Validation:** `bandit -c pyproject.toml -r quadro/` runs without errors

- [ ] **1.1.7** Setup pytest configuration in `pyproject.toml`
  - **[tool.pytest.ini_options]**
    - `testpaths = ["tests"]`
    - `python_files = "test_*.py"`
    - `python_functions = "test_*"`
    - `addopts = "-v --strict-markers --cov=quadro --cov-report=term-missing --cov-report=html --cov-fail-under=80"`
    - `markers = ["slow: marks tests as slow", "integration: marks tests as integration tests"]`
  - **[tool.coverage.run]**
    - `branch = true`
    - `source = ["quadro"]`
    - `omit = ["tests/*", "**/__init__.py"]`
  - **[tool.coverage.report]**
    - `precision = 2`
    - `show_missing = true`
    - `skip_covered = false`
  - **Validation:** `pytest --collect-only` succeeds

- [ ] **1.1.8** Create `.pre-commit-config.yaml`
  - **repos:**
    - **Ruff** (https://github.com/astral-sh/ruff-pre-commit, rev: v0.1.9)
      - `id: ruff` with `args: [--fix]`
      - `id: ruff-format`
    - **Mypy** (https://github.com/pre-commit/mirrors-mypy, rev: v1.7.1)
      - `id: mypy`
      - `additional_dependencies: [click, rich, python-frontmatter, types-python-frontmatter]`
    - **Bandit** (https://github.com/PyCQA/bandit, rev: 1.7.5)
      - `id: bandit`
      - `args: [-c, pyproject.toml]`
      - `additional_dependencies: ["bandit[toml]"]`
    - **Pytest** (https://github.com/pre-commit/mirrors-pytest, rev: v7.4.3)
      - `id: pytest`
      - `args: [--cov=quadro, --cov-fail-under=80]`
      - `pass_filenames: false`
      - `always_run: true`
  - **Validation:** Manual review

- [ ] **1.1.9** Initialize pre-commit hooks
  - Run: `uv run pre-commit install`
  - Run: `uv run pre-commit run --all-files` (should pass on empty repo)
  - **Validation:** `.git/hooks/pre-commit` exists and contains pre-commit script

- [ ] **1.1.10** Create `.github/workflows/ci.yml` for GitHub Actions
  - **name:** CI
  - **on:** push, pull_request (branches: main, master)
  - **jobs.test:**
    - **Strategy matrix:** Python versions: `["3.12", "3.13"]`
    - **Steps:**
      1. Checkout code (`actions/checkout@v4`)
      2. Install uv (`astral-sh/setup-uv@v3`)
      3. Set Python version (`uv python install ${{ matrix.python-version }}`)
      4. Install dependencies (`uv sync --all-extras --dev`)
      5. Run Ruff (`uv run ruff check quadro/ && uv run ruff format --check quadro/`)
      6. Run Mypy (`uv run mypy quadro/`)
      7. Run Bandit (`uv run bandit -c pyproject.toml -r quadro/`)
      8. Run tests (`uv run pytest tests/ --cov=quadro --cov-report=xml --cov-report=term`)
      9. Upload coverage to Codecov (`codecov/codecov-action@v3`, if: `matrix.python-version == '3.12'`)
  - **Validation:** Manual review

- [ ] **1.1.11** Create `.github/workflows/release.yml` for releases (future)
  - **name:** Release
  - **on:** push to tags `v*`
  - **jobs.release:**
    - Build package with `uv build`
    - Publish to PyPI with `uv publish`
  - **Validation:** Manual review (won't run until tags exist)

#### Task 1.2: Task Data Model ⏳
**Deliverable:** Task class with frontmatter parsing/writing

- [ ] **1.2.1** Create `quadro/models.py` with `TaskStatus` enum
  - Import: `from enum import Enum`
  - Class: `TaskStatus(str, Enum)` with values: `TODO = "todo"`, `PROGRESS = "progress"`, `DONE = "done"`
  - **Validation:** Run validation pipeline

- [ ] **1.2.2** Create `Task` dataclass in `quadro/models.py`
  - Import: `from dataclasses import dataclass`, `from datetime import datetime`
  - Fields: `id: int`, `title: str`, `description: str`, `status: TaskStatus`, `milestone: str | None`, `created: datetime`, `completed: datetime | None`
  - **Validation:** Run validation pipeline

- [ ] **1.2.3** Create `tests/test_models.py` with basic tests
  - Test: `test_task_creation()` - Create Task instance with all fields
  - Test: `test_task_status_enum()` - Verify TaskStatus values
  - **Validation:** `pytest tests/test_models.py -v` passes

- [ ] **1.2.4** Add `Task.from_markdown()` classmethod in `quadro/models.py`
  - Import: `import frontmatter`
  - Signature: `def from_markdown(cls, content: str, task_id: int, file_path: str) -> Task`
  - Parse frontmatter, extract title (first H1), extract description
  - **Validation:** Run validation pipeline

- [ ] **1.2.5** Create `tests/test_models.py::test_from_markdown()`
  - Test with sample markdown string with frontmatter
  - Verify all fields parsed correctly
  - **Validation:** `pytest tests/test_models.py::test_from_markdown -v` passes

- [ ] **1.2.6** Add `Task.to_markdown()` method in `quadro/models.py`
  - Signature: `def to_markdown(self) -> str`
  - Generate frontmatter + H1 title + description
  - **Validation:** Run validation pipeline

- [ ] **1.2.7** Create `tests/test_models.py::test_to_markdown()`
  - Test roundtrip: markdown → Task → markdown
  - Verify output matches expected format
  - **Validation:** `pytest tests/test_models.py::test_to_markdown -v` passes

#### Task 1.3: Storage Layer ⏳
**Deliverable:** File system operations for tasks

- [ ] **1.3.1** Create `quadro/storage.py` with `TaskStorage` class
  - Import: `from pathlib import Path`, `import re`
  - Class: `TaskStorage` with `__init__(self, base_path: Path = Path("tasks"))`
  - **Validation:** Run validation pipeline

- [ ] **1.3.2** Add `TaskStorage.get_next_id()` method
  - Signature: `def get_next_id(self) -> int`
  - Scan all task files, extract IDs from filenames, return max + 1
  - **Validation:** Run validation pipeline

- [ ] **1.3.3** Create `tests/test_storage.py::test_get_next_id()`
  - Use `tmp_path` fixture
  - Create dummy task files, verify next ID
  - **Validation:** `pytest tests/test_storage.py::test_get_next_id -v` passes

- [ ] **1.3.4** Add `TaskStorage.save_task()` method
  - Signature: `def save_task(self, task: Task) -> Path`
  - Create milestone folder if needed
  - Write task to `tasks/[milestone]/[id].md` or `tasks/[id].md`
  - **Validation:** Run validation pipeline

- [ ] **1.3.5** Create `tests/test_storage.py::test_save_task()`
  - Test saving to milestone and root
  - Verify file created at correct path
  - **Validation:** `pytest tests/test_storage.py::test_save_task -v` passes

- [ ] **1.3.6** Add `TaskStorage.load_task()` method
  - Signature: `def load_task(self, task_id: int) -> Task | None`
  - Search for task file by ID
  - Return Task or None if not found
  - **Validation:** Run validation pipeline

- [ ] **1.3.7** Create `tests/test_storage.py::test_load_task()`
  - Test loading existing and non-existent tasks
  - **Validation:** `pytest tests/test_storage.py::test_load_task -v` passes

- [ ] **1.3.8** Add `TaskStorage.load_all_tasks()` method
  - Signature: `def load_all_tasks(self) -> list[Task]`
  - Recursively find all `.md` files
  - Parse each into Task object
  - **Validation:** Run validation pipeline

- [ ] **1.3.9** Create `tests/test_storage.py::test_load_all_tasks()`
  - Create multiple tasks, verify all loaded
  - **Validation:** `pytest tests/test_storage.py::test_load_all_tasks -v` passes

- [ ] **1.3.10** Add `TaskStorage.move_task()` method
  - Signature: `def move_task(self, task_id: int, to_milestone: str | None) -> Path`
  - Move task file to new location
  - Update task.milestone field
  - **Validation:** Run validation pipeline

- [ ] **1.3.11** Create `tests/test_storage.py::test_move_task()`
  - Test moving between milestones and to/from root
  - **Validation:** `pytest tests/test_storage.py::test_move_task -v` passes

- [ ] **1.3.12** Add `TaskStorage.get_milestones()` method
  - Signature: `def get_milestones(self) -> list[str]`
  - Return list of all milestone names (folder names in tasks/)
  - **Validation:** Run validation pipeline

- [ ] **1.3.13** Create `tests/test_storage.py::test_get_milestones()`
  - Create tasks in multiple milestones, verify list returned
  - **Validation:** `pytest tests/test_storage.py::test_get_milestones -v` passes

#### Task 1.4: Terminal Rendering ⏳
**Deliverable:** Rich formatting utilities

- [ ] **1.4.1** Create `quadro/renderer.py` with `Renderer` class
  - Import: `from rich.console import Console`, `from rich.table import Table`
  - Class: `Renderer` with `__init__(self, console: Console | None = None)`
  - **Validation:** Run validation pipeline

- [ ] **1.4.2** Add `Renderer.status_symbol()` static method
  - Signature: `@staticmethod def status_symbol(status: TaskStatus) -> str`
  - Return: `✓` for DONE, `▶` for PROGRESS, `○` for TODO
  - **Validation:** Run validation pipeline

- [ ] **1.4.3** Create `tests/test_renderer.py::test_status_symbol()`
  - Test all three status values
  - **Validation:** `pytest tests/test_renderer.py::test_status_symbol -v` passes

- [ ] **1.4.4** Add `Renderer.render_task_list()` method
  - Signature: `def render_task_list(self, tasks: list[Task], milestone_filter: str | None = None) -> None`
  - Create Rich Table with columns: Milestone, ID, Title, Status
  - Print summary line: "X tasks • Y done • Z in progress • W todo"
  - **Validation:** Run validation pipeline

- [ ] **1.4.5** Create `tests/test_renderer.py::test_render_task_list()`
  - Mock Console, verify table created with correct data
  - **Validation:** `pytest tests/test_renderer.py::test_render_task_list -v` passes

- [ ] **1.4.6** Add `Renderer.render_task_detail()` method
  - Signature: `def render_task_detail(self, task: Task) -> None`
  - Print formatted task details with separator lines
  - **Validation:** Run validation pipeline

- [ ] **1.4.7** Create `tests/test_renderer.py::test_render_task_detail()`
  - Mock Console, verify output format
  - **Validation:** `pytest tests/test_renderer.py::test_render_task_detail -v` passes

- [ ] **1.4.8** Add `Renderer.render_milestones()` method
  - Signature: `def render_milestones(self, tasks: list[Task]) -> None`
  - Create table with: Milestone, Tasks, Done, Progress bar, Completion %
  - **Validation:** Run validation pipeline

- [ ] **1.4.9** Create `tests/test_renderer.py::test_render_milestones()`
  - Test with tasks across multiple milestones
  - **Validation:** `pytest tests/test_renderer.py::test_render_milestones -v` passes

#### Task 1.5: CLI Commands ⏳
**Deliverable:** Working CLI with all commands

- [ ] **1.5.1** Create `quadro/cli.py` with Click setup
  - Import: `import click`, `from rich.console import Console`
  - Create `@click.group()` decorated `main()` function
  - Add `invoke_without_command=True` and default to `list` command
  - **Validation:** Run validation pipeline

- [ ] **1.5.2** Create `tests/test_cli.py` with Click testing setup
  - Import: `from click.testing import CliRunner`
  - Create fixture: `runner` returning `CliRunner()`
  - **Validation:** `pytest tests/test_cli.py -v` passes

- [ ] **1.5.3** Implement `quadro add` command in `quadro/cli.py`
  - Signature: `@main.command() def add(title: str, milestone: str | None) -> None`
  - Use `TaskStorage` to create and save task
  - Print success message with task ID and file path
  - **Validation:** Run validation pipeline

- [ ] **1.5.4** Create `tests/test_cli.py::test_add_command()`
  - Test adding task with and without milestone
  - Verify file created and output message correct
  - **Validation:** `pytest tests/test_cli.py::test_add_command -v` passes

- [ ] **1.5.5** Implement `quadro list` command in `quadro/cli.py`
  - Signature: `@main.command() def list(milestone: str | None) -> None`
  - Load tasks, filter if needed, render with `Renderer`
  - Handle empty task list with helpful message
  - **Validation:** Run validation pipeline

- [ ] **1.5.6** Create `tests/test_cli.py::test_list_command()`
  - Test with tasks, without tasks, with milestone filter
  - **Validation:** `pytest tests/test_cli.py::test_list_command -v` passes

- [ ] **1.5.7** Implement `quadro start` command in `quadro/cli.py`
  - Signature: `@main.command() def start(task_id: int) -> None`
  - Load task, update status to PROGRESS, save
  - Handle task not found, already in progress, already done
  - **Validation:** Run validation pipeline

- [ ] **1.5.8** Create `tests/test_cli.py::test_start_command()`
  - Test valid case, already started, already done, not found
  - **Validation:** `pytest tests/test_cli.py::test_start_command -v` passes

- [ ] **1.5.9** Implement `quadro done` command in `quadro/cli.py`
  - Signature: `@main.command() def done(task_id: int) -> None`
  - Load task, update status to DONE, set completed timestamp, save
  - Handle task not found, already done
  - **Validation:** Run validation pipeline

- [ ] **1.5.10** Create `tests/test_cli.py::test_done_command()`
  - Test valid case, already done, not found
  - Verify completed timestamp set
  - **Validation:** `pytest tests/test_cli.py::test_done_command -v` passes

- [ ] **1.5.11** Implement `quadro show` command in `quadro/cli.py`
  - Signature: `@main.command() def show(task_id: int) -> None`
  - Load task, render with `Renderer.render_task_detail()`
  - Handle task not found
  - **Validation:** Run validation pipeline

- [ ] **1.5.12** Create `tests/test_cli.py::test_show_command()`
  - Test valid case, not found
  - **Validation:** `pytest tests/test_cli.py::test_show_command -v` passes

- [ ] **1.5.13** Implement `quadro milestones` command in `quadro/cli.py`
  - Signature: `@main.command() def milestones() -> None`
  - Load all tasks, render with `Renderer.render_milestones()`
  - Handle no milestones case
  - **Validation:** Run validation pipeline

- [ ] **1.5.14** Create `tests/test_cli.py::test_milestones_command()`
  - Test with milestones, without milestones
  - **Validation:** `pytest tests/test_cli.py::test_milestones_command -v` passes

- [ ] **1.5.15** Implement `quadro move` command in `quadro/cli.py`
  - Signature: `@main.command() def move(task_id: int, to: str) -> None`
  - Use `TaskStorage.move_task()`
  - Handle "root" as special value for `to`
  - Print old path → new path
  - **Validation:** Run validation pipeline

- [ ] **1.5.16** Create `tests/test_cli.py::test_move_command()`
  - Test moving to milestone, to root, task not found
  - **Validation:** `pytest tests/test_cli.py::test_move_command -v` passes

- [ ] **1.5.17** Implement `quadro edit` command in `quadro/cli.py`
  - Signature: `@main.command() def edit(task_id: int) -> None`
  - Find task file, open in `$EDITOR` (use `click.edit()`)
  - Reload and re-save after editing
  - **Validation:** Run validation pipeline

- [ ] **1.5.18** Create `tests/test_cli.py::test_edit_command()`
  - Mock `click.edit()`, verify called with correct file content
  - **Validation:** `pytest tests/test_cli.py::test_edit_command -v` passes

#### Task 1.6: Integration & Polish ⏳
**Deliverable:** Fully working CLI ready for use

- [ ] **1.6.1** Create `tests/test_integration.py` for end-to-end tests
  - Test: Create task → start → done → show (full workflow)
  - Test: Create multiple tasks → list → filter by milestone
  - Test: Create task → move → verify new location
  - **Validation:** `pytest tests/test_integration.py -v` passes

- [ ] **1.6.2** Add comprehensive error handling in `quadro/cli.py`
  - Wrap commands in try/except for common errors
  - Pretty print errors with Rich
  - Exit with appropriate codes
  - **Validation:** Run validation pipeline

- [ ] **1.6.3** Create `README.md` with installation and usage
  - Badges: CI status, coverage, Python version
  - Installation: `uv pip install quadro` (or `pip install quadro`)
  - Development setup: `uv sync && uv run pre-commit install`
  - Quick start examples
  - Command reference
  - **Validation:** Manual review

- [ ] **1.6.4** Final validation
  - Run full test suite: `uv run pytest tests/ -v --cov=quadro`
  - Run linting: `uv run ruff check quadro/`
  - Run security: `uv run bandit -c pyproject.toml -r quadro/`
  - Run type checking: `uv run mypy quadro/`
  - Run pre-commit: `uv run pre-commit run --all-files`
  - Manual testing: Install with `uv pip install -e .` and use all commands
  - Verify CI passes on GitHub Actions
  - **Validation:** All checks pass ✓

### Phase 2: Enhancements 📋

**Goal:** Polish UX and add quality-of-life features

- [ ] Better error messages and validation
- [ ] Add `quadro delete <id>` command
- [ ] Add `quadro undo <id>` (revert status: done→progress→todo)
- [ ] Color themes for different statuses
- [ ] Task filtering (by status: `--todo`, `--done`, `--progress`)
- [ ] Search functionality (`quadro search <query>`)

### Phase 3: Advanced Features 🚀

**Goal:** Make Quadro more powerful and flexible

- [ ] Task metadata
  - [ ] Tags support (`tags: [bug, urgent]`)
  - [ ] Priority levels
  - [ ] Due dates
- [ ] Advanced organization
  - [ ] Subtasks support
  - [ ] Task dependencies
  - [ ] Archive completed tasks
- [ ] Configuration
  - [ ] `.quadrorc` config file
  - [ ] Custom task templates
  - [ ] Configurable task ID format
- [ ] Export/Import
  - [ ] Export to JSON/CSV
  - [ ] GitHub Issues integration

### Phase 4: Distribution 📦

- [ ] Package for PyPI
- [ ] Documentation website
- [ ] Installation guide
- [ ] Usage examples and tutorials
- [ ] Contribution guidelines

---

## Design Principles

1. **Zero configuration** - Works immediately, no setup required
2. **Markdown-first** - Tasks are readable markdown files
3. **Beautiful output** - Rich tables, colors, Unicode symbols
4. **Fast feedback** - Clear success/error messages
5. **Intuitive** - Commands match git/npm patterns
6. **Flexible** - Direct file editing or CLI commands

---

## Status Indicators

- ✓ Done
- ▶ In Progress
- ○ Todo
- ⏳ Planned

---

## Current Status

**Phase:** 1 - MVP
**Progress:** Just started! 🎉
**Next:** Setup project structure and dependencies
