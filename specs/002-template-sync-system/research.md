# Research Findings: Template Sync System

**Date**: 2025-11-09
**Feature**: Template Sync System
**Phase**: Phase 0 - Research & Technical Decisions

This document consolidates research findings for all technical unknowns identified in the implementation plan. Each section presents the decision made, rationale, alternatives considered, and implementation guidance.

---

## 1. Template Manifest Format

### Decision

Use YAML manifest file named `templatekit.yaml` at repository root with the following schema:

```yaml
name: "Team Coding Standards"
description: "Shared coding standards and commands for our team"
version: "1.2.0"
author: "Platform Team"

templates:
  - name: python-style-guide
    description: "Python coding style and conventions"
    files:
      - path: standards/python-style.md
        ide: all  # Works for all IDEs
    tags: [python, style, standards]

  - name: test-command
    description: "Standard testing command"
    files:
      - path: commands/test.cursor.md
        ide: cursor
      - path: commands/test.claude.md
        ide: claude
      - path: commands/test.copilot.md
        ide: copilot
      - path: commands/test.windsurf.md
        ide: windsurf
    tags: [testing, command]
    dependencies: [python-style-guide]  # Requires this template

  - name: deploy-command
    description: "Deployment command"
    files:
      - path: commands/deploy.md
        ide: all
    tags: [deployment, command]

bundles:
  - name: python-essentials
    description: "Essential Python templates"
    templates: [python-style-guide, test-command]
    tags: [python, essential]

  - name: full-stack
    description: "Complete template set"
    templates: [python-style-guide, test-command, deploy-command]
    tags: [complete]
```

### Rationale

1. **Consistency with existing InstructionKit**: Mirrors `instructionkit.yaml` format for instruction repositories
2. **IDE-specific support**: Allows per-IDE file variants when needed while supporting "all" for generic templates
3. **Dependency tracking**: Templates can declare dependencies on other templates
4. **Bundle support**: Enables installing related templates as a group
5. **Semantic versioning**: Standard version format for tracking updates
6. **Metadata richness**: Tags, descriptions enable better discovery and selection

### Alternatives Considered

**Alternative 1: JSON format**
- Pros: Strictly validated, native Python parsing
- Cons: Less human-readable, no comments, more verbose
- Rejected: YAML is more maintainable for config files

**Alternative 2: Per-template metadata files**
- Structure: Each template has companion `.meta.yaml`
- Pros: Metadata colocated with template files
- Cons: Multiple files to track, harder to get repository overview
- Rejected: Single manifest easier to validate and version

**Alternative 3: Convention over configuration**
- Structure: No manifest, infer from directory structure
- Pros: Less boilerplate, automatic discovery
- Cons: No explicit dependencies, versions, or IDE mappings
- Rejected: Not flexible enough for complex template repos

### Implementation Notes

```python
# instructionkit/core/template_manifest.py

from dataclasses import dataclass
from typing import List, Optional, Literal
import yaml

IDEType = Literal["all", "cursor", "claude", "windsurf", "copilot"]

@dataclass
class TemplateFile:
    path: str
    ide: IDEType = "all"

@dataclass
class TemplateDefinition:
    name: str
    description: str
    files: List[TemplateFile]
    tags: List[str]
    dependencies: List[str] = None

@dataclass
class TemplateBundle:
    name: str
    description: str
    templates: List[str]
    tags: List[str]

@dataclass
class TemplateManifest:
    name: str
    description: str
    version: str
    author: Optional[str]
    templates: List[TemplateDefinition]
    bundles: List[TemplateBundle]

    @classmethod
    def load(cls, manifest_path: Path) -> "TemplateManifest":
        """Load and validate manifest from YAML file"""
        with open(manifest_path, 'r') as f:
            data = yaml.safe_load(f)
        # Validate and construct dataclass
        # Raise TemplateManifestError if invalid
```

---

## 2. Git Operations with Credential Helpers

### Decision

Use **GitPython** library with system Git credential helpers (no custom credential storage). Rely on user's existing Git configuration for authentication.

