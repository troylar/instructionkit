# Implementation Plan: Configuration Package System

**Branch**: `004-config-package` | **Date**: 2025-11-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-config-package/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable users to bundle multiple AI configuration components (MCP servers, instructions, hooks, slash commands, and custom resources) into shareable packages. Packages use IDE-agnostic manifests that translate to IDE-specific formats during installation, with secure credential management via template-based MCP configs. Support package creation, installation, versioning, updates, and cross-project tracking with a main registry system.

## Technical Context

**Language/Version**: Python 3.10+ (minimum 3.10, support 3.10-3.13)
**Primary Dependencies**: PyYAML (manifest parsing), Rich/Textual (TUI), Typer (CLI), existing ai-config-kit modules
**Storage**: JSON files (registry, package tracker) + YAML (manifests) + filesystem (.instructionkit/ structure)
**Testing**: pytest with unit and integration tests, minimum 80% coverage
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single Python package extending existing ai-config-kit codebase
**Performance Goals**: Package install <5 seconds, scan/registry rebuild <2 seconds for 100 projects
**Constraints**: Offline-capable, no external services, streaming for large files (>10MB), checksum validation
**Scale/Scope**: 100+ packages per library, 50+ projects tracked, 200MB max resource size, semantic versioning

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with InstructionKit Constitution v1.1.0:

- [x] **GitHub Issue**: Work tied to GitHub issue #24 (https://github.com/troylar/instructionkit/issues/24)
- [x] **CLI-First Design**: Commands: `aiconfig package install`, `aiconfig package create`, `aiconfig package update`, `aiconfig package list`, `aiconfig scan` (with TUI and non-interactive modes)
- [x] **Local-First**: All operations work offline; packages in `~/.instructionkit/library/`, manifests, and registry are local files
- [x] **Project-Level Scoping**: Packages install to `.instructionkit/` with project-specific tracking in `packages.json`
- [x] **Multi-Tool Support**: IDE translation layer ensures packages work across Cursor, Claude Code, Windsurf, Copilot via capability registry
- [x] **Type Safety**: All new code will include type hints and pass mypy strict mode
- [x] **Testing**: Unit tests (models, utilities) + integration tests (package install/create flows) targeting 80%+ coverage
- [x] **User Experience**: Interactive TUI for browsing/creation, progress indicators, conflict prompts, credential guidance, clear error messages
- [x] **Simplicity**: Extends existing architecture (library, tracker, TUI, git ops), single-responsibility modules (manifest parser, translator, secret detector)

**Violations**: None

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
ai-config-kit/
├── core/
│   ├── models.py                    # [EXTEND] Add package-related models
│   ├── package_manifest.py          # [NEW] Package manifest parser
│   ├── version.py                   # [NEW] Semantic versioning utilities
│   └── secret_detector.py           # [NEW] Secret detection engine
│
├── storage/
│   ├── library.py                   # [EXTEND] Package support in library
│   ├── package_tracker.py           # [NEW] Package installation tracking
│   └── registry.py                  # [NEW] Main registry manager
│
├── ai_tools/
│   ├── base.py                      # [EXTEND] IDE capability declarations
│   ├── capability_registry.py       # [NEW] IDE capability definitions
│   └── translator.py                # [NEW] Component translation framework
│
├── cli/
│   ├── package_install.py           # [NEW] Package installation command
│   ├── package_create.py            # [NEW] Package creation command
│   ├── package_update.py            # [NEW] Package update command
│   ├── package_list.py              # [NEW] Package listing command
│   └── scan.py                      # [NEW] Registry scan command
│
├── tui/
│   ├── package_browser.py           # [NEW] Package browsing TUI
│   └── package_creator.py           # [NEW] Package creation TUI
│
└── utils/
    ├── streaming.py                 # [NEW] Streaming file download/copy
    └── checksum.py                  # [EXTEND] Binary file checksums

tests/
├── unit/
│   ├── test_package_manifest.py     # [NEW] Manifest parsing tests
│   ├── test_version.py              # [NEW] Versioning tests
│   ├── test_secret_detector.py      # [NEW] Secret detection tests
│   ├── test_capability_registry.py  # [NEW] IDE capability tests
│   ├── test_translator.py           # [NEW] Translation tests
│   └── test_registry.py             # [NEW] Registry tests
│
└── integration/
    ├── test_package_install.py      # [NEW] End-to-end install tests
    ├── test_package_create.py       # [NEW] Package creation tests
    └── test_package_update.py       # [NEW] Update workflow tests
