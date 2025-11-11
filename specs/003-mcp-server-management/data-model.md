# Data Model: MCP Server Configuration Management

**Feature**: 003-mcp-server-management
**Date**: 2025-11-11
**Spec**: [spec.md](spec.md)

## Overview

This document defines the data models for MCP server configuration management. Models are implemented as Python dataclasses with full type hints and validation logic.

## Core Entities

### MCPServer

Represents a single MCP server definition from a template repository.

**Fields**:
- `name: str` - Unique identifier within namespace (alphanumeric, hyphens, underscores)
- `command: str` - Executable command to launch MCP server
- `args: list[str]` - Command-line arguments for the server
- `env: dict[str, str | None]` - Environment variables (None = requires user configuration)
- `namespace: str` - Source template namespace (for namespaced identification)

**Validation Rules**:
- `name` must match pattern `^[a-zA-Z0-9_-]+$`
- `command` must be non-empty string
- `args` defaults to empty list if not provided
- `env` keys must match pattern `^[A-Z][A-Z0-9_]*$` (uppercase with underscores)

**Methods**:
- `get_fully_qualified_name() -> str` - Returns `{namespace}.{name}`
- `get_required_env_vars() -> list[str]` - Returns env var names where value is None
- `has_all_credentials(env_config: EnvironmentConfig) -> bool` - Check if all required vars are configured
- `to_dict() -> dict` - Serialize for JSON
- `from_dict(data: dict, namespace: str) -> MCPServer` - Deserialize from templatekit.yaml

**State Transitions**: Immutable once created

**Example**:
```python
mcp_server = MCPServer(
    name="github",
    command="uvx",
    args=["mcp-server-github"],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": None},  # Requires configuration
    namespace="backend"
)
```

---

### MCPSet

A named collection of MCP servers for a specific workflow or task context.

**Fields**:
- `name: str` - Set identifier (e.g., "backend-dev", "frontend-dev")
- `description: str` - Human-readable description of set purpose
- `server_names: list[str]` - Names of MCP servers included in this set
- `namespace: str` - Source template namespace

**Validation Rules**:
- `name` must match pattern `^[a-zA-Z0-9_-]+$`
- `server_names` must not be empty
- Each server name must reference a server defined in the same template

**Methods**:
- `get_fully_qualified_name() -> str` - Returns `{namespace}.{name}`
- `resolve_servers(all_servers: list[MCPServer]) -> list[MCPServer]` - Get actual server objects
- `to_dict() -> dict` - Serialize
- `from_dict(data: dict, namespace: str) -> MCPSet` - Deserialize

**Example**:
```python
mcp_set = MCPSet(
    name="backend-dev",
    description="MCP servers for backend development",
    server_names=["filesystem", "github", "database"],
    namespace="backend"
)
```

---

### MCPTemplate

Represents an installed MCP template from a repository.

**Fields**:
- `namespace: str` - Unique identifier for this template
- `source_url: str | None` - Git URL or None for local installs
- `source_path: str | None` - Local directory path or None for Git installs
- `version: str` - Template version from templatekit.yaml
- `description: str` - Template description
- `installed_at: datetime` - Installation timestamp
- `servers: list[MCPServer]` - MCP servers defined in template
- `sets: list[MCPSet]` - MCP sets defined in template

**Validation Rules**:
- Either `source_url` or `source_path` must be set, not both
- `namespace` must be unique across all installed templates
- `version` follows semantic versioning pattern

**Methods**:
- `get_server_by_name(name: str) -> MCPServer | None` - Find server by name
- `get_set_by_name(name: str) -> MCPSet | None` - Find set by name
- `get_library_path(library_root: Path) -> Path` - Returns `{library_root}/{namespace}/`
- `to_dict() -> dict` - Serialize
- `from_dict(data: dict) -> MCPTemplate` - Deserialize
- `from_repository(repo: Repository, namespace: str, source_url: str | None, source_path: str | None) -> MCPTemplate` - Create from parsed templatekit.yaml

**Example**:
```python
template = MCPTemplate(
    namespace="backend",
    source_url="https://github.com/company/backend-standards",
    source_path=None,
    version="1.0.0",
    description="Backend development standards",
    installed_at=datetime.now(),
    servers=[...],
    sets=[...]
)
```

---

### EnvironmentConfig

Manages environment variables from `.instructionkit/.env` file.

**Fields**:
- `variables: dict[str, str]` - Environment variable name-value pairs
- `file_path: Path` - Path to .env file
- `scope: InstallationScope` - PROJECT or GLOBAL

**Validation Rules**:
- Variable names must match `^[A-Z][A-Z0-9_]*$`
- Values can be multi-line (quoted with `\n`)
- No duplicate variable names

