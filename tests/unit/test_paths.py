"""Unit tests for path utilities."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from instructionkit.utils.paths import (
    ensure_directory_exists,
    get_claude_config_dir,
    get_copilot_config_dir,
    get_cursor_config_dir,
    get_home_directory,
    get_installation_tracker_path,
    get_instructionkit_data_dir,
    get_library_dir,
    get_winsurf_config_dir,
    resolve_conflict_name,
    safe_file_name,
)


class TestHomeDirectory:
    """Test home directory retrieval."""

    def test_get_home_directory(self):
        home = get_home_directory()
        assert isinstance(home, Path)
        assert home.exists()


class TestInstructionKitDataDir:
    """Test InstructionKit data directory."""

    def test_get_data_dir(self):
        data_dir = get_instructionkit_data_dir()
        assert isinstance(data_dir, Path)
        assert ".instructionkit" in str(data_dir)


class TestSafeFileName:
    """Test safe filename generation."""

    def test_remove_unsafe_characters(self):
        assert safe_file_name("test<>file") == "test__file"
        assert safe_file_name("test|file") == "test_file"
        assert safe_file_name("test:file") == "test_file"

    def test_preserve_safe_characters(self):
        assert safe_file_name("test-file-123.md") == "test-file-123.md"


class TestResolveConflictName:
    """Test conflict name resolution."""

    def test_resolve_with_suffix(self, tmp_path):
        original = tmp_path / "file.md"
        resolved = resolve_conflict_name(original, "backup")
        assert resolved.name == "file-backup.md"
        assert resolved.parent == tmp_path

    def test_resolve_without_suffix(self, tmp_path):
        # Create a file
        test_file = tmp_path / "file.md"
        test_file.touch()

        # Resolve conflict should return file-1.md
        resolved = resolve_conflict_name(test_file)
        assert "file-1.md" in str(resolved)

    def test_resolve_without_suffix_auto_increment(self, tmp_path):
        """Test auto-increment when multiple conflicts exist."""
        test_file = tmp_path / "file.md"
        test_file.touch()
        (tmp_path / "file-1.md").touch()
        (tmp_path / "file-2.md").touch()

        resolved = resolve_conflict_name(test_file)
        assert "file-3.md" in str(resolved)


class TestCursorConfigDir:
    """Test Cursor config directory detection."""

    @pytest.mark.skipif(sys.platform == "win32", reason="macOS-specific test")
    def test_get_cursor_config_dir_macos(self, monkeypatch, temp_dir):
        """Test Cursor config dir on macOS."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)
        monkeypatch.setattr("os.name", "posix")

        with patch("os.uname") as mock_uname:
            mock_uname.return_value = Mock(sysname="Darwin")
            config_dir = get_cursor_config_dir()
            assert "Library/Application Support/Cursor" in str(config_dir)

    @pytest.mark.skipif(sys.platform == "win32", reason="Linux-specific test")
    def test_get_cursor_config_dir_linux(self, monkeypatch, temp_dir):
        """Test Cursor config dir on Linux."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)
        monkeypatch.setattr("os.name", "posix")

        with patch("os.uname") as mock_uname:
            mock_uname.return_value = Mock(sysname="Linux")
            config_dir = get_cursor_config_dir()
            assert ".config/Cursor" in str(config_dir)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_get_cursor_config_dir_windows(self, monkeypatch, temp_dir):
        """Test Cursor config dir on Windows."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)
        monkeypatch.setattr("os.name", "nt")

        config_dir = get_cursor_config_dir()
        assert "AppData/Roaming/Cursor" in str(config_dir) or "AppData\\Roaming\\Cursor" in str(config_dir)


