"""Tests for GitHub Copilot AI tool integration."""

import pytest

from aiconfigkit.ai_tools.copilot import CopilotTool
from aiconfigkit.core.models import AIToolType, InstallationScope, Instruction


@pytest.fixture
def copilot_tool():
    """Create a Copilot tool instance."""
    return CopilotTool()


@pytest.fixture
def mock_copilot_installed(monkeypatch, temp_dir):
    """Mock GitHub Copilot as installed."""
    import os

    home_dir = temp_dir / "home"
    home_dir.mkdir(parents=True)

    # Create platform-specific directory structure
    if os.name == "nt":  # Windows
        copilot_dir = home_dir / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "github.copilot"
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            copilot_dir = (
                home_dir / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "github.copilot"
            )
        else:  # Linux
            copilot_dir = home_dir / ".config" / "Code" / "User" / "globalStorage" / "github.copilot"
    else:
        raise OSError(f"Unsupported operating system: {os.name}")

    copilot_dir.mkdir(parents=True)

    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
    return copilot_dir


class TestCopilotTool:
    """Test suite for CopilotTool."""

    def test_tool_type(self, copilot_tool):
        """Test tool type property."""
        assert copilot_tool.tool_type == AIToolType.COPILOT

    def test_tool_name(self, copilot_tool):
        """Test tool name property."""
        assert copilot_tool.tool_name == "GitHub Copilot"

    def test_is_installed_when_present(self, copilot_tool, mock_copilot_installed):
        """Test is_installed returns True when Copilot is present."""
        assert copilot_tool.is_installed() is True

    def test_is_installed_when_absent(self, temp_dir, monkeypatch):
        """Test is_installed returns False when Copilot is not present."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
        copilot_tool = CopilotTool()
        assert copilot_tool.is_installed() is False

    def test_is_installed_handles_exception(self, monkeypatch):
        """Test is_installed handles exceptions gracefully."""

        def raise_error():
            raise RuntimeError("Test error")

        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", raise_error)
        copilot_tool = CopilotTool()
        assert copilot_tool.is_installed() is False

    def test_get_instructions_directory_raises_not_implemented(self, copilot_tool):
        """Test get_instructions_directory raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            copilot_tool.get_instructions_directory()

        assert "global installation is not supported" in str(exc_info.value).lower()

    def test_get_instruction_file_extension(self, copilot_tool):
        """Test instruction file extension."""
        assert copilot_tool.get_instruction_file_extension() == ".instructions.md"

    def test_get_project_instructions_directory(self, copilot_tool, temp_dir):
        """Test project instructions directory."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instructions_dir = copilot_tool.get_project_instructions_directory(project_root)

        assert instructions_dir == project_root / ".github" / "instructions"
        assert instructions_dir.exists()

    def test_install_instruction(self, copilot_tool, temp_dir):
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

        path = copilot_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        assert path.exists()
        assert path.read_text() == "Test content"
        assert path.name.endswith(".instructions.md")

    def test_repr(self, copilot_tool):
        """Test string representation."""
        repr_str = repr(copilot_tool)
        assert "CopilotTool" in repr_str
        assert AIToolType.COPILOT.value in repr_str
