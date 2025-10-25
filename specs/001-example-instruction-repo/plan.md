# Implementation Plan: Example Instruction Repository

**Branch**: `001-example-instruction-repo` | **Date**: 2025-10-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-example-instruction-repo/spec.md`

## Summary

Create a curated GitHub repository (`troylar/instructionkit-examples`) containing 10-15 high-quality example instructions across 7 categories (Python, JavaScript, testing, API design, security, documentation, git). This repository will be the default starting point for new InstructionKit users, reducing time-to-value to under 2 minutes. Examples will be tested with real AI coding tools to ensure 80% guideline adherence. Users download examples with existing `inskit download` command, browse via TUI, and install to projects. Documentation updates to README/quickstart guide make examples easily discoverable.

**Technical Approach**: This is primarily a content creation and documentation feature - no code changes to InstructionKit CLI are required. All existing commands (`download`, `install`, `update`) already support the required functionality. Work focuses on creating the example repository with proper structure, high-quality instruction content, validation testing, and documentation updates.

## Technical Context

**Language/Version**: Markdown (instruction content) | Python 3.10+ (for InstructionKit CLI - no changes needed)
**Primary Dependencies**: Git (for repository hosting), existing InstructionKit commands (no new dependencies)
**Storage**: GitHub repository at `troylar/instructionkit-examples` | Git-based versioning
**Testing**: Manual AI tool validation (Cursor, Claude Code, Windsurf, Copilot) | 80% guideline adherence target
**Target Platform**: Cross-platform (macOS, Linux, Windows) via Git | Works wherever InstructionKit CLI works
**Project Type**: Content repository (not software code) - follows instructionkit.yaml specification
**Performance Goals**: Download completes in <10 seconds on standard connection | Repository size <5MB
**Constraints**: Offline-capable (after initial download) | Examples must work with all 4 supported AI tools | 200-800 words per instruction
**Scale/Scope**: 10-15 instruction files | 7 categories minimum | 1-2 examples per category (extras for Python/JS)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with InstructionKit Constitution v1.1.0:

- [x] **GitHub Issue**: Work tied to GitHub issue (will be created for this feature)
- [x] **CLI-First Design**: Uses existing `inskit download`, `inskit install`, `inskit update` commands - no new commands needed
- [x] **Local-First**: Repository downloaded to local library (`~/.instructionkit/library/`), fully offline after download
- [x] **Project-Level Scoping**: Instructions installed at project level via existing install mechanism
- [x] **Multi-Tool Support**: Examples tested with all 4 tools (Cursor, Claude, Windsurf, Copilot) - no tool-specific content
- [x] **Type Safety**: N/A - this is content creation, not code (InstructionKit CLI unchanged)
- [x] **Testing**: Manual validation with 80% guideline adherence criteria | Integration test: download→browse→install flow
- [x] **User Experience**: Clear README in example repo | Discoverable via InstructionKit README/quickstart updates | Clear categorization
- [x] **Simplicity**: Leverages existing commands | Standard instructionkit.yaml format | No new abstractions needed

**Violations**: None - This feature is purely content creation using existing infrastructure.

## Project Structure

### Documentation (this feature)

```text
specs/001-example-instruction-repo/
├── plan.md              # This file
├── spec.md              # Feature specification (complete)
├── research.md          # Example content strategy & category research
├── data-model.md        # instructionkit.yaml schema & example structure
├── quickstart.md        # User guide for downloading and using examples
└── checklists/
    └── requirements.md  # Specification validation checklist
```

### Example Repository Structure (GitHub: troylar/instructionkit-examples)

```text
troylar/instructionkit-examples/
├── README.md                        # How to use examples, how to create similar
├── LICENSE                          # MIT License
├── instructionkit.yaml              # Repository metadata + instruction definitions
└── instructions/
    ├── python-best-practices.md     # Modern Python coding standards
    ├── python-fastapi-patterns.md   # FastAPI development guidelines
    ├── pytest-testing-guide.md      # Pytest patterns and best practices
    ├── javascript-modern-patterns.md # ES6+, async/await, modules
    ├── react-component-guide.md     # React functional components & hooks
    ├── api-design-principles.md     # RESTful API best practices
    ├── security-guidelines.md       # Common security patterns
    ├── security-owasp-checklist.md  # OWASP top 10 for developers
    ├── documentation-standards.md   # Code documentation guidelines
    ├── git-commit-conventions.md    # Conventional commits format
    └── [2-5 more based on research]
