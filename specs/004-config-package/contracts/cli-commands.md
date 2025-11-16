# CLI Command Contracts: Configuration Package System

**Feature**: 004-config-package
**Date**: 2025-11-14

## Overview

This document defines the command-line interface contracts for package management commands. All commands follow the AI Config Kit CLI conventions using Typer.

---

## Command Group: `aiconfig package`

Parent command group for all package operations.

**Synopsis**:
```bash
aiconfig package [COMMAND]
```

**Commands**:
- `install` - Install a package
- `create` - Create a package from current project
- `update` - Update installed packages
- `list` - List packages (installed or available)
- `uninstall` - Uninstall a package
- `info` - Show package information

---

## `aiconfig package install`

Install a package from a repository.

**Synopsis**:
```bash
aiconfig package install [OPTIONS] PACKAGE_SPEC
```

**Arguments**:
- `PACKAGE_SPEC` (required) - Package identifier in format `namespace/package[@version]`
  - Examples: `acme/productivity`, `acme/productivity@1.2.0`

**Options**:
- `--project PATH` - Project directory (default: current directory)
- `--interactive / --no-interactive` - Use interactive TUI for component selection (default: --no-interactive)
- `--conflict [skip|overwrite|rename|prompt]` - Conflict resolution strategy (default: prompt)
- `--scope [project]` - Installation scope (default: project) [global deferred]
- `--skip-credentials` - Skip credential prompting for MCP servers
- `--force` - Force installation even if already installed (reinstall)
- `--quiet` - Minimal output

**Exit Codes**:
- `0` - Success (all components installed)
- `1` - Partial success (some components installed, some failed)
- `2` - Failure (no components installed)
- `3` - Invalid arguments
- `4` - Package not found

**Output** (non-quiet):
```
📦 Installing: productivity-workflow v1.2.0

Components:
  ✓ 2 instructions installed
  🔌 Beeminder MCP server
    ? Enter BEEMINDER_AUTH_TOKEN: ********
    ✓ Credentials stored in .env
  ✓ 3 resources installed
  ⚠ 1 hook skipped (Cursor doesn't support hooks)

✅ Package installed successfully!

Installation summary:
  - Installed: 5 components
  - Skipped: 1 component
  - Failed: 0 components

Project: /Users/troy/projects/acme-web
Package: acme/productivity-workflow@1.2.0
```

**JSON Output** (`--json` flag):
```json
{
  "status": "success",
  "package": {
    "name": "productivity-workflow",
    "namespace": "acme",
    "version": "1.2.0"
  },
  "summary": {
    "installed": 5,
    "skipped": 1,
    "failed": 0
  },
  "components": [
    {
      "type": "instruction",
      "name": "beeminder-guide",
      "status": "installed",
      "path": ".claude/rules/beeminder-guide.md"
    },
    {
      "type": "mcp_server",
      "name": "beeminder",
      "status": "installed",
      "path": ".instructionkit/mcp/beeminder/"
    }
  ]
}
```

**Examples**:
```bash
# Install latest version with prompts
aiconfig package install acme/productivity

# Install specific version
aiconfig package install acme/productivity@1.2.0

# Install with interactive TUI
aiconfig package install --interactive acme/productivity

# Install with auto-overwrite conflicts
aiconfig package install --conflict overwrite acme/productivity

# Install without credential prompts (mark as pending)
aiconfig package install --skip-credentials acme/productivity
```

**Validation**:
- Package must exist in library (downloaded) or be valid Git URL
- Version must be valid semver if specified
- Project directory must be valid
- IDE must be detected in project

**Errors**:
- Package not found: `Error: Package 'acme/productivity' not found in library. Run 'aiconfig download acme/productivity' first.`
- Invalid version: `Error: Version '1.x' is not a valid semantic version.`
- No IDE detected: `Error: No supported IDE detected in /path/to/project`

---

## `aiconfig package create`

Create a package from current project components.

