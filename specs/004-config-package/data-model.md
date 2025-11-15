# Data Model: Configuration Package System

**Feature**: 004-config-package
**Date**: 2025-11-14
**Status**: Complete

## Overview

This document defines the data structures for the package system, extending the existing AI Config Kit data model with package-related entities.

---

## Core Entities

### Package

A bundle of related configuration components with metadata.

**Fields**:
- `name: str` - Package identifier (lowercase, hyphenated)
- `version: str` - Semantic version (major.minor.patch)
- `description: str` - Human-readable description
- `author: str` - Package author/maintainer
- `license: str` - License identifier (e.g., MIT, Apache-2.0)
- `namespace: str` - Repository namespace (e.g., owner/repo)
- `components: PackageComponents` - Included components
- `created_at: datetime` - Package creation timestamp
- `updated_at: datetime` - Last update timestamp

**Validation Rules**:
- Name must match pattern: `^[a-z0-9-]+$`
- Version must be valid semver (validated by `packaging.version`)
- Namespace must match pattern: `^[a-z0-9-]+/[a-z0-9-]+$`
- At least one component must be included

**Relationships**:
- Contains multiple `PackageComponent` instances
- Stored in `PackageRepository`
- Tracked by `PackageInstallationRecord` when installed

**State Transitions**:
None - packages are immutable once versioned (new version = new package)

---

### PackageComponents

Container for all component types in a package.

**Fields**:
- `instructions: list[InstructionComponent]` - Instruction files
- `mcp_servers: list[MCPServerComponent]` - MCP server configs
- `hooks: list[HookComponent]` - IDE lifecycle hooks
- `commands: list[CommandComponent]` - Slash commands/scripts
- `resources: list[ResourceComponent]` - Arbitrary files

**Validation Rules**:
- At least one component list must be non-empty
- Component names must be unique within each type
- All component files must exist in repository

**Derived Properties**:
- `total_count: int` - Sum of all component counts
- `component_types: list[str]` - List of component types present

---

### InstructionComponent

Reference to an instruction file in the package.

**Fields**:
- `name: str` - Instruction identifier
- `file: str` - Relative path to instruction file
- `description: str` - What the instruction does
- `tags: list[str]` - Searchable tags
- `ide_support: Optional[list[str]]` - Specific IDE support (if restricted)

**Validation Rules**:
- File must exist in package repository
- File must be markdown (.md)
- If `ide_support` specified, must be valid IDE names

**Translation Rules**:
- `.md` file → `.mdc` for Cursor
- `.md` file → `.md` for Claude Code, Windsurf
- `.md` file → `.instructions.md` for GitHub Copilot
- Path: `<ide_instruction_path>/<name><extension>`

---

### MCPServerComponent

Reference to an MCP server configuration template.

**Fields**:
- `name: str` - Server identifier
- `file: str` - Relative path to MCP config template
- `description: str` - What the server provides
- `credentials: list[CredentialDescriptor]` - Required environment variables
- `ide_support: list[str]` - IDEs that support MCP (claude_code, windsurf)

**Validation Rules**:
- File must exist in package repository
- Config must be valid JSON with `${VARIABLE}` placeholders
- Credentials must reference variables used in template
- `ide_support` must only include MCP-capable IDEs

