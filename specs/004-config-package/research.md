# Research: Configuration Package System

**Feature**: 004-config-package
**Date**: 2025-11-14
**Status**: Complete

## Research Questions

### 1. Package Manifest Format Design

**Question**: What's the optimal YAML structure for IDE-agnostic package manifests that can translate to multiple IDE formats?

**Decision**: Extend existing `ai-config-kit.yaml` format with package-specific fields

**Rationale**:
- Users already familiar with `ai-config-kit.yaml` for instruction repositories
- YAML parsing infrastructure (PyYAML) already in place
- Can reuse validation patterns from existing repository parsing
- Natural extension: instructions → packages (both are bundles of components)

**Structure**:
```yaml
name: package-name
version: 1.0.0
description: Package description
author: Author Name
license: MIT

components:
  instructions:
    - name: instruction-name
      file: instructions/file.md
      description: What it does
      tags: [tag1, tag2]

  mcp_servers:
    - name: server-name
      file: mcp/server-config.json
      description: Server description
      credentials:
        - name: API_KEY
          description: API key for service
          required: true

  hooks:
    - name: hook-name
      file: hooks/pre-commit.sh
      description: Hook description
      ide_support: [claude_code]  # Only Claude Code supports hooks

  commands:
    - name: command-name
      file: commands/my-command.sh
      description: Command description
      ide_support: [cursor, claude_code]

  resources:
    - name: resource-name
      file: resources/logo.png
      description: Brand logo
      checksum: sha256:...
```

**Alternatives Considered**:
- JSON format: Less human-readable, harder to edit manually
- TOML format: Less familiar to users, would require new dependency
- Custom DSL: Over-engineering, steep learning curve

---

### 2. IDE Capability Registry Architecture

**Question**: How should we model IDE capabilities to enable accurate component translation?

**Decision**: Code-based capability registry with declarative capability definitions per IDE

**Rationale**:
- Capabilities change with IDE versions but not frequently enough to warrant external config
- Type safety: Python dataclasses provide validation and IDE autocomplete
- Centralized: Single source of truth for what each IDE supports
- Extensible: Easy to add new IDEs without changing core logic

**Implementation Pattern**:
```python
@dataclass
class IDECapability:
    name: str
    supports_instructions: bool
    instruction_extension: str  # .md, .mdc, .instructions.md
    instruction_path: str  # .cursor/rules/, .claude/rules/
    supports_mcp: bool
    mcp_config_path: Optional[str]
    mcp_config_format: Optional[str]  # claude_desktop, windsurf
    supports_hooks: bool
    hook_path: Optional[str]
    supports_commands: bool
    command_path: Optional[str]
    command_type: Optional[str]  # slash, shell

CAPABILITY_REGISTRY = {
    "cursor": IDECapability(
        name="Cursor",
        supports_instructions=True,
        instruction_extension=".mdc",
        instruction_path=".cursor/rules/",
        supports_mcp=False,
        supports_hooks=False,
        supports_commands=True,
        command_path=".cursor/commands/",
        command_type="shell"
    ),
    "claude_code": IDECapability(...),
    "windsurf": IDECapability(...),
    "copilot": IDECapability(...)
}
```

**Alternatives Considered**:
- YAML config file: Harder to validate, no type safety, harder to test
- Plugin architecture: Over-engineering for 4 IDEs, adds complexity
- Runtime discovery: Unreliable, slower, harder to test

---

### 3. Secret Detection Strategy

**Question**: How to reliably detect secrets in environment variables and MCP configs during package creation?

**Decision**: Multi-heuristic approach with confidence scoring

**Rationale**:
- No single heuristic is 100% accurate
- Combining multiple signals improves detection
- Confidence levels allow user override for edge cases
- Better to template too much (safe) than leak secrets (dangerous)

**Heuristics** (in order of precedence):
1. **Keyword matching** (high confidence): Variable names containing `token`, `key`, `secret`, `password`, `auth`, `credential`, `api_key`
2. **Entropy analysis** (medium confidence): High-entropy strings (>4.5 bits/char) suggest random tokens
3. **Pattern matching** (high confidence): UUIDs, base64 strings, hex patterns
4. **Value type** (safe): Booleans, numbers, simple URLs → preserve
5. **User confirmation** (medium confidence): Prompt for borderline cases