**Synopsis**:
```bash
aiconfig package create [OPTIONS]
```

**Options**:
- `--name TEXT` - Package name (default: interactive prompt)
- `--version TEXT` - Package version (default: 1.0.0)
- `--description TEXT` - Package description (default: interactive prompt)
- `--author TEXT` - Package author (default: git user.name)
- `--license TEXT` - Package license (default: MIT)
- `--output PATH` - Output directory (default: ./package-<name>/)
- `--interactive / --no-interactive` - Use interactive TUI for component selection (default: --interactive)
- `--include TEXT` - Include specific components (glob pattern, can be repeated)
- `--exclude TEXT` - Exclude components (glob pattern, can be repeated)
- `--scrub-secrets / --keep-secrets` - Auto-detect and template secrets (default: --scrub-secrets)
- `--force` - Overwrite existing package directory

**Exit Codes**:
- `0` - Success (package created)
- `1` - Failure (package creation failed)
- `2` - Cancelled by user
- `3` - Invalid arguments

**Output** (interactive):
```
🎁 Package Creator

Detected components:
  [x] beeminder MCP (npm package)
  [x] clickup MCP (npm package)
  [x] productivity instruction
  [x] sync-goals command
  [ ] logo.png resource
  [ ] brand-guide.pdf resource

? Select components to include: [2 selected]

MCP Servers:
? How to handle 'beeminder'?
  › npm install @modelcontextprotocol/server-beeminder
  [x] Include in package (recommended)

🔒 Secret Detection:
  BEEMINDER_AUTH_TOKEN → ${BEEMINDER_AUTH_TOKEN} (auto-templated)
  CLICKUP_API_KEY → ${CLICKUP_API_KEY} (auto-templated)
  CLICKUP_WORKSPACE → "workspace-123" (keep value) [y/N]?

Package Metadata:
? Package name: productivity-workflow
? Version: 1.0.0
? Description: Beeminder + ClickUp productivity tracking
? Author: Troy Larson
? License: MIT

✅ Package created: ./package-productivity-workflow/

Next steps:
  1. Review manifest: ./package-productivity-workflow/ai-config-kit-package.yaml
  2. Test installation: aiconfig package install ./package-productivity-workflow
  3. Publish to Git repository for sharing
```

**Package Structure Created**:
```
package-productivity-workflow/
├── ai-config-kit-package.yaml   # Package manifest
├── instructions/
│   └── productivity.md
├── mcp/
│   ├── beeminder/
│   │   └── config.json
│   └── clickup/
│       └── config.json
├── commands/
│   └── sync-goals.sh
└── README.md                    # Auto-generated documentation
```

**Examples**:
```bash
# Interactive mode (default)
aiconfig package create

# Non-interactive with flags
aiconfig package create --name my-package --version 1.0.0 \
  --description "My package" --no-interactive

# Include specific components
aiconfig package create --include "*.md" --include "mcp/beeminder/*"

# Keep secrets (don't template)
aiconfig package create --keep-secrets

# Output to specific directory
aiconfig package create --output /tmp/my-package
```

**Validation**:
- Must be run from project with .instructionkit directory
- Package name must be valid (lowercase, hyphens only)
- Version must be valid semver
- At least one component must be selected
- Output directory must not exist (unless --force)

**Errors**:
- Not in project: `Error: No .instructionkit directory found. Run from a project root.`
- No components: `Error: No components detected. Install some instructions or MCP servers first.`
- Invalid name: `Error: Package name 'My Package' is invalid. Use lowercase with hyphens.`
- Directory exists: `Error: Directory './package-my-package' already exists. Use --force to overwrite.`

---

## `aiconfig package update`

Update installed packages to newer versions.

**Synopsis**:
```bash
aiconfig package update [OPTIONS] [PACKAGE_SPEC]
```

**Arguments**:
- `PACKAGE_SPEC` (optional) - Specific package to update (default: all)