**Translation Rules**:
- Claude Desktop format: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windsurf format: `.windsurf/mcp_config.json`
- Merge into existing config (don't replace)
- Replace placeholders with `.env` values

---

### HookComponent

Reference to an IDE lifecycle hook script.

**Fields**:
- `name: str` - Hook identifier
- `file: str` - Relative path to hook script
- `description: str` - What the hook does
- `hook_type: str` - Hook trigger (e.g., pre-commit, post-install)
- `ide_support: list[str]` - IDEs that support hooks (currently only claude_code)

**Validation Rules**:
- File must exist and be executable (or .sh, .py, .js)
- `hook_type` must be valid for target IDE
- `ide_support` must only include hook-capable IDEs

**Translation Rules**:
- Claude Code: `.claude/hooks/<hook_type>.sh`
- Other IDEs: Skip with notification

---

### CommandComponent

Reference to a slash command or script.

**Fields**:
- `name: str` - Command identifier
- `file: str` - Relative path to command script
- `description: str` - What the command does
- `command_type: str` - Type (slash, shell)
- `ide_support: list[str]` - IDEs that support commands

**Validation Rules**:
- File must exist
- `command_type` must match IDE capabilities
- Name must be valid command name (no spaces, starts with letter)

**Translation Rules**:
- Cursor: `.cursor/commands/<name>.sh` (shell type)
- Claude Code: `.claude/commands/<name>.md` (slash type)
- Other IDEs: Skip with notification

---

### ResourceComponent

Reference to an arbitrary file resource.

**Fields**:
- `name: str` - Resource identifier
- `file: str` - Relative path to resource file
- `description: str` - What the resource is
- `checksum: str` - SHA256 checksum for integrity
- `size: int` - File size in bytes

**Validation Rules**:
- File must exist in package repository
- Size must be ≤ 200MB (enforced during package creation)
- Checksum must match file content
- Warn if size > 50MB

**Installation Rules**:
- Install to `.instructionkit/resources/<package-name>/<file>`
- Preserve directory structure
- Update checksum on modification detection

---

### CredentialDescriptor

Declaration of required environment variable for MCP server.

**Fields**:
- `name: str` - Environment variable name (UPPER_SNAKE_CASE)
- `description: str` - What the credential is for
- `required: bool` - Whether credential is mandatory
- `default: Optional[str]` - Default value if not required
- `example: Optional[str]` - Example value for guidance

**Validation Rules**:
- Name must match pattern: `^[A-Z][A-Z0-9_]*$`
- Required credentials cannot have default values
- Example should not contain real secrets

**Usage**:
- Prompt user during package installation
- Validate all required credentials before MCP config merge
- Store in `.instructionkit/.env` (gitignored)

---

## Storage Entities

### PackageInstallationRecord

Tracks installed package in a project.

**Fields**:
- `package_name: str` - Package identifier
- `namespace: str` - Repository namespace
- `version: str` - Installed version
- `installed_at: datetime` - Installation timestamp
- `updated_at: datetime` - Last update timestamp
- `scope: InstallationScope` - Installation scope (project_level)
- `components: list[InstalledComponent]` - Installed component details
- `status: InstallationStatus` - Installation state

**File Location**: `<project>/.instructionkit/packages.json`

**Validation Rules**:
- Package name and namespace must match manifest
- Version must be valid semver
- Component paths must be relative to project root
- Status must be valid enum value

**State Transitions**:
```
INSTALLING → COMPLETE (all components installed)
INSTALLING → PARTIAL (some components failed)
COMPLETE → UPDATING (update in progress)
UPDATING → COMPLETE (update successful)
UPDATING → PARTIAL (update partially failed)
PARTIAL → COMPLETE (retry successful)
```

---

### InstalledComponent

Tracks individual installed component within a package.

**Fields**:
- `type: ComponentType` - Component type (instruction, mcp, hook, command, resource)
- `name: str` - Component name
- `installed_path: str` - Relative path where installed
- `checksum: str` - File checksum for update detection
- `status: ComponentStatus` - Installation status (installed, failed, skipped, pending_credentials)

**Validation Rules**:
- Path must be relative
- Checksum must be SHA256
- Status must match component state

---

### MainRegistry

System-wide index of installations across all projects.

**Fields**:
- `projects: list[ProjectRegistration]` - Registered projects
- `last_scan: datetime` - Last scan timestamp
- `version: str` - Registry schema version

**File Location**: `~/.instructionkit/registry.json`

**Validation Rules**:
- Project paths must be absolute
- No duplicate project paths
- Version must match current schema version

**Operations**:
- Auto-update on install/uninstall
- Rebuild from project trackers via scan
- Validate and repair on load

---

### ProjectRegistration

Represents a project in the main registry.

**Fields**:
- `path: str` - Absolute path to project
- `name: str` - Project name (directory name)
- `packages: list[PackageReference]` - Installed packages
- `instructions: list[InstructionReference]` - Individual instructions
- `mcp_servers: list[MCPReference]` - MCP servers
- `registered_at: datetime` - When project was registered
- `last_updated: datetime` - Last installation activity

**Validation Rules**:
- Path must exist and be absolute
- Name must match directory name
- References must match project tracker data

---

### PackageReference

Reference to an installed package in registry.

**Fields**:
- `name: str` - Package name
- `namespace: str` - Repository namespace
- `version: str` - Installed version
- `installed_at: datetime` - Installation timestamp

**Usage**:
- Cross-project queries (e.g., "which projects use package X?")
- Update detection across projects
- Outdated package identification

---

## Enumerations

### ComponentType

```python
class ComponentType(Enum):
    INSTRUCTION = "instruction"
    MCP_SERVER = "mcp_server"
    HOOK = "hook"
    COMMAND = "command"
    RESOURCE = "resource"
```

### InstallationStatus

```python
class InstallationStatus(Enum):
    INSTALLING = "installing"
    COMPLETE = "complete"
    PARTIAL = "partial"  # Some components failed
    UPDATING = "updating"
    FAILED = "failed"
```

### ComponentStatus

```python
class ComponentStatus(Enum):
    INSTALLED = "installed"
    FAILED = "failed"
    SKIPPED = "skipped"  # Unsupported by IDE
    PENDING_CREDENTIALS = "pending_credentials"  # MCP missing credentials
```

### InstallationScope

```python
class InstallationScope(Enum):
    PROJECT_LEVEL = "project"
    # GLOBAL = "global"  # Deferred to future version
```

### SecretConfidence

```python
class SecretConfidence(Enum):
    HIGH = "high"  # Auto-template
    MEDIUM = "medium"  # Prompt user
    SAFE = "safe"  # Preserve value
```

---

## Translation Entities

### IDECapability

Defines what features each IDE supports.

**Fields**:
- `name: str` - IDE name
- `supports_instructions: bool` - Can install instructions
- `instruction_extension: str` - File extension (.md, .mdc, .instructions.md)
- `instruction_path: str` - Installation directory
- `supports_mcp: bool` - Can use MCP servers
- `mcp_config_path: Optional[str]` - MCP config file location
- `mcp_config_format: Optional[str]` - Config format (claude_desktop, windsurf)
- `supports_hooks: bool` - Can run lifecycle hooks
- `hook_path: Optional[str]` - Hook installation directory
- `supports_commands: bool` - Can run custom commands
- `command_path: Optional[str]` - Command installation directory
- `command_type: Optional[str]` - Command type (slash, shell)

**Validation Rules**:
- If `supports_*` is True, corresponding paths/formats must be set
- Paths must be relative to project root
- Format must be valid enum value

**Registry**:
```python
CAPABILITY_REGISTRY: dict[str, IDECapability]
```

---

### TranslatedComponent

Result of translating a component to IDE-specific format.

**Fields**:
- `source: PackageComponent` - Original component
- `target_path: str` - Where to install (relative to project)
- `content: str | bytes` - Translated content
- `extension: str` - File extension
- `merge_strategy: Optional[MergeStrategy]` - How to merge with existing

**Validation Rules**:
- Target path must not escape project directory
- Merge strategy required for config files (MCP)

---

### MergeStrategy

```python
class MergeStrategy(Enum):
    REPLACE = "replace"  # Overwrite entire file
    MERGE_JSON = "merge_json"  # Merge JSON keys
    MERGE_YAML = "merge_yaml"  # Merge YAML keys
    APPEND = "append"  # Append to file
```

---

## Versioning Entities

### SemanticVersion

Parsed semantic version for comparison.

**Fields**:
- `major: int` - Major version (breaking changes)
- `minor: int` - Minor version (new features)
- `patch: int` - Patch version (bug fixes)
- `prerelease: Optional[str]` - Prerelease identifier
- `build: Optional[str]` - Build metadata

**Operations**:
- `__lt__`, `__eq__`, `__gt__` - Version comparison
- `parse(version_string: str) -> SemanticVersion` - Parse from string
- `bump_major/minor/patch() -> SemanticVersion` - Increment version

**Validation Rules**:
- Must follow semver format: `major.minor.patch[-prerelease][+build]`
- Major, minor, patch must be non-negative integers
- Prerelease and build must match semver spec

---

### VersionUpdate

Information about an available update.

**Fields**:
- `package_name: str` - Package identifier
- `current_version: SemanticVersion` - Installed version
- `latest_version: SemanticVersion` - Available version
- `update_type: UpdateType` - Type of update (major, minor, patch)
- `changelog: Optional[str]` - Changes in new version

**Derived Properties**:
- `is_breaking: bool` - Whether update is major version bump
- `is_security: bool` - Whether update fixes security issue (from tags)

---

### UpdateType

```python
class UpdateType(Enum):
    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features
    PATCH = "patch"  # Bug fixes
```

---

## Validation Summary

### Cross-Entity Constraints

1. **Package Manifest Completeness**: All components referenced in `PackageComponents` must have corresponding files in the repository
2. **Installation Consistency**: Components in `PackageInstallationRecord` must match components in package manifest
3. **Registry Sync**: `MainRegistry` project registrations must match data in project trackers (source of truth)
4. **Credential Completeness**: All required credentials in `CredentialDescriptor` must exist in `.env` before MCP sync
5. **IDE Compatibility**: Components with `ide_support` restrictions can only install on supported IDEs
6. **Version Ordering**: Version comparisons must use semver rules (not lexicographic)
7. **Checksum Integrity**: Installed component checksums must match repository checksums (or be marked modified)
8. **Path Safety**: All installed paths must be relative and not escape project directory

---

## File Formats

### packages.json Structure

```json
{
  "version": "1.0",
  "packages": [
    {
      "name": "productivity-workflow",
      "namespace": "acme/configs",
      "version": "1.2.0",
      "installed_at": "2025-11-14T10:30:00Z",
      "updated_at": "2025-11-14T10:30:00Z",
      "scope": "project",
      "status": "complete",
      "components": [
        {
          "type": "instruction",
          "name": "beeminder-guide",
          "installed_path": ".claude/rules/beeminder-guide.md",
          "checksum": "sha256:abc123...",
          "status": "installed"
        },
        {
          "type": "mcp_server",
          "name": "beeminder",
          "installed_path": ".instructionkit/mcp/beeminder/config.json",
          "checksum": "sha256:def456...",
          "status": "installed"
        }
      ]
    }
  ]
}
```

### registry.json Structure

```json
{
  "version": "1.0",
  "last_scan": "2025-11-14T11:00:00Z",
  "projects": [
    {
      "path": "/Users/troy/projects/acme-web",
      "name": "acme-web",
      "registered_at": "2025-11-01T09:00:00Z",
      "last_updated": "2025-11-14T10:30:00Z",
      "packages": [
        {
          "name": "productivity-workflow",
          "namespace": "acme/configs",
          "version": "1.2.0",
          "installed_at": "2025-11-14T10:30:00Z"
        }
      ],
      "instructions": [...],
      "mcp_servers": [...]
    }
  ]
}
```

---

## Migration Considerations

### Backward Compatibility

- Existing `installations.json` (individual instructions) remains unchanged
- New `packages.json` file created alongside for package tracking
- Main registry is new - built from scratch on first scan
- No breaking changes to existing data structures

### Schema Versioning

- All JSON files include `"version"` field for future migrations
- Version 1.0 for initial release
- Future versions can include migration logic

---

## Performance Considerations

1. **Lazy Loading**: Don't load all packages into memory - parse on demand
2. **Caching**: Cache parsed manifests during installation to avoid re-parsing
3. **Streaming**: Use streaming for large resource files (>10MB)
4. **Checksum Comparison**: Only compute checksums when needed (update detection)
5. **Registry Indexing**: Main registry indexed by project path for O(1) lookup
6. **Batch Operations**: Batch file operations during installation to reduce I/O

---

## Security Considerations

1. **Path Traversal**: Validate all paths to prevent escaping project directory
2. **Secret Leakage**: Never log or display credential values
3. **Checksum Validation**: Always verify checksums to detect tampering
4. **File Permissions**: Ensure `.env` files have restricted permissions (0600)
5. **Gitignore Enforcement**: Warn if `.env` not in `.gitignore`
6. **Input Validation**: Validate all user input (package names, versions, credentials)

---

## Testing Strategy

### Unit Tests

- Model validation (all dataclasses)
- Version comparison logic
- Secret detection heuristics
- Checksum computation
- Path validation

### Integration Tests

- Package installation end-to-end
- Package creation from project
- Registry rebuild from trackers
- Update detection and application
- Conflict resolution flows

### Property Tests

- Semver ordering (transitivity, reflexivity)
- Checksum uniqueness
- Path safety (no escapes)

---

## References

- Existing data models: `ai-config-kit/core/models.py`
- Installation tracking: `ai-config-kit/storage/tracker.py`
- Repository parsing: `ai-config-kit/core/repository.py`
