"""Comprehensive E2E tests covering IDE compatibility, edge cases, errors, and workflows."""

import os
import subprocess
from pathlib import Path

import pytest

from aiconfigkit.cli.package_install import install_package
from aiconfigkit.core.models import AIToolType, ConflictResolution, InstallationScope
from aiconfigkit.storage.package_tracker import PackageTracker


class TestIDECompatibility:
    """Test package installation across different IDEs."""

    def test_claude_code_installs_all_components(self, package_builder, test_project: Path) -> None:
        """Test that Claude Code installs all component types."""
        pkg = package_builder(
            name="complete-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Guide"}],
            mcp_servers=[{"name": "filesystem", "description": "FS"}],
            hooks=[{"name": "pre-commit", "content": "#!/bin/bash\necho 'hook'\n"}],
            commands=[{"name": "test", "content": "#!/bin/bash\necho 'test'\n"}],
            resources=[{"name": ".gitignore", "content": "*.pyc"}],
        )

        result = install_package(pkg, test_project, AIToolType.CLAUDE)

        assert result.success is True
        assert result.installed_count == 5  # All components

        # Verify files
        assert (test_project / ".claude/rules/guide.md").exists()
        assert (test_project / ".claude/mcp/filesystem.json").exists()
        assert (test_project / ".claude/hooks/pre-commit.sh").exists()
        assert (test_project / ".claude/commands/test.sh").exists()
        assert (test_project / ".gitignore").exists()

    def test_cursor_filters_unsupported_components(self, package_builder, test_project: Path) -> None:
        """Test that Cursor only installs instructions and resources."""
        pkg = package_builder(
            name="complete-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Guide"}],
            mcp_servers=[{"name": "filesystem", "description": "FS"}],
            hooks=[{"name": "pre-commit", "content": "#!/bin/bash\n"}],
            commands=[{"name": "test", "content": "#!/bin/bash\n"}],
            resources=[{"name": ".editorconfig", "content": "root = true"}],
        )

        result = install_package(pkg, test_project, AIToolType.CURSOR)

        assert result.success is True
        # Only instructions and resources installed
        assert result.installed_count == 2
        # MCP, hooks, commands filtered
        assert result.skipped_count == 3

        # Verify only supported components installed
        assert (test_project / ".cursor/rules/guide.mdc").exists()  # Note: .mdc extension
        assert (test_project / ".editorconfig").exists()

        # Unsupported not installed
        assert not (test_project / ".cursor/mcp").exists()
        assert not (test_project / ".cursor/hooks").exists()
        assert not (test_project / ".cursor/commands").exists()

    def test_cursor_uses_mdc_extension(self, package_builder, test_project: Path) -> None:
        """Test that Cursor installs instructions with .mdc extension."""
        pkg = package_builder(
            name="cursor-pkg",
            version="1.0.0",
            instructions=[
                {"name": "style", "content": "# Style"},
                {"name": "testing", "content": "# Testing"},
            ],
        )

        result = install_package(pkg, test_project, AIToolType.CURSOR)

        assert result.success is True

        # Verify .mdc extension
        assert (test_project / ".cursor/rules/style.mdc").exists()
        assert (test_project / ".cursor/rules/testing.mdc").exists()

        # Not .md
        assert not (test_project / ".cursor/rules/style.md").exists()

    def test_windsurf_filters_correctly(self, package_builder, test_project: Path) -> None:
        """Test that Windsurf filters components correctly."""
        pkg = package_builder(
            name="windsurf-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Guide"}],
            mcp_servers=[{"name": "fs", "description": "FS"}],
            hooks=[{"name": "hook", "content": "#!/bin/bash\n"}],
            commands=[{"name": "cmd", "content": "#!/bin/bash\n"}],
            resources=[{"name": ".env.example", "content": "API_KEY="}],
        )

        result = install_package(pkg, test_project, AIToolType.WINSURF)

        assert result.success is True
        # Instructions and resources only
        assert result.installed_count == 2

        # Verify paths
        assert (test_project / ".windsurf/rules/guide.md").exists()
        assert (test_project / ".env.example").exists()

    def test_github_copilot_instructions_only(self, package_builder, test_project: Path) -> None:
        """Test that GitHub Copilot only supports instructions."""
        pkg = package_builder(
            name="copilot-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Guide"}],
            resources=[{"name": ".editorconfig", "content": "root"}],
            hooks=[{"name": "hook", "content": "#!/bin/bash\n"}],
        )

        result = install_package(pkg, test_project, AIToolType.COPILOT)

        assert result.success is True
        # Only instructions
        assert result.installed_count == 1
        assert result.skipped_count == 2

        # Verify path (.github/instructions/)
        assert (test_project / ".github/instructions/guide.md").exists()

        # Others not installed
        assert not (test_project / ".editorconfig").exists()

    def test_same_package_different_ides(self, package_builder, tmp_path: Path) -> None:
        """Test installing the same package to projects using different IDEs."""
        pkg = package_builder(
            name="universal-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Guide"}],
            mcp_servers=[{"name": "fs", "description": "FS"}],
        )

        # Create four projects for different IDEs
        claude_project = tmp_path / "claude"
        cursor_project = tmp_path / "cursor"
        windsurf_project = tmp_path / "windsurf"
        copilot_project = tmp_path / "copilot"

        for proj in [claude_project, cursor_project, windsurf_project, copilot_project]:
            proj.mkdir()

        # Install to each
        claude_result = install_package(pkg, claude_project, AIToolType.CLAUDE)
        cursor_result = install_package(pkg, cursor_project, AIToolType.CURSOR)
        windsurf_result = install_package(pkg, windsurf_project, AIToolType.WINSURF)
        copilot_result = install_package(pkg, copilot_project, AIToolType.COPILOT)

        # Claude gets everything
        assert claude_result.installed_count == 2  # instruction + mcp

        # Others filter MCP
        assert cursor_result.installed_count == 1  # instruction only
        assert windsurf_result.installed_count == 1
        assert copilot_result.installed_count == 1

        # Verify paths
        assert (claude_project / ".claude/rules/guide.md").exists()
        assert (cursor_project / ".cursor/rules/guide.mdc").exists()
        assert (windsurf_project / ".windsurf/rules/guide.md").exists()
        assert (copilot_project / ".github/instructions/guide.md").exists()


