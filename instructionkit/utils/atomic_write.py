"""Atomic file write utilities for safe config file updates."""

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


@contextmanager
def atomic_write(
    file_path: Path,
    mode: str = "w",
    encoding: str = "utf-8",
    create_backup: bool = True,
) -> Generator:
    """
    Context manager for atomic file writes using temp file + os.replace().

    This ensures that file writes are atomic - if the write fails, the original
    file is left unchanged. If create_backup is True, creates a backup before
    replacing the original file.

    Args:
        file_path: Path to file to write
        mode: File open mode ("w" for text, "wb" for binary)
        encoding: Text encoding (ignored for binary mode)
        create_backup: Whether to create .bak backup before replacing

    Yields:
        File object for writing

    Example:
        with atomic_write(Path("config.json")) as f:
            json.dump(config, f)
    """
    file_path = Path(file_path).resolve()
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create backup if requested and file exists
    backup_path = None
    if create_backup and file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        # Copy original to backup
        import shutil

        shutil.copy2(file_path, backup_path)

    # Create temporary file in same directory as target
    # (ensures atomic rename on all platforms)
    fd, temp_path = tempfile.mkstemp(dir=file_path.parent, prefix=f".{file_path.name}.", suffix=".tmp")

    try:
        # Open temp file with requested mode
        if "b" in mode:
            # Binary mode
            temp_file = os.fdopen(fd, mode)
        else:
            # Text mode
            temp_file = os.fdopen(fd, mode, encoding=encoding)

        with temp_file as f:
            yield f
            # Ensure data is written to disk
            f.flush()
            os.fsync(f.fileno())

        # Atomic rename (replaces target file)
        # os.replace() is atomic on all platforms
        os.replace(temp_path, file_path)

    except Exception:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass

        # Restore from backup if available
        if backup_path and backup_path.exists():
            import shutil

            shutil.copy2(backup_path, file_path)

        raise

    finally:
        # Clean up backup file (optional - could keep for user reference)
        # For now, keep backups for safety
        pass
