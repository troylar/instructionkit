<div align="center">

# 🎯 InstructionKit

**Manage AI coding tool instructions from any source**

[![PyPI version](https://img.shields.io/pypi/v/instructionkit.svg)](https://pypi.org/project/instructionkit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Quick Start](#-quick-start) • [Features](#-features) • [Interactive TUI](#interactive-tui-browser) • [Library Management](#library-management) • [Usage](#-usage)

</div>

---

## 🌟 Overview

InstructionKit is a powerful CLI tool that enables developers to **browse, install, and manage** instructions for AI coding assistants. Download instruction repositories to your local library, browse them with an interactive TUI, and install exactly what you need. Whether you're standardizing your team's coding practices, sharing best practices across projects, or building a personal library of prompts, InstructionKit makes it effortless.

**Supports:** Cursor • GitHub Copilot • Windsurf • Claude Code

> **CLI name:** The command-line entry point is `inskit`. Older docs may reference `instructionkit`; use `inskit` for all commands.

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

### 🎯 **Project-Level Installation**

- All installations are project-specific
- Automatic project root detection
- Organized in tool-specific directories (`.cursor/rules/`, `.claude/rules/`, etc.)
- Clean, versioned alongside your code

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
inskit download --from https://github.com/company/instructions

# Download from local folder (for testing)
inskit download --from ./my-instructions
```

**Step 2: Browse and install with the TUI**

```bash
# Launch the interactive browser
inskit install
```

This opens a beautiful terminal UI where you can:

- 🔍 Search and filter instructions
- ☑️ Select multiple instructions with Space/Enter
- 🎯 Pick which AI tools to install to
- 📦 Install with confirmation to your project

**Step 3: Manage your library**

```bash
# See what's in your library
inskit list library

# Update to get latest changes
inskit update --all

# Remove a repository
inskit delete <repo-namespace>
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

Build your local library of instruction repositories:

```bash
# Download from Git repository
inskit download --from https://github.com/company/instructions

# Download from local folder
inskit download --from ./my-instructions

# Re-download to get latest updates
inskit download --from https://github.com/company/instructions --force
```

Your library is stored in `~/.instructionkit/library/` and organized by repository namespace.

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

# Filter by source alias/name
inskit list installed --source company
```

Shows where each instruction is installed and which tools have it.

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
- **Recommended:** Commit to Git so team members get the same setup
- Alternative: Add to `.gitignore` if instructions should be personal

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

Contributions are welcome! Here's how you can help:

1. **Report Bugs:** Open an issue describing the bug and steps to reproduce
2. **Suggest Features:** Open an issue with your feature request
3. **Submit PRs:** Fork the repo, make your changes, and submit a pull request

## 📬 Contact

- **Author:** Troy Larson
- **Email:** [troy@calvinware.com](mailto:troy@calvinware.com)

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/instructionkit.git
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