```python
from git import Repo
from git.exc import GitCommandError
from pathlib import Path

def clone_template_repo(url: str, destination: Path) -> Repo:
    """
    Clone template repository using system Git credentials.

    Raises:
        TemplateAuthError: If authentication fails
        TemplateNetworkError: If network/repository unavailable
    """
    try:
        repo = Repo.clone_from(
            url=url,
            to_path=str(destination),
            depth=1,  # Shallow clone for performance
            env={
                'GIT_TERMINAL_PROMPT': '0',  # Fail if credentials needed but not available
            }
        )
        return repo
    except GitCommandError as e:
        if 'Authentication failed' in str(e) or '401' in str(e) or '404' in str(e):
            raise TemplateAuthError(
                f"Authentication failed for {url}. "
                f"Ensure Git credentials are configured (git credential-helper or SSH keys)."
            ) from e
        raise TemplateNetworkError(f"Failed to clone repository: {e}") from e

def update_template_repo(repo_path: Path) -> bool:
    """
    Pull latest changes from template repository.

    Returns:
        True if updates were pulled, False if already up-to-date
    """
    repo = Repo(repo_path)
    origin = repo.remotes.origin

    fetch_info = origin.fetch()[0]

    # Check if remote has changes
    if repo.head.commit == fetch_info.commit:
        return False  # Already up-to-date

    # Pull changes
    origin.pull()
    return True
```

### Rationale

1. **No credential storage**: Leverages existing Git setup (credential.helper, SSH keys)
2. **Security**: Doesn't ask users to provide tokens/passwords to InstructionKit
3. **Standard workflow**: Same auth as `git clone` in terminal
4. **Cross-platform**: Works on Windows (Credential Manager), macOS (Keychain), Linux (gnome-keyring, etc.)
5. **Private repo support**: Automatically works if user has access configured

### Alternatives Considered

**Alternative 1: Custom token management**
- Store GitHub PAT in InstructionKit config
- Pros: Simpler for users (one-time setup)
- Cons: Security risk, token rotation complexity, platform-specific
- Rejected: Security concerns, duplicates Git's job

**Alternative 2: OAuth flow**
- Implement OAuth device flow for GitHub
- Pros: Secure, no manual token creation
- Cons: Complex, requires InstructionKit OAuth app, GitHub-specific
- Rejected: Over-engineered for MVP

**Alternative 3: Public repos only**
- Skip authentication entirely
- Pros: Simplest implementation
- Cons: Major limitation for enterprise teams
- Rejected: Private repos are a core requirement

### Implementation Notes

**Error Handling**:
```python
class TemplateAuthError(Exception):
    """Raised when Git authentication fails"""
    pass

class TemplateNetworkError(Exception):
    """Raised when network/repo unavailable"""
    pass
```

**User Guidance** (in error messages):
```
Authentication failed for private repository.

To configure Git credentials:

For HTTPS URLs:
  git config --global credential.helper store
  # Then perform a git clone manually to cache credentials

For SSH URLs:
  1. Generate SSH key: ssh-keygen -t ed25519
  2. Add to GitHub: cat ~/.ssh/id_ed25519.pub
  3. Use SSH URL: git@github.com:org/repo.git

Documentation: https://docs.instructionkit.dev/templates/auth
```

---

## 3. IDE Template Format Conversion

### Decision

**Minimal conversion approach**: Store templates in a "canonical format" (Markdown with YAML frontmatter) and apply IDE-specific transformations during installation.

**Canonical Template Format**:
```markdown
---
name: test-command
description: Run all tests with coverage
type: command
shortcut: /test
---

# Test Command

Runs the full test suite with coverage reporting.

## Usage

Type `/test` to run all tests.

## Implementation

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## Variables

- `{project_root}`: Project root directory
- `{python_version}`: Python version in use
```

**IDE-Specific Transformations**:

| IDE | File Extension | Transformation |
|-----|----------------|----------------|
| Cursor | `.mdc` | Remove YAML frontmatter, convert to Cursor's format |
| Claude Code | `.md` | Keep as-is (Markdown native) |
| Windsurf | `.md` | Keep as-is (Markdown native) |
| GitHub Copilot | `.md` | Add Copilot-specific comment headers |

### Rationale

1. **Single source of truth**: One template file → multiple IDE formats
2. **Maintainability**: Update once, deploy everywhere
3. **Future-proof**: Easy to add new IDE support
4. **Markdown base**: Universal, human-readable, Git-friendly

