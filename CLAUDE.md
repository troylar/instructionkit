# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**InstructionKit** is a CLI tool for managing AI coding assistant instructions. It allows users to download instruction repositories to a local library, browse them with an interactive TUI, and install them to AI tools (Cursor, Claude Code, Windsurf, GitHub Copilot) at the project level.

**CLI entry point:** `inskit` (installed via `pip install instructionkit`)

## Architecture

### Core Concepts

1. **Library System**: Instructions are downloaded from Git repos or local folders to `~/.instructionkit/library/` organized by namespace
2. **Project-Level Installation**: All installations are project-specific, stored in tool-specific directories (`.cursor/rules/`, `.claude/rules/`, etc.)
3. **Installation Tracking**: Tracked in `<project-root>/.instructionkit/installations.json` for each project
4. **Interactive TUI**: Terminal UI for browsing and selecting instructions from the library

### Package Structure

```
instructionkit/
├── ai_tools/          # AI tool integrations and detection
│   ├── base.py       # Abstract AITool base class
│   ├── claude.py     # Claude Code (.claude/rules/*.md)
│   ├── cursor.py     # Cursor (.cursor/rules/*.mdc)
│   ├── winsurf.py    # Windsurf (.windsurf/rules/*.md)
│   ├── copilot.py    # GitHub Copilot (.github/instructions/*.md)
│   └── detector.py   # Tool detection logic
├── cli/               # Typer CLI commands
│   ├── main.py       # CLI app definition
│   ├── download.py   # Download repos to library
│   ├── install.py    # Legacy install command
│   ├── install_new.py # New install with TUI
│   ├── list.py       # List library/installed/available
│   ├── update.py     # Update library repos
│   ├── delete.py     # Delete from library
│   ├── uninstall.py  # Uninstall from projects
│   └── tools.py      # List detected AI tools
├── core/              # Core business logic
│   ├── models.py     # Data models (Instruction, Repository, etc.)
│   ├── repository.py # Parse instructionkit.yaml
│   ├── git_operations.py # Git clone/pull operations
│   ├── checksum.py   # File integrity checking
│   └── conflict_resolution.py # Handle file conflicts
├── storage/           # Data persistence
│   ├── library.py    # LibraryManager for ~/.instructionkit/library/
│   └── tracker.py    # InstallationTracker for installations.json
├── tui/               # Terminal UI
│   └── installer.py  # Textual-based interactive browser
└── utils/             # Utilities
    ├── project.py    # Project root detection
    └── logging.py    # Logging configuration
```

### Key Data Models

From `instructionkit/core/models.py`:

- **Instruction**: Single instruction file with name, description, content, file_path, tags, checksum
- **InstructionBundle**: Group of related instructions
- **Repository**: Instruction repository with instructions and bundles
- **InstallationRecord**: Tracks installed instruction with ai_tool, source_repo, installed_path, scope
- **LibraryInstruction**: Instruction in library (downloaded but not installed)
- **LibraryRepository**: Downloaded repository in library

### AI Tool Integration

Each AI tool integration (in `ai_tools/`) inherits from `AITool` base class:
- `name`: Tool identifier
- `install_path`: Where to install files (e.g., `.cursor/rules/`)
- `file_extension`: File extension (e.g., `.mdc` for Cursor, `.md` for others)
- `detect()`: Check if tool is installed
- `get_install_path(scope, project_root)`: Get installation directory
- `install(instruction, scope, project_root, conflict_strategy)`: Install instruction file

## Development Commands

### Setup
```bash
# Install in editable mode with dev dependencies
pip install -e .[dev]

# Or use invoke
invoke dev-setup
```

### Testing
```bash
# Run all tests (preferred)
invoke test

# Run with coverage
invoke test --coverage

# Run specific test types
invoke test-unit         # Unit tests only
invoke test-integration  # Integration tests only

# Manual pytest
pytest                        # All tests
pytest tests/unit/            # Unit tests
pytest tests/integration/     # Integration tests
pytest -k "test_name"         # Specific test pattern
```

### Code Quality
```bash
# Run all checks (lint, format, typecheck)
invoke quality

# Auto-fix issues
invoke quality --fix

# Individual checks
invoke lint              # Ruff linting
invoke lint --fix        # Auto-fix lint issues
invoke format            # Black formatting
invoke format --check    # Check without changes
invoke typecheck         # MyPy type checking
```

### Build & Install
```bash
invoke clean             # Clean build artifacts
invoke build             # Build package
invoke install           # Install package
invoke install --dev     # Install with dev dependencies
```

### Release
```bash
# Pre-release checks (runs clean, quality, test)
invoke release-check

# Build and publish to PyPI
invoke build
invoke publish           # Publish to PyPI
invoke publish --repository testpypi  # Test PyPI first
```