class TestEdgeCases:
    """Test edge cases and unusual scenarios."""

    def test_package_with_very_long_names(self, package_builder, test_project: Path) -> None:
        """Test package and component with very long names."""
        long_instruction_name = "a" * 50  # 50 character name

        pkg = package_builder(
            name="long-package",
            version="1.0.0",
            instructions=[{"name": long_instruction_name, "content": "# Long"}],
        )

        result = install_package(pkg, test_project, AIToolType.CLAUDE)

        assert result.success is True
        assert (test_project / f".claude/rules/{long_instruction_name}.md").exists()

    def test_package_with_many_components(self, package_builder, test_project: Path) -> None:
        """Test package with large number of components."""
        # Create 50 instructions
        instructions = [{"name": f"guide-{i:02d}", "content": f"# Guide {i}"} for i in range(50)]

        pkg = package_builder(
            name="large-pkg",
            version="1.0.0",
            instructions=instructions,
        )

        result = install_package(pkg, test_project, AIToolType.CLAUDE)

        assert result.success is True
        assert result.installed_count == 50

        # Verify all installed
        for i in range(50):
            assert (test_project / f".claude/rules/guide-{i:02d}.md").exists()

    @pytest.mark.skipif(os.name == "nt", reason="Unicode encoding issues on Windows")
    def test_package_with_special_characters_in_content(self, package_builder, test_project: Path) -> None:
        """Test package with special characters and unicode in content."""
        content = """# Guide with Special Characters

## Symbols
- © Copyright
- ™ Trademark
- ® Registered
- € Euro
- ¥ Yen

## Code blocks
```python
def hello():
    print("Hello, 世界!")  # Unicode
```

## Emojis
🚀 🎯 ✨ 💡 📦
"""

        pkg = package_builder(
            name="special-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": content}],
        )

        result = install_package(pkg, test_project, AIToolType.CLAUDE)

        assert result.success is True

        installed_content = (test_project / ".claude/rules/guide.md").read_text()
        assert "世界" in installed_content
        assert "🚀" in installed_content
        assert "©" in installed_content

    def test_empty_package_no_components(self, test_project: Path, tmp_path: Path) -> None:
        """Test package with valid manifest but no components."""
        # Create minimal package
        pkg_path = tmp_path / "empty-pkg"
        pkg_path.mkdir()

        (pkg_path / "ai-config-kit-package.yaml").write_text(
            """name: empty-pkg
version: 1.0.0
description: Empty package
author: Test
namespace: test/empty
license: MIT

components:
"""
        )

        # Should succeed but install nothing
        result = install_package(pkg_path, test_project, AIToolType.CLAUDE)
        assert result.success is True
        assert result.installed_count == 0

    def test_package_with_nested_directory_structures(
        self, package_builder, test_project: Path, tmp_path: Path
    ) -> None:
        """Test package with deeply nested directory structures."""
        pkg_path = tmp_path / "nested-pkg"
        pkg_path.mkdir()

        # Create nested structure
        (pkg_path / "instructions/deep/nested/path").mkdir(parents=True)
        (pkg_path / "instructions/deep/nested/path/guide.md").write_text("# Deep")

        (pkg_path / "ai-config-kit-package.yaml").write_text(
            """name: nested-pkg
version: 1.0.0
description: Nested package
author: Test
namespace: test/nested
license: MIT

components:
  instructions:
    - name: deep-guide
      description: Deeply nested guide
      file: instructions/deep/nested/path/guide.md
      tags: [nested]
"""
        )

        result = install_package(pkg_path, test_project, AIToolType.CLAUDE)

        assert result.success is True
        assert (test_project / ".claude/rules/deep-guide.md").exists()

    def test_package_with_binary_resource_content(self, package_builder, test_project: Path, tmp_path: Path) -> None:
        """Test package with binary file as resource."""
        pkg_path = tmp_path / "binary-pkg"
        pkg_path.mkdir()
        (pkg_path / "resources").mkdir()

        # Create a small binary file (PNG-like header)
        binary_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        (pkg_path / "resources/icon.png").write_bytes(binary_data)

        # Calculate checksum
        import hashlib

        checksum = hashlib.sha256(binary_data).hexdigest()

        (pkg_path / "ai-config-kit-package.yaml").write_text(
            f"""name: binary-pkg
version: 1.0.0
description: Package with binary
author: Test
namespace: test/binary
license: MIT

components:
  resources:
    - name: icon
      description: Icon file
      file: resources/icon.png
      install_path: assets/icon.png
      checksum: sha256:{checksum}
      size: {len(binary_data)}
      tags: [binary]
"""
        )

        result = install_package(pkg_path, test_project, AIToolType.CLAUDE)

        assert result.success is True

        installed_file = test_project / "assets/icon.png"
        assert installed_file.exists()
        assert installed_file.read_bytes() == binary_data


