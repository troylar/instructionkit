"""E2E tests for basic package management workflows."""

from pathlib import Path

from aiconfigkit.cli.package_install import install_package
from aiconfigkit.core.models import AIToolType, ConflictResolution, InstallationScope, InstallationStatus
from aiconfigkit.storage.package_tracker import PackageTracker


class TestBasicInstallation:
    """Test basic package installation workflows."""

    def test_install_simple_package_from_directory(self, package_builder, test_project: Path) -> None:
        """Test installing a simple package from a local directory."""
        # Create package
        pkg = package_builder(
            name="simple-pkg",
            version="1.0.0",
            instructions=[
                {"name": "style-guide", "description": "Style guidelines"},
            ],
        )

        # Install
        result = install_package(
            package_path=pkg,
            project_root=test_project,
            target_ide=AIToolType.CLAUDE,
        )

        # Verify
        assert result.success is True
        assert result.status == InstallationStatus.COMPLETE
        assert result.installed_count == 1
        assert result.skipped_count == 0

        # Verify files exist
        assert (test_project / ".claude/rules/style-guide.md").exists()

        # Verify tracking
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("simple-pkg", InstallationScope.PROJECT)
        assert pkg_record is not None
        assert pkg_record.version == "1.0.0"

    def test_install_complete_package_all_components(self, package_builder, test_project: Path) -> None:
        """Test installing a package with all component types."""
        pkg = package_builder(
            name="complete-pkg",
            version="1.0.0",
            instructions=[
                {"name": "style", "description": "Style guide"},
                {"name": "testing", "description": "Test guide"},
            ],
            mcp_servers=[
                {"name": "filesystem", "description": "FS access"},
            ],
            hooks=[
                {"name": "pre-commit", "description": "Pre-commit hook"},
            ],
            commands=[
                {"name": "test", "description": "Run tests"},
            ],
            resources=[
                {"name": ".gitignore", "description": "Git ignore file"},
            ],
        )

        result = install_package(
            package_path=pkg,
            project_root=test_project,
            target_ide=AIToolType.CLAUDE,
        )

        # Verify installation
        assert result.success is True
        assert result.status == InstallationStatus.COMPLETE
        assert result.installed_count == 6

        # Verify all files exist
        assert (test_project / ".claude/rules/style.md").exists()
        assert (test_project / ".claude/rules/testing.md").exists()
        assert (test_project / ".claude/mcp/filesystem.json").exists()
        assert (test_project / ".claude/hooks/pre-commit.sh").exists()
        assert (test_project / ".claude/commands/test.sh").exists()
        assert (test_project / ".gitignore").exists()

        # Verify hook is executable (Unix-only)
        import os

        if os.name != "nt":  # Skip permission check on Windows
            hook_path = test_project / ".claude/hooks/pre-commit.sh"
            assert hook_path.stat().st_mode & 0o111  # Has execute permission

    def test_install_to_different_project_locations(self, package_builder, tmp_path: Path) -> None:
        """Test installing to different project locations."""
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "description": "Guide"}],
        )

        # Create multiple projects
        project1 = tmp_path / "project1"
        project1.mkdir()
        project2 = tmp_path / "nested/project2"
        project2.mkdir(parents=True)

        # Install to both
        result1 = install_package(pkg, project1, AIToolType.CLAUDE)
        result2 = install_package(pkg, project2, AIToolType.CLAUDE)

        assert result1.success is True
        assert result2.success is True

        # Verify separate installations
        assert (project1 / ".claude/rules/guide.md").exists()
        assert (project2 / ".claude/rules/guide.md").exists()
        assert (project1 / ".ai-config-kit/packages.json").exists()
        assert (project2 / ".ai-config-kit/packages.json").exists()


