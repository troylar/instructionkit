"""Unit tests for streaming utilities."""

from pathlib import Path

import pytest

from aiconfigkit.core.checksum import calculate_file_checksum
from aiconfigkit.utils.streaming import (
    StreamingError,
    copy_directory_tree,
    format_file_size,
    get_file_size,
    is_large_file,
    stream_copy_file,
    stream_copy_with_verification,
)


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    """Create a sample file for testing."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Hello, World! This is a test file.")
    return file_path


@pytest.fixture
def large_file(tmp_path: Path) -> Path:
    """Create a large file for testing (> 10MB)."""
    file_path = tmp_path / "large.bin"
    # Create a 15MB file
    with open(file_path, "wb") as f:
        f.write(b"x" * (15 * 1024 * 1024))
    return file_path


@pytest.fixture
def sample_directory(tmp_path: Path) -> Path:
    """Create a sample directory structure for testing."""
    dir_path = tmp_path / "source"
    dir_path.mkdir()

    # Create nested structure
    (dir_path / "file1.txt").write_text("File 1")
    (dir_path / "file2.txt").write_text("File 2")

    sub_dir = dir_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "file3.txt").write_text("File 3")

    return dir_path


class TestStreamCopyFile:
    """Test stream_copy_file function."""

    def test_copy_file_basic(self, sample_file: Path, tmp_path: Path) -> None:
        """Test basic file copying."""
        dest = tmp_path / "destination.txt"

        stream_copy_file(sample_file, dest)

        assert dest.exists()
        assert dest.read_text() == sample_file.read_text()

    def test_copy_file_creates_parent_directory(self, sample_file: Path, tmp_path: Path) -> None:
        """Test that parent directories are created."""
        dest = tmp_path / "nested" / "dirs" / "file.txt"

        stream_copy_file(sample_file, dest)

        assert dest.exists()
        assert dest.read_text() == sample_file.read_text()

    def test_copy_file_missing_source_raises_error(self, tmp_path: Path) -> None:
        """Test that copying nonexistent file raises error."""
        source = tmp_path / "nonexistent.txt"
        dest = tmp_path / "dest.txt"

        with pytest.raises(FileNotFoundError, match="Source file not found"):
            stream_copy_file(source, dest)

    def test_copy_file_with_progress_callback(self, sample_file: Path, tmp_path: Path) -> None:
        """Test copying with progress callback."""
        dest = tmp_path / "dest.txt"
        progress_calls = []

        def progress_callback(bytes_copied: int, total_size: int) -> None:
            progress_calls.append((bytes_copied, total_size))

        stream_copy_file(sample_file, dest, progress_callback=progress_callback)

        assert dest.exists()
        assert len(progress_calls) > 0
        # Last call should have all bytes copied
        assert progress_calls[-1][0] == progress_calls[-1][1]

    def test_copy_file_with_custom_chunk_size(self, sample_file: Path, tmp_path: Path) -> None:
        """Test copying with custom chunk size."""
        dest = tmp_path / "dest.txt"

        stream_copy_file(sample_file, dest, chunk_size=4)

        assert dest.exists()
        assert dest.read_text() == sample_file.read_text()


class TestStreamCopyWithVerification:
    """Test stream_copy_with_verification function."""

    def test_copy_with_valid_checksum(self, sample_file: Path, tmp_path: Path) -> None:
        """Test copying with valid checksum."""
        dest = tmp_path / "dest.txt"
        checksum = calculate_file_checksum(str(sample_file), "sha256")

        result = stream_copy_with_verification(sample_file, dest, checksum)

        assert result is True
        assert dest.exists()
        assert dest.read_text() == sample_file.read_text()

    def test_copy_without_checksum(self, sample_file: Path, tmp_path: Path) -> None:
        """Test copying without checksum verification."""
        dest = tmp_path / "dest.txt"

        result = stream_copy_with_verification(sample_file, dest)

        assert result is True
        assert dest.exists()

    def test_copy_with_invalid_checksum_raises_error(self, sample_file: Path, tmp_path: Path) -> None:
        """Test that invalid checksum raises error and cleans up."""
        dest = tmp_path / "dest.txt"
        invalid_checksum = "0" * 64  # Invalid checksum

        with pytest.raises(StreamingError, match="Checksum verification failed"):
            stream_copy_with_verification(sample_file, dest, invalid_checksum)

        # Destination should be deleted after verification failure
        assert not dest.exists()


class TestGetFileSize:
    """Test get_file_size function."""

    def test_get_file_size(self, sample_file: Path) -> None:
        """Test getting file size."""
        size = get_file_size(sample_file)

        assert size > 0
        assert size == len(sample_file.read_bytes())

    def test_get_file_size_nonexistent_raises_error(self, tmp_path: Path) -> None:
        """Test that getting size of nonexistent file raises error."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            get_file_size(tmp_path / "nonexistent.txt")


