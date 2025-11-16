"""Tests for AITool base class."""

import os
from pathlib import Path

import pytest

from aiconfigkit.ai_tools.base import AITool
from aiconfigkit.core.models import AIToolType, InstallationScope, Instruction


class MockAITool(AITool):
    """Mock AI tool for testing base class."""

    def __init__(self, installed=True, can_write=True):
        self._installed = installed
        self._can_write = can_write

    @property
    def tool_type(self) -> AIToolType:
        return AIToolType.CURSOR

    @property
    def tool_name(self) -> str:
        return "Mock Tool"

    def is_installed(self) -> bool:
        return self._installed

    def get_instructions_directory(self) -> Path:
        return Path("/mock/instructions")

    def get_instruction_file_extension(self) -> str:
        return ".md"

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        return project_root / ".mock" / "instructions"


class TestAIToolBase:
    """Test suite for AITool base class."""

    def test_get_instruction_path_global(self, temp_dir):
        """Test get_instruction_path for global scope."""
        tool = MockAITool()
        path = tool.get_instruction_path("test", InstallationScope.GLOBAL)
        assert path == Path("/mock/instructions/test.md")

    def test_get_instruction_path_project(self, temp_dir):
        """Test get_instruction_path for project scope."""
        tool = MockAITool()
        project_root = temp_dir / "project"
        path = tool.get_instruction_path("test", InstallationScope.PROJECT, project_root)
        assert path == project_root / ".mock" / "instructions" / "test.md"

    def test_get_instruction_path_project_requires_root(self):
        """Test get_instruction_path raises ValueError without project_root."""
        tool = MockAITool()
        with pytest.raises(ValueError) as exc_info:
            tool.get_instruction_path("test", InstallationScope.PROJECT)
        assert "project_root is required" in str(exc_info.value)

    def test_instruction_exists_false(self, temp_dir):
        """Test instruction_exists returns False for non-existent file."""
        tool = MockAITool()
        project_root = temp_dir / "project"
        project_root.mkdir()
        assert tool.instruction_exists("nonexistent", InstallationScope.PROJECT, project_root) is False

    def test_instruction_exists_handles_exceptions(self):
        """Test instruction_exists handles exceptions gracefully."""
        tool = MockAITool()
        # No project_root with PROJECT scope should return False
        assert tool.instruction_exists("test", InstallationScope.PROJECT) is False

    def test_install_instruction_creates_directory(self, temp_dir):
        """Test install_instruction creates directory if needed."""
        tool = MockAITool()
        project_root = temp_dir / "project"
        project_root.mkdir()

        instruction = Instruction(
            name="test",
            description="Test",
            content="Test content",
            file_path="test.md",
        )

        path = tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        assert path.exists()
        assert path.parent.exists()
        assert path.read_text() == "Test content"

    def test_install_instruction_raises_file_exists(self, temp_dir):
        """Test install_instruction raises FileExistsError."""
        tool = MockAITool()
        project_root = temp_dir / "project"
        instructions_dir = project_root / ".mock" / "instructions"
        instructions_dir.mkdir(parents=True)

        # Create existing file
        (instructions_dir / "test.md").write_text("Old content")

        instruction = Instruction(
            name="test",
            description="Test",
            content="New content",
            file_path="test.md",
        )

        with pytest.raises(FileExistsError):
            tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

    def test_uninstall_instruction_returns_false_for_nonexistent(self, temp_dir):
        """Test uninstall_instruction returns False for non-existent file."""
        tool = MockAITool()
        project_root = temp_dir / "project"
        project_root.mkdir()

        result = tool.uninstall_instruction("nonexistent", InstallationScope.PROJECT, project_root)
        assert result is False

    def test_uninstall_instruction_handles_exceptions(self):
        """Test uninstall_instruction handles exceptions gracefully."""
        tool = MockAITool()
        # No project_root with PROJECT scope should return False
        result = tool.uninstall_instruction("test", InstallationScope.PROJECT)
        assert result is False

    def test_validate_installation_not_installed(self):
        """Test validate_installation returns error when not installed."""
        tool = MockAITool(installed=False)
        error = tool.validate_installation()
        assert error is not None
        assert "not installed" in error.lower()

    def test_validate_installation_creates_directory(self, temp_dir, monkeypatch):
        """Test validate_installation creates directory if needed."""
        monkeypatch.chdir(temp_dir)
        instructions_dir = temp_dir / "mock_instructions"

        class TestTool(MockAITool):
            def get_instructions_directory(self) -> Path:
                return instructions_dir

        tool = TestTool()
        error = tool.validate_installation()

        assert error is None
        assert instructions_dir.exists()

    def test_validate_installation_checks_write_permission(self, temp_dir, monkeypatch):
        """Test validate_installation checks write permission."""
        monkeypatch.chdir(temp_dir)
        instructions_dir = temp_dir / "mock_instructions"
        instructions_dir.mkdir()

        # Mock os.access to return False for write permission
        original_access = os.access

        def mock_access(path, mode):
            if mode == os.W_OK and str(path) == str(instructions_dir):
                return False
            return original_access(path, mode)

        monkeypatch.setattr(os, "access", mock_access)

        class TestTool(MockAITool):
            def get_instructions_directory(self) -> Path:
                return instructions_dir

        tool = TestTool()
        error = tool.validate_installation()

        assert error is not None
        assert "No write permission" in error

    def test_validate_installation_handles_exception(self, monkeypatch):
        """Test validate_installation handles exceptions."""

        class ErrorTool(MockAITool):
            def get_instructions_directory(self) -> Path:
                raise RuntimeError("Test error")

        tool = ErrorTool()
        error = tool.validate_installation()

        assert error is not None
        assert "Error accessing" in error

    def test_repr(self):
        """Test string representation."""
        tool = MockAITool()
        repr_str = repr(tool)
        assert "MockAITool" in repr_str
        assert AIToolType.CURSOR.value in repr_str

    def test_get_mcp_config_path_not_implemented(self):
        """Test get_mcp_config_path raises NotImplementedError by default."""
        tool = MockAITool()
        with pytest.raises(NotImplementedError) as exc_info:
            tool.get_mcp_config_path()
        assert "does not support MCP server configuration" in str(exc_info.value)
