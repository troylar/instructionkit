"""Additional tests for package installation to increase code coverage."""

from pathlib import Path

import pytest

from aiconfigkit.cli.package_install import (
    _filter_components_by_capability,
    _install_command_component,
    _install_hook_component,
    _install_mcp_component,
    _install_resource_component,
)
from aiconfigkit.ai_tools.capability_registry import get_capability
from aiconfigkit.ai_tools.translator import get_translator
from aiconfigkit.core.models import (
    AIToolType,
    CommandComponent,
    ConflictResolution,
    HookComponent,
    MCPServerComponent,
    Package,
    PackageComponents,
    ResourceComponent,
)


class TestFilterComponentsByCapability:
    """Test component filtering by IDE capability."""

    def test_filter_all_components_for_claude(self) -> None:
        """Test that Claude Code supports all component types."""
        from aiconfigkit.core.models import InstructionComponent

        package = Package(
            name="test",
            version="1.0.0",
            description="Test",
            author="Test",
            namespace="test/test",
            license="MIT",
            components=PackageComponents(
                instructions=[InstructionComponent(name="i1", file="f1", description="d1")],
                mcp_servers=[MCPServerComponent(name="m1", file="mf1", description="md1")],
                hooks=[HookComponent(name="h1", file="hf1", description="hd1", hook_type="pre-commit")],
                commands=[CommandComponent(name="c1", file="cf1", description="cd1", command_type="shell")],
                resources=[
                    ResourceComponent(
                        name="r1", file="rf1", description="rd1", install_path="r1", checksum="sha256:abc", size=100
                    )
                ],
            ),
        )

        capability = get_capability(AIToolType.CLAUDE)
        filtered = _filter_components_by_capability(package, capability)

        assert len(filtered["instructions"]) == 1
        assert len(filtered["mcp_servers"]) == 1
        assert len(filtered["hooks"]) == 1
        assert len(filtered["commands"]) == 1
        assert len(filtered["resources"]) == 1

    def test_filter_components_for_cursor(self) -> None:
        """Test that Cursor only supports instructions and resources."""
        from aiconfigkit.core.models import InstructionComponent

        package = Package(
            name="test",
            version="1.0.0",
            description="Test",
            author="Test",
            namespace="test/test",
            license="MIT",
            components=PackageComponents(
                instructions=[InstructionComponent(name="i1", file="f1", description="d1")],
                mcp_servers=[MCPServerComponent(name="m1", file="mf1", description="md1")],
                hooks=[HookComponent(name="h1", file="hf1", description="hd1", hook_type="pre-commit")],
                commands=[CommandComponent(name="c1", file="cf1", description="cd1", command_type="shell")],
                resources=[
                    ResourceComponent(
                        name="r1", file="rf1", description="rd1", install_path="r1", checksum="sha256:abc", size=100
                    )
                ],
            ),
        )

        capability = get_capability(AIToolType.CURSOR)
        filtered = _filter_components_by_capability(package, capability)

        assert len(filtered["instructions"]) == 1
        assert len(filtered.get("mcp_servers", [])) == 0
        assert len(filtered.get("hooks", [])) == 0
        assert len(filtered.get("commands", [])) == 0
        assert len(filtered["resources"]) == 1


