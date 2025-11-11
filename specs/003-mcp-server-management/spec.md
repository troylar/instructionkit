# Feature Specification: MCP Server Configuration Management

**Feature Branch**: `003-mcp-server-management`
**Created**: 2025-11-11
**Status**: Draft
**Input**: User description: "Add MCP server configuration management and syncing"
**Related Issue**: #23

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install MCP Configurations from Template Repository (Priority: P1)

A developer wants to use their team's standardized MCP server configurations across projects without manually copying config files or sharing secrets.

**Why this priority**: Core functionality - without the ability to install MCP configurations from template repositories, none of the other features have value. This is the foundation of the entire feature.

**Independent Test**: Can be fully tested by creating a template repository with MCP server definitions, running the install command, and verifying that configurations are stored in the local library without exposing secrets.

**Acceptance Scenarios**:

1. **Given** a template repository with MCP server definitions in `templatekit.yaml`, **When** user runs `inskit mcp install https://github.com/company/backend-standards --as backend`, **Then** MCP server definitions are downloaded to `~/.instructionkit/library/backend/` and environment variables requiring values are identified
2. **Given** a template repository with multiple MCP servers, **When** user installs the template, **Then** all MCP server definitions are available in `inskit mcp list` command
3. **Given** an MCP server definition with required environment variables, **When** user installs the template, **Then** the system identifies which environment variables need configuration and stores placeholder values
4. **Given** an already installed MCP template, **When** user attempts to reinstall with the same namespace, **Then** system prompts for conflict resolution (skip, overwrite, or rename)

---

### User Story 2 - Configure MCP Server Credentials (Priority: P1)

A developer needs to provide API keys, tokens, and other credentials for MCP servers without committing secrets to version control.

**Why this priority**: Without credential management, MCP servers cannot function. This is essential for making installed MCP configurations operational.

**Independent Test**: Can be fully tested by installing an MCP template with required credentials, running the configure command, entering test credentials, and verifying they are stored securely in a gitignored file.

**Acceptance Scenarios**:

1. **Given** an installed MCP server with missing credentials, **When** user runs `inskit mcp configure backend.github`, **Then** system prompts for each required environment variable with secure input (masked for sensitive values)
2. **Given** configured credentials in `.instructionkit/.env`, **When** user runs `inskit mcp list`, **Then** MCP servers with complete credentials show as "configured/ready" while those missing credentials show as "needs configuration"
3. **Given** an MCP server requiring multiple environment variables, **When** user configures some but not all variables, **Then** system indicates partial configuration and lists remaining required variables
4. **Given** existing configured credentials, **When** user runs configure command again, **Then** system allows updating credentials while masking current values

---

### User Story 3 - Sync MCP Configurations to AI Tools (Priority: P1)

A developer wants their configured MCP servers automatically available in their AI coding tools (Claude Desktop, Cursor, Windsurf) without manually editing JSON config files.

**Why this priority**: This is the primary value proposition - automating the tedious manual process of editing tool-specific config files. Without syncing, users would still need to manually copy configurations.

**Independent Test**: Can be fully tested by installing and configuring an MCP server, running the sync command, and verifying that the AI tool's config file contains the correct MCP server configuration with resolved environment variables.

**Acceptance Scenarios**:

1. **Given** a configured MCP server and Claude Desktop installed, **When** user runs `inskit mcp sync --tool claude`, **Then** `~/.claude/claude_desktop_config.json` is updated with the MCP server configuration and environment variables are resolved from `.instructionkit/.env`
2. **Given** multiple configured MCP servers, **When** user runs `inskit mcp sync --tool all`, **Then** all detected AI tools (Claude, Cursor, Windsurf) are updated with complete MCP configurations
3. **Given** an existing AI tool config file with other settings, **When** user runs sync command, **Then** only the `mcpServers` section is updated while preserving other configuration settings
4. **Given** an MCP server with missing credentials, **When** user attempts to sync, **Then** system warns about incomplete configuration and skips that server or prompts for credentials

---

### User Story 4 - Import MCP Servers from AI Tools (Priority: P2)

A developer has manually configured MCP servers in an AI tool (e.g., Cursor) and wants to import them into their library for reuse across other tools and projects.

**Why this priority**: Important for users who start by manually configuring MCP servers and want to formalize them into templates. Enables a "bottom-up" workflow complementing the "top-down" template installation approach. Not critical for MVP but valuable for adoption.

**Independent Test**: Can be fully tested by manually configuring MCP servers in Cursor, running the import command, and verifying that servers are added to the library as a template with proper templatekit.yaml and credential extraction.

**Acceptance Scenarios**:

