"""Integration tests for installation tracking."""

from datetime import datetime
from pathlib import Path

from instructionkit.core.models import AIToolType, InstallationRecord, InstallationScope
from instructionkit.storage.tracker import InstallationTracker


class TestInstallationTracker:
    """Test installation tracking functionality."""

    def test_create_tracker(self, temp_dir: Path):
        """Test creating installation tracker."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        assert tracker.tracker_file == tracker_file
        assert tracker_file.exists()

    def test_add_installation(self, temp_dir: Path):
        """Test adding installation record."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            checksum="abc123",
            scope=InstallationScope.GLOBAL,
        )

        tracker.add_installation(record)

        # Verify it was added
        records = tracker.get_installed_instructions()
        assert len(records) == 1
        assert records[0].instruction_name == "python-style"

    def test_add_project_installation(self, temp_dir: Path, mock_project_dir: Path):
        """Test adding project-scoped installation."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path=str(mock_project_dir / ".cursor" / "rules" / "python-style.mdc"),
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            project_root=str(mock_project_dir),
        )

        tracker.add_installation(record, project_root=mock_project_dir)

        # Should be in project tracker, not global
        global_records = tracker.get_installed_instructions(include_project=False)
        assert len(global_records) == 0

        # Should be in project tracker
        project_records = tracker.get_installed_instructions(project_root=mock_project_dir, include_global=False)
        assert len(project_records) == 1

    def test_remove_installation(self, temp_dir: Path):
        """Test removing installation record."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.GLOBAL,
        )

        tracker.add_installation(record)

        # Remove it
        removed = tracker.remove_installation("python-style")
        assert len(removed) == 1

        # Verify it's gone
        records = tracker.get_installed_instructions()
        assert len(records) == 0

    def test_remove_installation_specific_tool(self, temp_dir: Path):
        """Test removing installation for specific tool only."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add to multiple tools
        for tool in [AIToolType.CURSOR, AIToolType.CLAUDE]:
            record = InstallationRecord(
                instruction_name="python-style",
                ai_tool=tool,
                source_repo="https://github.com/test/repo",
                installed_path=f"/path/to/{tool.value}/instruction.md",
                installed_at=datetime.now(),
                scope=InstallationScope.GLOBAL,
            )
            tracker.add_installation(record)

        # Remove from cursor only
        removed = tracker.remove_installation("python-style", ai_tool=AIToolType.CURSOR)
        assert len(removed) == 1

        # Claude should still be there
        records = tracker.get_installed_instructions()
        assert len(records) == 1
        assert records[0].ai_tool == AIToolType.CLAUDE

    def test_get_installed_instructions(self, temp_dir: Path):
        """Test getting all installed instructions."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add multiple installations
        for i in range(3):
            record = InstallationRecord(
                instruction_name=f"instruction-{i}",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",
                installed_path=f"/path/to/instruction-{i}.mdc",
                installed_at=datetime.now(),
                scope=InstallationScope.GLOBAL,
            )
            tracker.add_installation(record)

        records = tracker.get_installed_instructions()
        assert len(records) == 3

    def test_get_installed_instructions_filtered(self, temp_dir: Path):
        """Test getting installed instructions with filters."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add installations for different tools
        for tool in [AIToolType.CURSOR, AIToolType.CLAUDE]:
            record = InstallationRecord(
                instruction_name="python-style",
                ai_tool=tool,
                source_repo="https://github.com/test/repo",
                installed_path=f"/path/to/{tool.value}/instruction.md",
                installed_at=datetime.now(),
                scope=InstallationScope.GLOBAL,
            )
            tracker.add_installation(record)

        # Filter by tool
        cursor_records = tracker.get_installed_instructions(ai_tool=AIToolType.CURSOR)
        assert len(cursor_records) == 1
        assert cursor_records[0].ai_tool == AIToolType.CURSOR

    def test_is_installed(self, temp_dir: Path):
        """Test checking if instruction is installed."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.GLOBAL,
        )

        tracker.add_installation(record)

        assert tracker.is_installed("python-style") is True
        assert tracker.is_installed("nonexistent") is False

    def test_get_installation(self, temp_dir: Path):
        """Test getting specific installation record."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            checksum="abc123",
            scope=InstallationScope.GLOBAL,
        )

        tracker.add_installation(record)

        retrieved = tracker.get_installation("python-style", AIToolType.CURSOR)
        assert retrieved is not None
        assert retrieved.checksum == "abc123"

    def test_get_installations_from_repo(self, temp_dir: Path):
        """Test getting all installations from specific repo."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        repo_url = "https://github.com/test/repo"

        # Add installations from different repos
        for i in range(2):
            record = InstallationRecord(
                instruction_name=f"instruction-{i}",
                ai_tool=AIToolType.CURSOR,
                source_repo=repo_url if i == 0 else "https://github.com/other/repo",
                installed_path=f"/path/to/instruction-{i}.mdc",
                installed_at=datetime.now(),
                scope=InstallationScope.GLOBAL,
            )
            tracker.add_installation(record)

        records = tracker.get_installations_from_repo(repo_url)
        assert len(records) == 1
        assert records[0].instruction_name == "instruction-0"

    def test_get_bundle_installations(self, temp_dir: Path):
        """Test getting installations from a bundle."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        bundle_name = "python-stack"

        # Add installations, some from bundle
        for i in range(3):
            record = InstallationRecord(
                instruction_name=f"instruction-{i}",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",
                installed_path=f"/path/to/instruction-{i}.mdc",
                installed_at=datetime.now(),
                bundle_name=bundle_name if i < 2 else None,
                scope=InstallationScope.GLOBAL,
            )
            tracker.add_installation(record)

        records = tracker.get_bundle_installations(bundle_name)
        assert len(records) == 2

    def test_update_existing_installation(self, temp_dir: Path):
        """Test that adding same instruction updates the record."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add initial record
        record1 = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            checksum="old_checksum",
            scope=InstallationScope.GLOBAL,
        )
        tracker.add_installation(record1)

        # Add updated record
        record2 = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            checksum="new_checksum",
            scope=InstallationScope.GLOBAL,
        )
        tracker.add_installation(record2)

        # Should only have one record with new checksum
        records = tracker.get_installed_instructions()
        assert len(records) == 1
        assert records[0].checksum == "new_checksum"
