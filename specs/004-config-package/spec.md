# Feature Specification: Configuration Package System

**Feature Branch**: `004-config-package`
**Created**: 2025-11-14
**Status**: Draft
**Input**: User description: "I want to add a new packaging feature that allows me to package up one ore more MCP server configs, one ore more instuctions, Claude hooks, etc. The idea is that we can share a compete set of setttings. I have an MCP server with tools, but I also have custom instructions I want to add to my IDE that givs more value. I have Beeminder MCP server AND clickup MCP and I have custom instrutionson how they work together and a few /commands. I want to bundle all of that together as a packge. There's a manifest for each package. The packages can support one or more IDEs, but only capabilities the IDE supports. SO if there is a claude hook in the package, everythig else will be installed in Cursor, if it's supported. Packages can be installed from a template repo. User can browse and select/update individual packages. Packages can be installed globally or at the project level, based on the IDE config settings."

## Clarifications

### Session 2025-11-14

- Q: How should system handle very large resource files (>100MB)? → A: Soft limit - warn for files >50MB, allow up to 200MB maximum, use streaming downloads for large files
- Q: How should system handle partial installation failures (some components succeed, others fail)? → A: Best-effort - install successful components, log failures, allow retry of failed components only
- Q: How should system handle main registry corruption? → A: Validate on startup, attempt to repair invalid entries, rebuild from project trackers if unrecoverable
- Q: How should system handle binary file conflicts during updates (can't show diff)? → A: Show metadata (size, date, checksum), install new version with timestamp suffix, keep old version for comparison
- Q: What happens when user cancels credential prompting mid-installation? → A: Continue with non-MCP components, mark MCP server as "pending credentials", allow configuration retry later

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install Complete Workflow Package (Priority: P1)

A developer wants to install a productivity workflow package that includes Beeminder and ClickUp MCP servers along with custom instructions that explain how they work together. They want everything set up in one command instead of manually configuring each component.

**Why this priority**: This is the core value proposition - enabling users to share and install complete, integrated configurations rather than individual components. Without this, the feature provides no benefit over existing installation methods.

**Independent Test**: Can be fully tested by installing a sample package from a repository and verifying all components (MCP configs, instructions, hooks, commands) are correctly installed in the appropriate IDE directories.

**Acceptance Scenarios**:

1. **Given** a package repository URL containing MCP configs, instructions, and commands, **When** user runs install command for that package, **Then** all compatible components are installed to the correct IDE-specific locations
2. **Given** a package contains components not supported by the user's IDE, **When** user installs the package, **Then** only supported components are installed and user is notified which components were skipped
3. **Given** a package is already installed, **When** user attempts to install it again, **Then** system detects existing installation and offers options to skip, overwrite, or update

---

### User Story 2 - Browse and Select Packages (Priority: P1)

A user wants to discover available configuration packages from a repository and select which ones to install, similar to how they currently browse individual instructions.

**Why this priority**: Discovery is essential for adoption. Users need to see what packages are available before they can install them. This is equally critical as installation itself.

**Independent Test**: Can be tested by adding packages to a repository and verifying users can view package details (name, description, included components, IDE compatibility) and select packages for installation through the interactive browser.

**Acceptance Scenarios**:

1. **Given** packages exist in the library, **When** user opens package browser, **Then** system displays all available packages with their metadata (name, description, component counts, IDE support)
2. **Given** user is viewing a package in the browser, **When** user selects "view details", **Then** system shows complete manifest including all components (MCP servers, instructions, hooks, commands) and their IDE compatibility
3. **Given** user has selected one or more packages, **When** user confirms selection, **Then** system installs all selected packages with their components

---

### User Story 3 - Create and Share Custom Package (Priority: P2)

A developer has configured their IDE with specific MCP servers, custom instructions, hooks, and slash commands that work well together. They want to package these configurations into a shareable bundle so team members can replicate the same setup.

**Why this priority**: Creation enables ecosystem growth. While consuming packages is most important initially, enabling users to create packages drives adoption and community contributions.

**Independent Test**: Can be tested by creating a package manifest, adding various component files, and verifying the package can be shared and installed by another user.

**Acceptance Scenarios**:

1. **Given** user has MCP configs, instructions, and other components, **When** user runs package creation command, **Then** system generates a manifest file listing all components with their metadata and IDE compatibility
2. **Given** a package manifest exists, **When** user adds or removes components, **Then** manifest can be updated to reflect changes
3. **Given** a complete package with manifest, **When** package is pushed to a repository, **Then** other users can discover and install it

---

### User Story 4 - Update Installed Packages (Priority: P2)

A user has installed a package and the package maintainer releases an update with bug fixes or new components. The user wants to update their installation to get the latest version.

**Why this priority**: Update capability is important for maintenance but not required for initial value delivery. Users can manually reinstall packages if needed initially.

**Independent Test**: Can be tested by installing a package version, publishing an update to the repository, and verifying user can detect and install the update with appropriate conflict handling.

**Acceptance Scenarios**:

1. **Given** a package is installed, **When** user runs update check, **Then** system compares local version with repository version and reports available updates
2. **Given** an update is available, **When** user chooses to update, **Then** system updates components with changes while preserving user customizations where possible
3. **Given** updated components conflict with user modifications, **When** update is applied, **Then** system prompts user to choose between keeping local changes or accepting updates

---

### User Story 5 - Install Packages at Different Scopes (Priority: P3 - DEFERRED)

**Note**: This story is out of scope for the initial release and deferred to a future version.

A user wants to install some packages globally (available to all projects) and other packages at the project level (specific to one project), based on whether the configuration is general-purpose or project-specific.

**Why this priority**: Scope flexibility is valuable but not essential for initial adoption. Most users can start with project-level installations and add global support later. This is deferred to reduce initial complexity and gather user feedback first.

**Independent Test**: Can be tested by installing the same package at both global and project scopes, verifying each installation is independent and IDE tools respect the appropriate scope.

**Acceptance Scenarios**:

1. **Given** user specifies global scope, **When** installing a package, **Then** components are installed to IDE's global configuration directory (if IDE supports it)
2. **Given** user specifies project scope, **When** installing a package, **Then** components are installed to project-specific IDE directories
3. **Given** a package is installed globally and at project level, **When** IDE loads configuration, **Then** project-level components override global ones (per IDE precedence rules)

---

### Edge Cases

**Package Installation:**
- What happens when a package manifest specifies components that don't exist in the repository?
- How does the system handle packages with circular dependencies or conflicting components?
- What happens when a package requires a specific IDE version or MCP server version that isn't available?
- How does the system handle partial installation failures (some components install successfully, others fail)? → Best-effort installation: successful components remain installed, failures logged, user can retry failed components
- What happens when user manually modifies installed components from a package?
- What happens when IDE configuration directories don't exist yet (fresh IDE installation)?
- How does the system handle packages from untrusted sources?
- What happens when installing a package that contains components with same names as already-installed individual components?

**Versioning:**
- What happens when user tries to install an older version of an already-installed package?
- How does system handle rollback if intermediate versions are missing from repository?
- What happens when package repository rewrites history (force push) and versions change?

**MCP Security:**
- What happens when user cancels credential prompting mid-installation? → Install non-MCP components, mark MCP as "pending credentials", allow retry via configure command
- How does system handle MCP configs with secrets that are already in the config (pre-existing, non-templated)?
- What happens when `.env` file has merge conflicts during package update?
- How does system handle credentials for MCP servers that are uninstalled but still in `.env`?

**Resources:**
- What happens when resource file is very large (>100MB)? → System warns for files >50MB, rejects files >200MB, uses streaming downloads for large files
- How does system handle binary file conflicts during updates (can't show diff)? → Show metadata comparison (size, date, checksum), install new version with timestamp suffix, keep old version
- What happens when resource path conflicts with existing project file?

**Package Creation:**
- What happens when user selects MCP server with hardcoded secrets in current config?
- How does system detect secrets in resource files (PDFs, images with embedded metadata)?
- What happens when local MCP server path is invalid or inaccessible during package creation?
- How does system handle symbolic links in project when creating package?

**IDE Translation:**
- What happens when IDE capabilities change in future versions (new features added)?
- How does system handle unknown/new IDE that's not in capability registry?
- What happens when IDE-specific config file is corrupted or has invalid JSON/YAML?
- How does system handle IDE config file merge conflicts?

**Cross-Project:**
- What happens when project path no longer exists but is still in main registry?
- How does system handle projects on different drives or network shares?
- What happens when multiple projects have same name but different paths?
- How does system handle main registry corruption? → Validate on startup, repair invalid entries, rebuild from project trackers if unrecoverable

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support a package manifest format that declares package metadata (name, version, description, author)
- **FR-002**: System MUST allow packages to include multiple component types (MCP server configs, instructions, hooks, slash commands)
- **FR-003**: System MUST declare IDE compatibility for each component in the manifest (Claude Code, Cursor, Windsurf, GitHub Copilot)
- **FR-004**: System MUST validate package manifests for completeness and correctness before installation
- **FR-005**: System MUST install only IDE-supported components and skip unsupported ones
- **FR-006**: System MUST notify users which components were installed and which were skipped due to IDE incompatibility
- **FR-007**: System MUST detect already-installed packages and prevent duplicate installations
- **FR-008**: System MUST allow users to browse available packages from repositories
- **FR-009**: System MUST display package details including all included components and IDE compatibility
- **FR-010**: System MUST download packages from remote repositories (Git-based)
- **FR-011**: System MUST store downloaded packages in the AI Config Kit library structure
- **FR-012**: System MUST track installed packages separately from component-level installation tracking
- **FR-013**: System MUST support installing packages at project-level scope
- **FR-014**: System MUST handle component installation conflicts using existing conflict resolution strategies (skip, rename, overwrite)
- **FR-015**: System MUST allow updating installed packages to newer versions
- **FR-016**: System MUST prompt user for each conflict when package updates would overwrite user-modified components, offering options to keep local changes, accept updates, or view differences
- **FR-017**: System MUST allow users to uninstall entire packages and all their components
- **FR-018**: System MUST provide command to list all installed packages with their versions
- **FR-019**: System MUST validate that all components referenced in package manifest exist in the package repository
- **FR-020**: System MUST allow users to create new package manifests from existing components
- **FR-021**: System MUST support package versioning using semantic versioning (major.minor.patch)
- **FR-022**: System MUST use best-effort installation strategy for packages (install successful components even if some fail)
- **FR-023**: System MUST log all component installation failures with detailed error messages
- **FR-024**: System MUST track partially installed packages with list of successful and failed components
- **FR-025**: System MUST allow retry of only failed components from partial installation
- **FR-026**: System MUST report installation summary showing successful, failed, and skipped components

#### Main Registry

- **FR-027**: System MUST maintain a main registry at `~/.instructionkit/registry.json` tracking installations across all projects
- **FR-028**: System MUST auto-update main registry on install/uninstall operations
- **FR-029**: System MUST provide scan command to rebuild main registry from project manifests
- **FR-030**: System MUST treat project manifests as source of truth when syncing to main registry
- **FR-031**: System MUST auto-register projects in main registry on first package installation
- **FR-032**: System MUST validate main registry JSON structure on startup before operations
- **FR-033**: System MUST attempt to repair invalid registry entries by removing malformed data
- **FR-034**: System MUST rebuild main registry from project trackers if validation fails and repair is unsuccessful
- **FR-035**: System MUST log registry corruption events with details for debugging
- **FR-036**: System MUST continue operations with empty registry if rebuild fails (degraded mode)

#### Package Versioning

- **FR-037**: Package manifest MUST declare semantic version (major.minor.patch)
- **FR-038**: System MUST track installed package version in project tracker
- **FR-039**: System MUST track installed package version in main registry per project
- **FR-040**: System MUST detect available package updates by comparing installed vs. repository versions
- **FR-041**: System MUST support updating packages to specific versions
- **FR-042**: System MUST support rollback to previously installed package versions

#### MCP Security

- **FR-043**: MCP configs in packages MUST be templates with `${VARIABLE}` placeholders for credentials
- **FR-044**: System MUST prompt users for required MCP credentials during package installation
- **FR-045**: System MUST store MCP credentials in `.instructionkit/.env` (gitignored)
- **FR-046**: System MUST merge MCP config templates with credentials when syncing to IDE config files
- **FR-047**: System MUST preserve existing MCP credentials during package updates
- **FR-048**: System MUST warn users if `.env` file is not in `.gitignore`
- **FR-049**: Package manifest MUST declare required credentials for each MCP server component
- **FR-050**: System MUST validate all required credentials are set before syncing MCP config to IDE
- **FR-051**: System MUST allow users to cancel credential prompting during installation
- **FR-052**: System MUST continue installing non-MCP components when user cancels credential prompting
- **FR-053**: System MUST mark MCP servers as "pending credentials" when user cancels credential prompt
- **FR-054**: System MUST provide command to configure credentials for pending MCP servers later
- **FR-055**: System MUST track pending credential state in package installation record

#### Custom Resources

- **FR-056**: Packages MUST support resource components of any file type (PDF, PNG, SVG, JSON, YAML, ZIP, fonts, etc.)
- **FR-057**: Resources MUST be installed to `.instructionkit/resources/<package-name>/` directory
- **FR-058**: System MUST track resources with checksums for integrity validation and update detection
- **FR-059**: Resource updates MUST prompt user for conflict resolution (keep local, accept update, view diff)
- **FR-060**: Instructions MUST be able to reference resources using standard paths
- **FR-061**: System MUST warn users when adding resources larger than 50MB during package creation
- **FR-062**: System MUST reject resources larger than 200MB with clear error message
- **FR-063**: System MUST use streaming downloads for resources larger than 10MB to prevent memory issues
- **FR-064**: System MUST detect binary file conflicts by comparing checksums during resource updates
- **FR-065**: System MUST display metadata comparison (file size, modification date, checksum) for binary file conflicts
- **FR-066**: System MUST install new binary file version with timestamp suffix when conflict detected
- **FR-067**: System MUST preserve original binary file for user comparison when conflict occurs
- **FR-068**: System MUST notify user of binary file conflict with paths to both old and new versions

#### Package Creation

- **FR-069**: System MUST provide command to create packages from current project components
- **FR-070**: System MUST allow interactive component selection via TUI for package creation
- **FR-071**: System MUST allow non-interactive component selection via CLI flags for package creation
- **FR-072**: System MUST scan current project to detect all packageable components (MCP servers, instructions, commands, resources)
- **FR-073**: System MUST prompt for package metadata (name, version, description, author, license) during creation
- **FR-074**: System MUST generate valid package manifest with all selected components

#### Secret Detection and Scrubbing

- **FR-075**: System MUST analyze environment variables for secret likelihood during package creation
- **FR-076**: System MUST auto-template high-confidence secrets (tokens, keys, passwords)
- **FR-077**: System MUST prompt users to confirm templating for medium-confidence values
- **FR-078**: System MUST preserve safe values (URLs, booleans, simple config) in package manifests
- **FR-079**: System MUST allow manual override of automatic secret detection

#### Local MCP Server Handling

- **FR-080**: System MUST detect local MCP server file paths during package creation
- **FR-081**: System MUST offer options for local MCP servers: include source code, provide external install instructions, or skip
- **FR-082**: System MUST normalize local file paths to package-relative paths when including source code
- **FR-083**: System MUST generate install instructions for external MCP servers (npm, git, docker)
- **FR-084**: System MUST handle project-relative MCP servers correctly

#### IDE Translation Layer

- **FR-085**: System MUST maintain IDE capability registry defining what each IDE supports
- **FR-086**: System MUST translate package components to IDE-specific formats during installation
- **FR-087**: System MUST skip components not supported by target IDE with clear user notification
- **FR-088**: System MUST apply IDE-specific file extensions (.md vs .mdc vs .instructions.md)
- **FR-089**: System MUST install components to IDE-specific paths (.cursor/rules/ vs .claude/rules/ vs .github/instructions/)
- **FR-090**: System MUST translate MCP configs to IDE-specific format (Claude Desktop vs Windsurf)
- **FR-091**: System MUST merge MCP configs into existing IDE config files (not replace entire file)
- **FR-092**: System MUST apply IDE-specific transformations (frontmatter, formatting, structure)
- **FR-093**: Package manifest MUST declare IDE-agnostic component definitions with optional IDE-specific translation hints

### Key Entities *(include if feature involves data)*

- **Package**: A bundle of related configuration components with metadata (name, version, description, author, license). Contains references to one or more components (instructions, MCP servers, hooks, commands, resources) that work together to provide integrated functionality. Stored in IDE-agnostic canonical format.

- **Package Manifest**: A YAML declaration file (`ai-config-kit-package.yaml`) that lists package metadata and all included components with IDE compatibility specifications. Declares semantic version, requirements, component definitions, credential requirements, and optional IDE-specific translation hints.

- **Package Component**: An individual element within a package. Types include: instruction (markdown guidance), MCP server (tool integration), hook (IDE lifecycle script), command (slash command/script), or resource (arbitrary file). Each component has IDE compatibility declarations and optional transformation rules.

- **Package Repository**: A Git repository or local directory containing one or more packages with their manifests and component files. Organized with standard directory structure (instructions/, mcp/, hooks/, commands/, resources/).

- **Package Installation Record**: Tracking data stored in `<project>/.instructionkit/packages.json` that records which packages are installed in a project. Includes package name, version, namespace, installation timestamp, scope, and list of installed components with their paths and checksums.

- **Main Registry**: System-wide index stored at `~/.instructionkit/registry.json` that aggregates installation information across all projects. Tracks which projects have which packages/instructions/MCP servers installed, with versions and timestamps. Auto-updated on install/uninstall, rebuildable via scan command.

- **Resource**: A non-code file included in a package (PDF, image, font, JSON config, etc.). Installed to `.instructionkit/resources/<package-name>/` and referenceable from instructions. Tracked with checksum for update detection.

- **IDE Capability**: Definition of what features each IDE supports (instructions, MCP, hooks, commands) and their specific requirements (file extensions, paths, formats). Maintained in capability registry to enable translation layer.

- **Component Translator**: Logic layer that converts IDE-agnostic package components to IDE-specific formats during installation. Handles file extensions, paths, frontmatter, config formats, and merging strategies per IDE.

- **MCP Template**: MCP server configuration with credential placeholders (`${VARIABLE}`). Stored in package in generic format, translated to IDE-specific config format, merged with credentials from `.env` file during installation.

- **Credential Descriptor**: Declaration in package manifest specifying required environment variables for MCP server, including variable name, description, and whether required. Used to prompt user during installation and validate completeness.

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Package Installation

- **SC-001**: Users can install a complete multi-component package (MCP servers + instructions + hooks + commands + resources) in a single command
- **SC-002**: Users can browse and view details of available packages showing all included components before installation
- **SC-003**: System correctly installs only IDE-compatible components, with at least 95% accuracy in IDE capability detection
- **SC-004**: Package installation reduces setup time by at least 70% compared to installing individual components manually
- **SC-005**: 90% of users successfully install their first package without errors or support intervention
- **SC-006**: System handles installation conflicts gracefully with clear user prompts in 100% of cases

#### Package Updates and Versioning

- **SC-007**: Users can update installed packages without losing custom modifications to non-conflicting components
- **SC-008**: System detects available package updates within 1 second of checking
- **SC-009**: Users can rollback to previous package version with all components restored correctly
- **SC-010**: Version conflicts are detected and reported with clear resolution options in 100% of cases

#### MCP Security

- **SC-011**: MCP credentials are never committed to version control (100% of packages use template pattern)
- **SC-012**: Users can configure MCP server credentials in under 2 minutes with guided prompts
- **SC-013**: Credential prompts provide clear descriptions and examples for 100% of required variables
- **SC-014**: Package updates preserve existing credentials in 100% of cases without user intervention

#### Custom Resources

- **SC-015**: Users can include any file type as a resource in packages (PDFs, images, fonts, configs, etc.)
- **SC-016**: Resources are accessible from instructions with correct paths in 100% of installations
- **SC-017**: Resource updates with conflicts present clear diff/merge options to users

#### Package Creation

- **SC-018**: Users can create a shareable package from existing project in under 5 minutes
- **SC-019**: Interactive package creator detects 100% of packageable components in current project
- **SC-020**: Secret detection automatically identifies and templates credentials with at least 95% accuracy
- **SC-021**: Users can include local MCP server source code in packages successfully
- **SC-022**: Created packages install successfully on different machines without path errors

#### IDE Translation

- **SC-023**: Components are translated to correct IDE-specific format in 100% of installations
- **SC-024**: Instructions receive correct file extension for target IDE (.md, .mdc, .instructions.md)
- **SC-025**: MCP configs merge into existing IDE configs without overwriting other servers
- **SC-026**: Users receive clear notification of which components were skipped due to IDE incompatibility

#### Cross-Project Management

- **SC-027**: Main registry accurately reflects installations across all projects within 1 second of scan
- **SC-028**: Users can query which projects use a specific package and see results in under 1 second
- **SC-029**: Scan command detects and registers new projects automatically
- **SC-030**: Users can identify and update outdated packages across all projects with single command

## Assumptions

### Package Structure and Storage

1. **Package manifest format**: YAML format (`ai-config-kit-package.yaml`) for consistency with existing `ai-config-kit.yaml` instruction repos
2. **Storage location**: Packages stored in `~/.instructionkit/library/<namespace>/` alongside existing instruction repositories
3. **Repository structure**: Package repositories follow standard directory structure:
   - `ai-config-kit-package.yaml` at root
   - `instructions/` for instruction files
   - `mcp/` for MCP templates
   - `hooks/` for IDE hooks
   - `commands/` for slash commands/scripts
   - `resources/` for arbitrary files (PDFs, images, etc.)

### Installation and Tracking

4. **Installation tracking**: Package installations tracked in `<project>/.instructionkit/packages.json` (separate from `installations.json` for backward compatibility)
5. **Main registry location**: System-wide registry at `~/.instructionkit/registry.json` for cross-project visibility
6. **Resource installation**: Resources installed to `.instructionkit/resources/<package-name>/` for organization
7. **IDE detection**: Existing AI tool detection logic (from `ai_tools/detector.py`) reused for IDE capability detection

### Versioning and Updates

8. **Versioning scheme**: Semantic versioning (major.minor.patch) for package versions
9. **Update strategy**: Prompt user for each conflict when package updates would overwrite local modifications (safer than auto-merge)
10. **Version history**: Git tags/branches used for version tracking in package repositories
11. **Rollback support**: Previous package versions retained in library for rollback capability

### MCP Security

12. **Credential storage**: MCP credentials stored in `.instructionkit/.env` (project) and `~/.instructionkit/global/.env` (global)
13. **Template format**: MCP configs use `${VARIABLE}` placeholder syntax for credentials
14. **Credential merge**: Project `.env` overrides global `.env` when merging
15. **Security default**: All credential-containing variables auto-templated unless explicitly marked safe by user
16. **Secret detection**: Heuristic-based (keywords, patterns, entropy) with user confirmation for medium-confidence cases

### IDE Translation

17. **Capability registry**: IDE capabilities defined in code (not user-configurable initially)
18. **Translation layer**: Component-specific translators handle IDE format differences
19. **Config merging**: MCP and other configs merged into existing IDE files (never replace entire file)
20. **Unknown IDEs**: Components for unknown IDEs skipped with warning (fail gracefully)

### Scope and Security

21. **Initial scope support**: Project-level scope sufficient for initial release; global scope deferred to future version
22. **Security model**: Packages from Git repositories (trusted by user); security scanning/validation can be added later
23. **Gitignore enforcement**: Warn but don't block if `.env` not in `.gitignore` (user may have reasons)

### Package Creation

24. **Component detection**: Scan uses existing installation trackers (`installations.json`, MCP configs) to find packageable components
25. **Local MCP handling**: Prefer npm/docker/git install instructions over bundling source code unless user explicitly chooses
26. **Binary resources**: Binary files (images, PDFs) included as-is without transformation
27. **Secret heuristics**: Secret detection optimized for false-negative (template too much) rather than false-positive (leak secrets)

## Dependencies

### Existing Systems (Reuse)

- Existing AI tool detection system (`ai_tools/detector.py`)
- Existing library management system (`storage/library.py`)
- Existing installation tracking system (`storage/tracker.py`)
- Existing Git operations functionality (`core/git_operations.py`)
- Existing conflict resolution logic (`core/conflict_resolution.py`)
- Existing repository parsing system (`core/repository.py`)
- Existing interactive TUI browser (`tui/installer.py`)
- Existing MCP credential management (`core/mcp/credentials.py`)
- Existing MCP manager (`core/mcp/manager.py`)
- Existing environment config utilities (`utils/dotenv.py`)

### New Components (To Be Built)

- Package manifest parser (extends repository parser)
- IDE capability registry (defines what each IDE supports)
- Component translator framework (IDE-agnostic → IDE-specific)
- Secret detection engine (heuristic-based credential scanner)
- Main registry manager (cross-project tracking)
- Package creation wizard (TUI for component selection)
- Version management system (semantic versioning, update detection, rollback)

## Out of Scope

- Global-scope installations (deferred to future version; initial release supports project-level only)
- Automatic package dependency resolution (packages depending on other packages)
- Package marketplace or central registry
- Package signing or cryptographic verification
- Automatic package recommendations based on user behavior
- Package ratings or reviews
- Package analytics or telemetry
- IDE plugin installation (only configuration files, not extensions)
- Cross-IDE migration (converting packages from one IDE format to another)
- Package testing framework
- Version pinning or lock files
