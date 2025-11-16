# CLI Command Contracts: MCP Server Management

**Feature**: 003-mcp-server-management
**Date**: 2025-11-11

This document defines the command-line interface contracts for all MCP-related commands. These contracts serve as the specification for implementation and testing.

---

## Base Command

```bash
inskit mcp [SUBCOMMAND] [OPTIONS] [ARGUMENTS]
```

**Common Options** (available on all subcommands):
- `--help` - Show command help
- `--json` - Output in JSON format for scripting
- `--verbose` / `-v` - Enable verbose output
- `--quiet` / `-q` - Suppress non-error output

---

## 1. inskit mcp install

Install MCP server configurations from a template repository.

### Syntax

```bash
inskit mcp install <URL|PATH> --as <NAMESPACE> [OPTIONS]
```

### Arguments

- `<URL|PATH>` (required) - Git repository URL or local directory path
  - Git URL: `https://github.com/company/templates` or `git@github.com:company/templates.git`
  - Local path: `/path/to/templates` or `./templates`

### Options

- `--as <NAMESPACE>` (required) - Namespace for this template installation
  - Must be unique
  - Alphanumeric, hyphens, underscores only
  - Example: `backend`, `my-team-tools`

- `--scope {project|global}` - Installation scope (default: `project`)
  - `project`: Store in current project's `.instructionkit/` directory
  - `global`: Store in `~/.instructionkit/global/` for all projects

- `--force` / `-f` - Overwrite existing installation with same namespace

- `--conflict {skip|overwrite|rename}` - Conflict resolution strategy
  - `skip`: Don't reinstall if namespace exists (default)
  - `overwrite`: Replace existing installation
  - `rename`: Install with incremented suffix (e.g., `backend-1`)

### Output

**Success (Human-readable)**:
```
✓ Cloning repository...
✓ Parsing templatekit.yaml...
✓ Found 3 MCP servers: filesystem, github, database
✓ Found 2 MCP sets: backend-dev, backend-prod
✓ Installed to: ~/.instructionkit/library/backend/

Next steps:
  1. Configure credentials: inskit mcp configure backend.github
  2. List servers: inskit mcp list backend
  3. Sync to tools: inskit mcp sync --tool all
```

**Success (JSON)**:
```json
{
  "status": "success",
  "namespace": "backend",
  "servers_count": 3,
  "sets_count": 2,
  "installation_path": "/Users/user/.instructionkit/library/backend",
  "servers_requiring_config": ["github", "database"],
  "next_steps": [
    "inskit mcp configure backend.github",
    "inskit mcp configure backend.database"
  ]
}
```

**Error Cases**:
- Exit 1: Namespace already exists (without `--force`)
- Exit 2: Invalid repository URL or path not found
- Exit 3: Invalid `templatekit.yaml` format
- Exit 4: No MCP servers defined in template

### Examples

```bash
# Install from GitHub
inskit mcp install https://github.com/company/backend-tools --as backend

# Install from local directory
inskit mcp install ./my-tools --as personal

# Install globally
inskit mcp install https://github.com/me/productivity --as personal --scope global

# Force reinstall
inskit mcp install https://github.com/company/backend-tools --as backend --force
```

---

## 2. inskit mcp configure

Interactively configure credentials for an MCP server.

### Syntax

```bash
inskit mcp configure <NAMESPACE>.<SERVER> [OPTIONS]
```

### Arguments

- `<NAMESPACE>.<SERVER>` (required) - Fully qualified server name
  - Example: `backend.github`, `personal.slack`

### Options

- `--scope {project|global}` - Which .env file to update (default: auto-detect)
  - If server is in global scope, updates global .env
  - If server is in project scope, updates project .env

- `--non-interactive` - Provide credentials via environment variables
  - Reads from env vars: `INSKIT_<VAR_NAME>=value`
  - Example: `GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx inskit mcp configure backend.github --non-interactive`

- `--show-current` - Display current configured values (masked)

### Interactive Prompts

```
Configuring MCP server: backend.github

Required environment variables:
  1. GITHUB_PERSONAL_ACCESS_TOKEN

Enter GITHUB_PERSONAL_ACCESS_TOKEN: ****************************
Confirm GITHUB_PERSONAL_ACCESS_TOKEN: ****************************

✓ Credentials saved to: .instructionkit/.env
✓ Server 'backend.github' is now configured
```

### Output

**Success (Human-readable)**:
```
✓ Server 'backend.github' configured successfully
✓ Credentials saved to: .instructionkit/.env

You can now sync this server:
  inskit mcp sync --tool all
```