class TestCopilotConfigDir:
    """Test Copilot config directory detection."""

    @pytest.mark.skipif(sys.platform == "win32", reason="macOS-specific test")
    def test_get_copilot_config_dir_macos(self, monkeypatch, temp_dir):
        """Test Copilot config dir on macOS."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)
        monkeypatch.setattr("os.name", "posix")

        with patch("os.uname") as mock_uname:
            mock_uname.return_value = Mock(sysname="Darwin")
            config_dir = get_copilot_config_dir()
            assert "Library/Application Support/Code" in str(config_dir)
            assert "github.copilot" in str(config_dir)

    @pytest.mark.skipif(sys.platform == "win32", reason="Linux-specific test")
    def test_get_copilot_config_dir_linux(self, monkeypatch, temp_dir):
        """Test Copilot config dir on Linux."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)
        monkeypatch.setattr("os.name", "posix")

        with patch("os.uname") as mock_uname:
            mock_uname.return_value = Mock(sysname="Linux")
            config_dir = get_copilot_config_dir()
            assert ".config/Code" in str(config_dir)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_get_copilot_config_dir_windows(self, monkeypatch, temp_dir):
        """Test Copilot config dir on Windows."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)
        monkeypatch.setattr("os.name", "nt")

        config_dir = get_copilot_config_dir()
        assert "AppData/Roaming/Code" in str(config_dir) or "AppData\\Roaming\\Code" in str(config_dir)


class TestWinsurfConfigDir:
    """Test Windsurf config directory detection."""

    @pytest.mark.skipif(sys.platform == "win32", reason="macOS-specific test")
    def test_get_winsurf_config_dir_macos(self, monkeypatch, temp_dir):
        """Test Windsurf config dir on macOS."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)
        monkeypatch.setattr("os.name", "posix")

        with patch("os.uname") as mock_uname:
            mock_uname.return_value = Mock(sysname="Darwin")
            config_dir = get_winsurf_config_dir()
            assert "Library/Application Support/Windsurf" in str(config_dir)

    @pytest.mark.skipif(sys.platform == "win32", reason="Linux-specific test")
    def test_get_winsurf_config_dir_linux(self, monkeypatch, temp_dir):
        """Test Windsurf config dir on Linux."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)
        monkeypatch.setattr("os.name", "posix")

        with patch("os.uname") as mock_uname:
            mock_uname.return_value = Mock(sysname="Linux")
            config_dir = get_winsurf_config_dir()
            assert ".config/Windsurf" in str(config_dir)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_get_winsurf_config_dir_windows(self, monkeypatch, temp_dir):
        """Test Windsurf config dir on Windows."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)
        monkeypatch.setattr("os.name", "nt")

        config_dir = get_winsurf_config_dir()
        assert "AppData/Roaming/Windsurf" in str(config_dir) or "AppData\\Roaming\\Windsurf" in str(config_dir)


class TestClaudeConfigDir:
    """Test Claude config directory detection."""

    def test_get_claude_config_dir(self, monkeypatch, temp_dir):
        """Test Claude config dir (same across all platforms)."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)

        config_dir = get_claude_config_dir()
        assert ".claude/rules" in str(config_dir)


class TestLibraryDir:
    """Test library directory."""

    def test_get_library_dir(self, monkeypatch, temp_dir):
        """Test get_library_dir creates directory."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)

        library_dir = get_library_dir()
        assert library_dir.exists()
        assert ".instructionkit/library" in str(library_dir)


class TestInstallationTrackerPath:
    """Test installation tracker path."""

    def test_get_installation_tracker_path(self, monkeypatch, temp_dir):
        """Test get_installation_tracker_path."""
        home = temp_dir / "home"
        home.mkdir()
        monkeypatch.setattr("instructionkit.utils.paths.get_home_directory", lambda: home)

        tracker_path = get_installation_tracker_path()
        assert "installations.json" in str(tracker_path)


class TestEnsureDirectoryExists:
    """Test ensure_directory_exists."""

    def test_ensure_directory_exists(self, temp_dir):
        """Test ensure_directory_exists creates directory."""
        test_dir = temp_dir / "test" / "nested" / "dir"
        ensure_directory_exists(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()
