# Quickstart Guide: MCP Server Configuration Management

**Feature**: 003-mcp-server-management
**For**: Developers and team leads
**Time to Complete**: 5-10 minutes

## What You'll Learn

- Install MCP server configurations from a template repository
- Configure credentials securely
- Sync MCP servers to your AI coding tools
- Switch between different MCP server sets for different workflows

## Prerequisites

- InstructionKit installed (`pip install instructionkit`)
- At least one AI coding tool installed (Claude Desktop, Cursor, or Windsurf)
- Access to a template repository with MCP server definitions (or use the example below)

## Quick Start (30 Seconds)

```bash
# 1. Install MCP template from repository
inskit mcp install https://github.com/company/backend-tools --as backend

# 2. Configure credentials
inskit mcp configure backend.github

# 3. Sync to all AI tools
inskit mcp sync --tool all

# Done! Your AI tools now have MCP servers configured
```

## Step-by-Step Walkthrough

### Step 1: Install MCP Configuration Template

Install MCP server definitions from your team's template repository:

```bash
inskit mcp install https://github.com/company/backend-tools --as backend
```

**What this does**:
- Clones the repository to `~/.instructionkit/library/backend/`
- Parses MCP server definitions from `templatekit.yaml`
- Identifies which servers need credential configuration

**Output**:
```
✓ Cloning repository...
✓ Parsing templatekit.yaml...
✓ Found 3 MCP servers: filesystem, github, database
✓ Found 2 MCP sets: backend-dev, backend-prod

Next steps:
  1. Configure credentials: inskit mcp configure backend.github
  2. List servers: inskit mcp list backend
```

---

### Step 2: See What's Available

List all installed MCP servers and their configuration status:

```bash
inskit mcp list --status
```

**Output**:
```
MCP Servers:

backend (3 servers) - Backend Development Standards
  ✓ filesystem         [configured]
  ⚠ github            [needs configuration: GITHUB_PERSONAL_ACCESS_TOKEN]
  ⚠ database          [needs configuration: DATABASE_URL]

Total: 3 MCP servers
  • 1 configured
  • 2 need configuration
```

---

### Step 3: Configure Credentials

Provide required credentials for MCP servers that need them:

```bash
inskit mcp configure backend.github
```

**Interactive Prompts**:
```
Configuring MCP server: backend.github

Required environment variables:
  1. GITHUB_PERSONAL_ACCESS_TOKEN

Enter GITHUB_PERSONAL_ACCESS_TOKEN: ****************************

✓ Credentials saved to: .instructionkit/.env
✓ Server 'backend.github' is now configured
```

**Where credentials are stored**:
- Project-scoped: `<project-root>/.instructionkit/.env` (gitignored automatically)
- Global-scoped: `~/.instructionkit/global/.env`

**Repeat for other servers**:
```bash
inskit mcp configure backend.database
```

---

### Step 4: Validate Configuration

Check that everything is set up correctly:

```bash
inskit mcp validate
```

**Output**:
```
Validating MCP configurations...

✓ Credentials Check
  • All required environment variables configured

✓ Command Check
  • All MCP server commands found in PATH

✓ AI Tool Config Check
  • Claude Desktop detected
  • Cursor detected

No issues found. All MCP servers are ready.
```

---

### Step 5: Sync to AI Tools

Synchronize your configured MCP servers to your AI coding tools:

```bash
inskit mcp sync --tool all
```

**Output**:
```
Syncing MCP servers...

✓ Detected Claude Desktop
✓ Detected Cursor

Syncing to Claude Desktop:
  ✓ backend.github (configured)
  ✓ backend.filesystem (configured)
  ✓ backend.database (configured)

Syncing to Cursor:
  ✓ backend.github (configured)
  ✓ backend.filesystem (configured)
  ✓ backend.database (configured)

Summary:
  • 3 servers synced successfully
  • 2 tools updated
  • Backups created

Your AI tools are now configured!
```

**What this does**:
- Reads configured MCP servers from library
- Resolves environment variables from `.instructionkit/.env`
- Updates AI tool config files (e.g., `~/.claude/claude_desktop_config.json`)
- Creates backups before modification
- Preserves other settings in config files

---

