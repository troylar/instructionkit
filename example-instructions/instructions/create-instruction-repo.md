# Creating InstructionKit-Compatible Repositories

This guide will help you create your own InstructionKit-compatible repository to share AI coding instructions with your team or the community.

## Repository Structure

Your repository needs a specific structure that InstructionKit can understand:

```
my-instructions/
├── instructionkit.yaml          # Required: Repository metadata
├── instructions/                # Required: Instruction files
│   ├── instruction-1.md
│   ├── instruction-2.md
│   └── instruction-3.md
└── README.md                    # Optional: Documentation
```

## The instructionkit.yaml File

This is the heart of your repository. It defines metadata and lists all available instructions.

### Minimal Example

```yaml
name: My Instructions
description: A collection of coding instructions
version: 1.0.0

instructions:
  - name: python-style
    description: Python coding standards
    file: instructions/python-style.md
    tags:
      - python
      - style
```

### Full Example with Bundles

```yaml
name: Enterprise Coding Standards
description: Company-wide coding standards and best practices
version: 1.0.0
author: Engineering Team
repository: https://github.com/company/instructions

instructions:
  - name: python-style
    description: Python coding standards and conventions
    file: instructions/python-style.md
    tags:
      - python
      - style
      - backend

  - name: testing-practices
    description: Unit testing and integration testing guidelines
    file: instructions/testing-practices.md
    tags:
      - testing
      - quality

  - name: api-design
    description: RESTful API design principles
    file: instructions/api-design.md
    tags:
      - api
      - backend
      - design

  - name: react-patterns
    description: React component patterns and best practices
    file: instructions/react-patterns.md
    tags:
      - react
      - frontend
      - javascript

bundles:
  - name: python-backend
    description: Complete Python backend development setup
    instructions:
      - python-style
      - testing-practices
      - api-design
    tags:
      - python
      - backend

  - name: full-stack
    description: Full-stack development standards
    instructions:
      - python-style
      - testing-practices
      - api-design
      - react-patterns
    tags:
      - fullstack
```

### YAML Field Definitions

**Top-level fields:**
- `name` (required): Repository name
- `description` (required): Brief description of the repository
- `version` (required): Semantic version (e.g., "1.0.0")
- `author` (optional): Author name or team
- `repository` (optional): Git repository URL

**Instruction fields:**
- `name` (required): Unique identifier for the instruction
- `description` (required): Brief description shown in listings
- `file` (required): Path to the markdown file (relative to repo root)
- `tags` (optional): Array of tags for filtering

**Bundle fields:**
- `name` (required): Unique identifier for the bundle
- `description` (required): Brief description of what's included
- `instructions` (required): Array of instruction names to include
- `tags` (optional): Array of tags for filtering

## Writing Instruction Files

Instruction files are markdown documents that will be installed into AI coding tools. They should be clear, specific, and actionable.

### Best Practices for Instructions

1. **Be Specific**: Provide clear, actionable guidance
2. **Use Examples**: Show concrete code examples
3. **Keep Context**: Remember these will be used by AI assistants
4. **Structure Well**: Use headings, lists, and code blocks
5. **Stay Focused**: Each instruction should have a single purpose

### Example Instruction Template

```markdown
# [Instruction Name]

[Brief overview of what this instruction helps with]

## Context

[When and why to use this instruction]

## Guidelines

1. **[Principle 1]**: [Explanation]
   - [Detail or example]
   - [Detail or example]

2. **[Principle 2]**: [Explanation]
   - [Detail or example]

## Code Examples

### Good Example
\`\`\`python
# Example showing the correct approach
def process_data(items: list[dict]) -> list[dict]:
    """Process items with proper error handling."""
    return [item for item in items if item.get('valid')]
\`\`\`

### What to Avoid
\`\`\`python
# Example showing what NOT to do
def process_data(items):
    return [x for x in items if x['valid']]  # May raise KeyError
\`\`\`

## Key Takeaways

- [Important point 1]
- [Important point 2]
- [Important point 3]
```

## Creating Bundles

Bundles allow users to install multiple related instructions at once. They're perfect for:

- **Onboarding**: New team member setup
- **Project Types**: Frontend, backend, full-stack setups
- **Technology Stacks**: Python + FastAPI + PostgreSQL
- **Roles**: Junior developer, senior developer standards

### Bundle Strategy

