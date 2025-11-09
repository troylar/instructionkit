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

### Installation Scopes: Project vs Global

**Two places to install templates:**

| Scope | Where Files Go | When Active | Best For |
|-------|---------------|-------------|----------|
| **Project** (default) | `<project>/.claude/rules/`<br>`<project>/.instructionkit/` | Only in that project directory | Project-specific standards, team practices |
| **Global** | `~/.claude/rules/`<br>`~/.instructionkit/` | All projects on your machine | Personal tools, company-wide policies |

**Example:**

```bash
# Project scope (default)
cd ~/projects/backend-api
inskit template install https://github.com/acme/backend-standards --as backend
# Files go to: ~/projects/backend-api/.claude/rules/backend.*
# Only active when working in ~/projects/backend-api/

# Global scope (use --scope global)
inskit template install https://github.com/acme/security-policy --as acme-security --scope global
# Files go to: ~/.claude/rules/acme-security.*
# Active in ALL projects
```

**Can I mix both? YES!**

```bash
# Global: Company security policy (applies to all projects)
inskit template install https://github.com/acme/security --as acme-security --scope global

# Project: Backend-specific patterns (only for this project)
cd ~/projects/backend-api
inskit template install https://github.com/acme/backend --as backend

# Your IDE now has BOTH:
# ~/.claude/rules/acme-security.* (global, always available)
# ~/projects/backend-api/.claude/rules/backend.* (project-specific)
```

**Decision Guide:**

| Install Global | Install Project |
|---------------|-----------------|
| Company security policies | Team-specific practices |
| Personal productivity tools | Project architecture patterns |
| Code review checklists (all code) | Technology-specific guides (this stack) |
| Your coding shortcuts | Experimental/testing templates |

---

## Use Cases: Starting from Zero

### Scenario 1: New Team Member Onboarding

**Context:** You just joined ACME Corp as a backend engineer.

**Step 1: Install company-wide standards (global)**
```bash
# Security policies apply to ALL your work
inskit template install https://github.com/acme-corp/security-policy --as acme-security --scope global

# Company code review checklist
inskit template install https://github.com/acme-corp/code-review --as acme-review --scope global
```

**Step 2: Clone your team's project**
```bash
cd ~/projects
git clone https://github.com/acme-corp/backend-api.git
cd backend-api
```

**Step 3: Install project-specific templates**
```bash
# Backend team API standards (only for backend projects)
inskit template install https://github.com/acme-corp/backend-team --as backend

# This project's specific templates
inskit template install https://github.com/acme-corp/api-patterns --as api
```

**Result:**
- **Global templates** (security, code review) → Available in ALL projects
- **Project templates** (backend, API) → Only in this project
- Your IDE has layered guidance: company-wide + team + project

### Scenario 2: Starting a New Project

**Context:** Creating a new Python backend service.

**Step 1: Company standards (if not already installed globally)**
```bash
# Only need to do this once on your machine
inskit template install https://github.com/company/standards --as company --scope global
```

**Step 2: Create project and install project-specific templates**
```bash
mkdir my-new-service
cd my-new-service
git init

# Python backend templates (specific to this tech stack)
inskit template install https://github.com/company/python-backend --as python-backend

# API design patterns (this service is an API)
inskit template install https://github.com/company/api-design --as api
```

**Step 3: Commit template configuration**
```bash
# Let your team get the same setup automatically
git add .instructionkit/
git commit -m "Add template configuration"
git push
```

**When teammates clone:**
```bash
git clone <repo>
cd <repo>

# Templates are NOT automatically installed, but tracked
# They can see what to install:
cat .instructionkit/template-installations.json

# Then install the same templates:
inskit template install https://github.com/company/python-backend --as python-backend
inskit template install https://github.com/company/api-design --as api
```

### Scenario 3: Solo Developer / Personal Use

**Context:** You want consistent coding habits across all your projects.

**Install everything globally:**
```bash
# Your personal coding standards (all projects)
inskit template install https://github.com/yourname/my-standards --as personal --scope global

# Community best practices (all projects)
inskit template install https://github.com/python/best-practices --as python-community --scope global

# Your productivity shortcuts (all projects)
inskit template install https://github.com/yourname/shortcuts --as shortcuts --scope global
```