### Step 6: Use MCP Sets (Optional)

If your template defines MCP sets, you can activate different groups of servers for different workflows:

```bash
# List available sets
inskit mcp list --sets
```

**Output**:
```
MCP Sets:

backend.backend-dev
  Description: MCP servers for backend development
  Servers: filesystem, github, database (3)

backend.backend-prod
  Description: Production backend servers (read-only)
  Servers: filesystem, github (2)
```

**Activate a set**:
```bash
inskit mcp activate backend.backend-dev
```

**Output**:
```
Activating MCP set: backend.backend-dev

Set includes 3 servers:
  ✓ backend.filesystem
  ✓ backend.github
  ✓ backend.database

Syncing to AI tools...
  ✓ Claude Desktop: 3 servers synced
  ✓ Cursor: 3 servers synced

✓ Set 'backend.backend-dev' activated
```

**Switch to a different set**:
```bash
inskit mcp activate backend.backend-prod
```

---

## Common Workflows

### New Team Member Onboarding

```bash
# 1. Clone project repository
git clone https://github.com/company/project
cd project

# 2. Install team's MCP configuration
inskit mcp install https://github.com/company/mcp-configs --as company

# 3. Configure credentials (interactive prompts)
inskit mcp configure company.github
inskit mcp configure company.slack
inskit mcp configure company.jira

# 4. Sync to tools
inskit mcp sync --tool all

# 5. Activate development set
inskit mcp activate company.development

# Ready to code!
```

---

### Switching Between Projects

```bash
# Working on backend project
cd ~/projects/backend-api
inskit mcp activate backend.backend-dev

# Switch to frontend project
cd ~/projects/frontend-app
inskit mcp activate frontend.frontend-dev

# MCP servers automatically update in your AI tools!
```

---

### Adding Personal Productivity Tools

```bash
# Install personal tools globally (available in all projects)
inskit mcp install https://github.com/me/personal-tools --as personal --scope global

# Configure once
inskit mcp configure personal.slack
inskit mcp configure personal.time-tracker

# Sync with project tools
inskit mcp sync --tool all --scope both
# Both global (personal) and project-specific MCP servers are now active
```

---

### Updating When Template Changes

```bash
# Team lead updates template repository with new servers
# You pull the changes:

inskit mcp update backend
```

**Output**:
```
Updating MCP template: backend

Changes:
  + Added server: redis
  ~ Modified server: database (added env var: DB_PORT)

✓ Updated to version 1.1.0
✓ Preserved existing credentials

New server 'redis' requires configuration:
  inskit mcp configure backend.redis
```

---

### CI/CD Pipeline Integration

```bash
#!/bin/bash
# .github/workflows/setup-mcp.sh

set -e

# Install MCP configuration
inskit mcp install https://github.com/company/ci-tools --as ci --force

# Configure from CI secrets (non-interactive)
export GITHUB_PERSONAL_ACCESS_TOKEN="${CI_GITHUB_TOKEN}"
export DATABASE_URL="${CI_DATABASE_URL}"

inskit mcp configure ci.github --non-interactive
inskit mcp configure ci.database --non-interactive

# Sync to tools
inskit mcp sync --tool all --no-backup

echo "MCP servers configured for CI"
```

---

## Troubleshooting

### MCP Server Not Showing in AI Tool

**Problem**: Configured server doesn't appear in AI tool

**Solution**:
```bash
# 1. Validate configuration
inskit mcp validate

# 2. Check sync status
inskit mcp list --status

# 3. Re-sync
inskit mcp sync --tool all

# 4. Restart AI tool (required for config reload)
```

---

### Missing Credentials Error

**Problem**: `inskit mcp sync` reports missing credentials

**Solution**:
```bash
# 1. List servers needing configuration
inskit mcp list --status

# 2. Configure missing servers
inskit mcp configure <namespace>.<server>

# 3. Sync again
inskit mcp sync --tool all
```

---

### Command Not Found in PATH

**Problem**: `inskit mcp validate` reports command not found

**Solution**:
```bash
# Install the missing MCP server package
# Example for GitHub MCP server:
pip install mcp-server-github

# Or with npm:
npm install -g @modelcontextprotocol/server-github

# Verify installation
which mcp-server-github

# Validate again
inskit mcp validate --check-commands
```

