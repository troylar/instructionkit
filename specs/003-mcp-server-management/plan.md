# Implementation Plan: MCP Server Configuration Management

**Branch**: `003-mcp-server-management` | **Date**: 2025-11-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-mcp-server-management/spec.md`
**Related Issue**: #23

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add Model Context Protocol (MCP) server configuration management to InstructionKit. Enable teams to share MCP server configurations via template repositories while keeping credentials local. Support installing MCP configs from Git repos, configuring credentials securely in `.instructionkit/.env`, and syncing to multiple AI tools (Claude Desktop, Cursor, Windsurf). Include listing/validation, MCP sets for workflow-based activation, and project vs global scoping.

## Technical Context

**Language/Version**: Python 3.10+ (targeting 3.10-3.13)
**Primary Dependencies**: Typer (CLI), Rich (output), PyYAML (parsing), python-dotenv (credential management), NEEDS CLARIFICATION: JSON manipulation library for AI tool config files
**Storage**: Filesystem-based (MCP definitions in `~/.instructionkit/library/<namespace>/`, credentials in `.instructionkit/.env`, AI tool configs at standard locations)
**Testing**: pytest with fixtures, integration tests for file operations and Git cloning
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux)
**Project Type**: Single project (CLI application extending existing InstructionKit architecture)
**Performance Goals**: Install MCP template in <10 seconds, sync to AI tools in <2 seconds, list/validate operations in <1 second
**Constraints**: No network calls during sync (local-first), atomic file writes for AI tool configs, preserve existing config sections, cross-platform path handling
**Scale/Scope**: Support 10-50 MCP servers per project, 5-10 MCP sets per template, handle templates from 100+ repositories in library

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with InstructionKit Constitution v1.1.0:

- [x] **GitHub Issue**: Work tied to GitHub issue #23 (enhancement label)
- [x] **CLI-First Design**: All features accessible via `inskit mcp` subcommands (install, configure, sync, list, validate, activate, update) with non-interactive flags
- [x] **Local-First**: Core sync functionality works offline (reads from local library and `.instructionkit/.env`, no network calls during sync)
- [⚠️] **Project-Level Scoping**: Feature supports both project-level (`.instructionkit/.env` in project) AND global scoping (`--scope global` flag) per spec requirements
- [x] **Multi-Tool Support**: Feature enhances existing AI tool support by managing their MCP configurations (Claude, Cursor, Windsurf)
- [x] **Type Safety**: All models, CLI commands, and core logic will have type hints and pass mypy strict mode
- [x] **Testing**: Unit tests for models/validation/parsing, integration tests for install/sync/configure workflows, target 80%+ coverage
- [x] **User Experience**: Rich output with status indicators, progress bars for downloads, confirmation prompts for overwrite/credential updates
- [x] **Simplicity**: Single responsibility modules (mcp_manager, credential_manager, tool_syncer), reuse existing library/repository patterns

**Violations**:

- **Project-Level Scoping (Partial)**: Feature spec explicitly requires global scoping support (`--scope global` flag, FR-046 and FR-047). This is justified because MCP servers for personal productivity tools (e.g., Slack notifications, personal scripts) should be available across all projects without per-project configuration. Project-scoped MCP servers remain the default to maintain constitution compliance. Global scope is opt-in and stored in separate `~/.instructionkit/global/` directory. See Complexity Tracking section.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
instructionkit/
├── cli/
│   ├── mcp_install.py        # NEW: inskit mcp install command
│   ├── mcp_configure.py      # NEW: inskit mcp configure command
│   ├── mcp_sync.py           # NEW: inskit mcp sync command
│   ├── mcp_list.py           # NEW: inskit mcp list command
│   ├── mcp_validate.py       # NEW: inskit mcp validate command
│   ├── mcp_activate.py       # NEW: inskit mcp activate command
│   └── mcp_update.py         # NEW: inskit mcp update command
├── core/
│   ├── models.py             # EXTEND: Add MCP-related dataclasses
│   ├── repository.py         # EXTEND: Parse mcp_servers/mcp_sets from templatekit.yaml
│   └── mcp/                  # NEW: MCP-specific core logic
│       ├── manager.py        # MCP installation and library management
│       ├── credentials.py    # .env file parsing and validation
│       ├── validator.py      # MCP server validation logic
│       └── set_manager.py    # MCP set activation and tracking
├── ai_tools/
│   ├── base.py               # EXTEND: Add MCP sync methods to AITool base
│   ├── claude.py             # EXTEND: Add MCP config sync for Claude Desktop
│   ├── cursor.py             # EXTEND: Add MCP config sync for Cursor
│   ├── windsurf.py           # EXTEND: Add MCP config sync for Windsurf
│   └── mcp_syncer.py         # NEW: Cross-tool MCP synchronization orchestration
├── storage/
│   ├── library.py            # EXTEND: Add MCP template listing methods
│   └── mcp_tracker.py        # NEW: Track active MCP sets per project
└── utils/
    ├── dotenv.py             # NEW: .env file manipulation utilities
    └── atomic_write.py       # NEW: Atomic file write for AI tool configs

tests/
├── unit/
│   ├── test_mcp_models.py           # NEW: Test MCP dataclasses
│   ├── test_mcp_credentials.py      # NEW: Test .env parsing/validation
│   ├── test_mcp_validator.py        # NEW: Test MCP server validation
│   ├── test_mcp_set_manager.py      # NEW: Test set activation logic
│   └── test_mcp_syncer.py           # NEW: Test cross-tool sync logic
└── integration/
    ├── test_mcp_install.py          # NEW: Test install workflow
    ├── test_mcp_configure.py        # NEW: Test credential configuration
    ├── test_mcp_sync.py             # NEW: Test AI tool sync workflow
    └── test_mcp_lifecycle.py        # NEW: Test full install→configure→sync→activate flow
```