**Implementation**:
```python
def detect_secret(var_name: str, value: str) -> SecretConfidence:
    # High confidence (auto-template)
    if keyword_match(var_name, SENSITIVE_KEYWORDS):
        return SecretConfidence.HIGH
    if pattern_match(value, TOKEN_PATTERNS):
        return SecretConfidence.HIGH

    # Medium confidence (prompt user)
    if entropy(value) > 4.5:
        return SecretConfidence.MEDIUM

    # Safe (preserve)
    if is_safe_value(value):
        return SecretConfidence.SAFE

    return SecretConfidence.MEDIUM  # Default to asking
```

**Alternatives Considered**:
- ML-based detection: Overkill, requires training data, adds dependency
- Manual annotation only: Error-prone, users will forget to mark secrets
- Whitelist approach: Doesn't scale, requires maintaining lists

---

### 4. Semantic Versioning and Update Detection

**Question**: How to implement version comparison and update detection that works with Git repositories?

**Decision**: Use Python's `packaging.version` module for semver comparison + Git tags for version tracking

**Rationale**:
- `packaging.version` is stdlib-like (pip dependency), battle-tested for semver
- Git tags are standard practice for version management
- Can query available versions via `git ls-remote --tags`
- Supports version constraints (e.g., >=1.0.0, <2.0.0) for future dependency resolution

**Implementation**:
```python
from packaging.version import Version, parse

def get_available_versions(repo_url: str) -> list[Version]:
    tags = git_ls_remote_tags(repo_url)
    versions = [parse(tag.strip('v')) for tag in tags if is_semver(tag)]
    return sorted(versions, reverse=True)

def has_update(installed: str, available: list[Version]) -> Optional[Version]:
    current = parse(installed)
    latest = available[0] if available else None
    return latest if latest and latest > current else None

def compare_versions(v1: str, v2: str) -> int:
    return parse(v1).__cmp__(parse(v2))  # -1, 0, or 1
```

**Alternatives Considered**:
- Manual version parsing: Reinventing the wheel, error-prone
- Custom version scheme: Diverges from industry standard
- No versioning: Can't track updates or rollback

---

### 5. Streaming File Downloads for Large Resources

**Question**: How to handle large resource files (>10MB) without loading entire file into memory?

**Decision**: Implement chunked file copying with progress reporting using `shutil.copyfileobj`

**Rationale**:
- Standard library solution (no new dependencies)
- Memory-efficient for files of any size
- Can integrate with Rich progress bars for UX
- Works for both local file copies and remote downloads (via urllib)

**Implementation**:
```python
def stream_copy_file(
    src: Union[str, IO],
    dst: str,
    chunk_size: int = 8192,
    progress_callback: Optional[Callable[[int], None]] = None
) -> None:
    """Copy file in chunks to avoid memory issues with large files."""
    with open(src, 'rb') if isinstance(src, str) else src as src_file:
        with open(dst, 'wb') as dst_file:
            while True:
                chunk = src_file.read(chunk_size)
                if not chunk:
                    break
                dst_file.write(chunk)
                if progress_callback:
                    progress_callback(len(chunk))
```

**Integration with progress**:
```python
from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("[cyan]Downloading...", total=file_size)
    stream_copy_file(
        src, dst,
        progress_callback=lambda n: progress.update(task, advance=n)
    )
```

**Alternatives Considered**:
- Load entire file: Fails for large files, OOM risk
- External download library (requests, httpx): Unnecessary dependency for local files
- Async I/O: Over-engineering, CLI is synchronous

---

### 6. Binary File Conflict Resolution

**Question**: How to handle conflicts for binary files where diff is not possible?

**Decision**: Metadata comparison + timestamp-based conflict resolution with both versions preserved

**Rationale**:
- Can't show textual diff for binaries (images, PDFs, fonts)
- File size, modification date, and checksum provide useful comparison data
- Preserving both versions lets user manually inspect/choose
- Timestamp suffix prevents data loss

**Conflict Resolution Flow**:
```python
def resolve_binary_conflict(
    existing_path: str,
    new_content: bytes,
    new_checksum: str
) -> ConflictResolution:
    existing_checksum = compute_checksum(existing_path)

    if existing_checksum == new_checksum:
        return ConflictResolution.SKIP  # Files identical

    # Show metadata comparison
    existing_stat = os.stat(existing_path)
    console.print(f"Existing: {existing_stat.st_size} bytes, modified {existing_stat.st_mtime}")
    console.print(f"New: {len(new_content)} bytes, checksum {new_checksum}")

    # Install new with timestamp, keep old
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    new_path = f"{existing_path}.{timestamp}"
    write_file(new_path, new_content)

    console.print(f"[yellow]Both versions preserved:[/yellow]")
    console.print(f"  Original: {existing_path}")
    console.print(f"  Updated:  {new_path}")

    return ConflictResolution.KEEP_BOTH
```

