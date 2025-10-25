# Tasks: Example Instruction Repository

**Input**: Design documents from `/specs/001-example-instruction-repo/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), quickstart.md (complete)

**Tests**: This feature does not require automated tests. Validation is manual via AI tool testing (80% guideline adherence).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Example Repository**: `troylar/instructionkit-examples/` (new GitHub repository)
- **InstructionKit CLI**: `instructionkit/` (existing repository, documentation updates only)

---

## Phase 1: Setup (Repository Initialization)

**Purpose**: Create GitHub repository and basic structure

- [ ] T001 Create GitHub issue for this feature with label "enhancement"
- [ ] T002 Create new GitHub repository `troylar/instructionkit-examples` (public, with description)
- [ ] T003 Clone repository locally to workspace
- [ ] T004 [P] Create MIT LICENSE file in repository root
- [ ] T005 [P] Create `.gitignore` file (standard for documentation repos)
- [ ] T006 Create `instructions/` directory for instruction markdown files
- [ ] T007 Create initial `README.md` scaffold in repository root (will be completed in Phase 6)
- [ ] T008 Create initial `instructionkit.yaml` with repository metadata (name, description, version 1.0.0, author)
- [ ] T009 Initial commit and push to GitHub

---

## Phase 2: Foundational (Content Templates & Guidelines)

**Purpose**: Establish content creation standards and templates

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 [P] Create `CONTRIBUTING.md` with guidelines for instruction improvements and PR process
- [ ] T011 [P] Create `TESTING.md` template for recording 80% adherence validation results
- [ ] T012 Create instruction template file `.templates/instruction-template.md` with structure from data-model.md
- [ ] T013 Document validation criteria checklist in `.templates/quality-checklist.md`

**Checkpoint**: Foundation ready - instruction content creation can now begin in parallel

---

## Phase 3: User Story 1 - First-Time User Discovers Value (Priority: P1) 🎯 MVP

**Goal**: Create minimum 7 instructions (1 per category) that new users can download, browse via TUI, and install to projects

**Independent Test**: Fresh InstructionKit install → download examples → browse in TUI (sees 7+ instructions with tags) → install python-best-practices → AI generates code following guidelines

###Implementation for User Story 1

**Python Category Instructions** (2 required for US1):

- [ ] T014 [P] [US1] Create `instructions/python-best-practices.md` (400-600 words: type hints, naming, docstrings, error handling, PEP 8)
- [ ] T015 [P] [US1] Create `instructions/python-async-patterns.md` (400-600 words: async/await, FastAPI patterns, asyncio, error handling)

**JavaScript Category Instructions** (1 required for US1):

- [ ] T016 [P] [US1] Create `instructions/javascript-modern-patterns.md` (400-600 words: ES6+, async/await, modules, functional patterns)

**Testing Category Instruction** (1 required for US1):

- [ ] T017 [P] [US1] Create `instructions/pytest-testing-guide.md` (400-600 words: fixtures, parametrize, mocking, test organization)

**API Design Category Instruction** (1 required for US1):

- [ ] T018 [P] [US1] Create `instructions/api-design-principles.md` (400-600 words: REST resource naming, HTTP methods, status codes, pagination)

**Security Category Instruction** (1 required for US1):

- [ ] T019 [P] [US1] Create `instructions/security-guidelines.md` (400-600 words: input validation, auth basics, secrets management, SQL injection/XSS prevention)

**Git Category Instruction** (1 required for US1):

- [ ] T020 [P] [US1] Create `instructions/git-commit-conventions.md` (400-600 words: Conventional Commits format, types, scopes, breaking changes)

**Metadata Updates**:

- [ ] T021 [US1] Update `instructionkit.yaml` with all 7 instruction entries (name, description, file path, tags per data-model.md)

**Validation (Manual Testing)**:

- [ ] T022 [US1] Validate python-best-practices: create 5-10 test prompts, test with all 4 AI tools (Cursor, Claude, Windsurf, Copilot), record 80%+ adherence in TESTING.md
- [ ] T023 [US1] Validate python-async-patterns: test prompts + 4 AI tools, record results
- [ ] T024 [US1] Validate javascript-modern-patterns: test prompts + 4 AI tools, record results
- [ ] T025 [US1] Validate pytest-testing-guide: test prompts + 4 AI tools, record results
- [ ] T026 [US1] Validate api-design-principles: test prompts + 4 AI tools, record results
- [ ] T027 [US1] Validate security-guidelines: test prompts + 4 AI tools, record results
- [ ] T028 [US1] Validate git-commit-conventions: test prompts + 4 AI tools, record results

**Integration Testing**:

- [ ] T029 [US1] Test full user flow: `inskit download --from <repo>` → verify repository clones → verify 7 instructions appear in `inskit install` TUI
- [ ] T030 [US1] Test installation: select python-best-practices in TUI → install → verify file created in `.cursor/rules/` and `.claude/rules/`
- [ ] T031 [US1] Test AI usage: open Cursor with installed instruction → test prompt → verify AI follows guidelines

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (7 instructions, all categories covered, validated, downloadable, installable)

---

## Phase 4: User Story 2 - Developer Finds Relevant Examples by Category (Priority: P2)

**Goal**: Expand to 10-12 instructions with clear multi-tag support enabling search/filter by technology stack

**Independent Test**: Download examples → search TUI for "/python" → sees all Python instructions → search "/react" → sees React instructions → search "/security" → sees security instructions

### Implementation for User Story 2

**Additional JavaScript/React Instruction**:

- [ ] T032 [P] [US2] Create `instructions/react-component-guide.md` (400-600 words: functional components, hooks - useState/useEffect/custom, composition, props)

**Additional Security Instruction**:

- [ ] T033 [P] [US2] Create `instructions/security-owasp-checklist.md` (400-600 words: OWASP Top 10 mapped to code patterns, checklist format)

**Documentation Category Instruction**:

- [ ] T034 [P] [US2] Create `instructions/documentation-standards.md` (400-600 words: docstrings, comments, README structure, API documentation)

**Bonus Instructions (bring total to 12)**:

- [ ] T035 [P] [US2] Create `instructions/typescript-best-practices.md` (400-600 words: type definitions, generics, utility types, strict mode)
- [ ] T036 [P] [US2] Create `instructions/docker-best-practices.md` (400-600 words: Dockerfile optimization, multi-stage builds, security, image size)

**Metadata Updates**:

- [ ] T037 [US2] Update `instructionkit.yaml` with 5 new instruction entries, ensuring multi-tag support (e.g., react-component-guide gets [javascript, frontend, react, components, hooks])

**Validation**:

- [ ] T038 [US2] Validate react-component-guide: test prompts + 4 AI tools, record 80%+ adherence
- [ ] T039 [US2] Validate security-owasp-checklist: test prompts + 4 AI tools, record results
- [ ] T040 [US2] Validate documentation-standards: test prompts + 4 AI tools, record results
- [ ] T041 [US2] Validate typescript-best-practices: test prompts + 4 AI tools, record results
- [ ] T042 [US2] Validate docker-best-practices: test prompts + 4 AI tools, record results

**Search/Filter Testing**:

- [ ] T043 [US2] Test TUI search: search "/python" → verify 2-3 Python instructions appear (python-best-practices, python-async-patterns, pytest-testing-guide)
- [ ] T044 [US2] Test TUI search: search "/javascript" → verify 3 JavaScript instructions appear (javascript-modern-patterns, react-component-guide, typescript-best-practices)
- [ ] T045 [US2] Test TUI search: search "/security" → verify 2 security instructions appear
- [ ] T046 [US2] Test TUI search: search "/frontend" → verify React, JavaScript, TypeScript instructions appear
- [ ] T047 [US2] Verify search results show in <30 seconds (SC-004)

**Checkpoint**: At this point, User Story 2 is complete (12 instructions total, multi-tag search working, all categories well-represented)

---

## Phase 5: User Story 3 - Team Lead Shares Examples as Starting Point (Priority: P3)

**Goal**: Complete repository documentation enabling team collaboration and instruction authoring

**Independent Test**: Clone project with installed instructions → team member gets same files via Git → team member can create custom instruction following README guidance

### Implementation for User Story 3

**Repository Documentation**:

- [ ] T048 [P] [US3] Complete `README.md` in troylar/instructionkit-examples with: installation instructions, instruction list with descriptions, how to use examples, how to create similar instructions (per quickstart.md guidance)
- [ ] T049 [P] [US3] Update `CONTRIBUTING.md` with: how to improve existing instructions, how to propose new instructions, PR process, testing requirements
- [ ] T050 [P] [US3] Finalize `TESTING.md` with all validation results from T022-T042

**InstructionKit CLI Documentation Updates**:

- [ ] T051 [US3] Update `instructionkit/README.md`: add "Quick Start with Examples" section with `inskit download --from https://github.com/troylar/instructionkit-examples` command and link to example repository
- [ ] T052 [US3] Check if `instructionkit/docs/quickstart.md` exists; if yes, add example download workflow section

