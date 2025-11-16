# Feature Specification: Autonomous Tool-Driven Journal AI

**Feature Branch**: `001-function-calling-spec`  
**Created**: 2025-11-15  
**Status**: Draft  
**Input**: User description: "let's create a awesome fucking spec around this"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Morning Briefing Without Prompts (Priority: P1)

Troy opens the AI Journal console, types “good morning,” and instantly receives a full briefing that already includes yesterday’s note, today’s draft note, Rize stats, and Beeminder gaps without being asked to provide file paths or confirm actions.

**Why this priority**: This is the daily core workflow; failure here breaks user trust and forces manual work every single day.

**Independent Test**: Execute only the morning-check-in flow in a clean journal and verify that the AI fetches all required context through tool calls before responding.

**Acceptance Scenarios**:

1. **Given** yesterday’s and today’s notes exist, **When** the user greets the console, **Then** the response must cite both entries and include Rize + Beeminder summaries by calling the appropriate tools without prompts.
2. **Given** MCP data is unavailable, **When** the user greets the console, **Then** the AI must still brief using journal data and explicitly note that time-tracking data is unavailable, without throwing errors.

---

### User Story 2 - Autonomous Capture of New Context (Priority: P2)

While journaling, Troy mentions “I realized I avoid hard projects because I’m afraid to fail” and references meeting with Sarah. The AI stores the insight in memories, updates Sarah’s people note, and appends the daily note without Troy issuing explicit commands.

**Why this priority**: Reduces friction during the actual reflective moments, turning journaling into conversation rather than manual bookkeeping.

**Independent Test**: Feed the AI only conversational notes about insights/people and verify that create-memory, link-people, and update-daily-note tools are invoked automatically with correct payloads.

**Acceptance Scenarios**:

1. **Given** a conversation mentioning a new insight, **When** the AI processes the message, **Then** it must create a memory entry summarizing the insight and confirm it to the user.
2. **Given** a conversation that references a known person, **When** the AI processes it, **Then** it must update the person’s note and mention the update in the response.

---

### User Story 3 - Installable MCP Extensions (Priority: P3)

A power user installs an “AI Journal MCP Tools” package via AI Config Kit, which adds new server connections (e.g., Rize, Beeminder, ClickUp). After installation, the console immediately exposes the new MCP-backed tools and uses them when applicable.

**Why this priority**: Enables community growth and custom data sources without modifying core code, aligning with the package ecosystem vision.

**Independent Test**: Install the package in isolation, confirm that new tools are registered, configurable credentials are requested, and tool calls succeed/fail gracefully.

**Acceptance Scenarios**:

1. **Given** an MCP package providing Rize access is installed, **When** the AI needs time-tracking data, **Then** it must invoke the new MCP tool automatically and include the results in user responses.
2. **Given** the user uninstalls the MCP package, **When** the AI is asked for time-tracking data, **Then** it must skip MCP calls, explain the omission, and continue responding.

---

### Edge Cases

- Missing permissions or expired tokens for an MCP server: tool call must fail silently, log the error, and inform the user that the data source needs reconfiguration.
- Journal path resolvers cannot locate today’s note: AI must create the file using the daily template before continuing.
- Tool recursion or chain length exceeds limits: execution engine must cap iterations and return a helpful message rather than looping indefinitely.
- Concurrent tool calls attempt to update the same note: system must serialize writes or merge conflicts deterministically.
- Community package installs a malformed tool definition: validator must reject it with actionable errors before it reaches runtime.
- Test harness AI judge yields ambiguous verdict: framework should flag the case and store artifacts for manual review.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The console MUST expose a declarative tool registry describing each capability (name, parameters, description) that the AI model can invoke.
- **FR-002**: The console MUST execute AI-initiated tool calls (read note, search, update, memory creation, people linking) without prompting the user for confirmation.
- **FR-003**: System MUST cap tool-call chains to a configurable maximum iterations and return a descriptive error when the limit is reached.
- **FR-004**: System MUST fallback gracefully when optional MCP tools are unavailable, still completing the user request with journal-only data.
- **FR-005**: System MUST log every tool call (timestamp, parameters, duration, success/failure) for troubleshooting and testing evidence.
- **FR-006**: System MUST provide a packaging interface so MCP tool bundles can be installed, versioned, and removed via AI Config Kit without editing ai-journal-kit source.
- **FR-007**: Tool definitions installed via packages MUST be validated (schema conformity, permission scope, naming collisions) before activation.
- **FR-008**: The test harness MUST simulate user prompts, capture AI responses plus tool-call traces, and evaluate them with an AI judge against scenario-specific criteria.
- **FR-009**: Test harness MUST store verdicts and failing artifacts (prompt, response, tool log, judge reasoning) for regressions.
- **FR-010**: System MUST update `.ai-instructions/my-coach.md` (or equivalent) to describe when each tool should be invoked so behavior remains instruction-driven rather than keyword-driven.

### Key Entities *(include if feature involves data)*

- **ToolDefinition**: Metadata describing a callable capability (name, description, parameter schema, source package, availability flags).
- **ToolExecutionLog**: Audit record capturing each invocation’s request, result, latency, and error states.
- **MCPPackageDescriptor**: Bundle manifest specifying MCP servers, instructions, hooks, and dependencies for installation through AI Config Kit.
- **AIJudgeResult**: Structured output from the AI-based validation harness containing pass/fail status, reasoning, and references to captured artifacts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of morning-check-in automated tests must pass on first attempt, verifying that journal + MCP contexts are fetched without user prompts.
- **SC-002**: 100% of conversational insight tests must produce the correct note updates or memory entries within 5 seconds of user input.
- **SC-003**: When MCP tooling is removed, the AI must still satisfy all journal-only scenarios with no more than one informational message about missing integrations.
- **SC-004**: AI judge-based regression suite must achieve ≥90% overall pass rate before release, with any failures automatically logged for review.
- **SC-005**: Community MCP packages must install/uninstall in under 2 minutes and expose their tools to the AI without manual config edits.

## Assumptions & Dependencies

- Existing AI Journal Kit journaling structure (daily/, people/, memories/) remains unchanged so tool definitions can locate files.
- MCP integrations rely on AI Config Kit for credential management; users must install the relevant packages before MCP-backed tools are active.
- AI judge harness can access the same tool metadata and logs produced during console runs to evaluate behavior.