class TestComponentInstallation:
    """Test individual component installation functions."""

    @pytest.fixture
    def temp_package(self, tmp_path: Path) -> Path:
        """Create a temporary package directory."""
        pkg_path = tmp_path / "package"
        pkg_path.mkdir()

        # Create component files
        (pkg_path / "mcp").mkdir()
        (pkg_path / "mcp/test.json").write_text('{"mcpServers": {}}')

        (pkg_path / "hooks").mkdir()
        (pkg_path / "hooks/test.sh").write_text("#!/bin/bash\necho test")

        (pkg_path / "commands").mkdir()
        (pkg_path / "commands/test.sh").write_text("#!/bin/bash\necho test")

        (pkg_path / "resources").mkdir()
        (pkg_path / "resources/test.txt").write_text("test content")

        return pkg_path

    @pytest.fixture
    def temp_project(self, tmp_path: Path) -> Path:
        """Create a temporary project directory."""
        project = tmp_path / "project"
        project.mkdir()
        return project

    def test_install_mcp_with_overwrite(
        self, temp_package: Path, temp_project: Path
    ) -> None:
        """Test MCP installation with OVERWRITE conflict resolution."""
        component = MCPServerComponent(name="test", file="mcp/test.json", description="Test")
        translator = get_translator(AIToolType.CLAUDE)

        # Create existing file
        existing_file = temp_project / ".claude/mcp/test.json"
        existing_file.parent.mkdir(parents=True, exist_ok=True)
        existing_file.write_text('{"old": "content"}')

        # Install with overwrite
        result = _install_mcp_component(
            component, temp_package, temp_project, translator, ConflictResolution.OVERWRITE
        )

        assert result is not None
        assert result.name == "test"
        # New content should overwrite old
        assert existing_file.read_text() == '{"mcpServers": {}}'

    def test_install_hook_with_rename(
        self, temp_package: Path, temp_project: Path
    ) -> None:
        """Test hook installation with RENAME conflict resolution."""
        component = HookComponent(name="test", file="hooks/test.sh", description="Test", hook_type="pre-commit")
        translator = get_translator(AIToolType.CLAUDE)

        # Create existing file
        existing_file = temp_project / ".claude/hooks/test.sh"
        existing_file.parent.mkdir(parents=True, exist_ok=True)
        existing_file.write_text("old content")

        # Install with rename
        result = _install_hook_component(
            component, temp_package, temp_project, translator, ConflictResolution.RENAME
        )

        assert result is not None
        # Should create numbered copy
        renamed_file = temp_project / ".claude/hooks/test-1.sh"
        assert renamed_file.exists()
        assert existing_file.read_text() == "old content"  # Original preserved

    def test_install_command_error_handling(
        self, temp_package: Path, temp_project: Path
    ) -> None:
        """Test command installation error handling."""
        # Component with non-existent file
        component = CommandComponent(
            name="missing", file="commands/missing.sh", description="Missing", command_type="shell"
        )
        translator = get_translator(AIToolType.CLAUDE)

        result = _install_command_component(
            component, temp_package, temp_project, translator, ConflictResolution.SKIP
        )

        # Should return None on error
        assert result is None

    def test_install_resource_with_skip(
        self, temp_package: Path, temp_project: Path
    ) -> None:
        """Test resource installation with SKIP conflict resolution."""
        component = ResourceComponent(
            name="test",
            file="resources/test.txt",
            description="Test",
            install_path=".testfile",
            checksum="sha256:abc",
            size=100,
        )
        translator = get_translator(AIToolType.CLAUDE)

        # Create existing file
        existing_file = temp_project / ".testfile"
        existing_file.write_text("existing content")

        # Install with skip
        result = _install_resource_component(
            component, temp_package, temp_project, translator, ConflictResolution.SKIP
        )

        # Should return None (skipped)
        assert result is None
        # Original file preserved
        assert existing_file.read_text() == "existing content"

    def test_install_resource_without_source_path(
        self, temp_package: Path, temp_project: Path
    ) -> None:
        """Test resource installation fallback when no source_path in metadata."""
        from unittest.mock import MagicMock
        from aiconfigkit.ai_tools.translator import TranslatedComponent

        component = ResourceComponent(
            name="test",
            file="resources/test.txt",
            description="Test",
            install_path=".testfile",
            checksum="sha256:abc",
            size=100,
        )

        # Create mock translator that returns TranslatedComponent without source_path
        from aiconfigkit.core.models import ComponentType

        translator = MagicMock()
        translator.translate_resource.return_value = TranslatedComponent(
            component_type=ComponentType.RESOURCE,
            component_name="test",
            target_path=".testfile",
            content="test content",
            metadata={}  # No source_path - triggers fallback
        )

        # Install resource
        result = _install_resource_component(
            component, temp_package, temp_project, translator, ConflictResolution.OVERWRITE
        )

        # Should install successfully using content fallback
        assert result is not None
        assert result.name == "test"
        # File should contain the content
        installed_file = temp_project / ".testfile"
        assert installed_file.exists()
        assert installed_file.read_text() == "test content"