**Options**:
- `--project PATH` - Project directory (default: current directory)
- `--check-only` - Only check for updates, don't install
- `--to-version TEXT` - Update to specific version
- `--conflict [skip|overwrite|prompt]` - Conflict resolution (default: prompt)
- `--force` - Skip confirmation prompts
- `--dry-run` - Show what would be updated without making changes

**Exit Codes**:
- `0` - Success (packages updated or no updates available)
- `1` - Partial success (some updates failed)
- `2` - Failure (all updates failed)
- `3` - Invalid arguments

**Output** (check-only):
```
📦 Checking for updates...

Updates available:
  productivity-workflow: 1.2.0 → 1.3.0 (minor update)
    - Added: Todoist integration
    - Fixed: Beeminder sync race condition

  brand-kit: 2.0.0 → 3.0.0 (major update - breaking changes)
    ⚠ Breaking: Updated logo format from PNG to SVG
    - Added: New color palette
    - Removed: Legacy brand guidelines

No updates:
  code-standards: 1.5.2 (latest)

Run 'aiconfig package update' to install updates.
```

**Output** (updating):
```
📦 Updating packages...

Updating productivity-workflow (1.2.0 → 1.3.0):
  ✓ Updated instruction: beeminder-guide
  ✓ Added MCP server: todoist
  ? Enter TODOIST_API_TOKEN: ********
  ⚠ Conflict: commands/sync-goals.sh
    Your version: Modified (checksum: abc123)
    New version: Updated (checksum: def456)
    [K]eep yours, [A]ccept theirs, [D]iff, [S]kip? a
  ✓ Updated command: sync-goals

✅ 1 package updated successfully

Summary:
  - Updated: 1 package (4 components)
  - Skipped: 0 packages
  - Failed: 0 packages
```

**Examples**:
```bash
# Check for updates
aiconfig package update --check-only

# Update all packages
aiconfig package update

# Update specific package
aiconfig package update acme/productivity

# Update to specific version
aiconfig package update acme/productivity --to-version 1.3.0

# Update without prompts (use defaults)
aiconfig package update --force --conflict skip

# Dry run
aiconfig package update --dry-run
```

**Validation**:
- Project must have packages installed
- Package must exist in library if specified
- Target version must exist if specified

**Errors**:
- No packages: `Error: No packages installed in this project.`
- Package not found: `Error: Package 'acme/productivity' is not installed.`
- Version not found: `Error: Version '1.9.0' not found for 'acme/productivity'.`

---

## `aiconfig package list`

List packages (installed or available in library).

**Synopsis**:
```bash
aiconfig package list [OPTIONS] [FILTER]
```

**Arguments**:
- `FILTER` (optional) - Filter by package name pattern

**Options**:
- `--installed` - Show installed packages (default if in project)
- `--available` - Show available packages from library
- `--outdated` - Show only outdated installed packages
- `--project PATH` - Project directory (default: current directory)
- `--json` - Output as JSON
- `--verbose` - Show detailed information

**Exit Codes**:
- `0` - Success
- `1` - No packages found

**Output** (installed):
```
📦 Installed Packages (in /Users/troy/projects/acme-web):

  acme/productivity-workflow@1.2.0
    Description: Beeminder + ClickUp productivity tracking
    Installed: 2025-11-14 (2 weeks ago)
    Components: 2 instructions, 2 MCP servers, 1 command, 3 resources
    Status: Outdated (1.3.0 available)

  acme/brand-kit@2.0.0
    Description: ACME brand guidelines and assets
    Installed: 2025-10-01 (6 weeks ago)
    Components: 1 instruction, 5 resources
    Status: Up to date

Total: 2 packages (8 instructions, 2 MCP servers, 1 command, 8 resources)
```

