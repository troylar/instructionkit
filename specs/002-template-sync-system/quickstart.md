# Quickstart Guide: Template Sync System

**Last Updated**: 2025-11-09
**Feature**: Template Sync System

This guide will have you up and running with template repositories in under 5 minutes.

---

## What Are Templates?

Templates are reusable project artifacts that keep your team consistent:
- **Commands**: Like `/test` or `/deploy` that work across all projects
- **Coding Standards**: Style guides, patterns, best practices
- **Skills**: AI assistant capabilities
- **Guidelines**: Documentation templates, checklists

Unlike instructions (which configure AI behavior once), templates are actively synchronized—when your team updates standards, you pull the latest version.

---

## Prerequisites

- InstructionKit installed (`pip install instructionkit`)
- Git configured with credentials (for private repositories)
- An AI coding assistant (Cursor, Claude Code, Windsurf, or GitHub Copilot)

---

## Quick Start (5 Minutes)

### Step 1: Install Your First Template Repository

```bash
# Navigate to your project
cd ~/projects/my-api

# Install team's template repository
inskit template install https://github.com/myteam/coding-standards
```

**What happens:**
```
Cloning repository from github.com/myteam/coding-standards... ✓ Repository cloned

Installing python-style-guide... ✓
Installing test-command... ✓
Installing deploy-command... ✓
Installing pr-checklist... ✓

┌─────────────────────────────────────┐
│       Installation Summary          │
├──────────┬───────┬──────────────────┤
│ Status   │ Count │ Templates        │
├──────────┼───────┼──────────────────┤
│ ✓ Installed │ 4  │ python-style-... │
└──────────┴───────┴──────────────────┘

✓ Installation complete
```

### Step 2: Verify Installation

```bash
# List installed templates
inskit template list
```

**Output:**
```
Installed Templates (Project Scope)

Repository: myteam/coding-standards (v1.2.0)
┌──────────────────────┬─────────┬──────────────┐
│ Template             │ IDE     │ Installed    │
├──────────────────────┼─────────┼──────────────┤
│ python-style-guide   │ cursor  │ 2025-11-09   │
│ test-command         │ cursor  │ 2025-11-09   │
│ deploy-command       │ cursor  │ 2025-11-09   │
│ pr-checklist         │ cursor  │ 2025-11-09   │
└──────────────────────┴─────────┴──────────────┘

Total: 4 templates from 1 repository
```

### Step 3: Use Templates in Your IDE

Open your AI coding assistant (Cursor, Claude Code, etc.) and:

```
Type: /test

The /test command runs your team's standard test suite with coverage reporting.
```

Your team's standardized commands now work in this project!

### Step 4: Update Templates When Team Standards Change

```bash
# Pull latest template updates
inskit template update myteam/coding-standards
```

**If no conflicts:**
```
Checking for updates to myteam/coding-standards... ✓
Found updates for 1 template

Updating test-command... ✓

✓ Updated 1 template
```

**If local modifications conflict:**
```
⚠️  Conflict detected for 'test-command'
Local file modified on 2025-11-05
Remote updated on 2025-11-08

Choose action:
  [K]eep local version
  [O]verwrite with remote
  [R]ename local and install remote
Your choice [k]: o

Updating test-command... ✓
```

---

## Common Workflows

### Install Templates to Multiple Projects

```bash
# Install to project A
cd ~/projects/api-gateway
inskit template install https://github.com/myteam/coding-standards

# Install to project B
cd ~/projects/auth-service
inskit template install https://github.com/myteam/coding-standards

# Both projects now have identical commands and standards
```

### Install Global Templates (Apply to All Projects)

```bash
# Install your personal templates globally
inskit template install https://github.com/me/personal-templates --scope global

# These templates now available in any project
# Project-specific templates override global when both exist
```

### Selective Template Installation

If you only need specific templates from a repository:

```bash
inskit template install https://github.com/team/full-stack-templates --select
```

**Interactive selection:**
```
Available templates in team/full-stack-templates:

[ ] backend-testing
[✓] frontend-testing    ← Select with Space
[ ] database-migrations
[✓] deploy-frontend     ← Select what you need
[✓] pr-checklist

Press Enter to install selected templates
```

### Install Template Bundles

Repositories can define bundles (preset collections):

```bash
inskit template install https://github.com/team/templates --bundle python-essentials
```

This installs the "python-essentials" bundle (e.g., style guide + test command + lint command) without manually selecting each template.

---

## Working with Private Repositories

### HTTPS Authentication

```bash
# Configure Git credential helper (one-time setup)
git config --global credential.helper store

# Manually clone the private repo once to cache credentials
git clone https://github.com/myteam/private-templates /tmp/test
# Enter username and password when prompted
# Credentials are now cached

# Now InstructionKit can access private repos
inskit template install https://github.com/myteam/private-templates
```

### SSH Authentication

```bash
# Use SSH URL instead of HTTPS
inskit template install git@github.com:myteam/private-templates.git

# Requires SSH key configured with GitHub:
# 1. ssh-keygen -t ed25519 -C "your_email@example.com"
# 2. cat ~/.ssh/id_ed25519.pub
# 3. Add public key to GitHub Settings → SSH Keys
```

---

## Managing Templates

### List All Installed Templates

```bash
# All templates (project + global)
inskit template list

# Only project-level
inskit template list --scope project

# Only global
inskit template list --scope global

# From specific repository
inskit template list --repo myteam/coding-standards

# JSON output for scripting
inskit template list --format json
```

### Update All Templates

```bash
# Update all installed template repositories
inskit template update --all

# Update specific repository
inskit template update myteam/coding-standards

# Preview updates without applying
inskit template update --all --dry-run
```

