# Implementation Plan: Git-Based Repository Versioning

**Branch**: `001-git-repo-versioning` | **Date**: 2025-10-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-git-repo-versioning/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature enables users to download instruction repositories with specific Git references (tags, branches, commits), install instructions with version tracking, and automatically update only branch-based instructions while keeping tag/commit-based instructions pinned. Multiple versions of the same repository can coexist in the library, and name collisions across repositories are handled gracefully.

## Technical Context

**Language/Version**: Python 3.10-3.13 (minimum 3.10)
**Primary Dependencies**: GitPython (for Git operations), Typer (CLI), Rich (output), Textual (TUI), PyYAML (config)
**Storage**: Filesystem-based (~/.instructionkit/library/ for repos, project/.instructionkit/installations.json for tracking)
**Testing**: pytest with unit and integration tests, minimum 80% coverage
**Target Platform**: Cross-platform (Linux, macOS, Windows)
**Project Type**: Single project (CLI tool)
**Performance Goals**: Download operations under 30s for typical repos, update operations under 10s for <100 instructions
**Constraints**: Offline-capable (core features work without internet), local-first, project-level installations only
**Scale/Scope**: Support dozens of repository versions in library, hundreds of installed instructions per project

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with InstructionKit Constitution v1.1.0:

- [x] **GitHub Issue**: Work tied to GitHub issue (will create before implementation starts)
- [x] **CLI-First Design**: Feature accessible via `inskit download --ref <ref>`, `inskit update`, `inskit install` commands
- [x] **Local-First**: Downloads stored locally, updates use local git operations, works offline after initial download
- [x] **Project-Level Scoping**: Installations remain project-level, version tracking added to installations.json
- [x] **Multi-Tool Support**: No changes to AI tool integrations, version tracking is storage-layer feature
- [x] **Type Safety**: All new code will include type hints and pass mypy strict mode
- [x] **Testing**: Unit tests for version detection, integration tests for download/update workflows, target 80%+ coverage
- [x] **User Experience**: Clear version display in TUI, update progress indication, confirmation for ambiguous operations
- [x] **Simplicity**: Extends existing git_operations and storage modules, no new abstractions needed

**Violations**: None

## Project Structure

### Documentation (this feature)

```text
specs/001-git-repo-versioning/
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
├── core/
│   ├── models.py           # [MODIFY] Add source_ref, source_ref_type to InstallationRecord
│   ├── repository.py       # [EXISTING] No changes needed
│   ├── git_operations.py   # [MODIFY] Add ref detection, versioned download/update
│   ├── checksum.py         # [EXISTING] No changes needed
│   └── conflict_resolution.py  # [EXISTING] May need minor updates for collision handling
├── storage/
│   ├── library.py          # [MODIFY] Support versioned namespaces (repo@ref)
│   └── tracker.py          # [MODIFY] Track ref type, filter updateable instructions
├── cli/
│   ├── main.py             # [EXISTING] No changes
│   ├── download.py         # [MODIFY] Add --ref flag for version specification
│   ├── install.py          # [MODIFY] Display version info in prompts
│   ├── install_new.py      # [MODIFY] Display version info in TUI
│   ├── update.py           # [MODIFY] Add ref-type filtering, specific instruction updates
│   ├── list.py             # [MODIFY] Display version info for library/installations
│   └── [other commands]    # [EXISTING] No changes
├── tui/
│   └── installer.py        # [MODIFY] Display repository version in instruction list
└── utils/
    └── [existing utilities] # [EXISTING] No changes

tests/
├── unit/
│   ├── test_models.py      # [MODIFY] Test new InstallationRecord fields
│   ├── test_git_operations.py  # [MODIFY] Test ref detection and versioned operations
│   ├── test_library.py     # [MODIFY] Test versioned namespace handling
│   └── test_tracker.py     # [MODIFY] Test ref-type filtering
└── integration/
    ├── test_library.py     # [MODIFY] Test multi-version coexistence
    ├── test_download_versioned.py  # [NEW] Test download with --ref flag
    ├── test_update_selective.py    # [NEW] Test selective update behavior
    └── test_upgrade_flow.py        # [NEW] Test version upgrade workflow
```

**Structure Decision**: Single project structure maintained. All changes are extensions to existing modules (core, storage, cli) following the established architecture. No new top-level directories needed.

## Complexity Tracking

**No violations** - this feature extends existing architecture without introducing new complexity patterns.

---

## Phase 0: Outline & Research

### Research Questions

The following unknowns need investigation before design:

1. **Git Reference Detection**: How to programmatically determine if a ref is a tag, branch, or commit hash?
2. **GitPython API**: What GitPython APIs support cloning/pulling with specific refs? How to detect ref types?
3. **Namespace Strategy**: How to format versioned namespaces (e.g., `repo@v1.0.0` vs `repo_v1.0.0`) to avoid filesystem issues?
4. **Update Detection**: How to efficiently check if a remote branch has changes without full clone/pull?
5. **Collision UX**: What's the best CLI/TUI pattern for prompting users during name collisions?
6. **Version Display**: How to clearly show version info in TUI's existing table layout?