**Methods**:
- `get(key: str, default: str | None = None) -> str | None` - Get variable value
- `set(key: str, value: str) -> None` - Set variable value (validates name)
- `has(key: str) -> bool` - Check if variable exists
- `save() -> None` - Write to .env file with atomic write
- `load() -> None` - Read from .env file (validates syntax)
- `merge(other: EnvironmentConfig) -> EnvironmentConfig` - Merge two configs (for global + project)
- `validate_for_server(server: MCPServer) -> list[str]` - Return list of missing required vars
- `to_dict() -> dict[str, str]` - Export as plain dictionary

**File Format** (uses python-dotenv):
```bash
# MCP Server Credentials
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxx
DATABASE_URL="postgresql://user:pass@localhost/db"
MULTI_LINE_VALUE="line 1\nline 2\nline 3"
```

**Example**:
```python
env_config = EnvironmentConfig.load(project_root / ".instructionkit" / ".env", InstallationScope.PROJECT)
env_config.set("GITHUB_PERSONAL_ACCESS_TOKEN", "ghp_xxxxx")
env_config.save()
```

---

### AIToolMCPConfig

Represents an AI tool's MCP configuration structure for syncing.

**Fields**:
- `tool_type: AIToolType` - CLAUDE, CURSOR, WINDSURF, etc.
- `config_path: Path` - Path to tool's config file
- `mcp_servers: dict[str, MCPServerConfig]` - Current MCP servers in tool config
- `other_settings: dict` - Non-MCP settings to preserve

**Nested Type: MCPServerConfig**:
- `command: str`
- `args: list[str]`
- `env: dict[str, str]` - With resolved values (no None)

**Validation Rules**:
- `config_path` must be absolute
- `mcp_servers` keys must be valid server names
- Environment variables in `env` must have string values (no None)

**Methods**:
- `load(config_path: Path) -> AIToolMCPConfig` - Parse from tool's JSON config
- `save() -> None` - Write back to tool's config with atomic write
- `update_server(server: MCPServer, env_config: EnvironmentConfig) -> None` - Add/update MCP server with resolved env vars
- `remove_server(name: str) -> None` - Remove MCP server
- `sync_servers(servers: list[MCPServer], env_config: EnvironmentConfig) -> None` - Replace all MCP servers
- `backup() -> Path` - Create backup before modification
- `to_dict() -> dict` - Full config including other_settings

**Example**:
```python
tool_config = AIToolMCPConfig.load(Path.home() / ".claude" / "claude_desktop_config.json")
tool_config.update_server(mcp_server, env_config)
tool_config.save()  # Atomic write
```

---

### ActiveSetState

Tracks which MCP set is currently active in a project.

**Fields**:
- `namespace: str | None` - Active set's namespace (None = no active set)
- `set_name: str | None` - Active set's name (None = no active set)
- `activated_at: datetime | None` - When set was activated
- `active_servers: list[str]` - Fully qualified server names currently active

**Storage**: Stored in `.instructionkit/mcp_state.json` per project

**Validation Rules**:
- If `namespace` is set, `set_name` must also be set (and vice versa)
- `active_servers` must be empty if no active set

**Methods**:
- `load(project_root: Path) -> ActiveSetState` - Read from mcp_state.json
- `save(project_root: Path) -> None` - Write to mcp_state.json
- `activate_set(mcp_set: MCPSet, servers: list[MCPServer]) -> None` - Set active set
- `deactivate() -> None` - Clear active set
- `is_active() -> bool` - Check if any set is active
- `get_active_set_fqn() -> str | None` - Returns "namespace.set_name" or None

**Example**:
```python
state = ActiveSetState.load(project_root)
state.activate_set(backend_dev_set, servers)
state.save(project_root)
```

---

### MCPInstallation

Tracks an installed MCP template in the library for listing and management.

**Fields**:
- `template: MCPTemplate` - The template definition
- `scope: InstallationScope` - PROJECT or GLOBAL
- `installation_path: Path` - Actual path on filesystem

**Methods**:
- `list_all(library_root: Path, scope: InstallationScope) -> list[MCPInstallation]` - List all installations
- `find_by_namespace(namespace: str, library_root: Path, scope: InstallationScope) -> MCPInstallation | None`
- `uninstall() -> None` - Remove from filesystem

**Example**:
```python
installations = MCPInstallation.list_all(library_root, InstallationScope.PROJECT)
for install in installations:
    print(f"{install.template.namespace}: {len(install.template.servers)} servers")
```

---

## Enumerations

### InstallationScope