1. **Given** MCP servers configured in Cursor, **When** user runs `inskit mcp import --from cursor --as my-servers`, **Then** MCP servers are extracted from `~/.cursor/mcp.json` and saved to `~/.instructionkit/library/my-servers/` with generated `templatekit.yaml`
2. **Given** MCP servers with environment variables in Cursor config, **When** user imports, **Then** system prompts which variables are secrets vs defaults, extracts secrets to `.instructionkit/.env`, and marks them as `null` in templatekit.yaml
3. **Given** MCP servers in multiple AI tools, **When** user runs `inskit mcp import --from all --as my-collection`, **Then** servers from all detected tools are combined into a single template
4. **Given** an existing template namespace, **When** user attempts to import with the same namespace, **Then** system prompts for conflict resolution (skip, merge, overwrite)
5. **Given** imported template, **When** user runs `inskit mcp import --export-template`, **Then** system creates full repository structure with README, .gitignore, and examples for sharing via Git

---

### User Story 5 - List and Validate MCP Configurations (Priority: P2)

A developer wants to see all available MCP servers, their configuration status, and any issues preventing them from working.

**Why this priority**: Important for discoverability and troubleshooting, but the system can function without it. Users can still install, configure, and sync MCP servers without this visibility.

**Independent Test**: Can be fully tested by installing multiple MCP templates with varying configuration states, running the list and validate commands, and verifying accurate status reporting.

**Acceptance Scenarios**:

1. **Given** multiple installed MCP templates, **When** user runs `inskit mcp list`, **Then** system displays all available MCP servers grouped by namespace with configuration status indicators
2. **Given** MCP servers in different configuration states, **When** user runs `inskit mcp validate`, **Then** system reports each server's status (ready, missing credentials, invalid configuration) with specific details
3. **Given** installed MCP templates with defined sets, **When** user runs `inskit mcp list --sets`, **Then** system displays all available MCP sets with their included servers and descriptions
4. **Given** a namespace filter, **When** user runs `inskit mcp list backend`, **Then** system shows only MCP servers from the backend namespace

---

### User Story 6 - Activate MCP Server Sets (Priority: P3)

A developer wants to switch between different groups of MCP servers based on their current task (backend work, frontend work, data analysis) without reconfiguring everything.

**Why this priority**: Nice-to-have convenience feature. Users can accomplish the same outcome by syncing specific servers individually, though sets make it more convenient for predefined workflows.

**Independent Test**: Can be fully tested by installing a template with multiple MCP sets, activating one set, verifying that only those servers are synced, then switching to another set and verifying the change.

**Acceptance Scenarios**:

1. **Given** an installed MCP template with multiple sets defined, **When** user runs `inskit mcp activate backend.backend-dev`, **Then** only MCP servers in the backend-dev set are synced to AI tools and marked as active
2. **Given** an active MCP set, **When** user runs `inskit mcp activate backend.frontend-dev`, **Then** the previous set is deactivated, the new set is activated and synced, and the system reports which servers changed
3. **Given** no active set, **When** user runs `inskit mcp list`, **Then** system shows all MCP servers but indicates no active set
4. **Given** an MCP set with servers missing credentials, **When** user attempts to activate the set, **Then** system warns about unconfigured servers and prompts whether to proceed with partial activation

---

### User Story 7 - Update MCP Configurations from Template Repository (Priority: P3)

A team maintainer updates MCP server definitions in the template repository, and developers want to pull those updates to their local library without losing their configured credentials.

**Why this priority**: Important for ongoing maintenance but not critical for initial feature launch. Users can manually reinstall templates as a workaround.

**Independent Test**: Can be fully tested by making changes to a template repository, running the update command, and verifying that MCP definitions are updated while credentials remain unchanged.

**Acceptance Scenarios**:

1. **Given** an installed MCP template with configured credentials, **When** user runs `inskit mcp update backend`, **Then** MCP server definitions are updated from the repository while local `.instructionkit/.env` credentials are preserved
2. **Given** an MCP template with added servers in the repository, **When** user runs update command, **Then** new servers appear in list with "needs configuration" status
3. **Given** an MCP template with removed servers in the repository, **When** user runs update command, **Then** system reports which servers were removed and optionally cleans up unused credentials
4. **Given** multiple installed MCP templates, **When** user runs `inskit mcp update --all`, **Then** all templates are updated in sequence with status reporting for each

---

### User Story 8 - Scope MCP Configurations (Project vs Global) (Priority: P3)

A developer wants some MCP servers available globally across all projects (personal productivity tools) while others are project-specific (database connections to project resources).

**Why this priority**: Advanced feature for power users. Most users will be satisfied with project-scoped or global-scoped installation without mixing. Can be added later based on user feedback.

**Independent Test**: Can be fully tested by installing one MCP template globally and another at project scope, then verifying that both are available when working in a project directory, but only global templates are available outside projects.

**Acceptance Scenarios**:

