# Package System Architecture Review & Recommendations

**Date**: 2025-11-14
**Purpose**: Ensure package feature integrates seamlessly with existing AI Config Kit architecture
**Status**: Pre-implementation review

---

## Executive Summary

✅ **The dual registry + package system will integrate well with existing architecture**
✅ **Existing patterns can be extended for packages**
⚠️ **Need to consolidate tracking systems to avoid confusion**
⚠️ **MCP credential handling needs careful integration**
✅ **Custom files (PDFs, images) fit naturally with existing structure**

---

## 1. Current Architecture Analysis

### 1.1 Installation Tracking (Existing)

**What exists today:**

```
~/.instructionkit/                          # Global/user data
  ├── installations.json                    # Global instruction installs
  ├── library.json                          # Downloaded instruction repos
  └── library/                              # Downloaded repo content
      └── <namespace>/

<project>/.instructionkit/                  # Project-specific data
  └── installations.json                    # Project instruction installs
```

**Data model (InstallationRecord):**
```json
{
  "instruction_name": "python-best-practices",
  "ai_tool": "cursor",
  "source_repo": "https://github.com/user/repo",
  "installed_path": "/path/to/file.md",
  "installed_at": "2025-10-21T14:33:16",
  "checksum": "sha256hash",
  "bundle_name": null,
  "scope": "global",
  "project_root": null
}
```

**Key patterns:**
- ✅ Dual-level tracking (global + project)
- ✅ Project tracker uses **relative paths** for portability
- ✅ Global tracker uses **absolute paths**
- ✅ Checksums for integrity validation
- ✅ Bundle support already exists
- ✅ Source repo tracking for updates

### 1.2 MCP Server Management (Feature 003 - ~70% complete)

**Credential storage:**
```
~/.instructionkit/global/.env                # Global MCP credentials
<project>/.instructionkit/.env               # Project MCP credentials (overrides global)
```

**Current MCP flow:**
1. Download MCP template to `library/<namespace>/`
2. Parse `templatekit.yaml` manifest
3. Prompt user for required credentials
4. Store credentials in `.env` (project or global)
5. Sync to IDE's MCP config (e.g., `claude_desktop_config.json`)

**Security patterns:**
- ✅ Credentials in `.env` files (gitignored)
- ✅ Interactive prompting with masked input
- ✅ Project overrides global (merge logic)
- ✅ Validation before sync
- ⚠️ **Tracker not implemented yet** (`mcp_tracker.py` is stubbed)

### 1.3 Template Sync System (Feature 002)

**Separate tracking file:**
```
<project>/.instructionkit/template-installations.json
```

**Why separate?**
- Templates support file-level tracking with UUIDs
- Different update semantics (content vs. structure)
- Dependency management
- Per-file conflict detection

⚠️ **INCONSISTENCY ALERT**: We now have 2 tracker files in same directory!

---

## 2. Package System Integration Design

### 2.1 Recommended Directory Structure

```
~/.instructionkit/                          # Global/user home
  ├── installations.json                    # [KEEP] Global instruction installs
  ├── registry.json                         # [NEW] Main registry (all projects)
  ├── library.json                          # [KEEP] Downloaded repo index
  ├── library/                              # [KEEP] Downloaded content
  │   └── <namespace>/                     # Instructions, MCP templates, packages
  └── global/
      └── .env                              # [KEEP] Global MCP credentials

<project>/.instructionkit/                  # Project-specific
  ├── installations.json                    # [KEEP] Instruction installs
  ├── packages.json                         # [NEW] Package installs
  ├── template-installations.json           # [KEEP] Template installs
  ├── .env                                  # [KEEP] Project MCP credentials
  ├── mcp/                                  # [KEEP] MCP templates
  │   └── <namespace>/
  └── resources/                            # [NEW] Package resources (PDFs, images, etc.)
      └── <package-name>/
          ├── logo.png
          ├── brand-guide.pdf
          └── colors.json
```

### 2.2 Main Registry Format (NEW)

**Purpose**: System-wide index of what's installed where