### Research Tasks

Research agents will investigate:

- **Task 1**: GitPython reference detection and versioned clone/pull operations
- **Task 2**: Filesystem-safe namespace formatting for Git refs (handling special chars like `/`, `:`)
- **Task 3**: Efficient remote branch change detection (fetch vs full pull)
- **Task 4**: CLI/TUI UX patterns for versioned selections and collision resolution
- **Task 5**: Best practices for version display in terminal tables (Rich library patterns)

**Output**: `research.md` with all decisions documented

---

## Phase 1: Design & Contracts

### Prerequisites

- Phase 0 research complete
- All NEEDS CLARIFICATION items resolved

### Data Model Updates

**Key Entities** (from spec):

1. **Repository Version** → Represented in filesystem as library namespace
   - Namespace format: `{owner}/{repo}@{ref}` (e.g., `troylar/examples@v1.0.0`)
   - Metadata: stored in existing instructionkit.yaml within each version

2. **Installation Record** → Updates to existing `InstallationRecord` in models.py
   - Add fields: `source_ref: str`, `source_ref_type: RefType`
   - Enum: `RefType` with values TAG, BRANCH, COMMIT

3. **Reference Type** → New Enum in models.py
   - `RefType(Enum)`: TAG = "tag", BRANCH = "branch", COMMIT = "commit"

### API Contracts

**CLI Commands** (contracts between CLI and core modules):

1. **Download with Ref**
   ```python
   # cli/download.py
   @app.command()
   def download(
       source: str,
       ref: Optional[str] = None,  # New parameter: tag, branch, or commit
       destination: Optional[str] = None
   ) -> None
   ```

2. **Update Command**
   ```python
   # cli/update.py
   @app.command()
   def update(
       instruction_name: Optional[str] = None,  # Specific instruction to update
       from_repo: Optional[str] = None,  # Source repo filter for collisions
       all: bool = False  # Update all (default behavior)
   ) -> None
   ```

3. **List with Version Info**
   ```python
   # cli/list.py - Extend existing commands to show version info
   # No signature changes, output format includes version column
   ```

**Internal Contracts** (between modules):

1. **git_operations.py**
   ```python
   def detect_ref_type(repo_url: str, ref: str) -> RefType:
       """Determine if ref is tag, branch, or commit hash."""
       ...

   def clone_at_ref(repo_url: str, destination: Path, ref: Optional[str]) -> RefType:
       """Clone repository at specific ref, return detected ref type."""
       ...

   def pull_if_branch(repo_path: Path, ref: str, ref_type: RefType) -> bool:
       """Pull updates only if ref_type is BRANCH, return True if updated."""
       ...
   ```

2. **library.py**
   ```python
   def get_versioned_namespace(repo_identifier: str, ref: str) -> str:
       """Generate filesystem-safe namespace for repo@ref."""
       ...

   def list_repository_versions(repo_identifier: str) -> list[tuple[str, RefType]]:
       """List all downloaded versions of a repository."""
       ...
   ```

3. **tracker.py**
   ```python
   def get_updatable_instructions(project_root: Path) -> list[InstallationRecord]:
       """Return instructions with ref_type=BRANCH (mutable references)."""
       ...

   def find_instructions_by_name(
       project_root: Path,
       instruction_name: str
   ) -> list[InstallationRecord]:
       """Find all installations matching name (for collision resolution)."""
       ...
   ```

### Quickstart Documentation

Will generate `quickstart.md` with:
- Examples of downloading specific versions
- Update workflow scenarios (all vs selective vs specific)
- Upgrade workflow (moving from v1.0.0 to v2.0.0)
- Collision resolution examples

### Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh claude` to add:
- GitPython dependency
- RefType enum
- Version tracking concepts

**Outputs**:
- `data-model.md` - Entity definitions and relationships
- `contracts/cli-contracts.md` - CLI command signatures
- `contracts/module-contracts.md` - Internal module APIs
- `quickstart.md` - User-facing workflow examples
- `.claude/rules/instructionkit-dev-guide.md` - Updated with new technology

---

## Phase 2: Task Breakdown

**Not generated by this command** - Run `/speckit.tasks` after plan approval to generate task breakdown.

---

## Post-Design Constitution Re-Check

*To be completed after Phase 1 design artifacts are generated*

- [ ] **GitHub Issue**: Verified issue exists with proper labels
- [ ] **CLI-First Design**: All commands defined in contracts/, CLI-accessible
- [ ] **Local-First**: No cloud dependencies introduced, all operations local/git-based
- [ ] **Project-Level Scoping**: Installation tracking remains project-scoped
- [ ] **Multi-Tool Support**: No tool-specific code changed, backward compatible
- [ ] **Type Safety**: All new functions/classes have type hints, mypy-compliant
- [ ] **Testing**: Test cases outlined in data-model.md covering all scenarios
- [ ] **User Experience**: Workflows in quickstart.md demonstrate clear UX
- [ ] **Simplicity**: No new abstractions, extends existing modules naturally

**Final Gate**: All checkboxes must pass before proceeding to `/speckit.tasks`