class TestFormatFileSize:
    """Test format_file_size function."""

    def test_format_bytes(self) -> None:
        """Test formatting bytes."""
        assert format_file_size(500) == "500 B"

    def test_format_kilobytes(self) -> None:
        """Test formatting kilobytes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"

    def test_format_megabytes(self) -> None:
        """Test formatting megabytes."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 5) == "5.0 MB"

    def test_format_gigabytes(self) -> None:
        """Test formatting gigabytes."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_format_terabytes(self) -> None:
        """Test formatting terabytes."""
        assert format_file_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"

    def test_format_zero(self) -> None:
        """Test formatting zero bytes."""
        assert format_file_size(0) == "0 B"


class TestIsLargeFile:
    """Test is_large_file function."""

    def test_small_file(self, sample_file: Path) -> None:
        """Test detecting small file."""
        assert not is_large_file(sample_file, threshold_mb=10)

    def test_large_file(self, large_file: Path) -> None:
        """Test detecting large file."""
        assert is_large_file(large_file, threshold_mb=10)

    def test_custom_threshold(self, large_file: Path) -> None:
        """Test with custom threshold."""
        # 15MB file with 20MB threshold should not be considered large
        assert not is_large_file(large_file, threshold_mb=20)

        # 15MB file with 5MB threshold should be considered large
        assert is_large_file(large_file, threshold_mb=5)

    def test_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that checking nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            is_large_file(tmp_path / "nonexistent.txt")


class TestCopyDirectoryTree:
    """Test copy_directory_tree function."""

    def test_copy_directory_basic(self, sample_directory: Path, tmp_path: Path) -> None:
        """Test basic directory copying."""
        dest = tmp_path / "destination"

        files_copied = copy_directory_tree(sample_directory, dest)

        assert files_copied == 3
        assert (dest / "file1.txt").exists()
        assert (dest / "file2.txt").exists()
        assert (dest / "subdir" / "file3.txt").exists()
        assert (dest / "file1.txt").read_text() == "File 1"

    def test_copy_directory_preserves_structure(self, sample_directory: Path, tmp_path: Path) -> None:
        """Test that directory structure is preserved."""
        dest = tmp_path / "destination"

        copy_directory_tree(sample_directory, dest)

        # Check structure
        assert dest.is_dir()
        assert (dest / "subdir").is_dir()
        assert (dest / "subdir" / "file3.txt").is_file()

    def test_copy_directory_with_progress_callback(self, sample_directory: Path, tmp_path: Path) -> None:
        """Test copying with progress callback."""
        dest = tmp_path / "destination"
        progress_calls = []

        def progress_callback(file_path: str, current: int, total: int) -> None:
            progress_calls.append((file_path, current, total))

        copy_directory_tree(sample_directory, dest, progress_callback)

        assert len(progress_calls) == 3  # 3 files
        # Check that all files were reported
        file_names = {call[0] for call in progress_calls}
        assert "file1.txt" in file_names
        assert "file2.txt" in file_names

    def test_copy_directory_not_a_directory_raises_error(self, sample_file: Path, tmp_path: Path) -> None:
        """Test that copying a file as directory raises error."""
        dest = tmp_path / "dest"

        with pytest.raises(StreamingError, match="not a directory"):
            copy_directory_tree(sample_file, dest)

    def test_copy_empty_directory(self, tmp_path: Path) -> None:
        """Test copying empty directory."""
        source = tmp_path / "empty"
        source.mkdir()
        dest = tmp_path / "destination"

        files_copied = copy_directory_tree(source, dest)

        assert files_copied == 0
        assert dest.exists()
        assert dest.is_dir()