**Location**: `~/.instructionkit/registry.json`

**Format**:
```json
{
  "version": "1.0",
  "last_updated": "2025-11-14T10:30:00Z",
  "projects": {
    "/Users/troy/my-project": {
      "last_scanned": "2025-11-14T10:30:00Z",
      "packages": [
        {
          "name": "brand-kit",
          "version": "1.2.0",
          "namespace": "acme/brand-kit",
          "installed_at": "2025-11-10T15:00:00Z",
          "components": {
            "instructions": 3,
            "mcp_servers": 0,
            "hooks": 1,
            "commands": 2,
            "resources": 5
          }
        }
      ],
      "instructions": [
        {
          "name": "python-best-practices",
          "source_repo": "acme/instructions",
          "installed_at": "2025-11-01T12:00:00Z"
        }
      ],
      "mcp_servers": [
        {
          "name": "beeminder",
          "namespace": "beeminder-mcp",
          "installed_at": "2025-11-10T15:00:00Z"
        }
      ]
    },
    "/Users/troy/another-project": {
      "last_scanned": "2025-11-14T10:32:00Z",
      "packages": [],
      "instructions": [],
      "mcp_servers": []
    }
  }
}
```

**Update Strategy**:
- Auto-update on install/uninstall
- `aiconfig scan` command rebuilds from project trackers
- Project trackers are **always** source of truth

### 2.3 Package Tracking Format (NEW)

**Location**: `<project>/.instructionkit/packages.json`

**Format**:
```json
[
  {
    "package_name": "brand-kit",
    "package_version": "1.2.0",
    "namespace": "acme/brand-kit",
    "source_repo": "https://github.com/acme/brand-kit",
    "installed_at": "2025-11-10T15:00:00Z",
    "scope": "project",
    "components": [
      {
        "type": "instruction",
        "name": "brand-guidelines",
        "installed_path": ".cursor/rules/brand-guidelines.mdc",
        "checksum": "sha256hash"
      },
      {
        "type": "mcp_server",
        "name": "beeminder",
        "namespace": "beeminder-mcp",
        "config_path": ".instructionkit/mcp/beeminder-mcp/"
      },
      {
        "type": "hook",
        "name": "pre-commit-check",
        "installed_path": ".claude/hooks/pre-commit",
        "ai_tool": "claude"
      },
      {
        "type": "command",
        "name": "brand-check",
        "installed_path": ".cursor/commands/brand-check.sh",
        "ai_tool": "cursor"
      },
      {
        "type": "resource",
        "name": "logo.png",
        "installed_path": ".instructionkit/resources/brand-kit/logo.png",
        "checksum": "sha256hash"
      },
      {
        "type": "resource",
        "name": "brand-guide.pdf",
        "installed_path": ".instructionkit/resources/brand-kit/brand-guide.pdf",
        "checksum": "sha256hash"
      }
    ]
  }
]
```

**Why separate from installations.json?**
- Packages are composite entities (multiple components)
- Need version tracking at package level
- Different update semantics (package updates vs. individual installs)
- Cleaner separation of concerns

---

## 3. Package Manifest Format

### 3.1 Package Manifest Structure

**Location**: `<repo-root>/ai-config-kit-package.yaml`

