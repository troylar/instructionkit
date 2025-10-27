# Tasks: Git-Based Repository Versioning

**Feature Branch**: `001-git-repo-versioning`
**Input**: Design documents from `/specs/001-git-repo-versioning/`
**Prerequisites**: plan.md, spec.md, research.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Git versioning dependencies

- [X] T001 Add GitPython dependency to pyproject.toml (version >=3.1.45)
- [X] T002 [P] Create RefType enum in instructionkit/core/models.py
- [X] T003 [P] Add source_ref and source_ref_type fields to InstallationRecord in instructionkit/core/models.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Git operations infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement detect_ref_type() function in instructionkit/core/git_operations.py
- [X] T005 Implement validate_remote_ref() function using ls-remote in instructionkit/core/git_operations.py
- [X] T006 [P] Implement clone_at_ref() function with tag/branch/commit support in instructionkit/core/git_operations.py
- [X] T007 [P] Implement get_repo_info() helper function in instructionkit/core/git_operations.py
- [X] T008 Add error handling classes (RepositoryOperationError) in instructionkit/core/git_operations.py
- [X] T009 Implement get_versioned_namespace() function in instructionkit/storage/library.py
- [X] T010 [P] Implement list_repository_versions() function in instructionkit/storage/library.py
- [X] T011 Update InstallationRecord to_dict() and from_dict() methods to include ref fields in instructionkit/core/models.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Download Specific Repository Version (Priority: P1) 🎯 MVP

**Goal**: Users can download instruction repositories with specific Git references (tags, branches, commits) to their library

**Independent Test**: Download a repository with `--ref v1.0.0`, verify it's stored in library with correct namespace and metadata

### Implementation for User Story 1

- [X] T012 [US1] Add --ref parameter to download command in instructionkit/cli/download.py
- [X] T013 [US1] Modify download command to call validate_remote_ref() before cloning in instructionkit/cli/download.py
- [X] T014 [US1] Update download command to use clone_at_ref() with ref parameter in instructionkit/cli/download.py
- [X] T015 [US1] Update download command to use versioned namespace (repo@ref) in instructionkit/cli/download.py
- [X] T016 [US1] Add ref type detection and storage in library metadata in instructionkit/cli/download.py
- [X] T017 [US1] Add error handling for invalid refs with user-friendly messages in instructionkit/cli/download.py
- [X] T018 [US1] Update library storage to support multiple versions of same repository in instructionkit/storage/library.py
- [X] T019 [US1] Add validation to prevent duplicate downloads of same repo@ref combination in instructionkit/cli/download.py

**Checkpoint**: User Story 1 complete - users can download specific repository versions

---

## Phase 4: User Story 2 - Install Instructions with Version Tracking (Priority: P1)

**Goal**: Users can install instructions from versioned repositories and see which version each instruction came from

**Independent Test**: Install an instruction from a tagged repo, verify installation record includes source_ref and source_ref_type

### Implementation for User Story 2

- [X] T020 [US2] Update TUI installer to display repository version in instruction list in instructionkit/tui/installer.py
- [X] T021 [US2] Add version column to TUI selection table in instructionkit/tui/installer.py
- [X] T022 [US2] Update InstallationTracker.add_installation() to store source_ref and source_ref_type in instructionkit/storage/tracker.py
- [X] T023 [US2] Modify install workflow to pass ref metadata to tracker in instructionkit/cli/install_new.py
- [X] T024 [US2] Update list command to display version information for installed instructions in instructionkit/cli/list.py
- [X] T025 [US2] Add formatting for ref_type display (tag/branch/commit badges) in instructionkit/cli/list.py
- [X] T026 [US2] Handle installation from multiple versions of same repository in instructionkit/storage/tracker.py

**Checkpoint**: User Story 2 complete - installation tracking includes version information

---

## Phase 5: User Story 3 - Automatic Update Behavior Based on Ref Type (Priority: P1)