### Alternatives Considered

**Alternative 1: IDE-specific files in repository**
- Each template has cursor.mdc, claude.md, copilot.md variants
- Pros: No conversion logic needed
- Cons: Maintenance burden (4x files), drift between variants
- Rejected: Doesn't scale as IDEs added

**Alternative 2: Lowest common denominator**
- Use simplest format that works everywhere
- Pros: No conversion
- Cons: Can't use IDE-specific features (shortcuts, metadata)
- Rejected: Limits functionality

**Alternative 3: IDE query during install**
- Ask user which IDE they use, only install that format
- Pros: Simpler, smaller footprint
- Cons: Breaks multi-IDE support (user switches IDEs)
- Rejected: Violates multi-tool support requirement

### Implementation Notes

```python
# instructionkit/ai_tools/template_converter.py

from dataclasses import dataclass
from pathlib import Path
import yaml
from typing import Dict, Any

@dataclass
class CanonicalTemplate:
    """Parsed canonical template with metadata and content"""
    metadata: Dict[str, Any]  # YAML frontmatter
    content: str  # Markdown body

    @classmethod
    def parse(cls, template_path: Path) -> "CanonicalTemplate":
        """Parse template file with YAML frontmatter"""
        text = template_path.read_text()

        if text.startswith('---'):
            # Split frontmatter and content
            parts = text.split('---', 2)
            metadata = yaml.safe_load(parts[1])
            content = parts[2].strip()
        else:
            metadata = {}
            content = text

        return cls(metadata=metadata, content=content)

class TemplateConverter:
    """Convert canonical templates to IDE-specific formats"""

    def to_cursor(self, template: CanonicalTemplate) -> str:
        """Convert to Cursor .mdc format"""
        # Cursor uses special comment format for metadata
        output = []

        if 'name' in template.metadata:
            output.append(f"<!-- @name {template.metadata['name']} -->")
        if 'description' in template.metadata:
            output.append(f"<!-- @description {template.metadata['description']} -->")
        if 'shortcut' in template.metadata:
            output.append(f"<!-- @shortcut {template.metadata['shortcut']} -->")

        output.append("")
        output.append(template.content)

        return "\n".join(output)

    def to_claude(self, template: CanonicalTemplate) -> str:
        """Convert to Claude Code .md format"""
        # Claude Code uses YAML frontmatter natively
        # Return as-is or with minimal adjustments
        return self._reconstruct_frontmatter(template)

    def to_copilot(self, template: CanonicalTemplate) -> str:
        """Convert to GitHub Copilot .md format"""
        # Copilot uses special comment headers
        output = [template.content]

        if 'name' in template.metadata:
            # Add Copilot instruction header
            output.insert(0, f"# {template.metadata['name']}")
            output.insert(1, "")

        return "\n".join(output)

    def _reconstruct_frontmatter(self, template: CanonicalTemplate) -> str:
        """Reconstruct template with YAML frontmatter"""
        if not template.metadata:
            return template.content

        frontmatter = yaml.dump(template.metadata, default_flow_style=False)
        return f"---\n{frontmatter}---\n\n{template.content}"
```

---

## 4. Conflict Detection Strategy

### Decision

Use **content-based checksums** (SHA-256) stored in installation tracking to detect modifications. Prompt user on any detected change.

**Detection Algorithm**:
```python
def detect_conflict(
    installed_file: Path,
    new_template_content: str,
    installation_record: TemplateInstallationRecord
) -> ConflictType:
    """
    Detect if conflict exists between installed and new template.

    Returns:
        ConflictType.NONE: No conflict, safe to update
        ConflictType.LOCAL_MODIFIED: User modified local file
        ConflictType.BOTH_MODIFIED: Both local and remote changed
    """
    # Calculate current file checksum
    current_checksum = sha256_file(installed_file)

    # Compare with recorded checksum at installation
    original_checksum = installation_record.checksum

    # Calculate new template checksum
    new_checksum = sha256_string(new_template_content)

    # Decision matrix:
    if current_checksum == original_checksum:
        # File unchanged since installation
        if new_checksum == original_checksum:
            return ConflictType.NONE  # No changes anywhere
        else:
            return ConflictType.NONE  # Only remote changed, safe to update
    else:
        # File modified locally
        if new_checksum == original_checksum:
            return ConflictType.LOCAL_MODIFIED  # Only local changed
        else:
            return ConflictType.BOTH_MODIFIED  # Both changed
```

