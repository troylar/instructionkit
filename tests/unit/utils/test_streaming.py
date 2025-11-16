"""Unit tests for streaming utilities."""

from pathlib import Path
from unittest.mock import patch

import pytest

from aiconfigkit.utils.streaming import (
    StreamingError,
    copy_directory_tree,
    format_file_size,
    get_file_size,
    is_large_file,
    stream_copy_file,
    stream_copy_with_verification,
)


class TestStreamCopyFile:
    """Test stream_copy_file function."""

    def test_stream_copy_basic(self, tmp_path: Path) -> None:
        """Test basic file streaming copy."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        source.write_text("test content")

        stream_copy_file(source, dest)

        assert dest.exists()
        assert dest.read_text() == "test content"

    def test_stream_copy_large_file(self, tmp_path: Path) -> None:
        """Test copying large file in chunks."""
        source = tmp_path / "large.bin"
        dest = tmp_path / "large_copy.bin"
        # Create file larger than default chunk size (8KB)
        content = b"x" * 20000
        source.write_bytes(content)

        stream_copy_file(source, dest)

        assert dest.read_bytes() == content

    def test_stream_copy_with_progress_callback(self, tmp_path: Path) -> None:
        """Test streaming with progress callback."""
        source = tmp_path / "file.txt"
        dest = tmp_path / "copy.txt"
        content = b"x" * 10000
        source.write_bytes(content)

        progress_calls = []

        def progress_callback(bytes_copied: int, total_size: int) -> None:
            progress_calls.append((bytes_copied, total_size))

        stream_copy_file(source, dest, progress_callback=progress_callback)

        # Should have called progress callback multiple times
        assert len(progress_calls) > 0
        # Last call should have total bytes
        assert progress_calls[-1][0] == 10000
        assert progress_calls[-1][1] == 10000

    def test_stream_copy_custom_chunk_size(self, tmp_path: Path) -> None:
        """Test streaming with custom chunk size."""
        source = tmp_path / "file.txt"
        dest = tmp_path / "copy.txt"
        content = b"x" * 100
        source.write_bytes(content)

        stream_copy_file(source, dest, chunk_size=10)

        assert dest.read_bytes() == content

    def test_stream_copy_creates_destination_dir(self, tmp_path: Path) -> None:
        """Test streaming creates destination directory."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "nested" / "dirs" / "dest.txt"
        source.write_text("content")

        stream_copy_file(source, dest)

        assert dest.parent.exists()
        assert dest.read_text() == "content"

    def test_stream_copy_nonexistent_source(self, tmp_path: Path) -> None:
        """Test streaming with non-existent source raises error."""
        source = tmp_path / "nonexistent.txt"
        dest = tmp_path / "dest.txt"

        with pytest.raises(FileNotFoundError, match="Source file not found"):
            stream_copy_file(source, dest)

    def test_stream_copy_binary_file(self, tmp_path: Path) -> None:
        """Test streaming binary file."""
        source = tmp_path / "binary.dat"
        dest = tmp_path / "binary_copy.dat"
        binary_content = bytes(range(256))
        source.write_bytes(binary_content)

        stream_copy_file(source, dest)

        assert dest.read_bytes() == binary_content

    def test_stream_copy_empty_file(self, tmp_path: Path) -> None:
        """Test streaming empty file."""
        source = tmp_path / "empty.txt"
        dest = tmp_path / "empty_copy.txt"
        source.write_text("")

        stream_copy_file(source, dest)

        assert dest.exists()
        assert dest.read_text() == ""

    def test_stream_copy_error_cleanup(self, tmp_path: Path) -> None:
        """Test cleanup on streaming error."""
        source = tmp_path / "source.txt"
        source.write_text("content")
        dest = tmp_path / "dest.txt"

        # Mock open to raise error during write
        with patch("builtins.open", side_effect=[open(source, "rb"), IOError("Write error")]):
            with pytest.raises(StreamingError, match="Failed to copy file"):
                stream_copy_file(source, dest)

        # Destination should not exist (cleaned up on error)
        assert not dest.exists()

    def test_stream_copy_error_cleanup_partial_file(self, tmp_path: Path) -> None:
        """Test cleanup when partial destination file exists."""

        source = tmp_path / "source.txt"
        source.write_text("test content")
        dest = tmp_path / "dest.txt"

        # Create partial destination file
        dest.write_text("partial")
        assert dest.exists()

        # Mock to raise error after destination exists
        original_open = open

        def mock_open_func(file, mode="r", *args, **kwargs):
            if "wb" in mode and str(file) == str(dest):
                raise IOError("Write error")
            return original_open(file, mode, *args, **kwargs)

        with patch("builtins.open", side_effect=mock_open_func):
            with pytest.raises(StreamingError, match="Failed to copy file"):
                stream_copy_file(source, dest)

        # Destination should be cleaned up
        assert not dest.exists()


