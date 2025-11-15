# Quickstart: Configuration Package System

**Feature**: 004-config-package
**Audience**: Developers implementing this feature
**Status**: Planning phase

## For Feature Developers

This quickstart helps you implement the Configuration Package System. Follow these steps to get started with development.

---

## Prerequisites

- AI Config Kit repository cloned
- Python 3.10+ installed
- Development environment set up (`invoke dev-setup`)
- Feature branch created: `004-config-package`
- GitHub issue #24 created

---

## Phase-by-Phase Implementation

### Phase 1: Core Data Models

**Goal**: Define package-related data structures

**Files to create**:
```python
# ai-config-kit/core/models.py (extend existing)
@dataclass
class Package:
    name: str
    version: str
    description: str
    author: str
    license: str
    namespace: str
    components: PackageComponents

@dataclass
class PackageComponents:
    instructions: list[InstructionComponent]
    mcp_servers: list[MCPServerComponent]
    hooks: list[HookComponent]
    commands: list[CommandComponent]
    resources: list[ResourceComponent]
```

**Tests first**:
```bash
# Create test file
touch tests/unit/test_package_models.py

# Write tests for validation
pytest tests/unit/test_package_models.py -v
```

**Run validation**:
```bash
invoke typecheck  # Must pass
invoke test-unit  # Models should validate correctly
```

---

### Phase 2: Package Manifest Parser

**Goal**: Parse `ai-config-kit-package.yaml` files

**File to create**:
```python
# ai-config-kit/core/package_manifest.py
class PackageManifestParser:
    def parse(self, manifest_path: Path) -> Package:
        """Parse package manifest YAML file."""

    def validate(self, package: Package) -> list[ValidationError]:
        """Validate package structure and references."""
```

**Tests**:
```python
# tests/unit/test_package_manifest.py
def test_parse_valid_manifest():
    manifest = create_test_manifest()
    package = parser.parse(manifest)
    assert package.name == "test-package"

def test_validate_missing_files():
    package = create_package_with_missing_files()
    errors = parser.validate(package)
    assert len(errors) > 0
```

**Integration point**: Extends existing `core/repository.py` patterns

---

### Phase 3: Semantic Versioning

**Goal**: Version comparison and management

**File to create**:
```python
# ai-config-kit/core/version.py
from packaging.version import Version

class VersionManager:
    def parse(self, version_str: str) -> Version:
        """Parse semantic version string."""

    def compare(self, v1: str, v2: str) -> int:
        """Compare two versions: -1, 0, or 1."""

    def get_available_versions(self, repo_url: str) -> list[Version]:
        """Query Git tags for available versions."""
```

**Tests**:
```python
def test_version_comparison():
    assert version_manager.compare("1.0.0", "1.0.1") == -1
    assert version_manager.compare("2.0.0", "1.9.9") == 1

def test_get_versions_from_git():
    versions = version_manager.get_available_versions("https://...")
    assert len(versions) > 0
```

---

### Phase 4: IDE Capability Registry

**Goal**: Define what each IDE supports

**File to create**:
```python
# ai-config-kit/ai_tools/capability_registry.py
@dataclass
class IDECapability:
    name: str
    supports_instructions: bool
    instruction_extension: str
    instruction_path: str
    supports_mcp: bool
    # ... other fields

CAPABILITY_REGISTRY = {
    "cursor": IDECapability(...),
    "claude_code": IDECapability(...),
    "windsurf": IDECapability(...),
    "copilot": IDECapability(...)
}
```

**Tests**:
```python
def test_cursor_capabilities():
    cursor = CAPABILITY_REGISTRY["cursor"]
    assert cursor.supports_instructions
    assert cursor.instruction_extension == ".mdc"
    assert not cursor.supports_mcp
```

---

### Phase 5: Component Translator

**Goal**: Translate IDE-agnostic components to IDE-specific formats

**File to create**:
```python
# ai-config-kit/ai_tools/translator.py
class ComponentTranslator(ABC):
    @abstractmethod
    def translate_instruction(self, inst: Instruction) -> TranslatedComponent:
        pass

class CursorTranslator(ComponentTranslator):
    def translate_instruction(self, inst: Instruction) -> TranslatedComponent:
        return TranslatedComponent(
            path=f".cursor/rules/{inst.name}.mdc",
            content=inst.content,
            extension=".mdc"
        )
```

**Tests**:
```python
def test_cursor_instruction_translation():
    translator = CursorTranslator()
    instruction = create_test_instruction()
    result = translator.translate_instruction(instruction)
    assert result.path == ".cursor/rules/test.mdc"
    assert result.extension == ".mdc"
```

---

### Phase 6: Package Tracker