### Uninstall Templates

```bash
# Uninstall entire repository (with confirmation)
inskit template uninstall myteam/coding-standards

# Skip confirmation
inskit template uninstall myteam/coding-standards --force

# Uninstall specific template only
inskit template uninstall myteam/coding-standards --template test-command

# Remove from tracking but keep files on disk
inskit template uninstall myteam/coding-standards --keep-files
```

---

## Creating Your Own Template Repository

### 1. Repository Structure

```
my-template-repo/
├── templatekit.yaml          # Manifest (required)
└── templates/
    ├── commands/
    │   ├── test.md           # Command templates
    │   └── deploy.md
    └── standards/
        ├── python-style.md   # Guidelines
        └── pr-checklist.md
```

### 2. Create Manifest (`templatekit.yaml`)

```yaml
name: "My Team Templates"
description: "Coding standards and commands for our team"
version: "1.0.0"
author: "Platform Team"

templates:
  - name: python-style-guide
    description: "Python coding style and conventions"
    files:
      - path: templates/standards/python-style.md
        ide: all  # Works for all IDEs
    tags: [python, style, standards]

  - name: test-command
    description: "Standard testing command"
    files:
      - path: templates/commands/test.md
        ide: all
    tags: [testing, command]
    dependencies: [python-style-guide]  # Requires style guide

bundles:
  - name: python-essentials
    description: "Essential Python templates"
    templates: [python-style-guide, test-command]
    tags: [python, essential]
```

### 3. Create Template Files

Example: `templates/commands/test.md`

```markdown
---
name: test-command
description: Run all tests with coverage
type: command
shortcut: /test
---

# Test Command

Runs the full test suite with coverage reporting.

## Usage

Type `/test` to run all tests.

## Implementation

```bash
pytest tests/ --cov=src --cov-report=term-missing
```
```

### 4. Publish and Install

```bash
# Push to GitHub
git init
git add .
git commit -m "Initial template repository"
git remote add origin https://github.com/myteam/templates
git push -u origin main

# Install to your project
cd ~/projects/my-project
inskit template install https://github.com/myteam/templates
```

---

## Cross-IDE Support

Templates automatically work with multiple IDEs:

| IDE | Template Location | Auto-Detected |
|-----|-------------------|---------------|
| Cursor | `.cursor/rules/*.md` | Yes (if `.cursor/` exists) |
| Claude Code | `.claude/rules/*.md` | Yes (if `.claude/` exists) |
| Windsurf | `.windsurf/rules/*.md` | Yes (if `.windsurf/` exists) |
| GitHub Copilot | `.github/instructions/*.md` | Yes (if `.github/copilot/` exists) |

**Example**: Install templates once, use them in any IDE you switch to.

---

## Conflict Resolution

When updating templates, you might modify local files. Here's how conflicts are handled:

### Scenario 1: Safe Update (No Local Changes)

```
Local file unchanged since installation
Remote has updates

→ Auto-update with no prompt
```

### Scenario 2: Local Modifications Only

```
You modified the local file
Remote unchanged

→ Keep your local version, skip update
```

### Scenario 3: Both Changed (Conflict)

```
You modified the local file
Remote also has updates

→ Prompt you to choose:
  [K]eep local (ignore remote update)
  [O]verwrite with remote (discard your changes)
  [R]ename local, install remote (keep both)
```

**Best Practice**: Use `[R]ename` to keep both versions, then manually merge if needed.

---

## Troubleshooting

### "Authentication failed" Error

**Problem**: Can't access private repository

**Solution**:
```bash
# HTTPS: Configure credential helper
git config --global credential.helper store
git clone https://github.com/org/repo /tmp/test  # Cache credentials

# SSH: Add SSH key to GitHub
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub  # Add to GitHub
```

### "No IDE detected" Warning

**Problem**: System can't find AI coding assistant

**Solution**: Install templates anyway (they'll work when IDE is set up):
```bash
inskit template install <repo-url>  # Still installs to default locations
```

### Templates Not Showing in IDE

**Problem**: Installed templates but IDE doesn't see them

**Solution**:
1. Restart your IDE
2. Check installation path:
   ```bash
   inskit template list --verbose  # Shows full paths
   ```
3. Verify IDE-specific directory exists (e.g., `.cursor/rules/`)

### Repository Clone Failed

**Problem**: Network or repository accessibility issue

**Solution**:
```bash
# Verify URL is correct
git clone <repo-url> /tmp/test

# Check network connectivity
ping github.com

# Verify repository exists and you have access
```

---

## Next Steps

Now that you've installed your first templates:

1. **Explore the templates** in your project's `.cursor/rules/` (or equivalent) directory
2. **Try the commands** in your AI coding assistant
3. **Create your own template repository** for your team
4. **Set up CI/CD** to validate template repositories on commit

---

## Additional Resources

- **Full CLI Reference**: Run `inskit template --help`
- **Template Manifest Schema**: See example repositories
- **InstructionKit Docs**: https://docs.instructionkit.dev/templates/
- **GitHub Discussions**: https://github.com/troylar/instructionkit/discussions

---

## Quick Reference Card

```bash
# Installation
inskit template install <repo-url>                    # Install to project
inskit template install <repo-url> --scope global     # Install globally
inskit template install <repo-url> --select           # Choose templates

# Management
inskit template list                                  # List all
inskit template list --format json                    # JSON output
inskit template update --all                          # Update all
inskit template update <repo-name>                    # Update one
inskit template uninstall <repo-name>                 # Remove templates

# Conflict handling during update
# [K]eep local | [O]verwrite with remote | [R]ename and keep both
```

---

Happy templating! 🚀
