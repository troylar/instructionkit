"""Integration tests for package installation workflow."""

from pathlib import Path

import pytest

from aiconfigkit.core.models import (
    AIToolType,
    ComponentType,
    InstallationScope,
    InstallationStatus,
)
from aiconfigkit.storage.package_tracker import PackageTracker


@pytest.fixture
def sample_package_dir(tmp_path: Path) -> Path:
    """Create a sample package for testing."""
    package_dir = tmp_path / "test-package"
    package_dir.mkdir()

    # Create manifest
    manifest_content = """name: test-package
version: 1.0.0
description: Test package for integration testing
author: Test Author
license: MIT
namespace: test/repo

components:
  instructions:
    - name: python-style
      file: instructions/python-style.md
      description: Python style guide
      tags: [python, style]

  mcp_servers:
    - name: filesystem
      file: mcp/filesystem.json
      description: Filesystem MCP server
      credentials:
        - name: BASE_PATH
          description: Base path for filesystem access
          required: true

  hooks:
    - name: pre-commit
      file: hooks/pre-commit.sh
      description: Pre-commit formatting hook
      hook_type: pre-commit

  commands:
    - name: format
      file: commands/format.sh
      description: Format code command
      command_type: shell

  resources:
    - name: config
      file: resources/config.json
      description: Configuration file
      checksum: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 100
"""
    (package_dir / "ai-config-kit-package.yaml").write_text(manifest_content)

    # Create instruction file
    (package_dir / "instructions").mkdir()
    (package_dir / "instructions" / "python-style.md").write_text("# Python Style Guide\n\nFollow PEP 8 conventions.")

    # Create MCP config
    (package_dir / "mcp").mkdir()
    (package_dir / "mcp" / "filesystem.json").write_text(
        '{"mcpServers": {"filesystem": {"command": "mcp-server-filesystem"}}}'
    )

    # Create hook
    (package_dir / "hooks").mkdir()
    (package_dir / "hooks" / "pre-commit.sh").write_text("#!/bin/bash\nblack .")

    # Create command
    (package_dir / "commands").mkdir()
    (package_dir / "commands" / "format.sh").write_text("#!/bin/bash\nblack .")

    # Create resource
    (package_dir / "resources").mkdir()
    (package_dir / "resources" / "config.json").write_text("{}")

    return package_dir


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Create a temporary project root directory."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Initialize git repo to mark as project root
    (project_dir / ".git").mkdir()

    return project_dir


