"""E2E tests for conflict resolution strategies."""

from pathlib import Path

from aiconfigkit.cli.package_install import install_package
from aiconfigkit.core.models import AIToolType, ConflictResolution, InstallationScope
from aiconfigkit.storage.package_tracker import PackageTracker


class TestSkipStrategy:
    """Test SKIP conflict resolution strategy."""

    def test_skip_preserves_user_modifications(self, package_builder, test_project: Path) -> None:
        """Test that SKIP strategy preserves user modifications."""
        # Install package
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[
                {"name": "guide", "content": "# Original\n\nPackage content"},
            ],
        )
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # User modifies file
        guide_path = test_project / ".claude/rules/guide.md"
        user_content = "# Custom\n\nUser modifications"
        guide_path.write_text(user_content)

        # Reinstall with SKIP
        result = install_package(
            pkg,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.SKIP,
        )

        assert result.success is True
        assert result.skipped_count > 0

        # Verify user modifications preserved
        assert guide_path.read_text() == user_content

    def test_skip_only_affects_existing_files(self, package_builder, test_project: Path) -> None:
        """Test that SKIP only affects files that already exist."""
        # Install v1 with one instruction
        pkg_v1 = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[
                {"name": "guide1", "content": "# Guide 1"},
            ],
        )
        install_package(pkg_v1, test_project, AIToolType.CLAUDE)

        # Modify existing file
        guide1_path = test_project / ".claude/rules/guide1.md"
        guide1_path.write_text("# Modified")

        # Install v2 with two instructions
        pkg_v2 = package_builder(
            name="test-pkg",
            version="1.1.0",
            instructions=[
                {"name": "guide1", "content": "# Guide 1 Updated"},
                {"name": "guide2", "content": "# Guide 2 New"},
            ],
        )

        result = install_package(
            pkg_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.SKIP,
        )

        assert result.success is True

        # Existing file skipped
        assert guide1_path.read_text() == "# Modified"

        # New file installed
        guide2_path = test_project / ".claude/rules/guide2.md"
        assert guide2_path.exists()
        assert "Guide 2 New" in guide2_path.read_text()

    def test_skip_with_multiple_file_types(self, package_builder, test_project: Path) -> None:
        """Test SKIP strategy with different component types."""
        # Install package with multiple components
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Guide"}],
            hooks=[{"name": "pre-commit", "content": "#!/bin/bash\necho 'original'\n"}],
            commands=[{"name": "test", "content": "#!/bin/bash\necho 'test'\n"}],
        )
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # Modify instruction and hook, leave command unchanged
        (test_project / ".claude/rules/guide.md").write_text("# Modified Guide")
        (test_project / ".claude/hooks/pre-commit.sh").write_text("#!/bin/bash\necho 'modified'\n")

        # Reinstall with SKIP
        result = install_package(
            pkg,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.SKIP,
        )

        assert result.success is True
        assert result.skipped_count >= 2  # Instruction and hook skipped

        # Verify modifications preserved
        assert "Modified Guide" in (test_project / ".claude/rules/guide.md").read_text()
        assert "modified" in (test_project / ".claude/hooks/pre-commit.sh").read_text()