class TestStreamCopyWithVerification:
    """Test stream_copy_with_verification function."""

    def test_copy_with_verification_valid_checksum(self, tmp_path: Path) -> None:
        """Test copy with valid checksum verification."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        content = "test content"
        source.write_text(content)

        # Calculate expected checksum
        import hashlib

        expected_checksum = hashlib.sha256(content.encode()).hexdigest()

        result = stream_copy_with_verification(source, dest, checksum=expected_checksum)

        assert result is True
        assert dest.read_text() == content

    def test_copy_with_verification_invalid_checksum(self, tmp_path: Path) -> None:
        """Test copy with invalid checksum raises error."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        source.write_text("test content")

        wrong_checksum = "a" * 64

        with pytest.raises(StreamingError, match="Checksum verification failed"):
            stream_copy_with_verification(source, dest, checksum=wrong_checksum)

        # Destination should be deleted after failed verification
        assert not dest.exists()

    def test_copy_with_verification_no_checksum(self, tmp_path: Path) -> None:
        """Test copy without checksum verification."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        source.write_text("content")

        result = stream_copy_with_verification(source, dest, checksum=None)

        assert result is True
        assert dest.read_text() == "content"

    def test_copy_with_verification_case_insensitive(self, tmp_path: Path) -> None:
        """Test checksum verification is case-insensitive."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        content = "test content"
        source.write_text(content)

        import hashlib

        checksum = hashlib.sha256(content.encode()).hexdigest()

        # Test with uppercase checksum
        result = stream_copy_with_verification(source, dest, checksum=checksum.upper())

        assert result is True


class TestGetFileSize:
    """Test get_file_size function."""

    def test_get_file_size_basic(self, tmp_path: Path) -> None:
        """Test getting file size."""
        test_file = tmp_path / "test.txt"
        content = "Hello, World!"
        test_file.write_text(content)

        size = get_file_size(test_file)

        assert size == len(content.encode())

    def test_get_file_size_empty(self, tmp_path: Path) -> None:
        """Test getting size of empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        size = get_file_size(test_file)

        assert size == 0

    def test_get_file_size_binary(self, tmp_path: Path) -> None:
        """Test getting size of binary file."""
        test_file = tmp_path / "binary.dat"
        content = bytes(range(256))
        test_file.write_bytes(content)

        size = get_file_size(test_file)

        assert size == 256

    def test_get_file_size_nonexistent(self, tmp_path: Path) -> None:
        """Test getting size of non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError, match="File not found"):
            get_file_size(test_file)

    def test_get_file_size_large(self, tmp_path: Path) -> None:
        """Test getting size of large file."""
        test_file = tmp_path / "large.bin"
        # Create 1MB file
        content = b"x" * (1024 * 1024)
        test_file.write_bytes(content)

        size = get_file_size(test_file)

        assert size == 1024 * 1024


class TestFormatFileSize:
    """Test format_file_size function."""

    def test_format_bytes(self) -> None:
        """Test formatting bytes."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(100) == "100 B"
        assert format_file_size(1023) == "1023 B"

    def test_format_kilobytes(self) -> None:
        """Test formatting kilobytes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(10240) == "10.0 KB"

    def test_format_megabytes(self) -> None:
        """Test formatting megabytes."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1.5) == "1.5 MB"
        assert format_file_size(1024 * 1024 * 100) == "100.0 MB"

    def test_format_gigabytes(self) -> None:
        """Test formatting gigabytes."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(1024 * 1024 * 1024 * 2.5) == "2.5 GB"

    def test_format_terabytes(self) -> None:
        """Test formatting terabytes."""
        assert format_file_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"
        assert format_file_size(1024 * 1024 * 1024 * 1024 * 5) == "5.0 TB"

    def test_format_large_terabytes(self) -> None:
        """Test formatting very large sizes (max at TB)."""
        # Should not go beyond TB
        huge_size = 1024 * 1024 * 1024 * 1024 * 1000
        result = format_file_size(huge_size)
        assert "TB" in result


