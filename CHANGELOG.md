# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
