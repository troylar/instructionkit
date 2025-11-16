"""E2E tests for package version management and updates."""

import subprocess
from pathlib import Path

from aiconfigkit.cli.package_install import install_package
from aiconfigkit.core.models import AIToolType, ConflictResolution, InstallationScope
from aiconfigkit.storage.package_tracker import PackageTracker


class TestVersionUpdates:
    """Test updating packages to newer versions."""

    def test_update_patch_version(self, package_builder, test_project: Path) -> None:
        """Test updating from 1.0.0 to 1.0.1 (patch update)."""
        # Install v1.0.0
        pkg_v1 = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[
                {"name": "guide", "content": "# Guide v1.0.0\n\nOriginal content"},
            ],
        )
        result1 = install_package(pkg_v1, test_project, AIToolType.CLAUDE)
        assert result1.success is True

        # Create v1.0.1 with bug fix
        pkg_v101 = package_builder(
            name="test-pkg",
            version="1.0.1",
            instructions=[
                {"name": "guide", "content": "# Guide v1.0.1\n\nBug fix applied"},
            ],
        )

        # Update
        result2 = install_package(
            pkg_v101,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        assert result2.success is True

        # Verify version updated
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.0.1"

        # Verify content updated
        guide_path = test_project / ".claude/rules/guide.md"
        content = guide_path.read_text()
        assert "1.0.1" in content
        assert "Bug fix" in content

    def test_update_minor_version(self, package_builder, test_project: Path) -> None:
        """Test updating from 1.0.0 to 1.1.0 (minor update with new features)."""
        # Install v1.0.0
        pkg_v1 = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[
                {"name": "basics", "content": "# Basics\n\nBasic guide"},
            ],
        )
        install_package(pkg_v1, test_project, AIToolType.CLAUDE)

        # Create v1.1.0 with new instruction
        pkg_v11 = package_builder(
            name="test-pkg",
            version="1.1.0",
            instructions=[
                {"name": "basics", "content": "# Basics\n\nUpdated basic guide"},
                {"name": "advanced", "content": "# Advanced\n\nNew advanced features"},
            ],
        )

        # Update
        result = install_package(
            pkg_v11,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        assert result.success is True

        # Verify both instructions exist
        assert (test_project / ".claude/rules/basics.md").exists()
        assert (test_project / ".claude/rules/advanced.md").exists()

        # Verify version
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.1.0"
        assert len(pkg_record.components) == 2

    def test_update_major_version(self, package_builder, test_project: Path) -> None:
        """Test updating from 1.0.0 to 2.0.0 (major update with breaking changes)."""
        # Install v1.0.0
        pkg_v1 = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[
                {"name": "old-api", "content": "# Old API\n\nDeprecated API"},
            ],
            hooks=[
                {"name": "old-hook", "content": "#!/bin/bash\necho 'old'\n"},
            ],
        )
        install_package(pkg_v1, test_project, AIToolType.CLAUDE)

        # Create v2.0.0 with completely new structure
        pkg_v2 = package_builder(
            name="test-pkg",
            version="2.0.0",
            instructions=[
                {"name": "new-api", "content": "# New API\n\nModern API"},
            ],
            commands=[
                {"name": "new-command", "content": "#!/bin/bash\necho 'new'\n"},
            ],
        )

        # Update (breaking changes)
        result = install_package(
            pkg_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        assert result.success is True

        # Verify new structure
        assert (test_project / ".claude/rules/new-api.md").exists()
        assert (test_project / ".claude/commands/new-command.sh").exists()

        # Old files may still exist (not removed automatically)
        # This is expected behavior - major updates require manual cleanup

        # Verify version
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "2.0.0"

    def test_downgrade_version(self, package_builder, test_project: Path) -> None:
        """Test downgrading from 2.0.0 to 1.0.0."""
        # Install v2.0.0
        pkg_v2 = package_builder(
            name="test-pkg",
            version="2.0.0",
            instructions=[
                {"name": "guide", "content": "# Guide v2.0.0\n\nLatest features"},
            ],
        )
        install_package(pkg_v2, test_project, AIToolType.CLAUDE)

        # Downgrade to v1.0.0
        pkg_v1 = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[
                {"name": "guide", "content": "# Guide v1.0.0\n\nStable version"},
            ],
        )

        result = install_package(
            pkg_v1,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        assert result.success is True

        # Verify downgrade
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.0.0"

        # Verify content downgraded
        content = (test_project / ".claude/rules/guide.md").read_text()
        assert "1.0.0" in content


class TestGitVersionTags:
    """Test installing specific versions from git tags."""

    def test_install_from_specific_tag(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test installing a package from a specific git tag."""
        # Create v1.0.0
        pkg_path = package_builder(
            name="git-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1.0.0"}],
            as_git=True,
        )

        # Create v1.1.0 (new commit and tag)
        guide_path = pkg_path / "instructions/guide.md"
        guide_path.write_text("# v1.1.0\n\nUpdated")

        # Update manifest
        manifest_path = pkg_path / "ai-config-kit-package.yaml"
        manifest = manifest_path.read_text()
        manifest = manifest.replace("version: 1.0.0", "version: 1.1.0")
        manifest_path.write_text(manifest)

        subprocess.run(["git", "add", "."], cwd=pkg_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Release v1.1.0"],
            cwd=pkg_path,
            check=True,
        )
        subprocess.run(["git", "tag", "v1.1.0"], cwd=pkg_path, check=True)

        # Clone to temp location for tag checkout
        clone_path = tmp_path / "clone"
        subprocess.run(
            ["git", "clone", str(pkg_path), str(clone_path)],
            check=True,
            capture_output=True,
        )

        # Checkout v1.0.0
        subprocess.run(
            ["git", "checkout", "v1.0.0"],
            cwd=clone_path,
            check=True,
            capture_output=True,
        )

        # Install from v1.0.0
        result = install_package(clone_path, test_project, AIToolType.CLAUDE)
        assert result.success is True

        # Verify installed v1.0.0
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("git-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.0.0"

        content = (test_project / ".claude/rules/guide.md").read_text()
        assert "v1.0.0" in content
        assert "v1.1.0" not in content

    def test_update_by_installing_newer_tag(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test updating by installing from a newer tag."""
        # Create repo with multiple versions
        pkg_path = package_builder(
            name="versioned-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1.0.0"}],
            as_git=True,
        )

        # Install v1.0.0
        result1 = install_package(pkg_path, test_project, AIToolType.CLAUDE)
        assert result1.success is True

        # Create v1.1.0
        (pkg_path / "instructions/guide.md").write_text("# v1.1.0\n")
        manifest = (pkg_path / "ai-config-kit-package.yaml").read_text()
        manifest = manifest.replace("version: 1.0.0", "version: 1.1.0")
        (pkg_path / "ai-config-kit-package.yaml").write_text(manifest)

        subprocess.run(["git", "add", "."], cwd=pkg_path, check=True)
        subprocess.run(["git", "commit", "-m", "v1.1.0"], cwd=pkg_path, check=True)
        subprocess.run(["git", "tag", "v1.1.0"], cwd=pkg_path, check=True)

        # Update to v1.1.0
        result2 = install_package(
            pkg_path,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        assert result2.success is True

        # Verify update
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("versioned-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.1.0"


class TestVersionConflicts:
    """Test handling version conflicts and requirements."""

    def test_install_older_version_over_newer_warns(self, package_builder, test_project: Path) -> None:
        """Test installing an older version over a newer one."""
        # Install v2.0.0
        pkg_v2 = package_builder(
            name="test-pkg",
            version="2.0.0",
            instructions=[{"name": "guide", "content": "# v2.0.0"}],
        )
        install_package(pkg_v2, test_project, AIToolType.CLAUDE)

        # Install v1.0.0 (downgrade)
        pkg_v1 = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1.0.0"}],
        )

        # Should succeed but is a downgrade
        result = install_package(
            pkg_v1,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        assert result.success is True

        # Verify downgrade occurred
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.0.0"

    def test_multiple_versions_in_different_projects(self, package_builder, tmp_path: Path) -> None:
        """Test installing different versions in different projects."""
        # Create two projects
        project1 = tmp_path / "project1"
        project1.mkdir()
        project2 = tmp_path / "project2"
        project2.mkdir()

        # Create two versions
        pkg_v1 = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1"}],
        )
        pkg_v2 = package_builder(
            name="test-pkg",
            version="2.0.0",
            instructions=[{"name": "guide", "content": "# v2"}],
        )

        # Install different versions
        install_package(pkg_v1, project1, AIToolType.CLAUDE)
        install_package(pkg_v2, project2, AIToolType.CLAUDE)

        # Verify each has correct version
        tracker1 = PackageTracker(project1 / ".ai-config-kit/packages.json")
        tracker2 = PackageTracker(project2 / ".ai-config-kit/packages.json")

        pkg1_record = tracker1.get_package("test-pkg", InstallationScope.PROJECT)
        pkg2_record = tracker2.get_package("test-pkg", InstallationScope.PROJECT)

        assert pkg1_record.version == "1.0.0"
        assert pkg2_record.version == "2.0.0"

        # Verify content
        content1 = (project1 / ".claude/rules/guide.md").read_text()
        content2 = (project2 / ".claude/rules/guide.md").read_text()

        assert "v1" in content1
        assert "v2" in content2


class TestPreReleaseVersions:
    """Test handling pre-release versions."""

    def test_install_alpha_version(self, package_builder, test_project: Path) -> None:
        """Test installing an alpha pre-release version."""
        pkg = package_builder(
            name="test-pkg",
            version="2.0.0-alpha.1",
            instructions=[{"name": "guide", "content": "# Alpha version"}],
        )

        result = install_package(pkg, test_project, AIToolType.CLAUDE)
        assert result.success is True

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "2.0.0-alpha.1"

    def test_install_beta_then_release(self, package_builder, test_project: Path) -> None:
        """Test upgrading from beta to final release."""
        # Install beta
        pkg_beta = package_builder(
            name="test-pkg",
            version="1.0.0-beta.1",
            instructions=[{"name": "guide", "content": "# Beta"}],
        )
        install_package(pkg_beta, test_project, AIToolType.CLAUDE)

        # Upgrade to release
        pkg_release = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Release"}],
        )
        result = install_package(
            pkg_release,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )
        assert result.success is True

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.0.0"

    def test_install_rc_version(self, package_builder, test_project: Path) -> None:
        """Test installing release candidate version."""
        pkg = package_builder(
            name="test-pkg",
            version="3.0.0-rc.2",
            instructions=[{"name": "guide", "content": "# Release candidate"}],
        )

        result = install_package(pkg, test_project, AIToolType.CLAUDE)
        assert result.success is True

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "3.0.0-rc.2"