Group instructions that:
1. Are commonly used together
2. Form a complete workflow
3. Apply to a specific technology stack
4. Match a team role or seniority level

## Testing Your Repository

### Local Testing

Before publishing, test your repository locally:

```bash
# List available instructions
instructionkit list available --repo ./my-instructions

# Install an instruction
instructionkit install python-style --repo ./my-instructions --scope project

# Install a bundle
instructionkit install python-backend --bundle --repo ./my-instructions
```

### Validation Checklist

- [ ] `instructionkit.yaml` is valid YAML
- [ ] All `file` paths in YAML exist
- [ ] All instruction names are unique
- [ ] All bundle instruction references exist
- [ ] Markdown files render properly
- [ ] Tags are meaningful and consistent
- [ ] Test installation works locally

## Publishing Your Repository

### Option 1: Git Repository (Recommended)

1. Create a Git repository (GitHub, GitLab, Bitbucket, etc.)
2. Push your instructions
3. Users install with:
   ```bash
   instructionkit install <name> --repo https://github.com/you/repo
   ```

### Option 2: Local Distribution

For teams without Git access or for testing:

```bash
# Users can install from any local path
instructionkit install <name> --repo /path/to/instructions
instructionkit install <name> --repo ./shared/instructions
```

## Version Management

Follow semantic versioning in your `instructionkit.yaml`:

- **Major** (1.0.0 → 2.0.0): Breaking changes, major rewrites
- **Minor** (1.0.0 → 1.1.0): New instructions, non-breaking additions
- **Patch** (1.0.0 → 1.0.1): Fixes, typos, clarifications

## Real-World Examples

### Enterprise Team Repository

```
company-instructions/
├── instructionkit.yaml
├── instructions/
│   ├── python-style-guide.md
│   ├── code-review-checklist.md
│   ├── security-guidelines.md
│   ├── api-versioning.md
│   ├── database-migrations.md
│   └── deployment-process.md
└── README.md
```

### Personal Productivity Library

```
my-coding-helpers/
├── instructionkit.yaml
├── instructions/
│   ├── git-commit-messages.md
│   ├── documentation-templates.md
│   ├── debugging-checklist.md
│   └── refactoring-patterns.md
└── README.md
```

### Open Source Project

```
project-instructions/
├── instructionkit.yaml
├── instructions/
│   ├── contributing.md
│   ├── architecture-overview.md
│   ├── testing-guide.md
│   └── release-process.md
└── README.md
```

## Advanced Features

### Dynamic Tags

Use tags strategically for filtering:

```yaml
instructions:
  - name: async-patterns
    description: Async/await patterns in Python
    file: instructions/async-patterns.md
    tags:
      - python
      - async
      - advanced
      - performance
```

Users can filter by tag:
```bash
instructionkit list available --repo <url> --tag python
instructionkit list available --repo <url> --tag advanced
```

### Multiple Bundles Per Instruction

Instructions can appear in multiple bundles:

```yaml
bundles:
  - name: python-basics
    instructions:
      - python-style
      - testing-practices

  - name: python-advanced
    instructions:
      - async-patterns
      - performance-tuning

  - name: full-python-stack
    instructions:
      - python-style
      - testing-practices
      - async-patterns
      - performance-tuning
      - api-design
```

## Maintenance Tips

1. **Keep Instructions Updated**: Review and update regularly
2. **Gather Feedback**: Ask users what's helpful or confusing
3. **Version Carefully**: Document breaking changes
4. **Use Clear Names**: Make instruction names self-explanatory
5. **Document Changes**: Keep a CHANGELOG.md

## Getting Help

- **InstructionKit Docs**: https://github.com/troylar/instructionkit
- **Report Issues**: https://github.com/troylar/instructionkit/issues
- **Examples**: Check the `example-instructions/` folder

## Quick Start Checklist

- [ ] Create folder structure
- [ ] Write `instructionkit.yaml`
- [ ] Create at least one instruction in `instructions/`
- [ ] Test locally with `instructionkit list available --repo .`
- [ ] Test installation with `instructionkit install <name> --repo .`
- [ ] Create bundles if needed
- [ ] Add README.md with usage instructions
- [ ] Push to Git repository
- [ ] Share with your team!

---

**Remember**: The goal is to help AI coding assistants provide better, more consistent help to developers. Focus on clarity, specificity, and actionable guidance.
