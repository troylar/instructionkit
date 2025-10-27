# Feature Specification: Git-Based Repository Versioning

**Feature Branch**: `001-git-repo-versioning`
**Created**: 2025-10-26
**Status**: Draft
**Input**: User description: "Support Git-based versioning for instruction repositories with selective installation and automatic update behavior based on ref type (tags vs branches)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Download Specific Repository Version (Priority: P1)

As a developer, I want to download a specific version of an instruction repository so that I can use stable, tested instructions without risk of unexpected changes.

**Why this priority**: This is the foundation of version control - users must be able to specify which version of a repository they want before any other versioning features can work.

**Independent Test**: Can be fully tested by running a download command with a version reference and verifying the correct version is stored in the library. Delivers immediate value by allowing users to control which repository version they use.

**Acceptance Scenarios**:

1. **Given** I have an instruction repository URL, **When** I download it with a specific tag reference (e.g., v2.0.0), **Then** the repository is downloaded to the library with the tag version in its namespace
2. **Given** I have an instruction repository URL, **When** I download it with a branch reference (e.g., main), **Then** the repository is downloaded to the library with the branch name in its namespace
3. **Given** I have an instruction repository URL, **When** I download it with a commit hash reference, **Then** the repository is downloaded to the library with the commit hash in its namespace
4. **Given** I have already downloaded a repository at version v1.0.0, **When** I download the same repository at version v2.0.0, **Then** both versions coexist in the library under different namespaces

---

### User Story 2 - Install Instructions with Version Tracking (Priority: P1)

As a developer, I want to install specific instructions from versioned repositories so that I know exactly which version of each instruction is active in my project.

**Why this priority**: This is the core value proposition - users need to know which version of each instruction is installed. Without this, version control is meaningless.

**Independent Test**: Can be fully tested by installing an instruction from a versioned repository and verifying the installation tracking records the source version. Delivers value by providing version transparency and traceability.

**Acceptance Scenarios**:

1. **Given** I have multiple versions of the same repository in my library, **When** I install an instruction, **Then** I can see which repository version each instruction came from in the selection interface
2. **Given** I install an instruction from a tagged repository version, **When** the installation completes, **Then** the installation record includes the repository name, tag reference, and reference type
3. **Given** I install an instruction from a branch-based repository, **When** the installation completes, **Then** the installation record includes the repository name, branch reference, and reference type
4. **Given** I have installed the same instruction name from different repository versions, **When** I view my installations, **Then** I can distinguish between them by their source repository version

---

### User Story 3 - Automatic Update Behavior Based on Ref Type (Priority: P1)

As a developer, I want instructions from branch-based repositories to auto-update while tag-based instructions remain stable, so that I get new features from development branches while keeping production instructions pinned.

**Why this priority**: This is the key user experience benefit - automatic, intelligent update behavior without manual configuration. This is what differentiates this feature from manual version management.

**Independent Test**: Can be fully tested by installing instructions from both tags and branches, running update, and verifying only branch-based instructions are updated. Delivers value through time savings and reduced risk.

**Acceptance Scenarios**:

1. **Given** I have installed an instruction from a tag-based repository (e.g., v2.0.0), **When** I run an update command, **Then** that instruction is NOT updated (tags are immutable)
2. **Given** I have installed an instruction from a branch-based repository (e.g., main), **When** I run an update command, **Then** that instruction IS updated if changes exist in the remote branch
3. **Given** I have installed an instruction from a commit hash, **When** I run an update command, **Then** that instruction is NOT updated (commits are immutable)
4. **Given** I have a mix of tag-based and branch-based instructions installed, **When** I run an update command, **Then** only branch-based instructions are updated
5. **Given** I have installed an instruction from a branch, **When** changes are pushed to that branch in the remote repository, **Then** running update pulls those changes and updates my installed instruction

---

### User Story 4 - Upgrade Pinned Instructions to New Versions (Priority: P2)

As a developer, I want to upgrade an instruction from an old tag version to a new tag version when I'm ready, so that I can test and adopt new versions on my own timeline.

**Why this priority**: This enables controlled upgrades for stability-focused users. While important, it's secondary to the basic version control and automatic update features.

**Independent Test**: Can be fully tested by installing from v1.0.0, downloading v2.0.0, then reinstalling from v2.0.0 and verifying the upgrade. Delivers value through safe, controlled version adoption.

**Acceptance Scenarios**:

1. **Given** I have an instruction installed from repository version v1.0.0, **When** I download version v2.0.0 of the same repository and reinstall the instruction, **Then** the instruction is upgraded from v1.0.0 to v2.0.0
2. **Given** I have an instruction installed from version v1.0.0, **When** I upgrade to v2.0.0, **Then** the installation record is updated to reflect the new version
3. **Given** I have multiple instructions from the same repository at v1.0.0, **When** I download v2.0.0, **Then** I can selectively upgrade specific instructions while leaving others at v1.0.0

---

### User Story 5 - Handle Instruction Name Collisions Across Repositories (Priority: P2)

As a developer, I want to install instructions with the same name from different repositories without conflicts, so that I can use the best instruction from each source.

**Why this priority**: This solves a real problem (name collisions) but is less critical than core versioning functionality. Users can work around this with manual renaming if needed.

**Independent Test**: Can be fully tested by installing identically-named instructions from two different repositories and verifying both can coexist. Delivers value through flexibility and reduced friction.

**Acceptance Scenarios**:

1. **Given** I have instruction "python-testing" installed from repository A, **When** I install instruction "python-testing" from repository B, **Then** the system prompts me to choose a name for the second installation
2. **Given** I have instruction "python-testing" from repository A installed as "python-testing.mdc", **When** I install "python-testing" from repository B with a different name, **Then** both instructions coexist with different filenames
3. **Given** I need to update an instruction that has a name collision, **When** I specify the source repository in the update command, **Then** only the instruction from that specific repository is updated