**Success (JSON)**:
```json
{
  "status": "success",
  "server": "backend.github",
  "configured_vars": ["GITHUB_PERSONAL_ACCESS_TOKEN"],
  "env_file": "/path/to/project/.instructionkit/.env"
}
```

**Error Cases**:
- Exit 1: Server not found
- Exit 2: Mismatched credentials during confirmation
- Exit 3: Invalid environment variable value
- Exit 4: Permission denied writing .env file

### Examples

```bash
# Interactive configuration
inskit mcp configure backend.github

# Non-interactive
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx inskit mcp configure backend.github --non-interactive

# Show current values
inskit mcp configure backend.github --show-current
```

---

## 3. inskit mcp sync

Sync MCP server configurations to AI tool config files.

### Syntax

```bash
inskit mcp sync [OPTIONS]
```

### Options

- `--tool {claude|cursor|windsurf|all}` (required) - Which AI tool(s) to sync
  - `claude`: Sync to Claude Desktop
  - `cursor`: Sync to Cursor IDE
  - `windsurf`: Sync to Windsurf IDE
  - `all`: Sync to all detected tools

- `--server <NAMESPACE>.<SERVER>` - Sync only specific server (can repeat)
  - Example: `--server backend.github --server backend.filesystem`

- `--scope {project|global|both}` - Which MCP servers to include (default: `both`)
  - `project`: Only project-scoped servers
  - `global`: Only global-scoped servers
  - `both`: Merge global + project (project takes precedence on conflicts)

- `--dry-run` - Show what would be synced without modifying files

- `--backup` - Create backup of AI tool configs before modification (enabled by default)

- `--no-backup` - Skip backup creation

### Output

**Success (Human-readable)**:
```
Syncing MCP servers...

✓ Detected Claude Desktop at: ~/.claude/claude_desktop_config.json
✓ Detected Cursor at: ~/.cursor/mcp.json
  Windsurf not detected (skipped)

Syncing to Claude Desktop:
  ✓ backend.github (configured)
  ✓ backend.filesystem (configured)
  ⚠ backend.database (missing credentials: DATABASE_URL)

Syncing to Cursor:
  ✓ backend.github (configured)
  ✓ backend.filesystem (configured)
  ⚠ backend.database (missing credentials: DATABASE_URL)

Summary:
  • 2 servers synced successfully
  • 1 server skipped (missing credentials)
  • 2 tools updated
  • Backups created

Next steps:
  Configure backend.database: inskit mcp configure backend.database
```

**Success (JSON)**:
```json
{
  "status": "success",
  "tools_synced": ["claude", "cursor"],
  "tools_skipped": ["windsurf"],
  "servers_synced": [
    {"name": "backend.github", "status": "success"},
    {"name": "backend.filesystem", "status": "success"}
  ],
  "servers_skipped": [
    {"name": "backend.database", "reason": "missing_credentials", "missing_vars": ["DATABASE_URL"]}
  ],
  "backups": [
    "/Users/user/.claude/claude_desktop_config.json.backup.20251111103045",
    "/Users/user/.cursor/mcp.json.backup.20251111103045"
  ]
}
```

**Error Cases**:
- Exit 1: No AI tools detected
- Exit 2: All servers missing credentials
- Exit 3: Permission denied writing tool config
- Exit 4: Invalid JSON in existing tool config

### Examples

```bash
# Sync to all detected tools
inskit mcp sync --tool all

# Sync to Claude only
inskit mcp sync --tool claude

# Sync specific server
inskit mcp sync --tool all --server backend.github

# Dry run
inskit mcp sync --tool all --dry-run

# Project-scoped only
inskit mcp sync --tool all --scope project
```

---

## 4. inskit mcp import

Import MCP server configurations from AI tool config files into the library.

### Syntax

```bash
inskit mcp import --from <TOOL> --as <NAMESPACE> [OPTIONS]
```

### Arguments

- `--from <TOOL>` (required) - Which AI tool to import from
  - `claude`: Import from Claude Desktop (`~/.claude/claude_desktop_config.json`)
  - `cursor`: Import from Cursor (`~/.cursor/mcp.json`)
  - `windsurf`: Import from Windsurf (`~/.codeium/windsurf/mcp_config.json`)
  - `all`: Import from all detected tools

- `--as <NAMESPACE>` (required) - Namespace for imported template
  - Must be unique (unless using `--merge`)
  - Alphanumeric, hyphens, underscores only

### Options

- `--scope {project|global}` - Where to store imported template (default: `project`)

- `--merge` - Merge imported servers into existing template (instead of creating new)

- `--export-template` - Create full repository structure for Git sharing
  - Generates README.md, .gitignore, and example documentation