**Output** (available):
```
📦 Available Packages (in library):

  acme/productivity-workflow
    Latest: 1.3.0
    Description: Beeminder + ClickUp productivity tracking
    Author: Troy Larson
    License: MIT

  acme/brand-kit
    Latest: 2.0.0
    Description: ACME brand guidelines and assets
    Author: ACME Corp
    License: Proprietary

  acme/code-standards
    Latest: 1.5.2
    Description: Code style and quality standards
    Author: ACME Corp
    License: MIT

Total: 3 packages available
```

**Examples**:
```bash
# List installed packages
aiconfig package list --installed

# List available packages
aiconfig package list --available

# List outdated packages
aiconfig package list --outdated

# Filter by pattern
aiconfig package list acme/*

# JSON output
aiconfig package list --json
```

---

## `aiconfig package uninstall`

Uninstall a package from the project.

**Synopsis**:
```bash
aiconfig package uninstall [OPTIONS] PACKAGE_SPEC
```

**Arguments**:
- `PACKAGE_SPEC` (required) - Package identifier (namespace/package)

**Options**:
- `--project PATH` - Project directory (default: current directory)
- `--keep-credentials` - Keep MCP credentials in .env file
- `--force` - Skip confirmation prompt
- `--dry-run` - Show what would be removed without removing

**Exit Codes**:
- `0` - Success
- `1` - Failure
- `2` - Cancelled by user
- `3` - Invalid arguments

**Output**:
```
📦 Uninstalling: acme/productivity-workflow@1.2.0

Components to remove:
  - .claude/rules/beeminder-guide.md
  - .claude/rules/productivity.md
  - .instructionkit/mcp/beeminder/config.json
  - .instructionkit/mcp/clickup/config.json
  - .claude/commands/sync-goals.sh
  - .instructionkit/resources/productivity-workflow/ (3 files)

? Remove MCP credentials from .env? [y/N]: n

✅ Package uninstalled

Summary:
  - Removed: 8 files
  - Kept: MCP credentials (in .env)
```

**Examples**:
```bash
# Uninstall with confirmation
aiconfig package uninstall acme/productivity

# Uninstall without prompts
aiconfig package uninstall acme/productivity --force

# Uninstall and remove credentials
aiconfig package uninstall acme/productivity --force

# Dry run
aiconfig package uninstall acme/productivity --dry-run
```

**Validation**:
- Package must be installed in project
- Project must exist

**Errors**:
- Not installed: `Error: Package 'acme/productivity' is not installed in this project.`
- No project: `Error: No .instructionkit directory found.`

---

## `aiconfig package info`

Show detailed information about a package.

**Synopsis**:
```bash
aiconfig package info [OPTIONS] PACKAGE_SPEC
```

**Arguments**:
- `PACKAGE_SPEC` (required) - Package identifier

**Options**:
- `--installed` - Show info for installed package (from project)
- `--available` - Show info for available package (from library)
- `--project PATH` - Project directory (default: current directory)
- `--json` - Output as JSON

**Exit Codes**:
- `0` - Success
- `1` - Package not found

**Output**:
```
📦 Package: acme/productivity-workflow

Version: 1.2.0
Description: Beeminder + ClickUp productivity tracking
Author: Troy Larson
License: MIT
Repository: https://github.com/acme/ai-configs

Components (8 total):

Instructions (2):
  - beeminder-guide: Guide for using Beeminder MCP
  - productivity: Productivity workflow overview

MCP Servers (2):
  - beeminder: Beeminder goal tracking
    Credentials: BEEMINDER_AUTH_TOKEN (required)
    IDE Support: claude_code, windsurf
  - clickup: ClickUp task management
    Credentials: CLICKUP_API_KEY (required), CLICKUP_WORKSPACE (required)
    IDE Support: claude_code, windsurf

Commands (1):
  - sync-goals: Sync Beeminder goals with ClickUp tasks
    IDE Support: claude_code

Resources (3):
  - workflow-diagram.png (1.2 MB): Workflow visualization
  - beeminder-setup.pdf (500 KB): Setup guide
  - examples.yaml (10 KB): Example configurations

Installation:
  aiconfig package install acme/productivity-workflow@1.2.0
```

