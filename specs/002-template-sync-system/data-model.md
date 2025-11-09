# Data Model: Template Sync System

**Date**: 2025-11-09
**Feature**: Template Sync System
**Phase**: Phase 1 - Design

This document defines all data entities, their attributes, relationships, validation rules, and state transitions for the Template Sync System.

---

## Entity Diagram

```
┌─────────────────────┐
│ TemplateRepository  │
│─────────────────────│
│ + name              │
│ + description       │
│ + version           │
│ + source_url        │
│ + author            │
│ + manifest_path     │
└──────┬──────────────┘
       │
       │ contains
       │
       ├──────────────────────────┐
       │                          │
       ▼                          ▼
┌─────────────────┐     ┌─────────────────┐
│ Template        │     │ TemplateBundle  │
│─────────────────│     │─────────────────│
│ + name          │     │ + name          │
│ + description   │     │ + description   │
│ + files         │     │ + template_refs │
│ + tags          │     │ + tags          │
│ + dependencies  │     └─────────────────┘
└────────┬────────┘
         │
         │ installed as
         │
         ▼
┌──────────────────────────────┐
│ TemplateInstallationRecord   │
│──────────────────────────────│
│ + id                         │
│ + template_name              │
│ + source_repo                │
│ + source_version             │
│ + installed_path             │
│ + scope                      │
│ + installed_at               │
│ + checksum                   │
│ + ide_type                   │
└──────────────────────────────┘
```

---

## Entity Definitions

### 1. TemplateRepository

Represents a collection of templates downloaded from a Git repository.

