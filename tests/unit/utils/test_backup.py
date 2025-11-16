"""Unit tests for backup utilities."""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aiconfigkit.utils.backup import (
    cleanup_old_backups,
    create_backup,
    list_backups,
    restore_backup,
)


class TestCreateBackup:
    """Test create_backup function."""

    def test_create_backup_basic(self, tmp_path: Path) -> None:
        """Test creating a basic backup."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create backup in custom directory
        backup_dir = tmp_path / "backups"
        backup_path = create_backup(test_file, backup_dir)

        assert backup_path.exists()
        assert backup_path.read_text() == "test content"
        assert backup_path.name == "test.txt"
        assert "backups" in str(backup_path)

    def test_create_backup_preserves_content(self, tmp_path: Path) -> None:
        """Test backup preserves file content exactly."""
        test_file = tmp_path / "data.txt"
        content = "Important data\nLine 2\nLine 3"
        test_file.write_text(content)

        backup_dir = tmp_path / "backups"
        backup_path = create_backup(test_file, backup_dir)

        assert backup_path.read_text() == content

    def test_create_backup_nonexistent_file(self, tmp_path: Path) -> None:
        """Test backing up non-existent file raises error."""
        nonexistent = tmp_path / "nonexistent.txt"
        backup_dir = tmp_path / "backups"

        with pytest.raises(FileNotFoundError, match="Cannot backup non-existent file"):
            create_backup(nonexistent, backup_dir)

    def test_create_backup_creates_timestamped_directory(self, tmp_path: Path) -> None:
        """Test backup creates timestamped directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        backup_dir = tmp_path / "backups"
        backup_path = create_backup(test_file, backup_dir)

        # Check timestamped directory exists (format: YYYYMMDD_HHMMSS)
        timestamp_dir = backup_path.parent
        assert timestamp_dir.parent == backup_dir
        assert len(timestamp_dir.name) == 15  # YYYYMMDD_HHMMSS = 15 chars
        assert "_" in timestamp_dir.name

    def test_create_backup_handles_name_collision(self, tmp_path: Path) -> None:
        """Test backup handles file name collisions."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        backup_dir = tmp_path / "backups"

        # Create first backup
        backup1 = create_backup(test_file, backup_dir)

        # Create second backup in same directory (simulate same second)
        # Manually create collision by making backup1 exist
        backup_path2 = create_backup(test_file, backup_dir)

        # Second backup should have different name
        assert backup1.exists()
        assert backup_path2.exists()

    def test_create_backup_with_extension(self, tmp_path: Path) -> None:
        """Test backup preserves file extension."""
        test_file = tmp_path / "document.md"
        test_file.write_text("# Markdown content")

        backup_dir = tmp_path / "backups"
        backup_path = create_backup(test_file, backup_dir)

        assert backup_path.suffix == ".md"
        assert backup_path.name == "document.md"

    def test_create_backup_binary_file(self, tmp_path: Path) -> None:
        """Test backing up binary file."""
        test_file = tmp_path / "binary.dat"
        binary_content = bytes(range(256))
        test_file.write_bytes(binary_content)

        backup_dir = tmp_path / "backups"
        backup_path = create_backup(test_file, backup_dir)

        assert backup_path.read_bytes() == binary_content

    @patch("aiconfigkit.utils.project.find_project_root")
    def test_create_backup_default_dir_with_project(self, mock_find_root: MagicMock, tmp_path: Path) -> None:
        """Test default backup directory with project root."""
        mock_find_root.return_value = tmp_path

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        backup_path = create_backup(test_file)

        expected_dir = tmp_path / ".instructionkit" / "backups"
        assert str(expected_dir) in str(backup_path)

    @patch("aiconfigkit.utils.project.find_project_root")
    def test_create_backup_default_dir_no_project(
        self, mock_find_root: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test default backup directory fallback to home."""
        mock_find_root.return_value = None
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        backup_path = create_backup(test_file)

        expected_dir = tmp_path / ".instructionkit" / "backups"
        assert str(expected_dir) in str(backup_path)

    def test_create_backup_collision_counter(self, tmp_path: Path) -> None:
        """Test backup collision counter increments correctly."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        backup_dir = tmp_path / "backups"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_dir = backup_dir / timestamp
        timestamped_dir.mkdir(parents=True, exist_ok=True)

        # Pre-create colliding files
        (timestamped_dir / "test.txt").write_text("existing 1")
        (timestamped_dir / "test_1.txt").write_text("existing 2")

        backup_path = create_backup(test_file, backup_dir)

        # Should create test_2.txt due to collisions
        assert backup_path.name == "test_2.txt"


class TestListBackups:
    """Test list_backups function."""

    def test_list_backups_empty_directory(self, tmp_path: Path) -> None:
        """Test listing backups with no backups."""
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        backups = list_backups(backup_dir)
        assert backups == []

    def test_list_backups_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test listing backups with non-existent directory."""
        backup_dir = tmp_path / "backups"
        backups = list_backups(backup_dir)
        assert backups == []

    def test_list_backups_single_backup(self, tmp_path: Path) -> None:
        """Test listing single backup."""
        backup_dir = tmp_path / "backups"
        timestamp_dir = backup_dir / "20251109_143052"
        timestamp_dir.mkdir(parents=True)

        backups = list_backups(backup_dir)

        assert len(backups) == 1
        timestamp, path = backups[0]
        assert isinstance(timestamp, datetime)
        assert timestamp.year == 2025
        assert timestamp.month == 11
        assert timestamp.day == 9
        assert path == timestamp_dir

    def test_list_backups_multiple_sorted(self, tmp_path: Path) -> None:
        """Test listing multiple backups sorted by date."""
        backup_dir = tmp_path / "backups"

        # Create backups in non-chronological order
        dir1 = backup_dir / "20251109_100000"
        dir2 = backup_dir / "20251109_150000"
        dir3 = backup_dir / "20251109_120000"

        dir1.mkdir(parents=True)
        dir2.mkdir(parents=True)
        dir3.mkdir(parents=True)

        backups = list_backups(backup_dir)

        assert len(backups) == 3
        # Should be sorted newest first
        assert backups[0][1] == dir2  # 15:00:00
        assert backups[1][1] == dir3  # 12:00:00
        assert backups[2][1] == dir1  # 10:00:00

    def test_list_backups_skips_invalid_names(self, tmp_path: Path) -> None:
        """Test listing skips directories with invalid timestamp names."""
        backup_dir = tmp_path / "backups"

        # Create valid and invalid backup directories
        valid_dir = backup_dir / "20251109_143052"
        invalid_dir1 = backup_dir / "not_a_timestamp"
        invalid_dir2 = backup_dir / "20251109"  # Missing time

        valid_dir.mkdir(parents=True)
        invalid_dir1.mkdir(parents=True)
        invalid_dir2.mkdir(parents=True)

        backups = list_backups(backup_dir)

        # Should only include valid timestamp
        assert len(backups) == 1
        assert backups[0][1] == valid_dir

    def test_list_backups_skips_files(self, tmp_path: Path) -> None:
        """Test listing skips files (only processes directories)."""
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create a file with timestamp name
        (backup_dir / "20251109_143052").write_text("not a directory")

        backups = list_backups(backup_dir)
        assert len(backups) == 0

    @patch("aiconfigkit.utils.project.find_project_root")
    def test_list_backups_default_dir_with_project(self, mock_find_root: MagicMock, tmp_path: Path) -> None:
        """Test default backup directory detection with project."""
        mock_find_root.return_value = tmp_path

        backup_dir = tmp_path / ".instructionkit" / "backups"
        timestamp_dir = backup_dir / "20251109_143052"
        timestamp_dir.mkdir(parents=True)

        backups = list_backups()

        assert len(backups) == 1

    @patch("aiconfigkit.utils.project.find_project_root")
    def test_list_backups_default_dir_no_project(
        self, mock_find_root: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test default backup directory fallback to home."""
        mock_find_root.return_value = None
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        backup_dir = tmp_path / ".instructionkit" / "backups"
        timestamp_dir = backup_dir / "20251109_143052"
        timestamp_dir.mkdir(parents=True)

        backups = list_backups()

        assert len(backups) == 1


class TestCleanupOldBackups:
    """Test cleanup_old_backups function."""

    def test_cleanup_no_backups(self, tmp_path: Path) -> None:
        """Test cleanup with no backups."""
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        removed = cleanup_old_backups(30, backup_dir)
        assert removed == 0

    def test_cleanup_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test cleanup with non-existent directory."""
        backup_dir = tmp_path / "backups"

        removed = cleanup_old_backups(30, backup_dir)
        assert removed == 0

    def test_cleanup_removes_old_backups(self, tmp_path: Path) -> None:
        """Test cleanup removes old backups."""
        backup_dir = tmp_path / "backups"

        # Create old backup (60 days ago)
        old_date = datetime.now() - timedelta(days=60)
        old_timestamp = old_date.strftime("%Y%m%d_%H%M%S")
        old_dir = backup_dir / old_timestamp
        old_dir.mkdir(parents=True)
        (old_dir / "old_file.txt").write_text("old content")

        # Create recent backup (10 days ago)
        recent_date = datetime.now() - timedelta(days=10)
        recent_timestamp = recent_date.strftime("%Y%m%d_%H%M%S")
        recent_dir = backup_dir / recent_timestamp
        recent_dir.mkdir(parents=True)
        (recent_dir / "recent_file.txt").write_text("recent content")

        # Cleanup backups older than 30 days
        removed = cleanup_old_backups(30, backup_dir)

        assert removed == 1
        assert not old_dir.exists()
        assert recent_dir.exists()

    def test_cleanup_keeps_recent_backups(self, tmp_path: Path) -> None:
        """Test cleanup keeps all recent backups."""
        backup_dir = tmp_path / "backups"

        # Create recent backups
        for days_ago in [1, 5, 10, 20, 29]:
            date = datetime.now() - timedelta(days=days_ago)
            timestamp = date.strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / timestamp
            backup_path.mkdir(parents=True)

        removed = cleanup_old_backups(30, backup_dir)

        assert removed == 0
        # All 5 backups should still exist
        assert len(list(backup_dir.iterdir())) == 5

    def test_cleanup_removes_multiple_old_backups(self, tmp_path: Path) -> None:
        """Test cleanup removes multiple old backups."""
        backup_dir = tmp_path / "backups"

        # Create old backups
        for days_ago in [40, 50, 60, 70, 90]:
            date = datetime.now() - timedelta(days=days_ago)
            timestamp = date.strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / timestamp
            backup_path.mkdir(parents=True)

        removed = cleanup_old_backups(30, backup_dir)

        assert removed == 5
        assert not backup_dir.exists() or len(list(backup_dir.iterdir())) == 0

    def test_cleanup_custom_max_age(self, tmp_path: Path) -> None:
        """Test cleanup with custom max age."""
        backup_dir = tmp_path / "backups"

        # Create backups at various ages
        for days_ago in [5, 10, 15]:
            date = datetime.now() - timedelta(days=days_ago)
            timestamp = date.strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / timestamp
            backup_path.mkdir(parents=True)

        # Cleanup with max age of 7 days
        removed = cleanup_old_backups(7, backup_dir)

        assert removed == 2  # 10 and 15 day old backups removed
        assert len(list(backup_dir.iterdir())) == 1  # 5 day old backup remains

    @patch("aiconfigkit.utils.project.find_project_root")
    def test_cleanup_default_dir_with_project(self, mock_find_root: MagicMock, tmp_path: Path) -> None:
        """Test cleanup with default project directory."""
        mock_find_root.return_value = tmp_path

        backup_dir = tmp_path / ".instructionkit" / "backups"
        old_date = datetime.now() - timedelta(days=60)
        old_timestamp = old_date.strftime("%Y%m%d_%H%M%S")
        old_dir = backup_dir / old_timestamp
        old_dir.mkdir(parents=True)

        removed = cleanup_old_backups(30)

        assert removed == 1

    @patch("aiconfigkit.utils.project.find_project_root")
    def test_cleanup_default_dir_no_project(
        self, mock_find_root: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test cleanup with default home directory."""
        mock_find_root.return_value = None
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        backup_dir = tmp_path / ".instructionkit" / "backups"
        old_date = datetime.now() - timedelta(days=60)
        old_timestamp = old_date.strftime("%Y%m%d_%H%M%S")
        old_dir = backup_dir / old_timestamp
        old_dir.mkdir(parents=True)

        removed = cleanup_old_backups(30)

        assert removed == 1


class TestRestoreBackup:
    """Test restore_backup function."""

    def test_restore_backup_basic(self, tmp_path: Path) -> None:
        """Test basic backup restoration."""
        # Create backup file
        backup_path = tmp_path / "backup" / "test.txt"
        backup_path.parent.mkdir(parents=True)
        backup_path.write_text("backup content")

        # Restore to target
        target_path = tmp_path / "target" / "restored.txt"
        restore_backup(backup_path, target_path)

        assert target_path.exists()
        assert target_path.read_text() == "backup content"

    def test_restore_backup_creates_target_directory(self, tmp_path: Path) -> None:
        """Test restoration creates target directory if needed."""
        backup_path = tmp_path / "backup.txt"
        backup_path.write_text("content")

        target_path = tmp_path / "nested" / "dirs" / "target.txt"
        restore_backup(backup_path, target_path)

        assert target_path.exists()
        assert target_path.parent.exists()

    def test_restore_backup_nonexistent_backup(self, tmp_path: Path) -> None:
        """Test restoring non-existent backup raises error."""
        backup_path = tmp_path / "nonexistent.txt"
        target_path = tmp_path / "target.txt"

        with pytest.raises(FileNotFoundError, match="Backup not found"):
            restore_backup(backup_path, target_path)

    def test_restore_backup_overwrites_existing(self, tmp_path: Path) -> None:
        """Test restoration overwrites existing target file."""
        backup_path = tmp_path / "backup.txt"
        backup_path.write_text("new content")

        target_path = tmp_path / "target.txt"
        target_path.write_text("old content")

        restore_backup(backup_path, target_path)

        assert target_path.read_text() == "new content"

    def test_restore_backup_preserves_content(self, tmp_path: Path) -> None:
        """Test restoration preserves exact content."""
        backup_path = tmp_path / "backup.txt"
        content = "Line 1\nLine 2\nLine 3\nSpecial chars: åéîøü"
        backup_path.write_text(content)

        target_path = tmp_path / "target.txt"
        restore_backup(backup_path, target_path)

        assert target_path.read_text() == content

    def test_restore_backup_binary_file(self, tmp_path: Path) -> None:
        """Test restoring binary file."""
        backup_path = tmp_path / "backup.dat"
        binary_content = bytes(range(256))
        backup_path.write_bytes(binary_content)

        target_path = tmp_path / "target.dat"
        restore_backup(backup_path, target_path)

        assert target_path.read_bytes() == binary_content

    def test_restore_backup_preserves_extension(self, tmp_path: Path) -> None:
        """Test restoration preserves file extension."""
        backup_path = tmp_path / "backup.md"
        backup_path.write_text("# Markdown")

        target_path = tmp_path / "target.md"
        restore_backup(backup_path, target_path)

        assert target_path.suffix == ".md"
        assert target_path.read_text() == "# Markdown"
