"""E2E tests for git repository operations with packages."""

import subprocess
from pathlib import Path

from aiconfigkit.cli.package_install import install_package
from aiconfigkit.core.models import AIToolType, ConflictResolution, InstallationScope
from aiconfigkit.storage.package_tracker import PackageTracker


class TestGitRepositoryInstallation:
    """Test installing packages from git repositories."""

    def test_install_from_local_git_repo(self, package_builder, test_project: Path) -> None:
        """Test installing a package from a local git repository."""
        pkg = package_builder(
            name="git-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "description": "Git-based guide"}],
            as_git=True,
        )

        result = install_package(pkg, test_project, AIToolType.CLAUDE)

        assert result.success is True
        assert (test_project / ".claude/rules/guide.md").exists()

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("git-pkg", InstallationScope.PROJECT)
        assert pkg_record is not None
        assert pkg_record.version == "1.0.0"

    def test_install_from_cloned_repo(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test installing from a git repository that was cloned."""
        # Create original repo
        original = package_builder(
            name="original-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Original"}],
            as_git=True,
        )

        # Clone it
        clone_path = tmp_path / "clone"
        subprocess.run(
            ["git", "clone", str(original), str(clone_path)],
            check=True,
            capture_output=True,
        )

        # Install from clone
        result = install_package(clone_path, test_project, AIToolType.CLAUDE)

        assert result.success is True
        assert (test_project / ".claude/rules/guide.md").exists()

    def test_install_after_git_pull_updates_package(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test that pulling updates from git and reinstalling updates the package."""
        # Create repo with v1.0.0
        repo = package_builder(
            name="updated-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Version 1"}],
            as_git=True,
        )

        # Clone it
        clone_path = tmp_path / "clone"
        subprocess.run(
            ["git", "clone", str(repo), str(clone_path)],
            check=True,
            capture_output=True,
        )

        # Install v1.0.0
        install_package(clone_path, test_project, AIToolType.CLAUDE)

        # Update original repo
        (repo / "instructions/guide.md").write_text("# Version 2\n\nUpdated content")
        manifest = (repo / "ai-config-kit-package.yaml").read_text()
        manifest = manifest.replace("version: 1.0.0", "version: 1.1.0")
        (repo / "ai-config-kit-package.yaml").write_text(manifest)

        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "Update to 1.1.0"], cwd=repo, check=True)

        # Pull updates
        subprocess.run(
            ["git", "pull"],
            cwd=clone_path,
            check=True,
            capture_output=True,
        )

        # Reinstall
        result = install_package(
            clone_path,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        assert result.success is True

        # Verify updated
        content = (test_project / ".claude/rules/guide.md").read_text()
        assert "Version 2" in content

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("updated-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.1.0"


class TestGitBranches:
    """Test installing from different git branches."""

    def test_install_from_main_branch(self, package_builder, test_project: Path) -> None:
        """Test installing from main branch."""
        pkg = package_builder(
            name="main-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Main branch"}],
            as_git=True,
        )

        result = install_package(pkg, test_project, AIToolType.CLAUDE)

        assert result.success is True

        content = (test_project / ".claude/rules/guide.md").read_text()
        assert "Main branch" in content

    def test_install_from_feature_branch(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test installing from a feature branch."""
        # Create repo on main
        repo = package_builder(
            name="branch-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Main branch"}],
            as_git=True,
        )

        # Create feature branch
        subprocess.run(
            ["git", "checkout", "-b", "feature/new-feature"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Make changes on feature branch
        (repo / "instructions/guide.md").write_text("# Feature branch\n\nNew feature")
        (repo / "instructions/experimental.md").write_text("# Experimental\n")

        # Update manifest to include new instruction
        manifest = (repo / "ai-config-kit-package.yaml").read_text()
        manifest = manifest.replace("version: 1.0.0", "version: 1.1.0-dev")
        manifest += """    - name: experimental
      description: Experimental feature
      file: instructions/experimental.md
      tags: [experimental]
"""
        (repo / "ai-config-kit-package.yaml").write_text(manifest)

        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Feature branch changes"],
            cwd=repo,
            check=True,
        )

        # Clone and checkout feature branch
        clone_path = tmp_path / "clone"
        subprocess.run(
            ["git", "clone", "-b", "feature/new-feature", str(repo), str(clone_path)],
            check=True,
            capture_output=True,
        )

        # Install from feature branch
        result = install_package(clone_path, test_project, AIToolType.CLAUDE)

        assert result.success is True
        assert (test_project / ".claude/rules/guide.md").exists()
        assert (test_project / ".claude/rules/experimental.md").exists()

        content = (test_project / ".claude/rules/guide.md").read_text()
        assert "Feature branch" in content

    def test_switch_between_branches(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test switching between branches and reinstalling."""
        # Create repo with two branches
        repo = package_builder(
            name="multi-branch-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Main"}],
            as_git=True,
        )

        # Create dev branch with different content
        subprocess.run(
            ["git", "checkout", "-b", "dev"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        (repo / "instructions/guide.md").write_text("# Dev branch")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "Dev changes"], cwd=repo, check=True)

        # Clone
        clone_path = tmp_path / "clone"
        subprocess.run(
            ["git", "clone", str(repo), str(clone_path)],
            check=True,
            capture_output=True,
        )

        # Install from main
        subprocess.run(
            ["git", "checkout", "master"],
            cwd=clone_path,
            check=True,
            capture_output=True,
        )
        install_package(clone_path, test_project, AIToolType.CLAUDE)

        content_main = (test_project / ".claude/rules/guide.md").read_text()
        assert "Main" in content_main

        # Switch to dev and reinstall
        subprocess.run(
            ["git", "checkout", "dev"],
            cwd=clone_path,
            check=True,
            capture_output=True,
        )
        install_package(
            clone_path,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        content_dev = (test_project / ".claude/rules/guide.md").read_text()
        assert "Dev branch" in content_dev


class TestGitTags:
    """Test installing from git tags."""

    def test_install_from_latest_tag(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test installing from the latest git tag."""
        # Create repo with multiple tags
        repo = package_builder(
            name="tagged-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1.0.0"}],
            as_git=True,
        )

        # Create v1.1.0
        (repo / "instructions/guide.md").write_text("# v1.1.0")
        manifest = (repo / "ai-config-kit-package.yaml").read_text()
        manifest = manifest.replace("version: 1.0.0", "version: 1.1.0")
        (repo / "ai-config-kit-package.yaml").write_text(manifest)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "v1.1.0"], cwd=repo, check=True)
        subprocess.run(["git", "tag", "v1.1.0"], cwd=repo, check=True)

        # Install latest (v1.1.0)
        result = install_package(repo, test_project, AIToolType.CLAUDE)

        assert result.success is True

        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("tagged-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.1.0"

    def test_install_specific_tag_version(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test checking out and installing a specific tag."""
        # Create repo with v1.0.0 and v2.0.0
        repo = package_builder(
            name="versioned-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1.0.0"}],
            as_git=True,
        )

        # Create v2.0.0
        (repo / "instructions/guide.md").write_text("# v2.0.0")
        manifest = (repo / "ai-config-kit-package.yaml").read_text()
        manifest = manifest.replace("version: 1.0.0", "version: 2.0.0")
        (repo / "ai-config-kit-package.yaml").write_text(manifest)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "v2.0.0"], cwd=repo, check=True)
        subprocess.run(["git", "tag", "v2.0.0"], cwd=repo, check=True)

        # Clone and checkout v1.0.0
        clone_path = tmp_path / "clone"
        subprocess.run(
            ["git", "clone", str(repo), str(clone_path)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "v1.0.0"],
            cwd=clone_path,
            check=True,
            capture_output=True,
        )

        # Install v1.0.0
        result = install_package(clone_path, test_project, AIToolType.CLAUDE)

        assert result.success is True

        # Verify v1.0.0 installed
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("versioned-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "1.0.0"

        content = (test_project / ".claude/rules/guide.md").read_text()
        assert "v1.0.0" in content
        assert "v2.0.0" not in content


class TestGitCommits:
    """Test installing from specific commits."""

    def test_install_from_specific_commit(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test checking out and installing from a specific commit."""
        # Create repo with multiple commits
        repo = package_builder(
            name="commit-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# First"}],
            as_git=True,
        )

        # Get first commit hash
        first_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        # Make second commit
        (repo / "instructions/guide.md").write_text("# Second")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "Second"], cwd=repo, check=True)

        # Make third commit
        (repo / "instructions/guide.md").write_text("# Third")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "Third"], cwd=repo, check=True)

        # Clone and checkout first commit
        clone_path = tmp_path / "clone"
        subprocess.run(
            ["git", "clone", str(repo), str(clone_path)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", first_commit],
            cwd=clone_path,
            check=True,
            capture_output=True,
        )

        # Install from first commit
        result = install_package(clone_path, test_project, AIToolType.CLAUDE)

        assert result.success is True

        # Verify content from first commit
        content = (test_project / ".claude/rules/guide.md").read_text()
        assert "First" in content
        assert "Second" not in content
        assert "Third" not in content

    def test_update_to_latest_commit(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test updating from old commit to latest commit."""
        # Create repo
        repo = package_builder(
            name="evolving-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Old"}],
            as_git=True,
        )

        # Clone
        clone_path = tmp_path / "clone"
        subprocess.run(
            ["git", "clone", str(repo), str(clone_path)],
            check=True,
            capture_output=True,
        )

        # Install old version
        install_package(clone_path, test_project, AIToolType.CLAUDE)

        content_old = (test_project / ".claude/rules/guide.md").read_text()
        assert "Old" in content_old

        # Update original repo
        (repo / "instructions/guide.md").write_text("# New\n\nLatest updates")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "Latest"], cwd=repo, check=True)

        # Pull and reinstall
        subprocess.run(["git", "pull"], cwd=clone_path, check=True, capture_output=True)
        install_package(
            clone_path,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        content_new = (test_project / ".claude/rules/guide.md").read_text()
        assert "New" in content_new
        assert "Latest updates" in content_new


class TestGitHistory:
    """Test scenarios involving git history."""

    def test_install_then_package_repo_history_changes(self, package_builder, test_project: Path) -> None:
        """Test that package can be updated even after git history is rewritten."""
        # Create repo
        repo = package_builder(
            name="history-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Original"}],
            as_git=True,
        )

        # Install
        install_package(repo, test_project, AIToolType.CLAUDE)

        # Amend last commit (rewrite history)
        (repo / "instructions/guide.md").write_text("# Amended")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(
            ["git", "commit", "--amend", "--no-edit"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Force reinstall
        result = install_package(
            repo,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        assert result.success is True

        content = (test_project / ".claude/rules/guide.md").read_text()
        assert "Amended" in content

    def test_install_from_repo_with_no_commits(self, test_project: Path, tmp_path: Path) -> None:
        """Test installing from a freshly initialized git repo with no commits."""
        # Create empty git repo
        empty_repo = tmp_path / "empty-repo"
        empty_repo.mkdir()

        subprocess.run(["git", "init"], cwd=empty_repo, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=empty_repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=empty_repo,
            check=True,
        )

        # Add package files but don't commit
        (empty_repo / "ai-config-kit-package.yaml").write_text(
            """name: no-commit-pkg
version: 1.0.0
description: Package with no commits
author: Test
namespace: test/pkg
license: MIT

components:
  instructions:
    - name: guide
      description: Guide
      file: instructions/guide.md
      tags: [test]
"""
        )
        (empty_repo / "instructions").mkdir()
        (empty_repo / "instructions/guide.md").write_text("# Guide")

        # Should still be able to install from working directory
        result = install_package(empty_repo, test_project, AIToolType.CLAUDE)

        assert result.success is True
        assert (test_project / ".claude/rules/guide.md").exists()
