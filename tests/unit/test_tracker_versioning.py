"""Unit tests for tracker versioning functions."""

from datetime import datetime

from aiconfigkit.core.models import AIToolType, InstallationRecord, InstallationScope, RefType
from aiconfigkit.storage.tracker import InstallationTracker


class TestGetUpdatableInstructions:
    """Test get_updatable_instructions function."""

    def test_get_updatable_with_branch_refs(self, tmp_path):
        """Test that branch-based installations are returned as updatable."""
        tracker_file = tmp_path / "installations.json"
        tracker = InstallationTracker(tracker_file=tracker_file)

        # Add branch-based installation
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            source_ref="main",
            source_ref_type=RefType.BRANCH,
        )
        tracker.add_installation(record)

        updatable = tracker.get_updatable_instructions()

        assert len(updatable) == 1
        assert updatable[0].source_ref == "main"
        assert updatable[0].source_ref_type == RefType.BRANCH

    def test_get_updatable_filters_out_tags(self, tmp_path):
        """Test that tag-based installations are NOT updatable."""
        tracker_file = tmp_path / "installations.json"
        tracker = InstallationTracker(tracker_file=tracker_file)

        # Add tag-based installation
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )
        tracker.add_installation(record)

        updatable = tracker.get_updatable_instructions()

        assert len(updatable) == 0

    def test_get_updatable_filters_out_commits(self, tmp_path):
        """Test that commit-based installations are NOT updatable."""
        tracker_file = tmp_path / "installations.json"
        tracker = InstallationTracker(tracker_file=tracker_file)

        # Add commit-based installation
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CLAUDE,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            source_ref="abc123def456",
            source_ref_type=RefType.COMMIT,
        )
        tracker.add_installation(record)

        updatable = tracker.get_updatable_instructions()

        assert len(updatable) == 0

    def test_get_updatable_includes_legacy_records(self, tmp_path):
        """Test that records without ref info are included (legacy format)."""
        tracker_file = tmp_path / "installations.json"
        tracker = InstallationTracker(tracker_file=tracker_file)

        # Add legacy installation (no ref fields)
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.WINSURF,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        tracker.add_installation(record)

        updatable = tracker.get_updatable_instructions()

        assert len(updatable) == 1
        assert updatable[0].source_ref is None
        assert updatable[0].source_ref_type is None

    def test_get_updatable_mixed_ref_types(self, tmp_path):
        """Test filtering with mixed ref types."""
        tracker_file = tmp_path / "installations.json"
        tracker = InstallationTracker(tracker_file=tracker_file)

        # Add various ref types
        records = [
            InstallationRecord(
                instruction_name="branch-instruction",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/user/repo",
                installed_path="/path/branch.md",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                source_ref="main",
                source_ref_type=RefType.BRANCH,
            ),
            InstallationRecord(
                instruction_name="tag-instruction",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/user/repo",
                installed_path="/path/tag.md",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                source_ref="v1.0.0",
                source_ref_type=RefType.TAG,
            ),
            InstallationRecord(
                instruction_name="commit-instruction",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/user/repo",
                installed_path="/path/commit.md",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                source_ref="abc123",
                source_ref_type=RefType.COMMIT,
            ),
            InstallationRecord(
                instruction_name="another-branch",
                ai_tool=AIToolType.CLAUDE,
                source_repo="https://github.com/user/repo",
                installed_path="/path/another.md",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                source_ref="develop",
                source_ref_type=RefType.BRANCH,
            ),
        ]

        for record in records:
            tracker.add_installation(record)

        updatable = tracker.get_updatable_instructions()

        # Only branches should be updatable
        assert len(updatable) == 2
        updatable_names = [r.instruction_name for r in updatable]
        assert "branch-instruction" in updatable_names
        assert "another-branch" in updatable_names
        assert "tag-instruction" not in updatable_names
        assert "commit-instruction" not in updatable_names

    def test_get_updatable_empty_tracker(self, tmp_path):
        """Test get_updatable_instructions with no installations."""
        tracker_file = tmp_path / "installations.json"
        tracker = InstallationTracker(tracker_file=tracker_file)

        updatable = tracker.get_updatable_instructions()

        assert updatable == []

    def test_get_updatable_multiple_branches(self, tmp_path):
        """Test multiple branch-based installations from different repos."""
        tracker_file = tmp_path / "installations.json"
        tracker = InstallationTracker(tracker_file=tracker_file)

        # Add multiple branch-based installations
        records = [
            InstallationRecord(
                instruction_name="repo1-main",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/user/repo1",
                installed_path="/path/repo1.md",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                source_ref="main",
                source_ref_type=RefType.BRANCH,
            ),
            InstallationRecord(
                instruction_name="repo2-develop",
                ai_tool=AIToolType.CLAUDE,
                source_repo="https://github.com/user/repo2",
                installed_path="/path/repo2.md",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                source_ref="develop",
                source_ref_type=RefType.BRANCH,
            ),
            InstallationRecord(
                instruction_name="repo3-feature",
                ai_tool=AIToolType.WINSURF,
                source_repo="https://github.com/user/repo3",
                installed_path="/path/repo3.md",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                source_ref="feature/new",
                source_ref_type=RefType.BRANCH,
            ),
        ]

        for record in records:
            tracker.add_installation(record)

        updatable = tracker.get_updatable_instructions()

        assert len(updatable) == 3
        refs = [r.source_ref for r in updatable]
        assert "main" in refs
        assert "develop" in refs
        assert "feature/new" in refs