class TestErrorHandling:
    """Test error handling and validation."""

    def test_missing_manifest_file(self, test_project: Path, tmp_path: Path) -> None:
        """Test installing from directory without manifest."""
        empty_dir = tmp_path / "no-manifest"
        empty_dir.mkdir()

        result = install_package(empty_dir, test_project, AIToolType.CLAUDE)

        assert result.success is False
        assert "manifest" in result.error_message.lower()

    def test_invalid_manifest_yaml(self, test_project: Path, tmp_path: Path) -> None:
        """Test manifest with invalid YAML syntax."""
        pkg_path = tmp_path / "invalid-yaml"
        pkg_path.mkdir()

        (pkg_path / "ai-config-kit-package.yaml").write_text(
            """name: test
version: 1.0.0
description: Test
  invalid yaml syntax here
author: Test
"""
        )

        result = install_package(pkg_path, test_project, AIToolType.CLAUDE)

        assert result.success is False
        assert result.error_message is not None

    def test_missing_required_manifest_fields(self, test_project: Path, tmp_path: Path) -> None:
        """Test manifest missing required fields."""
        pkg_path = tmp_path / "incomplete"
        pkg_path.mkdir()

        # Missing 'author' field
        (pkg_path / "ai-config-kit-package.yaml").write_text(
            """name: test
version: 1.0.0
description: Test
namespace: test/pkg
"""
        )

        result = install_package(pkg_path, test_project, AIToolType.CLAUDE)

        assert result.success is False
        assert "author" in result.error_message.lower()

    def test_component_file_does_not_exist(self, test_project: Path, tmp_path: Path) -> None:
        """Test component referencing non-existent file."""
        pkg_path = tmp_path / "missing-file"
        pkg_path.mkdir()

        (pkg_path / "ai-config-kit-package.yaml").write_text(
            """name: missing-file-pkg
version: 1.0.0
description: Test
author: Test
namespace: test/pkg
license: MIT

components:
  instructions:
    - name: nonexistent
      description: This file doesn't exist
      file: instructions/nonexistent.md
      tags: [test]
"""
        )

        result = install_package(pkg_path, test_project, AIToolType.CLAUDE)

        assert result.success is False
        assert "not found" in result.error_message.lower() or "exist" in result.error_message.lower()

    def test_invalid_version_format(self, test_project: Path, tmp_path: Path) -> None:
        """Test manifest with invalid version format."""
        pkg_path = tmp_path / "bad-version"
        pkg_path.mkdir()
        (pkg_path / "instructions").mkdir()
        (pkg_path / "instructions/guide.md").write_text("# Guide")

        (pkg_path / "ai-config-kit-package.yaml").write_text(
            """name: bad-version
version: not-a-version
description: Test
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

        result = install_package(pkg_path, test_project, AIToolType.CLAUDE)

        assert result.success is False
        assert result.error_message is not None

    def test_install_to_nonexistent_project_directory(self, package_builder, tmp_path: Path) -> None:
        """Test installing to a project directory that doesn't exist."""
        pkg = package_builder(
            name="test-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# Guide"}],
        )

        nonexistent = tmp_path / "does-not-exist"

        # Should either create directory or raise appropriate error
        # (depending on implementation)
        try:
            _result = install_package(pkg, nonexistent, AIToolType.CLAUDE)
            # If it succeeds, directory should be created
            assert nonexistent.exists()
        except Exception as e:
            # Or it should raise a clear error
            assert "not found" in str(e).lower() or "exist" in str(e).lower()


