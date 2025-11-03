# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-03

### Changed
- Make MCP dependencies required and improve install docs by @morais90
- Add commitizen to pre-commit hooks by @morais90

### Documentation
- Update CHANGELOG.md [skip ci] by @github-actions[bot]
- Update CHANGELOG.md [skip ci] by @github-actions[bot]
- Update CHANGELOG.md [skip ci] by @github-actions[bot]
- Update MCP setup to use correct PyPI package name by @morais90
- Update CHANGELOG.md [skip ci] by @github-actions[bot]
- Add PyPI badge to README by @morais90

### Fixed
- Regenerate entire changelog to prevent duplicates by @morais90
- Specify Python 3.12 for mypy pre-commit hook by @morais90

## [1.0.0] - 2025-11-03

### Added
- Add automatic changelog update workflow by @morais90
- Add automated release workflow by @morais90
- Add brand logos and improve visual identity by @morais90
- Add MkDocs site with interactive landing page by @morais90
- Add task resources for direct content access by @morais90
- Add list_milestones tool by @morais90
- Add delete_task tool by @morais90
- Add move_task tool by @morais90
- Add start_task and complete_task tools by @morais90
- Add create_task tool by @morais90
- Implement get_task tool by @morais90
- Implement list_tasks tool with filtering by @morais90
- Add FastMCP server integration by @morais90
- Add description option to task creation by @morais90
- Add status filtering flags by @morais90
- Add filter_by_status method by @morais90
- Add delete command with confirmation by @morais90
- Add delete_task method by @morais90
- Add comprehensive error handling to all commands by @morais90
- Add edit command to modify tasks in editor by @morais90
- Add move command to relocate tasks between milestones by @morais90
- Add milestones command to display progress overview by @morais90
- Add show command to display task details by @morais90
- Add done command to mark tasks as completed by @morais90
- Add start command to mark tasks in progress by @morais90
- Implement list command by @morais90
- Implement add command by @morais90
- Add Click CLI framework setup by @morais90
- Add render_milestones method by @morais90
- Add render_task_detail method by @morais90
- Add render_task_list method by @morais90
- Add status symbol mapping by @morais90
- Add get_milestones method by @morais90
- Add move_task method by @morais90
- Add load_all_tasks method by @morais90
- Add load_task method by @morais90
- Add save_task method by @morais90
- Add TaskStorage with ID generation by @morais90
- Add Task.to_markdown serialization by @morais90
- Add Task.from_markdown parser by @morais90
- Add Task dataclass with tests by @morais90
- Add TaskStatus enum by @morais90

### Changed
- Set initial git-cliff version to 1.0.0 by @morais90
- Bump version to 1.0.0 and regenerate changelog by @morais90
- Add git-cliff configuration by @morais90
- Bump version to 0.1.0 by @morais90
- Rename PyPI package to qdr by @morais90
- Bump version to 0.1.1b0 by @morais90
- Make MCP dependencies optional by @morais90
- Add PyPI metadata to pyproject.toml by @morais90
- Migrate to dependency-groups format by @morais90
- Remove completed tasks from milestones by @morais90
- Add feature request issue template by @morais90
- Add bug report issue template by @morais90
- Add MIT License to the project by @morais90
- Remove MCP server integration planning tasks by @morais90
- Consolidate commands module into single file by @morais90
- Refine task checklists based on list_tasks pattern by @morais90
- Migrate roadmap to quadro task management by @morais90
- Refactor assertions to use dedent by @morais90
- Extract edit command for MCP integration by @morais90
- Extract move command for MCP integration by @morais90
- Extract milestones command for MCP integration by @morais90
- Extract show command for MCP integration by @morais90
- Extract done command for MCP integration by @morais90
- Extract start command with custom exceptions by @morais90
- Extract list command logic for MCP integration by @morais90
- Extract add command logic for MCP integration by @morais90
- Stop tracking roadmap.md by @morais90
- Add pre-commit hooks configuration by @morais90
- Add pytest and coverage configuration by @morais90
- Add strict mypy type checking by @morais90
- Add bandit security scanning by @morais90
- Configure ruff linting and formatting by @morais90
- Add .gitignore for Python project by @morais90
- Initialize Python project structure by @morais90

### Documentation
- Update CHANGELOG.md [skip ci] by @github-actions[bot]
- Update CHANGELOG.md [skip ci] by @github-actions[bot]
- Regenerate CHANGELOG.md without bad tag references by @morais90
- Create initial CHANGELOG.md by @morais90
- Update installation guide and repository URLs by @morais90
- Refocus messaging on planning with AI assistants by @morais90
- Update reporting email for community incidents by @morais90
- Add README with project overview and examples by @morais90
- Reorganize documentation planning into new milestone by @morais90
- Add CLAUDE.md for AI assistant guidance by @morais90
- Add comprehensive docstrings to commands by @morais90

### Fixed
- Change release commit message and skip in changelog by @morais90
- Remove conflicting OUTPUT env var in changelog workflow by @morais90
- Download artifacts to dist directory for PyPI publish by @morais90
- Add skip ci to release commit by @morais90
- Prevent double v prefix in release tag by @morais90
- Use absolute URL for logo in README by @morais90

### New Contributors
* @github-actions[bot] made their first contribution
* @morais90 made their first contribution

[1.0.1]: https://github.com/spec-driven/quadro/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/spec-driven/quadro/compare/...v1.0.0

<!-- generated by git-cliff -->
