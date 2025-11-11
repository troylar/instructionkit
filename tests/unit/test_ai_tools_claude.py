"""Tests for Claude Code AI tool integration."""

import pytest

from aiconfigkit.ai_tools.claude import ClaudeTool
from aiconfigkit.core.models import AIToolType, InstallationScope, Instruction


@pytest.fixture
def claude_tool():
    """Create a Claude tool instance."""
    return ClaudeTool()


@pytest.fixture
def mock_claude_installed(monkeypatch, temp_dir):
    """Mock Claude Code as installed."""
    home_dir = temp_dir / "home"
    home_dir.mkdir(parents=True)
    claude_dir = home_dir / ".claude" / "rules"
    claude_dir.mkdir(parents=True)

    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
    return claude_dir


class TestClaudeTool:
    """Test suite for ClaudeTool."""

    def test_tool_type(self, claude_tool):
        """Test tool type property."""
        assert claude_tool.tool_type == AIToolType.CLAUDE

    def test_tool_name(self, claude_tool):
        """Test tool name property."""
        assert claude_tool.tool_name == "Claude Code"

    def test_is_installed_when_present(self, claude_tool, mock_claude_installed):
        """Test is_installed returns True when Claude is present."""
        assert claude_tool.is_installed() is True

    def test_is_installed_when_absent(self, temp_dir, monkeypatch):
        """Test is_installed returns False when Claude is not present."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
        claude_tool = ClaudeTool()
        assert claude_tool.is_installed() is False

    def test_is_installed_handles_exception(self, monkeypatch):
        """Test is_installed handles exceptions gracefully."""

        def raise_error():
            raise RuntimeError("Test error")

        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", raise_error)
        claude_tool = ClaudeTool()
        assert claude_tool.is_installed() is False

    def test_get_instructions_directory_raises_not_implemented(self, claude_tool):
        """Test get_instructions_directory raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            claude_tool.get_instructions_directory()

        assert "global installation is not supported" in str(exc_info.value).lower()

    def test_get_instruction_file_extension(self, claude_tool):
        """Test instruction file extension."""
        assert claude_tool.get_instruction_file_extension() == ".md"

    def test_get_project_instructions_directory(self, claude_tool, temp_dir):
        """Test project instructions directory."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instructions_dir = claude_tool.get_project_instructions_directory(project_root)

        assert instructions_dir == project_root / ".claude" / "rules"
        assert instructions_dir.exists()

    def test_install_instruction(self, claude_tool, temp_dir):
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

        path = claude_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        assert path.exists()
        assert path.read_text() == "Test content"
        assert path.suffix == ".md"

    def test_repr(self, claude_tool):
        """Test string representation."""
        repr_str = repr(claude_tool)
        assert "ClaudeTool" in repr_str
        assert AIToolType.CLAUDE.value in repr_str
