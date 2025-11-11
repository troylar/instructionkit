"""Unit tests for tracker relative path functionality."""

import json
from datetime import datetime
from pathlib import Path

from aiconfigkit.core.models import AIToolType, InstallationRecord, InstallationScope
from aiconfigkit.storage.tracker import InstallationTracker


class TestRelativePathStorage:
    """Test that project-scoped installations store relative paths."""

    def test_project_installation_saves_relative_path(self, temp_dir: Path):
        """Test that project-scoped installation saves relative path in JSON."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        tracker_file = project_root / ".instructionkit" / "installations.json"
        tracker = InstallationTracker()

        # Create record with absolute path
        absolute_path = project_root / ".github" / "instructions" / "test.md"
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.COPILOT,
            source_repo="https://github.com/test/repo",
            installed_path=str(absolute_path),
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )

        # Add with project_root
        tracker.add_installation(record, project_root=project_root)

        # Read the JSON file directly
        with open(tracker_file, "r") as f:
            data = json.load(f)

        # Verify path is relative in JSON
        assert len(data) == 1
        saved_path = data[0]["installed_path"]
        # Normalize for cross-platform comparison (Windows uses backslashes)
        normalized_path = Path(saved_path).as_posix()
        assert normalized_path == ".github/instructions/test.md"
        assert not Path(saved_path).is_absolute()

    def test_project_installation_no_project_root_field(self, temp_dir: Path):
        """Test that project_root field is not saved in JSON."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        tracker_file = project_root / ".instructionkit" / "installations.json"
        tracker = InstallationTracker()

        absolute_path = project_root / ".claude" / "rules" / "test.md"
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CLAUDE,
            source_repo="https://github.com/test/repo",
            installed_path=str(absolute_path),
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )

        tracker.add_installation(record, project_root=project_root)

        # Read JSON directly
        with open(tracker_file, "r") as f:
            data = json.load(f)

        # Verify no project_root field
        assert "project_root" not in data[0]

    def test_global_installation_keeps_absolute_path(self, temp_dir: Path):
        """Test that global installations still use absolute paths."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Use temp_dir to create a truly absolute path that works on all platforms
        absolute_path = str(temp_dir / ".cursor" / "rules" / "global.mdc")
        record = InstallationRecord(
            instruction_name="global-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path=absolute_path,
            installed_at=datetime.now(),
            scope=InstallationScope.GLOBAL,
        )

        tracker.add_installation(record)

        # Read JSON
        with open(tracker_file, "r") as f:
            data = json.load(f)

        # Global installations should keep absolute paths
        saved_path = data[0]["installed_path"]
        assert saved_path == absolute_path
        assert Path(saved_path).is_absolute()


class TestRelativePathRetrieval:
    """Test that relative paths are converted to absolute when reading."""

    def test_reading_project_installation_returns_absolute_path(self, temp_dir: Path):
        """Test that reading project installations converts relative to absolute."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        tracker = InstallationTracker()

        # Save with absolute path (will be stored as relative)
        absolute_path = project_root / ".windsurf" / "rules" / "test.md"
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.WINSURF,
            source_repo="https://github.com/test/repo",
            installed_path=str(absolute_path),
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )

        tracker.add_installation(record, project_root=project_root)

        # Read back
        records = tracker.get_installed_instructions(project_root=project_root, include_global=False)

        assert len(records) == 1
        retrieved_path = records[0].installed_path

        # Should be converted back to absolute
        assert Path(retrieved_path).is_absolute()
        assert retrieved_path == str(absolute_path)

    def test_reading_project_installation_path_exists_check(self, temp_dir: Path):
        """Test that retrieved absolute paths can be used for file operations."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        tracker = InstallationTracker()

        # Create actual file
        file_path = project_root / ".cursor" / "rules" / "test.mdc"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("test content")

        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path=str(file_path),
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )

        tracker.add_installation(record, project_root=project_root)

        # Read back
        records = tracker.get_installed_instructions(project_root=project_root, include_global=False)

        # Verify path works for file operations
        retrieved_path = Path(records[0].installed_path)
        assert retrieved_path.exists()
        assert retrieved_path.read_text() == "test content"


class TestBackwardCompatibility:
    """Test backward compatibility with old absolute path format."""

    def test_reading_old_absolute_paths_still_works(self, temp_dir: Path):
        """Test that old installations with absolute paths still work."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        tracker_file = project_root / ".instructionkit" / "installations.json"
        tracker_file.parent.mkdir(parents=True)

        # Manually create old-format JSON with absolute path
        old_format_data = [
            {
                "instruction_name": "old-instruction",
                "ai_tool": "cursor",
                "source_repo": "https://github.com/test/repo",
                "installed_path": str(project_root / ".cursor" / "rules" / "old.mdc"),
                "installed_at": datetime.now().isoformat(),
                "checksum": "abc123",
                "bundle_name": None,
                "scope": "project",
                "project_root": str(project_root),  # Old format included this
            }
        ]

        with open(tracker_file, "w") as f:
            json.dump(old_format_data, f)

        # Read using tracker
        tracker = InstallationTracker()
        records = tracker.get_installed_instructions(project_root=project_root, include_global=False)

        # Should still read correctly
        assert len(records) == 1
        assert records[0].instruction_name == "old-instruction"
        # Absolute path should still work
        assert Path(records[0].installed_path).is_absolute()

    def test_migrating_old_format_on_save(self, temp_dir: Path):
        """Test that re-saving old format converts to new format."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        tracker_file = project_root / ".instructionkit" / "installations.json"
        tracker_file.parent.mkdir(parents=True)

        # Create old format
        absolute_path = project_root / ".github" / "instructions" / "test.md"
        old_format_data = [
            {
                "instruction_name": "test-instruction",
                "ai_tool": "copilot",
                "source_repo": "https://github.com/test/repo",
                "installed_path": str(absolute_path),
                "installed_at": datetime.now().isoformat(),
                "scope": "project",
                "project_root": str(project_root),
            }
        ]

        with open(tracker_file, "w") as f:
            json.dump(old_format_data, f)

        # Read and re-save using tracker
        tracker = InstallationTracker()
        records = tracker.get_installed_instructions(project_root=project_root, include_global=False)

        # Update the record (triggers a save)
        updated_record = InstallationRecord(
            instruction_name=records[0].instruction_name,
            ai_tool=records[0].ai_tool,
            source_repo=records[0].source_repo,
            installed_path=records[0].installed_path,
            installed_at=datetime.now(),
            checksum="new_checksum",
            scope=InstallationScope.PROJECT,
        )
        tracker.add_installation(updated_record, project_root=project_root)

        # Read JSON directly
        with open(tracker_file, "r") as f:
            data = json.load(f)

        # Should now be in new format
        # Normalize for cross-platform comparison (Windows uses backslashes)
        normalized_path = Path(data[0]["installed_path"]).as_posix()
        assert normalized_path == ".github/instructions/test.md"
        assert "project_root" not in data[0]

    def test_mixed_old_and_new_format(self, temp_dir: Path):
        """Test handling mixture of old absolute and new relative paths."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        tracker_file = project_root / ".instructionkit" / "installations.json"
        tracker_file.parent.mkdir(parents=True)

        # Create mixed format
        mixed_data = [
            {
                # Old format with absolute path
                "instruction_name": "old-instruction",
                "ai_tool": "cursor",
                "source_repo": "https://github.com/test/repo",
                "installed_path": str(project_root / ".cursor" / "rules" / "old.mdc"),
                "installed_at": datetime.now().isoformat(),
                "scope": "project",
            },
            {
                # New format with relative path
                "instruction_name": "new-instruction",
                "ai_tool": "claude",
                "source_repo": "https://github.com/test/repo",
                "installed_path": ".claude/rules/new.md",
                "installed_at": datetime.now().isoformat(),
                "scope": "project",
            },
        ]

        with open(tracker_file, "w") as f:
            json.dump(mixed_data, f)

        # Read using tracker
        tracker = InstallationTracker()
        records = tracker.get_installed_instructions(project_root=project_root, include_global=False)

        # Both should work and have absolute paths
        assert len(records) == 2
        for record in records:
            assert Path(record.installed_path).is_absolute()