- `--auto-secrets` - Automatically detect and extract secrets (no prompts)
  - Heuristics: Variables with "KEY", "TOKEN", "SECRET", "PASSWORD" in name

- `--keep-values` - Keep all environment variable values in template (less secure)

- `--force` / `-f` - Overwrite existing namespace without prompting

### Output

**Success (Human-readable)**:
```
Importing MCP servers from Cursor...

✓ Detected Cursor config: ~/.cursor/mcp.json
✓ Found 3 MCP servers: github, filesystem, custom-api

Analyzing environment variables...

github:
  GITHUB_PERSONAL_ACCESS_TOKEN: Is this a secret? (Y/n): y
  → Will extract to .instructionkit/.env

custom-api:
  API_KEY: Is this a secret? (Y/n): y
  → Will extract to .instructionkit/.env

  DEFAULT_TIMEOUT: Is this a secret? (Y/n): n
  → Will keep value "30" in template

✓ Created template: ~/.instructionkit/library/my-cursor-servers/
✓ Generated templatekit.yaml with 3 servers
✓ Extracted 2 secrets to .instructionkit/.env

Template is now available:
  List: inskit mcp list my-cursor-servers
  Sync to other tools: inskit mcp sync --tool all
```

**Success with --export-template (Human-readable)**:
```
Importing MCP servers from Cursor...

✓ Found 3 MCP servers
✓ Created template: ~/.instructionkit/library/my-servers/
✓ Generated templatekit.yaml
✓ Created README.md
✓ Created .gitignore
✓ Created example documentation

Template repository structure:
my-servers/
├── templatekit.yaml        # Template manifest
├── README.md               # Usage documentation
├── .gitignore              # Ignores .env files
└── examples/
    └── .env.example        # Example credentials

Ready to share:
  cd ~/.instructionkit/library/my-servers
  git init && git add . && git commit -m "Initial commit"
  git remote add origin <your-repo-url>
  git push -u origin main
```

**Success (JSON)**:
```json
{
  "status": "success",
  "source_tool": "cursor",
  "namespace": "my-cursor-servers",
  "servers_imported": 3,
  "servers": [
    {"name": "github", "command": "uvx", "secrets_extracted": 1},
    {"name": "filesystem", "command": "npx", "secrets_extracted": 0},
    {"name": "custom-api", "command": "python", "secrets_extracted": 1}
  ],
  "template_path": "/Users/user/.instructionkit/library/my-cursor-servers",
  "secrets_extracted": 2,
  "exported_as_repo": false
}
```

**Error Cases**:
- Exit 1: AI tool not detected or config file not found
- Exit 2: No MCP servers found in tool config
- Exit 3: Namespace already exists (without `--force` or `--merge`)
- Exit 4: Invalid tool config format

### Examples

```bash
# Import from Cursor
inskit mcp import --from cursor --as my-cursor-servers

# Import from all detected tools
inskit mcp import --from all --as my-collection

# Import and create shareable repository
inskit mcp import --from cursor --as my-servers --export-template

# Import globally (available in all projects)
inskit mcp import --from cursor --as personal-tools --scope global

# Merge into existing template
inskit mcp import --from cursor --as backend --merge

# Auto-detect secrets without prompts
inskit mcp import --from cursor --as my-servers --auto-secrets

# Keep all values in template (less secure)
inskit mcp import --from cursor --as my-servers --keep-values
```

---

## 5. inskit mcp list

List installed MCP servers and sets.

### Syntax

```bash
inskit mcp list [NAMESPACE] [OPTIONS]
```

### Arguments

- `[NAMESPACE]` (optional) - Filter by namespace
  - Example: `inskit mcp list backend` shows only backend namespace

### Options

- `--sets` - Show MCP sets instead of servers

- `--scope {project|global|both}` - Which scope to list (default: `both`)

- `--status` - Include configuration status for each server
  - Shows: configured, partially configured, needs configuration

- `--verbose` / `-v` - Show detailed information (source URL, version, install date)

### Output

**Default (Servers, Human-readable)**:
```
MCP Servers:

backend (3 servers) - Backend Development Standards
  Source: https://github.com/company/backend-tools
  Installed: 2025-11-11

  ✓ filesystem         [configured]
  ✓ github            [configured]
  ⚠ database          [needs configuration: DATABASE_URL]

personal (2 servers) - Personal Productivity Tools [GLOBAL]
  Source: /Users/user/my-tools
  Installed: 2025-11-10

  ✓ slack             [configured]
  ✓ notes             [configured]

Total: 5 MCP servers across 2 templates
```