**Structure Decision**: Single project structure extending existing InstructionKit architecture. New CLI commands in `cli/` directory, MCP-specific core logic isolated in `core/mcp/` submodule, existing AI tool classes extended with MCP sync capabilities. No new top-level directories needed - feature integrates cleanly into existing package structure.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Global scoping support | Personal productivity MCP servers (Slack, time tracking, note-tracking) should be available across all projects without per-project duplication | Requiring per-project configuration of personal tools creates excessive friction and maintenance burden. Users would need to reconfigure the same servers in every project directory. |

---

## Phase 0: Research (COMPLETED)

**Status**: ✅ All technical unknowns resolved

**Research Document**: [research.md](research.md)

### Key Decisions

1. **JSON Library**: Use Python's built-in `json` module
   - No external dependencies
   - Preserves key order (Python 3.7+)
   - Trade-off: Comments will be lost, but acceptable for MCP configs

2. **Dotenv Library**: Use `python-dotenv`
   - Industry standard for .env file management
   - Supports multi-line values, escape sequences
   - Naming convention: UPPERCASE_WITH_UNDERSCORES

3. **Atomic File Write**: Context manager with temp file + `os.replace()`
   - Cross-platform compatible
   - Prevents corruption from crashes
   - No external dependencies

4. **Command Validation**: Use `shutil.which()`
   - Built-in since Python 3.3
   - Cross-platform, checks executability
   - No caching needed (< 1ms overhead)

5. **AI Tool Config Locations**: Documented for all platforms
   - Claude Desktop: `~/Library/Application Support/Claude/` (macOS), `%APPDATA%\Claude\` (Windows), `~/.config/Claude/` (Linux)
   - Cursor: `~/.cursor/mcp.json` (global), `.cursor/mcp.json` (project)
   - Windsurf: `~/.codeium/windsurf/mcp_config.json`

**New Dependency**: `python-dotenv>=1.0.0`

---

## Phase 1: Design & Contracts (COMPLETED)

**Status**: ✅ Data models, contracts, and quickstart guide created

### Artifacts Created

1. **Data Model** ([data-model.md](data-model.md))
   - 7 core entities defined with full type hints
   - Validation rules specified for all fields
   - Serialization methods documented
   - State transitions and relationships mapped
   - Testing strategy outlined

2. **CLI Contracts** ([contracts/cli-commands.md](contracts/cli-commands.md))
   - 7 MCP commands fully specified
   - Input/output contracts defined
   - Error cases documented with exit codes
   - JSON output schemas provided
   - Examples for common patterns

3. **Quickstart Guide** ([quickstart.md](quickstart.md))
   - Step-by-step tutorials for all workflows
   - Common use cases documented
   - Troubleshooting guide included
   - Advanced usage patterns provided

### Constitution Re-Check (Post-Design)

Re-evaluating constitution compliance after design phase:

- [x] **GitHub Issue**: Maintained (issue #23)
- [x] **CLI-First Design**: All 7 commands specified with non-interactive flags
- [x] **Local-First**: Sync operations are offline (read from local library)
- [⚠️] **Project-Level Scoping**: Still includes global scope (justified in Complexity Tracking)
- [x] **Multi-Tool Support**: Extends existing AITool classes with MCP sync methods
- [x] **Type Safety**: All models use dataclasses with full type hints, mypy compliance planned
- [x] **Testing**: Comprehensive test strategy in data-model.md, contracts specify test requirements
- [x] **User Experience**: Rich output with status indicators, confirmation prompts, progress bars planned
- [x] **Simplicity**: Single responsibility modules (mcp_manager, credentials, validator, syncer)

**No new violations introduced during design phase.** Global scoping violation remains justified.

---

## Next Phase

**Phase 2: Task Generation** (`/speckit.tasks` command)

This phase will:
- Generate `tasks.md` with dependency-ordered implementation tasks
- Break down into testable, granular work items
- Assign priorities based on user story priorities (P1, P2, P3)
- Create timeline estimates for each task

**DO NOT proceed to Phase 2 in this command.** Phase 2 is handled by `/speckit.tasks`.