class TestRealWorldWorkflows:
    """Test realistic end-to-end workflows."""

    def test_new_developer_onboarding_workflow(self, package_builder, tmp_path: Path) -> None:
        """Simulate complete new developer onboarding."""
        # New dev clones project
        project = tmp_path / "backend-api"
        project.mkdir()

        # Company security package (would be git cloned)
        security_pkg = package_builder(
            name="company-security",
            version="1.0.0",
            instructions=[
                {"name": "security-policy", "content": "# Security policies"},
                {"name": "code-review", "content": "# Code review checklist"},
            ],
            hooks=[{"name": "pre-commit", "content": "#!/bin/bash\necho 'Security checks'\n"}],
        )

        # Backend team standards
        backend_pkg = package_builder(
            name="backend-standards",
            version="2.1.0",
            instructions=[
                {"name": "api-design", "content": "# API design"},
                {"name": "database-patterns", "content": "# DB patterns"},
            ],
            commands=[{"name": "test", "content": "#!/bin/bash\necho 'Run tests'\n"}],
        )

        # Python-specific package
        python_pkg = package_builder(
            name="python-style",
            version="1.5.0",
            instructions=[
                {"name": "pep8", "content": "# PEP 8 style"},
            ],
        )

        # Install all packages
        install_package(security_pkg, project, AIToolType.CLAUDE)
        install_package(backend_pkg, project, AIToolType.CLAUDE)
        install_package(python_pkg, project, AIToolType.CLAUDE)

        # Verify complete setup
        tracker = PackageTracker(project / ".ai-config-kit/packages.json")
        packages = tracker.get_installed_packages()

        assert len(packages) == 3
        assert {p.package_name for p in packages} == {"company-security", "backend-standards", "python-style"}

        # All files installed
        assert (project / ".claude/rules/security-policy.md").exists()
        assert (project / ".claude/rules/api-design.md").exists()
        assert (project / ".claude/rules/pep8.md").exists()
        assert (project / ".claude/hooks/pre-commit.sh").exists()
        assert (project / ".claude/commands/test.sh").exists()

    def test_team_sync_workflow(self, package_builder, tmp_path: Path) -> None:
        """Test team keeping packages in sync."""
        # Create team package repo
        team_pkg_v1 = package_builder(
            name="team-standards",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1.0"}],
            as_git=True,
        )

        # Three team members install
        dev1 = tmp_path / "dev1"
        dev2 = tmp_path / "dev2"
        dev3 = tmp_path / "dev3"

        for dev in [dev1, dev2, dev3]:
            dev.mkdir()
            install_package(team_pkg_v1, dev, AIToolType.CLAUDE)

        # Package is updated in repo
        (team_pkg_v1 / "instructions/guide.md").write_text("# v1.1\n\nUpdated")
        manifest = (team_pkg_v1 / "ai-config-kit-package.yaml").read_text()
        manifest = manifest.replace("version: 1.0.0", "version: 1.1.0")
        (team_pkg_v1 / "ai-config-kit-package.yaml").write_text(manifest)

        subprocess.run(["git", "add", "."], cwd=team_pkg_v1, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Update to 1.1.0"],
            cwd=team_pkg_v1,
            check=True,
        )

        # All team members update
        for dev in [dev1, dev2, dev3]:
            install_package(
                team_pkg_v1,
                dev,
                AIToolType.CLAUDE,
                force=True,
                conflict_resolution=ConflictResolution.OVERWRITE,
            )

        # Verify all on same version
        for dev in [dev1, dev2, dev3]:
            tracker = PackageTracker(dev / ".ai-config-kit/packages.json")
            record = tracker.get_package("team-standards", InstallationScope.PROJECT)
            assert record.version == "1.1.0"

    def test_multi_project_selective_packages(self, package_builder, tmp_path: Path) -> None:
        """Test installing different packages to different projects."""
        # Create packages
        frontend_pkg = package_builder(
            name="frontend-pkg",
            version="1.0.0",
            instructions=[{"name": "react", "content": "# React"}],
        )
        backend_pkg = package_builder(
            name="backend-pkg",
            version="1.0.0",
            instructions=[{"name": "api", "content": "# API"}],
        )
        shared_pkg = package_builder(
            name="shared-pkg",
            version="1.0.0",
            instructions=[{"name": "git", "content": "# Git"}],
        )

        # Create projects
        frontend = tmp_path / "frontend"
        backend = tmp_path / "backend"
        frontend.mkdir()
        backend.mkdir()

        # Frontend gets frontend + shared
        install_package(frontend_pkg, frontend, AIToolType.CLAUDE)
        install_package(shared_pkg, frontend, AIToolType.CLAUDE)

        # Backend gets backend + shared
        install_package(backend_pkg, backend, AIToolType.CLAUDE)
        install_package(shared_pkg, backend, AIToolType.CLAUDE)

        # Verify frontend
        fe_tracker = PackageTracker(frontend / ".ai-config-kit/packages.json")
        fe_packages = {p.package_name for p in fe_tracker.get_installed_packages()}
        assert fe_packages == {"frontend-pkg", "shared-pkg"}

        # Verify backend
        be_tracker = PackageTracker(backend / ".ai-config-kit/packages.json")
        be_packages = {p.package_name for p in be_tracker.get_installed_packages()}
        assert be_packages == {"backend-pkg", "shared-pkg"}

    def test_migration_from_manual_to_packages(self, package_builder, test_project: Path) -> None:
        """Test migrating from manual files to package management."""
        # User has manually created files
        rules_dir = test_project / ".claude/rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "my-custom-style.md").write_text("# My Custom Style\n")
        (rules_dir / "my-testing.md").write_text("# My Testing Guide\n")

        # Now install a package with SKIP to preserve custom files
        pkg = package_builder(
            name="official-standards",
            version="1.0.0",
            instructions=[
                {"name": "company-style", "content": "# Company Style"},
                {"name": "company-testing", "content": "# Company Testing"},
            ],
        )

        result = install_package(
            pkg,
            test_project,
            AIToolType.CLAUDE,
            conflict_resolution=ConflictResolution.SKIP,
        )

        assert result.success is True

        # Custom files still exist
        assert (rules_dir / "my-custom-style.md").exists()
        assert (rules_dir / "my-testing.md").exists()

        # Package files added
        assert (rules_dir / "company-style.md").exists()
        assert (rules_dir / "company-testing.md").exists()

        # Package is tracked
        tracker = PackageTracker(test_project / ".ai-config-kit/packages.json")
        assert tracker.is_package_installed("official-standards", InstallationScope.PROJECT)

    def test_cleanup_old_versions_workflow(self, package_builder, test_project: Path) -> None:
        """Test cleaning up after multiple version installs with RENAME."""
        pkg_v1 = package_builder(
            name="evolving-pkg",
            version="1.0.0",
            instructions=[{"name": "guide", "content": "# v1.0"}],
        )

        # Install v1
        install_package(pkg_v1, test_project, AIToolType.CLAUDE)

        # Install v2 and v3 with RENAME
        for version in ["2.0.0", "3.0.0"]:
            pkg = package_builder(
                name="evolving-pkg",
                version=version,
                instructions=[{"name": "guide", "content": f"# v{version}"}],
            )
            install_package(
                pkg,
                test_project,
                AIToolType.CLAUDE,
                force=True,
                conflict_resolution=ConflictResolution.RENAME,
            )

        # Should have guide.md, guide-1.md, guide-2.md
        rules_dir = test_project / ".claude/rules"
        assert (rules_dir / "guide.md").exists()
        assert (rules_dir / "guide-1.md").exists()
        assert (rules_dir / "guide-2.md").exists()

        # Clean up old versions
        (rules_dir / "guide-1.md").unlink()
        (rules_dir / "guide-2.md").unlink()

        # Only latest remains
        assert (rules_dir / "guide.md").exists()
        assert not (rules_dir / "guide-1.md").exists()