**Team Collaboration Testing**:

- [ ] T053 [US3] Test Git workflow: install examples to test project → commit `.cursor/rules/`, `.claude/rules/`, `.instructionkit/` → clone to different directory → verify instructions work immediately
- [ ] T054 [US3] Test instruction authoring: follow README guidance to create test instruction → verify follows template structure → validate with checklist
- [ ] T055 [US3] Verify example repository README enables self-service instruction creation (SC-006)

**Checkpoint**: All user stories complete - repository is fully documented, team-ready, and enables self-service

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements affecting multiple instructions

- [ ] T056 [P] Proofread all 12 instruction files for typos, grammar, consistency
- [ ] T057 [P] Verify all code examples in instructions have proper syntax highlighting (language tags)
- [ ] T058 [P] Ensure all instructions meet length guidelines (300-800 words, target 400-600)
- [ ] T059 [P] Verify all instructions follow imperative tone ("Use type hints" not "Consider type hints")
- [ ] T060 Verify instructionkit.yaml schema validity: all names unique, all file paths exist, all instructions have 1+ tags
- [ ] T061 Verify repository size <5MB (performance goal from plan.md)
- [ ] T062 Create repository release v1.0.0 on GitHub with tag and release notes
- [ ] T063 Test complete download → browse → install flow with fresh InstructionKit installation
- [ ] T064 Verify all 7 success criteria pass (SC-001 through SC-007 from spec.md)
- [ ] T065 Run quickstart.md validation: follow guide as new user, verify <2 minute time-to-value

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - MVP
- **User Story 2 (Phase 4)**: Can start after Foundational, but logically after US1 for content consistency
- **User Story 3 (Phase 5)**: Depends on US1 and US2 having content to document
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - independently valuable (7 instructions across all categories)
- **User Story 2 (P2)**: No hard dependency on US1, but builds upon it (adds 5 more instructions for total of 12)
- **User Story 3 (P3)**: Depends on US1 and US2 content existing (documents the 12 instructions created)