```

**Structure Decision**: Single Python package (Option 1) extending existing ai-config-kit architecture. Reuses existing modules (library, tracker, TUI, git ops, conflict resolution) and adds package-specific components. Maintains existing directory organization under `ai-config-kit/` with new modules integrated into appropriate subdirectories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all constitution requirements satisfied.

---

## Implementation Phases

### Phase 0: Research & Design ✅ COMPLETE

**Artifacts**:
- [research.md](research.md) - Technical decisions and rationale
- [data-model.md](data-model.md) - Complete data structures
- [contracts/cli-commands.md](contracts/cli-commands.md) - CLI interface contracts
- [quickstart.md](quickstart.md) - Developer implementation guide

**Key Decisions**:
1. **Manifest Format**: Extend `ai-config-kit.yaml` with package-specific fields (YAML)
2. **Versioning**: Use `packaging.version` for semver comparison
3. **Secret Detection**: Multi-heuristic approach with confidence scoring
4. **Translation**: Translator interface with IDE-specific implementations
5. **Storage**: JSON for tracking, YAML for manifests, filesystem for components

### Phase 1: Core Foundation

**Goal**: Implement data models, manifest parsing, and versioning

**Components**:
1. Package data models (extend `core/models.py`)
2. Package manifest parser (`core/package_manifest.py`)
3. Semantic versioning (`core/version.py`)
4. IDE capability registry (`ai_tools/capability_registry.py`)
5. Component translator framework (`ai_tools/translator.py`)

**Acceptance**:
- [ ] All models pass mypy type checking
- [ ] Unit tests for manifest parsing (valid and invalid cases)
- [ ] Version comparison works correctly (semver rules)
- [ ] IDE capabilities defined for all 4 IDEs
- [ ] Translator interface implemented

**Estimated Effort**: 3-5 days

### Phase 2: Storage & Tracking

**Goal**: Package installation tracking and cross-project registry

**Components**:
1. Package tracker (`storage/package_tracker.py`)
2. Main registry manager (`storage/registry.py`)
3. Extend library manager for packages (`storage/library.py`)
4. Checksum utilities for binary files (`utils/checksum.py`)
5. Streaming file operations (`utils/streaming.py`)

**Acceptance**:
- [ ] Package installations tracked in `packages.json`
- [ ] Main registry updates on install/uninstall
- [ ] Registry scan rebuilds from project trackers
- [ ] Large file streaming works (>10MB)
- [ ] Checksums computed for integrity validation

**Estimated Effort**: 3-4 days

### Phase 3: Secret Detection & Security

**Goal**: Detect and template secrets during package creation

**Components**:
1. Secret detector (`core/secret_detector.py`)
2. MCP template handling (extends Feature 003)
3. Credential prompting during install
4. `.env` management and gitignore validation

**Acceptance**:
- [ ] High-confidence secrets auto-templated
- [ ] Medium-confidence secrets prompt user
- [ ] Safe values preserved (URLs, booleans)
- [ ] Credentials stored in `.env` securely
- [ ] Gitignore warnings for `.env`

**Estimated Effort**: 2-3 days

### Phase 4: Package Installation

**Goal**: Install packages with all components

**Components**:
1. Package install command (`cli/package_install.py`)
2. Component installation logic
3. Conflict resolution integration
4. Progress indicators and UX
5. Registry updates

**Acceptance**:
- [ ] Install from library package spec
- [ ] Install specific version
- [ ] IDE detection and component translation
- [ ] Conflict prompts working
- [ ] Credential prompting for MCP servers
- [ ] Progress bars for long operations
- [ ] Installation tracked in project and registry

**Estimated Effort**: 4-5 days

### Phase 5: Package Creation

**Goal**: Create packages from current project

**Components**:
1. Package create command (`cli/package_create.py`)
2. Component detection in project
3. Interactive TUI for selection (`tui/package_creator.py`)
4. Manifest generation
5. Resource copying with checksums

**Acceptance**:
- [ ] Detect all packageable components
- [ ] Interactive selection via TUI
- [ ] Non-interactive mode with flags
- [ ] Secrets auto-detected and templated
- [ ] Valid manifest generated
- [ ] Package directory created with structure
- [ ] README auto-generated

**Estimated Effort**: 4-5 days

### Phase 6: Package Updates

**Goal**: Update installed packages to newer versions

**Components**:
1. Package update command (`cli/package_update.py`)
2. Version detection (compare installed vs available)
3. Conflict detection for modified files
4. Credential preservation during updates
5. Partial update support (retry failed components)

**Acceptance**:
- [ ] Check for updates across all packages
- [ ] Update specific package to version
- [ ] Detect conflicts with local modifications
- [ ] Prompt for conflict resolution
- [ ] Preserve MCP credentials
- [ ] Update tracking and registry

**Estimated Effort**: 3-4 days

### Phase 7: Package Management Commands

**Goal**: List, uninstall, info commands

**Components**:
1. Package list command (`cli/package_list.py`)
2. Package uninstall command (`cli/package_uninstall.py`)
3. Package info command (`cli/package_info.py`)
4. Scan command for registry rebuild (`cli/scan.py`)

**Acceptance**:
- [ ] List installed packages with details
- [ ] List available packages from library
- [ ] Show outdated packages
- [ ] Uninstall with credential cleanup option
- [ ] Show package details (components, metadata)
- [ ] Scan projects to rebuild registry

**Estimated Effort**: 2-3 days

### Phase 8: TUI Components

**Goal**: Interactive browsing and selection interfaces

**Components**:
1. Package browser TUI (`tui/package_browser.py`)
2. Package creator TUI (from Phase 5)
3. Integration with install/create commands

**Acceptance**:
- [ ] Browse available packages interactively
- [ ] Filter and search packages
- [ ] View package details in TUI
- [ ] Select components for installation
- [ ] Create package with interactive selection

**Estimated Effort**: 3-4 days

### Phase 9: Integration & Polish

**Goal**: End-to-end testing and UX refinement

**Components**:
1. Integration tests for all workflows
2. Error message improvements
3. Help text and documentation
4. Performance optimization
5. Edge case handling

**Acceptance**:
- [ ] 80%+ test coverage
- [ ] All integration tests pass
- [ ] All edge cases from spec handled
- [ ] CLI help text complete
- [ ] Performance targets met (<5s install, <2s scan)

**Estimated Effort**: 3-4 days

---

## Total Estimated Effort

**28-36 days** (4-6 weeks) for complete implementation

---

## Dependencies Between Phases

```
Phase 0 (Research) → Phase 1 (Core)
                  → Phase 2 (Storage)
                  → Phase 3 (Security)