**Attributes:**

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `name` | string | Yes | Human-readable repository name | Non-empty, max 100 chars |
| `description` | string | Yes | Repository purpose/contents | Non-empty, max 500 chars |
| `version` | string | Yes | Semantic version | Format: `X.Y.Z` (semver) |
| `source_url` | string | Yes | Git repository URL | Valid Git URL (https:// or git@) |
| `author` | string | No | Repository maintainer | Max 100 chars |
| `manifest_path` | Path | Yes | Path to templatekit.yaml | Must exist on filesystem |
| `templates` | List[Template] | Yes | Templates in this repository | Min 1 template |
| `bundles` | List[TemplateBundle] | No | Predefined template bundles | Optional |
| `cloned_at` | datetime | Yes | When repository was cloned | Auto-set on creation |
| `last_checked` | datetime | No | Last update check timestamp | Updated on `inskit template update` |

**Relationships:**
- Contains 1-to-many Templates
- Contains 0-to-many TemplateBundles

**Validation Rules:**
1. Repository name must be unique within installation scope
2. Version must follow semantic versioning (MAJOR.MINOR.PATCH)
3. Source URL must be valid and accessible (checked at clone time)
4. Manifest path must exist and be valid YAML
5. At least one template must be defined

**Example:**
```python
TemplateRepository(
    name="team-coding-standards",
    description="Shared coding standards and commands",
    version="1.2.0",
    source_url="https://github.com/myteam/coding-standards",
    author="Platform Team",
    manifest_path=Path("~/.instructionkit/templates/team-coding-standards/templatekit.yaml"),
    templates=[...],
    bundles=[...],
    cloned_at=datetime(2025, 11, 9, 10, 30, 0),
    last_checked=None
)
```

---

### 2. Template

Represents an individual template (command, skill, guideline document) within a repository.

**Attributes:**

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `name` | string | Yes | Unique template identifier | Non-empty, alphanumeric + hyphens, max 50 chars |
| `description` | string | Yes | What this template provides | Non-empty, max 200 chars |
| `files` | List[TemplateFile] | Yes | File paths and IDE mappings | Min 1 file |
| `tags` | List[string] | No | Categorization tags | Each tag max 30 chars, lowercase |
| `dependencies` | List[string] | No | Other templates required | Must reference valid template names in same repo |
| `repository` | TemplateRepository | Yes | Parent repository | Back-reference |

**Sub-Entity: TemplateFile**

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `path` | string | Yes | Relative path from repo root | Must exist in repository |
| `ide` | IDEType | Yes | Target IDE or "all" | One of: all, cursor, claude, windsurf, copilot |

**Relationships:**
- Belongs to 1 TemplateRepository
- May depend on 0-to-many other Templates
- Creates 0-to-many TemplateInstallationRecords (when installed)

**Validation Rules:**
1. Template name must be unique within repository
2. Template name must be valid identifier (alphanumeric, hyphens, underscores)
3. At least one file must be specified
4. File paths must exist in repository
5. Dependencies must reference existing templates in same repository
6. Circular dependencies are not allowed

**State Transitions:**
```
Available (in repository) → Selected (user chooses to install) → Installed (on filesystem)
                                                                       ↓
                                                                  Outdated (remote updated)
                                                                       ↓
                                                                  Updated (sync complete)
```

**Example:**
```python
Template(
    name="python-style-guide",
    description="Python coding style and conventions",
    files=[
        TemplateFile(
            path="standards/python-style.md",
            ide="all"
        )
    ],
    tags=["python", "style", "standards"],
    dependencies=[],
    repository=<TemplateRepository>
)

Template(
    name="test-command",
    description="Standard testing command",
    files=[
        TemplateFile(path="commands/test.cursor.md", ide="cursor"),
        TemplateFile(path="commands/test.claude.md", ide="claude"),
        TemplateFile(path="commands/test.copilot.md", ide="copilot"),
    ],
    tags=["testing", "command"],
    dependencies=["python-style-guide"],  # Requires style guide
    repository=<TemplateRepository>
)
```

---

### 3. TemplateBundle

Represents a predefined collection of related templates that should be installed together.

**Attributes:**

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `name` | string | Yes | Bundle identifier | Non-empty, alphanumeric + hyphens, max 50 chars |
| `description` | string | Yes | What this bundle provides | Non-empty, max 200 chars |
| `template_refs` | List[string] | Yes | Template names in bundle | Min 2 templates, must reference valid templates |
| `tags` | List[string] | No | Categorization tags | Each tag max 30 chars, lowercase |
| `repository` | TemplateRepository | Yes | Parent repository | Back-reference |

**Relationships:**
- Belongs to 1 TemplateRepository
- References 2-to-many Templates (by name)

**Validation Rules:**
1. Bundle name must be unique within repository
2. Must reference at least 2 templates
3. All referenced templates must exist in same repository
4. Bundle cannot reference other bundles (no nesting)

**Example:**
```python
TemplateBundle(
    name="python-essentials",
    description="Essential Python templates for new projects",
    template_refs=["python-style-guide", "test-command", "lint-command"],
    tags=["python", "essential", "quickstart"],
    repository=<TemplateRepository>
)
```

---

### 4. TemplateInstallationRecord

Tracks an installed template in a project or globally, enabling update detection and conflict resolution.

**Attributes:**

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `id` | string | Yes | Unique installation ID | UUID v4 |
| `template_name` | string | Yes | Installed template identifier | Must match Template.name |
| `source_repo` | string | Yes | Source repository name | Must match TemplateRepository.name |
| `source_version` | string | Yes | Repository version at install | Semantic version format |
| `installed_path` | Path | Yes | Absolute path to installed file | Must exist on filesystem |
| `scope` | InstallationScope | Yes | Installation scope | "project" or "global" |
| `namespace` | string | Yes | Repository namespace (derived from repo name) | Alphanumeric + hyphens, max 50 chars |
| `installed_at` | datetime | Yes | Installation timestamp | ISO 8601 format |
| `checksum` | string | Yes | SHA-256 of installed content | 64-character hex string |
| `ide_type` | IDEType | Yes | Target IDE for this installation | cursor, claude, windsurf, copilot |
| `custom_metadata` | dict | No | User-defined metadata | JSON-serializable dict |

**Enums:**

```python
class InstallationScope(Enum):
    PROJECT = "project"  # Installed in project directory
    GLOBAL = "global"    # Installed in user's home directory

class IDEType(Enum):
    CURSOR = "cursor"
    CLAUDE = "claude"
    WINDSURF = "windsurf"
    COPILOT = "copilot"
```

**Relationships:**
- References 1 Template (by name)
- References 1 TemplateRepository (by name)

**Validation Rules:**
1. Installation ID must be unique across all installations
2. Template name must exist in source repository
3. Installed path must be absolute
4. Checksum must be valid SHA-256 (64 hex characters)
5. Scope must be either "project" or "global"
6. Namespace must be non-empty and valid identifier format
7. Installed path must follow dot-notation: `{base_path}/{namespace}.{template_name}.{ext}`

**State Transitions:**
```
Created (template installed) → Current (in sync with source)
                                    ↓
                                Outdated (source has newer version)
                                    ↓
                                Conflicted (local + remote both changed)
                                    ↓
                                Resolved (user chose keep/overwrite/rename)
                                    ↓
                                Updated (sync complete)
```

**Persistence:**

Stored in JSON file:
- Project scope: `<project-root>/.instructionkit/template-installations.json`
- Global scope: `~/.instructionkit/global-template-installations.json`

**Example JSON:**
```json
{
  "installations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "template_name": "python-style-guide",
      "source_repo": "team-coding-standards",
      "source_version": "1.2.0",
      "namespace": "team-coding-standards",
      "installed_path": "/home/user/project/.cursor/rules/team-coding-standards.python-style-guide.md",
      "scope": "project",
      "installed_at": "2025-11-09T10:45:00Z",
      "checksum": "a3b5c7d9e1f2a3b5c7d9e1f2a3b5c7d9e1f2a3b5c7d9e1f2a3b5c7d9e1f2a3b5",
      "ide_type": "cursor",
      "custom_metadata": {}
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "template_name": "test-command",
      "source_repo": "team-coding-standards",
      "source_version": "1.2.0",
      "namespace": "team-coding-standards",
      "installed_path": "/home/user/project/.cursor/rules/team-coding-standards.test-command.mdc",
      "scope": "project",
      "installed_at": "2025-11-09T10:45:02Z",
      "checksum": "b4c6d8e0f3b4c6d8e0f3b4c6d8e0f3b4c6d8e0f3b4c6d8e0f3b4c6d8e0f3b4c6",
      "ide_type": "cursor",
      "custom_metadata": {}
    }
  ],
  "last_updated": "2025-11-09T10:45:02Z",
  "schema_version": "1.0"
}
```

---

### 5. ValidationIssue

Represents a problem detected during template validation.

**Attributes:**

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `issue_type` | IssueType | Yes | Type of validation issue | Enum value |
| `severity` | IssueSeverity | Yes | How critical the issue is | error, warning, info |
| `title` | string | Yes | Short description of issue | Max 100 chars |
| `description` | string | Yes | Detailed explanation | Max 500 chars |
| `affected_items` | List[string] | Yes | Templates/repos affected | Min 1 item |
| `recommendation` | string | Yes | How to fix the issue | Max 300 chars |
| `auto_fixable` | bool | Yes | Can system auto-fix this? | True/False |
| `fix_command` | string | No | Command to fix issue | CLI command string |
| `ai_analysis` | AIAnalysis | No | AI-provided insights | Optional AI recommendations |

**Enums:**

```python
class IssueType(Enum):
    TRACKING_INCONSISTENCY = "tracking_inconsistency"  # File exists but not tracked
    MISSING_FILE = "missing_file"  # Tracked but file missing
    OUTDATED = "outdated"  # Newer version available
    BROKEN_DEPENDENCY = "broken_dependency"  # Required template not installed
    LOCAL_MODIFICATION = "local_modification"  # File changed since install
    SEMANTIC_CONFLICT = "semantic_conflict"  # AI detected conflicting guidance
    CLARITY_ISSUE = "clarity_issue"  # AI detected unclear instructions

class IssueSeverity(Enum):
    ERROR = "error"  # Must fix
    WARNING = "warning"  # Should fix
    INFO = "info"  # Nice to know
```

**Sub-Entity: AIAnalysis** (Optional)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `confidence` | float | Yes | AI confidence (0.0-1.0) |
| `explanation` | string | Yes | Why AI flagged this |
| `suggested_fix` | string | No | AI-generated fix |
| `can_merge` | bool | No | For conflicts: mergeable? |
| `merge_suggestion` | string | No | Merged version |

**Example:**

```python
ValidationIssue(
    issue_type=IssueType.SEMANTIC_CONFLICT,
    severity=IssueSeverity.WARNING,
    title="Conflicting error handling guidance",
    description="python-style-guide and error-patterns contradict each other",
    affected_items=["python-style-guide", "error-patterns"],
    recommendation="Align error-patterns with python-style-guide philosophy",
    auto_fixable=False,
    ai_analysis=AIAnalysis(
        confidence=0.85,
        explanation="Both templates discuss exception handling with opposite guidance",
        suggested_fix="Use minimal exception handling as per style guide"
    )
)
```

---

## Data Flow

### Installation Flow

```
1. User runs: inskit template install <repo-url> [--as namespace]
   ↓
2. System derives namespace:
   - If --as provided: use that
   - Else: extract repo name from URL (e.g., "coding-standards" from github.com/team/coding-standards)
   ↓
3. System clones TemplateRepository
   ↓
4. System parses templatekit.yaml → creates TemplateRepository entity
   ↓
5. User selects Templates (or installs all)
   ↓
6. For each Template:
   - Detect IDE(s) in project
   - Convert template to IDE-specific format(s)
   - Construct namespaced filename: {namespace}.{template_name}.{ext}
   - Write file to IDE-specific directory (e.g., .cursor/rules/team.test-command.md)
   - Calculate checksum of installed content
   - Create TemplateInstallationRecord (with namespace field)
   - Append to installations.json
```

### Update Flow

```
1. User runs: inskit template update <repo-name>
   ↓
2. System pulls latest from Git repository
   ↓
3. System parses updated templatekit.yaml
   ↓
4. System compares versions (old vs new)
   ↓
5. For each changed Template:
   - Read TemplateInstallationRecord (get original checksum)
   - Calculate current file checksum
   - Calculate new template checksum
   - Detect conflict type (none, local_modified, both_modified)
   ↓
6. If conflict:
   - Prompt user for resolution (keep/overwrite/rename)
   - Apply user's choice
   ↓
7. Update TemplateInstallationRecord with new version + checksum
```

### Precedence Resolution (Global vs Project)

```
When IDE loads templates:
   ↓
1. Scan project-level: <project>/.cursor/rules/*.md
   ↓
2. Scan global-level: ~/.instructionkit/global-templates/cursor/*.md
   ↓
3. For each template filename:
   - If exists in project-level → use project version (precedence)
   - Else if exists in global-level → use global version
   ↓
4. Merge effective templates (project overrides global)
```

---

## Validation & Constraints Summary

| Entity | Key Constraints |
|--------|----------------|
| **TemplateRepository** | Unique name per scope, valid semver, accessible Git URL, min 1 template |
| **Template** | Unique name in repo, no circular dependencies, valid file paths, valid IDE types |
| **TemplateBundle** | Min 2 templates, all refs exist, no bundle nesting |
| **TemplateInstallationRecord** | Unique ID, valid checksum (SHA-256), absolute path, scope enum |

---

## Schema Evolution

**Current Version**: 1.0

**Future Considerations**:
- **Multi-version support**: Allow installing multiple versions of same template
- **Rollback**: Store previous versions for quick rollback
- **Template variants**: Support A/B testing of template versions
- **Usage analytics**: Track which templates are most used
- **Template deprecation**: Mark templates as deprecated with migration guides

---

## Next Steps

With data model defined, proceed to:
1. Generate CLI contracts (`contracts/cli-commands.yaml`)
2. Generate quickstart guide (`quickstart.md`)
3. Update agent context with new patterns