### Utilities
```bash
invoke count             # Count lines of code
invoke version           # Show current version
invoke tree              # Show project structure
invoke security-check    # Run security scans
```

## Testing Structure

```
tests/
├── conftest.py              # Shared fixtures (temp_dir, mock repos)
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_models.py      # Model validation
│   ├── test_checksum.py    # Checksum utilities
│   └── ...
└── integration/             # Integration tests (file I/O, Git)
    ├── test_library.py     # Library management
    ├── test_repository.py  # Repository parsing
    └── test_tracker.py     # Installation tracking
```

**Testing conventions:**
- Use fixtures from `conftest.py` (especially `temp_dir` for file operations)
- Integration tests may use actual Git operations and file I/O
- All tests should clean up after themselves
- Use `pytest -v` for verbose output, `pytest --cov` for coverage

## Code Style

- **Formatter**: Black (line length: 120)
- **Linter**: Ruff (select: E, F, I, N, W)
- **Type Checker**: MyPy (strict type hints required)
- **Python Version**: 3.10+ (using modern type hints like `list[str]`, not `List[str]`)

**Key conventions:**
- All functions must have type hints
- Use dataclasses for data models
- Use Enum for constants (AIToolType, ConflictResolution, InstallationScope)
- Docstrings for all public functions/classes (Google style)
- Line length: 120 characters

## Important Implementation Details

### Project Root Detection
The `utils/project.py` module detects project root by looking for markers like `.git/`, `pyproject.toml`, `package.json`, etc. This enables running `inskit` from any subdirectory within a project.

### Installation Workflow
1. **Download**: Clone/copy repo to `~/.instructionkit/library/<namespace>/`
2. **Browse**: TUI reads library, displays instructions
3. **Install**: Copy instruction file to project's tool-specific directory
4. **Track**: Record in `<project-root>/.instructionkit/installations.json`

### Conflict Resolution
When installing an instruction that already exists:
- **SKIP**: Don't install, leave existing
- **RENAME**: Install with suffix (e.g., `instruction-1.md`)
- **OVERWRITE**: Replace existing file

### Repository Format
Instruction repositories must have `instructionkit.yaml`:
```yaml
name: My Instructions
description: Description
version: 1.0.0

instructions:
  - name: my-instruction
    description: What it does
    file: instructions/my-instruction.md
    tags: [tag1, tag2]

bundles:
  - name: my-bundle
    description: Bundle description
    instructions: [instruction1, instruction2]
    tags: [tag]
```

## CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml`:
- Runs on Python 3.10, 3.11, 3.12, 3.13
- Matrix testing on ubuntu-latest, macos-latest, windows-latest
- Steps: lint, format check, typecheck, tests with coverage
- Coverage uploaded to Codecov

**Local pre-push hook** (`.githooks/pre-push`):
```bash
# Enable with:
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

## Common Tasks

### Adding a New AI Tool
1. Create `instructionkit/ai_tools/newtool.py` inheriting from `AITool`
2. Implement `detect()`, `get_install_path()`, and `install()` methods
3. Add to `AIToolType` enum in `models.py`
4. Register in `detector.py`
5. Add tests in `tests/unit/test_ai_tools.py`

### Adding a New CLI Command
1. Create command file in `instructionkit/cli/`
2. Define Typer command with `@app.command()`
3. Register in `cli/main.py`
4. Add tests in `tests/unit/test_cli.py`
5. Update README.md with usage examples

### Modifying Data Models
1. Update dataclass in `core/models.py`
2. Update `to_dict()` and `from_dict()` methods
3. Consider backwards compatibility for existing installations
4. Add tests in `tests/unit/test_models.py`

## Dependencies

**Core:**
- `typer[all]` - CLI framework
- `rich` - Terminal formatting
- `pyyaml` - YAML parsing
- `textual` - TUI framework

**Dev:**
- `pytest`, `pytest-cov` - Testing
- `black` - Formatting
- `ruff` - Linting
- `mypy` - Type checking
- `invoke` - Task automation

## Documentation Standards

Follow the `.cursor/rules/documentation-practices.mdc` guide:
- README-first approach
- Comprehensive docstrings (Google style)
- Explain WHY in comments, not WHAT
- Keep CHANGELOG.md updated
- Architecture decision records (ADRs) for major decisions

## Debugging

```bash
# Enable debug logging
LOGLEVEL=DEBUG inskit install

# Run specific test with output
pytest tests/unit/test_models.py -s -vv

# Use breakpoints
import pdb; pdb.set_trace()
# or
breakpoint()
```

## Version Management

Version is in `pyproject.toml`:
```toml
[project]
version = "0.1.1"
```

Update version, CHANGELOG, then:
```bash
git tag v0.1.1
git push --tags
invoke build
invoke publish
```
