# Advanced Usage

Advanced patterns and techniques for InstructionKit power users.

## Table of Contents

- [Scopes Deep Dive](#scopes-deep-dive)
- [Namespace Strategies](#namespace-strategies)
- [Conflict Resolution](#conflict-resolution)
- [Git References](#git-references)
- [Credential Management](#credential-management)
- [Multiple Environments](#multiple-environments)
- [CI/CD Integration](#cicd-integration)
- [Backup and Recovery](#backup-and-recovery)

---

## Scopes Deep Dive

### Understanding Project vs Global

**Project Scope:**
- Files: `<project>/.claude/rules/`, `.instructionkit/`
- Active: Only in that project directory
- Use: Team practices, project-specific patterns

**Global Scope:**
- Files: `~/.claude/rules/`, `~/.instructionkit/global/`
- Active: All projects on your machine
- Use: Personal tools, company-wide policies

### Mixing Scopes

Your IDE sees templates from **both** scopes simultaneously:

```bash
# Global templates (always available)
~/.claude/rules/
├── personal.productivity.md
├── company.security-policy.md
└── company.code-review.md

# Project templates (context-specific)
~/projects/backend-api/.claude/rules/
├── backend.api-patterns.md
├── backend.database-patterns.md
└── python.async-patterns.md
```

When working in `~/projects/backend-api/`, AI sees **all 6 templates**.

### Scope Precedence

When same-named templates exist in both scopes, **project wins**:

```bash
# Global
~/.claude/rules/standards.python.md

# Project (this one is used)
~/projects/my-app/.claude/rules/standards.python.md
```

---

## Namespace Strategies

### Company-Wide Namespaces

Use consistent namespaces across your organization:

```bash
# Convention: company.category
inskit template install <repo> --as acme.security
inskit template install <repo> --as acme.code-review
inskit template install <repo> --as acme.legal
```

### Team Namespaces

```bash
# Convention: team.category
inskit template install <repo> --as backend.api
inskit template install <repo> --as backend.database
inskit template install <repo> --as frontend.react
```

### Environment Namespaces

```bash
# Different configs per environment
cd ~/projects/app-dev
inskit mcp install <repo> --as dev

cd ~/projects/app-staging
inskit mcp install <repo> --as staging

cd ~/projects/app-prod
inskit mcp install <repo> --as prod
```

### Personal Namespaces

```bash
# Your personal tools (global scope)
inskit template install <repo> --as personal.shortcuts --scope global
inskit template install <repo> --as personal.templates --scope global
```

---

## Conflict Resolution

### Handling Name Conflicts

When installing templates with conflicting names, InstructionKit provides strategies:

**Skip (default):**
```bash
# Existing template kept, new template not installed
inskit template install <repo> --as namespace
# Conflict: namespace.standards.md already exists
# Action: Skip
```

**Rename:**
```bash
# New template gets suffix
inskit template install <repo> --as namespace --conflict rename
# Existing: namespace.standards.md
# New: namespace.standards-1.md
```

**Overwrite:**
```bash
# New template replaces existing
inskit template install <repo> --as namespace --conflict overwrite
# Existing: namespace.standards.md (deleted)
# New: namespace.standards.md (installed)
```

### Automatic Conflict Detection

InstructionKit checks for conflicts before installation:

```bash
inskit template install <repo> --as namespace

# Output:
# ⚠ Conflicts detected:
#   - namespace.python-standards.md (exists)
#   - namespace.security-checklist.md (exists)
#
# Choose resolution strategy:
#   [s]kip - Keep existing, don't install new (default)
#   [r]ename - Install with suffix (-1, -2, etc.)
#   [o]verwrite - Replace existing with new
#   [a]bort - Cancel installation
```

---

## Git References

### Using Branches

```bash
# Install from specific branch
inskit template install https://github.com/org/repo --as namespace --ref develop
inskit template install https://github.com/org/repo --as namespace --ref feature/new-templates
```

### Using Tags/Versions

```bash
# Pin to specific version
inskit template install https://github.com/org/repo --as namespace --ref v1.2.0

# Use semantic versioning
inskit template install https://github.com/org/repo --as namespace --ref v2.0.0
```

### Using Commits

```bash
# Pin to specific commit
inskit template install https://github.com/org/repo --as namespace --ref abc123def456
```

### Version Management

**Lock versions for stability:**
```bash
# Production: Use tagged releases
inskit template install <repo> --as prod --ref v1.0.0

# Development: Use latest from branch
inskit template install <repo> --as dev --ref main
```

**Update workflow:**
```bash
# Check current version
inskit template list namespace

# Update to latest
inskit template update namespace

# Or update to specific version
inskit template uninstall namespace
inskit template install <repo> --as namespace --ref v2.0.0
```

---

## Credential Management

### Environment Variable Patterns

**Recommended naming:**
```bash
# Pattern: <SYSTEM>_<PURPOSE>_<TYPE>
GITHUB_API_TOKEN=ghp_xxxxx
POSTGRES_CONNECTION_URL=postgresql://...
SLACK_BOT_TOKEN=xoxb-xxxxx
AWS_ACCESS_KEY_ID=AKIA...
```

### Credential Rotation

```bash
# Update credentials without reinstalling
inskit mcp configure backend.github

# Or update via environment
export GITHUB_TOKEN=ghp_new_token
inskit mcp configure backend --non-interactive
```

### Per-Environment Credentials

```bash
# Development
cd ~/projects/app-dev
export DATABASE_URL=postgresql://localhost/dev_db
inskit mcp configure dev --non-interactive

# Production
cd ~/projects/app-prod
export DATABASE_URL=postgresql://prod-host/prod_db
inskit mcp configure prod --non-interactive
```

### Credential Validation

```bash
# Check which credentials are configured
inskit mcp configure backend --show-current

# Validate all credentials
inskit mcp validate

# Validate specific namespace
inskit mcp validate backend
```

---

## Multiple Environments

### Pattern 1: Separate Projects

```bash
# One project per environment
~/projects/
├── app-dev/          # Development environment
├── app-staging/      # Staging environment
└── app-prod/         # Production environment

# Each has own templates and credentials
cd ~/projects/app-dev
inskit mcp install <repo> --as dev
inskit mcp configure dev

cd ~/projects/app-staging
inskit mcp install <repo> --as staging
inskit mcp configure staging
```

### Pattern 2: Same Project, Different Namespaces

```bash
# Single project, multiple MCP configurations
cd ~/projects/app

# Install environment-specific configs
inskit mcp install <repo-dev> --as dev
inskit mcp install <repo-staging> --as staging
inskit mcp install <repo-prod> --as prod

# Configure separately
inskit mcp configure dev
inskit mcp configure staging
inskit mcp configure prod

# Sync specific environment
inskit mcp sync --tool claude  # Syncs all configured servers
```

### Pattern 3: Global + Project Mix

```bash
# Global: Company-wide tools (same everywhere)
inskit template install <company-tools> --as company --scope global

# Project: Environment-specific
cd ~/projects/app-dev
inskit mcp install <dev-mcp> --as dev

cd ~/projects/app-prod
inskit mcp install <prod-mcp> --as prod
```

---

## CI/CD Integration

### Non-Interactive Installation

```bash
#!/bin/bash
# setup.sh - Automated template installation

# Set credentials from CI environment
export GITHUB_TOKEN="${CI_GITHUB_TOKEN}"
export DATABASE_URL="${CI_DATABASE_URL}"

# Install templates
inskit template install https://github.com/company/standards --as company --force

# Install MCP servers
inskit mcp install https://github.com/company/mcp-servers --as backend --force

# Configure credentials (non-interactive)
inskit mcp configure backend --non-interactive

# Sync to tools
inskit mcp sync --tool all
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.11

# Install InstructionKit
RUN pip install instructionkit

# Copy credentials from build args
ARG GITHUB_TOKEN
ARG DATABASE_URL
ENV GITHUB_TOKEN=${GITHUB_TOKEN}
ENV DATABASE_URL=${DATABASE_URL}

# Install templates
RUN inskit template install https://github.com/company/standards --as company --force

# Install and configure MCP
RUN inskit mcp install https://github.com/company/mcp --as backend --force && \
    inskit mcp configure backend --non-interactive

WORKDIR /app
```

### GitHub Actions

```yaml
# .github/workflows/setup-templates.yml
name: Setup Templates

on: [push]

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install InstructionKit
        run: pip install instructionkit

      - name: Install Templates
        run: |
          inskit template install https://github.com/company/standards --as company --force

      - name: Configure MCP
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          inskit mcp install https://github.com/company/mcp --as backend --force
          inskit mcp configure backend --non-interactive
```

---

## Backup and Recovery

### Automatic Backups

InstructionKit automatically backs up config files before syncing:

```bash
# Backup files created:
~/Library/Application Support/Claude/claude_desktop_config.json.bak
~/Library/Application Support/Cursor/User/globalStorage/mcp_config.json.bak
```

### Manual Backup

```bash
# Before major changes
cp ~/.claude/rules ~/.claude/rules.backup
cp .instructionkit .instructionkit.backup

# Or use tar
tar -czf instructionkit-backup-$(date +%Y%m%d).tar.gz .instructionkit ~/.claude/rules
```

### Recovery

```bash
# Restore from automatic backup
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json.bak \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restore from manual backup
cp -r ~/.claude/rules.backup ~/.claude/rules
cp -r .instructionkit.backup .instructionkit
```

### Disaster Recovery

```bash
# Complete fresh start
rm -rf ~/.instructionkit
rm -rf .instructionkit
rm -rf ~/.claude/rules/*

# Reinstall everything
inskit template install <repo1> --as namespace1
inskit template install <repo2> --as namespace2
inskit mcp install <mcp-repo> --as backend
inskit mcp configure backend
inskit mcp sync --tool all
```

---

## Tips and Tricks

### List All Installed Content

```bash
# Templates
find ~/.claude/rules -type f -name "*.md" | sort
find .claude/rules -type f -name "*.md" | sort

# MCP installations
inskit mcp list --json | jq .
```

### Bulk Operations

```bash
# Update all templates and MCP configs
inskit template update --all
inskit mcp update --all

# Sync to all tools
inskit mcp sync --tool all
```

### Debugging

```bash
# Enable debug logging
export LOGLEVEL=DEBUG
inskit mcp sync --tool all

# Dry run (preview changes)
inskit mcp sync --tool all --dry-run

# Check what's installed
inskit template list
inskit mcp list
inskit tools
```

### Performance

```bash
# Skip backups for faster syncing
inskit mcp sync --tool claude --no-backup

# Use specific tool instead of "all"
inskit mcp sync --tool claude
```

---

**[← Back to Main Documentation](../README.md)**