**User Prompt Flow**:
```python
def prompt_conflict_resolution(
    template_name: str,
    conflict_type: ConflictType
) -> ConflictResolution:
    """
    Interactive prompt for conflict resolution.

    Returns user's choice: KEEP, OVERWRITE, or RENAME
    """
    console = Console()

    console.print(f"\n[yellow]⚠️  Conflict detected for '{template_name}'[/yellow]")

    if conflict_type == ConflictType.LOCAL_MODIFIED:
        console.print("Local file was modified since installation")
    elif conflict_type == ConflictType.BOTH_MODIFIED:
        console.print("Both local and remote versions have changes")

    console.print("\nChoose action:")
    console.print("  [K]eep local version (ignore remote update)")
    console.print("  [O]verwrite with remote version (discard local changes)")
    console.print("  [R]ename local and install remote")

    choice = Prompt.ask(
        "Your choice",
        choices=["k", "o", "r", "K", "O", "R"],
        default="k"
    ).lower()

    return {
        'k': ConflictResolution.KEEP,
        'o': ConflictResolution.OVERWRITE,
        'r': ConflictResolution.RENAME
    }[choice]
```

### Rationale

1. **Checksum accuracy**: SHA-256 reliably detects any content change
2. **User control**: Always prompt, never silently overwrite
3. **Safety first**: Default to keeping local changes
4. **Clear feedback**: Show what changed and why conflict exists
5. **Tracked state**: Installation record stores original checksum

### Alternatives Considered

**Alternative 1: Timestamp-based**
- Compare file modification times
- Pros: Simpler, no checksum storage
- Cons: Unreliable (git clone resets timestamps), doesn't detect what changed
- Rejected: Not accurate enough

**Alternative 2: Three-way merge**
- Git-style merge of local, original, remote
- Pros: Preserves both changes when possible
- Cons: Complex, can fail, requires diff/merge logic
- Rejected: Over-complex for MVP, can add later

**Alternative 3: Always prompt**
- Prompt on every update regardless of changes
- Pros: Simpler logic
- Cons: Annoying for users (100 templates = 100 prompts)
- Rejected: Poor UX

**Alternative 4: Git-based tracking**
- Store templates in Git, use Git to detect changes
- Pros: Leverages Git's power
- Cons: Requires project be Git repo, complex setup
- Rejected: Not all projects use Git

### Implementation Notes

```python
# instructionkit/storage/template_tracker.py

from dataclasses import dataclass
from datetime import datetime
import hashlib
from pathlib import Path

@dataclass
class TemplateInstallationRecord:
    template_name: str
    source_repo: str
    source_version: str
    installed_path: str
    scope: str  # "project" or "global"
    installed_at: datetime
    checksum: str  # SHA-256 of content at installation

def sha256_file(file_path: Path) -> str:
    """Calculate SHA-256 checksum of file"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def sha256_string(content: str) -> str:
    """Calculate SHA-256 checksum of string"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
```

---

## 5. Progress Feedback Implementation

### Decision

Use **Rich library** with simple progress indicators: spinner during operations, status messages per template, summary table at end.

**Implementation Pattern**:

```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

def install_templates(repo_url: str, templates: List[Template]):
    """Install templates with progress feedback"""
    console = Console()

    # Phase 1: Cloning repository (spinner)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Cloning repository from {repo_url}...", total=None)
        repo = clone_template_repo(repo_url, destination)
        progress.update(task, completed=True)

    console.print(f"✓ Repository cloned\n", style="green")

    # Phase 2: Installing templates (per-template messages)
    installed = []
    skipped = []
    failed = []

    for template in templates:
        console.print(f"Installing [cyan]{template.name}[/cyan]...", end=" ")

        try:
            install_template(template)
            console.print("✓", style="green")
            installed.append(template.name)
        except TemplateInstallError as e:
            console.print(f"✗ {e}", style="red")
            failed.append(template.name)

    # Phase 3: Summary table
    console.print("\n")

    table = Table(title="Installation Summary")
    table.add_column("Status", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Templates", style="green")

    if installed:
        table.add_row("✓ Installed", str(len(installed)), ", ".join(installed[:5]))
    if skipped:
        table.add_row("⊘ Skipped", str(len(skipped)), ", ".join(skipped[:5]))
    if failed:
        table.add_row("✗ Failed", str(len(failed)), ", ".join(failed[:5]))

    console.print(table)
    console.print(f"\n[green]✓ Installation complete[/green]")
```

