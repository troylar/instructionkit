"""Backup utilities for safe file operations."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


def create_backup(file_path: Path, backup_dir: Optional[Path] = None) -> Path:
    """
    Create a timestamped backup of a file before modifying it.

    Args:
        file_path: Path to file to backup
        backup_dir: Optional custom backup directory (defaults to .instructionkit/backups)

    Returns:
        Path to created backup file

    Raises:
        FileNotFoundError: If file doesn't exist

    Example:
        >>> from pathlib import Path
        >>> backup_path = create_backup(Path(".claude/rules/company.test.md"))
        >>> # Original file preserved at .instructionkit/backups/TIMESTAMP/company.test.md
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")

    # Determine backup directory
    if backup_dir is None:
        # Default: .instructionkit/backups in project root
        from instructionkit.utils.project import find_project_root

        project_root = find_project_root()
        if project_root:
            backup_dir = project_root / ".instructionkit" / "backups"
        else:
            # Fallback to global backups
            backup_dir = Path.home() / ".instructionkit" / "backups"

    # Create timestamped backup directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_dir = backup_dir / timestamp
    timestamped_dir.mkdir(parents=True, exist_ok=True)

    # Preserve relative structure
    # If file is .claude/rules/company.test.md, backup as backups/TIMESTAMP/company.test.md
    backup_path = timestamped_dir / file_path.name

    # Handle name collision (multiple backups in same second)
    counter = 1
    while backup_path.exists():
        backup_path = timestamped_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
        counter += 1

    # Copy file to backup
    shutil.copy2(file_path, backup_path)

    return backup_path


def list_backups(backup_dir: Optional[Path] = None) -> list[tuple[datetime, Path]]:
    """
    List all available backups sorted by date (newest first).

    Args:
        backup_dir: Optional custom backup directory

    Returns:
        List of (timestamp, backup_directory) tuples

    Example:
        >>> backups = list_backups()
        >>> for timestamp, backup_path in backups:
        ...     print(f"{timestamp}: {backup_path}")
    """
    if backup_dir is None:
        from instructionkit.utils.project import find_project_root

        project_root = find_project_root()
        if project_root:
            backup_dir = project_root / ".instructionkit" / "backups"
        else:
            backup_dir = Path.home() / ".instructionkit" / "backups"

    if not backup_dir.exists():
        return []

    backups: list[tuple[datetime, Path]] = []
    for item in backup_dir.iterdir():
        if item.is_dir():
            try:
                # Parse timestamp from directory name (YYYYMMDD_HHMMSS)
                timestamp = datetime.strptime(item.name, "%Y%m%d_%H%M%S")
                backups.append((timestamp, item))
            except ValueError:
                # Skip directories that don't match timestamp format
                continue

    # Sort by timestamp, newest first
    backups.sort(reverse=True, key=lambda x: x[0])
    return backups


def cleanup_old_backups(max_age_days: int = 30, backup_dir: Optional[Path] = None) -> int:
    """
    Remove backups older than specified age.

    Args:
        max_age_days: Maximum age of backups to keep (default: 30 days)
        backup_dir: Optional custom backup directory

    Returns:
        Number of backup directories removed

    Example:
        >>> # Remove backups older than 30 days
        >>> removed = cleanup_old_backups(30)
        >>> print(f"Removed {removed} old backup(s)")
    """
    if backup_dir is None:
        from instructionkit.utils.project import find_project_root

        project_root = find_project_root()
        if project_root:
            backup_dir = project_root / ".instructionkit" / "backups"
        else:
            backup_dir = Path.home() / ".instructionkit" / "backups"

    if not backup_dir.exists():
        return 0

    cutoff_date = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
    removed_count = 0

    for timestamp, backup_path in list_backups(backup_dir):
        if timestamp.timestamp() < cutoff_date:
            shutil.rmtree(backup_path)
            removed_count += 1

    return removed_count


def restore_backup(backup_path: Path, target_path: Path) -> None:
    """
    Restore a file from backup.

    Args:
        backup_path: Path to backup file
        target_path: Where to restore the file

    Raises:
        FileNotFoundError: If backup doesn't exist

    Example:
        >>> # Restore from specific backup
        >>> backup = Path(".instructionkit/backups/20251109_143052/company.test.md")
        >>> restore_backup(backup, Path(".claude/rules/company.test.md"))
    """
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    # Create target directory if needed
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy backup to target
    shutil.copy2(backup_path, target_path)