class TestTrackerVersioningBackwardsCompatibility:
    """Test backwards compatibility with non-versioned installations."""

    def test_add_installation_without_ref_fields(self, tmp_path):
        """Test adding installation without version fields (legacy)."""
        tracker_file = tmp_path / "installations.json"
        tracker = InstallationTracker(tracker_file=tracker_file)

        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            # No source_ref or source_ref_type
        )
        tracker.add_installation(record)

        records = tracker.get_installed_instructions()

        assert len(records) == 1
        assert records[0].source_ref is None
        assert records[0].source_ref_type is None

    def test_read_legacy_installation_json(self, tmp_path):
        """Test reading installations.json without ref fields."""
        import json

        tracker_file = tmp_path / "installations.json"

        # Create legacy JSON without ref fields
        legacy_data = [
            {
                "instruction_name": "legacy-instruction",
                "ai_tool": "cursor",
                "source_repo": "https://github.com/user/repo",
                "installed_path": "/path/to/file.md",
                "installed_at": "2025-10-26T12:00:00",
                "scope": "project",
                # No source_ref or source_ref_type
            }
        ]

        with open(tracker_file, "w") as f:
            json.dump(legacy_data, f)

        tracker = InstallationTracker(tracker_file=tracker_file)
        records = tracker.get_installed_instructions()

        assert len(records) == 1
        assert records[0].instruction_name == "legacy-instruction"
        assert records[0].source_ref is None
        assert records[0].source_ref_type is None

    def test_mixed_legacy_and_versioned_records(self, tmp_path):
        """Test reading mix of legacy and versioned records."""
        import json

        tracker_file = tmp_path / "installations.json"

        mixed_data = [
            {
                "instruction_name": "legacy-instruction",
                "ai_tool": "cursor",
                "source_repo": "https://github.com/user/repo",
                "installed_path": "/path/legacy.md",
                "installed_at": "2025-10-26T12:00:00",
                "scope": "project",
            },
            {
                "instruction_name": "versioned-instruction",
                "ai_tool": "claude",
                "source_repo": "https://github.com/user/repo",
                "installed_path": "/path/versioned.md",
                "installed_at": "2025-10-26T12:00:00",
                "scope": "project",
                "source_ref": "v1.0.0",
                "source_ref_type": "tag",
            },
        ]

        with open(tracker_file, "w") as f:
            json.dump(mixed_data, f)

        tracker = InstallationTracker(tracker_file=tracker_file)
        records = tracker.get_installed_instructions()

        assert len(records) == 2

        legacy = next(r for r in records if r.instruction_name == "legacy-instruction")
        versioned = next(r for r in records if r.instruction_name == "versioned-instruction")

        assert legacy.source_ref is None
        assert versioned.source_ref == "v1.0.0"
        assert versioned.source_ref_type == RefType.TAG
