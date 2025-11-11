<div align="center">

# 🎯 InstructionKit

**Distribute and sync coding standards, AI tool configurations, and MCP servers across your team**

[![CI](https://github.com/troylar/instructionkit/actions/workflows/ci.yml/badge.svg)](https://github.com/troylar/instructionkit/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/troylar/instructionkit/branch/main/graph/badge.svg)](https://codecov.io/gh/troylar/instructionkit)
[![PyPI version](https://img.shields.io/pypi/v/instructionkit.svg)](https://pypi.org/project/instructionkit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Works with:** Claude Code • Claude Desktop • Cursor • GitHub Copilot • Windsurf

</div>

---

## What is InstructionKit?

InstructionKit is a CLI tool for distributing and managing AI coding assistant configurations across teams:

- **📋 Templates**: Share coding standards, slash commands, and IDE configurations from Git repositories
- **🔌 MCP Servers**: Distribute and manage Model Context Protocol server configurations
- **🔄 Sync**: Keep your team aligned with single-command updates
- **✅ Safe**: Built-in validation, automatic backups, conflict resolution

> **Note:** Commands use `inskit` (short for InstructionKit)

---

## 🚀 Quick Start

### Install

```bash
pip install instructionkit
```

### Templates: Share Coding Standards (30 seconds)

```bash
# Create a template repository with examples
inskit template init my-standards

# Install it locally
cd my-standards
inskit template install . --as demo

# Your IDE now has coding standards in .claude/rules/demo.*
```

### MCP: Configure AI Tool Servers (2 minutes)

```bash
# Install MCP server configurations from a repository
inskit mcp install https://github.com/company/mcp-servers --as backend

# Configure credentials securely (stored in gitignored .env)
inskit mcp configure backend

# Sync to AI tools (Claude Desktop, Cursor, Windsurf)
inskit mcp sync --tool all
```

---

## Core Features

### 🎨 Template System

Distribute any IDE-specific content from Git repositories:

- **Coding Standards** → `.claude/rules/` (instructions for AI)
- **Slash Commands** → `.claude/commands/` (accessible as `/command-name`)
- **IDE Hooks** → Pre/post prompt automation
- **Any Configuration** → Snippets, settings, etc.

**Key Commands:**
```bash
inskit template install <repo> --as <namespace>  # Install templates
inskit template list                             # Show installed templates
inskit template update <namespace>               # Update to latest version
inskit template uninstall <namespace>            # Remove templates
```

[📖 Full Template Documentation →](docs/templates.md)

### 🔌 MCP Server Management

Manage Model Context Protocol servers across your team:

- **Share Configurations** → Distribute MCP server setups via Git
- **Secure Credentials** → Store secrets in gitignored `.env` files
- **Multi-Tool Sync** → One command syncs to Claude Desktop, Cursor, Windsurf
- **Environment Resolution** → Automatically inject credentials at sync time

**Key Commands:**
```bash
inskit mcp install <repo> --as <namespace>       # Install MCP configs
inskit mcp configure <namespace>                 # Set up credentials
inskit mcp sync --tool all                       # Sync to AI tools
inskit mcp list                                  # Show installed servers
```

[📖 Full MCP Documentation →](docs/mcp.md)

---

## Why InstructionKit?

### For Teams

✅ **Consistency** - Everyone uses the same standards and tools
✅ **Onboarding** - New members get configured in minutes
✅ **Compliance** - Enforce security policies and code review checklists
✅ **No Secrets in Git** - Credentials stay local, configs are shared

### For Individuals

✅ **Portable** - Same setup across all your machines
✅ **Composable** - Mix company + team + personal configurations
✅ **Discoverable** - Install templates from any Git repository
✅ **Safe** - Automatic backups, conflict resolution, validation

---

## Real-World Example

Here's how a team at ACME Corp uses InstructionKit:

```bash
# 1. Everyone installs company security policies (global, applies to all projects)
inskit template install https://github.com/acme/security-policy --as acme-security --scope global

# 2. Backend team members clone their project
git clone https://github.com/acme/backend-api.git && cd backend-api

# 3. Install team-specific templates (project scope)
inskit template install https://github.com/acme/backend-standards --as backend
inskit template install https://github.com/acme/python-patterns --as python

# 4. Install and configure MCP servers (for enhanced AI capabilities)
inskit mcp install https://github.com/acme/mcp-servers --as backend-mcp
inskit mcp configure backend-mcp
inskit mcp sync --tool claude

# Done! IDE now has:
# - Global security rules (all projects)
# - Backend coding standards (this project)
# - Python patterns (this project)
# - MCP servers configured (Claude Desktop, Cursor, etc.)
```

Team members update everything with:
```bash
inskit template update --all
inskit mcp update --all
```

---

## Documentation

| Guide | Description |
|-------|-------------|
| [**Templates**](docs/templates.md) | Comprehensive guide to the template system |
| [**MCP Servers**](docs/mcp.md) | Managing Model Context Protocol servers |
| [**CLI Reference**](docs/cli-reference.md) | Complete command reference |
| [**Advanced Usage**](docs/advanced.md) | Scopes, namespaces, conflict resolution |
| [**Creating Templates**](docs/creating-templates.md) | How to build your own template repositories |

---

## Project vs Global Scope

InstructionKit supports two installation scopes:

| Scope | Where Files Go | When Active | Best For |
|-------|---------------|-------------|----------|
| **Project** (default) | `<project>/.claude/rules/`<br>`<project>/.instructionkit/` | Only in that project | Team practices, project standards |
| **Global** | `~/.claude/rules/`<br>`~/.instructionkit/` | All projects | Personal tools, company policies |

**Example:**
```bash
# Global: Company-wide security policy (applies everywhere)
inskit template install https://github.com/company/security --as security --scope global

# Project: Team-specific patterns (only this project)
cd ~/projects/backend-api
inskit template install https://github.com/team/backend-patterns --as backend
```

Your IDE gets **both**: global templates (always available) + project templates (context-specific).

---

## What Can You Distribute?

### Templates

Any IDE-specific content from Git repositories:

- Coding standards and style guides
- Security checklists and compliance rules
- Custom slash commands (accessible as `/command-name`)
- Code review templates
- Architecture decision records (ADRs)
- Testing patterns and strategies
- IDE automation hooks (pre-prompt, post-prompt)

### MCP Server Configurations

Model Context Protocol server setups for enhanced AI capabilities:

- Database access (PostgreSQL, MySQL, SQLite)
- API integrations (GitHub, Jira, Slack)
- File system access with proper permissions
- Custom tools and commands
- Development environment connections

---

## Installation & Setup

### Requirements

- Python 3.10 or higher
- Git (for cloning template repositories)
- One of: Claude Code, Claude Desktop, Cursor, GitHub Copilot, or Windsurf

### Install InstructionKit

```bash
# Using pip
pip install instructionkit

# Verify installation
inskit --version
```

### Quick Configuration

```bash
# Check which AI tools are installed
inskit tools

# Create your first template repository
inskit template init my-standards

# Install and test it
cd my-standards
inskit template install . --as demo

# View installed templates
inskit template list
```

---

## Common Use Cases

### Scenario 1: New Team Member Onboarding

```bash
# Install company standards (once per machine)
inskit template install https://github.com/company/standards --as company --scope global

# Clone team project
git clone https://github.com/team/project.git && cd project

# Install project-specific templates
inskit template install https://github.com/team/backend-standards --as backend

# Set up MCP servers
inskit mcp install https://github.com/team/mcp-servers --as team-mcp
inskit mcp configure team-mcp
inskit mcp sync --tool all
```

### Scenario 2: Applying Templates to Existing Project

```bash
# You're working on a project, discover useful templates
cd ~/projects/my-api

# Install templates immediately
inskit template install https://github.com/owasp/security-templates --as owasp

# Templates are now in .claude/rules/owasp.*
# AI assistant immediately knows these security patterns
```

### Scenario 3: Solo Developer / Personal Use

```bash
# Install your personal tools globally (applies to all projects)
inskit template install https://github.com/yourname/my-tools --as personal --scope global

# Done! All your projects now have your preferred templates
```

---

## Development

### Running Tests

```bash
# Run all tests
invoke test

# Run with coverage
invoke test --coverage

# Code quality checks
invoke quality

# Auto-fix linting issues
invoke lint --fix
```

### Project Structure

```
instructionkit/
├── ai_tools/          # AI tool integrations (Claude, Cursor, etc.)
├── cli/               # CLI commands
├── core/              # Core business logic
│   ├── mcp/          # MCP server management
│   └── template/     # Template system
├── storage/           # Data persistence
└── utils/             # Utilities

tests/
├── unit/              # Unit tests
└── integration/       # Integration tests
```

---

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`invoke test`)
5. **Commit** (`git commit -m 'feat: add amazing feature'`)
6. **Push** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/troylar/instructionkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/troylar/instructionkit/discussions)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

<div align="center">

**Made with ❤️ for AI-powered development teams**

</div>