**Result:**
- All your projects automatically have these templates
- No per-project setup needed
- Consistent experience everywhere

### Scenario 4: Large Organization with Multiple Teams

**Context:** ACME Corp has Platform, Backend, Frontend, and Mobile teams.

**Global (Company-Wide):**
```bash
# Everyone installs these (security, legal, compliance)
inskit template install https://github.com/acme/security-policy --as acme-security --scope global
inskit template install https://github.com/acme/code-review-standards --as acme-review --scope global
inskit template install https://github.com/acme/legal-compliance --as acme-legal --scope global
```

**Project (Team-Specific):**

**Backend Team:**
```bash
cd ~/projects/backend-service
inskit template install https://github.com/acme/backend-standards --as backend
inskit template install https://github.com/acme/python-patterns --as python
inskit template install https://github.com/acme/database-patterns --as database
```

**Frontend Team:**
```bash
cd ~/projects/web-app
inskit template install https://github.com/acme/frontend-standards --as frontend
inskit template install https://github.com/acme/react-patterns --as react
inskit template install https://github.com/acme/accessibility --as a11y
```

**Mobile Team:**
```bash
cd ~/projects/mobile-app
inskit template install https://github.com/acme/mobile-standards --as mobile
inskit template install https://github.com/acme/ios-patterns --as ios
inskit template install https://github.com/acme/android-patterns --as android
```

**Result:**
- **Global templates** same for everyone (security, review, legal)
- **Project templates** customized per team/tech stack
- No conflicts, clear separation

### Scenario 5: Selective Installation (Mix & Match)

**Context:** You work on multiple types of projects and want different templates for each.

```bash
# Global: Your personal tools (available everywhere)
inskit template install https://github.com/yourname/personal-tools --as personal --scope global

# Global: Company security (required for all projects)
inskit template install https://github.com/company/security --as security --scope global

# Project 1: Backend API
cd ~/projects/backend-api
inskit template install https://github.com/company/python-backend --as backend
inskit template install https://github.com/company/api-patterns --as api

# Project 2: Frontend Web App
cd ~/projects/web-app
inskit template install https://github.com/company/react-frontend --as frontend
inskit template install https://github.com/company/accessibility --as a11y

# Project 3: Data Science
cd ~/projects/ml-pipeline
inskit template install https://github.com/company/data-science --as ds
inskit template install https://github.com/company/ml-ops --as mlops
```

**Your IDE in each project:**

**Backend API:**
- Global: `personal.*`, `security.*`
- Project: `backend.*`, `api.*`

**Frontend Web App:**
- Global: `personal.*`, `security.*`
- Project: `frontend.*`, `a11y.*`

**Data Science:**
- Global: `personal.*`, `security.*`
- Project: `ds.*`, `mlops.*`

---

## Use Cases: Existing Projects

### Scenario 6: Joining an Existing Project with Templates

**Context:** You clone a project that already uses InstructionKit templates.

**Step 1: Clone the project**
```bash
git clone https://github.com/acme-corp/backend-api.git
cd backend-api
```

**Step 2: Check what templates the project uses**
```bash
# Look at the tracking file
cat .instructionkit/template-installations.json
```

**Output shows:**
```json
{
  "installations": [
    {
      "namespace": "backend",
      "source_repo": "https://github.com/acme-corp/backend-standards",
      "templates": ["api-design", "database-patterns", "testing-guide"]
    },
    {
      "namespace": "python",
      "source_repo": "https://github.com/acme-corp/python-standards",
      "templates": ["coding-standards", "async-patterns"]
    }
  ]
}
```

**Step 3: Install the same templates**
```bash
# Install exactly what the project uses
inskit template install https://github.com/acme-corp/backend-standards --as backend
inskit template install https://github.com/acme-corp/python-standards --as python
```

**Step 4: Verify installation**
```bash
inskit template list

# Should match what's in template-installations.json
```

**Result:**
- Your IDE now has the same templates as your teammates
- Code reviews consistent across the team
- AI assistant follows project standards

