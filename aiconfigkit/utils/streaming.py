"""Streaming utilities for large file operations."""

from pathlib import Path
from typing import Callable, Optional


class StreamingError(Exception):
    """Raised when streaming operations fail."""

    pass


def stream_copy_file(
    source: Path,
    destination: Path,
    chunk_size: int = 8192,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """
    Copy a file in streaming chunks for memory-efficient large file handling.

    Args:
        source: Source file path
        destination: Destination file path
        chunk_size: Size of chunks to read/write (default 8KB)
        progress_callback: Optional callback for progress updates (bytes_copied, total_size)

    Raises:
        FileNotFoundError: If source file doesn't exist
        StreamingError: If copy operation fails
    """
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    try:
        # Get total file size for progress tracking
        total_size = source.stat().st_size
        bytes_copied = 0

        # Ensure destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Open both files and copy in chunks
        with open(source, "rb") as src_file:
            with open(destination, "wb") as dst_file:
                while True:
                    chunk = src_file.read(chunk_size)
                    if not chunk:
                        break

                    dst_file.write(chunk)
                    bytes_copied += len(chunk)

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(bytes_copied, total_size)

    except Exception as e:
        # Clean up partial destination file on error
        if destination.exists():
            destination.unlink()
        raise StreamingError(f"Failed to copy file: {e}") from e


def stream_copy_with_verification(
    source: Path,
    destination: Path,
    checksum: Optional[str] = None,
    chunk_size: int = 8192,
) -> bool:
    """
    Copy a file with optional checksum verification.

    Args:
        source: Source file path
        destination: Destination file path
        checksum: Expected SHA-256 checksum (optional)
        chunk_size: Size of chunks to read/write

    Returns:
        True if copy and verification succeeded

    Raises:
        FileNotFoundError: If source file doesn't exist
        StreamingError: If copy or verification fails
    """
    # First, copy the file
    stream_copy_file(source, destination, chunk_size)

    # Verify checksum if provided
    if checksum:
        from aiconfigkit.core.checksum import calculate_file_checksum

        actual_checksum = calculate_file_checksum(str(destination), "sha256")

        if actual_checksum.lower() != checksum.lower():
            # Delete corrupted file
            destination.unlink()
            raise StreamingError(f"Checksum verification failed! " f"Expected: {checksum}, Actual: {actual_checksum}")

    return True


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path.stat().st_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB", "100 KB")
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        # Bytes - no decimal places
        return f"{int(size)} {units[unit_index]}"
    else:
        # Other units - 1 decimal place
        return f"{size:.1f} {units[unit_index]}"


def is_large_file(file_path: Path, threshold_mb: int = 10) -> bool:
    """
    Check if file is considered "large" based on size threshold.

    Args:
        file_path: Path to file
        threshold_mb: Size threshold in megabytes (default 10 MB)

    Returns:
        True if file size exceeds threshold

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    size_bytes = get_file_size(file_path)
    threshold_bytes = threshold_mb * 1024 * 1024
    return size_bytes > threshold_bytes


def copy_directory_tree(
    source: Path,
    destination: Path,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """
    Copy an entire directory tree with progress tracking.

    Args:
        source: Source directory path
        destination: Destination directory path
        progress_callback: Optional callback(file_path, current, total)

    Returns:
        Number of files copied

    Raises:
        StreamingError: If copy operation fails
    """
    if not source.is_dir():
        raise StreamingError(f"Source is not a directory: {source}")

    try:
        # Count total files for progress tracking
        all_files = list(source.rglob("*"))
        total_files = len([f for f in all_files if f.is_file()])
        files_copied = 0

        # Recreate directory structure
        destination.mkdir(parents=True, exist_ok=True)

        for item in all_files:
            if item.is_file():
                # Calculate relative path
                rel_path = item.relative_to(source)
                dest_file = destination / rel_path

                # Copy file
                stream_copy_file(item, dest_file)
                files_copied += 1

                # Call progress callback
                if progress_callback:
                    progress_callback(str(rel_path), files_copied, total_files)

        return files_copied

    except Exception as e:
        raise StreamingError(f"Failed to copy directory tree: {e}") from e