**Format**:
```yaml
# Package metadata
name: brand-kit
version: 1.2.0
description: Complete Acme Corp brand kit with guidelines and assets
author: Acme Corp
license: MIT

# Package requirements
requires:
  ai-config-kit: ">=0.4.0"

# Components
components:
  # Instructions
  - type: instruction
    name: brand-guidelines
    description: Brand usage guidelines
    file: instructions/brand-guidelines.md
    ai_tools: [cursor, claude, winsurf, copilot]

  - type: instruction
    name: color-palette
    description: Approved color palette
    file: instructions/colors.md
    ai_tools: [cursor, claude, winsurf, copilot]

  # MCP servers (with credential requirements)
  - type: mcp_server
    name: beeminder
    description: Beeminder goal tracking
    template_path: mcp/beeminder/
    credentials_required:
      - name: BEEMINDER_AUTH_TOKEN
        description: "Your Beeminder API token from https://beeminder.com/api"
        required: true
      - name: BEEMINDER_USERNAME
        description: "Your Beeminder username"
        required: true

  # Hooks (IDE-specific)
  - type: hook
    name: pre-commit-check
    description: Pre-commit brand compliance check
    file: hooks/pre-commit.sh
    ai_tools: [claude]  # Only Claude supports hooks

  # Commands/slash commands
  - type: command
    name: brand-check
    description: Check file for brand compliance
    file: commands/brand-check.sh
    ai_tools: [cursor]

  # Resources (PDFs, images, fonts, etc.)
  - type: resource
    name: logo.png
    description: Company logo (PNG format)
    file: resources/logo.png

  - type: resource
    name: logo.svg
    description: Company logo (vector format)
    file: resources/logo.svg

  - type: resource
    name: brand-guide.pdf
    description: Complete brand guidelines PDF
    file: resources/brand-guide.pdf

  - type: resource
    name: fonts.zip
    description: Approved brand fonts
    file: resources/fonts.zip

  - type: resource
    name: colors.json
    description: Color palette JSON
    file: resources/colors.json

# Optional: Package-level tags
tags:
  - branding
  - design
  - corporate
```

### 3.2 MCP Server Template in Package

**Package structure**:
```
brand-kit-package/
├── ai-config-kit-package.yaml          # Package manifest
├── instructions/                        # Instruction files
│   ├── brand-guidelines.md
│   └── colors.md
├── mcp/                                 # MCP templates
│   └── beeminder/
│       ├── templatekit.yaml             # MCP template manifest
│       └── config.template.json         # Config with ${PLACEHOLDERS}
├── hooks/
│   └── pre-commit.sh
├── commands/
│   └── brand-check.sh
└── resources/                           # Custom resources
    ├── logo.png
    ├── logo.svg
    ├── brand-guide.pdf
    ├── fonts.zip
    └── colors.json
```

**MCP config template** (`mcp/beeminder/config.template.json`):
```json
{
  "beeminder": {
    "command": "npx",
    "args": ["-y", "@anthropic-ai/mcp-server-beeminder"],
    "env": {
      "BEEMINDER_AUTH_TOKEN": "${BEEMINDER_AUTH_TOKEN}",
      "BEEMINDER_USERNAME": "${BEEMINDER_USERNAME}"
    }
  }
}
```

---

## 4. Installation Flow with Security

### 4.1 Package Installation Flow

```
User runs: aiconfig package install acme/brand-kit
    │
    ├──> Check if package exists in library
    │    └──> If not: Download from repo to ~/.instructionkit/library/acme/brand-kit/
    │
    ├──> Parse ai-config-kit-package.yaml manifest
    │
    ├──> Validate package requirements
    │    └──> Check ai-config-kit version >= 0.4.0
    │
    ├──> Detect available AI tools
    │
    ├──> Install components (per AI tool compatibility):
    │    │
    │    ├──> Instructions:
    │    │    └──> Copy to .cursor/rules/, .claude/rules/, etc.
    │    │
    │    ├──> MCP Servers:
    │    │    ├──> Check for required credentials
    │    │    ├──> Prompt user for credentials (interactive)
    │    │    ├──> Store in <project>/.instructionkit/.env
    │    │    ├──> Merge template + credentials → IDE MCP config
    │    │    └──> Ensure .env in .gitignore
    │    │
    │    ├──> Hooks:
    │    │    └──> Copy to .claude/hooks/ (if Claude detected)
    │    │
    │    ├──> Commands:
    │    │    └──> Copy to .cursor/commands/, etc.
    │    │
    │    └──> Resources:
    │         └──> Copy to .instructionkit/resources/brand-kit/
    │
    ├──> Track in <project>/.instructionkit/packages.json
    │
    ├──> Auto-update ~/.instructionkit/registry.json
    │
    └──> Display summary:
         ✓ Installed 2 instructions
         ✓ Configured 1 MCP server (Beeminder)
         ✓ Installed 1 hook (Claude only)
         ✓ Installed 1 command
         ✓ Installed 5 resources
         ⚠ Skipped 1 hook (not supported by Cursor)
```

