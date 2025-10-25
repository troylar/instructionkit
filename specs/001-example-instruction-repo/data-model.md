# Data Model: Example Instruction Repository

**Feature**: Example Instruction Repository
**Phase**: 1 - Design & Structure
**Date**: 2025-10-24

## Overview

This document defines the structure of the `instructionkit.yaml` file and associated content files for the example repository. The schema follows the existing InstructionKit library format specification to ensure compatibility with existing `inskit` commands.

---

## Repository Metadata Schema

### instructionkit.yaml (Root Level)

```yaml
# Repository identification
name: string              # Human-readable repository name
description: string       # 1-2 sentence description of repository purpose
version: string           # Semantic version (MAJOR.MINOR.PATCH)
author: string            # Author name or organization

# Instruction definitions
instructions:             # Array of instruction objects
  - name: string          # Unique identifier (kebab-case)
    description: string   # 1-2 sentence description
    file: string          # Relative path to markdown file
    tags: array<string>   # Category and context tags
```

### Field Specifications

**name** (repository level):
- Format: Free-form string
- Example: "InstructionKit Official Examples"
- Purpose: Display name in TUI and listings

**description** (repository level):
- Format: 1-2 sentences, <200 characters
- Example: "Curated instruction examples for common development scenarios across Python, JavaScript, testing, API design, security, and more."
- Purpose: Helps users understand repository purpose before downloading

**version** (repository level):
- Format: Semantic versioning (X.Y.Z)
- Initial: "1.0.0"
- Increment rules:
  - MAJOR: Breaking changes to instruction format or removal of instructions
  - MINOR: New instructions added or significant content updates
  - PATCH: Typo fixes, minor clarifications
- Purpose: Users can track updates via `inskit update`

**author** (repository level):
- Format: Free-form string
- Example: "Troy Larson / InstructionKit"
- Purpose: Attribution and contact reference

**instructions** (array):
- Each element represents one instruction file
- Order in array determines display order in TUI (important for prioritization)

**name** (instruction level):
- Format: kebab-case, lowercase, alphanumeric + hyphens
- Must be unique within repository
- Examples: `python-best-practices`, `react-component-guide`, `api-design-principles`
- Purpose: Unique identifier for installation tracking

**description** (instruction level):
- Format: 1-2 sentences, <150 characters
- Should explain WHAT instruction covers, not how to use it
- Examples:
  - "Modern Python coding standards including type hints, naming conventions, and structure"
  - "RESTful API design principles covering resource naming, HTTP methods, and response patterns"
- Purpose: Display in TUI search results, helps users decide to install

**file** (instruction level):
- Format: Relative path from repository root
- Convention: `instructions/<name>.md`
- Must exist in repository
- Examples: `instructions/python-best-practices.md`
- Purpose: InstructionKit reads this file when installing

**tags** (instruction level):
- Format: Array of lowercase strings (kebab-case if multi-word)
- Minimum: 1 tag (primary category)
- Recommended: 2-4 tags
- Tag categories:
  - **Primary category** (required): `python`, `javascript`, `testing`, `security`, `api-design`, `documentation`, `git`
  - **Framework/tool**: `fastapi`, `react`, `pytest`, `typescript`
  - **Context**: `frontend`, `backend`, `full-stack`, `async`
  - **Practice**: `best-practices`, `patterns`, `conventions`, `guidelines`
- Examples:
  - `[python, backend, style, best-practices]`
  - `[javascript, frontend, react, components]`
  - `[testing, python, unit-testing, pytest]`
- Purpose: Filtering and search in TUI

---

## Complete Example: instructionkit.yaml

```yaml
name: InstructionKit Official Examples
description: Curated instruction examples for common development scenarios across Python, JavaScript, testing, API design, security, documentation, and git workflows.
version: 1.0.0
author: Troy Larson / InstructionKit

instructions:
  # Python Category (3 instructions)
  - name: python-best-practices
    description: Modern Python coding standards including type hints, naming conventions, structure, and documentation
    file: instructions/python-best-practices.md
    tags: [python, backend, style, best-practices]

  - name: python-async-patterns
    description: Async/await patterns for modern Python including FastAPI, asyncio, and error handling
    file: instructions/python-async-patterns.md
    tags: [python, async, backend, fastapi, patterns]

  - name: pytest-testing-guide
    description: Pytest patterns including fixtures, parametrization, mocking, and test organization
    file: instructions/pytest-testing-guide.md
    tags: [testing, python, unit-testing, pytest, best-practices]

  # JavaScript Category (2 instructions)
  - name: javascript-modern-patterns
    description: Modern JavaScript patterns including ES6+, async/await, modules, and functional programming
    file: instructions/javascript-modern-patterns.md
    tags: [javascript, frontend, es6, patterns, async]

  - name: react-component-guide
    description: React functional components and hooks including useState, useEffect, custom hooks, and composition
    file: instructions/react-component-guide.md
    tags: [javascript, frontend, react, components, hooks]

  # API Design Category (1 instruction)
  - name: api-design-principles
    description: RESTful API design principles covering resource naming, HTTP methods, status codes, and response patterns
    file: instructions/api-design-principles.md
    tags: [api-design, rest, backend, best-practices]

  # Security Category (2 instructions)
  - name: security-guidelines
    description: Security coding patterns including input validation, authentication, secrets management, and common vulnerability prevention
    file: instructions/security-guidelines.md
    tags: [security, backend, frontend, best-practices]

  - name: security-owasp-checklist
    description: OWASP Top 10 checklist for developers with specific code patterns to prevent common vulnerabilities
    file: instructions/security-owasp-checklist.md
    tags: [security, owasp, checklist, best-practices]

  # Documentation Category (1 instruction)
  - name: documentation-standards
    description: Code documentation guidelines including docstrings, comments, README structure, and API documentation
    file: instructions/documentation-standards.md
    tags: [documentation, best-practices, style]

  # Git Category (1 instruction)
  - name: git-commit-conventions
    description: Conventional commit message format including types, scopes, descriptions, and breaking change notation
    file: instructions/git-commit-conventions.md
    tags: [git, workflow, conventions, best-practices]

  # Bonus (TypeScript)
  - name: typescript-best-practices
    description: TypeScript coding standards including type definitions, generics, utility types, and strict mode configuration
    file: instructions/typescript-best-practices.md
    tags: [typescript, javascript, frontend, backend, type-safety]

  # Bonus (Docker)
  - name: docker-best-practices
    description: Docker best practices including Dockerfile optimization, multi-stage builds, security, and image size reduction
    file: instructions/docker-best-practices.md
    tags: [docker, devops, deployment, best-practices]
```