```python
class InstallationScope(str, Enum):
    PROJECT = "project"  # Stored in project-specific .instructionkit/
    GLOBAL = "global"    # Stored in ~/.instructionkit/global/
```

**Usage**: Determines where MCP configurations are stored and loaded from.

---

## Relationships

```
MCPTemplate
    │
    ├── 1:N ─> MCPServer (servers in template)
    │           │
    │           └── requires ─> EnvironmentConfig (credential resolution)
    │
    └── 1:N ─> MCPSet (sets in template)
                │
                └── references ─> MCPServer (by name)

ActiveSetState
    └── references ─> MCPSet (by namespace.name)

AIToolMCPConfig
    └── contains ─> MCPServer (synced servers with resolved env)
```

**Key Flows**:
1. **Install**: Parse templatekit.yaml → Create MCPTemplate → Store in library
2. **Configure**: Load EnvironmentConfig → Set credentials → Save
3. **Sync**: Load MCPTemplate → Resolve env vars → Update AIToolMCPConfig → Save
4. **Activate Set**: Load MCPSet → Resolve servers → Sync to tools → Update ActiveSetState

---

## Validation Summary

### Cross-Entity Validation

1. **MCP Set References**: When creating MCPSet, validate that all `server_names` reference existing MCPServer objects in the same template
2. **Environment Variable Completeness**: Before syncing, validate that all servers' required env vars exist in EnvironmentConfig
3. **Namespace Uniqueness**: Across all MCPTemplate objects, namespace must be unique within scope (PROJECT or GLOBAL)
4. **Config File Permissions**: AIToolMCPConfig.save() must verify write permissions before attempting atomic write
5. **Path Resolution**: All Path objects must be resolved (absolute) before storage

### Error States

- **Missing Credentials**: Server has required env vars (None values) not present in EnvironmentConfig
- **Invalid Set**: MCPSet references server names not defined in template
- **Conflicting Namespace**: Attempting to install template with namespace that already exists
- **Corrupted Config**: AIToolMCPConfig.load() fails to parse JSON (backup and warn)
- **No Active Set**: ActiveSetState operations fail when no set is active

---

## Testing Strategy

### Unit Tests
- Each model's `to_dict()` / `from_dict()` round-trip
- Validation rule enforcement (invalid names, patterns, etc.)
- Method behavior (get_required_env_vars, resolve_servers, etc.)
- Edge cases (empty lists, None values, special characters)

### Integration Tests
- Full workflow: Install template → Configure credentials → Sync to tools
- Cross-entity validation (set references, env var resolution)
- File I/O operations (load/save with actual files in temp directory)
- Atomic writes under failure conditions (disk full simulation)
- Multi-scope interaction (global + project merging)

### Property-Based Tests
- Namespace string validation with various inputs
- Environment variable name patterns
- Round-trip serialization for all models

---

## File Format Examples

### templatekit.yaml (Input)

```yaml
name: Backend Development Standards
version: 1.0.0
description: MCP servers for backend work

mcp_servers:
  - name: github
    command: uvx
    args: ["mcp-server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: null  # Requires user config

  - name: filesystem
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed"]
    env: {}  # No credentials needed

mcp_sets:
  - name: backend-dev
    description: "MCP servers for backend development"
    servers: ["filesystem", "github"]
```

### .instructionkit/.env (Credentials)

```bash
# GitHub Access
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxx

# Database
DATABASE_URL=postgresql://localhost/mydb

# Multi-line certificate
SSL_CERT="-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----"
```

### .instructionkit/mcp_state.json (Active Set)

```json
{
  "namespace": "backend",
  "set_name": "backend-dev",
  "activated_at": "2025-11-11T10:30:00Z",
  "active_servers": [
    "backend.filesystem",
    "backend.github"
  ]
}
```

### ~/.claude/claude_desktop_config.json (AI Tool Config)

```json
{
  "mcpServers": {
    "backend.github": {
      "command": "uvx",
      "args": ["mcp-server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    },
    "backend.filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed"],
      "env": {}
    }
  },
  "otherSettings": {
    "theme": "dark",
    "fontSize": 14
  }
}
```

---

## Implementation Notes

1. **Immutability**: MCPServer, MCPSet, and MCPTemplate should be immutable (frozen dataclasses) after creation
2. **Type Safety**: All models must pass mypy strict mode with no type: ignore comments
3. **Serialization**: Use `to_dict()` / `from_dict()` consistently, not pickle or other formats
4. **Error Messages**: Include field names and values in validation error messages for debugging
5. **Logging**: Log all file write operations and credential resolutions for audit trail
6. **Performance**: Cache EnvironmentConfig.load() results per command invocation (don't re-read .env file multiple times)