**Alternatives Considered**:
- Auto-overwrite: Data loss risk, user loses customizations
- Always skip: Can't get updates for binary resources
- Prompt for every binary: Annoying for users, can't provide helpful context

---

### 7. Registry Validation and Recovery

**Question**: How to handle registry corruption gracefully without losing installation data?

**Decision**: Layered validation with progressive recovery strategies

**Rationale**:
- Registry corruption can happen (disk issues, manual editing, partial writes)
- Project trackers are source of truth (more reliable, distributed)
- Graceful degradation better than hard failure
- Logging helps debugging without blocking users

**Recovery Strategy**:
```python
def load_registry() -> MainRegistry:
    try:
        # Step 1: Validate JSON structure
        data = json.load(registry_path)
        validate_schema(data)

        # Step 2: Validate individual entries
        valid_entries = []
        for entry in data['projects']:
            if is_valid_entry(entry):
                valid_entries.append(entry)
            else:
                log.warning(f"Removed invalid entry: {entry}")

        if len(valid_entries) < len(data['projects']):
            log.info("Registry repaired: removed invalid entries")
            save_registry({'projects': valid_entries})

        return MainRegistry(projects=valid_entries)

    except JSONDecodeError:
        log.error("Registry corrupted, rebuilding from project trackers")
        return rebuild_registry_from_projects()

    except Exception as e:
        log.error(f"Registry unrecoverable: {e}, using empty registry")
        return MainRegistry(projects=[])  # Degraded mode
```

**Alternatives Considered**:
- Fail hard on corruption: Blocks all operations, poor UX
- No validation: Corruption propagates, harder to debug
- Backup copies: Adds complexity, doesn't address root cause

---

### 8. Component Translation Architecture

**Question**: How to translate IDE-agnostic components to IDE-specific formats without tight coupling?

**Decision**: Translator interface with IDE-specific implementations + capability-based routing

**Rationale**:
- Open/closed principle: Easy to add new IDEs without modifying existing code
- Single responsibility: Each translator handles one IDE's quirks
- Testable: Can unit test each translator in isolation
- Capability-based: Skip unsupported components gracefully

**Architecture**:
```python
class ComponentTranslator(ABC):
    @abstractmethod
    def translate_instruction(self, instruction: Instruction) -> TranslatedComponent:
        pass

    @abstractmethod
    def translate_mcp_config(self, mcp: MCPServer) -> TranslatedComponent:
        pass

    @abstractmethod
    def translate_hook(self, hook: Hook) -> TranslatedComponent:
        pass

    @abstractmethod
    def translate_command(self, command: Command) -> TranslatedComponent:
        pass

class CursorTranslator(ComponentTranslator):
    def translate_instruction(self, instruction: Instruction) -> TranslatedComponent:
        return TranslatedComponent(
            path=f".cursor/rules/{instruction.name}.mdc",
            content=instruction.content,
            extension=".mdc"
        )

    def translate_mcp_config(self, mcp: MCPServer) -> TranslatedComponent:
        raise UnsupportedComponent("Cursor does not support MCP")

# Factory pattern for routing
def get_translator(ide: str) -> ComponentTranslator:
    return {
        "cursor": CursorTranslator(),
        "claude_code": ClaudeCodeTranslator(),
        "windsurf": WindsurfTranslator(),
        "copilot": CopilotTranslator()
    }[ide]
```

**Alternatives Considered**:
- Monolithic translation function with if/elif: Hard to maintain, violates SRP
- Configuration-based translation: Less type-safe, harder to express complex transformations
- No translation layer: Forces users to create IDE-specific packages (bad UX)

---

## Technology Stack Summary

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Manifest parsing | PyYAML | Already used, familiar format |
| Version comparison | packaging.version | Stdlib-quality, battle-tested |
| Secret detection | Custom heuristics | No good library, domain-specific |
| File streaming | shutil.copyfileobj | Stdlib, memory-efficient |
| Checksums | hashlib (SHA256) | Stdlib, secure, fast |
| Progress UI | Rich Progress | Already used in project |
| CLI | Typer | Already used in project |
| TUI | Textual | Already used in project |
| Testing | pytest | Already used in project |

---

## Open Questions for Implementation

None - all research complete. Ready for Phase 1 design.

---

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Python packaging.version docs](https://packaging.pypa.io/en/stable/version.html)
- [YAML specification](https://yaml.org/spec/1.2.2/)
- [Git ls-remote documentation](https://git-scm.com/docs/git-ls-remote)
- [Rich progress bars](https://rich.readthedocs.io/en/stable/progress.html)