**Update Operation Example**:
```python
def update_templates(repo_name: str):
    """Update templates with progress feedback"""
    console = Console()

    # Check for updates
    with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
        task = progress.add_task(f"Checking for updates to {repo_name}...")
        has_updates, changed_templates = check_for_updates(repo_name)
        progress.update(task, completed=True)

    if not has_updates:
        console.print(f"[green]✓ {repo_name} is up-to-date[/green]")
        return

    console.print(f"\nFound updates for {len(changed_templates)} templates:\n")

    # Process each changed template
    for template_name, new_content in changed_templates:
        conflict = detect_conflict(template_name, new_content)

        if conflict != ConflictType.NONE:
            # Prompt user for conflict resolution
            resolution = prompt_conflict_resolution(template_name, conflict)
            apply_resolution(template_name, new_content, resolution)
        else:
            # Safe to auto-update
            console.print(f"Updating [cyan]{template_name}[/cyan]...", end=" ")
            update_template(template_name, new_content)
            console.print("✓", style="green")
```

### Rationale

1. **Rich library**: Already a dependency, feature-rich, great terminal UX
2. **Simple indicators**: Spinner for operations, checkmarks for status
3. **Per-item feedback**: User sees progress for each template
4. **Summary table**: Clear overview of what happened
5. **No percentage bars**: Template count varies, percentages add complexity

### Alternatives Considered

**Alternative 1: Detailed progress bars**
- Show percentage, bytes, estimated time
- Pros: More information
- Cons: Complex for variable-count operations, can be inaccurate
- Rejected: Over-engineered for typical template counts

**Alternative 2: Silent with final output**
- No progress, just final summary
- Pros: Simpler code
- Cons: Poor UX for slow operations (network latency)
- Rejected: Violates "clear feedback" requirement

**Alternative 3: Verbose logging**
- Print detailed log of every operation
- Pros: Helpful for debugging
- Cons: Cluttered output for normal use
- Rejected: Can be added as --verbose flag later

### Implementation Notes

**Color Scheme**:
- Green (✓): Success
- Yellow (⚠️): Warning
- Red (✗): Error
- Cyan: Emphasis (template names, counts)
- Magenta: Numbers

**Examples**:

```
# Installing templates
Cloning repository from github.com/team/templates... ✓ Repository cloned

Installing python-style-guide... ✓
Installing test-command... ✓
Installing deploy-command... ✓

┌─────────────────────────────────────────┐
│       Installation Summary              │
├──────────┬───────┬──────────────────────┤
│ Status   │ Count │ Templates            │
├──────────┼───────┼──────────────────────┤
│ ✓ Installed │ 3  │ python-style-guide,  │
│          │       │ test-command,        │
│          │       │ deploy-command       │
└──────────┴───────┴──────────────────────┘

✓ Installation complete
```

```
# Updating templates
Checking for updates to team/templates... ✓

Found updates for 2 templates:

⚠️  Conflict detected for 'test-command'
Local file was modified since installation
Choose action:
  [K]eep local version (ignore remote update)
  [O]verwrite with remote version (discard local changes)
  [R]ename local and install remote
Your choice [k]: o

Updating test-command... ✓
Updating python-style-guide... ✓

✓ Updated 2 templates
```

---

## 6. Namespace Strategy

### Decision

**Always namespace templates using dot notation** with repository name as default.

**Format**: `{namespace}.{template-name}.{ext}`

**Example**:
- Repository: `github.com/acme/coding-standards`
- Namespace: `coding-standards` (derived from repo name)
- Template: `test-command`
- Installed as: `.cursor/rules/coding-standards.test-command.md`
- Command: `/coding-standards.test`

**Override Option**: `--as` flag allows custom namespace
```bash
inskit template install github.com/acme/coding-standards --as acme
# Result: acme.test-command.md, command: /acme.test
```

