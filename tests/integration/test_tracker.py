"""Integration tests for installation tracking."""

from datetime import datetime
from pathlib import Path

from aiconfigkit.core.models import AIToolType, InstallationRecord, InstallationScope
from aiconfigkit.storage.tracker import InstallationTracker


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

    def test_make_path_relative_with_non_relative_path(self, temp_dir: Path):
        """Test _make_path_relative when path is not relative to project root."""
        from aiconfigkit.storage.tracker import _make_path_relative

        project_root = temp_dir / "project"
        absolute_path = Path("/completely/different/path/file.md")

        # Should return path as-is with warning
        result = _make_path_relative(absolute_path, project_root)
        assert result == str(absolute_path)

    def test_read_records_with_invalid_record(self, temp_dir: Path):
        """Test _read_records skips invalid records."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Write invalid JSON record (missing required fields)
        import json

        invalid_data = [
            {"instruction_name": "valid", "ai_tool": "cursor", "source_repo": "test", "installed_path": "path"},
            {"invalid": "record"},  # Missing required fields
        ]
        with open(tracker_file, "w") as f:
            json.dump(invalid_data, f)

        # Should skip invalid record and return valid ones
        records = tracker._read_records()
        assert len(records) == 0  # Both invalid since first is missing required fields too

    def test_read_records_with_corrupted_json(self, temp_dir: Path):
        """Test _read_records handles corrupted JSON."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Write corrupted JSON
        with open(tracker_file, "w") as f:
            f.write("{invalid json content")

        # Should return empty list
        records = tracker._read_records()
        assert len(records) == 0

    def test_read_records_with_missing_file(self, temp_dir: Path):
        """Test _read_records handles missing file."""
        tracker_file = temp_dir / "nonexistent.json"
        tracker = InstallationTracker(tracker_file)

        # Manually delete the file
        if tracker_file.exists():
            tracker_file.unlink()

        # Should return empty list
        records = tracker._read_records()
        assert len(records) == 0

    def test_add_installation_with_corrupted_tracker(self, temp_dir: Path, mock_project_dir: Path):
        """Test add_installation handles corrupted tracker file."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Write corrupted JSON to project tracker
        project_tracker = mock_project_dir / ".ai-config-kit" / "installations.json"
        project_tracker.parent.mkdir(parents=True, exist_ok=True)
        with open(project_tracker, "w") as f:
            f.write("{invalid")

        # Should still be able to add installation
        record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path=str(mock_project_dir / ".cursor" / "rules" / "python-style.mdc"),
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )

        # Should not raise exception
        tracker.add_installation(record, project_root=mock_project_dir)

    def test_remove_installation_from_project(self, temp_dir: Path, mock_project_dir: Path):
        """Test removing installation from project tracker."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add project installation
        record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path=str(mock_project_dir / ".cursor" / "rules" / "python-style.mdc"),
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        tracker.add_installation(record, project_root=mock_project_dir)

        # Remove from project
        removed = tracker.remove_installation("python-style", project_root=mock_project_dir)
        assert len(removed) == 1

        # Should be gone from project tracker
        project_records = tracker.get_installed_instructions(project_root=mock_project_dir, include_global=False)
        assert len(project_records) == 0

    def test_remove_installation_with_scope_filter(self, temp_dir: Path, mock_project_dir: Path):
        """Test removing installation with scope filter."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add global installation
        global_record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/global/path/python-style.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.GLOBAL,
        )
        tracker.add_installation(global_record)

        # Add project installation
        project_record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path=str(mock_project_dir / ".cursor" / "rules" / "python-style.mdc"),
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        tracker.add_installation(project_record, project_root=mock_project_dir)

        # Remove only project scope
        removed = tracker.remove_installation("python-style", project_root=mock_project_dir, scope_filter="project")
        assert len(removed) == 1

        # Global should still exist
        global_records = tracker.get_installed_instructions(include_project=False)
        assert len(global_records) == 1

    def test_get_installed_instructions_with_corrupted_project_tracker(self, temp_dir: Path, mock_project_dir: Path):
        """Test get_installed_instructions handles corrupted project tracker."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Create corrupted project tracker
        project_tracker = mock_project_dir / ".ai-config-kit" / "installations.json"
        project_tracker.parent.mkdir(parents=True, exist_ok=True)
        with open(project_tracker, "w") as f:
            f.write("{invalid json")

        # Should not raise exception, just skip project records
        records = tracker.get_installed_instructions(project_root=mock_project_dir)
        assert isinstance(records, list)

    def test_list_installations(self, temp_dir: Path):
        """Test list_installations method."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add some installations
        for i in range(2):
            record = InstallationRecord(
                instruction_name=f"instruction-{i}",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",
                installed_path=f"/path/to/instruction-{i}.mdc",
                installed_at=datetime.now(),
                scope=InstallationScope.GLOBAL,
            )
            tracker.add_installation(record)

        # list_installations should return all records
        all_records = tracker.list_installations()
        assert len(all_records) == 2

    def test_clear_all(self, temp_dir: Path):
        """Test clear_all method."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add some installations
        record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.GLOBAL,
        )
        tracker.add_installation(record)

        # Clear all
        tracker.clear_all()

        # Should be empty
        records = tracker.list_installations()
        assert len(records) == 0

    def test_find_instructions_by_name(self, temp_dir: Path):
        """Test find_instructions_by_name method."""
        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add multiple installations with different names
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

        # Find by name
        found = tracker.find_instructions_by_name("python-style")
        assert len(found) == 2

    def test_get_updatable_instructions(self, temp_dir: Path):
        """Test get_updatable_instructions method."""
        from aiconfigkit.core.models import RefType

        tracker_file = temp_dir / "installations.json"
        tracker = InstallationTracker(tracker_file)

        # Add installation with branch ref (updatable)
        branch_record = InstallationRecord(
            instruction_name="branch-install",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/branch.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.GLOBAL,
            source_ref="main",
            source_ref_type=RefType.BRANCH,
        )
        tracker.add_installation(branch_record)

        # Add installation with tag ref (not updatable)
        tag_record = InstallationRecord(
            instruction_name="tag-install",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/tag.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.GLOBAL,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )
        tracker.add_installation(tag_record)

        # Only branch should be updatable
        updatable = tracker.get_updatable_instructions()
        assert len(updatable) == 1
        assert updatable[0].instruction_name == "branch-install"