**Goal**: Track installed packages in projects

**File to create**:
```python
# ai-config-kit/storage/package_tracker.py
class PackageTracker:
    def __init__(self, project_root: Path):
        self.tracker_path = project_root / ".instructionkit" / "packages.json"

    def record_installation(self, package: Package, components: list[InstalledComponent]):
        """Record package installation."""

    def get_installed_packages(self) -> list[PackageInstallationRecord]:
        """Get all installed packages."""

    def update_package(self, package_name: str, new_version: str):
        """Update package version."""
```

**Tests**:
```python
def test_record_installation(temp_dir):
    tracker = PackageTracker(temp_dir)
    package = create_test_package()
    tracker.record_installation(package, [])

    installed = tracker.get_installed_packages()
    assert len(installed) == 1
    assert installed[0].package_name == package.name
```

---

### Phase 7: Main Registry

**Goal**: Cross-project installation tracking

**File to create**:
```python
# ai-config-kit/storage/registry.py
class MainRegistry:
    def __init__(self):
        self.registry_path = Path.home() / ".instructionkit" / "registry.json"

    def register_project(self, project_path: Path, packages: list[Package]):
        """Register project with installed packages."""

    def scan_projects(self, search_path: Path, max_depth: int = 3) -> list[ProjectRegistration]:
        """Scan for projects and rebuild registry."""

    def get_projects_using_package(self, package_name: str) -> list[ProjectRegistration]:
        """Find projects using a specific package."""
```

**Tests**:
```python
def test_register_project(temp_dir):
    registry = MainRegistry()
    project = temp_dir / "test-project"
    project.mkdir()

    registry.register_project(project, [])
    projects = registry.get_all_projects()
    assert len(projects) == 1
```

---

### Phase 8: Secret Detector

**Goal**: Detect and template secrets during package creation

**File to create**:
```python
# ai-config-kit/core/secret_detector.py
class SecretDetector:
    def detect(self, var_name: str, value: str) -> SecretConfidence:
        """Detect if value is likely a secret."""

    def template_value(self, var_name: str, value: str) -> str:
        """Convert value to template placeholder."""
```

**Tests**:
```python
def test_detect_api_key():
    detector = SecretDetector()
    result = detector.detect("API_KEY", "sk-abc123...")
    assert result == SecretConfidence.HIGH

def test_detect_safe_value():
    detector = SecretDetector()
    result = detector.detect("DEBUG", "true")
    assert result == SecretConfidence.SAFE
```

---

### Phase 9: Package Installation

**Goal**: Install packages with all components

**File to create**:
```python
# ai-config-kit/cli/package_install.py
@app.command()
def install(
    package_spec: str,
    project: Optional[Path] = None,
    interactive: bool = False,
    conflict: ConflictResolution = ConflictResolution.PROMPT
):
    """Install a package."""
    # 1. Parse package spec
    # 2. Load package manifest
    # 3. Detect IDE
    # 4. Translate components
    # 5. Install components
    # 6. Track installation
    # 7. Update registry
```

**Integration test**:
```python
# tests/integration/test_package_install.py
def test_install_package_end_to_end(temp_dir, mock_library):
    # Create mock package in library
    # Run install command
    # Verify components installed
    # Verify tracking updated
```

---

### Phase 10: Package Creation

**Goal**: Create packages from current project

**File to create**:
```python
# ai-config-kit/cli/package_create.py
@app.command()
def create(
    name: Optional[str] = None,
    interactive: bool = True,
    scrub_secrets: bool = True
):
    """Create a package from current project."""
    # 1. Scan project for components
    # 2. Interactive selection (if enabled)
    # 3. Detect secrets
    # 4. Generate manifest
    # 5. Copy files
    # 6. Generate README
```

**Integration test**:
```python
def test_create_package(temp_project):
    # Set up project with components
    # Run create command
    # Verify manifest generated
    # Verify files copied
```

---

### Phase 11: Package Update

**Goal**: Update installed packages

**File to create**:
```python
# ai-config-kit/cli/package_update.py
@app.command()
def update(
    package_spec: Optional[str] = None,
    check_only: bool = False,
    to_version: Optional[str] = None
):
    """Update packages."""
    # 1. Get installed packages
    # 2. Check for updates
    # 3. Detect conflicts
    # 4. Apply updates
    # 5. Update tracking
```

---

### Phase 12: TUI Components

**Goal**: Interactive browsing and selection

**Files to create**:
```python
# ai-config-kit/tui/package_browser.py
class PackageBrowser(App):
    """Browse and select packages to install."""

# ai-config-kit/tui/package_creator.py
class PackageCreator(App):
    """Interactive package creation wizard."""
```

---

