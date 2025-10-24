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

## Git & Commit Conventions

**Commit Message Format:**
```
<type>: <subject>

[optional issue reference]

<body>
```

**IMPORTANT:** Do NOT include Claude as a co-author in commit messages. Do NOT add:
- `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
- `Co-Authored-By: Claude <noreply@anthropic.com>`
- Any other Claude attribution lines

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Issue References:**
Always reference GitHub issues in commit messages to create automatic links and tracking:

- **Closing issues**: Use `Fixes #123`, `Closes #123`, or `Resolves #123` in the commit body to automatically close the issue when merged to main
  ```
  fix: remove duplicate installation confirmation prompt

  Fixes #1

  The inskit install command was prompting users twice...
  ```

- **Referencing issues**: Use `Refs #123` or `See #123` to reference related issues without closing them
  ```
  test: add unit tests for duplicate confirmation fix

  Refs #1

  Add comprehensive unit tests...
  ```

**Examples:**
```bash
# Bug fix that closes an issue
git commit -m "fix: handle empty library gracefully

Fixes #42

Previously the CLI would crash when the library was empty.
This commit adds proper error handling..."

# Test addition referencing an issue
git commit -m "test: add tests for library edge cases

Refs #42

Adds tests to verify empty library handling..."

# Feature with multiple issue references
git commit -m "feat: add batch installation support

Closes #15, Refs #12

Allows installing multiple instructions in one command..."
```

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

## Release Workflow

**IMPORTANT:** When the user asks to "create a new release" or "make a release", follow this complete workflow.

This project uses **GitHub Actions with PyPI Trusted Publishing** for automated releases. Publishing to PyPI happens automatically when you create a GitHub release.

### PyPI Trusted Publishing Setup

**One-time setup** (if not already configured):

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - **PyPI Project Name**: `instructionkit`
   - **Owner**: `troylar`
   - **Repository**: `instructionkit`
   - **Workflow name**: `publish.yml`
   - **Environment**: (leave empty)
3. Save the trusted publisher

This allows GitHub Actions to publish without needing API tokens or passwords.

### Pre-Release Checklist

**IMPORTANT:** Before creating a release, you **must** run `invoke release-check` locally to ensure everything is working. This prevents CI failures and failed releases.

1. **Ensure you're on the main branch** (or merge feature branch PR first)
2. **Working directory must be clean** (no uncommitted changes)
3. **All checks must pass locally**: `invoke release-check`
4. **CI/CD pipeline must be green** on GitHub Actions (if PR was merged)

### Release Steps

Follow these steps in order when creating a new release:

#### 1. Check Current Branch and Status
```bash
# Check current branch
git branch --show-current

# If on feature branch with open PR, check PR status
gh pr status

# Check for uncommitted changes
git status
```

**Action:** If on a feature branch with an open PR:
- Ensure all CI checks are passing
- Merge the PR to main
- Then pull main locally

#### 2. Switch to Main and Pull Latest
```bash
git checkout main
git pull origin main
```

#### 3. Run Pre-Release Checks (REQUIRED)
```bash
# This runs clean, quality, and test
invoke release-check
```

**IMPORTANT:** This step is **required** before proceeding with the release. It verifies locally that:
- All tests pass
- Code quality checks pass (lint, format, typecheck)
- Build artifacts are clean

**Action:** Fix any failures before proceeding. Do NOT create a release if this command fails.

#### 4. Determine Version Bump

Version is in `pyproject.toml`:
```toml
[project]
version = "0.1.1"
```

**Semantic Versioning:**
- **Patch** (0.1.1 → 0.1.2): Bug fixes, minor changes
- **Minor** (0.1.1 → 0.2.0): New features, backwards compatible
- **Major** (0.1.1 → 1.0.0): Breaking changes

**Action:** Ask the user which version bump to apply if not specified.

#### 5. Update Version in pyproject.toml

Edit the version in `pyproject.toml`:
```toml
[project]
version = "0.2.0"  # New version
```

#### 6. Update CHANGELOG.md

Add a new version section at the top of CHANGELOG.md with changes since last release:
```markdown
## [0.2.0] - 2025-10-24

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description
```

**Tip:** Review commits since last release:
```bash
git log v0.1.1..HEAD --oneline
```

#### 7. Commit Version Bump

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"
```

**IMPORTANT:** Do NOT include Claude co-author attribution.

#### 8. Create and Push Git Tag

```bash
# Create annotated tag
git tag -a v0.2.0 -m "Release version 0.2.0"

# Push commits and tags
git push origin main
git push origin v0.2.0
```

#### 9. Create GitHub Release (Triggers Automated Publishing)

```bash
# Create release from tag
gh release create v0.2.0 \
  --title "v0.2.0" \
  --notes "$(awk '/## \[0.2.0\]/,/## \[/' CHANGELOG.md | head -n -1)"
```

**Alternative:** Create release manually on GitHub:
1. Go to https://github.com/troylar/instructionkit/releases/new
2. Click "Choose a tag" and select `v0.2.0`
3. Title: `v0.2.0`
4. Copy the relevant section from CHANGELOG.md into the description
5. Click "Publish release"

**What happens next:** The `.github/workflows/publish.yml` workflow will automatically:
1. Run quality checks and tests
2. Build the package
3. Publish to PyPI using trusted publishing

#### 10. Monitor the Publish Workflow

```bash
# Watch workflow progress
gh run watch

# Or view in browser
gh run list --workflow=publish.yml
```

You can also monitor at: https://github.com/troylar/instructionkit/actions

### Post-Release Verification

Wait for the GitHub Actions workflow to complete (usually 2-5 minutes), then:

```bash
# Verify package on PyPI
pip install --upgrade instructionkit

# Check installed version
inskit --version

# Verify GitHub release
gh release view v0.2.0

# Check PyPI page
open https://pypi.org/project/instructionkit/
```

### Testing on TestPyPI (Optional)

To test the release process without publishing to production PyPI:

```bash
# Manually trigger workflow with TestPyPI option
gh workflow run publish.yml -f repository=testpypi

# Monitor the test run
gh run watch
```

Then verify on TestPyPI: https://test.pypi.org/project/instructionkit/

### Rollback (If Needed)

If issues are discovered after release:

1. **Yank release from PyPI** (marks as unavailable, doesn't delete):
   ```bash
   # Install twine if needed
   pip install twine

   # Yank the version
   twine upload --repository pypi --yank <version>
   ```

2. **Delete GitHub release**:
   ```bash
   gh release delete v0.2.0 --yes
   ```

3. **Optionally delete the tag**:
   ```bash
   git tag -d v0.2.0
   git push origin :refs/tags/v0.2.0
   ```

4. **Fix issues and create new patch release** (e.g., 0.2.1)

### Quick Reference

For a standard release from main branch:

```bash
# 1. Ensure clean state
git checkout main && git pull

# 2. REQUIRED: Run checks locally (DO NOT SKIP!)
invoke release-check

# 3. Update version in pyproject.toml and CHANGELOG.md

# 4. Commit and tag
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to X.Y.Z"
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin main && git push origin vX.Y.Z

# 5. Create GitHub release (triggers automated publish)
gh release create vX.Y.Z --title "vX.Y.Z" \
  --notes "$(awk '/## \[X.Y.Z\]/,/## \[/' CHANGELOG.md | head -n -1)"

# 6. Monitor workflow and verify
gh run watch
```

The GitHub Actions workflow (`.github/workflows/publish.yml`) handles building and publishing automatically.