class TestPackageInstall:
    """Test package installation workflow."""

    def test_install_package_with_all_components(self, sample_package_dir: Path, project_root: Path) -> None:
        """
        Test installing a package with all component types.

        Verifies that:
        - All compatible components are installed to correct IDE locations
        - Installation is tracked in packages.json
        - Installed files have correct content
        - Installation status is COMPLETE
        """
        from aiconfigkit.cli.package_install import install_package

        # Install package for Claude Code IDE (supports all components)
        result = install_package(
            package_path=sample_package_dir,
            project_root=project_root,
            target_ide=AIToolType.CLAUDE,
            scope=InstallationScope.PROJECT,
        )

        # Verify installation succeeded
        assert result.success is True
        assert result.status == InstallationStatus.COMPLETE
        assert result.installed_count == 5  # All 5 components
        assert result.skipped_count == 0
        assert result.failed_count == 0

        # Verify instruction installed
        instruction_file = project_root / ".claude" / "rules" / "python-style.md"
        assert instruction_file.exists()
        assert "PEP 8" in instruction_file.read_text()

        # Verify MCP config installed (needs processing)
        # MCP goes to global config, so just verify it was processed
        assert result.components_installed[ComponentType.MCP_SERVER] == 1

        # Verify hook installed
        hook_file = project_root / ".claude" / "hooks" / "pre-commit.sh"
        assert hook_file.exists()
        assert "black" in hook_file.read_text()

        # Verify command installed
        command_file = project_root / ".claude" / "commands" / "format.sh"
        assert command_file.exists()

        # Verify resource installed
        resource_file = project_root / "resources" / "config.json"
        assert resource_file.exists()

        # Verify tracking
        tracker = PackageTracker(project_root / ".ai-config-kit" / "packages.json")
        record = tracker.get_package("test-package", InstallationScope.PROJECT)

        assert record is not None
        assert record.package_name == "test-package"
        assert record.version == "1.0.0"
        assert record.status == InstallationStatus.COMPLETE
        assert len(record.components) == 5

    def test_install_package_ide_filtering(self, sample_package_dir: Path, project_root: Path) -> None:
        """
        Test that unsupported components are skipped based on IDE capabilities.

        Verifies that:
        - Only components supported by target IDE are installed
        - Unsupported components are counted as skipped
        - Installation status reflects partial installation if some skipped
        """
        from aiconfigkit.cli.package_install import install_package

        # Install for Cursor (only supports instructions and resources)
        result = install_package(
            package_path=sample_package_dir,
            project_root=project_root,
            target_ide=AIToolType.CURSOR,
            scope=InstallationScope.PROJECT,
        )

        # Verify partial installation
        assert result.success is True
        assert result.status == InstallationStatus.PARTIAL
        assert result.installed_count == 2  # Only instruction + resource
        assert result.skipped_count == 3  # MCP, hook, command skipped
        assert result.failed_count == 0

        # Verify instruction installed
        instruction_file = project_root / ".cursor" / "rules" / "python-style.mdc"
        assert instruction_file.exists()

        # Verify resource installed
        resource_file = project_root / "resources" / "config.json"
        assert resource_file.exists()

        # Verify unsupported components NOT installed
        assert not (project_root / ".cursor" / "hooks").exists()
        assert not (project_root / ".cursor" / "commands").exists()

        # Verify tracking shows partial installation
        tracker = PackageTracker(project_root / ".ai-config-kit" / "packages.json")
        record = tracker.get_package("test-package", InstallationScope.PROJECT)

        assert record is not None
        assert record.status == InstallationStatus.PARTIAL
        assert len(record.components) == 2  # Only installed components tracked

    def test_install_package_already_exists(self, sample_package_dir: Path, project_root: Path) -> None:
        """
        Test reinstalling a package that's already installed.

        Verifies that:
        - Existing installation is detected
        - User is prompted or auto-handled based on conflict strategy
        - Installation record is updated (not duplicated)
        - Updated timestamp reflects reinstall
        """
        from aiconfigkit.cli.package_install import install_package
        from aiconfigkit.core.models import ConflictResolution

        # First installation
        result1 = install_package(
            package_path=sample_package_dir,
            project_root=project_root,
            target_ide=AIToolType.CLAUDE,
            scope=InstallationScope.PROJECT,
        )
        assert result1.success is True

        # Get original timestamp
        tracker = PackageTracker(project_root / ".ai-config-kit" / "packages.json")
        record1 = tracker.get_package("test-package", InstallationScope.PROJECT)
        original_time = record1.updated_at

        # Second installation (should detect existing)
        result2 = install_package(
            package_path=sample_package_dir,
            project_root=project_root,
            target_ide=AIToolType.CLAUDE,
            scope=InstallationScope.PROJECT,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        # Verify reinstall succeeded
        assert result2.success is True
        assert result2.is_reinstall is True

        # Verify tracking updated (not duplicated)
        assert tracker.get_package_count() == 1
        record2 = tracker.get_package("test-package", InstallationScope.PROJECT)
        assert record2.updated_at > original_time

    def test_install_package_with_conflict_skip(self, sample_package_dir: Path, project_root: Path) -> None:
        """Test that SKIP conflict resolution preserves existing files."""
        from aiconfigkit.cli.package_install import install_package
        from aiconfigkit.core.models import ConflictResolution

        # Create pre-existing file with different content
        rules_dir = project_root / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        existing_file = rules_dir / "python-style.md"
        existing_file.write_text("# Original Content")

        # Install with SKIP resolution
        result = install_package(
            package_path=sample_package_dir,
            project_root=project_root,
            target_ide=AIToolType.CLAUDE,
            scope=InstallationScope.PROJECT,
            conflict_resolution=ConflictResolution.SKIP,
        )

        # Verify installation completed but instruction was skipped
        assert result.success is True
        assert result.skipped_count >= 1

        # Verify original file unchanged
        assert existing_file.read_text() == "# Original Content"

    def test_install_package_with_conflict_rename(self, sample_package_dir: Path, project_root: Path) -> None:
        """Test that RENAME conflict resolution creates numbered copies."""
        from aiconfigkit.cli.package_install import install_package
        from aiconfigkit.core.models import ConflictResolution

        # Create pre-existing file
        rules_dir = project_root / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        existing_file = rules_dir / "python-style.md"
        existing_file.write_text("# Original Content")

        # Install with RENAME resolution
        install_package(
            package_path=sample_package_dir,
            project_root=project_root,
            target_ide=AIToolType.CLAUDE,
            scope=InstallationScope.PROJECT,
            conflict_resolution=ConflictResolution.RENAME,
        )

        # Verify both files exist
        assert existing_file.exists()
        assert existing_file.read_text() == "# Original Content"

        # New file should have number suffix
        renamed_file = rules_dir / "python-style-1.md"
        assert renamed_file.exists()
        assert "PEP 8" in renamed_file.read_text()

    def test_install_package_missing_manifest_fails(self, tmp_path: Path, project_root: Path) -> None:
        """Test that installing package without manifest fails gracefully."""
        from aiconfigkit.cli.package_install import install_package

        # Create package without manifest
        invalid_package = tmp_path / "invalid-package"
        invalid_package.mkdir()

        # Should return failure result (not raise exception)
        result = install_package(
            package_path=invalid_package,
            project_root=project_root,
            target_ide=AIToolType.CLAUDE,
            scope=InstallationScope.PROJECT,
        )

        assert result.success is False
        assert result.status == InstallationStatus.FAILED
        assert "Manifest not found" in result.error_message or "not found" in result.error_message

    def test_install_package_invalid_manifest_fails(self, tmp_path: Path, project_root: Path) -> None:
        """Test that invalid manifest causes installation to fail."""
        from aiconfigkit.cli.package_install import install_package

        # Create package with invalid manifest (missing required fields)
        invalid_package = tmp_path / "invalid-package"
        invalid_package.mkdir()
        (invalid_package / "ai-config-kit-package.yaml").write_text("name: test\n# Missing version, description, etc.")

        # Should return failure result (validation errors)
        result = install_package(
            package_path=invalid_package,
            project_root=project_root,
            target_ide=AIToolType.CLAUDE,
            scope=InstallationScope.PROJECT,
        )

        assert result.success is False
        assert result.status == InstallationStatus.FAILED
        assert "missing required field" in result.error_message.lower() or "validation" in result.error_message.lower()

    def test_list_installed_packages(self, sample_package_dir: Path, project_root: Path) -> None:
        """Test listing installed packages."""
        from aiconfigkit.cli.package_install import install_package

        # Install a package first
        result = install_package(
            package_path=sample_package_dir,
            project_root=project_root,
            target_ide=AIToolType.CLAUDE,
            scope=InstallationScope.PROJECT,
        )
        assert result.success is True

        # Now list packages
        tracker = PackageTracker(project_root / ".ai-config-kit" / "packages.json")
        packages = tracker.get_installed_packages()

        assert len(packages) == 1
        assert packages[0].package_name == "test-package"
        assert packages[0].version == "1.0.0"
        assert packages[0].status == InstallationStatus.COMPLETE
        assert len(packages[0].components) == 5

    def test_uninstall_package(self, sample_package_dir: Path, project_root: Path) -> None:
        """Test uninstalling a package."""
        from aiconfigkit.cli.package_install import install_package

        # Install a package first
        result = install_package(
            package_path=sample_package_dir,
            project_root=project_root,
            target_ide=AIToolType.CLAUDE,
            scope=InstallationScope.PROJECT,
        )
        assert result.success is True

        # Verify files exist
        instruction_file = project_root / ".claude" / "rules" / "python-style.md"
        assert instruction_file.exists()

        # Uninstall
        tracker = PackageTracker(project_root / ".ai-config-kit" / "packages.json")
        package = tracker.get_package("test-package", InstallationScope.PROJECT)
        assert package is not None

        # Remove files
        for component in package.components:
            file_path = project_root / component.installed_path
            if file_path.exists():
                file_path.unlink()

        # Remove from tracker
        success = tracker.remove_package("test-package", InstallationScope.PROJECT)
        assert success is True

        # Verify removed
        assert tracker.get_package("test-package", InstallationScope.PROJECT) is None
        assert not instruction_file.exists()