**Total**: 12 instructions across 7 required categories + 2 bonus = meets 10-15 requirement

---

## Instruction File Structure (Markdown)

### Template for instructions/*.md Files

```markdown
# [Instruction Title]

[1-2 sentence overview explaining what this instruction covers and why it matters for AI-assisted coding]

## Core Guidelines

### 1. [First Guideline Name]

[2-3 sentences explaining the rule clearly and specifically]

**Example**:
\`\`\`[language]
# Good
[code showing correct pattern]

# Avoid
[code showing what not to do]
\`\`\`

### 2. [Second Guideline Name]

[Continue pattern for 3-7 total guidelines]

### [N]. [Final Guideline Name]

[Last guideline]

## Quick Reference

- [ ] [Actionable checklist item 1]
- [ ] [Actionable checklist item 2]
- [ ] [Actionable checklist item 3]
[... up to 7 items max]
```

### Content Constraints

- **Length**: 400-600 words (acceptable range: 300-800)
- **Code examples**: Minimum 2 per instruction, maximum 5
- **Guidelines**: 3-7 core guidelines (cognitive limit)
- **Tone**: Imperative, specific, measurable
- **Format**: Markdown with syntax-highlighted code blocks
- **Language tags**: Always include for code blocks (```python, ```javascript, etc.)

---

## Repository Directory Structure

```text
troylar/instructionkit-examples/
├── README.md                        # User-facing documentation
├── LICENSE                          # MIT License
├── TESTING.md                       # Validation test results (80% adherence log)
├── CONTRIBUTING.md                  # How to improve or add instructions
├── instructionkit.yaml              # This schema
└── instructions/
    ├── python-best-practices.md
    ├── python-async-patterns.md
    ├── pytest-testing-guide.md
    ├── javascript-modern-patterns.md
    ├── react-component-guide.md
    ├── api-design-principles.md
    ├── security-guidelines.md
    ├── security-owasp-checklist.md
    ├── documentation-standards.md
    ├── git-commit-conventions.md
    ├── typescript-best-practices.md
    └── docker-best-practices.md
```

---

## Validation Rules

### Schema Validation

When InstructionKit CLI downloads repository, it validates:

1. **instructionkit.yaml exists** at repository root
2. **Required fields present**: name, description, version, author, instructions
3. **Version format**: Matches semver pattern (X.Y.Z where X, Y, Z are integers)
4. **Unique instruction names**: No duplicates in instructions array
5. **File paths exist**: Each `file` value points to existing file in repository
6. **Tags non-empty**: Each instruction has at least 1 tag

### Content Quality Checklist (Manual)

Before considering instruction "done":

- [ ] Length between 300-800 words (target 400-600)
- [ ] Contains 2-5 code examples with good/avoid pairs
- [ ] Has 3-7 core guidelines
- [ ] Includes Quick Reference checklist
- [ ] Language is imperative and specific
- [ ] No tool-specific references (works with all AI tools)
- [ ] Tested with 80%+ guideline adherence (see TESTING.md)

---

## Tag Taxonomy (Complete List)

### Primary Categories (Required - Pick 1+)
- `python`
- `javascript`
- `typescript`
- `testing`
- `security`
- `api-design`
- `documentation`
- `git`

### Frameworks & Tools
- `fastapi`
- `react`
- `pytest`
- `docker`

### Context Tags
- `frontend`
- `backend`
- `full-stack`
- `async`
- `devops`

### Practice Tags
- `best-practices`
- `patterns`
- `conventions`
- `guidelines`
- `checklist`
- `type-safety`
- `style`

### Technology-Specific
- `es6`
- `hooks`
- `rest`
- `owasp`
- `unit-testing`
- `workflow`
- `components`
- `deployment`

**Usage**: Each instruction gets 2-4 tags, mixing categories for discoverability.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | TBD | Initial release with 12 instructions across 7 categories |

---

## Migration / Update Strategy

When updating examples (future versions):

**MINOR version bump** (1.1.0, 1.2.0):
- Add new instructions
- Significantly expand existing instruction content
- Add new tags or categories
- User action: `inskit update --all` to fetch new content

**PATCH version bump** (1.0.1, 1.0.2):
- Fix typos or grammar
- Clarify existing guidelines without changing meaning
- Update code examples for accuracy
- User action: Optional update, no breaking changes

**MAJOR version bump** (2.0.0):
- Remove instructions
- Rename instruction files (breaks existing installations)
- Restructure schema in incompatible way
- User action: Review changelog, may need to reinstall

---

## Implementation Notes

This schema requires NO changes to InstructionKit CLI - it follows the existing library format. The data model is purely content structure in the example repository.

**Next Step**: Create quickstart.md to guide users through using these examples.
