<div align="center">

# 🎯 InstructionKit

**Manage AI coding tool instructions from any source**

[![PyPI version](https://img.shields.io/pypi/v/instructionkit.svg)](https://pypi.org/project/instructionkit/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Quick Start](#-quick-start) • [Features](#-features) • [Installation](#installation) • [Usage](#-usage) • [Scope Management](#-scope-management)

</div>

---

## 🌟 Overview

InstructionKit is a powerful CLI tool that enables developers to install, manage, and share instructions for AI coding assistants. Whether you're standardizing your team's coding practices, sharing best practices across projects, or building a personal library of prompts, InstructionKit makes it effortless.

**Supports:** Cursor • GitHub Copilot • Windsurf • Claude Code

## ✨ Features

<table>
<tr>
<td width="50%">

### 📦 **Flexible Sources**
- Install from Git repositories (GitHub, GitLab, Bitbucket, self-hosted)
- Install from local folders (perfect for testing and development)
- Support for private repositories with standard Git authentication

</td>
<td width="50%">

### 🎯 **Smart Management**
- Auto-detect installed AI coding tools
- Track all installed instructions with metadata
- Smart conflict resolution (skip, rename, overwrite)
- Easy uninstall functionality

</td>
</tr>
<tr>
<td>

### 📚 **Bundle Support**
- Group related instructions into bundles
- Install multiple instructions with a single command
- Perfect for onboarding or project setup

</td>
</tr>
<tr>
<td>

### 🔍 **Scope Management**
- Install globally (available across all projects)
- Install per-project (specific to current project)
- Automatic project root detection
- Scope-aware listing and uninstall

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

### Install Your First Instruction

```bash
# Install globally (default - available across all projects)
instructionkit install python-best-practices --repo https://github.com/company/instructions

# Install to current project only
instructionkit install python-best-practices --repo https://github.com/company/instructions --scope project

# From a local folder
instructionkit install python-best-practices --repo ./my-instructions
```

### List Available Instructions

```bash
# From any source
instructionkit list available --repo https://github.com/company/instructions
instructionkit list available --repo ./my-instructions
```

### See What's Installed

```bash
instructionkit list installed
```

## 📖 Usage

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

<details>
<summary><b>Install from Git Repository</b></summary>

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

### Listing Instructions

<details>
<summary><b>List Available Instructions</b></summary>

```bash
# From Git repository
instructionkit list available --repo https://github.com/company/instructions

# From local folder
instructionkit list available --repo ./my-instructions

# Filter by tag
instructionkit list available --repo https://github.com/company/instructions --tag python

# Show only bundles
instructionkit list available --repo https://github.com/company/instructions --bundles-only

# Show only individual instructions
instructionkit list available --repo https://github.com/company/instructions --instructions-only
```

</details>

<details>
<summary><b>List Installed Instructions</b></summary>

```bash
# Show all installed instructions
instructionkit list installed

# Filter by AI tool
instructionkit list installed --tool cursor

# Filter by source repository
instructionkit list installed --repo https://github.com/company/instructions
```

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

## 📂 Installation Tracking

InstructionKit automatically tracks all installed instructions:

**Global Installations:**
- Tracked in `~/.instructionkit/installations.json`
- Contains metadata for all globally installed instructions
- Persists across all projects

**Project Installations:**
- Tracked in `<project-root>/.instructionkit/installations.json`
- Contains metadata only for this project's instructions
- Created automatically when you install with `--scope project`
- Should be added to `.gitignore` (or committed to share with team)

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
# Install company-wide standards globally (available in all projects)
instructionkit install company-standards --bundle --repo git@github.com:company/instructions

# Install project-specific instructions to current project only
instructionkit install microservices-guide --repo git@github.com:company/instructions --scope project

# Install project architecture guidelines for this specific project
instructionkit install project-architecture --repo git@github.com:company/instructions --scope project
```

### For Open Source Projects

```bash
# Contributors install project-specific guidelines
instructionkit install contributing --repo https://github.com/project/instructions --scope project

# Project maintainers can include instructions in the repo
# Contributors just run: instructionkit install project-guidelines --repo . --scope project

# Keep your personal global standards while working on the project
instructionkit install my-personal-style --repo ~/my-instructions  # global
instructionkit install project-style --repo . --scope project      # project-specific
```

### For Personal Productivity

```bash
# Build your personal library of prompts
instructionkit install my-python-helpers --repo ~/Documents/my-instructions

# Test new instructions before publishing
instructionkit install draft-instruction --repo ./instruction-drafts
```

### For Education

```bash
# Share course materials with students
instructionkit install course-101 --bundle --repo https://github.com/university/course-instructions

# Provide assignment-specific guidance
instructionkit install assignment-1 --repo https://github.com/university/course-instructions
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
git clone https://github.com/yourusername/instructionkit.git
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

[Report Bug](https://github.com/yourusername/instructionkit/issues) • [Request Feature](https://github.com/yourusername/instructionkit/issues)

</div>