**Pro Tip:** Create a setup script for new team members:
```bash
#!/bin/bash
# setup-templates.sh
echo "Installing project templates..."
inskit template install https://github.com/acme-corp/backend-standards --as backend
inskit template install https://github.com/acme-corp/python-standards --as python
echo "✓ Templates installed. Run 'inskit template list' to verify."
```

### Scenario 7: Applying Templates to Your Current Project

**Context:** You're actively working on a project and discover a useful template repository you want to use.

**Step 1: You're working on your project**
```bash
cd ~/projects/my-api
# You're coding along, no templates installed yet
```

**Step 2: Discover a template repo**
```bash
# Maybe you found it on GitHub, or a colleague shared it
# Example: OWASP security templates
# URL: https://github.com/owasp/ai-coding-templates
```

**Step 3: Install templates to your current project**
```bash
# Install directly to your current project
inskit template install https://github.com/owasp/ai-coding-templates --as owasp

# ✓ Installed 5 templates:
#   - owasp.input-validation.md
#   - owasp.authentication.md
#   - owasp.sql-injection.md
#   - owasp.xss-prevention.md
#   - owasp.secrets-management.md
```

**Step 4: Templates are immediately available**
```bash
# Check what's installed
ls .claude/rules/
# owasp.input-validation.md
# owasp.authentication.md
# owasp.sql-injection.md
# ...

# Your AI assistant now knows these security patterns!
```

**Step 5: (Optional) Share with your team**
```bash
# Commit the installation tracking so teammates get the same templates
git add .instructionkit/template-installations.json
git commit -m "feat: add OWASP security templates"
git push

# Your team can now run the same command:
# inskit template install https://github.com/owasp/ai-coding-templates --as owasp
```

**Step 6: Apply multiple template repos**
```bash
# Add more as you discover them
inskit template install https://github.com/company/python-standards --as python
inskit template install https://github.com/team/api-patterns --as api

# Now you have:
# .claude/rules/owasp.*     (security)
# .claude/rules/python.*    (coding standards)
# .claude/rules/api.*       (API design patterns)
```

**Result:**
- Templates applied immediately to current project
- No project restructuring needed
- Can layer multiple template repos
- Team can sync by running same commands

**Common Discovery Sources:**
- GitHub search: "instructionkit templates python"
- Colleague shares a repo URL
- Company internal template registry
- Open source communities

### Scenario 8: Applying Templates to Multiple Existing Projects at Once

**Context:** You're an individual developer with a dozen Python projects and want to apply the same templates to all of them.

**Best Solution: Global Installation**
```bash
# Install templates globally - they apply to ALL projects
inskit template install https://github.com/yourname/python-standards --as python --scope global
inskit template install https://github.com/community/python-best-practices --as best-practices --scope global

# ✓ Templates now available in ALL Python projects on your machine
```

**How Global Installation Works:**
```bash
# Templates installed to ~/.claude/rules/
ls ~/.claude/rules/
# python.coding-standards.md
# python.async-patterns.md
# best-practices.error-handling.md
# best-practices.testing.md

# Work in ANY project, templates are active
cd ~/projects/project-1  # Templates active
cd ~/projects/project-2  # Templates active
cd ~/projects/project-12 # Templates active
```

**Alternative: Bulk Project Installation (if you need project-specific tracking)**

Create a script to install to specific projects:
```bash
#!/bin/bash
# apply-templates.sh

TEMPLATE_REPO="https://github.com/yourname/python-standards"
PROJECTS=(
  ~/projects/api-server
  ~/projects/data-pipeline
  ~/projects/ml-toolkit
  ~/projects/cli-app
  ~/projects/web-scraper
  ~/projects/automation-scripts
  ~/projects/discord-bot
  ~/projects/file-converter
  ~/projects/backup-utility
  ~/projects/monitoring-tool
  ~/projects/config-manager
  ~/projects/test-framework
)

for project in "${PROJECTS[@]}"; do
  echo "Installing templates in $project..."
  cd "$project"
  inskit template install "$TEMPLATE_REPO" --as python
  echo "✓ Done"
done

echo "✓ Templates installed in ${#PROJECTS[@]} projects"
```

**Run the bulk installation:**
```bash
chmod +x apply-templates.sh
./apply-templates.sh

# Output:
# Installing templates in /Users/you/projects/api-server...
# ✓ Done
# Installing templates in /Users/you/projects/data-pipeline...
# ✓ Done
# ...
# ✓ Templates installed in 12 projects
```