### Within Each User Story

**User Story 1**:
- T010-T013 (Foundation) MUST complete before any content creation
- T014-T020 (Content creation) can all run in parallel (different files)
- T021 (Metadata) depends on T014-T020 complete
- T022-T028 (Validation) can run in parallel, each depends on its corresponding content file
- T029-T031 (Integration) depends on all validation passing

**User Story 2**:
- T032-T036 (Content creation) can all run in parallel
- T037 (Metadata) depends on T032-T036 complete
- T038-T042 (Validation) can run in parallel
- T043-T047 (Search testing) depends on T037 (metadata with tags)

**User Story 3**:
- T048-T050 (Repository docs) can run in parallel
- T051-T052 (CLI docs) can run in parallel with repository docs
- T053-T055 (Testing) depends on all documentation complete

### Parallel Opportunities

- All Setup tasks (T004-T008) can run in parallel after T003
- All Foundational tasks (T010-T013) can run in parallel
- All content creation within a story can run in parallel:
  - US1: T014-T020 (7 instruction files simultaneously)
  - US2: T032-T036 (5 instruction files simultaneously)
- All validation tasks within a story can run in parallel (after content exists):
  - US1: T022-T028 (7 validations simultaneously)
  - US2: T038-T042 (5 validations simultaneously)
