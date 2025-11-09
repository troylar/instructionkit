<div align="center">

# 🎯 InstructionKit

**Distribute and sync coding standards, commands, and IDE configurations across your team**

[![CI](https://github.com/troylar/instructionkit/actions/workflows/ci.yml/badge.svg)](https://github.com/troylar/instructionkit/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/troylar/instructionkit/branch/main/graph/badge.svg)](https://codecov.io/gh/troylar/instructionkit)
[![PyPI version](https://img.shields.io/pypi/v/instructionkit.svg)](https://pypi.org/project/instructionkit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Works with:** Claude Code • Cursor • GitHub Copilot • Windsurf

</div>

---

## What is InstructionKit?

A CLI tool for **distributing IDE-specific content** to your team. Create a Git repository with your coding standards, slash commands, or IDE configurations, and your team can install and stay synchronized with a single command.

**Perfect for:**
- 🏢 **Teams** - Share coding standards, security policies, and custom workflows
- 🔄 **Consistency** - Everyone uses the same commands and follows the same practices
- 📦 **Multi-repo** - Combine company standards + team practices + personal tools
- ✅ **Safety** - Built-in validation, automatic backups, conflict resolution

> **Note:** Commands use `inskit` (short for InstructionKit)

---

## 🚀 Quick Start

### Option 1: Try the Official Examples (30 seconds)

```bash
# Install
pip install instructionkit

# Create your first template repository (includes Python/React/Testing examples)
inskit template init my-standards

# Test it locally
cd my-standards
inskit template install . --as demo

# Your IDE now has coding standards in .claude/rules/demo.*
```

### Option 2: Use an Existing Repository (60 seconds)

```bash
# Install
pip install instructionkit

# Install from any Git repository
inskit template install https://github.com/yourcompany/standards --as company

# That's it! Templates are now in your IDE
# .claude/rules/company.*.md
# .claude/commands/company.*.md (accessible as /company.command-name)
```

---

## What Can You Distribute?

InstructionKit distributes **any IDE-specific content** from Git repositories:

| Type | Example Files | What It Does |
|------|--------------|--------------|
| **Coding Standards** | `python-standards.md`<br>`security-checklist.md` | Appears in IDE as instructions/rules |
| **Slash Commands** | `test-api.md`<br>`review-pr.md` | Available as `/test-api`, `/review-pr` commands |
| **IDE Hooks** | `pre-prompt.md`<br>`post-prompt.md` | Automation hooks for context injection |
| **Anything Else** | Configuration, snippets, templates | Any content for `.claude/`, `.cursor/`, etc. |

**How it works:**
1. Create a Git repository with `templatekit.yaml` + your content
2. Team members run: `inskit template install <repo-url> --as <namespace>`
3. Content appears in their IDE with namespace prefix (e.g., `company.security-rules.md`)
4. Update anytime with: `inskit template update <namespace>`

---

## Core Concepts

### Repositories
A Git repository containing a `templatekit.yaml` manifest file that describes your templates.

```yaml
# templatekit.yaml
name: ACME Engineering Standards
version: 1.0.0

templates:
  - name: python-standards
    description: Python coding standards
    ide: claude
    files:
      - path: .claude/rules/python-standards.md
        type: instruction
    tags: [python, standards]
```

### Templates
Individual pieces of content (rules, commands, hooks) defined in `templatekit.yaml`.

### Namespaces
Each repository gets a namespace to prevent conflicts. When you install with `--as acme`, all templates are prefixed: `acme.python-standards.md`, `acme.security-rules.md`. Commands become `/acme.test-api`, etc.

**Why namespaces?**
- Install templates from multiple sources without conflicts
- Company standards + team practices + personal tools all coexist
- Clear ownership (know which repo each template came from)

### Installation Scopes
- **Project** (default) - Templates installed in current project only
- **Global** - Templates available across all projects

---

## Getting Started

### 1. Create Your First Template Repository

```bash
# Generate a template repository with examples
inskit template init my-company-standards \
  --namespace acme \
  --description "ACME Corp engineering standards" \
  --author "ACME Engineering Team"

# This creates:
# my-company-standards/
# ├── templatekit.yaml           # Manifest with examples
# ├── README.md                  # Usage docs
# ├── .gitignore                # Git setup
# └── .claude/
#     ├── rules/
#     │   └── example-instruction.md
#     ├── commands/
#     │   └── example-command.md
#     └── hooks/
#         └── example-hook.md
```

### 2. Customize Your Templates

```bash
cd my-company-standards

# Edit example files or create new ones
vim .claude/rules/python-standards.md
vim .claude/commands/run-tests.md

# Update templatekit.yaml to reference your templates
vim templatekit.yaml
```

### 3. Publish to Git

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourcompany/standards.git
git push -u origin main
```

### 4. Team Members Install

```bash
# Anyone can now install
inskit template install https://github.com/yourcompany/standards --as acme

# Templates appear in their IDE:
# .claude/rules/acme.python-standards.md
# .claude/commands/acme.run-tests.md (accessible as /acme.run-tests)
```

### 5. Stay Synchronized

```bash
# Check for issues
inskit template validate

# Update to latest version
inskit template update acme

# List what's installed
inskit template list
```

---

## Multi-Repository Workflows

InstructionKit is designed for **layered standards** from multiple sources.

### Why Multiple Repositories?

**Layered Standards:**
- 🏢 **Company-wide** - Security policies, code review standards (maintained by platform team)
- 👥 **Team-specific** - API design patterns, testing practices (maintained by team leads)
- 👤 **Personal** - Your productivity shortcuts and preferences
- 🌐 **Community** - Open-source best practices and patterns

**Different Update Cadences:**
- Company standards change quarterly
- Team practices evolve monthly
- Personal tools update continuously

### Example: Full Stack Setup

```bash
# 1. Company-wide security and standards
inskit template install https://github.com/acme-corp/security-standards --as acme-security

# 2. Backend team API patterns
inskit template install https://github.com/acme-corp/backend-team --as backend

# 3. Personal productivity tools
inskit template install https://github.com/yourname/my-tools --as personal

# 4. Python community best practices
inskit template install https://github.com/python/best-practices --as python-community

# All coexist with namespace isolation!
# .claude/rules/acme-security.owasp-top-10.md
# .claude/rules/backend.api-design.md
# .claude/commands/personal.quick-commit.md
# .claude/rules/python-community.typing-guide.md
```

### Managing Multiple Repositories

```bash
# List templates from specific repository
inskit template list --repo acme-security
inskit template list --repo backend

# Update specific repository
inskit template update acme-security
inskit template update backend

# Update all repositories
inskit template update --all

# Validate all templates
inskit template validate
```

### Namespace Conflicts (Prevented Automatically)

```bash
# Company repo has "python-standards" template
inskit template install https://github.com/company/standards --as company
# Creates: company.python-standards.md

# Personal repo also has "python-standards" template
inskit template install https://github.com/yourname/tools --as personal
# Creates: personal.python-standards.md

# Both coexist - no conflicts!
```

**Commands are also namespaced:**
- Multiple repos can define a `/test` command
- Installed as `/company.test`, `/backend.test`, `/personal.test`
- All accessible, zero conflicts

---

## Command Reference

### `inskit template init <directory>`

Create a new template repository with examples and documentation.

```bash
# Basic usage
inskit template init my-templates

# With customization
inskit template init company-standards \
  --namespace acme \
  --description "ACME Corp engineering standards" \
  --author "ACME Engineering Team"

# Overwrite existing directory
inskit template init my-templates --force
```

**What it creates:**
- `templatekit.yaml` - Pre-configured manifest with 3 example templates
- `.claude/rules/example-instruction.md` - Example coding standards
- `.claude/commands/example-command.md` - Example slash command
- `.claude/hooks/example-hook.md` - Example automation hook
- `README.md` - Complete usage documentation
- `.gitignore` - Standard Git ignores

**Next steps after init:**
1. `cd <directory>` and customize templates
2. Update `templatekit.yaml` with your templates
3. `git init && git add . && git commit -m "Initial commit"`
4. Push to GitHub/GitLab and share with team

### `inskit template install <repo-url>`

Install templates from a Git repository.

```bash
# Install from GitHub (HTTPS)
inskit template install https://github.com/acme/templates --as acme

# Install from GitHub (SSH)
inskit template install git@github.com:acme/templates.git --as acme

# Install to global scope (available in all projects)
inskit template install https://github.com/acme/templates --as acme --scope global

# Install from local directory (for testing)
inskit template install ./my-templates --as test

# Conflict resolution (default: prompt interactively)
inskit template install https://github.com/acme/templates --as acme --conflict skip
inskit template install https://github.com/acme/templates --as acme --conflict rename
inskit template install https://github.com/acme/templates --as acme --conflict overwrite
```

**What happens:**
1. Clones repository to `~/.instructionkit/templates/<namespace>/`
2. Parses `templatekit.yaml` manifest
3. Auto-detects IDEs (Claude Code, Cursor, Windsurf, Copilot)
4. Installs templates with namespace prefix
5. Tracks installation in `.instructionkit/template-installations.json`
6. Stores SHA-256 checksums for validation

**Namespace isolation:**
- Templates always have namespace: `<namespace>.<template-name>.md`
- Examples: `acme.python-standards.md`, `acme.test-api.md`
- Commands: `/acme.test-api` (accessible as slash command)

**Interactive conflict resolution (NEW in v0.4.0):**
When templates already exist, you'll be prompted:
- **Keep** - Ignore update, keep your local version
- **Overwrite** - Replace with new version (automatic backup created)
- **Rename** - Keep both (renames local file)

### `inskit template list`

List installed templates.

```bash
# List all templates (project + global)
inskit template list

# List project templates only
inskit template list --scope project

# List global templates only
inskit template list --scope global

# Filter by repository
inskit template list --repo acme
```

**Output:**
```
Project Templates (/path/to/project)
┌──────────────────────────┬────────────────┬──────────┬─────────┐
│ Template                 │ Repository     │ Type     │ IDE     │
├──────────────────────────┼────────────────┼──────────┼─────────┤
│ acme.python-standards    │ acme           │ rule     │ claude  │
│ acme.security-checklist  │ acme           │ rule     │ claude  │
│ backend.test-api         │ backend        │ command  │ claude  │
└──────────────────────────┴────────────────┴──────────┴─────────┘
```

### `inskit template update [namespace]`

Update installed templates to latest version.

```bash
# Update specific repository
inskit template update acme

# Update all repositories
inskit template update --all

# Update with scope
inskit template update acme --scope global
inskit template update --all --scope project
```

**What it does:**
1. Pulls latest changes from Git repository
2. Detects modified templates (checksum comparison)
3. Prompts for conflict resolution if needed
4. Creates automatic backups before overwriting
5. Updates installation tracking

### `inskit template uninstall <namespace>`

Remove all templates from a repository.

```bash
# Uninstall from current project
inskit template uninstall acme

# Uninstall from global scope
inskit template uninstall acme --scope global

# Skip confirmation
inskit template uninstall acme --force
```

### `inskit template validate`

Check template health and detect issues.

```bash
# Validate all templates
inskit template validate

# Validate project templates only
inskit template validate --scope project

# Validate with detailed output
inskit template validate --verbose

# Attempt automatic fixes (future feature)
inskit template validate --fix
```

**What it checks:**
1. **Missing Files** - Templates tracked but files deleted
2. **Local Modifications** - Detects if you edited templates (checksum mismatch)
3. **Outdated Versions** - Newer versions available in repository
4. **Broken Dependencies** - Invalid template references

**Output:**
```
Validating project templates...
  Found 8 template(s)

Validation Summary:
  ✗ 1 error(s)
  ⚠ 2 warning(s)
  ℹ 1 info

┌──────────┬────────────────────┬──────────────┬─────────────────┐
│ Severity │ Template           │ Issue        │ Description     │
├──────────┼────────────────────┼──────────────┼─────────────────┤
│ ✗ ERROR  │ acme.standards     │ missing_file │ File not found  │
│ ⚠ WARNING│ acme.security      │ modified     │ Local changes   │
│ ℹ INFO   │ backend.api-design │ outdated     │ v1.0.0 → v2.0.0 │
└──────────┴────────────────────┴──────────────┴─────────────────┘
```

**Severity levels:**
- **Error (✗)** - Critical issues requiring action
- **Warning (⚠️)** - Important but non-critical
- **Info (ℹ️)** - Helpful notifications

### `inskit template backup`

Manage automatic backups.

```bash
# List available backups
inskit template backup list
inskit template backup list --scope global
inskit template backup list --limit 20

# Restore from backup
inskit template backup restore 20251109_143052 acme.security-rules.md
inskit template backup restore 20251109_143052 acme.security-rules.md --target custom-path.md

# Clean up old backups
inskit template backup cleanup --days 30
inskit template backup cleanup --days 7 --force
```

**Automatic backups:**
- Created before ANY overwrite operation
- Stored in `.instructionkit/backups/<timestamp>/`
- Timestamped directories prevent conflicts
- List/restore/cleanup via CLI

---

## Creating Template Repositories

### Repository Structure

```
company-templates/
├── templatekit.yaml              # Required manifest
├── .claude/
│   ├── rules/
│   │   ├── python-standards.md
│   │   └── security-guidelines.md
│   ├── commands/
│   │   ├── test-api.md
│   │   └── review-pr.md
│   └── hooks/
│       └── pre-prompt.md
└── README.md                      # Optional docs
```

### Template Manifest (templatekit.yaml)

```yaml
name: ACME Engineering Standards
description: Company coding standards and tools
version: 1.0.0
author: ACME Engineering Team

templates:
  # Coding standards (instructions/rules)
  - name: python-standards
    description: Python coding standards and best practices
    ide: claude
    files:
      - path: .claude/rules/python-standards.md
        type: instruction
    tags: [python, standards]

  - name: security-guidelines
    description: OWASP Top 10 and security checklist
    ide: claude
    files:
      - path: .claude/rules/security-guidelines.md
        type: instruction
    tags: [security]

  # Slash commands
  - name: test-api
    description: Run API integration tests with coverage
    ide: claude
    files:
      - path: .claude/commands/test-api.md
        type: command
    tags: [testing, api]

  - name: review-pr
    description: Perform comprehensive code review
    ide: claude
    files:
      - path: .claude/commands/review-pr.md
        type: command
    tags: [code-review]

  # Automation hooks
  - name: pre-prompt
    description: Pre-prompt hook for context injection
    ide: claude
    files:
      - path: .claude/hooks/pre-prompt.md
        type: hook
    tags: [automation]

# Optional: Group related templates
bundles:
  - name: python-stack
    description: Complete Python development setup
    templates:
      - python-standards
      - test-api
    tags: [python]

  - name: security-suite
    description: All security templates
    templates:
      - security-guidelines
      - review-pr
    tags: [security]
```

### Template Types

| Type | Location | What It Does |
|------|----------|--------------|
| `instruction` | `.claude/rules/` | Coding standards, guidelines, best practices |
| `command` | `.claude/commands/` | Slash commands (accessible as `/namespace.name`) |
| `hook` | `.claude/hooks/` | Pre/post-prompt hooks for automation |

### IDE Support

| IDE | Rule/Instruction | Commands | Hooks |
|-----|------------------|----------|-------|
| **Claude Code** | `.claude/rules/*.md` | `.claude/commands/*.md` | `.claude/hooks/*.md` |
| **Cursor** | `.cursor/rules/*.mdc` | ❌ | ❌ |
| **Windsurf** | `.windsurf/rules/*.md` | ❌ | ❌ |
| **GitHub Copilot** | `.github/copilot-instructions.md` | ❌ | ❌ |

### Template Content

**Example: Coding Standard (Instruction)**

```markdown
# Python Coding Standards

## Purpose
Company-wide Python coding standards for all projects.

## Naming Conventions
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants

## Type Hints
Always use type hints:

```python
def process_data(input: str, count: int = 10) -> list[str]:
    """Process input data."""
    return input.split()[:count]
```

## Documentation
All public functions must have Google-style docstrings.
```

**Example: Slash Command**

```markdown
# Test API Command

Run comprehensive API integration tests with coverage reporting.

## Steps
1. Detect test framework (pytest, unittest, etc.)
2. Run tests: `pytest tests/api/ --cov --cov-report=term`
3. Parse output and create summary
4. Highlight failures with details
5. Show coverage metrics

## Expected Output
- Test summary table (passed/failed/skipped)
- Coverage percentage
- Failed test details with stack traces
```

**Example: Hook**

```markdown
# Pre-Prompt Context Hook

Inject project context before each AI interaction.

## Context to Add

**Project Info:**
- Framework: Django 4.2
- Python: 3.11
- Database: PostgreSQL
- Deployment: AWS ECS

**Current Sprint:**
- Focus: API performance optimization
- Goal: Reduce response times by 30%

**Recent Changes:**
[Last 3 git commits here]
```

---

## Best Practices

### Repository Organization

**✅ Good: Separate repositories by ownership**
```
acme-security/         (Security team maintains)
acme-backend/          (Backend team maintains)
acme-frontend/         (Frontend team maintains)
```

**❌ Avoid: Monolithic "everything" repository**
```
acme-all-standards/    (Too broad, unclear ownership)
```

### Namespace Naming

**✅ Good: Clear, descriptive**
```
--as acme-security
--as backend-team
--as personal
```

**❌ Avoid: Generic, ambiguous**
```
--as repo1
--as temp
--as test
```

### Update Strategy

**Project-specific standards:**
```bash
# Install to project scope (default)
inskit template install https://github.com/acme/backend --as backend
```

**Company-wide standards:**
```bash
# Install to global scope
inskit template install https://github.com/acme/security --as acme-security --scope global
```

### Version Control

**Commit template installations:**
```bash
# Add to Git so team gets same setup
git add .instructionkit/template-installations.json
git commit -m "Add ACME security templates"
```

**Why commit?**
- Team members see which templates are installed
- Works across different machines
- Changes tracked in version control
- No manual setup needed

### Validation

**Add to CI/CD:**
```yaml
# .github/workflows/ci.yml
- name: Validate templates
  run: inskit template validate
```

**Pre-commit hook:**
```bash
#!/bin/bash
inskit template validate || exit 1
```

---

## Troubleshooting

### Templates Not Appearing in IDE

**Check installation:**
```bash
inskit template list
```

**Verify files exist:**
```bash
ls .claude/rules/
ls .claude/commands/
```

**Check IDE is detected:**
```bash
# Claude Code users: Ensure you're in a project directory
# Cursor users: Check .cursor/rules/ directory
```

### Templates Out of Sync

**Validate:**
```bash
inskit template validate --verbose
```

**Update:**
```bash
inskit template update --all
```

### Backup Recovery

**List backups:**
```bash
inskit template backup list
```

**Restore file:**
```bash
inskit template backup restore <timestamp> <filename>
```

### Namespace Conflicts

Templates from different repositories automatically get namespaced - conflicts should never occur. If you see issues:

```bash
# List all templates to check namespaces
inskit template list

# Each should have unique namespace prefix
# ✓ acme.python-standards
# ✓ backend.python-standards
```

---

## Advanced Topics

### Private Repositories

InstructionKit uses standard Git authentication:

```bash
# SSH (recommended for private repos)
inskit template install git@github.com:company/private-standards.git --as company

# HTTPS with credentials
# Configure Git credential helper first:
git config --global credential.helper store
```

### Custom IDE Paths

Templates install to standard locations:
- Claude Code: `.claude/`
- Cursor: `.cursor/`
- Windsurf: `.windsurf/`
- GitHub Copilot: `.github/`

These are auto-detected based on installed IDEs.

### Template Inheritance

Use bundles to create template sets:

```yaml
bundles:
  - name: python-backend
    description: Everything for Python backend development
    templates:
      - python-standards
      - api-design
      - database-patterns
      - testing-guide
      - security-checklist
    tags: [python, backend]
```

Team members can install the entire bundle at once.

---

## Legacy: Instructions System

> **Note:** The original Instructions system is maintained for backward compatibility. **New users should use the Templates system above.**

The Instructions system uses `instructionkit.yaml` (vs `templatekit.yaml`) and only supports basic instruction files (not commands or hooks).

### Quick Reference

```bash
# Download instructions repository
inskit download --from https://github.com/company/instructions

# Install with interactive TUI
inskit install

# Or install directly
inskit install python-best-practices --from https://github.com/company/instructions

# List available
inskit list available --from https://github.com/company/instructions

# List installed
inskit list installed

# Update
inskit update --all

# Uninstall
inskit uninstall python-best-practices
```

### Instructions vs Templates

| Feature | Instructions | Templates |
|---------|-------------|-----------|
| Manifest | `instructionkit.yaml` | `templatekit.yaml` |
| Supports | Rules/instructions only | Rules, commands, hooks, anything |
| Namespacing | No | Yes (automatic) |
| Multi-repo | Limited | Full support |
| Validation | No | Yes |
| Backups | No | Automatic |
| Conflict Resolution | Basic | Interactive |
| **Recommendation** | Legacy | **Use this** |

---

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/troylar/instructionkit.git
cd instructionkit

# Install in development mode
pip install -e .[dev]

# Or use invoke
invoke dev-setup
```

### Testing

```bash
# Run all tests
invoke test

# Run with coverage
invoke test --coverage

# Run specific tests
invoke test-unit
invoke test-integration
```

### Code Quality

```bash
# Run all checks
invoke quality

# Auto-fix issues
invoke quality --fix

# Individual checks
invoke lint
invoke format
invoke typecheck
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Support

- **Documentation:** [https://github.com/troylar/instructionkit](https://github.com/troylar/instructionkit)
- **Issues:** [https://github.com/troylar/instructionkit/issues](https://github.com/troylar/instructionkit/issues)
- **Discussions:** [https://github.com/troylar/instructionkit/discussions](https://github.com/troylar/instructionkit/discussions)

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by the InstructionKit team**

[⭐ Star on GitHub](https://github.com/troylar/instructionkit) • [📦 Install from PyPI](https://pypi.org/project/instructionkit/)

</div>