**When to Use Global vs. Project Installation:**

| Use Global | Use Project Installation |
|------------|-------------------------|
| Same templates for all projects | Different templates per project |
| Personal coding standards | Team-specific standards (varies by project) |
| Solo developer | Working with teams |
| Don't need to commit template config | Want to commit `.instructionkit/template-installations.json` |
| Quick setup | Explicit per-project tracking |

**Example: Mix Global and Project-Specific**
```bash
# Global: Your personal Python standards (all projects)
inskit template install https://github.com/yourname/python-standards --as personal --scope global

# Project-specific: Client requirements (only this project)
cd ~/projects/client-api
inskit template install https://github.com/client/api-standards --as client

# Result in client-api project:
# ~/.claude/rules/personal.* (global, from personal standards)
# ~/projects/client-api/.claude/rules/client.* (project-specific)
```

**Result:**
- All 12 Python projects get your standards instantly (if using global)
- Or specific projects get templates (if using script)
- Consistent coding patterns across all your projects
- Update once, applies everywhere (global) or update all projects (script)

**Updating Templates Across All Projects:**

**Option 1: Global Installation (Simple - One Command)**
```bash
# Update once, applies to all projects
inskit template update python --scope global

# ✓ All 12 projects now have the updated templates
```

**Option 2: Bulk Project Installation (Script Needed)**

Create an update script:
```bash
#!/bin/bash
# update-templates.sh

PROJECTS=(
  ~/projects/api-server
  ~/projects/data-pipeline
  ~/projects/ml-toolkit
  ~/projects/cli-app
  ~/projects/web-scraper
  ~/projects/automation-scripts
  ~/projects/discord-bot
  ~/projects/file-converter
  ~/projects/backup-utility
  ~/projects/monitoring-tool
  ~/projects/config-manager
  ~/projects/test-framework
)

for project in "${PROJECTS[@]}"; do
  if [ -d "$project" ]; then
    echo "Updating templates in $project..."
    cd "$project"
    inskit template update python
    echo "✓ Updated"
  fi
done

echo "✓ Templates updated in all projects"
```

**Run the bulk update:**
```bash
chmod +x update-templates.sh
./update-templates.sh

# Output:
# Updating templates in /Users/you/projects/api-server...
# ✓ Updated
# Updating templates in /Users/you/projects/data-pipeline...
# ✓ Updated
# ...
# ✓ Templates updated in all projects
```

**Why Global is Easier for Solo Developers:**
- **Global**: One command to install, one command to update
- **Project-specific**: Need scripts for install and update
- **Recommendation**: Use global unless you need per-project version control

### Scenario 9: Migrating an Existing Project to Templates

**Context:** You have a 2-year-old project with no templates. Want to add standards.

**Step 1: Identify what standards you need**
```bash
cd ~/projects/legacy-api

# This is a Python API project, so we need:
# - Python coding standards
# - API design patterns
# - Database best practices
# - Testing guidelines
```

**Step 2: Create a template repository (if none exists)**
```bash
cd ~/
inskit template init backend-standards --namespace backend

cd backend-standards
# Customize templates based on existing project conventions
# Add: .claude/rules/api-design.md (document current patterns)
# Add: .claude/rules/database-patterns.md (document DB conventions)
# Add: .claude/commands/run-tests.md (standardize testing)

git init
git add .
git commit -m "Initial backend standards"
git remote add origin https://github.com/yourorg/backend-standards.git
git push -u origin main
```

**Step 3: Install templates in existing project**
```bash
cd ~/projects/legacy-api

# Install your new templates
inskit template install https://github.com/yourorg/backend-standards --as backend
```

**Step 4: Commit template configuration**
```bash
git add .instructionkit/
git add .claude/  # or .cursor/, .windsurf/, etc.
git commit -m "feat: add InstructionKit templates for coding standards"
git push
```

**Step 5: Document for team**
```markdown
# Add to README.md

## Development Setup

### Templates
This project uses InstructionKit for coding standards and patterns.

1. Install InstructionKit: `pip install instructionkit`
2. Install project templates: `inskit template install https://github.com/yourorg/backend-standards --as backend`
3. Verify: `inskit template list`