### 4.2 MCP Security Integration

**Critical security principles:**

1. **Never commit credentials**
   - All `.env` files auto-added to `.gitignore`
   - Warn user if `.env` not gitignored

2. **Template-based configs**
   - Package contains template with `${VAR}` placeholders
   - Real values only in `.env` files

3. **Project overrides global**
   - Project `.env` takes precedence
   - Allows per-project API keys

4. **Validation before sync**
   - Check all required vars are set
   - Validate format if possible
   - Test connectivity (future enhancement)

5. **Update preservation**
   - Package updates only update template structure
   - Existing credentials are preserved
   - User notified if new credentials required

**Example update flow**:
```
User runs: aiconfig package update brand-kit

Updating brand-kit 1.2.0 → 2.0.0

✓ Instructions updated (2 modified, 1 new)
✓ MCP template updated (structure only)
⚠ New MCP server added: ClickUp

  ClickUp requires credentials:
  ? Enter CLICKUP_API_KEY: ********

✓ Credentials stored in .instructionkit/.env
✓ MCP config synced to claude_desktop_config.json
✓ Resources updated (3 modified, 2 new)

Existing Beeminder credentials preserved.
```

---

## 5. Custom Files (Resources) Support

### 5.1 Use Cases

**Brand Kit**:
- Logo files (PNG, SVG)
- Brand guidelines (PDF)
- Color palettes (JSON)
- Font files (TTF, OTF, ZIP)
- Style guides (Markdown)

**API Documentation**:
- API spec files (OpenAPI YAML)
- Postman collections (JSON)
- Authentication guides (PDF)
- Example payloads (JSON)

**Project Templates**:
- Configuration examples (YAML, JSON)
- Database schemas (SQL)
- Diagrams (PNG, SVG)
- Architecture docs (PDF, Markdown)

### 5.2 Resource Installation

**Storage location**: `<project>/.instructionkit/resources/<package-name>/`

**Why this location?**
- ✅ Colocated with other package data
- ✅ Gitignored by default (can opt-in to commit if desired)
- ✅ Preserved across package updates (unless changed)
- ✅ Easy to reference from instructions or MCP servers

**Example instruction referencing resource**:
```markdown
# Brand Guidelines

Our brand colors are defined in the color palette file:
`<project>/.instructionkit/resources/brand-kit/colors.json`

Our logo files:
- PNG: `.instructionkit/resources/brand-kit/logo.png`
- SVG: `.instructionkit/resources/brand-kit/logo.svg`

For complete guidelines, see:
`.instructionkit/resources/brand-kit/brand-guide.pdf`
```

### 5.3 Resource Updates

**Update strategy**:
- Check checksum to detect changes
- If changed: prompt user (like instructions)
  - Keep local version (user may have customized)
  - Update to new version
  - View differences (if text-based)

---

## 6. User Mental Model Analysis

### 6.1 Conceptual Hierarchy (User Perspective)

```
AI Config Kit
├── Library (Downloaded repos)
│   ├── Instruction Repos
│   ├── MCP Template Repos
│   └── Package Repos            [NEW]
│
├── Project Installations (What's active in THIS project)
│   ├── Instructions             [EXISTING]
│   ├── MCP Servers              [EXISTING - Feature 003]
│   ├── Templates                [EXISTING - Feature 002]
│   └── Packages                 [NEW - Feature 004]
│       ├── Contains: Instructions, MCP servers, hooks, commands, resources
│       └── Versioned as a unit
│
└── Global Registry (What's installed WHERE)  [NEW]
    └── Cross-project visibility
```

### 6.2 Is This Intuitive?

✅ **YES - Package abstraction is familiar:**
- Like `npm install` (packages contain multiple files)
- Like `apt install` (packages have dependencies)
- Like Docker images (layers with different types of content)

