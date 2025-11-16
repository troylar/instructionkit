"""E2E tests for multiple package scenarios."""

from pathlib import Path

from aiconfigkit.cli.package_install import install_package
from aiconfigkit.core.models import AIToolType, ConflictResolution, InstallationScope
from aiconfigkit.storage.package_tracker import PackageTracker


class TestMultiplePackages:
    """Test installing and managing multiple packages."""

    def test_install_multiple_packages_same_project(self, package_builder, test_project: Path) -> None:
        """Test installing multiple packages to the same project."""
        # Create three different packages
        pkg1 = package_builder(
            name="python-pkg",
            version="1.0.0",
            instructions=[{"name": "python-style", "content": "# Python"}],
        )
        pkg2 = package_builder(
            name="django-pkg",
            version="1.0.0",
            instructions=[{"name": "django-models", "content": "# Django"}],
        )
        pkg3 = package_builder(
            name="testing-pkg",
            version="1.0.0",
            instructions=[{"name": "pytest-guide", "content": "# Testing"}],
        )

        # Install all three
        result1 = install_package(pkg1, test_project, AIToolType.CLAUDE)
        result2 = install_package(pkg2, test_project, AIToolType.CLAUDE)
        result3 = install_package(pkg3, test_project, AIToolType.CLAUDE)

        assert all([result1.success, result2.success, result3.success])

        # Verify all files exist
        assert (test_project / ".claude/rules/python-style.md").exists()
        assert (test_project / ".claude/rules/django-models.md").exists()
        assert (test_project / ".claude/rules/pytest-guide.md").exists()

        # Verify all tracked
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        packages = tracker.get_installed_packages()
        assert len(packages) == 3

        names = {p.package_name for p in packages}
        assert names == {"python-pkg", "django-pkg", "testing-pkg"}

    def test_packages_with_overlapping_namespaces(self, package_builder, test_project: Path) -> None:
        """Test packages from the same namespace but different names."""
        pkg1 = package_builder(
            name="base-pkg",
            version="1.0.0",
            instructions=[{"name": "base", "content": "# Base"}],
        )
        pkg2 = package_builder(
            name="advanced-pkg",
            version="1.0.0",
            instructions=[{"name": "advanced", "content": "# Advanced"}],
        )

        # Both have same namespace but different names
        # (package_builder sets namespace to test/{name})

        install_package(pkg1, test_project, AIToolType.CLAUDE)
        install_package(pkg2, test_project, AIToolType.CLAUDE)

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        packages = tracker.get_installed_packages()

        assert len(packages) == 2
        assert {p.package_name for p in packages} == {"base-pkg", "advanced-pkg"}

    def test_update_one_package_leaves_others_unchanged(self, package_builder, test_project: Path) -> None:
        """Test that updating one package doesn't affect others."""
        # Install two packages
        pkg1_v1 = package_builder(
            name="pkg1",
            version="1.0.0",
            instructions=[{"name": "guide1", "content": "# Pkg1 v1.0"}],
        )
        pkg2_v1 = package_builder(
            name="pkg2",
            version="1.0.0",
            instructions=[{"name": "guide2", "content": "# Pkg2 v1.0"}],
        )

        install_package(pkg1_v1, test_project, AIToolType.CLAUDE)
        install_package(pkg2_v1, test_project, AIToolType.CLAUDE)

        # Update pkg1
        pkg1_v2 = package_builder(
            name="pkg1",
            version="2.0.0",
            instructions=[{"name": "guide1", "content": "# Pkg1 v2.0"}],
        )

        install_package(
            pkg1_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        # Verify pkg1 updated
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg1_record = tracker.get_package("pkg1", InstallationScope.PROJECT)
        pkg2_record = tracker.get_package("pkg2", InstallationScope.PROJECT)

        assert pkg1_record.version == "2.0.0"
        assert pkg2_record.version == "1.0.0"  # Unchanged

        # Verify file contents
        assert "v2.0" in (test_project / ".claude/rules/guide1.md").read_text()
        assert "v1.0" in (test_project / ".claude/rules/guide2.md").read_text()

    def test_uninstall_one_package_leaves_others_installed(self, package_builder, test_project: Path) -> None:
        """Test that uninstalling one package doesn't affect others."""
        pkg1 = package_builder(
            name="pkg1",
            version="1.0.0",
            instructions=[{"name": "guide1", "content": "# Pkg1"}],
        )
        pkg2 = package_builder(
            name="pkg2",
            version="1.0.0",
            instructions=[{"name": "guide2", "content": "# Pkg2"}],
        )
        pkg3 = package_builder(
            name="pkg3",
            version="1.0.0",
            instructions=[{"name": "guide3", "content": "# Pkg3"}],
        )

        # Install all
        install_package(pkg1, test_project, AIToolType.CLAUDE)
        install_package(pkg2, test_project, AIToolType.CLAUDE)
        install_package(pkg3, test_project, AIToolType.CLAUDE)

        # Uninstall pkg2
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg2_record = tracker.get_package("pkg2", InstallationScope.PROJECT)

        for component in pkg2_record.components:
            file_path = test_project / component.installed_path
            if file_path.exists():
                file_path.unlink()

        tracker.remove_package("pkg2", InstallationScope.PROJECT)

        # Verify pkg1 and pkg3 still exist
        assert (test_project / ".claude/rules/guide1.md").exists()
        assert not (test_project / ".claude/rules/guide2.md").exists()
        assert (test_project / ".claude/rules/guide3.md").exists()

        packages = tracker.get_installed_packages()
        assert len(packages) == 2
        assert {p.package_name for p in packages} == {"pkg1", "pkg3"}


class TestPackageConflicts:
    """Test conflicts between different packages."""

    def test_packages_with_same_instruction_name(self, package_builder, test_project: Path) -> None:
        """Test two packages with instructions of the same name."""
        pkg1 = package_builder(
            name="pkg1",
            version="1.0.0",
            instructions=[{"name": "style-guide", "content": "# Pkg1 Style"}],
        )
        pkg2 = package_builder(
            name="pkg2",
            version="1.0.0",
            instructions=[{"name": "style-guide", "content": "# Pkg2 Style"}],
        )

        # Install pkg1
        result1 = install_package(pkg1, test_project, AIToolType.CLAUDE)
        assert result1.success is True

        # Install pkg2 with SKIP (preserves pkg1's file)
        result2 = install_package(
            pkg2,
            test_project,
            AIToolType.CLAUDE,
            conflict_resolution=ConflictResolution.SKIP,
        )

        assert result2.success is True
        assert result2.skipped_count > 0

        # Verify pkg1's version is preserved
        content = (test_project / ".claude/rules/style-guide.md").read_text()
        assert "Pkg1 Style" in content

    def test_packages_with_same_instruction_name_rename(self, package_builder, test_project: Path) -> None:
        """Test RENAME strategy with conflicting instruction names."""
        pkg1 = package_builder(
            name="pkg1",
            version="1.0.0",
            instructions=[{"name": "config", "content": "# Pkg1 Config"}],
        )
        pkg2 = package_builder(
            name="pkg2",
            version="1.0.0",
            instructions=[{"name": "config", "content": "# Pkg2 Config"}],
        )

        # Install both with RENAME
        install_package(pkg1, test_project, AIToolType.CLAUDE)
        install_package(
            pkg2,
            test_project,
            AIToolType.CLAUDE,
            conflict_resolution=ConflictResolution.RENAME,
        )

        # Should have both files
        assert (test_project / ".claude/rules/config.md").exists()
        assert (test_project / ".claude/rules/config-1.md").exists()

        content1 = (test_project / ".claude/rules/config.md").read_text()
        content2 = (test_project / ".claude/rules/config-1.md").read_text()

        assert "Pkg1" in content1
        assert "Pkg2" in content2

    def test_package_with_resource_conflicts_with_project_file(self, package_builder, test_project: Path) -> None:
        """Test package resource conflicting with existing project file."""
        # Create project file
        (test_project / ".gitignore").write_text("# Project gitignore\n*.pyc\n")

        # Create package with .gitignore
        pkg = package_builder(
            name="pkg",
            version="1.0.0",
            resources=[{"name": ".gitignore", "content": "# Package gitignore\nnode_modules/\n"}],
        )

        # Install with SKIP (preserves project file)
        result = install_package(
            pkg,
            test_project,
            AIToolType.CLAUDE,
            conflict_resolution=ConflictResolution.SKIP,
        )

        assert result.success is True

        # Project file preserved
        content = (test_project / ".gitignore").read_text()
        assert "*.pyc" in content
        assert "node_modules" not in content


class TestPackageDependencies:
    """Test scenarios involving package dependencies."""

    def test_install_base_then_extension_package(self, package_builder, test_project: Path) -> None:
        """Test installing a base package followed by an extension."""
        # Base package
        base_pkg = package_builder(
            name="python-base",
            version="1.0.0",
            instructions=[
                {"name": "python-basics", "content": "# Python basics"},
                {"name": "python-style", "content": "# PEP 8"},
            ],
        )

        # Extension package (assumes base is installed)
        extension_pkg = package_builder(
            name="python-advanced",
            version="1.0.0",
            instructions=[
                {"name": "async-patterns", "content": "# Async programming"},
                {"name": "type-hints", "content": "# Advanced typing"},
            ],
        )

        # Install both
        install_package(base_pkg, test_project, AIToolType.CLAUDE)
        install_package(extension_pkg, test_project, AIToolType.CLAUDE)

        # All instructions should exist
        assert (test_project / ".claude/rules/python-basics.md").exists()
        assert (test_project / ".claude/rules/python-style.md").exists()
        assert (test_project / ".claude/rules/async-patterns.md").exists()
        assert (test_project / ".claude/rules/type-hints.md").exists()

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        packages = tracker.get_installed_packages()
        assert len(packages) == 2

    def test_company_team_personal_package_layering(self, package_builder, tmp_path: Path) -> None:
        """Test realistic scenario: company + team + personal packages."""
        project = tmp_path / "project"
        project.mkdir()

        # Company-wide package (security policies)
        company_pkg = package_builder(
            name="company-security",
            version="1.0.0",
            instructions=[
                {"name": "security-policy", "content": "# Company security"},
            ],
        )

        # Team package (backend practices)
        team_pkg = package_builder(
            name="team-backend",
            version="1.0.0",
            instructions=[
                {"name": "api-standards", "content": "# API standards"},
                {"name": "database-patterns", "content": "# DB patterns"},
            ],
        )

        # Personal package (preferred tools)
        personal_pkg = package_builder(
            name="personal-tools",
            version="1.0.0",
            instructions=[
                {"name": "my-shortcuts", "content": "# Personal shortcuts"},
            ],
        )

        # Install all three (simulating different scopes)
        install_package(company_pkg, project, AIToolType.CLAUDE)
        install_package(team_pkg, project, AIToolType.CLAUDE)
        install_package(personal_pkg, project, AIToolType.CLAUDE)

        # Verify all coexist
        tracker = PackageTracker(project / ".ai-config-kit/packages.json")
        packages = tracker.get_installed_packages()
        assert len(packages) == 3

        names = {p.package_name for p in packages}
        assert names == {"company-security", "team-backend", "personal-tools"}


class TestPackageOrdering:
    """Test installation order and its effects."""

    def test_installation_order_matters_for_conflicts(self, package_builder, test_project: Path) -> None:
        """Test that installation order matters when files conflict."""
        pkg_a = package_builder(
            name="pkg-a",
            version="1.0.0",
            instructions=[{"name": "shared", "content": "# From Package A"}],
        )
        pkg_b = package_builder(
            name="pkg-b",
            version="1.0.0",
            instructions=[{"name": "shared", "content": "# From Package B"}],
        )

        # Test A then B with SKIP
        install_package(pkg_a, test_project, AIToolType.CLAUDE)
        install_package(
            pkg_b,
            test_project,
            AIToolType.CLAUDE,
            conflict_resolution=ConflictResolution.SKIP,
        )

        content = (test_project / ".claude/rules/shared.md").read_text()
        assert "Package A" in content  # First one wins

    def test_reinstall_all_in_different_order(self, package_builder, test_project: Path) -> None:
        """Test reinstalling multiple packages in different order."""
        pkg1 = package_builder(
            name="pkg1",
            version="1.0.0",
            instructions=[{"name": "guide1", "content": "# Pkg1"}],
        )
        pkg2 = package_builder(
            name="pkg2",
            version="1.0.0",
            instructions=[{"name": "guide2", "content": "# Pkg2"}],
        )
        pkg3 = package_builder(
            name="pkg3",
            version="1.0.0",
            instructions=[{"name": "guide3", "content": "# Pkg3"}],
        )

        # Install in order 1, 2, 3
        install_package(pkg1, test_project, AIToolType.CLAUDE)
        install_package(pkg2, test_project, AIToolType.CLAUDE)
        install_package(pkg3, test_project, AIToolType.CLAUDE)

        # Get tracker
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")

        # Reinstall in order 3, 1, 2
        install_package(
            pkg3,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        install_package(
            pkg1,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        install_package(
            pkg2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        # All should still be installed
        packages2 = tracker.get_installed_packages()
        assert len(packages2) == 3

        # Order in tracker may differ but all exist
        assert {p.package_name for p in packages2} == {"pkg1", "pkg2", "pkg3"}


class TestPackageUpdates:
    """Test updating multiple packages."""

    def test_update_all_packages_to_latest(self, package_builder, test_project: Path) -> None:
        """Test updating all installed packages to newer versions."""
        # Install v1.0.0 of three packages
        pkg1_v1 = package_builder(
            name="pkg1",
            version="1.0.0",
            instructions=[{"name": "guide1", "content": "# Pkg1 v1.0"}],
        )
        pkg2_v1 = package_builder(
            name="pkg2",
            version="1.0.0",
            instructions=[{"name": "guide2", "content": "# Pkg2 v1.0"}],
        )
        pkg3_v1 = package_builder(
            name="pkg3",
            version="1.0.0",
            instructions=[{"name": "guide3", "content": "# Pkg3 v1.0"}],
        )

        install_package(pkg1_v1, test_project, AIToolType.CLAUDE)
        install_package(pkg2_v1, test_project, AIToolType.CLAUDE)
        install_package(pkg3_v1, test_project, AIToolType.CLAUDE)

        # Update all to v2.0.0
        pkg1_v2 = package_builder(
            name="pkg1",
            version="2.0.0",
            instructions=[{"name": "guide1", "content": "# Pkg1 v2.0"}],
        )
        pkg2_v2 = package_builder(
            name="pkg2",
            version="2.0.0",
            instructions=[{"name": "guide2", "content": "# Pkg2 v2.0"}],
        )
        pkg3_v2 = package_builder(
            name="pkg3",
            version="2.0.0",
            instructions=[{"name": "guide3", "content": "# Pkg3 v2.0"}],
        )

        install_package(
            pkg1_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        install_package(
            pkg2_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        install_package(
            pkg3_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        # Verify all updated
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        for name in ["pkg1", "pkg2", "pkg3"]:
            record = tracker.get_package(name, InstallationScope.PROJECT)
            assert record.version == "2.0.0"

    def test_selective_package_updates(self, package_builder, test_project: Path) -> None:
        """Test updating only some packages while leaving others at old versions."""
        # Install three packages
        pkg1 = package_builder(
            name="stable-pkg",
            version="1.0.0",
            instructions=[{"name": "stable", "content": "# Stable v1.0"}],
        )
        pkg2 = package_builder(
            name="beta-pkg",
            version="1.0.0",
            instructions=[{"name": "beta", "content": "# Beta v1.0"}],
        )
        pkg3 = package_builder(
            name="experimental-pkg",
            version="1.0.0",
            instructions=[{"name": "experimental", "content": "# Exp v1.0"}],
        )

        install_package(pkg1, test_project, AIToolType.CLAUDE)
        install_package(pkg2, test_project, AIToolType.CLAUDE)
        install_package(pkg3, test_project, AIToolType.CLAUDE)

        # Update only beta and experimental
        pkg2_v2 = package_builder(
            name="beta-pkg",
            version="2.0.0",
            instructions=[{"name": "beta", "content": "# Beta v2.0"}],
        )
        pkg3_v2 = package_builder(
            name="experimental-pkg",
            version="2.0.0",
            instructions=[{"name": "experimental", "content": "# Exp v2.0"}],
        )

        install_package(
            pkg2_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        install_package(
            pkg3_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        # Verify selective updates
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        stable = tracker.get_package("stable-pkg", InstallationScope.PROJECT)
        beta = tracker.get_package("beta-pkg", InstallationScope.PROJECT)
        experimental = tracker.get_package("experimental-pkg", InstallationScope.PROJECT)

        assert stable.version == "1.0.0"  # Not updated
        assert beta.version == "2.0.0"  # Updated
        assert experimental.version == "2.0.0"  # Updated