class TestListPackages:
    """Test listing installed packages."""

    def test_list_empty_project(self, test_project: Path) -> None:
        """Test listing packages when none are installed."""
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        packages = tracker.get_installed_packages()

        assert len(packages) == 0

    def test_list_single_package(self, package_builder, test_project: Path) -> None:
        """Test listing a single installed package."""
        pkg = package_builder(
            name="my-package",
            version="1.0.0",
            instructions=[{"name": "guide", "description": "Guide"}],
        )

        install_package(pkg, test_project, AIToolType.CLAUDE)

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        packages = tracker.get_installed_packages()

        assert len(packages) == 1
        assert packages[0].package_name == "my-package"
        assert packages[0].version == "1.0.0"
        assert packages[0].status == InstallationStatus.COMPLETE

    def test_list_multiple_packages(self, package_builder, test_project: Path) -> None:
        """Test listing multiple installed packages."""
        pkg1 = package_builder(
            name="package-1",
            version="1.0.0",
            instructions=[{"name": "guide1", "description": "Guide 1"}],
        )
        pkg2 = package_builder(
            name="package-2",
            version="2.0.0",
            instructions=[{"name": "guide2", "description": "Guide 2"}],
        )

        install_package(pkg1, test_project, AIToolType.CLAUDE)
        install_package(pkg2, test_project, AIToolType.CLAUDE)

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        packages = tracker.get_installed_packages()

        assert len(packages) == 2
        package_names = {p.package_name for p in packages}
        assert package_names == {"package-1", "package-2"}


class TestUninstallPackages:
    """Test uninstalling packages."""

    def test_uninstall_removes_files(self, package_builder, test_project: Path) -> None:
        """Test that uninstalling removes all package files."""
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "description": "Guide"}],
            hooks=[{"name": "pre-commit", "description": "Hook"}],
        )

        # Install
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # Verify files exist
        guide_path = test_project / ".claude/rules/guide.md"
        hook_path = test_project / ".claude/hooks/pre-commit.sh"
        assert guide_path.exists()
        assert hook_path.exists()

        # Uninstall
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record is not None

        # Remove files
        for component in pkg_record.components:
            file_path = test_project / component.installed_path
            if file_path.exists():
                file_path.unlink()

        # Remove from tracker
        tracker.remove_package("test-pkg", InstallationScope.PROJECT)

        # Verify
        assert not guide_path.exists()
        assert not hook_path.exists()
        assert tracker.get_package("test-pkg", InstallationScope.PROJECT) is None

    def test_uninstall_does_not_affect_other_packages(self, package_builder, test_project: Path) -> None:
        """Test that uninstalling one package doesn't affect others."""
        pkg1 = package_builder(
            name="package-1",
            version="1.0.0",
            instructions=[{"name": "guide1", "description": "Guide 1"}],
        )
        pkg2 = package_builder(
            name="package-2",
            version="1.0.0",
            instructions=[{"name": "guide2", "description": "Guide 2"}],
        )

        # Install both
        install_package(pkg1, test_project, AIToolType.CLAUDE)
        install_package(pkg2, test_project, AIToolType.CLAUDE)

        # Uninstall package-1
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg1_record = tracker.get_package("package-1", InstallationScope.PROJECT)

        for component in pkg1_record.components:
            file_path = test_project / component.installed_path
            if file_path.exists():
                file_path.unlink()

        tracker.remove_package("package-1", InstallationScope.PROJECT)

        # Verify package-1 is gone but package-2 remains
        assert not (test_project / ".claude/rules/guide1.md").exists()
        assert (test_project / ".claude/rules/guide2.md").exists()
        assert tracker.get_package("package-1", InstallationScope.PROJECT) is None
        assert tracker.get_package("package-2", InstallationScope.PROJECT) is not None

    def test_uninstall_nonexistent_package(self, test_project: Path) -> None:
        """Test uninstalling a package that doesn't exist."""
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        result = tracker.remove_package("nonexistent", InstallationScope.PROJECT)

        assert result is False


class TestReinstallation:
    """Test reinstalling packages."""

    def test_reinstall_without_force_skips(self, package_builder, test_project: Path) -> None:
        """Test that reinstalling without force detects existing installation."""
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "description": "Guide"}],
        )

        # Install once
        result1 = install_package(pkg, test_project, AIToolType.CLAUDE)
        assert result1.success is True

        # Install again without force
        result2 = install_package(pkg, test_project, AIToolType.CLAUDE, force=False)

        # Should detect as reinstall
        assert result2.is_reinstall is True

    def test_reinstall_with_force_overwrites(self, package_builder, test_project: Path) -> None:
        """Test that force reinstall overwrites existing installation."""
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "description": "Guide"}],
        )

        # Install once
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # Modify installed file
        guide_path = test_project / ".claude/rules/guide.md"
        guide_path.write_text("# Modified content")

        # Force reinstall
        result = install_package(
            pkg,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        assert result.success is True

        # Verify content restored
        new_content = guide_path.read_text()
        assert new_content != "# Modified content"
        assert "guide" in new_content.lower()