**Goal**: Branch-based instructions auto-update while tag/commit-based instructions remain stable

**Independent Test**: Install from both tag and branch, run update, verify only branch-based instruction updates

### Implementation for User Story 3

- [X] T027 [US3] Implement check_for_updates() function using fetch and SHA comparison in instructionkit/core/git_operations.py
- [X] T028 [US3] Implement pull_repository_updates() function with conflict detection in instructionkit/core/git_operations.py
- [X] T029 [US3] Implement update_if_mutable() function to update only branches in instructionkit/core/git_operations.py
- [X] T030 [US3] Implement get_updatable_instructions() in tracker to filter branch-based installations in instructionkit/storage/tracker.py
- [X] T031 [US3] Create or modify update command to call get_updatable_instructions() in instructionkit/cli/update.py
- [X] T032 [US3] Add logic to fetch updates from remote for branch-based repos in instructionkit/cli/update.py
- [X] T033 [US3] Add logic to skip immutable refs (tags/commits) with informative message in instructionkit/cli/update.py
- [X] T034 [US3] Update installation files after pulling changes from branch repos in instructionkit/cli/update.py
- [X] T035 [US3] Add update progress indication using Rich progress bars in instructionkit/cli/update.py
- [X] T036 [US3] Add conflict resolution for modified instruction files in instructionkit/cli/update.py

**Checkpoint**: User Story 3 complete - selective auto-update based on ref type works

---

## Phase 6: User Story 4 - Upgrade Pinned Instructions to New Versions (Priority: P2)

**Goal**: Users can manually upgrade instructions from one tag version to a newer tag version

**Independent Test**: Install from v1.0.0, download v2.0.0, reinstall from v2.0.0, verify upgrade in tracking

### Implementation for User Story 4

- [ ] T037 [US4] Add detection for existing installation when reinstalling same instruction in instructionkit/cli/install_new.py
- [ ] T038 [US4] Add upgrade confirmation prompt when installing newer version in instructionkit/cli/install_new.py
- [ ] T039 [US4] Update installation record with new version when upgrading in instructionkit/storage/tracker.py
- [ ] T040 [US4] Add upgrade history logging (optional) in instructionkit/storage/tracker.py
- [ ] T041 [US4] Display version diff during upgrade prompt (old → new) in instructionkit/cli/install_new.py

**Checkpoint**: User Story 4 complete - manual upgrades work with clear version tracking

---

## Phase 7: User Story 5 - Handle Instruction Name Collisions Across Repositories (Priority: P2)

**Goal**: Users can install instructions with the same name from different repositories without conflicts

**Independent Test**: Install "python-testing" from repo A, then install "python-testing" from repo B with different name

### Implementation for User Story 5

- [ ] T042 [US5] Implement find_instructions_by_name() in tracker to detect collisions in instructionkit/storage/tracker.py
- [ ] T043 [US5] Add collision detection before installation in instructionkit/cli/install_new.py
- [ ] T044 [US5] Add prompt for custom filename when collision detected in instructionkit/cli/install_new.py
- [ ] T045 [US5] Update installation logic to use custom filename if provided in instructionkit/cli/install_new.py
- [ ] T046 [US5] Display source repository in collision prompt to help user decide in instructionkit/cli/install_new.py

**Checkpoint**: User Story 5 complete - name collision handling works

---

## Phase 8: User Story 6 - Update Specific Instructions (Priority: P3)

**Goal**: Users can update individual instructions by name, with repository disambiguation for collisions

**Independent Test**: Run update with instruction name, verify only that instruction updates

### Implementation for User Story 6

- [ ] T047 [US6] Add --instruction-name parameter to update command in instructionkit/cli/update.py
- [ ] T048 [US6] Add --from-repo parameter to update command for disambiguation in instructionkit/cli/update.py
- [ ] T049 [US6] Implement filtering to update only specified instruction in instructionkit/cli/update.py
- [ ] T050 [US6] Add disambiguation prompt when name matches multiple repos in instructionkit/cli/update.py
- [ ] T051 [US6] Add validation to prevent updating tag-based instructions by name in instructionkit/cli/update.py
- [ ] T052 [US6] Display informative message when tag-based instruction update is attempted in instructionkit/cli/update.py

