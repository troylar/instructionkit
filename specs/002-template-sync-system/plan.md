# Implementation Plan: Template Sync System

**Branch**: `002-template-sync-system` | **Date**: 2025-11-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-template-sync-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The Template Sync System enables teams to maintain consistent coding standards, commands, and workflows across multiple projects by installing and synchronizing template repositories. Teams can share templates via GitHub (public or private), install them at project or global level, and keep them updated as standards evolve. The system supports all major AI coding assistants (Cursor, Claude Code, Windsurf, GitHub Copilot) with cross-IDE command consistency.

## Technical Context

**Language/Version**: Python 3.10+ (targeting 3.10-3.13)
**Primary Dependencies**:
- GitPython (Git operations for cloning/updating template repositories)
- PyYAML (manifest parsing)
- Typer (CLI framework - existing)
- Rich (terminal UI - existing)
- Existing InstructionKit dependencies (ai_tools, storage, core modules)

**Storage**:
- Template repositories: `~/.instructionkit/templates/` (new directory structure)
- Installation tracking: Project-level `.instructionkit/template-installations.json` (new tracking file)
- Global templates: `~/.instructionkit/global-templates/` (optional global installation directory)

**Testing**: pytest (existing), with new test modules for template operations
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single Python package (extending existing InstructionKit structure)
**Performance Goals**:
- Template repository installation <1 minute for typical repos (<50MB, <100 templates)
- Update operations <30 seconds for checking and applying changes
- List operations <1 second for displaying installed templates

**Constraints**:
- Must work with existing Git credential helpers (no custom auth)
- Must not break existing instruction repository functionality
- Soft limits: warn at 100 templates or 50MB per repository
- Interactive prompts required for conflict resolution (no silent overwrites)

**Scale/Scope**:
- Support 10+ template repositories per project
- Handle template repos with up to 100 templates
- Support 50+ projects using same global templates
- Cross-IDE consistency for 4 AI tools initially (Cursor, Claude Code, Windsurf, GitHub Copilot)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with InstructionKit Constitution v1.1.0:

- [ ] **GitHub Issue**: Work tied to GitHub issue (created with proper labels)
- [x] **CLI-First Design**: Feature accessible via `inskit` commands: `inskit template install`, `inskit template update`, `inskit template list`, `inskit template uninstall`
- [x] **Local-First**: Core functionality works offline after initial clone (browse, list, install from local cache)
- [x] **Project-Level Scoping**: Templates installed to project directories (`.cursor/templates/`, `.claude/templates/`, etc.) with tracking in `.instructionkit/`
- [x] **Multi-Tool Support**: Detects and installs templates for all supported AI tools, converting format as needed
- [x] **Type Safety**: All code will include type hints and pass mypy strict mode
- [x] **Testing**: Unit tests planned for template operations, integration tests for Git operations and installations
- [x] **User Experience**: Progress indicators during install/update, interactive conflict resolution prompts, clear summaries
- [x] **Simplicity**: Extends existing storage/ai_tools patterns, single responsibility per module

**Violations** (if any, document in Complexity Tracking section below): None

**Note on Global Templates**: While Constitution III specifies project-level scoping for instructions, templates are a meta-layer that generate project-level artifacts. Global templates serve as defaults that projects can override, maintaining project-level precedence. This is consistent with the spirit of project-level scoping.

## Project Structure

### Documentation (this feature)

```text
specs/002-template-sync-system/
├── plan.md              # This file
├── research.md          # Phase 0: Git operations, manifest format, IDE template mappings
├── data-model.md        # Phase 1: Template entities, installation records
├── quickstart.md        # Phase 1: Quick start guide for users
├── contracts/           # Phase 1: CLI command contracts
│   └── cli-commands.yaml
└── tasks.md             # Phase 2: Not created by /speckit.plan
```

### Source Code (repository root)

```text
instructionkit/
├── cli/
│   ├── template.py            # New: Template subcommand group
│   ├── template_install.py    # New: Install command
│   ├── template_update.py     # New: Update command
│   ├── template_list.py       # New: List command
│   └── template_uninstall.py  # New: Uninstall command
├── core/
│   ├── models.py              # Extended: Add template-related models
│   ├── template_repository.py # New: Template repo parsing and validation
│   └── template_manifest.py   # New: Manifest schema and loading
├── storage/
│   ├── template_library.py    # New: Template library management
│   └── template_tracker.py    # New: Installation tracking
├── ai_tools/
│   ├── base.py                # Extended: Add template installation methods
│   ├── template_converter.py  # New: Convert templates between IDE formats
│   └── [existing tool files]  # Extended: Add template support
└── utils/
    └── git_helpers.py         # New: Git operations (clone, pull, credential handling)

tests/
├── unit/
│   ├── test_template_manifest.py
│   ├── test_template_repository.py
│   ├── test_template_converter.py
│   └── test_template_tracker.py
└── integration/
    ├── test_template_install.py
    ├── test_template_update.py
    └── test_template_git_operations.py
```

**Structure Decision**: Single project structure extending existing InstructionKit package. Template functionality is added as a new CLI command group with supporting modules in core, storage, and ai_tools. This maintains consistency with existing instruction repository architecture while clearly separating template-specific logic.

## Complexity Tracking

No Constitution violations requiring justification.

