"""Tests for Winsurf AI tool integration."""

import pytest

from aiconfigkit.ai_tools.winsurf import WinsurfTool
from aiconfigkit.core.models import AIToolType, InstallationScope, Instruction


@pytest.fixture
def winsurf_tool():
    """Create a Winsurf tool instance."""
    return WinsurfTool()


@pytest.fixture
def mock_winsurf_installed(monkeypatch, temp_dir):
    """Mock Windsurf as installed."""
    import os

    home_dir = temp_dir / "home"
    home_dir.mkdir(parents=True)

    # Create platform-specific directory structure
    if os.name == "nt":  # Windows
        winsurf_dir = home_dir / "AppData" / "Roaming" / "Windsurf" / "User" / "globalStorage"
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            winsurf_dir = home_dir / "Library" / "Application Support" / "Windsurf" / "User" / "globalStorage"
        else:  # Linux
            winsurf_dir = home_dir / ".config" / "Windsurf" / "User" / "globalStorage"
    else:
        raise OSError(f"Unsupported operating system: {os.name}")

    winsurf_dir.mkdir(parents=True)

    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
    return winsurf_dir


class TestWinsurfTool:
    """Test suite for WinsurfTool."""

    def test_tool_type(self, winsurf_tool):
        """Test tool type property."""
        assert winsurf_tool.tool_type == AIToolType.WINSURF

    def test_tool_name(self, winsurf_tool):
        """Test tool name property."""
        assert winsurf_tool.tool_name == "Windsurf"

    def test_is_installed_when_present(self, winsurf_tool, mock_winsurf_installed):
        """Test is_installed returns True when Windsurf is present."""
        assert winsurf_tool.is_installed() is True

    def test_is_installed_when_absent(self, temp_dir, monkeypatch):
        """Test is_installed returns False when Windsurf is not present."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
        winsurf_tool = WinsurfTool()
        assert winsurf_tool.is_installed() is False

    def test_is_installed_handles_exception(self, monkeypatch):
        """Test is_installed handles exceptions gracefully."""

        def raise_error():
            raise RuntimeError("Test error")

        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", raise_error)
        winsurf_tool = WinsurfTool()
        assert winsurf_tool.is_installed() is False

    def test_get_instructions_directory_raises_not_implemented(self, winsurf_tool):
        """Test get_instructions_directory raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            winsurf_tool.get_instructions_directory()

        assert "global installation is not supported" in str(exc_info.value).lower()

    def test_get_instruction_file_extension(self, winsurf_tool):
        """Test instruction file extension."""
        assert winsurf_tool.get_instruction_file_extension() == ".md"

    def test_get_project_instructions_directory(self, winsurf_tool, temp_dir):
        """Test project instructions directory."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instructions_dir = winsurf_tool.get_project_instructions_directory(project_root)

        assert instructions_dir == project_root / ".windsurf" / "rules"
        assert instructions_dir.exists()

    def test_install_instruction(self, winsurf_tool, temp_dir):
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

        path = winsurf_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        assert path.exists()
        assert path.read_text() == "Test content"
        assert path.suffix == ".md"

    def test_get_mcp_config_path(self, winsurf_tool):
        """Test get_mcp_config_path returns correct path."""
        config_path = winsurf_tool.get_mcp_config_path()
        # Should return a Path object pointing to Windsurf MCP config
        assert config_path is not None
        assert "windsurf" in str(config_path).lower()

    def test_repr(self, winsurf_tool):
        """Test string representation."""
        repr_str = repr(winsurf_tool)
        assert "WinsurfTool" in repr_str
        assert AIToolType.WINSURF.value in repr_str