**Checkpoint**: User Story 6 complete - selective instruction updates work

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Testing, documentation, and improvements across all user stories

- [ ] T053 [P] Add unit test for RefType enum validation in tests/unit/test_models.py
- [ ] T054 [P] Add unit test for InstallationRecord with ref fields in tests/unit/test_models.py
- [ ] T055 [P] Add unit test for detect_ref_type() function in tests/unit/test_git_operations.py
- [ ] T056 [P] Add unit test for validate_remote_ref() function in tests/unit/test_git_operations.py
- [ ] T057 [P] Add integration test for download with --ref flag in tests/integration/test_download_versioned.py
- [ ] T058 [P] Add integration test for multi-version coexistence in tests/integration/test_library.py
- [ ] T059 [P] Add integration test for selective update behavior in tests/integration/test_update_selective.py
- [ ] T060 [P] Add integration test for version upgrade workflow in tests/integration/test_upgrade_flow.py
- [ ] T061 [P] Update CHANGELOG.md with feature description and user-facing changes
- [ ] T062 [P] Update README.md with versioning usage examples
- [ ] T063 [P] Add docstrings to all new functions following Google style
- [ ] T064 Run mypy type checking and fix any type errors
- [ ] T065 Run pytest with coverage and ensure 80%+ coverage
- [ ] T066 Run invoke quality and fix any linting/formatting issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - Can proceed in priority order: US1 (P1) → US2 (P1) → US3 (P1) → US4 (P2) → US5 (P2) → US6 (P3)
  - Or in parallel if multiple developers available
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (needs version info from downloads) - BUT can be independently tested
- **User Story 3 (P1)**: Depends on US1 and US2 (needs installations to update) - BUT independently testable
- **User Story 4 (P2)**: Depends on US1 and US2 (needs versioned downloads and installations)
- **User Story 5 (P2)**: Depends on US2 (needs installation tracking)
- **User Story 6 (P3)**: Depends on US3 (extends update functionality)

### Within Each User Story

- Setup before implementation
- Implementation before testing
- Core functionality before polish
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: T002 and T003 can run in parallel (different parts of models.py)
- Phase 2: T006 and T007, T010 can run in parallel (different functions)
- Phase 9: All test tasks (T053-T060) can run in parallel, all documentation (T061-T063) can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (download with versions)
4. Complete Phase 4: User Story 2 (install with tracking)
5. Complete Phase 5: User Story 3 (auto-update behavior)
6. **STOP and VALIDATE**: Test core versioning functionality
7. Complete Phase 9: Polish (tests and documentation)
8. Deploy/demo if ready

### Full Feature (All User Stories)

1. Complete MVP (Phases 1-5, 9)
2. Add Phase 6: User Story 4 (manual upgrades)
3. Add Phase 7: User Story 5 (collision handling)
4. Add Phase 8: User Story 6 (selective updates)
5. Update Phase 9: Add tests for US4-US6
6. Final validation and deployment

### Incremental Delivery

- **Milestone 1**: Foundational complete → Git operations ready
- **Milestone 2**: US1 complete → Can download versions
- **Milestone 3**: US2 complete → Can track installed versions
- **Milestone 4**: US3 complete → Auto-update works (MVP COMPLETE)
- **Milestone 5**: US4-6 complete → Advanced features ready
- **Milestone 6**: Polish complete → Production ready

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story delivers independent value and is testable on its own
- All new code must include type hints and pass mypy strict mode
- Minimum 80% test coverage required
- Commit after each task or logical group
- Reference GitHub issue in all commit messages
- Follow existing InstructionKit code style and patterns
- Avoid breaking changes to existing CLI commands