### Rationale

1. **Zero collisions**: Every template uniquely identified by namespace
2. **Clear attribution**: Source visible in filename
3. **Simple mental model**: One rule, always applied
4. **Flat structure**: No subdirectory complexity, IDE-agnostic
5. **Command clarity**: `/namespace.command` is self-documenting

### Alternatives Considered

**Alternative 1: Optional namespacing**
- Pros: Simpler commands when possible
- Cons: Decision fatigue, collision management complexity
- Rejected: Complexity outweighs benefit

**Alternative 2: Subdirectory namespacing**
- Format: `.cursor/rules/namespace/template.md`
- Pros: Visual separation
- Cons: IDE compatibility unknown, path complexity
- Rejected: Dot notation is simpler and universally compatible

### Implementation Notes

```python
def derive_namespace(repo_url: str, override: Optional[str] = None) -> str:
    """
    Derive namespace from repository URL or use override.

    Examples:
    - github.com/org/repo-name → "repo-name"
    - Override "acme" → "acme"
    """
    if override:
        return override
    return extract_repo_name_from_url(repo_url)

def get_install_path(
    namespace: str,
    template_name: str,
    ide_base_path: Path,
    extension: str
) -> Path:
    """
    Construct namespaced installation path.

    Always uses dot notation: {namespace}.{template-name}.{ext}
    """
    filename = f"{namespace}.{template-name}.{extension}"
    return ide_base_path / filename
```

---

## 7. AI Validation Integration

### Decision

**Optional AI-powered validation** through provider abstraction, supporting multiple AI backends.

**Activation**: `--ai` flag on validate command
```bash
inskit template validate --ai
```

**Capabilities**:
1. Semantic conflict detection (contradictory guidance)
2. Template clarity analysis (understandability)
3. Cross-template consistency checking
4. Merge suggestions for conflicts

### Rationale

1. **Goes beyond syntax**: Understands meaning, not just structure
2. **Improves quality**: Actionable feedback for template authors
3. **Intelligent merging**: AI suggests how to combine conflicting templates
4. **Provider agnostic**: Works with any AI backend

### Provider Abstraction

```python
class ValidationProvider(ABC):
    @abstractmethod
    async def analyze_semantic_conflict(
        self, template1: str, template2: str
    ) -> dict:
        pass

    @abstractmethod
    async def analyze_clarity(self, template: str) -> dict:
        pass

# Implementations
- AnthropicValidationProvider (Claude API)
- CursorValidationProvider (Cursor AI)
- OpenAIValidationProvider (GPT API)
- Auto-detect based on environment
```

### Configuration

```yaml
# ~/.instructionkit/config.yaml
ai_validation:
  enabled: true
  provider: "auto"  # or: anthropic, cursor, openai
  api_key: "${ANTHROPIC_API_KEY}"
  min_confidence: 0.7
  cache_results: true
```

### Privacy & Cost

- **Privacy mode**: Local-only validation, no API calls
- **Cost estimation**: Warn before expensive operations
- **Caching**: Cache AI results for 24h to reduce costs

---

## Summary of Decisions

| Research Area | Decision | Key Rationale |
|--------------|----------|---------------|
| **Manifest Format** | YAML with `templatekit.yaml` | Consistency with instructionkit.yaml, human-readable, supports metadata |
| **Git Operations** | GitPython with system credentials | Security (no token storage), leverages existing Git setup |
| **IDE Conversion** | Canonical format → IDE-specific | Single source of truth, maintainable, extensible |
| **Conflict Detection** | SHA-256 checksums with prompts | Accurate, user control, safe defaults |
| **Progress Feedback** | Rich library with simple indicators | Clear UX, already a dependency, appropriate detail level |
| **Namespace Strategy** | Always namespace with dot notation | Zero collisions, clear attribution, simple |
| **AI Validation** | Optional provider-based integration | Semantic understanding, quality improvement, flexible |

---

## Next Steps

With all technical decisions made, proceed to **Phase 1: Design & Contracts**:

1. Generate `data-model.md` with entity definitions
2. Generate `contracts/cli-commands.yaml` with CLI contracts
3. Generate `quickstart.md` with user guide
4. Update agent context with new technologies

Execute these steps as part of the `/speckit.plan` workflow.