---

### User Story 6 - Update Specific Instructions (Priority: P3)

As a developer, I want to update a specific instruction by name (and optionally by source repository), so that I can pull the latest changes for just one instruction without updating everything.

**Why this priority**: This is a convenience feature that enhances user experience but isn't essential. Users can always update all instructions or manually reinstall.

**Independent Test**: Can be fully tested by running an update command with an instruction name and verifying only that instruction updates. Delivers value through precision and time savings.

**Acceptance Scenarios**:

1. **Given** I have multiple instructions installed, **When** I update a specific instruction by name, **Then** only that instruction is updated
2. **Given** I have the same instruction name from multiple repositories, **When** I update by name only, **Then** the system shows me which repositories have that instruction and asks which to update
3. **Given** I have the same instruction name from multiple repositories, **When** I update by name and specify the source repository, **Then** only the instruction from that repository is updated
4. **Given** I try to update an instruction that is from a tag-based repository, **When** I run the update command, **Then** the system informs me that tag-based instructions cannot be updated (must be upgraded manually)

---

### Edge Cases

- What happens when a user downloads the same repository version twice (e.g., downloads v2.0.0 twice)?
  - System should detect existing version and skip download or confirm overwrite

- What happens when a user tries to install from a repository version that doesn't exist in the library?
  - System should show only versions that are downloaded in the library

- What happens when a remote branch is deleted or a tag is removed?
  - System should handle gracefully with clear error messages, possibly offering to download a different version

- What happens when a user's installed instruction from a branch has local modifications?
  - System should detect conflicts and offer resolution strategies (skip, overwrite, backup)

- What happens when an instruction file is deleted from a repository in a newer version?
  - Update should detect the deletion and inform user, possibly offering to uninstall the instruction

- What happens when the reference type changes (e.g., a branch is converted to a tag)?
  - System should detect the change and update the ref type in the installation record

- What happens when network is unavailable during update?
  - System should fail gracefully with clear error message and maintain existing installations

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to download instruction repositories with a specific Git reference (tag, branch, or commit hash)

- **FR-002**: System MUST store multiple versions of the same repository in the library under unique namespaces that include the reference identifier

- **FR-003**: System MUST determine the reference type (tag, branch, or commit) when downloading a repository

- **FR-004**: System MUST track the source repository name, reference identifier, and reference type for each installed instruction

- **FR-005**: System MUST distinguish between mutable references (branches) and immutable references (tags, commits) when tracking installations

- **FR-006**: System MUST only update instructions from mutable references (branches) when running a global update command

- **FR-007**: System MUST NOT automatically update instructions from immutable references (tags, commits) during global updates

- **FR-008**: System MUST allow users to update specific instructions by name

- **FR-009**: System MUST detect when multiple installed instructions share the same name but come from different source repositories

- **FR-010**: System MUST allow users to specify the source repository when updating instructions with name collisions

- **FR-011**: System MUST detect when a user attempts to install an instruction with the same name as an existing installation from a different repository

- **FR-012**: System MUST prompt users to choose a filename when installing instructions with name collisions

- **FR-013**: System MUST allow users to download multiple versions of the same repository simultaneously

- **FR-014**: System MUST persist version information in installation tracking files

- **FR-015**: System MUST fetch latest changes from remote repositories for branch-based installations before updating

- **FR-016**: System MUST preserve instruction files from immutable references when running updates

- **FR-017**: System MUST allow users to manually upgrade instructions from one immutable reference to another (e.g., v1.0.0 to v2.0.0)

- **FR-018**: System MUST display repository version information when showing available instructions in the TUI

- **FR-019**: System MUST validate that the specified Git reference exists before downloading

- **FR-020**: System MUST handle network failures gracefully during download and update operations

### Key Entities

- **Repository Version**: Represents a specific version of an instruction repository identified by a Git reference
  - Attributes: repository name/URL, reference identifier (tag/branch/commit), reference type, namespace path, download timestamp
  - Relationships: Contains multiple instructions; multiple versions of same repository can coexist

- **Installation Record**: Represents an installed instruction with its version information
  - Attributes: instruction name, source repository, source reference, reference type, installed file path, installation timestamp, checksum
  - Relationships: Links to a specific Repository Version; tracked in project-level installations.json

- **Reference Type**: Classification of Git references determining update behavior
  - Types: Tag (immutable), Branch (mutable), Commit (immutable)
  - Determines: Whether instruction participates in automatic updates

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can download and install instructions from specific repository versions (tags, branches, commits) with 100% success rate for valid references

- **SC-002**: Users can maintain multiple versions of the same repository in their library simultaneously without conflicts

- **SC-003**: Running an update command updates only branch-based instructions while preserving tag/commit-based instructions in 100% of cases

- **SC-004**: Users can identify which repository version each installed instruction came from by viewing installation records

- **SC-005**: Users can upgrade instructions from an old immutable version to a new immutable version in under 30 seconds

- **SC-006**: Name collision detection and resolution works in 100% of cases where instructions from different repositories share a name

- **SC-007**: System correctly identifies and classifies reference types (tag, branch, commit) with 100% accuracy

- **SC-008**: Update operations complete in under 10 seconds for repositories with fewer than 100 instructions (network speed dependent)

- **SC-009**: 90% of users successfully manage versioned instructions without consulting documentation (based on intuitive commands and clear prompts)

- **SC-010**: Zero data loss occurs during update operations - existing installations are never corrupted or lost