**Examples**:
```bash
# Show available package info
aiconfig package info acme/productivity

# Show installed package info
aiconfig package info --installed acme/productivity

# JSON output
aiconfig package info --json acme/productivity
```

---

## `aiconfig scan`

Rebuild main registry from project trackers.

**Synopsis**:
```bash
aiconfig scan [OPTIONS]
```

**Options**:
- `--projects PATH` - Search for projects in directory (default: ~/)
- `--max-depth INT` - Maximum directory depth to search (default: 3)
- `--force` - Force full rebuild (ignore existing registry)
- `--quiet` - Minimal output

**Exit Codes**:
- `0` - Success
- `1` - Failure

**Output**:
```
🔍 Scanning for projects...

Found projects:
  /Users/troy/projects/acme-web
    - 2 packages, 5 instructions, 2 MCP servers
  /Users/troy/projects/acme-mobile
    - 1 package, 8 instructions, 1 MCP server
  /Users/troy/projects/client-site
    - 2 packages, 3 instructions, 3 MCP servers

✅ Registry updated

Summary:
  - Projects: 3
  - Packages: 5 total (3 unique)
  - Instructions: 16 total
  - MCP servers: 6 total

Registry: ~/.instructionkit/registry.json
```

**Examples**:
```bash
# Scan home directory
aiconfig scan

# Scan specific directory
aiconfig scan --projects /Users/troy/projects

# Deep scan
aiconfig scan --max-depth 5

# Force rebuild
aiconfig scan --force
```

**Validation**:
- Scan directory must exist
- Max depth must be positive integer

---

## Global Options

All commands support these global options:

- `--help` - Show command help
- `--version` - Show AI Config Kit version
- `--debug` - Enable debug logging
- `--no-color` - Disable colored output
- `--config PATH` - Custom config file location

---

## Exit Code Summary

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Partial success or general failure |
| 2 | User cancellation |
| 3 | Invalid arguments |
| 4 | Resource not found |

---

## JSON Output Format

All commands that support `--json` output use this structure:

```json
{
  "status": "success|partial|failure",
  "command": "package install",
  "data": {
    // Command-specific data
  },
  "errors": [
    {
      "type": "error_type",
      "message": "error message",
      "context": {}
    }
  ],
  "warnings": [
    {
      "type": "warning_type",
      "message": "warning message"
    }
  ]
}
```

---

## Error Handling

All errors follow this format:

```
Error: <message>

Suggestion: <helpful suggestion>

For more information, run with --debug
```

Examples:
```
Error: Package 'acme/productivity' not found in library.

Suggestion: Download it first with:
  aiconfig download https://github.com/acme/ai-configs

For more information, run with --debug
```

---

## Progress Indicators

For long-running operations, use Rich progress bars:

```
📦 Installing package...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:02

Components:
  ✓ Instructions  ━━━━━━━━━━━━━━━━━━━━━━━ 2/2
  ✓ MCP Servers   ━━━━━━━━━━━━━━━━━━━━━━━ 2/2
  ✓ Resources     ━━━━━━━━━━━━━━━━━━━━━━━ 3/3
```

---

## Interactive Prompts

Use Rich prompts with validation:

```python
from rich.prompt import Prompt, Confirm

# Text input with validation
name = Prompt.ask(
    "Package name",
    default="my-package",
    validator=validate_package_name
)

# Confirmation
if Confirm.ask("Continue with installation?"):
    install()

# Choice
strategy = Prompt.ask(
    "Conflict resolution",
    choices=["skip", "overwrite", "rename"],
    default="skip"
)
```

---

## Testing Strategy

### Unit Tests

- Command argument parsing
- Option validation
- Error message formatting
- JSON output structure

### Integration Tests

- End-to-end command execution
- File system operations
- Interactive prompt mocking
- Error handling flows

### Contract Tests

- CLI interface stability
- Backward compatibility
- Exit code consistency
- JSON schema validation
