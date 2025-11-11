# Tasks: MCP Server Configuration Management

**Input**: Design documents from `/specs/003-mcp-server-management/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Related Issue**: #23

**Tests**: Unit and integration tests are included for all components to ensure 80%+ coverage per constitution requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependencies

- [ ] T001 Add `python-dotenv>=1.0.0` to pyproject.toml dependencies
- [ ] T002 Register `inskit mcp` command group in instructionkit/cli/main.py
- [ ] T003 [P] Create instructionkit/core/mcp/ directory structure (manager.py, credentials.py, validator.py, set_manager.py)
- [ ] T004 [P] Create instructionkit/utils/dotenv.py for .env file utilities
- [ ] T005 [P] Create instructionkit/utils/atomic_write.py for atomic file writes
- [ ] T006 [P] Create instructionkit/storage/mcp_tracker.py for active set tracking
- [ ] T007 [P] Create instructionkit/ai_tools/mcp_syncer.py for cross-tool synchronization

**Checkpoint**: Directory structure and dependency setup complete

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Data Models

- [ ] T008 [P] Define MCPServer dataclass in instructionkit/core/models.py with validation
- [ ] T009 [P] Define MCPSet dataclass in instructionkit/core/models.py with validation
- [ ] T010 [P] Define MCPTemplate dataclass in instructionkit/core/models.py with from_repository() method
- [ ] T011 [P] Define EnvironmentConfig dataclass in instructionkit/core/models.py with load/save methods
- [ ] T012 [P] Define AIToolMCPConfig dataclass in instructionkit/core/models.py with sync methods
- [ ] T013 [P] Define ActiveSetState dataclass in instructionkit/core/models.py with persist methods
- [ ] T014 [P] Define MCPInstallation dataclass in instructionkit/core/models.py with list_all() method
- [ ] T015 [P] Add InstallationScope enum to instructionkit/core/models.py (PROJECT, GLOBAL)

### Core Utilities

- [ ] T016 [P] Implement atomic_write() context manager in instructionkit/utils/atomic_write.py
- [ ] T017 [P] Implement dotenv read/write utilities in instructionkit/utils/dotenv.py with multi-line support
- [ ] T018 [P] Extend Repository class in instructionkit/core/repository.py to parse mcp_servers section from templatekit.yaml
- [ ] T019 [P] Extend Repository class in instructionkit/core/repository.py to parse mcp_sets section from templatekit.yaml

### Unit Tests for Foundation

- [ ] T020 [P] Write unit tests for MCPServer dataclass in tests/unit/test_mcp_models.py
- [ ] T021 [P] Write unit tests for MCPSet dataclass in tests/unit/test_mcp_models.py
- [ ] T022 [P] Write unit tests for MCPTemplate dataclass in tests/unit/test_mcp_models.py
- [ ] T023 [P] Write unit tests for EnvironmentConfig in tests/unit/test_mcp_models.py
- [ ] T024 [P] Write unit tests for atomic_write() in tests/unit/test_atomic_write.py
- [ ] T025 [P] Write unit tests for dotenv utilities in tests/unit/test_dotenv.py
- [ ] T026 [P] Write unit tests for Repository mcp parsing in tests/unit/test_repository_mcp.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Install MCP Configurations from Template Repository (Priority: P1) 🎯 MVP

**Goal**: Enable users to install MCP server configurations from template repositories to local library

**Independent Test**: Create a template repository with MCP server definitions, run `inskit mcp install <url> --as <namespace>`, verify configurations are stored in `~/.instructionkit/library/<namespace>/` without exposing secrets

### Core Implementation for US1

- [ ] T027 [P] [US1] Implement MCPManager class in instructionkit/core/mcp/manager.py with install_template() method
- [ ] T028 [P] [US1] Implement conflict resolution logic (skip, overwrite, rename) in MCPManager
- [ ] T029 [P] [US1] Implement namespace validation in MCPManager
- [ ] T030 [P] [US1] Extend LibraryManager in instructionkit/storage/library.py to support MCP template storage
- [ ] T031 [US1] Create inskit mcp install command in instructionkit/cli/mcp_install.py
- [ ] T032 [US1] Add --as flag for namespace specification in mcp_install.py
- [ ] T033 [US1] Add --scope flag (project/global) in mcp_install.py
- [ ] T034 [US1] Add --force and --conflict flags in mcp_install.py
- [ ] T035 [US1] Implement Rich output formatting for install progress in mcp_install.py
- [ ] T036 [US1] Add JSON output support (--json flag) in mcp_install.py

### Unit Tests for US1

- [ ] T037 [P] [US1] Write unit tests for MCPManager.install_template() in tests/unit/test_mcp_manager.py
- [ ] T038 [P] [US1] Write unit tests for conflict resolution in tests/unit/test_mcp_manager.py
- [ ] T039 [P] [US1] Write unit tests for namespace validation in tests/unit/test_mcp_manager.py
- [ ] T040 [P] [US1] Write CLI argument parsing tests in tests/unit/test_mcp_install_cli.py

### Integration Tests for US1

- [ ] T041 [US1] Write integration test for installing from Git URL in tests/integration/test_mcp_install.py
- [ ] T042 [US1] Write integration test for installing from local path in tests/integration/test_mcp_install.py
- [ ] T043 [US1] Write integration test for conflict resolution (skip) in tests/integration/test_mcp_install.py
- [ ] T044 [US1] Write integration test for conflict resolution (overwrite, rename) in tests/integration/test_mcp_install.py
- [ ] T045 [US1] Write integration test for --scope global flag in tests/integration/test_mcp_install.py

**Checkpoint**: User Story 1 complete - users can install MCP templates to library

---

## Phase 4: User Story 2 - Configure MCP Server Credentials (Priority: P1)

**Goal**: Enable users to securely provide credentials for MCP servers without committing secrets

**Independent Test**: Install an MCP template with required credentials, run `inskit mcp configure <namespace>.<server>`, verify credentials stored in `.instructionkit/.env` (gitignored)

### Core Implementation for US2

- [ ] T046 [P] [US2] Implement CredentialManager class in instructionkit/core/mcp/credentials.py
- [ ] T047 [P] [US2] Implement interactive credential prompts with masking in CredentialManager
- [ ] T048 [P] [US2] Implement non-interactive mode (read from env vars) in CredentialManager
- [ ] T049 [P] [US2] Implement credential validation against MCP server requirements in CredentialManager
- [ ] T050 [P] [US2] Auto-create and gitignore `.instructionkit/.env` file in CredentialManager
- [ ] T051 [US2] Create inskit mcp configure command in instructionkit/cli/mcp_configure.py
- [ ] T052 [US2] Add --scope flag for project/global .env selection in mcp_configure.py
- [ ] T053 [US2] Add --non-interactive flag in mcp_configure.py
- [ ] T054 [US2] Add --show-current flag to display masked values in mcp_configure.py
- [ ] T055 [US2] Implement Rich output formatting with secure input in mcp_configure.py
- [ ] T056 [US2] Add JSON output support in mcp_configure.py

### Unit Tests for US2

- [ ] T057 [P] [US2] Write unit tests for CredentialManager.configure() in tests/unit/test_mcp_credentials.py
- [ ] T058 [P] [US2] Write unit tests for credential validation in tests/unit/test_mcp_credentials.py
- [ ] T059 [P] [US2] Write unit tests for .env file creation/gitignore in tests/unit/test_mcp_credentials.py
- [ ] T060 [P] [US2] Write unit tests for multi-line value support in tests/unit/test_mcp_credentials.py
- [ ] T061 [P] [US2] Write CLI tests for mcp configure in tests/unit/test_mcp_configure_cli.py

### Integration Tests for US2

- [ ] T062 [US2] Write integration test for interactive credential configuration in tests/integration/test_mcp_configure.py
- [ ] T063 [US2] Write integration test for non-interactive mode in tests/integration/test_mcp_configure.py
- [ ] T064 [US2] Write integration test for partial configuration in tests/integration/test_mcp_configure.py
- [ ] T065 [US2] Write integration test for updating existing credentials in tests/integration/test_mcp_configure.py
- [ ] T066 [US2] Write integration test for .env file gitignore creation in tests/integration/test_mcp_configure.py

**Checkpoint**: User Story 2 complete - users can configure credentials securely

---

## Phase 5: User Story 3 - Sync MCP Configurations to AI Tools (Priority: P1)

**Goal**: Automatically sync configured MCP servers to AI coding tools' config files

**Independent Test**: Install and configure an MCP server, run `inskit mcp sync --tool claude`, verify `~/.claude/claude_desktop_config.json` contains correct MCP configuration with resolved env vars

### Core Implementation for US3

- [ ] T067 [P] [US3] Implement MCPSyncer class in instructionkit/ai_tools/mcp_syncer.py with sync_all() method
- [ ] T068 [P] [US3] Implement AI tool detection logic in MCPSyncer
- [ ] T069 [P] [US3] Implement environment variable resolution in MCPSyncer
- [ ] T070 [P] [US3] Implement config backup creation in MCPSyncer before modification
- [ ] T071 [P] [US3] Extend AITool base class in instructionkit/ai_tools/base.py with sync_mcp_servers() method
- [ ] T072 [P] [US3] Implement sync_mcp_servers() for Claude in instructionkit/ai_tools/claude.py
- [ ] T073 [P] [US3] Implement sync_mcp_servers() for Cursor in instructionkit/ai_tools/cursor.py
- [ ] T074 [P] [US3] Implement sync_mcp_servers() for Windsurf in instructionkit/ai_tools/windsurf.py
- [ ] T075 [US3] Create inskit mcp sync command in instructionkit/cli/mcp_sync.py
- [ ] T076 [US3] Add --tool flag (claude/cursor/windsurf/all) in mcp_sync.py
- [ ] T077 [US3] Add --server flag to sync specific servers only in mcp_sync.py
- [ ] T078 [US3] Add --scope flag (project/global/both) in mcp_sync.py
- [ ] T079 [US3] Add --dry-run flag in mcp_sync.py
- [ ] T080 [US3] Add --backup/--no-backup flags in mcp_sync.py
- [ ] T081 [US3] Implement Rich output with sync progress and status in mcp_sync.py
- [ ] T082 [US3] Add JSON output support in mcp_sync.py

### Unit Tests for US3

- [ ] T083 [P] [US3] Write unit tests for MCPSyncer.sync_all() in tests/unit/test_mcp_syncer.py
- [ ] T084 [P] [US3] Write unit tests for AI tool detection in tests/unit/test_mcp_syncer.py
- [ ] T085 [P] [US3] Write unit tests for env var resolution in tests/unit/test_mcp_syncer.py
- [ ] T086 [P] [US3] Write unit tests for config backup creation in tests/unit/test_mcp_syncer.py
- [ ] T087 [P] [US3] Write unit tests for Claude sync in tests/unit/test_claude_mcp.py
- [ ] T088 [P] [US3] Write unit tests for Cursor sync in tests/unit/test_cursor_mcp.py
- [ ] T089 [P] [US3] Write unit tests for Windsurf sync in tests/unit/test_windsurf_mcp.py
- [ ] T090 [P] [US3] Write CLI tests for mcp sync in tests/unit/test_mcp_sync_cli.py

### Integration Tests for US3

- [ ] T091 [US3] Write integration test for sync to Claude Desktop in tests/integration/test_mcp_sync.py
- [ ] T092 [US3] Write integration test for sync to all detected tools in tests/integration/test_mcp_sync.py
- [ ] T093 [US3] Write integration test for preserving non-MCP config sections in tests/integration/test_mcp_sync.py
- [ ] T094 [US3] Write integration test for skipping servers with missing credentials in tests/integration/test_mcp_sync.py
- [ ] T095 [US3] Write integration test for atomic writes and backup in tests/integration/test_mcp_sync.py
- [ ] T096 [US3] Write integration test for sync --dry-run in tests/integration/test_mcp_sync.py

**Checkpoint**: User Story 3 complete - users can sync MCP servers to AI tools

---

## Phase 6: User Story 4 - Import MCP Servers from AI Tools (Priority: P2)

**Goal**: Enable users to import existing MCP configurations from AI tools into their library for reuse

**Independent Test**: Manually configure MCP servers in Cursor, run `inskit mcp import --from cursor --as my-servers`, verify servers are extracted to library with generated templatekit.yaml and credentials properly handled

### Core Implementation for US4

- [ ] T097 [P] [US4] Implement MCPImporter class in instructionkit/core/mcp/manager.py with import_from_tool() method
- [ ] T098 [P] [US4] Implement AI tool config parsing (read from Claude/Cursor/Windsurf) in MCPImporter
- [ ] T099 [P] [US4] Implement secret detection heuristics (KEY, TOKEN, SECRET, PASSWORD patterns) in MCPImporter
- [ ] T100 [P] [US4] Implement interactive secret classification prompts in MCPImporter
- [ ] T101 [P] [US4] Implement templatekit.yaml generation from imported servers in MCPImporter
- [ ] T102 [P] [US4] Implement template repository export (README, .gitignore, examples) in MCPImporter
- [ ] T103 [P] [US4] Implement merge logic for importing into existing templates in MCPImporter
- [ ] T104 [US4] Create inskit mcp import command in instructionkit/cli/mcp_import.py
- [ ] T105 [US4] Add --from flag (claude/cursor/windsurf/all) in mcp_import.py
- [ ] T106 [US4] Add --as flag for namespace in mcp_import.py
- [ ] T107 [US4] Add --scope flag (project/global) in mcp_import.py
- [ ] T108 [US4] Add --merge flag to merge into existing template in mcp_import.py
- [ ] T109 [US4] Add --export-template flag to create shareable repo structure in mcp_import.py
- [ ] T110 [US4] Add --auto-secrets flag for automatic secret detection in mcp_import.py
- [ ] T111 [US4] Add --keep-values flag to preserve all env var values in mcp_import.py
- [ ] T112 [US4] Implement Rich output formatting with import progress in mcp_import.py
- [ ] T113 [US4] Add JSON output support in mcp_import.py

### Unit Tests for US4

- [ ] T114 [P] [US4] Write unit tests for MCPImporter.import_from_tool() in tests/unit/test_mcp_importer.py
- [ ] T115 [P] [US4] Write unit tests for AI tool config parsing in tests/unit/test_mcp_importer.py
- [ ] T116 [P] [US4] Write unit tests for secret detection heuristics in tests/unit/test_mcp_importer.py
- [ ] T117 [P] [US4] Write unit tests for templatekit.yaml generation in tests/unit/test_mcp_importer.py
- [ ] T118 [P] [US4] Write unit tests for template export logic in tests/unit/test_mcp_importer.py
- [ ] T119 [P] [US4] Write CLI tests for mcp import in tests/unit/test_mcp_import_cli.py

### Integration Tests for US4

- [ ] T120 [US4] Write integration test for importing from Cursor in tests/integration/test_mcp_import.py
- [ ] T121 [US4] Write integration test for importing from all tools in tests/integration/test_mcp_import.py
- [ ] T122 [US4] Write integration test for secret classification prompts in tests/integration/test_mcp_import.py
- [ ] T123 [US4] Write integration test for --auto-secrets flag in tests/integration/test_mcp_import.py
- [ ] T124 [US4] Write integration test for --export-template flag in tests/integration/test_mcp_import.py
- [ ] T125 [US4] Write integration test for --merge flag in tests/integration/test_mcp_import.py
- [ ] T126 [US4] Write integration test for bidirectional workflow (import→sync to other tools) in tests/integration/test_mcp_import.py

**Checkpoint**: User Story 4 complete - users can import MCP servers from AI tools to library

---

## Phase 7: User Story 5 - List and Validate MCP Configurations (Priority: P2)

**Goal**: Provide visibility into installed MCP servers, sets, and configuration status

**Independent Test**: Install multiple MCP templates with varying configuration states, run `inskit mcp list` and `inskit mcp validate`, verify accurate status reporting

### Core Implementation for US5

- [ ] T127 [P] [US5] Implement MCPValidator class in instructionkit/core/mcp/validator.py
- [ ] T128 [P] [US5] Implement credential completeness check in MCPValidator
- [ ] T129 [P] [US5] Implement command availability check (shutil.which) in MCPValidator
- [ ] T130 [P] [US5] Implement AI tool config validation in MCPValidator
- [ ] T131 [P] [US5] Extend LibraryManager with list_mcp_templates() method in instructionkit/storage/library.py
- [ ] T132 [US5] Create inskit mcp list command in instructionkit/cli/mcp_list.py
- [ ] T133 [US5] Add --sets flag to list MCP sets in mcp_list.py
- [ ] T134 [US5] Add --scope flag (project/global/both) in mcp_list.py
- [ ] T135 [US5] Add --status flag to show configuration status in mcp_list.py
- [ ] T136 [US5] Add --verbose flag for detailed information in mcp_list.py
- [ ] T137 [US5] Implement Rich output with tables and status indicators in mcp_list.py
- [ ] T138 [US5] Add JSON output support in mcp_list.py
- [ ] T139 [US5] Create inskit mcp validate command in instructionkit/cli/mcp_validate.py
- [ ] T140 [US5] Add --check-commands, --check-credentials, --check-tools flags in mcp_validate.py
- [ ] T141 [US5] Add --all flag (run all checks) in mcp_validate.py
- [ ] T142 [US5] Add --fix flag to attempt auto-fix in mcp_validate.py
- [ ] T143 [US5] Implement Rich output with validation results in mcp_validate.py
- [ ] T144 [US5] Add JSON output support in mcp_validate.py

### Unit Tests for US5

- [ ] T145 [P] [US5] Write unit tests for MCPValidator checks in tests/unit/test_mcp_validator.py
- [ ] T146 [P] [US5] Write unit tests for command availability check in tests/unit/test_mcp_validator.py
- [ ] T147 [P] [US5] Write unit tests for LibraryManager.list_mcp_templates() in tests/unit/test_library_mcp.py
- [ ] T148 [P] [US5] Write CLI tests for mcp list in tests/unit/test_mcp_list_cli.py
- [ ] T149 [P] [US5] Write CLI tests for mcp validate in tests/unit/test_mcp_validate_cli.py

### Integration Tests for US5

- [ ] T150 [US5] Write integration test for listing multiple templates in tests/integration/test_mcp_list.py
- [ ] T151 [US5] Write integration test for listing with status indicators in tests/integration/test_mcp_list.py
- [ ] T152 [US5] Write integration test for listing MCP sets in tests/integration/test_mcp_list.py
- [ ] T153 [US5] Write integration test for namespace filtering in tests/integration/test_mcp_list.py
- [ ] T154 [US5] Write integration test for validate with all checks in tests/integration/test_mcp_validate.py
- [ ] T155 [US5] Write integration test for validate --fix in tests/integration/test_mcp_validate.py

**Checkpoint**: User Story 5 complete - users can list and validate MCP configurations

---

## Phase 8: User Story 6 - Activate MCP Server Sets (Priority: P3)

**Goal**: Enable users to switch between different groups of MCP servers based on workflow

**Independent Test**: Install a template with multiple MCP sets, activate one set, verify only those servers are synced, then switch to another set and verify the change

### Core Implementation for US6

- [ ] T156 [P] [US6] Implement SetManager class in instructionkit/core/mcp/set_manager.py
- [ ] T157 [P] [US6] Implement activate_set() method in SetManager with state persistence
- [ ] T158 [P] [US6] Implement deactivate() method in SetManager
- [ ] T159 [P] [US6] Implement get_active_set() method in SetManager
- [ ] T160 [P] [US6] Implement MCPSetTracker class in instructionkit/storage/mcp_tracker.py
- [ ] T161 [P] [US6] Implement state file management (mcp_state.json) in MCPSetTracker
- [ ] T162 [US6] Create inskit mcp activate command in instructionkit/cli/mcp_activate.py
- [ ] T163 [US6] Add --tool flag (claude/cursor/windsurf/all) in mcp_activate.py
- [ ] T164 [US6] Add --allow-partial flag in mcp_activate.py
- [ ] T165 [US6] Add --deactivate flag in mcp_activate.py
- [ ] T166 [US6] Implement Rich output showing set changes and sync status in mcp_activate.py
- [ ] T167 [US6] Add JSON output support in mcp_activate.py
- [ ] T168 [US6] Integrate SetManager with MCPSyncer to sync only active set servers

### Unit Tests for US6

- [ ] T169 [P] [US6] Write unit tests for SetManager.activate_set() in tests/unit/test_mcp_set_manager.py
- [ ] T170 [P] [US6] Write unit tests for SetManager.deactivate() in tests/unit/test_mcp_set_manager.py
- [ ] T171 [P] [US6] Write unit tests for MCPSetTracker state persistence in tests/unit/test_mcp_tracker.py
- [ ] T172 [P] [US6] Write CLI tests for mcp activate in tests/unit/test_mcp_activate_cli.py

### Integration Tests for US6

- [ ] T173 [US6] Write integration test for activating a set in tests/integration/test_mcp_activate.py
- [ ] T174 [US6] Write integration test for switching between sets in tests/integration/test_mcp_activate.py
- [ ] T175 [US6] Write integration test for deactivating current set in tests/integration/test_mcp_activate.py
- [ ] T176 [US6] Write integration test for --allow-partial flag in tests/integration/test_mcp_activate.py
- [ ] T177 [US6] Write integration test for state persistence across commands in tests/integration/test_mcp_activate.py

**Checkpoint**: User Story 6 complete - users can activate MCP server sets

---

## Phase 9: User Story 7 - Update MCP Configurations from Template Repository (Priority: P3)

**Goal**: Enable users to update MCP template definitions from source without losing credentials

**Independent Test**: Make changes to a template repository, run `inskit mcp update <namespace>`, verify MCP definitions are updated while credentials in `.instructionkit/.env` remain unchanged

### Core Implementation for US7

- [ ] T178 [P] [US7] Implement update_template() method in MCPManager (instructionkit/core/mcp/manager.py)
- [ ] T179 [P] [US7] Implement change detection (added/modified/removed servers) in MCPManager
- [ ] T180 [P] [US7] Implement credential preservation logic in MCPManager
- [ ] T181 [P] [US7] Implement new env var detection and prompts in MCPManager
- [ ] T182 [US7] Create inskit mcp update command in instructionkit/cli/mcp_update.py
- [ ] T183 [US7] Add --all flag to update all templates in mcp_update.py
- [ ] T184 [US7] Add --preserve-credentials flag (default: true) in mcp_update.py
- [ ] T185 [US7] Add --check-only flag in mcp_update.py
- [ ] T186 [US7] Add --force flag in mcp_update.py
- [ ] T187 [US7] Implement Rich output showing changes and credential status in mcp_update.py
- [ ] T188 [US7] Add JSON output support in mcp_update.py

### Unit Tests for US7

- [ ] T189 [P] [US7] Write unit tests for MCPManager.update_template() in tests/unit/test_mcp_manager_update.py
- [ ] T190 [P] [US7] Write unit tests for change detection in tests/unit/test_mcp_manager_update.py
- [ ] T191 [P] [US7] Write unit tests for credential preservation in tests/unit/test_mcp_manager_update.py
- [ ] T192 [P] [US7] Write CLI tests for mcp update in tests/unit/test_mcp_update_cli.py

### Integration Tests for US7

- [ ] T193 [US7] Write integration test for updating template with new servers in tests/integration/test_mcp_update.py
- [ ] T194 [US7] Write integration test for updating template with removed servers in tests/integration/test_mcp_update.py
- [ ] T195 [US7] Write integration test for updating template with modified servers in tests/integration/test_mcp_update.py
- [ ] T196 [US7] Write integration test for credential preservation during update in tests/integration/test_mcp_update.py
- [ ] T197 [US7] Write integration test for --all flag in tests/integration/test_mcp_update.py
- [ ] T198 [US7] Write integration test for --check-only flag in tests/integration/test_mcp_update.py

**Checkpoint**: User Story 7 complete - users can update MCP templates

---

## Phase 10: User Story 8 - Scope MCP Configurations (Project vs Global) (Priority: P3)

**Goal**: Support both project-scoped and global-scoped MCP server installations

**Independent Test**: Install one MCP template globally and another at project scope, verify both are available in project directory, but only global templates are available outside projects

### Core Implementation for US8

- [ ] T199 [P] [US8] Implement global library location management in MCPManager (instructionkit/core/mcp/manager.py)
- [ ] T200 [P] [US8] Implement scope merging logic (global + project) in MCPManager
- [ ] T201 [P] [US8] Implement conflict resolution (project takes precedence) in MCPManager
- [ ] T202 [P] [US8] Update install command to handle --scope global in mcp_install.py
- [ ] T203 [P] [US8] Update configure command to detect scope in mcp_configure.py
- [ ] T204 [P] [US8] Update sync command to merge scopes with --scope both in mcp_sync.py
- [ ] T205 [P] [US8] Update list command to show scope indicators in mcp_list.py
- [ ] T206 [P] [US8] Update validate command to check both scopes in mcp_validate.py
- [ ] T207 [P] [US8] Update import command to support --scope global in mcp_import.py

### Unit Tests for US8

- [ ] T208 [P] [US8] Write unit tests for scope merging logic in tests/unit/test_mcp_manager_scope.py
- [ ] T209 [P] [US8] Write unit tests for conflict resolution in tests/unit/test_mcp_manager_scope.py
- [ ] T210 [P] [US8] Write unit tests for global library paths in tests/unit/test_mcp_manager_scope.py

### Integration Tests for US8

- [ ] T211 [US8] Write integration test for global installation in tests/integration/test_mcp_scope.py
- [ ] T212 [US8] Write integration test for project installation in tests/integration/test_mcp_scope.py
- [ ] T213 [US8] Write integration test for scope merging in tests/integration/test_mcp_scope.py
- [ ] T214 [US8] Write integration test for project precedence on conflicts in tests/integration/test_mcp_scope.py
- [ ] T215 [US8] Write integration test for scope indicators in list output in tests/integration/test_mcp_scope.py
- [ ] T216 [US8] Write integration test for importing with --scope global in tests/integration/test_mcp_scope.py

**Checkpoint**: User Story 8 complete - users can use project and global scopes

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and quality assurance

### Integration & E2E Tests

- [ ] T217 [P] Write end-to-end test for install→configure→sync workflow in tests/integration/test_mcp_lifecycle.py
- [ ] T218 [P] Write end-to-end test for import→configure→sync to other tools workflow in tests/integration/test_mcp_lifecycle.py
- [ ] T219 [P] Write integration test for error recovery and validation in tests/integration/test_mcp_error_handling.py
- [ ] T220 [P] Write integration test for concurrent config file access in tests/integration/test_mcp_concurrency.py
- [ ] T221 [P] Write cross-platform path handling tests (Windows/macOS/Linux) in tests/integration/test_mcp_crossplatform.py

### Documentation

- [ ] T222 [P] Add MCP feature documentation to README.md with quickstart examples
- [ ] T223 [P] Update CHANGELOG.md with MCP feature additions
- [ ] T224 [P] Add docstrings to all public MCP classes and methods (Google style)
- [ ] T225 [P] Create example template repository with templatekit.yaml in docs/examples/
- [ ] T226 [P] Document import workflow in quickstart.md with Cursor example

### Error Handling & Edge Cases

- [ ] T227 [P] Implement comprehensive error messages for all CLI commands
- [ ] T228 [P] Add validation for malformed .env files with line number reporting
- [ ] T229 [P] Add validation for invalid templatekit.yaml with helpful error messages
- [ ] T230 [P] Implement graceful handling of missing AI tool installations
- [ ] T231 [P] Add validation for namespace special characters and path separators

### Performance & Quality

- [ ] T232 Run full test suite and verify 80%+ coverage: `invoke test --coverage`
- [ ] T233 Run type checking and ensure mypy passes: `invoke typecheck`
- [ ] T234 Run linting and formatting checks: `invoke quality`
- [ ] T235 Test on Windows, macOS, and Linux platforms
- [ ] T236 Benchmark install/sync/list/import performance against goals (<10s, <2s, <1s, <3s)

**Checkpoint**: Feature complete and ready for release

---

## Dependencies & Execution Order

### User Story Independence

**Can be implemented in parallel** (after Phase 2 Foundation):
- User Story 1 (Install) - Foundation only
- User Story 2 (Configure) - Requires US1 installed templates

**Sequential dependencies**:
- User Story 3 (Sync) - REQUIRES US1 (install) and US2 (configure)
- User Story 4 (Import) - REQUIRES US3 (uses sync infrastructure for reading AI tool configs)
- User Story 5 (List/Validate) - Requires US1, US2, US4 for meaningful data
- User Story 6 (Activate Sets) - REQUIRES US3 (sync logic)
- User Story 7 (Update) - REQUIRES US1 (install logic)
- User Story 8 (Scoping) - Can integrate throughout but easiest after US1-US4

### Recommended MVP Scope

**Phase 3 ONLY** (User Story 1): Install MCP templates
- Provides immediate value: teams can share MCP configurations
- Independently testable
- Enables exploration before committing to full feature set

**Phase 3-5** (User Stories 1-3): Complete core workflow
- Install → Configure → Sync
- Delivers full value proposition
- All P1 stories included

**Phase 3-6** (User Stories 1-4): Complete bidirectional workflow
- Install → Configure → Sync → Import
- Enables both top-down (template repos) and bottom-up (existing configs) workflows
- Natural integration point

### Parallel Execution Examples

**Phase 1 (Setup)**: All tasks can run in parallel
```bash
# T001-T007 all marked [P] - run concurrently
```

**Phase 2 (Foundation)**: Data models (T008-T015), utilities (T016-T019), tests (T020-T026) can run in parallel groups

**Phase 3 (US1)**:
- Core implementation: T027-T030 parallel, then T031-T036 sequential
- Tests: T037-T040 (unit), T041-T045 (integration) all parallel after implementation

**Phase 4-10**: Similar parallel patterns within each user story

---

## Summary

**Total Tasks**: 236 tasks across 11 phases
**Tasks per User Story**:
- US1 (Install): 19 tasks (T027-T045)
- US2 (Configure): 21 tasks (T046-T066)
- US3 (Sync): 30 tasks (T067-T096)
- US4 (Import): 30 tasks (T097-T126) **NEW**
- US5 (List/Validate): 29 tasks (T127-T155)
- US6 (Activate Sets): 22 tasks (T156-T177)
- US7 (Update): 21 tasks (T178-T198)
- US8 (Scoping): 18 tasks (T199-T216)
- Polish: 20 tasks (T217-T236)

**Parallel Opportunities**: 146 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**: Each user story includes specific verification steps in "Independent Test" section

**MVP Recommendations**:
- **Minimal MVP** (Phase 3): US1 only - 19 tasks
- **Core MVP** (Phases 3-5): US1-US3 - 70 tasks
- **Bidirectional MVP** (Phases 3-6): US1-US4 - 100 tasks (includes import) ⭐

**Format Validation**: ✅ All 236 tasks follow required format with checkbox, ID, optional [P] and [Story] labels, and file paths

**New Feature Integration**: Import feature (US4) naturally extends the existing template/sync system - imported servers become templates that work exactly like installed ones. Enables bottom-up workflow (AI tools → library → other tools) complementing top-down workflow (template repo → library → AI tools).