**Sets (Human-readable)**:
```
MCP Sets:

backend.backend-dev
  Description: MCP servers for backend development
  Servers: filesystem, github, database (3)
  Status: 2/3 configured

backend.backend-prod
  Description: Production backend servers
  Servers: filesystem, database (2)
  Status: 1/2 configured

Total: 2 MCP sets
```

**JSON Output**:
```json
{
  "templates": [
    {
      "namespace": "backend",
      "scope": "project",
      "source_url": "https://github.com/company/backend-tools",
      "version": "1.0.0",
      "installed_at": "2025-11-11T10:00:00Z",
      "servers": [
        {
          "name": "filesystem",
          "status": "configured",
          "required_vars": []
        },
        {
          "name": "github",
          "status": "configured",
          "required_vars": []
        },
        {
          "name": "database",
          "status": "needs_configuration",
          "required_vars": ["DATABASE_URL"]
        }
      ]
    }
  ],
  "total_servers": 5,
  "total_templates": 2
}
```

**Error Cases**:
- Exit 1: Namespace not found (when specified)
- Exit 0: No templates installed (empty list)

### Examples

```bash
# List all servers
inskit mcp list

# List backend namespace only
inskit mcp list backend

# List with configuration status
inskit mcp list --status

# List MCP sets
inskit mcp list --sets

# Verbose output
inskit mcp list -v

# Global scope only
inskit mcp list --scope global
```

---

## 6. inskit mcp validate

Validate MCP server configurations and report issues.

### Syntax

```bash
inskit mcp validate [NAMESPACE] [OPTIONS]
```

### Arguments

- `[NAMESPACE]` (optional) - Validate only specific namespace

### Options

- `--check-commands` - Verify that MCP server commands exist in PATH

- `--check-credentials` - Verify all required credentials are configured

- `--check-tools` - Verify AI tool config files are valid

- `--all` - Run all checks (default)

- `--fix` - Attempt to fix issues automatically (e.g., add missing .env vars with prompts)

### Output

**Success (All Valid, Human-readable)**:
```
Validating MCP configurations...

✓ Credentials Check
  • All required environment variables configured
  • .instructionkit/.env is valid

✓ Command Check
  • All MCP server commands found in PATH

✓ AI Tool Config Check
  • Claude Desktop config is valid
  • Cursor config is valid

No issues found. All MCP servers are ready.
```

**With Issues (Human-readable)**:
```
Validating MCP configurations...

✗ Credentials Check
  backend.database:
    • Missing: DATABASE_URL

⚠ Command Check
  backend.custom-server:
    • Command 'custom-mcp-tool' not found in PATH
    • Install with: npm install -g custom-mcp-tool

✓ AI Tool Config Check
  • All configs valid

Summary:
  • 1 server missing credentials
  • 1 server missing commands
  • 3 servers ready

Fix issues:
  inskit mcp configure backend.database
  npm install -g custom-mcp-tool
```

**JSON Output**:
```json
{
  "status": "invalid",
  "checks": {
    "credentials": {
      "passed": false,
      "issues": [
        {
          "server": "backend.database",
          "missing_vars": ["DATABASE_URL"]
        }
      ]
    },
    "commands": {
      "passed": false,
      "issues": [
        {
          "server": "backend.custom-server",
          "command": "custom-mcp-tool",
          "found": false
        }
      ]
    },
    "tool_configs": {
      "passed": true,
      "issues": []
    }
  },
  "servers_ready": 3,
  "servers_invalid": 2
}
```

**Error Cases**:
- Exit 0: All validations pass
- Exit 1: Some validations fail (shown in output)
- Exit 2: Namespace not found

### Examples

```bash
# Validate all
inskit mcp validate

# Validate specific namespace
inskit mcp validate backend

# Check credentials only
inskit mcp validate --check-credentials

# Validate and attempt to fix
inskit mcp validate --fix
```

---

## 7. inskit mcp activate

Activate an MCP set (sync only servers in that set).

### Syntax

```bash
inskit mcp activate <NAMESPACE>.<SET> [OPTIONS]
```

### Arguments

- `<NAMESPACE>.<SET>` (required) - Fully qualified set name
  - Example: `backend.backend-dev`

### Options

- `--tool {claude|cursor|windsurf|all}` - Which AI tool(s) to sync (default: `all`)

- `--allow-partial` - Activate even if some servers are missing credentials

- `--deactivate` - Deactivate current set without activating a new one

### Output

