# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking Changes
- **GitHub Copilot file extension**: Instructions now use `.instructions.md` extension (was `.md`) (#15)
  - Required by GitHub Copilot's [official specification](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
  - Previous installations with `.md` extension will not be recognized by Copilot
  - **Action required** if you have existing Copilot instructions:
    ```bash
    inskit uninstall <instruction-name> --tool copilot
    inskit install <instruction-name>
    ```
  - Affects: GitHub Copilot only (Cursor, Claude Code, Windsurf unchanged)

### Added
- Git-based repository versioning support - download and manage multiple versions of instruction repositories
  - `inskit download --ref <tag|branch|commit>` to download specific Git references
  - Support for tags (e.g., `v1.0.0`), branches (e.g., `main`), and commit hashes
  - Multiple versions of the same repository can coexist in the library
  - Version information tracked in installation records (`source_ref` and `source_ref_type`)
  - Automatic update behavior: branch-based installs auto-update, tag/commit-based installs remain pinned
  - `inskit update` intelligently updates only mutable references (branches)
  - Version display in TUI installer and `inskit list` commands
- **Upgrade detection and prompts** - when installing a newer version of an existing instruction:
  - Automatically detects version changes (e.g., v1.0.0 → v2.0.0)
  - Displays side-by-side version comparison with old and new versions
  - Prompts for user confirmation before upgrading
  - Works across all AI tools (Cursor, Claude Code, Copilot, Windsurf)
- **Name collision handling** - when installing instructions with duplicate names from different repositories:
  - Detects when instruction name already exists from a different repository
  - Displays detailed information about existing and new installations
  - Allows users to provide custom filename to avoid conflicts
  - Option to skip installation if collision cannot be resolved
  - `find_instructions_by_name()` method in `InstallationTracker` for collision detection
- New `RefType` enum for tracking Git reference types (tag, branch, commit)
- `GitOperations` class with functions for:
  - `detect_ref_type()` - automatically determine if a reference is a tag, branch, or commit
  - `validate_remote_ref()` - verify Git references exist on remote before cloning
  - `clone_at_ref()` - clone repository at a specific Git reference
  - `check_for_updates()` - check if updates are available for branch-based repos
  - `pull_repository_updates()` - pull latest changes with conflict detection
- Versioned namespace generation in `LibraryManager`:
  - `get_versioned_namespace()` - creates unique namespaces like `repo@v1.0.0`
  - `list_repository_versions()` - lists all downloaded versions of a repository
- Enhanced update command with progress bars and detailed status reporting
- Comprehensive unit tests for upgrade detection and collision handling (8 new tests)

### Changed
- `InstallationRecord` now includes `source_ref` and `source_ref_type` fields for version tracking
- Library organization now supports version-specific namespaces (e.g., `github_com_user_repo@v1.0.0`)
- Update workflow now filters installations by ref mutability (only updates branches)
- Installation workflow now includes upgrade and collision checks before file operations

## [0.2.0] - 2025-10-24

### Changed
- Project-scoped installations now use relative paths in `installations.json` for version control compatibility (#8, #9)
- Removed `project_root` field from `InstallationRecord` model
- Installation tracking files are now safe to commit to version control across different machines

### Added
- Comprehensive release workflow documentation in CLAUDE.md with GitHub Actions automation
- Unit tests for relative path functionality in installation tracking
- Automatic migration from absolute to relative paths on save

### Fixed
- PyPI trusted publishing workflow configuration

## [0.1.2] - 2025-10-24

### Fixed
- Fixed duplicate installation confirmation prompt in `inskit install` command (#1)
- Improved path assertions for cross-platform compatibility (Windows support)

### Changed
- Added CODECOV_TOKEN to codecov upload step in CI workflow

### Added
- Comprehensive unit tests for installation confirmation workflow
- Git and commit message conventions documentation in CLAUDE.md

## [0.1.1] - 2025-10-21

### Added
- Initial release with core functionality
- CLI commands: download, install, list, update, delete, uninstall, tools
- Support for Claude Code, Cursor, Windsurf, and GitHub Copilot
- Interactive TUI for browsing and installing instructions
- Library management system for instruction repositories
- Installation tracking and conflict resolution