class TestIsLargeFile:
    """Test is_large_file function."""

    def test_is_large_file_below_threshold(self, tmp_path: Path) -> None:
        """Test file below threshold is not large."""
        test_file = tmp_path / "small.txt"
        # 1 MB file (below 10 MB default threshold)
        test_file.write_bytes(b"x" * (1024 * 1024))

        assert is_large_file(test_file) is False

    def test_is_large_file_above_threshold(self, tmp_path: Path) -> None:
        """Test file above threshold is large."""
        test_file = tmp_path / "large.bin"
        # 15 MB file (above 10 MB default threshold)
        test_file.write_bytes(b"x" * (15 * 1024 * 1024))

        assert is_large_file(test_file) is True

    def test_is_large_file_custom_threshold(self, tmp_path: Path) -> None:
        """Test custom threshold."""
        test_file = tmp_path / "file.bin"
        # 3 MB file
        test_file.write_bytes(b"x" * (3 * 1024 * 1024))

        assert is_large_file(test_file, threshold_mb=2) is True
        assert is_large_file(test_file, threshold_mb=5) is False

    def test_is_large_file_exact_threshold(self, tmp_path: Path) -> None:
        """Test file exactly at threshold."""
        test_file = tmp_path / "file.bin"
        # Exactly 10 MB
        test_file.write_bytes(b"x" * (10 * 1024 * 1024))

        # Should be False (not greater than threshold)
        assert is_large_file(test_file, threshold_mb=10) is False

    def test_is_large_file_nonexistent(self, tmp_path: Path) -> None:
        """Test checking non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            is_large_file(test_file)


class TestCopyDirectoryTree:
    """Test copy_directory_tree function."""

    def test_copy_directory_basic(self, tmp_path: Path) -> None:
        """Test basic directory tree copy."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        # Create source directory structure
        source.mkdir()
        (source / "file1.txt").write_text("content 1")
        (source / "file2.txt").write_text("content 2")
        subdir = source / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content 3")

        files_copied = copy_directory_tree(source, dest)

        assert files_copied == 3
        assert (dest / "file1.txt").read_text() == "content 1"
        assert (dest / "file2.txt").read_text() == "content 2"
        assert (dest / "subdir" / "file3.txt").read_text() == "content 3"

    def test_copy_directory_with_progress(self, tmp_path: Path) -> None:
        """Test directory copy with progress callback."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        (source / "file1.txt").write_text("content 1")
        (source / "file2.txt").write_text("content 2")

        progress_calls = []

        def progress_callback(file_path: str, current: int, total: int) -> None:
            progress_calls.append((file_path, current, total))

        files_copied = copy_directory_tree(source, dest, progress_callback=progress_callback)

        assert files_copied == 2
        assert len(progress_calls) == 2
        # Check that total is always 2
        assert all(call[2] == 2 for call in progress_calls)

    def test_copy_directory_empty(self, tmp_path: Path) -> None:
        """Test copying empty directory."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()

        files_copied = copy_directory_tree(source, dest)

        assert files_copied == 0
        assert dest.exists()
        assert dest.is_dir()

    def test_copy_directory_nested_structure(self, tmp_path: Path) -> None:
        """Test copying deeply nested directory structure."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        # Create nested structure
        source.mkdir()
        (source / "a" / "b" / "c").mkdir(parents=True)
        (source / "a" / "b" / "c" / "file.txt").write_text("deep content")

        files_copied = copy_directory_tree(source, dest)

        assert files_copied == 1
        assert (dest / "a" / "b" / "c" / "file.txt").read_text() == "deep content"

    def test_copy_directory_not_directory_error(self, tmp_path: Path) -> None:
        """Test copying non-directory raises error."""
        source = tmp_path / "file.txt"
        dest = tmp_path / "dest"
        source.write_text("content")

        with pytest.raises(StreamingError, match="Source is not a directory"):
            copy_directory_tree(source, dest)

    def test_copy_directory_preserves_structure(self, tmp_path: Path) -> None:
        """Test directory copy preserves exact structure."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        # Create structure with multiple levels
        source.mkdir()
        (source / "level1").mkdir()
        (source / "level1" / "file1.txt").write_text("file 1")
        (source / "level1" / "level2").mkdir()
        (source / "level1" / "level2" / "file2.txt").write_text("file 2")

        copy_directory_tree(source, dest)

        assert (dest / "level1" / "file1.txt").exists()
        assert (dest / "level1" / "level2" / "file2.txt").exists()

    def test_copy_directory_binary_files(self, tmp_path: Path) -> None:
        """Test copying directory with binary files."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        binary_content = bytes(range(256))
        (source / "binary.dat").write_bytes(binary_content)

        files_copied = copy_directory_tree(source, dest)

        assert files_copied == 1
        assert (dest / "binary.dat").read_bytes() == binary_content

    def test_copy_directory_error_handling(self, tmp_path: Path) -> None:
        """Test error handling during directory copy."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        (source / "file.txt").write_text("content")

        # Mock stream_copy_file to raise an error
        with patch("aiconfigkit.utils.streaming.stream_copy_file", side_effect=IOError("Copy error")):
            with pytest.raises(StreamingError, match="Failed to copy directory tree"):
                copy_directory_tree(source, dest)


class TestStreamingError:
    """Test StreamingError exception."""

    def test_streaming_error_creation(self) -> None:
        """Test creating StreamingError."""
        error = StreamingError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