✅ **YES - Library vs. Installed distinction is clear:**
- Library = Downloaded (not active yet)
- Installed = Active in a project
- Same pattern as existing instructions

✅ **YES - Scope makes sense:**
- Project-level = This project only
- Global-level = All projects (deferred to v2)

⚠️ **POTENTIAL CONFUSION - Too many tracker files:**

**Current state** (with packages):
```
<project>/.instructionkit/
├── installations.json              # Instructions
├── packages.json                   # Packages
├── template-installations.json     # Templates
└── (future: mcp-installations.json?)  # MCP servers
```

**User question**: "Where do I look to see what's installed?"

### 6.3 Recommendation: Unified Installation Manifest

**OPTION A: Keep separate trackers** (as designed above)
- ✅ Simple implementation
- ✅ Backward compatible
- ❌ User confusion (4 tracker files!)
- ❌ Harder to query "show me everything installed"

**OPTION B: Unified tracker** ⭐ **RECOMMENDED**

```json
// <project>/.instructionkit/manifest.json
{
  "version": "1.0",
  "updated_at": "2025-11-14T10:30:00Z",

  "instructions": [
    {
      "name": "python-best-practices",
      "ai_tool": "cursor",
      "source_repo": "acme/instructions",
      "installed_path": ".cursor/rules/python-best-practices.mdc",
      "checksum": "sha256",
      "installed_via": null  // or "package:brand-kit"
    }
  ],

  "packages": [
    {
      "name": "brand-kit",
      "version": "1.2.0",
      "namespace": "acme/brand-kit",
      "components": [...]
    }
  ],

  "mcp_servers": [
    {
      "name": "beeminder",
      "namespace": "beeminder-mcp",
      "config_path": ".instructionkit/mcp/beeminder-mcp/",
      "installed_via": "package:brand-kit"
    }
  ],

  "templates": [
    {
      "file_id": "uuid",
      "source": "template-repo",
      "installed_path": "..."
    }
  ]
}
```

**Benefits**:
- ✅ Single source of truth
- ✅ Clear "what's installed" view
- ✅ Tracks relationships (installed_via)
- ✅ Can still query by type
- ⚠️ Migration needed from existing files

**Migration path**:
1. Keep backward compatibility (read old files)
2. On first package install, migrate to unified manifest
3. Preserve old files for rollback
4. Document migration in v0.4.0 release notes

---

## 7. Command Structure

### 7.1 Proposed Commands

**Package management**:
```bash
# Install package
aiconfig package install <namespace>          # From library
aiconfig package install <url>                # From URL (downloads first)
aiconfig package install <path>               # From local path

# Browse packages
aiconfig package list                         # Available in library
aiconfig package list --installed             # Installed in current project
aiconfig package list --all-projects          # All installations (uses registry)

# Package details
aiconfig package info <namespace>             # Show package details
aiconfig package components <namespace>       # List all components

# Update packages
aiconfig package update <namespace>           # Update to latest
aiconfig package update <namespace> --version 1.2.0  # Specific version
aiconfig package update --all                 # Update all packages

# Remove packages
aiconfig package uninstall <namespace>        # From current project
aiconfig package delete <namespace>           # From library

# Version management
aiconfig package versions <namespace>         # Show available versions
aiconfig package rollback <namespace>         # Revert to previous version
```

**Global registry management**:
```bash
# Scan projects to update main registry
aiconfig scan                                 # Scan current project
aiconfig scan ~/projects/                     # Scan directory tree
aiconfig scan --all                           # Scan all known projects

# Query cross-project installations
aiconfig projects                             # List all tracked projects
aiconfig projects --using <package>           # Which projects use this package?
aiconfig projects --outdated                  # Projects with outdated packages

# Registry maintenance
aiconfig registry show                        # Display full registry
aiconfig registry validate                    # Check consistency
aiconfig registry cleanup                     # Remove non-existent projects
```

