<div align="center">

# 🎯 InstructionKit

**Get your AI coding assistant following best practices in under 2 minutes**

[![CI](https://github.com/troylar/instructionkit/actions/workflows/ci.yml/badge.svg)](https://github.com/troylar/instructionkit/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/troylar/instructionkit/branch/main/graph/badge.svg)](https://codecov.io/gh/troylar/instructionkit)
[![PyPI version](https://img.shields.io/pypi/v/instructionkit.svg)](https://pypi.org/project/instructionkit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Supports:** Cursor • GitHub Copilot • Windsurf • Claude Code

</div>

---

## 🚀 Get Started in 60 Seconds

```bash
# 1. Install
pip install instructionkit

# 2. Download instruction repository (with optional version control)
inskit download --repo https://github.com/troylar/instructionkit-examples
# Or pin to a specific version:
# inskit download --repo https://github.com/user/repo --ref v1.0.0

# 3. Browse & install with interactive TUI
inskit install
```

**✨ What you just got:**
- 🐍 Python best practices (type hints, async patterns)
- ⚛️ React & TypeScript patterns
- 🧪 Testing with pytest
- 🔐 Security (OWASP Top 10)
- 🐳 Docker optimization
- 📝 Documentation standards
- ...and more!

Your AI assistant now follows these guidelines automatically when you code. **No configuration needed.**

👉 **[Browse all 12 examples](https://github.com/troylar/instructionkit-examples)** or keep reading to use your own instructions.

---

## 🌟 What is InstructionKit?

A powerful CLI tool that enables developers to **browse, install, and manage** instructions for AI coding assistants. Download instruction repositories to your local library, browse them with an interactive TUI, and install exactly what you need.

Perfect for:
- ⚡️ **Getting started fast** with curated examples
- 🏢 **Standardizing team practices** across projects
- 📚 **Building personal libraries** of coding patterns
- 🔄 **Sharing knowledge** across your organization

> **CLI name:** Commands use `inskit` (short for InstructionKit)

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎨 **Interactive TUI Browser**

- Browse your instruction library with a beautiful terminal UI
- Search and filter instructions by name, description, or repository
- Select multiple instructions with checkboxes
- Choose installation location and target tools interactively
- See exactly where files will be installed before confirming

</td>
<td width="50%">

### 📚 **Local Library Management**

- Download instruction repositories to your local library
- Keep multiple repositories organized in one place
- Update repositories to get the latest instructions
- List and delete repositories from your library
- Fast offline browsing once downloaded

</td>
</tr>
<tr>
<td>

### 🎯 **Project-Level Installation**

- All installations are project-specific
- Automatic project root detection
- Organized in tool-specific directories (`.cursor/rules/`, `.claude/rules/`, etc.)
- Clean, versioned alongside your code
- Portable tracking with relative paths (works across teams and machines)

</td>
<td>

### 📦 **Flexible Sources & Versioning**

- Download from Git repositories (GitHub, GitLab, Bitbucket, self-hosted)
- **Version Control:** Pin to tags, track branches, or lock to commits
- Download from local folders (perfect for testing and development)
- Support for private repositories with standard Git authentication
- Bundle support for installing multiple instructions at once
- Automatic updates for branch-based installations

</td>
</tr>
<tr>
<td>

### 🎯 **Smart Management**

- Auto-detect installed AI coding tools
- Track all installed instructions with metadata
- **Interactive conflict resolution** - prompts before overwriting
- **Template validation** - check health and detect issues
- Easy uninstall functionality

</td>
<td>

### 🔐 **Enterprise Ready**

- Works with private repositories
- No external dependencies beyond Git
- Secure, local-only storage
- Cross-platform support (macOS, Linux, Windows)

</td>
</tr>
</table>

## 📚 Using Your Own Instructions

Want to use company or custom instructions instead? It's just as easy:

```bash
# Download from your GitHub repo
inskit download --from https://github.com/yourcompany/instructions

# Browse and install with the TUI
inskit install
```

The interactive TUI lets you:
- 🔍 Search and filter by tags
- ☑️ Select multiple instructions
- 🎯 Choose which AI tools to install to
- 📦 See exactly what gets installed

**Managing your library:**

```bash
inskit list library              # See what's downloaded
inskit update --all              # Get latest updates
inskit delete <repo-namespace>   # Remove a repository
```

### Alternative: Direct Installation

For quick one-off installs without using the library:

```bash
# Direct install (bypasses library)
inskit install python-best-practices --from https://github.com/company/instructions

# See what's available from a repo
inskit list available --from https://github.com/company/instructions
```

## 📖 Usage

### Library Management

<details>
<summary><b>Download Instructions to Your Library</b></summary>

Build your local library of instruction repositories with version control:

```bash
# Download from Git repository (default branch)
inskit download --repo https://github.com/company/instructions

# Download specific version by tag (pinned, won't auto-update)
inskit download --repo https://github.com/company/instructions --ref v1.0.0

# Download specific branch (will auto-update)
inskit download --repo https://github.com/company/instructions --ref main

# Download specific commit (pinned, won't auto-update)
inskit download --repo https://github.com/company/instructions --ref abc123def

# Download from local folder (no version control)
inskit download --repo ./my-instructions

# Re-download to get latest updates
inskit download --repo https://github.com/company/instructions --force
```

**Version Control Benefits:**
- 📌 **Tags:** Pin to specific releases (e.g., `v1.0.0`) - won't auto-update
- 🌿 **Branches:** Track latest changes (e.g., `main`, `develop`) - auto-updates
- 📍 **Commits:** Lock to exact state (e.g., `abc123`) - won't auto-update
- 📦 **Multiple Versions:** Install different versions of same repo side-by-side

Your library is stored in `~/.instructionkit/library/` and organized by repository namespace and version.

</details>

<details>
<summary><b>List Your Library Contents</b></summary>

```bash
# Show all repositories in library
inskit list library

# Show individual instructions
inskit list library --instructions

# Filter by repository alias
inskit list library --source company
```

</details>

<details>
<summary><b>Update Library Repositories</b></summary>

```bash
# Update a specific repository
inskit update --namespace github.com_company_instructions

# Update all repositories in library
inskit update --all
```

**Smart Update Behavior:**
- 🌿 **Branches:** Automatically pull latest changes from remote
- 📌 **Tags:** Skipped (immutable - won't update)
- 📍 **Commits:** Skipped (immutable - won't update)
- 🔄 **Installed Files:** Automatically updated after pulling changes

**Example Output:**
```
Updating 3 repository(ies)...

⊘ Skipped: python-standards (tag v1.0.0 is immutable)
✓ Updated: react-patterns (branch main)
✓ Updated: api-guidelines (branch develop)

✓ Updated: 2 repository(ies)
⊘ Skipped: 1 immutable reference(s)
```

</details>

<details>
<summary><b>Delete from Library</b></summary>

```bash
# Delete a repository (keeps installed instructions)
inskit delete github.com_company_instructions

# Skip confirmation
inskit delete github.com_company_instructions --force
```

Note: Deleting from library doesn't uninstall instructions. Use `inskit uninstall` for that.

</details>

### Interactive TUI Browser

<details>
<summary><b>Using the TUI to Browse and Install</b></summary>

Launch the interactive browser:

```bash
inskit install
```

**TUI Features:**

- **Search**: Type `/` to search by name or description
- **Filter**: Select repository from dropdown
- **Select**: Use `Space` or `Enter` to toggle instruction selection
- **Select All**: Press `Ctrl+A` or click "Select All" button
- **Target Tools**: Check boxes for Cursor, Windsurf, Claude Code, etc.
- **Install**: Review summary and click "📦 Install Selected"

The TUI shows exactly where files will be installed in your project before you confirm.

</details>

<details>
<summary><b>Install Specific Instruction by Name</b></summary>

Install directly from library without TUI:

```bash
# Install by name (opens selection if multiple matches)
inskit install python-style

# The command will:
# 1. Search your library for "python-style"
# 2. If found in multiple repos, ask which one
# 3. Install the selected instruction
```

</details>

### Installing Instructions

<details>
<summary><b>Project-Level Installation</b></summary>

InstructionKit installs all instructions at the **project level**:

**How it works:**

- All instructions are installed to your current project
- Stored in tool-specific directories in your project root:
  - **Claude Code**: `.claude/rules/*.md`
  - **Cursor**: `.cursor/rules/*.mdc`
  - **Windsurf**: `.windsurf/rules/*.md`
  - **GitHub Copilot**: `.github/instructions/*.md`
- Tracked in `<project-root>/.instructionkit/installations.json`
- Automatically detects project root (looks for `.git`, `pyproject.toml`, `package.json`, etc.)
- Can be run from any directory within the project

```bash
# Install to current project
inskit install python-best-practices --from https://github.com/company/instructions

# All installations are project-level
inskit install python-style

# List shows project installations
inskit list installed
```

**Why project-level?**

- Instructions stay with your code (version controlled)
- Team members get the same instructions automatically
- Different projects can have different instructions
- Clean, organized structure per tool
- Portable across machines - uses relative paths in tracking
- No setup needed when cloning - instructions just work

</details>

### Advanced: Direct Installation (Bypasses Library)

<details>
<summary><b>Install Directly from Repository</b></summary>

For one-off installs without downloading to library first:

```bash
# Basic install (to current project)
inskit install python-best-practices --from https://github.com/company/instructions

# Install to specific tool
inskit install python-best-practices --from https://github.com/company/instructions --tool cursor

# Handle conflicts by renaming
inskit install python-best-practices --from https://github.com/company/instructions --conflict rename

# Overwrite existing
inskit install python-best-practices --from https://github.com/company/instructions --conflict overwrite
```

</details>

<details>
<summary><b>Install from Local Folder</b></summary>

```bash
# Relative path
inskit install python-best-practices --from ./my-instructions

# Absolute path
inskit install python-best-practices --from /path/to/instructions

# Great for testing before committing to Git
inskit install my-new-instruction --from ~/Documents/instruction-drafts
```

</details>

<details>
<summary><b>Install Bundles</b></summary>

```bash
# Install a bundle of related instructions
inskit install python-backend --bundle --from https://github.com/company/instructions

# This might install: python-style, testing-practices, api-design, etc.
```

</details>

### Listing & Viewing

<details>
<summary><b>List Installed Instructions</b></summary>

```bash
# Show all installed instructions in current project
inskit list installed

# Filter by AI tool
inskit list installed --tool cursor

# Filter by source repository
inskit list installed --repo https://github.com/company/instructions
```

**Shows comprehensive information:**
- Instruction name and AI tool
- Source repository URL
- **Version information** with visual badges:
  - 📌 v1.0.0 (tag - pinned version)
  - 🌿 main (branch - tracking latest)
  - 📍 abc123 (commit - locked to specific state)
- Installation date
- Project scope

**Example Output:**
```
Installed Instructions
────────────────────────────────────────────────────────────
AI Tool    Instruction       Scope    Source         Version      Installed
Claude     python-style      Project  company/...    📌 v1.0.0   2025-10-26
Cursor     react-patterns    Project  company/...    🌿 main     2025-10-26
Claude     api-guidelines    Project  company/...    📍 abc123   2025-10-26
```

</details>

<details>
<summary><b>List Available Instructions (Without Library)</b></summary>

Directly query a repository without downloading it:

```bash
# From Git repository
inskit list available --from https://github.com/company/instructions

# From local folder
inskit list available --from ./my-instructions

# Filter by tag
inskit list available --from https://github.com/company/instructions --tag python

# Show only bundles
inskit list available --from https://github.com/company/instructions --bundles-only
```

**Tip:** For regular use, it's better to `download` the repo to your library and browse with the TUI!

</details>

### Uninstalling Instructions

```bash
# Uninstall from all tools in current project
inskit uninstall python-best-practices

# Uninstall from specific tool
inskit uninstall python-best-practices --tool cursor

# Skip confirmation
inskit uninstall python-best-practices --force
```

### Viewing Detected Tools

```bash
# See which AI coding tools are installed
inskit tools
```

## 📂 Storage & Tracking

InstructionKit stores everything locally:

**Library Storage:**

- Downloaded repositories: `~/.instructionkit/library/`
- Organized by repository namespace (e.g., `github.com_company_instructions/`)
- Browse offline after downloading

**Installation Tracking:**

- Tracked in `<project-root>/.instructionkit/installations.json`
- Contains metadata for all installed instructions in the project
- Created automatically when you install instructions
- **Uses relative paths** - portable across different machines and users
- **Version control friendly** - no absolute paths with usernames
- **Recommended:** Commit to Git so team members get the same setup automatically
- Alternative: Add to `.gitignore` if instructions should be personal

**Why commit installations.json?**

- Team members automatically see which instructions are installed
- Works seamlessly when cloned to different machines
- No manual setup needed - everyone gets the same configuration
- Changes to installed instructions are tracked in version control

The `list installed` command shows all instructions in the current project.

## 📁 Creating Your Own Instructions

InstructionKit works with simple folder structures - no Git repository required!

### Minimal Structure

```
my-instructions/
├── instructionkit.yaml          # Required: Metadata file
└── instructions/
    └── my-instruction.md        # Your instruction files
```

### instructionkit.yaml Format

```yaml
name: My Instructions Repository
description: A collection of my coding instructions
version: 1.0.0

instructions:
  - name: my-instruction
    description: What this instruction does
    file: instructions/my-instruction.md
    tags:
      - tag1
      - tag2
```

### Full Example with Bundles

```
my-instructions/
├── instructionkit.yaml
├── instructions/
│   ├── python-style.md
│   ├── testing.md
│   └── api-design.md
└── README.md                    # Optional
```

**instructionkit.yaml:**

```yaml
name: My Instructions
description: Personal coding standards
version: 1.0.0

instructions:
  - name: python-style
    description: Python coding standards
    file: instructions/python-style.md
    tags: [python, style]

  - name: testing
    description: Testing best practices
    file: instructions/testing.md
    tags: [testing, quality]

  - name: api-design
    description: API design guidelines
    file: instructions/api-design.md
    tags: [api, backend]

bundles:
  - name: python-stack
    description: Complete Python development setup
    instructions:
      - python-style
      - testing
    tags: [python]
```

## 🔄 Template Sync System

**NEW in v0.4.0:** Repository-based distribution for maintaining consistent IDE artifacts across multiple projects. Sync coding standards, commands, hooks, and any IDE content your team needs.

**Latest Features:**
- ✨ **Template Validation** - Check template health, detect modifications, find missing files
- 🛡️ **Interactive Conflict Resolution** - Prompts before overwriting, prevents data loss
- 🔍 **Modification Detection** - Checksum-based tracking of local changes

### What Are Templates?

Templates are **any reusable IDE artifacts** that teams can install and keep synchronized across projects. This includes:

- 📝 **Instructions/Rules** - Coding standards, best practices, guidelines (e.g., `python-standards.md`, `security-checklist.md`)
- 🎯 **Commands** - Slash commands for Claude Code (e.g., `/test-api`, `/review-pr`)
- 🪝 **Hooks** - Claude Code hooks for automation (e.g., pre-prompt, post-prompt hooks)
- 🔧 **Any IDE Artifact** - Anything you want version-controlled and synchronized

**Typical Use Cases:**
- Company-wide coding standards and guidelines
- Team-specific instructions and best practices
- Reusable commands and workflows
- IDE hooks for automation
- Any content in `.claude/rules/`, `.claude/commands/`, `.claude/hooks/`, etc.

### Why Templates?

**For Teams:**
- 🔄 **Synchronize** command repositories across all projects
- 🚀 **Consistent workflows** - everyone uses the same commands
- 📦 **Version control** - track template versions per project
- 🔍 **Namespace isolation** - multiple template repos coexist without conflicts

**For Individuals:**
- 🎯 **Personal command library** - reuse commands across projects
- 🔧 **Testing ground** - try new commands before sharing
- 📚 **Organized toolbox** - keep all templates in one place

### Template Repository Structure

Templates require a Git repository with `templatekit.yaml`:

```
company-templates/
├── templatekit.yaml              # Required: Template manifest
├── .claude/
│   ├── rules/
│   │   ├── python-standards.md   # Coding standards
│   │   └── security-guidelines.md # Security best practices
│   ├── commands/
│   │   ├── test-api.md           # Slash command
│   │   └── review-pr.md          # Another command
│   └── hooks/
│       └── pre-prompt.md         # Claude Code hook
└── README.md                      # Optional: Documentation
```

**templatekit.yaml Format:**

```yaml
name: ACME Engineering Standards
description: Company coding standards, commands, and hooks for all projects
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
    description: Security checklist and OWASP guidelines
    ide: claude
    files:
      - path: .claude/rules/security-guidelines.md
        type: instruction
    tags: [security]

  # Commands (slash commands)
  - name: test-api
    description: Run API integration tests with coverage
    ide: claude
    files:
      - path: .claude/commands/test-api.md
        type: command
    tags: [testing, api]

  # Hooks (automation)
  - name: pre-prompt
    description: Pre-prompt hook for context injection
    ide: claude
    files:
      - path: .claude/hooks/pre-prompt.md
        type: hook
    tags: [automation]

bundles:
  - name: python-stack
    description: Complete Python development setup
    templates:
      - python-standards
      - test-api
    tags: [python]
```

### Quick Start

```bash
# 1. Install templates from a repository
inskit template install https://github.com/company/standards

# This installs (with namespace prefix):
# - company.python-standards.md (coding standards)
# - company.security-guidelines.md (security checklist)
# - company.test-api.md (slash command)
# - company.pre-prompt.md (hook)

# 2. List installed templates
inskit template list

# 3. Your IDE now has:
# - Instructions in .claude/rules/company.python-standards.md
# - Commands accessible as /company.test-api
# - Hooks automatically active
# All namespaced to avoid conflicts!

# 4. Validate template health
inskit template validate
# Checks for missing files, local modifications, outdated versions

# 5. Update to latest version
inskit template update company

# 6. Uninstall when no longer needed
inskit template uninstall company
```

### Working with Multiple Template Repositories

InstructionKit is designed from the ground up for **multi-repository workflows**. You can install templates from unlimited sources, and they'll all coexist peacefully using namespace isolation.

#### Why Multiple Repositories?

**Layered Standards:**
- 🏢 **Company-wide** - Organization-level standards everyone follows
- 👥 **Team-specific** - Domain-specific practices (backend, frontend, mobile)
- 👤 **Personal** - Individual preferences and productivity shortcuts
- 🌐 **Community** - Open-source best practices and patterns

**Different Update Cadences:**
- Company standards change quarterly
- Team practices evolve monthly
- Personal tools update continuously
- Community templates track ecosystem changes

**Separation of Concerns:**
- Security team maintains security templates
- Platform team maintains infrastructure templates
- Each team owns their domain expertise
- No monolithic "everything" repository

#### Multi-Repo Workflow Example

```bash
# 1. Install company-wide standards (required for all projects)
inskit template install https://github.com/acme-corp/engineering-standards --as acme
# Installs: acme.security-guidelines, acme.code-review-checklist, acme.python-standards

# 2. Install team-specific templates (backend team)
inskit template install https://github.com/acme-corp/backend-standards --as backend
# Installs: backend.api-design, backend.database-patterns, backend.test-api

# 3. Install personal productivity tools (your own repo)
inskit template install https://github.com/yourname/my-tools --as personal
# Installs: personal.quick-commit, personal.code-snippet, personal.daily-standup

# 4. Install community best practices (optional)
inskit template install https://github.com/python/best-practices --as python-community
# Installs: python-community.typing-guide, python-community.async-patterns

# 5. List all installed templates across all repos
inskit template list
```

**Result in your IDE:**
```
.claude/
├── rules/
│   ├── acme.security-guidelines.md          # Company security policy
│   ├── acme.code-review-checklist.md        # Company code review standards
│   ├── acme.python-standards.md             # Company Python style guide
│   ├── backend.api-design.md                # Team API patterns
│   ├── backend.database-patterns.md         # Team database conventions
│   ├── personal.quick-commit.md             # Your commit helpers
│   └── python-community.typing-guide.md     # Community typing best practices
├── commands/
│   ├── backend.test-api.md                  # /backend.test-api command
│   ├── personal.daily-standup.md            # /personal.daily-standup command
│   └── personal.code-snippet.md             # /personal.code-snippet command
```

#### Managing Multiple Repositories

**List templates by repository:**
```bash
# Show all templates from a specific repo
inskit template list --repo acme
inskit template list --repo backend
inskit template list --repo personal

# Show all templates from all repos
inskit template list
```

**Update specific repositories:**
```bash
# Update company templates (quarterly)
inskit template update acme

# Update team templates (monthly)
inskit template update backend

# Update all repositories at once
inskit template update --all
```

**Validate across repositories:**
```bash
# Validate all templates from all repos
inskit template validate

# Check for outdated templates across all repos
inskit template validate --verbose
```

**Remove a repository:**
```bash
# Uninstall all templates from a repository
inskit template uninstall acme

# Remove repository from library (keeps installed files)
# Note: Use standard library management commands
```

#### Namespace Conflicts (Prevented Automatically)

Templates from different repos **never conflict** thanks to namespace isolation:

```bash
# Company repo has "python-standards" template
inskit template install https://github.com/company/standards --as company
# Creates: company.python-standards.md

# Personal repo also has "python-standards" template
inskit template install https://github.com/yourname/tools --as personal
# Creates: personal.python-standards.md

# Both coexist peacefully - no conflicts!
# Your IDE sees both:
# - .claude/rules/company.python-standards.md
# - .claude/rules/personal.python-standards.md
```

**Commands are also namespaced:**
- Multiple repos can define `/test` command
- Installed as `/company.test`, `/backend.test`, `/personal.test`
- No conflicts, all accessible

#### Best Practices for Multi-Repo Setup

1. **Use Meaningful Namespaces:**
   ```bash
   # Good: Clear, descriptive
   --as acme-security
   --as backend-team
   --as personal

   # Avoid: Generic, ambiguous
   --as repo1
   --as temp
   --as test
   ```

2. **Layer by Scope:**
   - **Company** (global scope) - Standards everyone must follow
   - **Team** (project scope) - Team-specific practices
   - **Personal** (global scope) - Your productivity tools

3. **Update Strategically:**
   ```bash
   # Update company standards across all projects
   inskit template update acme --scope global

   # Update team standards for current project only
   inskit template update backend --scope project
   ```

4. **Document Your Stack:**
   ```bash
   # Add to project README.md
   ## Required Templates

   ```bash
   # Company standards (required)
   inskit template install https://github.com/acme/standards --as acme

   # Backend team standards (required for backend projects)
   inskit template install https://github.com/acme/backend --as backend
   ```
   ```

5. **Validate Regularly:**
   ```bash
   # Add to CI/CD pipeline or git hooks
   inskit template validate
   ```

### Command Reference

#### `inskit template init <directory>`

**NEW in v0.4.0:** Create a new template repository with scaffolded structure and example templates.

```bash
# Create basic template repository
inskit template init my-templates

# Create with custom namespace and description
inskit template init company-standards \
  --namespace acme \
  --description "ACME Corp engineering standards" \
  --author "ACME Engineering Team"

# Overwrite existing directory
inskit template init my-templates --force
```

**What it creates:**

```
my-templates/
├── templatekit.yaml          # Pre-configured manifest with examples
├── README.md                 # Complete usage documentation
├── .gitignore               # Standard ignores for Python projects
└── .claude/
    ├── rules/
    │   └── example-instruction.md     # Example coding standards
    ├── commands/
    │   └── example-command.md        # Example slash command
    └── hooks/
        └── example-hook.md           # Example automation hook
```

**Next steps after creation:**

```bash
cd my-templates

# Customize templates
vim .claude/rules/example-instruction.md
vim .claude/commands/example-command.md

# Update manifest
vim templatekit.yaml

# Initialize git and push
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main

# Test locally
inskit template install . --as myteam

# Share with team
# Team members can now: inskit template install <repo-url> --as myteam
```

**Options:**

- `--namespace`, `-n` - Custom namespace (default: directory name)
- `--description`, `-d` - Repository description
- `--author`, `-a` - Author name
- `--force`, `-f` - Overwrite existing directory

**Example templates include:**

- **Instruction template** - Shows how to write coding standards and best practices
- **Command template** - Demonstrates slash command creation with examples
- **Hook template** - Explains pre/post-prompt hooks with use cases
- **README** - Complete documentation for your team
- **templatekit.yaml** - Fully commented manifest with all options

#### `inskit template validate`

**NEW in v0.4.0:** Validate installed templates for health issues and detect problems before they cause issues.

```bash
# Validate all templates (project + global)
inskit template validate

# Validate only project templates
inskit template validate --scope project

# Validate only global templates
inskit template validate --scope global

# Show detailed information
inskit template validate --verbose

# Attempt to fix issues automatically (future feature)
inskit template validate --fix
```

**What it checks:**
1. **Missing Files** - Templates tracked but files deleted
2. **Local Modifications** - Detects if you've edited installed templates (checksum mismatch)
3. **Outdated Versions** - Checks if newer versions are available in library
4. **Broken Dependencies** - Validates template references and structure

**Output Format:**
- **Errors** (❌): Critical issues that require action (missing files)
- **Warnings** (⚠️): Important but non-critical (local modifications)
- **Info** (ℹ️): Helpful notifications (newer versions available)

**Example output:**
```
Validating project templates (/path/to/project)...
  Found 8 template(s)

Validation Summary:
  ✗ 1 error(s)
  ⚠ 2 warning(s)
  ℹ 1 info

Validation Issues
Severity  Template                    Issue Type       Description                          Remediation
✗ ERROR   company.python-standards    missing_file     Installed file not found             Reinstall template with: inskit template install...
⚠ WARNING company.security-guidelines modified         Template has been modified locally   Update to restore original: inskit template update company
ℹ INFO    company.test-api           outdated         Newer version available (1.0.0 → 1.2.0) Update with: inskit template update company
```

**Use Cases:**
- **Before Updates**: Check template health before updating
- **Troubleshooting**: Diagnose why templates aren't working
- **Team Onboarding**: Verify team members have correct templates
- **CI/CD**: Add to CI pipeline to catch template issues early

**Best Practices:**
```bash
# Run validation weekly or when something seems off
inskit template validate

# Check before major updates
inskit template validate
inskit template update --all

# Verify after git clone/pull
git pull
inskit template validate
```

#### `inskit template install <repo-url>`

Install templates from a Git repository with namespace isolation.

```bash
# Install from GitHub (HTTPS)
inskit template install https://github.com/acme/templates

# Install from GitHub (SSH)
inskit template install git@github.com:acme/templates.git

# Install to global scope (available in all projects)
inskit template install https://github.com/acme/templates --scope global

# Use custom namespace (default: derived from repo name)
inskit template install https://github.com/acme/templates --as acme-eng

# Conflict resolution (by default, prompts interactively)
inskit template install https://github.com/acme/templates                    # Prompt for each conflict
inskit template install https://github.com/acme/templates --conflict skip    # Skip existing files
inskit template install https://github.com/acme/templates --conflict rename  # Rename on conflict
inskit template install https://github.com/acme/templates --conflict overwrite # Force overwrite
```

**What it does:**
1. Clones repository to `~/.instructionkit/templates/{namespace}/`
2. Parses `templatekit.yaml` manifest
3. Auto-detects IDEs in your project
4. Installs templates with namespace prefix (e.g., `company.python-standards.md`)
5. Tracks installation in `.instructionkit/template-installations.json`
6. Stores SHA-256 checksums for conflict detection

**Namespace isolation:**
- Templates always installed with namespace: `{namespace}.{template-name}.md`
- Examples:
  - `company.python-standards.md` (instruction/rule)
  - `company.test-api.md` (command - accessible as `/company.test-api`)
  - `company.pre-prompt.md` (hook)
- Prevents conflicts when using multiple template repos
- Each repo's content is isolated by namespace

**Conflict Handling:**
When installing templates that already exist, InstructionKit will **prompt you interactively** (NEW in v0.4.0):
- Shows which files will be affected
- Asks for your choice: Keep existing, Rename, or Overwrite
- Prevents accidental data loss
- Can be overridden with `--conflict` flag for automation

**Options:**
- `--scope project|global` - Install to project (default) or globally
- `--as <namespace>` - Override namespace (default: repo name)
- `--conflict prompt|skip|rename|overwrite` - Conflict resolution strategy (default: prompt)

**Project vs Global:**
- **Project** (default): Installed in current project's IDE directories
- **Global**: Installed in `~/.instructionkit/global-templates/` (available everywhere)

#### `inskit template list`

List installed templates with detailed information.

```bash
# List all templates (project + global)
inskit template list

# List only project templates
inskit template list --scope project

# List only global templates
inskit template list --scope global

# Filter by repository
inskit template list --repo acme-templates

# Output as JSON
inskit template list --format json

# Simple output (just names)
inskit template list --format simple

# Show verbose information (paths, checksums)
inskit template list --verbose
```

**Output formats:**
- `table` (default): Grouped by repository with version info
- `json`: Machine-readable format with all metadata
- `simple`: Just template names (one per line)

**Example output:**
```
Repository: ACME Engineering Standards (v1.2.0)
Namespace: company

Template             IDE     Scope     Installed
python-standards     claude  Project   2025-11-09
security-guidelines  claude  Project   2025-11-09
test-api            claude  Project   2025-11-09
pre-prompt          claude  Project   2025-11-09

Total: 4 templates from 1 repository(ies)
```

**Options:**
- `--scope all|project|global` - Which installations to list
- `--repo <name>` - Filter by repository name or namespace
- `--format table|json|simple` - Output format
- `--verbose` - Show paths and checksums

#### `inskit template update [repo-name]`

Update installed templates to latest version with conflict detection.

```bash
# Update specific repository
inskit template update acme-templates

# Update all repositories
inskit template update --all

# Update with scope filter
inskit template update --all --scope project

# Update both project and global
inskit template update --all --scope both

# Force update (overwrite local changes)
inskit template update acme-templates --force

# Dry run (show what would be updated)
inskit template update --all --dry-run
```

**What it does:**
1. Fetches latest changes from Git
2. Compares new version with installed version
3. For each template:
   - Calculates checksums (original, current, new)
   - Detects conflicts:
     - **None**: Safe to update (no local changes)
     - **Local Modified**: You changed it, upstream unchanged
     - **Both Modified**: Both you and upstream changed it
4. Prompts for conflict resolution (unless `--force`)
5. Updates template files and installation records

**Conflict resolution:**
When conflicts detected, you'll be prompted interactively for each file:
- **[K]eep local version**: Preserve your changes (ignore remote update)
- **[O]verwrite with remote**: Replace with new version (discard local changes)
- **[R]ename local and install remote**: Keep both versions side-by-side

The default choice is "Keep" to prevent accidental loss of local modifications.

**Options:**
- `--all` - Update all repositories instead of specific one
- `--scope project|global|both` - Which installations to update
- `--force` - Overwrite all without prompting
- `--dry-run` - Show what would happen without making changes

**Example output:**
```
Checking company for updates...
Found updates (v1.0.0 → v1.2.0)

Updating company.python-standards... ✓
Updating company.security-guidelines... ✓
Updating company.test-api...
  ⚠️  Conflict detected: local_modified
  Resolution: [Overwrite/Keep/Skip]? keep
Skipping company.test-api

✓ Updated 2 template(s)
Skipped 1 template(s) due to conflicts
```

#### `inskit template uninstall <repo-name>`

Remove installed templates from your project or global scope.

```bash
# Uninstall entire repository
inskit template uninstall acme-templates

# Uninstall specific template only
inskit template uninstall acme-templates --template test-api

# Uninstall from global scope
inskit template uninstall acme-templates --scope global

# Skip confirmation prompt
inskit template uninstall acme-templates --force

# Remove from tracking but keep files
inskit template uninstall acme-templates --keep-files
```

**What it does:**
1. Finds all templates from repository
2. Shows what will be removed
3. Prompts for confirmation (unless `--force`)
4. Deletes template files (unless `--keep-files`)
5. Removes from installation tracking
6. Cleans up library if no templates remain from that repo

**Options:**
- `--template <name>` - Uninstall specific template (not entire repo)
- `--scope project|global` - Which installation to remove
- `--force` - Skip confirmation prompt
- `--keep-files` - Remove from tracking but keep files on disk

**Example output:**
```
The following templates will be removed:
  - company.python-standards (claude)
  - company.security-guidelines (claude)
  - company.test-api (claude)
  - company.pre-prompt (claude)

Remove 4 template(s) from company? [y/N]: y

Removing company.python-standards... ✓
Removing company.security-guidelines... ✓
Removing company.test-api... ✓
Removing company.pre-prompt... ✓

✓ Uninstalled 4 template(s)
```

### Tutorials

#### Tutorial 1: Team Template Repository

**Scenario:** Set up company-wide coding standards and tools for all engineering projects.

**Step 1: Create Template Repository**

```bash
# Create new repo
mkdir company-standards
cd company-standards
git init

# Create template structure
mkdir -p .claude/rules .claude/commands .claude/hooks

# Create coding standards (instruction/rule)
cat > .claude/rules/python-standards.md << 'EOF'
# Python Coding Standards

Our company Python standards:

## Type Hints
- All functions must have type hints
- Use `from __future__ import annotations` for forward references
- Prefer built-in types (list[str]) over typing module (List[str])

## Error Handling
- Use specific exception types, not bare except
- Always provide context in exception messages
- Log errors with appropriate levels

## Testing
- Minimum 80% code coverage
- Use pytest for all tests
- Mock external dependencies
EOF

# Create security guidelines
cat > .claude/rules/security-guidelines.md << 'EOF'
# Security Guidelines

## Input Validation
- Validate all user inputs
- Use parameterized queries (no string concatenation for SQL)
- Sanitize file paths and names

## Authentication
- Never store passwords in plain text
- Use bcrypt or argon2 for hashing
- Implement rate limiting on auth endpoints

## Dependencies
- Run security scans weekly
- Keep dependencies updated
- Review CVE reports
EOF

# Create a command
cat > .claude/commands/test-api.md << 'EOF'
# Test API Endpoints

Run comprehensive API tests according to company standards.
EOF

# Create manifest
cat > templatekit.yaml << 'EOF'
name: Company Engineering Standards
description: Coding standards, security guidelines, and tools
version: 1.0.0
author: Engineering Team

templates:
  - name: python-standards
    description: Python coding standards for all projects
    ide: claude
    files:
      - path: .claude/rules/python-standards.md
        type: instruction
    tags: [python, standards]

  - name: security-guidelines
    description: Security checklist and best practices
    ide: claude
    files:
      - path: .claude/rules/security-guidelines.md
        type: instruction
    tags: [security]

  - name: test-api
    description: Run API integration tests
    ide: claude
    files:
      - path: .claude/commands/test-api.md
        type: command
    tags: [testing]
EOF

# Commit and push
git add .
git commit -m "feat: add company standards and guidelines"
git push origin main
```

**Step 2: Install in Your Projects**

```bash
# In any project
cd /path/to/project

# Install templates
inskit template install https://github.com/company/standards

# Output:
# Deriving namespace from repository: company
#
# Cloning repository from https://github.com/company/standards...
# ✓ Repository cloned
#
# Installing 3 templates...
# Installing company.python-standards... ✓
# Installing company.security-guidelines... ✓
# Installing company.test-api... ✓
#
# ✓ Installation complete
#
# Files installed:
#   .claude/rules/company.python-standards.md (instruction)
#   .claude/rules/company.security-guidelines.md (instruction)
#   .claude/commands/company.test-api.md (command)
#
# Now your IDE has:
# - Coding standards always active
# - Security guidelines enforced
# - Commands available: /company.test-api
```

**Step 3: Keep Templates Updated**

```bash
# Check for updates periodically
inskit template update --all

# Or update specific repository
inskit template update company
```

**Step 4: Add More Standards**

```bash
# In template repo
cat > .claude/rules/testing-standards.md << 'EOF'
# Testing Standards

## Unit Tests
- Test business logic in isolation
- Mock external dependencies
- Aim for 80%+ coverage

## Integration Tests
- Test API endpoints end-to-end
- Use test database
- Clean up data after tests
EOF

# Add a hook for automation
cat > .claude/hooks/pre-prompt.md << 'EOF'
# Pre-Prompt Hook

Before every request, remind Claude about:
- Our Python standards (type hints, error handling)
- Security guidelines (input validation, SQL injection prevention)
- Testing requirements (80% coverage)
EOF

# Update manifest
cat >> templatekit.yaml << 'EOF'

  - name: testing-standards
    description: Testing requirements and best practices
    ide: claude
    files:
      - path: .claude/rules/testing-standards.md
        type: instruction
    tags: [testing]

  - name: pre-prompt
    description: Context injection before every Claude request
    ide: claude
    files:
      - path: .claude/hooks/pre-prompt.md
        type: hook
    tags: [automation]
EOF

# Commit and push
git add .
git commit -m "feat: add testing standards and pre-prompt hook"
git tag v1.1.0
git push origin main --tags

# Team members update
inskit template update company
# Found updates (v1.0.0 → v1.1.0)
# Updating company.testing-standards... ✓
# Updating company.pre-prompt... ✓
```

#### Tutorial 2: Personal Template Library

**Scenario:** Build a personal collection of coding preferences and tools.

```bash
# Create personal template repo (local or GitHub)
mkdir ~/my-standards
cd ~/my-standards

# Create structure
mkdir -p .claude/rules .claude/commands

# Add personal coding preferences
cat > .claude/rules/my-python-style.md << 'EOF'
# My Python Style Preferences

## Documentation
- Docstrings for all public functions
- Use Google-style docstrings
- Include examples for complex functions

## Code Organization
- Max 50 lines per function
- Group related functions in classes
- Use dataclasses for simple data structures
EOF

cat > .claude/rules/code-review-checklist.md << 'EOF'
# My Code Review Checklist

Before committing:
- All tests pass
- Type hints on all functions
- No commented-out code
- No print() statements (use logging)
- Updated CHANGELOG.md
EOF

# Add personal commands
cat > .claude/commands/daily-standup.md << 'EOF'
# Generate Daily Standup

Generate standup summary from git commits and issues.
EOF

# Create manifest
cat > templatekit.yaml << 'EOF'
name: Personal Standards
description: My coding preferences and tools
version: 1.0.0

templates:
  - name: my-python-style
    description: Personal Python coding preferences
    ide: claude
    files:
      - path: .claude/rules/my-python-style.md
        type: instruction
    tags: [python, style]

  - name: code-review-checklist
    description: My pre-commit checklist
    ide: claude
    files:
      - path: .claude/rules/code-review-checklist.md
        type: instruction
    tags: [quality]

  - name: daily-standup
    description: Generate daily standup summary
    ide: claude
    files:
      - path: .claude/commands/daily-standup.md
        type: command
    tags: [productivity]
EOF

# Install globally (available in all projects)
inskit template install ~/my-standards --scope global --as personal

# Now available in any project:
# - Personal coding preferences always active
# - Commands: /personal.daily-standup
```

#### Tutorial 3: Multi-Repository Setup

**Scenario:** Combine standards from multiple sources (company + team + personal).

```bash
# Install company-wide standards
inskit template install https://github.com/company/standards --as company

# Install team-specific standards
inskit template install https://github.com/company/backend-team-standards --as backend

# Install personal preferences
inskit template install ~/my-standards --scope global --as personal

# List all templates
inskit template list

# Output shows all artifacts:
# Repository: Company Standards (v2.0.0)
# Namespace: company
#   company.python-standards (instruction)
#   company.security-guidelines (instruction)
#   company.test-api (command)
#
# Repository: Backend Team Standards (v1.5.0)
# Namespace: backend
#   backend.api-guidelines (instruction)
#   backend.database-patterns (instruction)
#   backend.setup-database (command)
#
# Repository: Personal Standards (v1.0.0)
# Namespace: personal
#   personal.my-python-style (instruction)
#   personal.code-review-checklist (instruction)
#   personal.daily-standup (command)

# Your IDE now has layers of guidance:
# 1. Company-wide: security, python standards
# 2. Team-specific: API patterns, database guidelines
# 3. Personal: your own preferences and shortcuts
#
# Commands available: /company.test-api, /backend.setup-database, /personal.daily-standup
```

### Use Cases

#### Team Standardization

**Problem:** Team members follow different coding standards and practices.

**Solution:**
```bash
# Team lead creates standards repo with:
# - Coding standards (Python, TypeScript, etc.)
# - Security guidelines
# - Testing requirements
# - Useful commands

# Team members install once
inskit template install https://github.com/team/standards

# Everyone now has:
# - Same coding standards (always active in IDE)
# - Same security guidelines
# - Same tools and commands
# All synchronized across the team!

# Update when standards evolve
inskit template update --all
```

#### Multi-Project Consistency

**Problem:** Maintaining consistent standards across multiple microservices.

**Solution:**
```bash
# Install in each microservice
cd service-auth && inskit template install https://github.com/company/standards
cd service-payments && inskit template install https://github.com/company/standards
cd service-notifications && inskit template install https://github.com/company/standards

# All services now have:
# - Same coding standards
# - Same security guidelines
# - Same tools and workflows
# Perfect consistency across your architecture!

# Update all at once when standards change:
for dir in service-*/; do
  (cd "$dir" && inskit template update --all)
done
```

#### Template Testing & Development

**Problem:** Need to test new standards before rolling out to team.

**Solution:**
```bash
# Test locally first
cd ~/standards-dev
# ... create/modify coding standards, guidelines, etc. ...

# Install to test project
cd ~/test-project
inskit template install ~/standards-dev --force

# Test in your IDE:
# - Are standards clear and helpful?
# - Do commands work as expected?
# - Are hooks behaving correctly?

# Once satisfied, push to Git
cd ~/standards-dev
git push origin main

# Team members get updates
inskit template update --all
```

#### Private Standards

**Problem:** Company has proprietary coding standards and internal guidelines.

**Solution:**
```bash
# Works with private repos (uses Git credentials)
inskit template install git@github.com:company/private-standards.git

# Or with HTTPS + credentials
inskit template install https://github.com/company/private-standards

# Git authentication methods:
# - SSH keys
# - GitHub CLI (gh auth login)
# - Credential helpers
# - Personal access tokens

# Your proprietary standards stay private
# Fully under your control
# No external dependencies
```

### Storage & Tracking

**Template Library:**
- Location: `~/.instructionkit/templates/{namespace}/`
- Structure: One directory per namespace
- Includes: Git repository with full history
- Updates: `git pull` when running `inskit template update`

**Installation Tracking:**
- **Project-level**: `<project-root>/.instructionkit/template-installations.json`
- **Global**: `~/.instructionkit/global-templates/template-installations.json`

**Example tracking file:**
```json
{
  "installations": [
    {
      "id": "uuid-1",
      "template_name": "python-standards",
      "source_repo": "Company Engineering Standards",
      "source_version": "1.2.0",
      "namespace": "company",
      "installed_path": ".claude/rules/company.python-standards.md",
      "scope": "project",
      "installed_at": "2025-11-09T10:30:00",
      "checksum": "sha256-hash-here",
      "ide_type": "claude"
    },
    {
      "id": "uuid-2",
      "template_name": "test-api",
      "source_repo": "Company Engineering Standards",
      "source_version": "1.2.0",
      "namespace": "company",
      "installed_path": ".claude/commands/company.test-api.md",
      "scope": "project",
      "installed_at": "2025-11-09T10:30:00",
      "checksum": "sha256-hash-here",
      "ide_type": "claude"
    },
    {
      "id": "uuid-3",
      "template_name": "pre-prompt",
      "source_repo": "Company Engineering Standards",
      "source_version": "1.2.0",
      "namespace": "company",
      "installed_path": ".claude/hooks/company.pre-prompt.md",
      "scope": "project",
      "installed_at": "2025-11-09T10:30:00",
      "checksum": "sha256-hash-here",
      "ide_type": "claude"
    }
  ],
  "last_updated": "2025-11-09T10:30:00",
  "schema_version": "1.0"
}
```

### Best Practices

1. **Version Your Templates**
   ```bash
   # Use semantic versioning
   git tag v1.0.0
   git tag v1.1.0
   git push --tags
   ```

2. **Namespace Thoughtfully**
   ```bash
   # Use descriptive, short namespaces
   --as company      # Good
   --as acme-eng     # Good
   --as my-custom-template-repository-name  # Too long
   ```

3. **Document Standards Clearly**
   - Add clear descriptions in templatekit.yaml
   - Provide examples in instruction files
   - Maintain a comprehensive README in template repo
   - Explain WHY, not just WHAT

4. **Test Before Distributing**
   ```bash
   # Test locally first
   inskit template install ~/dev/standards --force
   # Test in your IDE:
   # - Are instructions clear?
   # - Do commands work?
   # - Are standards helpful?
   # Then push to Git
   ```

5. **Use Bundles for Related Content**
   ```yaml
   bundles:
     - name: python-stack
       description: Complete Python development setup
       templates: [python-standards, testing-standards, test-api]
     - name: security-pack
       description: Security guidelines and tools
       templates: [security-guidelines, security-review-command]
   ```

6. **Keep Standards Updated**
   ```bash
   # Set up periodic updates
   # Weekly or when standards change:
   inskit template update --all

   # Team members stay in sync automatically
   ```

### Troubleshooting

**Problem: "Repository not found" error**
```bash
# Check Git authentication
git clone <repo-url>  # Try manually

# For private repos, ensure:
# - SSH keys configured: ssh -T git@github.com
# - Or credentials stored: gh auth login
```

**Problem: "Conflicts detected" during update**
```bash
# Check what changed
inskit template list --verbose

# Option 1: Keep local changes
inskit template update <repo> --dry-run  # See what would change
# Choose "keep" for modified templates

# Option 2: Force overwrite
inskit template update <repo> --force
```

**Problem: Templates not appearing in IDE**
```bash
# Check installation
inskit template list

# Verify files exist
ls .claude/commands/  # For Claude Code

# Restart IDE if needed
```

**Problem: Namespace collision**
```bash
# Use custom namespace
inskit template install <repo-url> --as unique-name

# Each repo should have unique namespace
```

### Advanced: Template Manifest Reference

Complete `templatekit.yaml` specification:

```yaml
# Required fields
name: string                    # Repository name
description: string             # What this repo contains
version: string                 # Semantic version (e.g., "1.0.0")

# Optional fields
author: string                  # Author name or org

# Templates (required, at least one)
templates:
  - name: string               # Template identifier (alphanumeric + hyphens)
    description: string        # What this template does
    ide: string               # Target IDE: "claude", "cursor", "windsurf", "copilot"
    files:                    # One or more files
      - path: string          # Relative path in repo
        type: string          # "instruction", "command", "hook", or "template"
    tags: [string]            # Optional: for filtering

# Bundles (optional)
bundles:
  - name: string              # Bundle identifier
    description: string       # What this bundle includes
    templates: [string]       # List of template names
    tags: [string]            # Optional: for filtering
```

**Validation rules:**
- Version must follow semantic versioning
- Template names must be unique
- File paths must exist in repository
- IDE must be one of: claude, cursor, windsurf, copilot
- Bundle templates must reference existing template names

## 💡 Use Cases

### For Enterprise Teams

```bash
# Step 1: Download company instruction repository
inskit download --from git@github.com:company/instructions

# Step 2: In your project, browse and install with TUI
cd /path/to/project
inskit install
# - Select company standards or project-specific guidelines
# - Choose which AI tools to install to
# - Install to current project
# - Commit .instructionkit/ and tool directories to Git
# - Team members automatically get the same setup!
```

### For Open Source Projects

```bash
# Maintainers: Set up project guidelines
cd your-project
inskit download --from https://github.com/project/instructions
inskit install
# Select "contributing", "code-style", etc.
# Commit to Git so all contributors get them

# Contributors: Clone and get instructions automatically
git clone https://github.com/project/repo
cd repo
# Instructions are already there in .cursor/rules/, .claude/rules/, etc.
# Just start coding with AI assistance!
```

### For Personal Productivity

```bash
# Build your personal library
inskit download --from ~/Documents/my-instructions
inskit download --from https://github.com/awesome/prompts

# In each project, pick what you need
cd my-project
inskit install
# Search, filter, and install what's relevant for this project

# Test new instructions locally before publishing
inskit download --from ./instruction-drafts --force
inskit install  # test them out in your current project
```

### For Education

```bash
# Instructors: Set up course template
inskit download --from https://github.com/university/course-materials
cd course-template
inskit install
# Select course-wide coding standards
# Commit and share template repo with students

# Students: Assignment-specific guidance
cd assignment-1
inskit install
# Select assignment-specific instructions
# AI assistants now follow assignment requirements
```

## 🛠 Requirements

- **Python:** 3.10 or higher
- **Git:** Installed and accessible from command line (only for Git repository sources)
- **AI Tool:** At least one of: Cursor, GitHub Copilot, Windsurf, or Claude Code

## 📋 Supported AI Tools

All tools use **project-level installation** with tool-specific directories:

| Tool               | Project Path            | File Extension | Status             |
| ------------------ | ----------------------- | -------------- | ------------------ |
| **Claude Code**    | `.claude/rules/`        | `.md`          | ✅ Fully Supported |
| **Cursor**         | `.cursor/rules/`        | `.mdc`         | ✅ Fully Supported |
| **Windsurf**       | `.windsurf/rules/`      | `.md`          | ✅ Fully Supported |
| **GitHub Copilot** | `.github/instructions/` | `.md`          | ✅ Fully Supported |

**Note:** All paths are relative to your project root. InstructionKit automatically detects the project root by looking for `.git/`, `pyproject.toml`, `package.json`, etc.

## 🤝 Contributing

We welcome community contributions of all sizes. Before you get started:

- 📘 Read the [Contributing Guide](CONTRIBUTING.md) for setup, coding standards, and PR expectations
- 🤝 Review the [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community respectful and inclusive
- 🐛 [Report a bug](https://github.com/troylar/instructionkit/issues/new?template=bug_report.yml) using the guided template
- 💡 [Request a feature](https://github.com/troylar/instructionkit/issues/new?template=feature_request.yml) and tell us how it helps your workflow

When you're ready to contribute code:

1. Fork the repo or create a feature branch
2. Run `invoke quality` and `invoke test` locally
3. Open a pull request using the template and link any related issues
4. Expect an automatic review request thanks to CODEOWNERS—feedback is collaborative and friendly

Curious where to start? Check out [good first issues](https://github.com/troylar/instructionkit/issues?q=is%3Aopen+label%3A%22good+first+issue%22) or start a [discussion](https://github.com/troylar/instructionkit/discussions) to explore ideas.

## 📬 Contact

- **Author:** Troy Larson
- **Email:** [troy@calvinware.com](mailto:troy@calvinware.com)

### Development Setup

```bash
# Clone repository
git clone https://github.com/troylar/instructionkit.git
cd instructionkit

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e .[dev]
```

### Common Development Tasks

```bash
# List all available tasks
invoke --list

# Run tests
invoke test                    # Run all tests
invoke test --verbose          # Verbose output
invoke test --coverage         # With coverage report
invoke test-unit               # Unit tests only
invoke test-integration        # Integration tests only

# Code quality
invoke quality                 # Run all checks
invoke quality --fix           # Auto-fix issues
invoke lint --fix              # Fix linting issues
invoke format                  # Format code
invoke typecheck               # Type checking

# Build and install
invoke clean                   # Clean build artifacts
invoke build                   # Build package
invoke install                 # Install package

# Utilities
invoke count                   # Count lines of code
invoke version                 # Show version
invoke tree                    # Show project structure
```

### Manual Testing

```bash
# Run all tests manually
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_models.py

# Run with coverage
pytest --cov=instructionkit --cov-report=html
```

See **[DEVELOPMENT.md](DEVELOPMENT.md)** for complete development guide including:

- Detailed task documentation
- Testing strategies
- Code style guidelines
- Debugging tips
- Release process
- Contributing guidelines

## 🗺 Roadmap

- [x] **Version Control:** Pin to tags, track branches, or lock to commits ✅ v0.2.0
- [x] **Template Sync System:** Repository-based template distribution with namespace isolation ✅ v0.4.0
- [x] **Template Validation:** Health checks, modification detection, version tracking ✅ v0.4.0
- [x] **Interactive Conflict Resolution:** Prompts before overwriting files ✅ v0.4.0
- [ ] **Cross-IDE Template Conversion:** Automatic template format conversion for different IDEs
- [ ] **Interactive Template Selection:** TUI for browsing and selecting templates
- [ ] **Template Variables:** Support for dynamic instruction content with variables
- [ ] **Instruction Search:** Search across all available instructions by content
- [ ] **Dependency Management:** Automatic installation of instruction dependencies
- [ ] **Remote Catalogs:** Centralized instruction catalogs for discovery
- [ ] **Instruction Content Validation:** AI-powered validation and linting of instruction content
- [ ] **Export/Backup:** Export installed instructions for backup or migration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:

- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Textual](https://textual.textualize.io/) - Interactive TUI
- [PyYAML](https://pyyaml.org/) - YAML parsing

---

<div align="center">

**Made with ❤️ for the AI coding community**

[Report Bug](https://github.com/troylar/instructionkit/issues) • [Request Feature](https://github.com/troylar/instructionkit/issues)

</div>