class TestOverwriteStrategy:
    """Test OVERWRITE conflict resolution strategy."""

    def test_overwrite_replaces_user_modifications(self, package_builder, test_project: Path) -> None:
        """Test that OVERWRITE replaces all user modifications."""
        # Install package
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[
                {"name": "guide", "content": "# Original Package Content\n"},
            ],
        )
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # User modifies file
        guide_path = test_project / ".claude/rules/guide.md"
        guide_path.write_text("# User Modifications\n\nCustom content")

        # Reinstall with OVERWRITE
        result = install_package(
            pkg,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        assert result.success is True
        assert result.skipped_count == 0

        # Verify package content restored
        content = guide_path.read_text()
        assert "Original Package Content" in content
        assert "User Modifications" not in content

    def test_overwrite_all_component_types(self, package_builder, test_project: Path) -> None:
        """Test OVERWRITE with all component types."""
        # Install package
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Original"}],
            hooks=[{"name": "pre-commit", "content": "#!/bin/bash\necho 'original'\n"}],
            commands=[{"name": "test", "content": "#!/bin/bash\necho 'test original'\n"}],
            resources=[{"name": ".gitignore", "content": "# Original gitignore"}],
        )
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # Modify all files
        (test_project / ".claude/rules/guide.md").write_text("# Modified")
        (test_project / ".claude/hooks/pre-commit.sh").write_text("#!/bin/bash\necho 'modified'\n")
        (test_project / ".claude/commands/test.sh").write_text("#!/bin/bash\necho 'modified'\n")
        (test_project / ".gitignore").write_text("# Modified gitignore")

        # Reinstall with OVERWRITE
        result = install_package(
            pkg,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        assert result.success is True

        # Verify all restored
        assert "# Original" in (test_project / ".claude/rules/guide.md").read_text()
        assert "echo 'original'" in (test_project / ".claude/hooks/pre-commit.sh").read_text()
        assert "echo 'test original'" in (test_project / ".claude/commands/test.sh").read_text()
        assert "# Original gitignore" in (test_project / ".gitignore").read_text()

    def test_overwrite_during_version_update(self, package_builder, test_project: Path) -> None:
        """Test OVERWRITE when updating package versions."""
        # Install v1.0.0
        pkg_v1 = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1.0.0 Content"}],
        )
        install_package(pkg_v1, test_project, AIToolType.CLAUDE)

        # User makes modifications
        guide_path = test_project / ".claude/rules/guide.md"
        guide_path.write_text("# User Content")

        # Install v2.0.0 with OVERWRITE
        pkg_v2 = package_builder(
            name="test-pkg",
            version="2.0.0",
            instructions=[{"name": "guide", "content": "# v2.0.0 Content\n\nNew features"}],
        )

        result = install_package(
            pkg_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        assert result.success is True

        # Verify v2 content installed
        content = guide_path.read_text()
        assert "v2.0.0 Content" in content
        assert "New features" in content
        assert "User Content" not in content

        # Verify version updated
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        pkg_record = tracker.get_package("test-pkg", InstallationScope.PROJECT)
        assert pkg_record.version == "2.0.0"


class TestRenameStrategy:
    """Test RENAME conflict resolution strategy."""

    def test_rename_creates_numbered_copy(self, package_builder, test_project: Path) -> None:
        """Test that RENAME creates numbered copies."""
        # Install package
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Original"}],
        )
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # Modify file
        original_path = test_project / ".claude/rules/guide.md"
        original_path.write_text("# User Modified")

        # Reinstall with RENAME
        result = install_package(
            pkg,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.RENAME,
        )

        assert result.success is True

        # Original file preserved
        assert original_path.exists()
        assert "User Modified" in original_path.read_text()

        # New numbered file created
        renamed_path = test_project / ".claude/rules/guide-1.md"
        assert renamed_path.exists()
        assert "# Original" in renamed_path.read_text()

    def test_rename_increments_number(self, package_builder, test_project: Path) -> None:
        """Test that RENAME increments number for multiple installs."""
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Version"}],
        )

        # Install original
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # Install with RENAME (creates guide-1.md)
        pkg_v2 = package_builder(
            name="test-pkg",
            version="1.1.0",
            instructions=[{"name": "guide", "content": "# Version 1.1"}],
        )
        install_package(
            pkg_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.RENAME,
        )

        # Install with RENAME again (creates guide-2.md)
        pkg_v3 = package_builder(
            name="test-pkg",
            version="1.2.0",
            instructions=[{"name": "guide", "content": "# Version 1.2"}],
        )
        install_package(
            pkg_v3,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.RENAME,
        )

        # Verify all three versions exist
        rules_dir = test_project / ".claude/rules"
        assert (rules_dir / "guide.md").exists()
        assert (rules_dir / "guide-1.md").exists()
        assert (rules_dir / "guide-2.md").exists()

    def test_rename_with_all_component_types(self, package_builder, test_project: Path) -> None:
        """Test RENAME works with all component types."""
        # Install package
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1"}],
            hooks=[{"name": "pre-commit", "content": "#!/bin/bash\necho 'v1'\n"}],
            commands=[{"name": "test", "content": "#!/bin/bash\necho 'test v1'\n"}],
        )
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # Reinstall with RENAME
        pkg_v2 = package_builder(
            name="test-pkg",
            version="2.0.0",
            instructions=[{"name": "guide", "content": "# v2"}],
            hooks=[{"name": "pre-commit", "content": "#!/bin/bash\necho 'v2'\n"}],
            commands=[{"name": "test", "content": "#!/bin/bash\necho 'test v2'\n"}],
        )

        result = install_package(
            pkg_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.RENAME,
        )

        assert result.success is True

        # Verify original files preserved
        assert (test_project / ".claude/rules/guide.md").exists()
        assert (test_project / ".claude/hooks/pre-commit.sh").exists()
        assert (test_project / ".claude/commands/test.sh").exists()

        # Verify numbered copies created
        assert (test_project / ".claude/rules/guide-1.md").exists()
        assert (test_project / ".claude/hooks/pre-commit-1.sh").exists()
        assert (test_project / ".claude/commands/test-1.sh").exists()

    def test_rename_preserves_permissions(self, package_builder, test_project: Path) -> None:
        """Test that RENAME preserves executable permissions for scripts."""
        # Install package with hook
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            hooks=[{"name": "pre-commit", "content": "#!/bin/bash\necho 'v1'\n"}],
        )
        install_package(pkg, test_project, AIToolType.CLAUDE)

        # Reinstall with RENAME
        pkg_v2 = package_builder(
            name="test-pkg",
            version="2.0.0",
            hooks=[{"name": "pre-commit", "content": "#!/bin/bash\necho 'v2'\n"}],
        )

        install_package(
            pkg_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.RENAME,
        )

        # Verify both are executable (Unix-only)
        import os

        if os.name != "nt":  # Skip permission check on Windows
            original = test_project / ".claude/hooks/pre-commit.sh"
            renamed = test_project / ".claude/hooks/pre-commit-1.sh"

            assert original.stat().st_mode & 0o111  # Executable
            assert renamed.stat().st_mode & 0o111  # Executable