**Backward compatible** (existing commands still work):
```bash
aiconfig install <instruction>                # Still works (individual instruction)
aiconfig list                                 # Still works (installed instructions)
aiconfig update                               # Still works (update instructions)
```

### 7.2 Is This Confusing?

**Potential confusion**:
- `aiconfig install` vs. `aiconfig package install`
- Are they the same? Different?

**Solution - Clear distinction**:
```bash
# Individual components
aiconfig install <instruction-name>           # Install single instruction
aiconfig mcp install <mcp-server>             # Install single MCP server

# Bundles (packages)
aiconfig package install <package-name>       # Install package (multiple components)
```

**User mental model**:
- "install" = single component
- "package install" = bundle of components

Alternative names considered:
- `aiconfig bundle install` - clearer but less standard
- `aiconfig pkg install` - shorter but less discoverable
- ⭐ `aiconfig package install` - most familiar (npm, apt, pip)

---

## 8. Final Recommendations

### 8.1 Core Decisions

| Decision | Recommendation | Rationale |
|----------|----------------|-----------|
| **Dual Registry** | ✅ Implement | Provides cross-project visibility |
| **Package Tracker** | ✅ Separate `packages.json` initially | Simpler implementation, can unify later |
| **Unified Manifest** | ⚠️ Consider for v0.5.0 | Better UX but requires migration |
| **Custom Resources** | ✅ Implement | Critical for brand kits, docs |
| **MCP Security** | ✅ Use template pattern | Secure, consistent with Feature 003 |
| **Versioning** | ✅ Full semantic versioning | Essential for packages |
| **Global Scope** | ❌ Defer to v2 | Reduce initial complexity |

### 8.2 Updated Spec Requirements

**Add to spec**:

1. **Main Registry**:
   - FR-NEW: System MUST maintain a main registry at `~/.instructionkit/registry.json`
   - FR-NEW: System MUST auto-update registry on install/uninstall operations
   - FR-NEW: System MUST provide scan command to rebuild registry from projects

2. **Package Versioning**:
   - FR-NEW: Package manifest MUST declare semantic version (major.minor.patch)
   - FR-NEW: System MUST track installed package version
   - FR-NEW: System MUST detect available updates
   - FR-NEW: System MUST support updating to specific versions
   - FR-NEW: System MUST support rollback to previous versions

3. **MCP Security**:
   - FR-NEW: MCP configs in packages MUST be templates with `${VAR}` placeholders
   - FR-NEW: System MUST prompt for required credentials during installation
   - FR-NEW: System MUST store credentials in `.instructionkit/.env` (gitignored)
   - FR-NEW: System MUST merge template + credentials when syncing to IDE
   - FR-NEW: System MUST preserve credentials during package updates
   - FR-NEW: System MUST warn if `.env` not in `.gitignore`
   - FR-NEW: Package manifest MUST declare required credentials per MCP server

4. **Custom Resources**:
   - FR-NEW: Packages MUST support resource components (any file type)
   - FR-NEW: Resources MUST be installed to `.instructionkit/resources/<package-name>/`
   - FR-NEW: Resources MUST be tracked with checksums for update detection
   - FR-NEW: Resource updates MUST prompt user for conflict resolution
   - FR-NEW: Common resource types: PDF, PNG, SVG, JSON, YAML, ZIP, fonts, etc.

5. **Project Discovery**:
   - FR-NEW: System MUST auto-register projects in main registry on first install
   - FR-NEW: System MUST provide scan command for manual registry sync
   - FR-NEW: Scan MUST detect and update registry from project manifests
   - FR-NEW: Registry MUST trust project manifests as source of truth

6. **Command Structure**:
   - FR-NEW: Package commands MUST use `aiconfig package <action>` format
   - FR-NEW: Existing `aiconfig install` MUST remain for backward compatibility
   - FR-NEW: Cross-project queries MUST use `aiconfig projects` commands

### 8.3 Implementation Priority

**Phase 1 (MVP - v0.4.0)**:
1. Package manifest format
2. Package installation (project-level only)
3. Resource component support
4. MCP template security integration
5. Package versioning and tracking
6. Main registry with auto-update
7. Basic scan command