## Phase 0: Research & Technical Decisions

### Research Tasks

The following technical unknowns require research before detailed design:

1. **Template Manifest Format**
   - Research: What structure best describes templates, their dependencies, and IDE mappings?
   - Investigate: YAML schema for template repository manifest (similar to instructionkit.yaml but for templates)
   - Deliverable: Manifest schema specification

2. **Git Operations with Credential Helpers**
   - Research: How to use GitPython with existing credential helpers (no custom token storage)
   - Investigate: Git credential.helper configuration, SSH key support, HTTPS auth
   - Deliverable: Git operations best practices

3. **IDE Template Format Conversion**
   - Research: Differences in command/skill formats across Cursor (.mdc), Claude Code (.md), Windsurf (.md), Copilot (.md)
   - Investigate: Variable substitution, path handling, metadata differences
   - Deliverable: Conversion mapping specification

4. **Conflict Detection Strategy**
   - Research: File comparison methods (checksum vs. content diff)
   - Investigate: When to prompt user (always, only on content change, only on manual edits)
   - Deliverable: Conflict detection algorithm

5. **Progress Feedback Implementation**
   - Research: Rich library progress indicators for CLI operations
   - Investigate: Per-template messages, summary tables, spinner vs. progress bar
   - Deliverable: UX pattern for feedback

### Output

All research findings will be consolidated in `research.md` with:
- Decision made
- Rationale
- Alternatives considered
- Example code/configuration where applicable

## Phase 1: Design & Contracts

### Data Model (data-model.md)

Key entities to be designed:

1. **TemplateRepository**
   - Fields: name, version, source_url, manifest_path, templates[], bundles[]
   - Relationships: Contains Templates and TemplateBundles
   - Validation: Manifest exists, version format, URL format

2. **Template**
   - Fields: name, description, file_paths[], tags[], dependencies[], ide_specific
   - Relationships: Part of TemplateRepository, may depend on other Templates
   - State: source (in repo) → installed (in project)

3. **TemplateInstallationRecord**
   - Fields: template_name, source_repo, source_version, installed_path, scope (project/global), installed_at, checksum
   - Relationships: Links installed templates back to source
   - Validation: Path exists, checksum matches

4. **TemplateBundle**
   - Fields: name, description, template_names[], tags[]
   - Relationships: References multiple Templates
   - Purpose: Install multiple related templates together

### CLI Contracts (contracts/cli-commands.yaml)

Commands to be designed:

1. `inskit template install <repo-url> [--scope project|global] [--select]`
   - Input: GitHub URL, installation scope, optional template selection
   - Output: Progress messages, final summary with counts
   - Behavior: Clone repo, validate manifest, install templates, track installation

2. `inskit template update [repo-name] [--all]`
   - Input: Optional specific repo or update all
   - Output: Change summary, conflict prompts if needed
   - Behavior: Pull latest, detect conflicts, prompt user, update files

3. `inskit template list [--scope project|global] [--format json]`
   - Input: Optional scope filter, optional JSON output
   - Output: Table of installed templates or JSON
   - Behavior: Read tracking files, display installations

4. `inskit template uninstall <repo-name> [--scope project|global]`
   - Input: Repository name, scope
   - Output: Confirmation prompt, removal summary
   - Behavior: Remove files, update tracking

### Quickstart Guide (quickstart.md)

Quick start documentation covering:
- Installing first template repository
- Browsing available templates
- Installing templates to a project
- Updating templates
- Using templates across multiple IDEs

### Agent Context Update

After design is complete, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will update `.claude/rules/` (or equivalent) with new template-related technologies and patterns.

## Phase 2: Task Generation

Phase 2 is handled by the `/speckit.tasks` command, which will:
- Generate dependency-ordered tasks in `tasks.md`
- Break down implementation into testable units
- Assign priorities based on user story priorities
- Create acceptance criteria for each task

This plan document stops here. Execute `/speckit.tasks` to proceed to task generation.

## Notes

### Integration with Existing InstructionKit

Templates build on top of existing instruction repository infrastructure:
- Reuse `ai_tools/` detection and installation patterns
- Extend `storage/` tracking mechanisms
- Follow `cli/` command structure conventions
- Mirror `core/models.py` entity patterns

### Key Differences from Instructions

| Aspect | Instructions | Templates |
|--------|-------------|-----------|
| **Purpose** | AI coding guidelines | Reusable project artifacts (commands, configs, docs) |
| **Source** | Downloaded once, rarely updated | Actively synchronized as standards evolve |
| **Installation** | Project-level only | Project-level with optional global defaults |
| **IDE Support** | Install as-is for detected IDE | Convert format per IDE if needed |
| **Tracking** | `installations.json` | `template-installations.json` (separate tracking) |
| **Conflict Handling** | Rename/skip/overwrite | Interactive prompts (required by spec) |

### Risk Mitigation

1. **Git Authentication Complexity**: Rely on existing Git credential helpers, provide clear error messages if credentials fail
2. **Cross-Platform Path Handling**: Use `pathlib` for all path operations, test on Windows/Mac/Linux
3. **Large Repository Performance**: Implement soft limits with warnings, consider shallow clones for very large repos
4. **IDE Format Compatibility**: Start with simple format mapping, extend as needed based on user feedback
