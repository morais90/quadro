# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quadro is a command-line task management tool that stores tasks as markdown files with frontmatter metadata. Tasks are organized in a file-based system where each task is a numbered markdown file (e.g., `1.md`, `2.md`) stored in a `tasks/` directory, optionally grouped into milestone subdirectories.

## Commands

### Development Setup

```bash
# Install dependencies (uses uv package manager)
uv sync

# Run the CLI locally
uv run quadro [command]
```

### Testing

```bash
# Run all tests with coverage
uv run pytest

# Run a single test file
uv run pytest tests/test_models.py

# Run a specific test
uv run pytest tests/test_models.py::test_task_creation

# Run tests with specific markers
uv run pytest -m slow
uv run pytest -m integration

# Coverage is configured to require 80% minimum (see pyproject.toml)
# Coverage reports are generated in htmlcov/ directory
```

### Code Quality

```bash
# Lint and auto-fix with Ruff
uv run ruff check --fix

# Format code
uv run ruff format

# Type checking with mypy (strict mode enabled)
uv run mypy quadro

# Security scanning with bandit
uv run bandit -r quadro

# Run all pre-commit hooks
pre-commit run --all-files
```

## Architecture

### Core Components

**models.py** - Defines the Task dataclass and TaskStatus enum. Tasks are bidirectionally converted between Python objects and markdown format with YAML frontmatter. The `Task.from_markdown()` and `Task.to_markdown()` methods handle serialization.

**storage.py** - TaskStorage class manages file I/O operations. Tasks are stored in `tasks/` directory (or milestone subdirectories like `tasks/MVP/`). Task IDs are derived from filenames using regex pattern `(\d+).md`. The storage layer handles task CRUD operations and milestone organization.

**cli.py** - Click-based command-line interface. Uses a decorator pattern (`@handle_exceptions`) to provide consistent error handling across all commands. The CLI defaults to `list` when invoked without arguments.

**renderer.py** - Rich-based terminal output formatting. Handles tables, progress bars, and markdown rendering for task display.

**commands/** - Each command is in its own module (add.py, list.py, start.py, done.py, etc.). Commands implement business logic and interact with TaskStorage. They return data that the CLI layer formats and displays.

**exceptions.py** - Custom exception hierarchy for task-related errors.

### Data Flow

1. User invokes CLI command via Click
2. CLI command calls business logic function from commands/ module
3. Command function uses TaskStorage to read/write task files
4. Task objects are serialized/deserialized via models.py
5. Results are formatted by Renderer and displayed via Rich Console

### File Structure

Tasks are stored as markdown files with this structure:

```markdown
---
status: todo
created: 2024-10-06T12:00:00+00:00
milestone: MVP
completed: null
---

# Task Title

Task description and details go here.
```

### Key Design Patterns

- **File-based storage**: Each task is a separate markdown file, making tasks git-friendly and human-readable
- **ID assignment**: Task IDs are auto-incrementing integers based on the highest existing ID across all files
- **Milestone organization**: Tasks can be grouped into milestones via subdirectories (e.g., `tasks/MVP/1.md`)
- **Status transitions**: TODO → PROGRESS → DONE. The `completed` timestamp is auto-set when status changes to DONE
- **Strict typing**: mypy strict mode is enabled with extensive type checking rules

### Testing Strategy

- Tests mirror the source structure (tests/test_models.py matches quadro/models.py)
- Command tests use Click's CliRunner for integration testing
- pytest fixtures are used for creating temporary task directories
- freezegun is used for datetime testing
- Test files can use S101 (assert), PLR2004 (magic values), and SLF001 (private access) freely

### Code Style

- Line length: 100 characters
- Ruff with "ALL" rules enabled, except D (docstrings), COM812, ISC001
- Imports: force-single-line with isort
- Double quotes for strings
- Python 3.12+ required
- Type hints required for all function definitions (disallow_untyped_defs)

### Important Constraints

- The `tasks/` directory is the default storage location but can be overridden via TaskStorage(base_path=...)
- Task IDs are globally unique across all milestones
- Moving tasks between milestones involves filesystem operations (create new file, delete old file)
- The edit command uses the system's $EDITOR environment variable
- All timestamps use UTC timezone
