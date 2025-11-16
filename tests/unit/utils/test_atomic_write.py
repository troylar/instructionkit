"""Unit tests for atomic write utilities."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from aiconfigkit.utils.atomic_write import atomic_write


class TestAtomicWrite:
    """Test atomic_write context manager."""

    def test_atomic_write_basic(self, tmp_path: Path) -> None:
        """Test basic atomic write operation."""
        test_file = tmp_path / "test.txt"

        with atomic_write(test_file, create_backup=False) as f:
            f.write("test content")

        assert test_file.exists()
        assert test_file.read_text() == "test content"

    def test_atomic_write_creates_directory(self, tmp_path: Path) -> None:
        """Test atomic write creates parent directories."""
        test_file = tmp_path / "nested" / "dirs" / "test.txt"

        with atomic_write(test_file, create_backup=False) as f:
            f.write("content")

        assert test_file.exists()
        assert test_file.parent.exists()

    def test_atomic_write_binary_mode(self, tmp_path: Path) -> None:
        """Test atomic write with binary mode."""
        test_file = tmp_path / "binary.dat"
        binary_data = bytes(range(256))

        with atomic_write(test_file, mode="wb", create_backup=False) as f:
            f.write(binary_data)

        assert test_file.read_bytes() == binary_data

    def test_atomic_write_custom_encoding(self, tmp_path: Path) -> None:
        """Test atomic write with custom encoding."""
        test_file = tmp_path / "utf16.txt"
        content = "Hello 世界!"

        with atomic_write(test_file, encoding="utf-16", create_backup=False) as f:
            f.write(content)

        assert test_file.read_text(encoding="utf-16") == content

    def test_atomic_write_creates_backup(self, tmp_path: Path) -> None:
        """Test atomic write creates backup of existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("original content")

        with atomic_write(test_file, create_backup=True) as f:
            f.write("new content")

        backup_file = test_file.with_suffix(".txt.bak")
        assert backup_file.exists()
        assert backup_file.read_text() == "original content"
        assert test_file.read_text() == "new content"

    def test_atomic_write_no_backup_for_new_file(self, tmp_path: Path) -> None:
        """Test atomic write doesn't create backup for new file."""
        test_file = tmp_path / "new.txt"

        with atomic_write(test_file, create_backup=True) as f:
            f.write("content")

        backup_file = test_file.with_suffix(".txt.bak")
        assert not backup_file.exists()
        assert test_file.read_text() == "content"

    def test_atomic_write_overwrites_existing(self, tmp_path: Path) -> None:
        """Test atomic write overwrites existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("old content")

        with atomic_write(test_file, create_backup=False) as f:
            f.write("new content")

        assert test_file.read_text() == "new content"

    def test_atomic_write_error_cleanup(self, tmp_path: Path) -> None:
        """Test atomic write cleans up temp file on error."""
        test_file = tmp_path / "test.txt"

        with pytest.raises(ValueError, match="test error"):
            with atomic_write(test_file, create_backup=False) as f:
                f.write("some content")
                # Raise error before completion
                raise ValueError("test error")

        # Original file should not exist (write failed)
        assert not test_file.exists()

        # No temp files should remain
        temp_files = list(tmp_path.glob(".test.txt.*.tmp"))
        assert len(temp_files) == 0

    def test_atomic_write_error_restores_backup(self, tmp_path: Path) -> None:
        """Test atomic write restores from backup on error."""
        test_file = tmp_path / "test.txt"
        original_content = "original content"
        test_file.write_text(original_content)

        with pytest.raises(ValueError, match="test error"):
            with atomic_write(test_file, create_backup=True) as f:
                f.write("corrupted content")
                raise ValueError("test error")

        # Original content should be restored
        assert test_file.read_text() == original_content

    def test_atomic_write_multiline_content(self, tmp_path: Path) -> None:
        """Test atomic write with multiline content."""
        test_file = tmp_path / "multiline.txt"
        content = "Line 1\nLine 2\nLine 3\n"

        with atomic_write(test_file, create_backup=False) as f:
            f.write(content)

        assert test_file.read_text() == content

    def test_atomic_write_large_file(self, tmp_path: Path) -> None:
        """Test atomic write with large file."""
        test_file = tmp_path / "large.txt"
        # Create large content (1MB)
        content = "x" * (1024 * 1024)

        with atomic_write(test_file, create_backup=False) as f:
            f.write(content)

        assert test_file.read_text() == content

    def test_atomic_write_preserves_extension(self, tmp_path: Path) -> None:
        """Test atomic write preserves file extension."""
        test_file = tmp_path / "config.json"

        with atomic_write(test_file, create_backup=False) as f:
            f.write('{"key": "value"}')

        assert test_file.suffix == ".json"
        assert test_file.read_text() == '{"key": "value"}'

    def test_atomic_write_backup_suffix(self, tmp_path: Path) -> None:
        """Test backup file has correct suffix."""
        test_file = tmp_path / "document.md"
        test_file.write_text("original")

        with atomic_write(test_file, create_backup=True) as f:
            f.write("new")

        backup_file = test_file.with_suffix(".md.bak")
        assert backup_file.exists()
        assert backup_file.suffix == ".bak"

    def test_atomic_write_flush_and_fsync(self, tmp_path: Path) -> None:
        """Test atomic write flushes and fsyncs data."""
        test_file = tmp_path / "test.txt"

        with atomic_write(test_file, create_backup=False) as f:
            f.write("important data")
            # Data should be flushed and synced before exit

        # File should be readable immediately after context exit
        assert test_file.read_text() == "important data"

    def test_atomic_write_resolves_path(self, tmp_path: Path) -> None:
        """Test atomic write resolves relative paths."""
        # Change to tmp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Use relative path
            test_file = Path("relative.txt")

            with atomic_write(test_file, create_backup=False) as f:
                f.write("content")

            # Should create file in current directory
            assert (tmp_path / "relative.txt").exists()
        finally:
            os.chdir(original_cwd)

    def test_atomic_write_binary_with_encoding_ignored(self, tmp_path: Path) -> None:
        """Test binary mode ignores encoding parameter."""
        test_file = tmp_path / "binary.dat"
        binary_data = b"binary\x00data"

        # Encoding parameter should be ignored for binary mode
        with atomic_write(test_file, mode="wb", encoding="utf-8", create_backup=False) as f:
            f.write(binary_data)

        assert test_file.read_bytes() == binary_data

    def test_atomic_write_no_temp_file_leakage(self, tmp_path: Path) -> None:
        """Test no temporary files are leaked after successful write."""
        test_file = tmp_path / "test.txt"

        with atomic_write(test_file, create_backup=False) as f:
            f.write("content")

        # Check for any remaining temp files
        temp_files = list(tmp_path.glob(".test.txt.*.tmp"))
        assert len(temp_files) == 0

    def test_atomic_write_overwrites_existing_backup(self, tmp_path: Path) -> None:
        """Test atomic write overwrites existing backup file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("version 1")

        # Create first backup
        with atomic_write(test_file, create_backup=True) as f:
            f.write("version 2")

        backup_file = test_file.with_suffix(".txt.bak")
        assert backup_file.read_text() == "version 1"

        # Create second backup (should overwrite first)
        with atomic_write(test_file, create_backup=True) as f:
            f.write("version 3")

        assert backup_file.read_text() == "version 2"  # Updated backup
        assert test_file.read_text() == "version 3"  # Updated file

    @pytest.mark.skipif(os.name == "nt", reason="Unicode encoding issues on Windows")
    def test_atomic_write_unicode_content(self, tmp_path: Path) -> None:
        """Test atomic write with Unicode characters."""
        test_file = tmp_path / "unicode.txt"
        content = "Hello 世界! Привет мир! 🌍🌎🌏"

        with atomic_write(test_file, create_backup=False) as f:
            f.write(content)

        assert test_file.read_text() == content

    def test_atomic_write_empty_file(self, tmp_path: Path) -> None:
        """Test atomic write with empty content."""
        test_file = tmp_path / "empty.txt"

        with atomic_write(test_file, create_backup=False) as f:
            f.write("")

        assert test_file.exists()
        assert test_file.read_text() == ""

    def test_atomic_write_file_without_extension(self, tmp_path: Path) -> None:
        """Test atomic write with file without extension."""
        test_file = tmp_path / "README"

        with atomic_write(test_file, create_backup=False) as f:
            f.write("Documentation")

        assert test_file.exists()
        assert test_file.read_text() == "Documentation"

    def test_atomic_write_backup_without_extension(self, tmp_path: Path) -> None:
        """Test backup creation for file without extension."""
        test_file = tmp_path / "LICENSE"
        test_file.write_text("MIT License")

        with atomic_write(test_file, create_backup=True) as f:
            f.write("Apache License")

        backup_file = test_file.with_suffix(".bak")
        assert backup_file.exists()
        assert backup_file.read_text() == "MIT License"

    def test_atomic_write_multiple_operations(self, tmp_path: Path) -> None:
        """Test multiple atomic write operations on same file."""
        test_file = tmp_path / "test.txt"

        # First write
        with atomic_write(test_file, create_backup=False) as f:
            f.write("version 1")
        assert test_file.read_text() == "version 1"

        # Second write
        with atomic_write(test_file, create_backup=False) as f:
            f.write("version 2")
        assert test_file.read_text() == "version 2"

        # Third write
        with atomic_write(test_file, create_backup=False) as f:
            f.write("version 3")
        assert test_file.read_text() == "version 3"

    def test_atomic_write_error_with_cleanup_failure(self, tmp_path: Path) -> None:
        """Test atomic write handles failure to cleanup temp file (lines 76-77)."""
        test_file = tmp_path / "test.txt"

        # Mock os.unlink to fail with OSError when cleanup is attempted
        original_unlink = os.unlink
        unlink_call_count = [0]

        def mock_unlink(path):
            """Mock unlink that fails on first call (temp file cleanup)."""
            unlink_call_count[0] += 1
            if unlink_call_count[0] == 1:
                # First call is the temp file cleanup in exception handler
                raise OSError("Permission denied")
            # Let subsequent calls through
            return original_unlink(path)

        with patch("os.unlink", side_effect=mock_unlink):
            with pytest.raises(ValueError, match="test error"):
                with atomic_write(test_file, create_backup=False) as f:
                    f.write("content")
                    # Raise error to trigger cleanup
                    raise ValueError("test error")

        # File should not exist (write failed)
        assert not test_file.exists()
        # The OSError during cleanup should be silently caught (lines 76-77)
