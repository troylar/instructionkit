# CLI Reference

Complete command-line interface reference for InstructionKit.

## Table of Contents

- [Template Commands](#template-commands)
- [MCP Commands](#mcp-commands)
- [Utility Commands](#utility-commands)
- [Global Options](#global-options)

---

## Template Commands

### `inskit template install`

Install a template repository.

```bash
inskit template install <source> --as <namespace> [options]
```

**Arguments:**
- `<source>` - Git URL or local directory path

**Options:**
- `--as <namespace>` - Namespace for installed templates (required)
- `--scope <scope>` - Installation scope: `project` (default) or `global`
- `--force` - Overwrite existing installation
- `--ref <ref>` - Git branch, tag, or commit (default: main)

**Examples:**
```bash
# Install from GitHub
inskit template install https://github.com/company/standards --as company

# Install from local directory
inskit template install ./my-templates --as local

# Install specific version
inskit template install https://github.com/company/standards --as company --ref v1.2.0

# Install globally
inskit template install https://github.com/personal/tools --as personal --scope global
```

### `inskit template list`

List installed templates.

```bash
inskit template list [namespace] [options]
```

**Options:**
- `--scope <scope>` - Filter by scope: `project` or `global`
- `--json` - Output as JSON

**Examples:**
```bash
# List all templates
inskit template list

# List specific namespace
inskit template list company

# JSON output
inskit template list --json
```

### `inskit template update`

Update installed templates to latest version.

```bash
inskit template update <namespace> [options]
inskit template update --all [options]
```

**Options:**
- `--all` - Update all installed templates
- `--scope <scope>` - Update scope: `project` or `global`

**Examples:**
```bash
# Update specific namespace
inskit template update company

# Update all templates
inskit template update --all
```

### `inskit template uninstall`

Uninstall template repository.

```bash
inskit template uninstall <namespace> [options]
```

**Options:**
- `--scope <scope>` - Uninstall scope: `project` or `global`
- `--force` - Skip confirmation

**Examples:**
```bash
# Uninstall namespace
inskit template uninstall company

# Uninstall global
inskit template uninstall personal --scope global
```

### `inskit template init`

Create a new template repository.

```bash
inskit template init <name> [options]
```

**Arguments:**
- `<name>` - Directory name for new repository

**Options:**
- `--minimal` - Create minimal structure (no examples)

**Examples:**
```bash
# Create with examples
inskit template init my-standards

# Create minimal structure
inskit template init my-standards --minimal
```

### `inskit template validate`

Validate a template repository.

```bash
inskit template validate <path>
```

**Arguments:**
- `<path>` - Path to template repository

**Examples:**
```bash
# Validate current directory
inskit template validate .

# Validate specific path
inskit template validate ./my-templates
```

---

## MCP Commands

### `inskit mcp install`

Install MCP server configurations.

```bash
inskit mcp install <source> --as <namespace> [options]
```

**Arguments:**
- `<source>` - Git URL or local directory path

**Options:**
- `--as <namespace>` - Namespace for MCP servers (required)
- `--scope <scope>` - Installation scope: `project` (default) or `global`
- `--force` - Overwrite existing installation
- `--ref <ref>` - Git branch, tag, or commit

**Examples:**
```bash
# Install from GitHub
inskit mcp install https://github.com/company/mcp-servers --as backend

# Install from local directory
inskit mcp install ./my-mcp-servers --as local

# Install globally
inskit mcp install https://github.com/personal/mcp --as personal --scope global
```

### `inskit mcp configure`

Configure credentials for MCP servers.

```bash
inskit mcp configure <server-ref> [options]
```

**Arguments:**
- `<server-ref>` - Format: `namespace` or `namespace.server`

**Options:**
- `--scope <scope>` - Configuration scope: `project` (default) or `global`
- `--non-interactive` - Read credentials from environment
- `--show-current` - Show current credentials (masked)
- `--json` - Output as JSON

**Examples:**
```bash
# Configure all servers in namespace (interactive)
inskit mcp configure backend

# Configure specific server
inskit mcp configure backend.github

# Non-interactive (from environment)
export GITHUB_TOKEN=ghp_xxxxx
inskit mcp configure backend --non-interactive

# Show current credentials
inskit mcp configure backend --show-current
```

### `inskit mcp sync`

Sync MCP servers to AI tool configuration files.

```bash
inskit mcp sync [options]
```

**Options:**
- `--tool <tool>` - Target tool: `claude`, `cursor`, `windsurf`, or `all` (default: `all`)
- `--scope <scope>` - Load from scope: `project` (default) or `global`
- `--dry-run` - Show what would be synced without making changes
- `--no-backup` - Skip creating backup files
- `--json` - Output as JSON

**Examples:**
```bash
# Sync to all detected tools
inskit mcp sync --tool all

# Sync to Claude Desktop only
inskit mcp sync --tool claude

# Dry run (no changes)
inskit mcp sync --tool all --dry-run

# Skip backups
inskit mcp sync --tool claude --no-backup
```

### `inskit mcp list`

List installed MCP servers.

```bash
inskit mcp list [namespace] [options]
```

**Options:**
- `--scope <scope>` - Filter by scope: `project` or `global`
- `--sets` - Show MCP sets
- `--json` - Output as JSON

**Examples:**
```bash
# List all servers
inskit mcp list

# List specific namespace
inskit mcp list backend

# Show sets
inskit mcp list --sets
```

### `inskit mcp update`

Update MCP server configurations.

```bash
inskit mcp update <namespace> [options]
inskit mcp update --all [options]
```

**Options:**
- `--all` - Update all MCP templates
- `--scope <scope>` - Update scope: `project` or `global`

**Examples:**
```bash
# Update specific namespace
inskit mcp update backend

# Update all MCP templates
inskit mcp update --all
```

### `inskit mcp uninstall`

Uninstall MCP template.

```bash
inskit mcp uninstall <namespace> [options]
```

**Options:**
- `--scope <scope>` - Uninstall scope: `project` or `global`

**Examples:**
```bash
# Uninstall namespace
inskit mcp uninstall backend

# Uninstall global
inskit mcp uninstall company --scope global
```

---

## Utility Commands

### `inskit tools`

Show detected AI coding tools.

```bash
inskit tools
```

Displays which AI tools are installed (Claude Code, Claude Desktop, Cursor, Copilot, Windsurf) and their configuration directories.

**Example output:**
```
AI Coding Tools
Tool               Installed    Config Directory
Claude Code        ✓            ~/.claude
Claude Desktop     ✓            ~/Library/Application Support/Claude
Cursor             ✓            ~/Library/Application Support/Cursor
GitHub Copilot     ✗            Not found
Windsurf           ✓            ~/Library/Application Support/Windsurf
```

### `inskit --version`

Show InstructionKit version.

```bash
inskit --version
```

### `inskit --help`

Show help information.

```bash
# General help
inskit --help

# Command-specific help
inskit template --help
inskit template install --help
inskit mcp --help
inskit mcp configure --help
```

---

## Global Options

These options can be used with any command:

- `--help` - Show help for command
- `--version` - Show version

---

## Environment Variables

### LOGLEVEL

Control logging verbosity:

```bash
# Debug mode
export LOGLEVEL=DEBUG
inskit mcp sync --tool all

# Quiet mode
export LOGLEVEL=ERROR
inskit template install <repo> --as demo
```

**Levels:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Command-line syntax error |

---

## Configuration Files

InstructionKit uses these configuration files:

| File | Location | Purpose |
|------|----------|---------|
| `template-installations.json` | `.instructionkit/` | Tracks installed templates |
| `mcp-installations.json` | `.instructionkit/` | Tracks installed MCP servers |
| `.env` | `.instructionkit/` | Project-scoped credentials (gitignored) |
| `.env` | `~/.instructionkit/global/` | Global-scoped credentials (gitignored) |

---

**[← Back to Main Documentation](../README.md)**