Templates provide:
- Python coding standards
- API design patterns
- Database conventions
- Testing commands
```

**Result:**
- Legacy project now has modern standards
- New team members get consistent guidance
- Can evolve standards over time via template updates

### Scenario 10: Working on Multiple Client Projects

**Context:** You're a consultant working on 3 different client projects simultaneously.

**Global Setup (Your personal tools):**
```bash
# Install once - available everywhere
inskit template install https://github.com/yourname/consultant-tools --as personal --scope global
inskit template install https://github.com/yourname/productivity --as productivity --scope global
```

**Client A - FinTech Project:**
```bash
cd ~/clients/fintech-api

# Client A's security requirements (strict finance regulations)
inskit template install https://github.com/client-a/security-standards --as clienta-security

# Client A's Python standards
inskit template install https://github.com/client-a/python-patterns --as clienta-python
```

**Client B - E-commerce Project:**
```bash
cd ~/clients/ecommerce-platform

# Client B's standards (different tech stack)
inskit template install https://github.com/client-b/react-standards --as clientb-react
inskit template install https://github.com/client-b/api-design --as clientb-api
```

**Client C - Healthcare Project:**
```bash
cd ~/clients/healthcare-app

# Client C's HIPAA compliance templates
inskit template install https://github.com/client-c/hipaa-compliance --as clientc-hipaa
inskit template install https://github.com/client-c/mobile-standards --as clientc-mobile
```

**Your IDE in each project:**

**FinTech Project:**
- Global: `personal.*`, `productivity.*` (yours)
- Project: `clienta-security.*`, `clienta-python.*` (client-specific)

**E-commerce Project:**
- Global: `personal.*`, `productivity.*` (yours)
- Project: `clientb-react.*`, `clientb-api.*` (client-specific)

**Healthcare Project:**
- Global: `personal.*`, `productivity.*` (yours)
- Project: `clientc-hipaa.*`, `clientc-mobile.*` (client-specific)

**Result:**
- Personal tools available everywhere
- Each client's standards isolated to their projects
- No mixing of client requirements
- Switch projects, templates switch automatically

### Scenario 11: Inheriting a Messy Legacy Project

**Context:** Taking over a 5-year-old project with inconsistent code and no documentation.

**Step 1: Document current state with templates**
```bash
cd ~/projects/legacy-mess

# Create templates that document what you found
inskit template init legacy-api-docs --namespace legacy

cd legacy-api-docs

# Document existing patterns (even if messy)
cat > .claude/rules/current-patterns.md << 'EOF'
# Current API Patterns

## What We Have (Document Before Changing)

### Authentication
- Currently using custom JWT implementation (see auth.py)
- No refresh tokens
- Tokens expire after 24 hours

### Database
- Direct SQL queries (no ORM)
- Connection pooling via custom pool.py
- Transactions managed manually

### Error Handling
- Mix of exceptions and return codes
- Some endpoints return 200 with error in body
- No consistent error format

## What We're Moving Toward
[Add improvement plan here]
EOF

git init
git add .
git commit -m "Document current state"
git remote add origin https://github.com/yourorg/legacy-api-docs.git
git push -u origin main
```

**Step 2: Install in project**
```bash
cd ~/projects/legacy-mess
inskit template install https://github.com/yourorg/legacy-api-docs --as legacy
```

**Step 3: Add improvement templates**
```bash
# Add better standards as separate templates
inskit template install https://github.com/yourorg/modern-api-standards --as modern
```

**Your IDE now has:**
- `legacy.*` - Documents current (messy) patterns
- `modern.*` - Shows where you want to go

**Step 4: Gradually migrate**
```bash
# Update template repository as you refactor
cd ~/legacy-api-docs

# Update current-patterns.md to show progress
# Add migration-guide.md command

