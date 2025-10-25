# Feature Specification: Example Instruction Repository

**Feature Branch**: `001-example-instruction-repo`
**Created**: 2025-10-24
**Status**: Draft
**Input**: User description: "let's start working on item 1 - example repository"

## Clarifications

### Session 2025-10-24

- Q: Where should the example repository be hosted on GitHub? → A: Use existing `troylar` personal account, host at `troylar/instructionkit-examples`
- Q: How should "tested with actual AI tools to verify effectiveness" (FR-011) be validated? → A: Each example must demonstrate AI follows at least 80% of the instruction guidelines in a set of test prompts
- Q: When example instructions are updated in the repository, how do existing users get the updates? → A: Users explicitly run `inskit update --all` or `inskit update <repo-namespace>` to fetch latest versions
- Q: FR-004 lists 7 minimum categories. How should the 10-15 total examples be distributed across categories? → A: At least 1-2 examples per category, with extras allocated based on popularity (Python/JavaScript get more)
- Q: How should the example repository be made "easily discoverable" for first-time users (FR-005)? → A: Documented in README and quickstart guide with clear command: `inskit download --from https://github.com/troylar/instructionkit-examples`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time User Discovers Value (Priority: P1)

A developer installs InstructionKit for the first time and wants to see example instructions to understand what the tool can do before creating their own or finding external repositories.

**Why this priority**: This is the critical first impression. Without examples, new users face an empty library and don't understand the tool's value. This directly impacts adoption and time-to-value (goal: under 2 minutes).

**Independent Test**: Install InstructionKit fresh, run download/quickstart command, verify example repository is downloaded and browsable. User can immediately install and use at least one example instruction without any prior setup.

**Acceptance Scenarios**:

1. **Given** a new InstructionKit installation with empty library, **When** user reads README or quickstart documentation, **Then** they find clear instructions to download example repository with provided command
2. **Given** the example repository is downloaded, **When** user browses the library via TUI, **Then** they see 10-15 categorized example instructions with clear descriptions
3. **Given** user views an example instruction, **When** they read the description and tags, **Then** they understand what the instruction does and which projects it applies to
4. **Given** user installs an example instruction (e.g., python-best-practices), **When** they use their AI coding tool, **Then** the AI follows the instruction guidelines demonstrably

---

### User Story 2 - Developer Finds Relevant Examples by Category (Priority: P2)

A developer working on a specific project type (Python backend, React frontend, etc.) wants to find all relevant example instructions for their use case without manually reviewing every example.

**Why this priority**: Once users understand the tool exists (P1), they need efficient discovery to find relevant instructions. Good categorization and tagging increases the likelihood of users finding and installing multiple relevant instructions.

**Independent Test**: Download example repository, filter/search by tag or category (e.g., "python", "testing", "security"), verify all matching examples are shown with clear indicators of their purpose.

**Acceptance Scenarios**:

1. **Given** example repository is in user's library, **When** user searches by tag (e.g., "python"), **Then** all Python-related examples appear in results
2. **Given** user working on a React project, **When** they browse examples, **Then** JavaScript/React/frontend examples are clearly identifiable by tags and descriptions
3. **Given** user needs testing guidelines, **When** they filter by "testing" tag, **Then** they see pytest, testing patterns, and TDD example instructions

---

### User Story 3 - Team Lead Shares Examples as Starting Point (Priority: P3)

A team lead wants to share the example repository as a baseline for their team, then customize or extend it with company-specific instructions.

**Why this priority**: Examples serve as templates for teams building their own instruction libraries. This extends value beyond individual users to team adoption.

**Independent Test**: Download example repository, install selected examples to a project, verify team members can clone project and immediately have same instructions available (via version control).

**Acceptance Scenarios**:

1. **Given** team lead has installed example instructions to project, **When** team member clones the repository, **Then** all installed instructions are immediately available in their AI tool
2. **Given** team wants to extend examples with company rules, **When** they create new instructions based on example patterns, **Then** the format and structure are consistent with examples
3. **Given** multiple teams want different example subsets, **When** they install only relevant examples, **Then** each project has only the instructions that apply to its technology stack

---

### Edge Cases