**Phase 2 (v0.4.1)**:
1. Package update command
2. Version pinning
3. Rollback support
4. Advanced queries (--using, --outdated)

**Phase 3 (v0.5.0)**:
1. Unified manifest migration
2. Global-scope packages
3. Package dependencies
4. Package bundles (packages of packages)

### 8.4 User Experience Validation

**User Story Walkthrough**:

1. **Brand Kit Installation**:
   ```bash
   $ aiconfig package install acme/brand-kit

   📦 Installing package: brand-kit v1.2.0

   ✓ Downloaded to library
   ✓ Detected AI tools: Claude Code, Cursor

   📝 Installing 2 instructions...
   ✓ brand-guidelines → .claude/rules/brand-guidelines.md
   ✓ color-palette → .cursor/rules/color-palette.mdc

   🔌 Installing MCP server: Beeminder
   ⚠ Beeminder requires credentials

   ? Enter BEEMINDER_AUTH_TOKEN: ********
   ? Enter BEEMINDER_USERNAME: myuser

   ✓ Credentials stored in .instructionkit/.env
   ✓ MCP config synced to claude_desktop_config.json

   📁 Installing 5 resources...
   ✓ logo.png → .instructionkit/resources/brand-kit/
   ✓ logo.svg → .instructionkit/resources/brand-kit/
   ✓ brand-guide.pdf → .instructionkit/resources/brand-kit/
   ✓ fonts.zip → .instructionkit/resources/brand-kit/
   ✓ colors.json → .instructionkit/resources/brand-kit/

   ✅ Package installed successfully!

   Summary:
   - 2 instructions (Claude, Cursor)
   - 1 MCP server configured
   - 5 resources
   - 0 hooks (Cursor doesn't support hooks)
   ```

2. **Cross-Project Query**:
   ```bash
   $ aiconfig projects --using brand-kit

   Projects using package 'brand-kit':

   /Users/troy/acme-web          v1.2.0  (2 days ago)
   /Users/troy/acme-mobile       v1.1.0  (outdated)
   /Users/troy/client-portal     v1.2.0  (5 hours ago)

   Tip: Run 'aiconfig package update brand-kit' in outdated projects
   ```

3. **Package Update**:
   ```bash
   $ aiconfig package update brand-kit

   Updating brand-kit 1.2.0 → 2.0.0

   ✓ 2 instructions updated
   ✓ MCP template updated (credentials preserved)
   ⚠ 3 resources modified, keeping local versions

   ? Updated resources available. View changes?
     › Yes, show diffs
       No, keep my versions
       Update all resources
   ```

**User feedback checkpoint**: Does this feel intuitive? Clear? Confusing?

---

## 9. Conclusion

### 9.1 Integration Assessment

✅ **Package system integrates well with existing architecture**
- Follows established patterns (dual registry, scope, tracking)
- Extends existing models cleanly
- Reuses MCP credential system
- Fits naturally with library structure

⚠️ **Minor concerns addressed**:
- Unified manifest considered for future (reduces tracker files)
- Command structure disambiguated (install vs. package install)
- Resource storage location chosen (.instructionkit/resources/)

✅ **User experience is intuitive**:
- Package abstraction is familiar
- Clear hierarchy (library → install → track)
- Secure by default (credentials in .env)
- Powerful queries (cross-project visibility)

### 9.2 Next Steps

1. ✅ **Review this architecture document** with stakeholders
2. ⬜ **Update spec** with detailed FR requirements (registries, versioning, security, resources)
3. ⬜ **Create data models** (Package, PackageComponent, MainRegistry, etc.)
4. ⬜ **Design package manifest schema** (validation rules)
5. ⬜ **Implement Phase 1** (MVP features)
6. ⬜ **User testing** (validate mental model assumptions)
7. ⬜ **Iterate** based on feedback

---

**Prepared by**: Claude Code
**Review Status**: Pending stakeholder approval
**Target Release**: v0.4.0