---

### Credential File Conflicts (Git)

**Problem**: Accidentally committed `.instructionkit/.env` with secrets

**Solution**:
```bash
# 1. Remove from Git history (if just committed)
git reset HEAD .instructionkit/.env
git checkout -- .instructionkit/.env

# 2. Ensure .gitignore is correct
echo ".instructionkit/.env" >> .gitignore
git add .gitignore
git commit -m "chore: ensure .env is gitignored"

# 3. If already pushed, rotate credentials immediately
# Then reconfigure:
inskit mcp configure <namespace>.<server>
```

---

### Sync to Specific Tool Only

**Problem**: Want to sync to Claude but not Cursor

**Solution**:
```bash
# Sync to Claude only
inskit mcp sync --tool claude

# Sync to multiple specific tools
inskit mcp sync --tool claude
inskit mcp sync --tool windsurf
```

---

## Advanced Usage

### Custom Template Repository Structure

Create your own template repository with `templatekit.yaml`:

```yaml
name: My Team's MCP Servers
version: 1.0.0
description: Backend development MCP configurations

mcp_servers:
  - name: github
    command: uvx
    args: ["mcp-server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: null  # User must provide

  - name: filesystem
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/code"]
    env: {}  # No credentials needed

  - name: database
    command: python
    args: ["-m", "mcp_server_postgres"]
    env:
      DATABASE_URL: null  # User must provide
      DB_POOL_SIZE: "10"  # Default value

mcp_sets:
  - name: backend-dev
    description: "Development environment"
    servers: ["filesystem", "github", "database"]

  - name: backend-prod
    description: "Production environment (read-only)"
    servers: ["filesystem", "github"]
```

**Install your custom template**:
```bash
inskit mcp install ./path/to/your/repo --as myteam
# or
inskit mcp install https://github.com/you/mcp-templates --as myteam
```

---

### Scripting with JSON Output

Get machine-readable output for scripts:

```bash
# Check if server is configured
CONFIGURED=$(inskit mcp list backend --json | jq -r '.templates[0].servers[] | select(.name=="github") | .status')

if [ "$CONFIGURED" = "configured" ]; then
  echo "GitHub server is configured"
else
  echo "Need to configure GitHub server"
  inskit mcp configure backend.github
fi
```

**List all servers needing configuration**:
```bash
inskit mcp validate --json | jq -r '.checks.credentials.issues[].server'
```

---

### Project vs Global Scoping

**Project-scoped** (default): MCP servers available only in this project
```bash
inskit mcp install <url> --as project-specific --scope project
```

**Global-scoped**: MCP servers available in all projects
```bash
inskit mcp install <url> --as personal-tools --scope global
```

**Merge both scopes**:
```bash
inskit mcp sync --tool all --scope both
# Project-scoped servers take precedence if names conflict
```

---

## Next Steps

### Learn More

- **View all MCP commands**: `inskit mcp --help`
- **Command-specific help**: `inskit mcp <command> --help`
- **See examples**: `inskit mcp <command> --help` (includes examples section)

### Create Your Own Templates

1. Create a repository with `templatekit.yaml`
2. Define your team's MCP servers and sets
3. Share the repository URL with your team
4. Team members: `inskit mcp install <your-repo-url> --as <namespace>`

### Integrate with Team Workflow

- Add MCP template installation to project README
- Include credential configuration in onboarding docs
- Set up CI/CD scripts for automated testing
- Create different MCP sets for dev/staging/prod environments

---

## Summary

**What we covered**:
1. ✅ Install MCP templates from repositories
2. ✅ Configure credentials securely in `.env` files
3. ✅ Sync MCP servers to AI coding tools
4. ✅ Use MCP sets for workflow-based server activation
5. ✅ Update templates when changes are made
6. ✅ Troubleshoot common issues

**Key commands to remember**:
```bash
inskit mcp install <url> --as <namespace>  # Install template
inskit mcp configure <namespace>.<server>  # Set credentials
inskit mcp sync --tool all                 # Sync to AI tools
inskit mcp list --status                   # Check status
inskit mcp validate                        # Validate setup
```

**You're ready to use MCP server management!** 🚀