**Success (Human-readable)**:
```
Activating MCP set: backend.backend-dev

Set includes 3 servers:
  ✓ backend.filesystem (configured)
  ✓ backend.github (configured)
  ⚠ backend.database (missing credentials: DATABASE_URL)

Syncing to AI tools...
  ✓ Claude Desktop: 2 servers synced, 1 skipped
  ✓ Cursor: 2 servers synced, 1 skipped

✓ Set 'backend.backend-dev' activated
  Active servers: filesystem, github

Previous set: personal.productivity (3 servers) → deactivated
```

**JSON Output**:
```json
{
  "status": "success",
  "activated_set": "backend.backend-dev",
  "servers_in_set": 3,
  "servers_synced": 2,
  "servers_skipped": 1,
  "tools_updated": ["claude", "cursor"],
  "previous_set": "personal.productivity",
  "activated_at": "2025-11-11T10:30:00Z"
}
```

**Error Cases**:
- Exit 1: Set not found
- Exit 2: All servers in set missing credentials (without `--allow-partial`)
- Exit 3: No AI tools detected

### Examples

```bash
# Activate set
inskit mcp activate backend.backend-dev

# Allow partial activation
inskit mcp activate backend.backend-dev --allow-partial

# Activate for Claude only
inskit mcp activate backend.backend-dev --tool claude

# Deactivate current set
inskit mcp activate --deactivate
```

---

## 8. inskit mcp update

Update MCP templates from their source repositories.

### Syntax

```bash
inskit mcp update [NAMESPACE] [OPTIONS]
```

### Arguments

- `[NAMESPACE]` (optional) - Update specific namespace
  - If omitted with `--all`, updates all templates
  - If omitted without `--all`, prompts for namespace

### Options

- `--all` - Update all installed templates

- `--preserve-credentials` - Keep local .env file unchanged (default: enabled)

- `--check-only` - Check for updates without applying them

- `--force` - Update even if local version is newer

### Output

**Success (Human-readable)**:
```
Updating MCP template: backend

Checking for updates...
  Current version: 1.0.0
  Latest version: 1.1.0

Changes:
  + Added server: redis
  ~ Modified server: database (added env var: DB_PORT)
  - Removed server: old-server

Updating...
  ✓ Downloaded latest version
  ✓ Updated templatekit.yaml
  ✓ Preserved credentials in .instructionkit/.env

New server 'redis' requires configuration:
  inskit mcp configure backend.redis

Modified server 'database' requires new variable:
  inskit mcp configure backend.database
```

**JSON Output**:
```json
{
  "status": "success",
  "namespace": "backend",
  "previous_version": "1.0.0",
  "new_version": "1.1.0",
  "changes": {
    "servers_added": ["redis"],
    "servers_modified": ["database"],
    "servers_removed": ["old-server"]
  },
  "requires_reconfiguration": ["redis", "database"]
}
```

**Error Cases**:
- Exit 0: Already up to date
- Exit 1: Namespace not found
- Exit 2: Failed to fetch updates
- Exit 3: Merge conflict (local modifications)

### Examples

```bash
# Update specific template
inskit mcp update backend

# Update all templates
inskit mcp update --all

# Check for updates
inskit mcp update backend --check-only

# Force update
inskit mcp update backend --force
```

---

## Common Patterns

### Chaining Commands

```bash
# Complete workflow
inskit mcp install https://github.com/company/tools --as backend && \
  inskit mcp configure backend.github && \
  inskit mcp sync --tool all && \
  inskit mcp activate backend.backend-dev
```

### Scripting with JSON Output

```bash
# Check if server is configured
inskit mcp list backend --json | jq -r '.templates[0].servers[] | select(.name=="github") | .status'

# Get all servers needing configuration
inskit mcp validate --json | jq -r '.checks.credentials.issues[].server'
```

### Non-Interactive CI/CD Usage

```bash
# Install and configure in CI
inskit mcp install $REPO_URL --as backend --force
GITHUB_PERSONAL_ACCESS_TOKEN=$CI_TOKEN inskit mcp configure backend.github --non-interactive
inskit mcp sync --tool all --no-backup
```

---

## Exit Codes

All commands follow consistent exit code conventions:

- `0` - Success
- `1` - General error (invalid arguments, resource not found)
- `2` - Validation error (invalid config, missing dependencies)
- `3` - Permission error (file system access denied)
- `4` - Network error (Git clone failed, unreachable repository)
- `130` - Interrupted by user (Ctrl+C)

---

## Testing Contract

Each command must have:

1. **Unit tests** for argument parsing and validation
2. **Integration tests** for happy path execution
3. **Error case tests** for each defined exit code
4. **JSON output tests** verifying schema compliance
5. **Cross-platform tests** on Windows, macOS, Linux