1. **Given** a template repository, **When** user runs `inskit mcp install <url> --scope global`, **Then** MCP servers are available in all projects and stored in global library location
2. **Given** a template repository, **When** user runs `inskit mcp install <url> --scope project` from a project directory, **Then** MCP servers are only available in that specific project
3. **Given** both global and project-scoped MCP servers configured, **When** user runs `inskit mcp list`, **Then** system displays both with clear scope indicators
4. **Given** a conflict between global and project MCP servers with same name, **When** user syncs configurations, **Then** project-scoped servers take precedence and system reports the override

---

### Edge Cases

- **What happens when syncing to an AI tool that is not installed?** System should detect missing tools, skip them, and report which tools were skipped with installation instructions.

- **How does system handle MCP server definitions that change required environment variables between updates?** System should detect new required variables after update and prompt for configuration, while preserving existing variables that still match.

- **What happens when `.instructionkit/.env` file contains invalid or malformed content?** System should validate the file on load, report specific parsing errors with line numbers, and refuse to sync until fixed.

- **How does system handle concurrent modifications to AI tool config files?** System should read current content, merge changes (preserving non-MCP sections), and write atomically to prevent corruption.

- **What happens when an MCP server command or binary is not installed on the user's system?** System should validate during sync that commands are available in PATH, warn about missing dependencies, and provide installation hints.

- **How does system handle namespaces containing special characters or path separators?** System should validate namespace format during install, rejecting invalid characters that could cause file system issues.

- **What happens when user manually edits `.instructionkit/.env` with invalid environment variable names?** System should validate variable names against installed MCP server definitions, warning about unused or unexpected variables.

- **How does system handle extremely large environment variable values (e.g., certificate files)?** System should support multi-line values using standard `.env` syntax with quotes and escaped newlines.

- **What happens when multiple MCP templates define servers with the same name?** System should use namespaced naming (`namespace.server-name`) to prevent conflicts and allow multiple templates to coexist.

- **How does system handle operating system differences in file paths (Windows vs Unix)?** All path handling should use platform-independent path libraries, and file paths in MCP configurations should use environment variables or be validated/converted during sync.

## Requirements *(mandatory)*

### Functional Requirements

#### Installation & Library Management

- **FR-001**: System MUST support installing MCP configurations from Git repositories using `inskit mcp install <url> --as <namespace>` command
- **FR-002**: System MUST support installing MCP configurations from local directories using `inskit mcp install <path> --as <namespace>` command
- **FR-003**: System MUST store installed MCP configurations in `~/.instructionkit/library/<namespace>/` directory structure
- **FR-004**: System MUST parse `templatekit.yaml` files containing `mcp_servers` and `mcp_sets` sections
- **FR-005**: System MUST validate that MCP server definitions include required fields: name, command, args
- **FR-006**: System MUST support namespace conflict resolution strategies during installation (skip, overwrite, rename)
- **FR-007**: System MUST track installation metadata including source URL, version, and installation date

#### Credential Management

- **FR-008**: System MUST store environment variables in `.instructionkit/.env` file in standard dotenv format
- **FR-009**: System MUST automatically add `.instructionkit/.env` to `.gitignore` when creating the file
- **FR-010**: System MUST mark environment variables with `null` values in `templatekit.yaml` as requiring user configuration
- **FR-011**: System MUST provide `inskit mcp configure <namespace>.<server-name>` command for interactive credential entry
- **FR-012**: System MUST mask sensitive input during credential configuration (passwords, tokens, API keys)
- **FR-013**: System MUST support multi-line environment variable values using standard dotenv quote syntax
- **FR-014**: System MUST validate environment variable names against standard naming conventions (alphanumeric and underscore only)
- **FR-015**: System MUST preserve existing credentials in `.instructionkit/.env` when updating MCP templates

#### AI Tool Synchronization

- **FR-016**: System MUST detect installed AI tools (Claude Desktop, Cursor, Windsurf) by checking standard config file locations
- **FR-017**: System MUST update Claude Desktop configuration at `~/.claude/claude_desktop_config.json` with `mcpServers` section
- **FR-018**: System MUST update Cursor configuration with MCP server definitions in tool-specific format
- **FR-019**: System MUST update Windsurf configuration with MCP server definitions in tool-specific format
- **FR-020**: System MUST resolve environment variable references (e.g., `${GITHUB_TOKEN}`) from `.instructionkit/.env` during sync
- **FR-021**: System MUST preserve existing non-MCP configuration sections in AI tool config files when syncing
- **FR-022**: System MUST create backup of AI tool config files before modification
- **FR-023**: System MUST write AI tool config files atomically to prevent corruption during concurrent access
- **FR-024**: System MUST provide `inskit mcp sync --tool <tool-name>` command for single tool sync
- **FR-025**: System MUST provide `inskit mcp sync --tool all` command for syncing to all detected tools
- **FR-026**: System MUST report which tools were updated and which were skipped during sync operation