git add .
git commit -m "Update patterns - migrated auth to OAuth2"
git push
```

**Update in project:**
```bash
cd ~/projects/legacy-mess
inskit template update legacy
```

**Result:**
- Legacy patterns documented (don't have to remember everything)
- Clear target patterns defined
- Can track migration progress via template updates
- New team members understand both current and target state

### Scenario 12: Contributing to Open Source Projects

**Context:** You contribute to multiple open-source projects, each with different standards.

**Global (Your personal setup):**
```bash
inskit template install https://github.com/yourname/oss-contributor-tools --as personal --scope global
```

**Project: Django (Python web framework):**
```bash
cd ~/oss/django

# Install Django contribution guidelines
inskit template install https://github.com/django/contributor-templates --as django

# Your IDE now has Django's:
# - Coding standards (PEP 8 + Django conventions)
# - PR templates
# - Testing requirements
# - Documentation standards
```

**Project: React (JavaScript library):**
```bash
cd ~/oss/react

# Install React contribution guidelines
inskit template install https://github.com/facebook/react-contributor-templates --as react

# Your IDE now has React's:
# - JavaScript style guide
# - Testing with Jest
# - Commit message conventions
```

**Project: Kubernetes (Go infrastructure):**
```bash
cd ~/oss/kubernetes

# Install Kubernetes contribution guidelines
inskit template install https://github.com/kubernetes/contributor-templates --as k8s

# Your IDE now has K8s:
# - Go coding standards
# - API conventions
# - CRD development patterns
```

**Result:**
- Each OSS project has its own standards
- Switch projects → standards switch automatically
- Contributions meet project requirements
- Personal tools available everywhere

### Scenario 13: Switching Tech Stacks on Existing Project

**Context:** Migrating a project from Node.js to Python.

**Before Migration:**
```bash
cd ~/projects/api-server

# Current templates (Node.js)
inskit template list
# Shows: nodejs.*, express.*, typescript.*
```

**During Migration (Both stacks):**
```bash
# Keep Node.js templates for reference
# Add Python templates for new code
inskit template install https://github.com/company/python-standards --as python
inskit template install https://github.com/company/fastapi-patterns --as fastapi

# Your IDE now has BOTH:
# - nodejs.* (for understanding old code)
# - python.*, fastapi.* (for writing new code)
```

**After Migration Complete:**
```bash
# Remove old Node.js templates
inskit template uninstall nodejs
inskit template uninstall express
inskit template uninstall typescript

# Only Python templates remain
inskit template list
# Shows: python.*, fastapi.*

# Update project tracking
git add .instructionkit/
git commit -m "Complete migration to Python stack"
```

**Result:**
- Templates evolve with your tech stack
- Keep old standards during migration for reference
- Clean removal when migration complete

### Scenario 14: Updating Templates on Running Production Project

**Context:** Your production app needs to adopt new security standards.

**Step 1: Check current state**
```bash
cd ~/projects/production-api
inskit template list

# Shows: security.owasp-2017.md (old)
```

**Step 2: Update security template repository**
```bash
# Security team updated their repository with OWASP 2021
# https://github.com/company/security-standards updated
```

**Step 3: Preview changes before updating**
```bash
# Validate current templates first
inskit template validate

# Output shows:
# ℹ INFO: security.owasp - Newer version available (2017 → 2021)
```

**Step 4: Update templates**
```bash
inskit template update security

# Interactive prompt appears:
# ⚠️  Conflict detected for 'security.owasp'
# Local file was modified since installation
#
# Choose action:
#   [K]eep local version (ignore update)
#   [O]verwrite with new version (backup created)
#   [R]ename local and install new
#
# Your choice [k/o/r] (k): o

# Backup created: .instructionkit/backups/20251109_143052/security.owasp.md
# ✓ Updated: .claude/rules/security.owasp.md
```

**Step 5: Review changes**
```bash
# Compare old vs new
diff .instructionkit/backups/20251109_143052/security.owasp.md \
     .claude/rules/security.owasp.md

# Shows: OWASP 2021 new vulnerabilities added
```

**Step 6: Rollback if needed**
```bash
# If update breaks something, restore from backup
inskit template backup restore 20251109_143052 security.owasp.md

# Or keep both versions
inskit template backup restore 20251109_143052 security.owasp.md \
  --target .claude/rules/security.owasp-2017.md
```

**Result:**
- Production project stays current with latest standards
- Automatic backups prevent data loss
- Can rollback if update causes issues
- Team stays synchronized with security updates

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