class TestConflictResolutionCombinations:
    """Test different conflict scenarios and strategy combinations."""

    def test_partial_conflicts_with_skip(self, package_builder, test_project: Path) -> None:
        """Test package with some conflicting and some new files with SKIP."""
        # Install v1 with 2 instructions
        pkg_v1 = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[
                {"name": "guide1", "content": "# Guide 1"},
                {"name": "guide2", "content": "# Guide 2"},
            ],
        )
        install_package(pkg_v1, test_project, AIToolType.CLAUDE)

        # Modify one file
        (test_project / ".claude/rules/guide1.md").write_text("# Modified")

        # Install v2 with 3 instructions (guide1 updated, guide2 same, guide3 new)
        pkg_v2 = package_builder(
            name="test-pkg",
            version="2.0.0",
            instructions=[
                {"name": "guide1", "content": "# Guide 1 Updated"},
                {"name": "guide2", "content": "# Guide 2"},
                {"name": "guide3", "content": "# Guide 3 New"},
            ],
        )

        result = install_package(
            pkg_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.SKIP,
        )

        assert result.success is True

        # guide1: skipped (modified)
        assert "# Modified" in (test_project / ".claude/rules/guide1.md").read_text()

        # guide2: could be skipped or overwritten (depends on checksum)
        assert (test_project / ".claude/rules/guide2.md").exists()

        # guide3: installed (new)
        assert (test_project / ".claude/rules/guide3.md").exists()
        assert "Guide 3 New" in (test_project / ".claude/rules/guide3.md").read_text()

    def test_no_conflicts_all_strategies_identical(self, package_builder, test_project: Path) -> None:
        """Test that all strategies work identically when there are no conflicts."""
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Guide"}],
        )

        # Test with each strategy
        for strategy in [ConflictResolution.SKIP, ConflictResolution.OVERWRITE, ConflictResolution.RENAME]:
            # Clean project
            import shutil

            claude_dir = test_project / ".claude"
            aikit_dir = test_project / ".ai-config-kit"
            if claude_dir.exists():
                shutil.rmtree(claude_dir)
            if aikit_dir.exists():
                shutil.rmtree(aikit_dir)

            # Install with strategy
            result = install_package(
                pkg,
                test_project,
                AIToolType.CLAUDE,
                conflict_resolution=strategy,
            )

            assert result.success is True
            assert (test_project / ".claude/rules/guide.md").exists()

    def test_changing_strategies_between_installs(self, package_builder, test_project: Path) -> None:
        """Test using different strategies for different installs."""
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Original"}],
        )

        # Install with SKIP
        install_package(
            pkg,
            test_project,
            AIToolType.CLAUDE,
            conflict_resolution=ConflictResolution.SKIP,
        )

        # Modify
        (test_project / ".claude/rules/guide.md").write_text("# Modified")

        # Reinstall with RENAME
        pkg_v2 = package_builder(
            name="test-pkg",
            version="1.1.0",
            instructions=[{"name": "guide", "content": "# v1.1"}],
        )

        install_package(
            pkg_v2,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.RENAME,
        )

        # Should have both files
        assert (test_project / ".claude/rules/guide.md").exists()
        assert (test_project / ".claude/rules/guide-1.md").exists()

        # Reinstall with OVERWRITE
        pkg_v3 = package_builder(
            name="test-pkg",
            version="1.2.0",
            instructions=[{"name": "guide", "content": "# v1.2"}],
        )

        install_package(
            pkg_v3,
            test_project,
            AIToolType.CLAUDE,
            force=True,
            conflict_resolution=ConflictResolution.OVERWRITE,
        )

        # guide.md should be overwritten
        assert "# v1.2" in (test_project / ".claude/rules/guide.md").read_text()

        # guide-1.md should still exist
        assert (test_project / ".claude/rules/guide-1.md").exists()