## Development Workflow

### 1. Setup Feature Branch

```bash
git checkout -b 004-config-package
```

### 2. Run Tests Continuously

```bash
# Watch mode (if available)
pytest -f

# Or run manually after each change
invoke test-unit
```

### 3. Maintain Type Safety

```bash
# Run before each commit
invoke typecheck
```

### 4. Code Quality

```bash
# Format code
invoke format

# Lint
invoke lint --fix

# Full quality check
invoke quality
```

### 5. Integration Testing

```bash
# Create test project
mkdir /tmp/test-aiconfig-project
cd /tmp/test-aiconfig-project

# Test package creation
aiconfig package create --name test --no-interactive

# Test package installation
aiconfig package install ./package-test
```

---

## Testing Strategy

### Unit Tests (Fast, Isolated)

```bash
tests/unit/
├── test_package_models.py        # Data model validation
├── test_package_manifest.py      # Manifest parsing
├── test_version.py                # Semver comparison
├── test_secret_detector.py       # Secret detection
├── test_capability_registry.py   # IDE capabilities
└── test_translator.py             # Component translation
```

Run: `invoke test-unit`

### Integration Tests (File I/O, Git)

```bash
tests/integration/
├── test_package_install.py       # End-to-end install
├── test_package_create.py        # Package creation
├── test_package_update.py        # Update workflow
└── test_registry.py               # Registry operations
```

Run: `invoke test-integration`

### Manual Testing Checklist

- [ ] Install package from Git repository
- [ ] Install package with MCP servers (credential prompting)
- [ ] Create package from project
- [ ] Update package with conflicts
- [ ] Scan projects to rebuild registry
- [ ] List packages (installed and available)
- [ ] Uninstall package
- [ ] Test with each IDE (Cursor, Claude Code, Windsurf, Copilot)

---

## Common Patterns

### Working with Paths

```python
from pathlib import Path

# Always use Path objects
project_root = Path.cwd()
instructionkit_dir = project_root / ".instructionkit"

# Relative paths for tracking
rel_path = installed_path.relative_to(project_root)
```

### Error Handling

```python
from rich.console import Console

console = Console()

try:
    install_package(package)
except PackageNotFoundError as e:
    console.print(f"[red]Error:[/red] {e}")
    console.print(f"[yellow]Suggestion:[/yellow] Run 'aiconfig download {package}'")
    sys.exit(4)
```

### Progress Indicators

```python
from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("[cyan]Installing...", total=len(components))
    for component in components:
        install_component(component)
        progress.update(task, advance=1)
```

### Checksums

```python
import hashlib

def compute_checksum(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"
```

---

## Debugging Tips

### Enable Debug Logging

```bash
# Set environment variable
export LOGLEVEL=DEBUG

# Or use flag
aiconfig package install --debug acme/productivity
```

### Inspect JSON Files

```bash
# Pretty-print tracker
cat .instructionkit/packages.json | python -m json.tool

# Pretty-print registry
cat ~/.instructionkit/registry.json | python -m json.tool
```

### Test in Isolation

```bash
# Create clean test environment
mkdir /tmp/clean-test
cd /tmp/clean-test
rm -rf ~/.instructionkit/library/test-*

# Run specific test
pytest tests/integration/test_package_install.py::test_install_with_mcp -v -s
```

---

## Dependencies on Existing Code

### Reuse These Modules

- `ai-config-kit/storage/library.py` - Library management
- `ai-config-kit/storage/tracker.py` - Installation tracking patterns
- `ai-config-kit/core/git_operations.py` - Git clone/pull
- `ai-config-kit/core/conflict_resolution.py` - Conflict handling
- `ai-config-kit/ai_tools/detector.py` - IDE detection
- `ai-config-kit/tui/installer.py` - TUI patterns
- `ai-config-kit/core/checksum.py` - File checksums

### Extend These Modules

- `ai-config-kit/core/models.py` - Add package models
- `ai-config-kit/ai_tools/base.py` - Add capability declarations

---

## Commit Convention

All commits reference issue #24:

```bash
git commit -m "feat(core): add package data models (#24)"
git commit -m "feat(storage): implement package tracker (#24)"
git commit -m "feat(cli): add package install command (#24)"
git commit -m "test(integration): add package install tests (#24)"
```

---

## Ready for Implementation

Once you've read this quickstart:

1. Start with Phase 1 (Core Data Models)
2. Follow TDD: write tests first
3. Run `invoke quality` before committing
4. Reference issue #24 in all commits
5. Create PR when phases 1-6 are complete

For detailed task breakdown, run:
```bash
/speckit.tasks
```

This will generate `tasks.md` with specific, actionable implementation tasks.