```

### InstructionKit Repository Updates (Main Project)

```text
instructionkit/
├── README.md                        # Add example repository to Quick Start section
└── docs/
    └── quickstart.md (if exists)    # Add example download instructions
```

**Structure Decision**:

This feature spans two repositories:

1. **New Repository** (`troylar/instructionkit-examples`): Contains instruction content only - no code
2. **Existing Repository** (`instructionkit`): Minor documentation updates only - no code changes

The separation is intentional: examples evolve independently from CLI tool (per FR-012), enabling updates without InstructionKit releases.

## Complexity Tracking

**No violations** - All constitution principles satisfied.

This feature demonstrates InstructionKit's design philosophy:
- Existing commands are composable and reusable
- Content can be distributed separately from code
- Local-first architecture enables offline use
- No special-case logic needed for "official" examples vs user repositories

---

## Phase 0: Research & Content Strategy

**Objective**: Research example instruction content, determine optimal distribution across categories, identify best practices for each domain.

### Research Tasks

1. **Category Research**: For each of 7 required categories, research:
   - Most impactful guidelines for that domain
   - Common pain points developers face with AI coding tools
   - What makes an instruction effective (specificity, examples, constraints)

2. **Example Distribution Strategy**: Determine exact 10-15 instruction breakdown:
   - Minimum 1-2 per category (7 categories = 7-14 baseline)
   - Identify popular categories needing extras (Python, JavaScript confirmed)
   - Final distribution plan with rationale

3. **Validation Testing Methodology**: Define 80% adherence testing approach:
   - How many test prompts per instruction?
   - What constitutes "following" a guideline?
   - Testing process for 4 AI tools (Cursor, Claude, Windsurf, Copilot)

4. **Content Best Practices**: Research effective instruction writing:
   - Optimal length (200-800 words guidance)
   - Structure (imperative vs examples vs constraints)
   - Tone and specificity level
   - How to make instructions tool-agnostic

**Output**: `research.md` with decisions and rationale for content creation

---

## Phase 1: Design & Structure

**Prerequisites**: research.md complete

### 1. Data Model (`data-model.md`)

Define the `instructionkit.yaml` schema and structure:

**Repository Metadata**:
- `name`: "InstructionKit Official Examples"
- `description`: "Curated instruction examples for common development scenarios"
- `version`: "1.0.0" (semantic versioning)
- `author`: "Troy Larson / InstructionKit"

**Instruction Schema** (per instruction):
```yaml
instructions:
  - name: string (unique identifier, kebab-case)
    description: string (1-2 sentences, what it does)
    file: string (relative path: instructions/*.md)
    tags: array<string> (categories for filtering)
```

**Example Entry**:
```yaml
  - name: python-best-practices
    description: "Modern Python coding standards including type hints, naming conventions, and structure"
    file: instructions/python-best-practices.md
    tags: [python, backend, style, best-practices]
```

**Validation Rules**:
- All `name` values must be unique
- All `file` paths must exist
- Each instruction must have at least 1 tag
- Tags must include category tag (python, javascript, testing, etc.)

### 2. Quickstart Guide (`quickstart.md`)

User-facing guide covering:

**For New Users**:
1. How to download the example repository
   ```bash
   inskit download --from https://github.com/troylar/instructionkit-examples
   ```

2. How to browse examples
   ```bash
   inskit install  # Opens TUI
   ```

3. How to search/filter by category
   - Use `/` to search
   - Filter by tag (python, testing, etc.)

4. How to install selected examples

5. How to verify AI is using instructions (test prompts to try)

**For Example Authors**:
1. Structure of an effective instruction
2. How to test instruction effectiveness
3. Guidelines for length, tone, specificity
4. How to contribute improvements (GitHub PR process)

### 3. Update Agent Context

Run `.specify/scripts/bash/update-agent-context.sh` to add:
- Repository structure knowledge
- Content creation guidelines
- Testing validation approach

**Technologies to add**:
- Markdown (instruction content format)
- YAML (instructionkit.yaml structure)
- Git/GitHub (repository hosting)

---

## Phase 2: Implementation Phases

**Note**: This section outlines the work breakdown. Actual task generation happens via `/speckit.tasks` command.

### Phase 2.1: Repository Setup (Foundational)

1. Create GitHub repository `troylar/instructionkit-examples`
2. Initialize with README template
3. Add MIT LICENSE
4. Create `instructions/` directory
5. Create initial `instructionkit.yaml` scaffold

### Phase 2.2: Content Creation (Core Work)

**Python Category** (2-3 examples):
- python-best-practices.md
- python-fastapi-patterns.md (or python-async-patterns.md)
- pytest-testing-guide.md (could be in testing category)

**JavaScript Category** (2 examples):
- javascript-modern-patterns.md
- react-component-guide.md (or typescript-best-practices.md)

**Testing Category** (1-2 examples):
- pytest-testing-guide.md (if not in Python)
- testing-patterns-general.md

**API Design Category** (1 example):
- api-design-principles.md

**Security Category** (2 examples):
- security-guidelines.md
- security-owasp-checklist.md

**Documentation Category** (1 example):
- documentation-standards.md

**Git Category** (1 example):
- git-commit-conventions.md

### Phase 2.3: Validation Testing

For each instruction:
1. Install to test project
2. Create 5-10 test prompts targeting different guidelines
3. Test with each AI tool (Cursor, Claude, Windsurf, Copilot)
4. Calculate adherence percentage
5. Refine instruction if <80% adherence
6. Document test results

### Phase 2.4: Documentation Updates

1. Update `troylar/instructionkit-examples/README.md`:
   - How to use examples
   - How to install InstructionKit
   - List of all examples with descriptions
   - How to contribute

2. Update `instructionkit/README.md`:
   - Add to Quick Start section
   - Example download command
   - Link to examples repository

3. Create/update quickstart guide with example workflow

### Phase 2.5: Release

1. Tag repository as v1.0.0
2. Test full user flow: install InstructionKit → download examples → install to project
3. Verify all examples appear in TUI with correct tags
4. Test update command works
5. Create announcement (README update merged, example repo live)

---

## Dependencies & Execution Order

1. **Phase 0 (Research)** → No dependencies, can start immediately
2. **Phase 1 (Design)** → Depends on Phase 0 research completion
3. **Phase 2.1 (Setup)** → Depends on Phase 1 design approval
4. **Phase 2.2 (Content)** → Depends on Phase 2.1 repository existence
5. **Phase 2.3 (Validation)** → Depends on Phase 2.2 (test each instruction as created)
6. **Phase 2.4 (Docs)** → Can happen in parallel with 2.2/2.3
7. **Phase 2.5 (Release)** → Depends on all prior phases complete

**Parallel Work Opportunities**:
- Content creation (2.2) can happen in parallel for different categories
- Documentation updates (2.4) can happen while content is being created
- Validation testing (2.3) should happen immediately after each instruction is drafted

**Critical Path**: Research → Design → Repository Setup → Content Creation → Validation → Release

---

## Success Validation

Before marking feature complete, verify all success criteria:

- [ ] **SC-001**: Time new user from `pip install instructionkit` to first instruction installed (<2 minutes)
- [ ] **SC-002**: Count instructions (10-15) and categories covered (7 minimum)
- [ ] **SC-003**: Measure download adoption (track via GitHub insights after launch)
- [ ] **SC-004**: Test search/filter time (<30 seconds to find relevant example)
- [ ] **SC-005**: Validate 80% guideline adherence for each instruction with all 4 AI tools
- [ ] **SC-006**: User test: Can someone create similar instruction using only README guidance?
- [ ] **SC-007**: Integration test: Download → Browse → Install → Verify (zero errors)

**Acceptance Gate**: All 7 success criteria must pass before feature is considered complete.

---

## Open Questions for Phase 0 Research

1. What specific Python guidelines have highest impact on AI-generated code quality?
2. Should React examples focus on functional components only, or include class components?
3. What security guidelines are most relevant for developers (vs security specialists)?
4. How detailed should API design examples be (general principles vs specific REST patterns)?
5. Should git conventions example include PR workflow or focus only on commits?
6. What length works best for instructions (bias toward 200-400 words or 600-800 words)?
7. Are there category combinations that work better (e.g., "python-testing" vs separate "python" and "testing")?

These will be answered in Phase 0 research.md document.
