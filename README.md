<div align="center">

# 🎯 InstructionKit

**Manage AI coding tool instructions from any source**

[![PyPI version](https://img.shields.io/pypi/v/instructionkit.svg)](https://pypi.org/project/instructionkit/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Quick Start](#-quick-start) • [Features](#-features) • [Interactive TUI](#interactive-tui-browser) • [Library Management](#library-management) • [Usage](#-usage)

</div>

---

## 🌟 Overview

InstructionKit is a powerful CLI tool that enables developers to **browse, install, and manage** instructions for AI coding assistants. Download instruction repositories to your local library, browse them with an interactive TUI, and install exactly what you need. Whether you're standardizing your team's coding practices, sharing best practices across projects, or building a personal library of prompts, InstructionKit makes it effortless.

**Supports:** Cursor • GitHub Copilot • Windsurf • Claude Code

**New:** Interactive TUI for browsing and selecting instructions from your library!

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

### 🔍 **Scope Management**
- Install globally (available across all projects)
- Install per-project (specific to current project)
- Automatic project root detection
- Scope-aware listing and uninstall
- See installation paths for each AI tool

</td>
<td>

### 📦 **Flexible Sources**
- Download from Git repositories (GitHub, GitLab, Bitbucket, self-hosted)
- Download from local folders (perfect for testing and development)
- Support for private repositories with standard Git authentication
- Bundle support for installing multiple instructions at once

</td>
</tr>
<tr>
<td>

### 🎯 **Smart Management**
- Auto-detect installed AI coding tools
- Track all installed instructions with metadata
- Smart conflict resolution (skip, rename, overwrite)
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

## 🚀 Quick Start

### Installation

```bash
pip install instructionkit
```

### The New Way: Library + Interactive TUI

**Step 1: Download instructions to your library**

```bash
# Download from GitHub
instructionkit download --repo https://github.com/company/instructions

# Download from local folder (for testing)
instructionkit download --repo ./my-instructions
```

**Step 2: Browse and install with the TUI**

```bash
# Launch the interactive browser
instructionkit install
```

This opens a beautiful terminal UI where you can:
- 🔍 Search and filter instructions
- ☑️  Select multiple instructions with Space/Enter
- 📍 Choose installation location (Global or Project)
- 🎯 Pick which AI tools to install to
- 📦 Install with confirmation

**Step 3: Manage your library**

```bash
# See what's in your library
instructionkit list library

# Update to get latest changes
instructionkit update --all

# Remove a repository
instructionkit delete <repo-namespace>
```

### Alternative: Direct Installation

For quick one-off installs without using the library:

```bash
# Direct install (bypasses library)
instructionkit install python-best-practices --repo https://github.com/company/instructions

# See what's available from a repo
instructionkit list available --repo https://github.com/company/instructions
```

## 📖 Usage

### Library Management

<details>
<summary><b>Download Instructions to Your Library</b></summary>

Build your local library of instruction repositories:

```bash
# Download from Git repository
instructionkit download --repo https://github.com/company/instructions

# Download from local folder
instructionkit download --repo ./my-instructions

# Re-download to get latest updates
instructionkit download --repo https://github.com/company/instructions --force
```

Your library is stored in `~/.instructionkit/library/` and organized by repository namespace.

</details>

<details>
<summary><b>List Your Library Contents</b></summary>

```bash
# Show all repositories in library
instructionkit list library

# Show individual instructions
instructionkit list library --instructions

# Filter by repository
instructionkit list library --repo company
```

</details>

<details>
<summary><b>Update Library Repositories</b></summary>

```bash
# Update a specific repository
instructionkit update --namespace github.com_company_instructions

# Update all repositories in library
instructionkit update --all
```

</details>

<details>
<summary><b>Delete from Library</b></summary>

```bash
# Delete a repository (keeps installed instructions)
instructionkit delete github.com_company_instructions

# Skip confirmation
instructionkit delete github.com_company_instructions --force
```

Note: Deleting from library doesn't uninstall instructions. Use `instructionkit uninstall` for that.

</details>

### Interactive TUI Browser

<details>
<summary><b>Using the TUI to Browse and Install</b></summary>

Launch the interactive browser:

```bash
instructionkit install
```

**TUI Features:**
- **Search**: Type `/` to search by name or description
- **Filter**: Select repository from dropdown
- **Select**: Use `Space` or `Enter` to toggle instruction selection
- **Select All**: Press `Ctrl+A` or click "Select All" button
- **Installation Location**: Choose Global (user config) or Project (current folder)
- **Target Tools**: Check boxes for Cursor, Windsurf, Claude Code, etc.
- **Install**: Review summary and click "📦 Install Selected"

The TUI shows exactly where files will be installed before you confirm.

</details>

<details>
<summary><b>Install Specific Instruction by Name</b></summary>

Install directly from library without TUI:

```bash
# Install by name (opens selection if multiple matches)
instructionkit install python-style

# The command will:
# 1. Search your library for "python-style"
# 2. If found in multiple repos, ask which one
# 3. Install the selected instruction
```

</details>

### Installing Instructions

<details>
<summary><b>Global vs Project Scope</b></summary>

InstructionKit supports two installation scopes:

**Global Scope (default):**
- Instructions available across all projects
- Stored in your AI tool's global config directory
- Tracked in `~/.instructionkit/installations.json`

**Project Scope:**
- Instructions specific to the current project
- Stored in `.cursor/instructions/`, `.windsurf/instructions/`, etc. in project root
- Tracked in `.instructionkit/installations.json` in project root
- Automatically detects project root (looks for `.git`, `pyproject.toml`, `package.json`, etc.)
- Can be run from any directory within the project

```bash
# Install globally (default)
instructionkit install python-best-practices --repo https://github.com/company/instructions

# Install to current project
instructionkit install python-best-practices --repo https://github.com/company/instructions --scope project

# List shows both global and project installations
instructionkit list installed
```

</details>

### Advanced: Direct Installation (Bypasses Library)

<details>
<summary><b>Install Directly from Repository</b></summary>

For one-off installs without downloading to library first:

```bash
# Basic install (global)
instructionkit install python-best-practices --repo https://github.com/company/instructions

# Install to current project
instructionkit install python-best-practices --repo https://github.com/company/instructions --scope project

# Install to specific tool
instructionkit install python-best-practices --repo https://github.com/company/instructions --tool cursor

# Handle conflicts by renaming
instructionkit install python-best-practices --repo https://github.com/company/instructions --conflict rename

# Overwrite existing
instructionkit install python-best-practices --repo https://github.com/company/instructions --conflict overwrite
```

</details>

<details>
<summary><b>Install from Local Folder</b></summary>

```bash
# Relative path
instructionkit install python-best-practices --repo ./my-instructions

# Absolute path
instructionkit install python-best-practices --repo /path/to/instructions

# Great for testing before committing to Git
instructionkit install my-new-instruction --repo ~/Documents/instruction-drafts
```

</details>

<details>
<summary><b>Install Bundles</b></summary>

```bash
# Install a bundle of related instructions
instructionkit install python-backend --bundle --repo https://github.com/company/instructions

# This might install: python-style, testing-practices, api-design, etc.
```

</details>

### Listing & Viewing

<details>
<summary><b>List Installed Instructions</b></summary>

```bash
# Show all installed instructions (both global and project)
instructionkit list installed

# Filter by AI tool
instructionkit list installed --tool cursor

# Filter by source repository
instructionkit list installed --repo https://github.com/company/instructions
```

Shows where each instruction is installed and which tools have it.

</details>

<details>
<summary><b>List Available Instructions (Without Library)</b></summary>

Directly query a repository without downloading it:

```bash
# From Git repository
instructionkit list available --repo https://github.com/company/instructions

# From local folder
instructionkit list available --repo ./my-instructions

# Filter by tag
instructionkit list available --repo https://github.com/company/instructions --tag python

# Show only bundles
instructionkit list available --repo https://github.com/company/instructions --bundles-only
```

**Tip:** For regular use, it's better to `download` the repo to your library and browse with the TUI!

</details>

### Uninstalling Instructions

```bash
# Uninstall from all tools and scopes
instructionkit uninstall python-best-practices

# Uninstall only from project scope
instructionkit uninstall python-best-practices --scope project

# Uninstall only from global scope
instructionkit uninstall python-best-practices --scope global

# Uninstall from specific tool
instructionkit uninstall python-best-practices --tool cursor

# Skip confirmation
instructionkit uninstall python-best-practices --force
```

### Viewing Detected Tools

```bash
# See which AI coding tools are installed
instructionkit tools
```

## 📂 Storage & Tracking

InstructionKit stores everything locally:

**Library Storage:**
- Downloaded repositories: `~/.instructionkit/library/`
- Organized by repository namespace (e.g., `github.com_company_instructions/`)
- Browse offline after downloading

**Installation Tracking:**

**Global Installations:**
- Tracked in `~/.instructionkit/installations.json`
- Contains metadata for all globally installed instructions
- Persists across all projects

**Project Installations:**
- Tracked in `<project-root>/.instructionkit/installations.json`
- Contains metadata only for this project's instructions
- Created automatically when you install with `--scope project`
- Can be added to `.gitignore` or committed to share with team

The `list installed` command automatically shows instructions from both scopes when run from within a project.

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

## 💡 Use Cases

### For Enterprise Teams

```bash
# Step 1: Download company instruction repository
instructionkit download --repo git@github.com:company/instructions

# Step 2: Browse and install with TUI
instructionkit install
# - Select company-wide standards
# - Choose "Global" scope (available in all projects)
# - Select all your AI tools
# - Install!

# For project-specific instructions
cd /path/to/project
instructionkit install
# - Select project-specific guidelines
# - Choose "Project" scope
# - Install to current project only
```

### For Open Source Projects

```bash
# Contributors set up project guidelines
instructionkit download --repo https://github.com/project/instructions
instructionkit install
# Select "contributing" and choose "Project" scope

# Keep personal standards separate
instructionkit download --repo ~/my-instructions
instructionkit install
# Select personal preferences and choose "Global" scope

# Now you have both: personal global + project-specific!
```

### For Personal Productivity

```bash
# Build your personal library
instructionkit download --repo ~/Documents/my-instructions
instructionkit download --repo https://github.com/awesome/prompts

# Browse and pick what you need
instructionkit install
# Search, filter, and install your favorites globally

# Test new instructions locally before publishing
instructionkit download --repo ./instruction-drafts --force
instructionkit install  # test them out
```

### For Education

```bash
# Instructors: Set up course materials
instructionkit download --repo https://github.com/university/course-materials

# Students: Install course instructions
instructionkit install
# Select course-specific instructions with "Global" scope

# Assignment-specific guidance (per project)
cd assignment-1
instructionkit install
# Select assignment-1 instructions with "Project" scope
```

## 🛠 Requirements

- **Python:** 3.8 or higher
- **Git:** Installed and accessible from command line (only for Git repository sources)
- **AI Tool:** At least one of: Cursor, GitHub Copilot, Windsurf, or Claude Code

## 📋 Supported AI Tools

| Tool | Global Instructions | Project Instructions | Status |
|------|-------|-------|--------|
| Cursor | `~/Library/Application Support/Cursor/User/globalStorage/` | `.cursor/instructions/` | ✅ Fully Supported |
| GitHub Copilot (VS Code) | `~/Library/Application Support/Code/User/globalStorage/github.copilot/` | `.github/copilot-instructions/` | ✅ Fully Supported |
| Windsurf | `~/Library/Application Support/Windsurf/User/globalStorage/` | `.windsurf/instructions/` | ✅ Fully Supported |
| Claude Code | `~/Library/Application Support/Claude/instructions/` | `.claude/instructions/` | ✅ Fully Supported |

*Note: Paths shown are for macOS. Linux uses `~/.config/` and Windows uses `%APPDATA%/`*

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs:** Open an issue describing the bug and steps to reproduce
2. **Suggest Features:** Open an issue with your feature request
3. **Submit PRs:** Fork the repo, make your changes, and submit a pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/troylar/instructionkit.git
cd instructionkit

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=instructionkit --cov-report=html
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_install.py

# Run with coverage
pytest --cov=instructionkit
```

## 🗺 Roadmap

- [ ] **Template Variables:** Support for dynamic instruction content with variables
- [ ] **Instruction Search:** Search across all available instructions by content
- [ ] **Dependency Management:** Automatic installation of instruction dependencies
- [ ] **Version Control:** Manage multiple versions of instructions
- [ ] **Remote Catalogs:** Centralized instruction catalogs for discovery
- [ ] **Instruction Validation:** Lint and validate instruction content
- [ ] **Export/Backup:** Export installed instructions for backup or migration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [PyYAML](https://pyyaml.org/) - YAML parsing
- [GitPython](https://gitpython.readthedocs.io/) - Git operations

---

<div align="center">

**Made with ❤️ for the AI coding community**

[Report Bug](https://github.com/troylar/instructionkit/issues) • [Request Feature](https://github.com/troylar/instructionkit/issues)

</div>