- All Polish tasks (T056-T059) can run in parallel

---

## Parallel Example: User Story 1 Content Creation

```bash
# After Foundation (T010-T013) completes, launch all instruction creation in parallel:

Task: "Create instructions/python-best-practices.md"
Task: "Create instructions/python-async-patterns.md"
Task: "Create instructions/javascript-modern-patterns.md"
Task: "Create instructions/pytest-testing-guide.md"
Task: "Create instructions/api-design-principles.md"
Task: "Create instructions/security-guidelines.md"
Task: "Create instructions/git-commit-conventions.md"

# All 7 can be written simultaneously (different files, no dependencies)
# Then sequentially: Update instructionkit.yaml (T021) after all content exists
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T013) - CRITICAL checkpoint
3. Complete Phase 3: User Story 1 (T014-T031)
4. **STOP and VALIDATE**: Test download → browse → install independently
5. If passing: Deploy to GitHub, announce availability

**Result**: 7 high-quality instructions covering all required categories, fully validated, ready for users

### Incremental Delivery

1. Setup + Foundation → Repository exists with templates
2. Add User Story 1 → Test independently → **Release v1.0.0** (7 instructions - MVP!)
3. Add User Story 2 → Test independently → **Release v1.1.0** (12 instructions total)
4. Add User Story 3 → Test independently → **Release v1.2.0** (full documentation)
5. Each story adds value without breaking previous functionality

### Parallel Team Strategy

If multiple people are working:

1. Team completes Setup + Foundational together (sequential, small)
2. Once Foundational done (T013 complete):
   - **Person A**: Python instructions (T014, T015, T022, T023)
   - **Person B**: JavaScript instruction (T016, T024)
   - **Person C**: Testing + API instructions (T017, T018, T025, T026)
   - **Person D**: Security + Git instructions (T019, T020, T027, T028)
3. One person handles metadata (T021) after content complete
4. All test integration together (T029-T031)

---

## Notes

- **[P]** tasks = different files, no dependencies
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No automated tests - validation is manual via AI tool testing
- Commit after each task or logical group (e.g., after all US1 instructions created)
- Stop at any checkpoint to validate story independently
- This is content creation, not software development - focus on quality writing and validation
- Repository evolves independently from InstructionKit CLI (FR-012)

---

## Success Validation Checklist

Before marking feature complete, verify:

- [ ] **SC-001**: Time new user install → first instruction installed (<2 minutes) ✓ via T065
- [ ] **SC-002**: Repository contains 10-15 instructions across 7 categories ✓ (12 instructions created)
- [ ] **SC-003**: Adoption tracking (measure via GitHub insights post-launch)
- [ ] **SC-004**: Search/filter time <30 seconds ✓ via T047
- [ ] **SC-005**: All instructions demonstrate 80%+ guideline adherence ✓ via T022-T042
- [ ] **SC-006**: README enables self-service instruction creation ✓ via T055
- [ ] **SC-007**: Zero errors in download → browse → install flow ✓ via T063

---

## Total Task Count

- **Setup**: 9 tasks
- **Foundational**: 4 tasks
- **User Story 1 (P1 - MVP)**: 18 tasks (7 content + 1 metadata + 7 validation + 3 integration)
- **User Story 2 (P2)**: 16 tasks (5 content + 1 metadata + 5 validation + 5 search testing)
- **User Story 3 (P3)**: 8 tasks (3 docs + 2 CLI updates + 3 testing)
- **Polish**: 10 tasks
- **TOTAL**: 65 tasks

**Parallel Opportunities**: 35+ tasks can run in parallel (marked with [P])
**MVP Scope**: 31 tasks (Setup + Foundational + US1) = minimum viable release
**Independent Stories**: Each of 3 user stories can be validated and released independently
