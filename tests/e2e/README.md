## End-to-End Tests for Package Management

Comprehensive end-to-end tests covering every aspect of the package management system.

## Test Coverage

### test_basic_workflows.py (470 lines)
**Basic package operations**
- Simple package installation
- Complete packages with all component types
- Installing to different project locations
- Listing installed packages
- Uninstalling packages
- Reinstallation scenarios

### test_version_management.py (439 lines)
**Version updates and management**
- Patch, minor, and major version updates
- Version downgrades
- Git tags for specific versions
- Installing from specific commit hashes
- Pre-release versions (alpha, beta, RC)
- Multiple versions across different projects

### test_git_operations.py (495 lines)
**Git repository interactions**
- Installing from local git repositories
- Installing from cloned repositories
- Git pull and package updates
- Working with git branches (main, feature)
- Installing from git tags
- Installing from specific commits
- Git history manipulation
- Repositories with no commits

### test_conflict_resolution.py (602 lines)
**Conflict resolution strategies**
- SKIP strategy (preserves user modifications)
- OVERWRITE strategy (replaces everything)
- RENAME strategy (creates numbered copies)
- Partial conflicts (some files exist, some don't)
- Conflicts across all component types
- Changing strategies between installs
- Permission preservation

### test_multi_package.py (626 lines)
**Multiple package scenarios**
- Installing multiple packages to same project
- Packages with overlapping namespaces
- Updating one package without affecting others
- Uninstalling selective packages
- Packages with conflicting component names
- Package dependencies and layering
- Company + team + personal package workflows
- Installation order effects
- Updating all vs selective packages

### test_comprehensive.py (903 lines)
**IDE compatibility, edge cases, errors, and workflows**

**IDE Compatibility:**
- Claude Code (all components)
- Cursor (instructions + resources, .mdc format)
- Windsurf (instructions + resources)
- GitHub Copilot (instructions only)
- Same package across different IDEs

**Edge Cases:**
- Very long package/component names
- Packages with 50+ components
- Special characters and Unicode in content
- Empty packages
- Deeply nested directory structures
- Binary file resources

**Error Handling:**
- Missing manifest files
- Invalid YAML syntax
- Missing required manifest fields
- Non-existent component files
- Invalid version formats
- Installing to non-existent directories

**Real-World Workflows:**
- New developer onboarding
- Team synchronization
- Multi-project selective packages
- Migration from manual to package management
- Cleanup after version iterations

## Running Tests

### Run All E2E Tests
```bash
pytest tests/e2e/ -v
```

### Run Specific Test File
```bash
pytest tests/e2e/test_basic_workflows.py -v
pytest tests/e2e/test_version_management.py -v
pytest tests/e2e/test_git_operations.py -v
pytest tests/e2e/test_conflict_resolution.py -v
pytest tests/e2e/test_multi_package.py -v
pytest tests/e2e/test_comprehensive.py -v
```

### Run Specific Test Class
```bash
pytest tests/e2e/test_basic_workflows.py::TestBasicInstallation -v
pytest tests/e2e/test_version_management.py::TestVersionUpdates -v
pytest tests/e2e/test_git_operations.py::TestGitBranches -v
```

### Run Specific Test
```bash
pytest tests/e2e/test_basic_workflows.py::TestBasicInstallation::test_install_simple_package_from_directory -v
```

### Run with Coverage
```bash
pytest tests/e2e/ --cov=aiconfigkit.cli.package_install --cov=aiconfigkit.storage.package_tracker --cov-report=html
```

### Run in Parallel (faster)
```bash
pytest tests/e2e/ -n auto
```

## Test Organization

### Fixtures (conftest.py)
- `git_repo(name, files)` - Creates a git repository
- `package_builder(...)` - Builds complete packages with all component types
- `test_project` - Creates a test project directory with git initialized

### Test Structure
Each test:
1. Sets up package(s) using fixtures
2. Performs installation/update/uninstall operations
3. Verifies files exist in correct locations
4. Verifies package tracking is correct
5. Checks file contents where relevant

## Key Scenarios Tested

### Installation
- ✅ Basic installation from directory
- ✅ Installation from local git repo
- ✅ Installation with all component types
- ✅ Installation to multiple projects
- ✅ Installation with different IDEs

### Updates
- ✅ Patch version updates (1.0.0 → 1.0.1)
- ✅ Minor version updates (1.0.0 → 1.1.0)
- ✅ Major version updates (1.0.0 → 2.0.0)
- ✅ Version downgrades
- ✅ Installing from git tags
- ✅ Installing from specific commits

### Conflicts
- ✅ SKIP preserves user modifications
- ✅ OVERWRITE replaces all files
- ✅ RENAME creates numbered copies
- ✅ Partial conflicts (some new, some existing)
- ✅ Conflicts between different packages

### Git Operations
- ✅ Cloning and installing
- ✅ Pulling updates and reinstalling
- ✅ Switching branches
- ✅ Checking out tags
- ✅ Installing from specific commits
- ✅ Git history changes

### Multi-Package
- ✅ Multiple packages in one project
- ✅ Overlapping component names
- ✅ Selective updates
- ✅ Selective uninstallation
- ✅ Package layering (company/team/personal)

### IDE Compatibility
- ✅ Claude Code (all components)
- ✅ Cursor (.mdc format, filtered components)
- ✅ Windsurf (filtered components)
- ✅ GitHub Copilot (instructions only)
- ✅ Same package across different IDEs

### Edge Cases
- ✅ Long names
- ✅ Many components (50+)
- ✅ Special characters and Unicode
- ✅ Nested directories
- ✅ Binary files

### Error Handling
- ✅ Missing manifest
- ✅ Invalid YAML
- ✅ Missing required fields
- ✅ Non-existent files
- ✅ Invalid versions

### Real Workflows
- ✅ New developer onboarding
- ✅ Team synchronization
- ✅ Multi-project setups
- ✅ Migration workflows
- ✅ Version cleanup

## Test Statistics

- **Total Lines**: 3,535+
- **Total Tests**: 100+
- **Test Files**: 6
- **Test Classes**: 30+
- **Coverage**: All core package management functionality

## Dependencies

These tests use:
- `pytest` - Test framework
- `subprocess` - Git operations
- `pathlib` - File system operations
- Package fixtures from `conftest.py`

## Notes

- All tests are isolated and use temporary directories
- Git operations use real git commands but in isolated repos
- Tests clean up after themselves
- Tests can run in parallel with `pytest -n auto`
- No external network dependencies (all local git repos)

## Adding New Tests

When adding new tests:

1. **Choose the right file**:
   - Basic operations → `test_basic_workflows.py`
   - Versions → `test_version_management.py`
   - Git → `test_git_operations.py`
   - Conflicts → `test_conflict_resolution.py`
   - Multiple packages → `test_multi_package.py`
   - Everything else → `test_comprehensive.py`

2. **Use fixtures**:
   ```python
   def test_my_scenario(package_builder, test_project):
       pkg = package_builder(
           name="my-pkg",
           version="1.0.0",
           instructions=[{"name": "guide", "content": "# Guide"}],
       )
       result = install_package(pkg, test_project, AIToolType.CLAUDE)
       assert result.success is True
   ```

3. **Verify thoroughly**:
   - File existence
   - File contents
   - Package tracking
   - Version numbers
   - Component counts

4. **Clean up if needed**:
   - Tests use `tmp_path` which cleans automatically
   - Explicitly clean only if reusing directories

## CI/CD Integration

These tests run in CI on:
- Push to main
- Pull requests
- Multiple Python versions (3.10-3.13)
- Multiple OS (Linux, macOS, Windows)

Expected runtime:
- Sequential: ~2-3 minutes
- Parallel (`-n auto`): ~30-45 seconds
