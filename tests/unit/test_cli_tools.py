"""Tests for CLI tools command."""

import pytest

from aiconfigkit.cli.tools import show_tools


@pytest.fixture
def mock_detector_with_tools(monkeypatch, temp_dir):
    """Mock detector with installed tools."""
    import os

    home_dir = temp_dir / "home"
    home_dir.mkdir(parents=True)

    # Create Cursor and Windsurf with platform-specific paths, leave others not installed
    if os.name == "nt":  # Windows
        cursor_dir = home_dir / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage"
        winsurf_dir = home_dir / "AppData" / "Roaming" / "Windsurf" / "User" / "globalStorage"
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            cursor_dir = home_dir / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage"
            winsurf_dir = home_dir / "Library" / "Application Support" / "Windsurf" / "User" / "globalStorage"
        else:  # Linux
            cursor_dir = home_dir / ".config" / "Cursor" / "User" / "globalStorage"
            winsurf_dir = home_dir / ".config" / "Windsurf" / "User" / "globalStorage"
    else:
        raise OSError(f"Unsupported operating system: {os.name}")

    cursor_dir.mkdir(parents=True)
    winsurf_dir.mkdir(parents=True)

    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)


@pytest.fixture
def mock_detector_no_tools(monkeypatch, temp_dir):
    """Mock detector with no installed tools."""
    home_dir = temp_dir / "empty_home"
    home_dir.mkdir()
    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)


class TestShowTools:
    """Test suite for show_tools command."""

    def test_show_tools_with_installed_tools(self, mock_detector_with_tools, capsys):
        """Test show_tools with some installed tools."""
        exit_code = show_tools()

        assert exit_code == 0

        captured = capsys.readouterr()
        assert "AI Coding Tools" in captured.out
        assert "Cursor" in captured.out
        assert "Windsurf" in captured.out
        assert "✓ Installed" in captured.out
        assert "✗ Not found" in captured.out

    def test_show_tools_no_tools_installed(self, mock_detector_no_tools, capsys):
        """Test show_tools with no installed tools."""
        exit_code = show_tools()

        assert exit_code == 0

        captured = capsys.readouterr()
        assert "AI Coding Tools" in captured.out
        assert "No AI coding tools detected" in captured.out

    def test_show_tools_handles_not_implemented_error(self, monkeypatch, temp_dir, capsys):
        """Test show_tools gracefully handles NotImplementedError."""
        home_dir = temp_dir / "home"
        home_dir.mkdir(parents=True)

        # Mock Cursor as installed
        cursor_dir = home_dir / "Library" / "Application Support" / "Cursor"
        cursor_dir = cursor_dir / "User" / "globalStorage"
        cursor_dir.mkdir(parents=True)

        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)

        exit_code = show_tools()

        assert exit_code == 0
        captured = capsys.readouterr()
        # Should show tool but not crash
        assert "Cursor" in captured.out

    def test_show_tools_displays_table_structure(self, mock_detector_with_tools, capsys):
        """Test that show_tools displays a proper table structure."""
        show_tools()

        captured = capsys.readouterr()
        # Check for table structure indicators
        assert "Tool" in captured.out
        assert "Status" in captured.out
        # Rich table uses box drawing characters
        assert "┃" in captured.out or "|" in captured.out or "│" in captured.out
