"""Tests for Cursor AI tool integration."""

import pytest

from aiconfigkit.ai_tools.cursor import CursorTool
from aiconfigkit.core.models import AIToolType, InstallationScope, Instruction


@pytest.fixture
def cursor_tool():
    """Create a Cursor tool instance."""
    return CursorTool()


@pytest.fixture
def mock_cursor_installed(monkeypatch, temp_dir):
    """Mock Cursor as installed."""
    import os

    home_dir = temp_dir / "home"
    home_dir.mkdir(parents=True)

    # Create platform-specific directory structure
    if os.name == "nt":  # Windows
        cursor_dir = home_dir / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage"
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            cursor_dir = home_dir / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage"
        else:  # Linux
            cursor_dir = home_dir / ".config" / "Cursor" / "User" / "globalStorage"
    else:
        raise OSError(f"Unsupported operating system: {os.name}")

    cursor_dir.mkdir(parents=True)

    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
    return cursor_dir


class TestCursorTool:
    """Test suite for CursorTool."""

    def test_tool_type(self, cursor_tool):
        """Test tool type property."""
        assert cursor_tool.tool_type == AIToolType.CURSOR

    def test_tool_name(self, cursor_tool):
        """Test tool name property."""
        assert cursor_tool.tool_name == "Cursor"

    def test_is_installed_when_present(self, cursor_tool, mock_cursor_installed):
        """Test is_installed returns True when Cursor is present."""
        assert cursor_tool.is_installed() is True

    def test_is_installed_when_absent(self, temp_dir, monkeypatch):
        """Test is_installed returns False when Cursor is not present."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
        cursor_tool = CursorTool()
        assert cursor_tool.is_installed() is False

    def test_is_installed_handles_exception(self, monkeypatch):
        """Test is_installed handles exceptions gracefully."""

        def raise_error():
            raise RuntimeError("Test error")

        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", raise_error)
        cursor_tool = CursorTool()
        assert cursor_tool.is_installed() is False

    def test_get_instructions_directory_raises_not_implemented(self, cursor_tool):
        """Test get_instructions_directory raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            cursor_tool.get_instructions_directory()

        assert "global installation is not supported" in str(exc_info.value).lower()

    def test_get_instruction_file_extension(self, cursor_tool):
        """Test instruction file extension."""
        assert cursor_tool.get_instruction_file_extension() == ".mdc"

    def test_get_project_instructions_directory(self, cursor_tool, temp_dir):
        """Test project instructions directory."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instructions_dir = cursor_tool.get_project_instructions_directory(project_root)

        assert instructions_dir == project_root / ".cursor" / "rules"
        assert instructions_dir.exists()

    def test_get_instruction_path_project_scope(self, cursor_tool, temp_dir):
        """Test get_instruction_path for project scope."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        path = cursor_tool.get_instruction_path(
            "test-instruction", scope=InstallationScope.PROJECT, project_root=project_root
        )

        assert path == project_root / ".cursor" / "rules" / "test-instruction.mdc"

    def test_get_instruction_path_project_scope_requires_root(self, cursor_tool):
        """Test get_instruction_path raises ValueError without project_root."""
        with pytest.raises(ValueError) as exc_info:
            cursor_tool.get_instruction_path("test-instruction", scope=InstallationScope.PROJECT)

        assert "project_root is required" in str(exc_info.value).lower()

    def test_instruction_exists(self, cursor_tool, temp_dir):
        """Test instruction_exists."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        # Create instruction
        instructions_dir = project_root / ".cursor" / "rules"
        instructions_dir.mkdir(parents=True)
        (instructions_dir / "test.mdc").write_text("test content")

        assert (
            cursor_tool.instruction_exists("test", scope=InstallationScope.PROJECT, project_root=project_root) is True
        )

        assert (
            cursor_tool.instruction_exists("nonexistent", scope=InstallationScope.PROJECT, project_root=project_root)
            is False
        )

    def test_install_instruction(self, cursor_tool, temp_dir):
        """Test install_instruction."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instruction = Instruction(
            name="test-instruction",
            description="Test",
            content="Test content",
            file_path="test.md",
            tags=[],
        )

        path = cursor_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        assert path.exists()
        assert path.read_text() == "Test content"

    def test_install_instruction_overwrite(self, cursor_tool, temp_dir):
        """Test install_instruction with overwrite."""
        project_root = temp_dir / "project"
        project_root.mkdir()
        instructions_dir = project_root / ".cursor" / "rules"
        instructions_dir.mkdir(parents=True)

        instruction = Instruction(name="test", description="Test", content="New content", file_path="test.md", tags=[])

        # Create existing file
        (instructions_dir / "test.mdc").write_text("Old content")

        # Should raise without overwrite
        with pytest.raises(FileExistsError):
            cursor_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        # Should succeed with overwrite
        path = cursor_tool.install_instruction(
            instruction, overwrite=True, scope=InstallationScope.PROJECT, project_root=project_root
        )

        assert path.read_text() == "New content"

    def test_uninstall_instruction(self, cursor_tool, temp_dir):
        """Test uninstall_instruction."""
        project_root = temp_dir / "project"
        project_root.mkdir()
        instructions_dir = project_root / ".cursor" / "rules"
        instructions_dir.mkdir(parents=True)

        # Create instruction
        (instructions_dir / "test.mdc").write_text("test")

        # Uninstall should succeed
        assert (
            cursor_tool.uninstall_instruction("test", scope=InstallationScope.PROJECT, project_root=project_root)
            is True
        )

        # Uninstalling again should return False
        assert (
            cursor_tool.uninstall_instruction("test", scope=InstallationScope.PROJECT, project_root=project_root)
            is False
        )

    def test_get_mcp_config_path(self, cursor_tool):
        """Test get_mcp_config_path returns correct path."""
        config_path = cursor_tool.get_mcp_config_path()
        # Should return a Path object pointing to Cursor MCP config
        assert config_path is not None
        assert "cursor" in str(config_path).lower()

    def test_repr(self, cursor_tool):
        """Test string representation."""
        repr_str = repr(cursor_tool)
        assert "CursorTool" in repr_str
        assert AIToolType.CURSOR.value in repr_str