#### Listing & Validation

- **FR-027**: System MUST provide `inskit mcp list` command showing all installed MCP servers with status indicators
- **FR-028**: System MUST indicate configuration status for each MCP server (configured, needs configuration, partially configured)
- **FR-029**: System MUST support filtering MCP list by namespace using `inskit mcp list <namespace>`
- **FR-030**: System MUST display MCP sets defined in templates with `inskit mcp list --sets`
- **FR-031**: System MUST provide `inskit mcp validate` command checking all MCP configurations for issues
- **FR-032**: System MUST report specific missing credentials for each MCP server during validation
- **FR-033**: System MUST validate that MCP server commands exist in system PATH during validation
- **FR-034**: System MUST report parsing errors in `.instructionkit/.env` file with line numbers

#### MCP Sets & Activation

- **FR-035**: System MUST parse `mcp_sets` definitions from `templatekit.yaml` including set name, description, and server list
- **FR-036**: System MUST provide `inskit mcp activate <namespace>.<set-name>` command to enable a specific MCP set
- **FR-037**: System MUST sync only servers in the active set to AI tools when a set is activated
- **FR-038**: System MUST track which MCP set is currently active in project-specific state file
- **FR-039**: System MUST deactivate previous set when activating a new set
- **FR-040**: System MUST report which servers are added/removed when switching between sets

#### Update & Maintenance

- **FR-041**: System MUST provide `inskit mcp update <namespace>` command to refresh MCP definitions from source repository
- **FR-042**: System MUST preserve configured credentials in `.instructionkit/.env` when updating MCP templates
- **FR-043**: System MUST report new servers added, servers removed, and servers modified during update
- **FR-044**: System MUST prompt for configuration of newly added environment variables after update
- **FR-045**: System MUST provide `inskit mcp update --all` command to update all installed MCP templates

#### Scoping

- **FR-046**: System MUST support `--scope project` flag to install MCP configurations only for current project
- **FR-047**: System MUST support `--scope global` flag to install MCP configurations available to all projects
- **FR-048**: System MUST merge global and project-scoped MCP servers when both are present
- **FR-049**: System MUST prioritize project-scoped MCP servers over global servers when names conflict
- **FR-050**: System MUST indicate scope (global/project) in `inskit mcp list` output

#### Template Format

- **FR-051**: System MUST support `mcp_servers` section in `templatekit.yaml` with fields: name, command, args, env
- **FR-052**: System MUST support optional `env` field in MCP server definitions mapping variable names to default values
- **FR-053**: System MUST support `null` values in `env` field to indicate required user configuration
- **FR-054**: System MUST support `mcp_sets` section in `templatekit.yaml` with fields: name, description, servers
- **FR-055**: System MUST validate that servers referenced in sets are defined in `mcp_servers` section

### Key Entities

- **MCP Server Definition**: Represents a Model Context Protocol server configuration with name, command, arguments, environment variables, and namespace. Defines how to launch an MCP server and what credentials it requires.

- **MCP Set**: A named collection of MCP servers for a specific task or workflow (e.g., backend-dev, frontend-dev). Includes set name, description, list of server references, and owning namespace.

- **MCP Installation**: Tracks an installed MCP template including namespace, source URL/path, installation timestamp, version, and list of defined servers and sets.

- **Environment Configuration**: Collection of environment variable name-value pairs stored in `.instructionkit/.env` file. Maps variable names to their configured values for MCP server credential injection.

- **AI Tool Config**: Represents an AI tool's configuration file location, format, and current MCP server settings. Used for syncing MCP servers to specific tools.

- **Active Set State**: Tracks which MCP set is currently active in a project, stored in project-specific state file. Determines which servers are synced to AI tools.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Teams can share MCP server configurations via template repositories without exposing credentials (100% of secrets remain local)
- **SC-002**: Developers can install and configure MCP servers in under 5 minutes (from initial install to working AI tool integration)
- **SC-003**: MCP server configurations sync correctly to all detected AI tools with 100% accuracy (no manual config file editing required)
- **SC-004**: Developers can switch between different MCP server sets in under 30 seconds
- **SC-005**: System detects and reports 100% of missing credentials before sync attempts fail
- **SC-006**: Updates to template repositories preserve 100% of locally configured credentials
- **SC-007**: System handles concurrent AI tool config modifications without corruption (atomic writes succeed 100% of time)
- **SC-008**: Validation reports provide actionable error messages that reduce support requests by 80% compared to manual MCP configuration
- **SC-009**: 90% of users successfully configure their first MCP server on first attempt without documentation
- **SC-010**: Template repositories with MCP configurations work cross-platform (Windows, macOS, Linux) without modification