Phase 1 + 2 + 3 → Phase 4 (Install)
                → Phase 5 (Create)

Phase 4 + 5 → Phase 6 (Update)
            → Phase 7 (Management)
            → Phase 8 (TUI)

All phases → Phase 9 (Integration)
```

**Critical Path**: Phase 0 → 1 → 2 → 4 → 9 (minimum viable feature)

---

## Post-Design Constitution Re-Check

Re-evaluating constitution compliance after design phase:

- [x] **GitHub Issue**: Issue #24 created and referenced
- [x] **CLI-First Design**: All features accessible via CLI commands
- [x] **Local-First**: All operations use local files, no cloud dependencies
- [x] **Project-Level Scoping**: Packages install to `.instructionkit/` in projects
- [x] **Multi-Tool Support**: Translation layer supports all 4 IDEs
- [x] **Type Safety**: All code will have type hints and pass mypy
- [x] **Testing**: Comprehensive unit and integration test plan (80%+ coverage)
- [x] **User Experience**: Progress bars, clear prompts, helpful errors
- [x] **Simplicity**: Extends existing architecture, single-responsibility modules

**Result**: ✅ All constitution requirements satisfied after design

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Secret detection false negatives | Medium | High | Conservative heuristics (template when unsure), user override |
| Registry corruption | Low | Medium | Validation + repair + rebuild from source of truth |
| Binary file conflict UX | Medium | Low | Metadata comparison + preserve both versions |
| Performance with large files | Low | Medium | Streaming for >10MB files, 200MB hard limit |
| IDE capability changes | Low | Low | Registry updates in minor versions |

### Implementation Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Scope creep | Medium | Medium | Deferred global scope, no dependency resolution |
| Complex test setup | Medium | Low | Reuse existing test fixtures, temp directories |
| MCP integration complexity | Low | Medium | Builds on Feature 003 (existing foundation) |

---

## Success Metrics

### Phase Completion Criteria

Each phase complete when:
1. All acceptance criteria met
2. Unit tests written and passing
3. Type checking passes
4. Code formatted and linted
5. PR reviewed and approved

### Feature Completion Criteria

Feature complete when:
1. All 9 phases complete
2. Integration tests passing
3. 30 success criteria from spec validated
4. 93 functional requirements implemented
5. Documentation complete (README, CHANGELOG)
6. Performance targets met

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Run `/speckit.tasks`** to generate detailed task breakdown
3. **Start Phase 1** implementation (Core Foundation)
4. **Create PR** after Phase 1-3 complete (foundation ready)
5. **Iterate** through remaining phases

---

## Artifacts Generated

This planning phase has produced:

- ✅ `plan.md` - This file (implementation plan)
- ✅ `research.md` - Technical research and decisions
- ✅ `data-model.md` - Complete data structure definitions
- ✅ `contracts/cli-commands.md` - CLI interface contracts
- ✅ `quickstart.md` - Developer implementation guide
- ⏳ `tasks.md` - Generated by `/speckit.tasks` command (next step)

**Planning Status**: ✅ COMPLETE

**Ready for**: Task generation (`/speckit.tasks`) and implementation