- What happens when example repository is already downloaded and user tries to download it again? (Re-downloading overwrites existing version; users should use `inskit update` instead)
- How does system handle example repository that fails to download due to network issues? (Clear error message with retry suggestion)
- What happens if example repository structure is malformed or missing required files? (Validation error with details about what's missing)
- How are example instructions versioned and updated? (Users run `inskit update --all` or `inskit update <repo-namespace>` to fetch latest versions from GitHub)
- What if user deletes example repository but installed instructions from it remain? (Installed instructions continue to work; source metadata shows deleted repository)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a curated example instruction repository hosted on GitHub at `troylar/instructionkit-examples`
- **FR-002**: Repository MUST contain 10-15 high-quality, tested instruction examples covering common development scenarios
- **FR-003**: Each example instruction MUST include clear name, description, applicable tags, and well-formatted content
- **FR-004**: Example repository MUST cover at minimum these categories with at least 1-2 examples per category: Python development, JavaScript/TypeScript development, testing practices, API design, security guidelines, documentation standards, git conventions (extras allocated to popular categories like Python/JavaScript)
- **FR-005**: Example repository MUST be documented in InstructionKit README and quickstart guide with clear download command: `inskit download --from https://github.com/troylar/instructionkit-examples`
- **FR-006**: Users MUST be able to download example repository using standard `inskit download` command
- **FR-007**: Downloaded examples MUST be browsable via the interactive TUI with search and filter capabilities
- **FR-008**: Example instructions MUST follow the instructionkit.yaml format specification
- **FR-009**: Each example MUST be independently installable (users can pick and choose, not all-or-nothing)
- **FR-010**: Example repository MUST include a comprehensive README explaining how to use examples and how to create similar instructions
- **FR-011**: Examples MUST be tested with actual AI coding tools (Cursor, Claude Code, Windsurf, Copilot) where each example demonstrates AI follows at least 80% of its instruction guidelines in a set of test prompts
- **FR-012**: Example repository MUST be maintained and versioned separately from InstructionKit CLI tool
- **FR-013**: Users MUST be able to update downloaded example repository using `inskit update --all` or `inskit update <repo-namespace>` command to fetch latest versions

### Key Entities

- **Example Repository**: A Git repository containing curated instruction examples with metadata file (instructionkit.yaml)
  - Contains: name, description, version, author, list of example instructions
  - Structure: instructions/ directory with .md files, instructionkit.yaml metadata, README.md

- **Example Instruction**: An individual instruction file demonstrating best practices for a specific domain
  - Contains: name, description, content (markdown), tags (category labels), file path
  - Categories: language-specific (Python, JavaScript), practice-specific (testing, security), tool-specific (git, documentation)

- **Category/Tag**: Classification system for organizing examples by technology, practice, or domain
  - Examples: "python", "javascript", "testing", "security", "api-design", "frontend", "backend"

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New users can find and install their first example instruction within 2 minutes of installing InstructionKit
- **SC-002**: Example repository contains 10-15 diverse, high-quality instructions covering at least 5 distinct categories (Python, JavaScript, testing, API design, security, git, documentation)
- **SC-003**: 80% of new users download the example repository within their first session
- **SC-004**: Each example instruction is tagged appropriately, enabling users to find relevant examples via search/filter in under 30 seconds
- **SC-005**: Example instructions demonstrably improve AI coding assistant output quality with at least 80% guideline adherence when tested with real AI tools
- **SC-006**: Example repository README provides clear guidance, enabling users to create similar instructions without external documentation
- **SC-007**: Zero errors when downloading, browsing, or installing example instructions using existing InstructionKit commands

### Business Impact

- Reduces time-to-value for new users from unknown to under 2 minutes
- Increases user activation rate (users who install at least one instruction)
- Provides templates that encourage users to create their own instructions
- Demonstrates InstructionKit value proposition immediately
- Reduces support burden by providing self-service examples

## Assumptions

- Example repository will be hosted on GitHub at `troylar/instructionkit-examples`
- Examples will be created in English language
- Examples will focus on general best practices rather than company-specific or opinionated styles
- Users have Git installed for repository downloads (existing InstructionKit requirement)
- Examples will be free and open-source (MIT license)
- Initial version focuses on common web development scenarios (Python, JavaScript, testing, API design)
- Examples can be updated/versioned independently without requiring InstructionKit CLI updates
- Each example instruction will be approximately 200-800 words (concise but comprehensive)

## Out of Scope

- User-contributed examples marketplace (future feature)
- Multiple example repositories from different authors (focus on single official examples repo)
- AI-generated example content (examples will be manually curated and tested)
- Localization/translation of examples to other languages
- Advanced example features like templating or variables (keep examples simple)
- Automated testing of example instruction effectiveness
- Example instruction analytics or usage tracking
