"""Tests for template installation tracking."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from aiconfigkit.core.models import AIToolType, InstallationScope, TemplateInstallationRecord
from aiconfigkit.storage.template_tracker import TemplateInstallationTracker


@pytest.fixture
def sample_record():
    """Create a sample installation record."""
    return TemplateInstallationRecord(
        id="550e8400-e29b-41d4-a716-446655440000",
        template_name="test-command",
        source_repo="acme-templates",
        source_version="1.0.0",
        namespace="acme",
        installed_path="/project/.claude/commands/acme.test-command.md",
        scope=InstallationScope.PROJECT,
        installed_at=datetime(2024, 1, 15, 10, 30, 0),
        checksum="a" * 64,
        ide_type=AIToolType.CLAUDE,
    )


@pytest.fixture
def sample_record_2():
    """Create a second sample installation record."""
    return TemplateInstallationRecord(
        id="660f9511-f3ac-52e5-b827-557766551111",
        template_name="python-standards",
        source_repo="acme-templates",
        source_version="1.0.0",
        namespace="acme",
        installed_path="/project/.claude/rules/acme.python-standards.md",
        scope=InstallationScope.PROJECT,
        installed_at=datetime(2024, 1, 15, 11, 0, 0),
        checksum="b" * 64,
        ide_type=AIToolType.CLAUDE,
    )


@pytest.fixture
def different_repo_record():
    """Create a record from a different repository."""
    return TemplateInstallationRecord(
        id="770f9622-f4bd-63f6-c938-668877662222",
        template_name="api-docs",
        source_repo="company-templates",
        source_version="2.0.0",
        namespace="company",
        installed_path="/project/.cursor/rules/company.api-docs.mdc",
        scope=InstallationScope.PROJECT,
        installed_at=datetime(2024, 1, 16, 9, 0, 0),
        checksum="c" * 64,
        ide_type=AIToolType.CURSOR,
    )


class TestTemplateInstallationTrackerInit:
    """Tests for TemplateInstallationTracker initialization."""

    def test_init_with_tracking_file(self, tmp_path):
        """Test initialization with tracking file path."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        assert tracker.tracking_file == tracking_file

    def test_for_project(self, tmp_path):
        """Test creating tracker for project."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        tracker = TemplateInstallationTracker.for_project(project_root)

        expected_file = project_root / ".instructionkit" / "template-installations.json"
        assert tracker.tracking_file == expected_file
        assert expected_file.parent.exists()

    def test_for_global(self):
        """Test creating tracker for global installations."""
        tracker = TemplateInstallationTracker.for_global()

        expected_file = Path.home() / ".instructionkit" / "global-template-installations.json"
        assert tracker.tracking_file == expected_file


class TestLoadInstallationRecords:
    """Tests for load_installation_records method."""

    def test_load_empty_returns_empty_list(self, tmp_path):
        """Test loading when file doesn't exist returns empty list."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        records = tracker.load_installation_records()

        assert records == []

    def test_load_valid_records(self, tmp_path, sample_record, sample_record_2):
        """Test loading valid installation records."""
        tracking_file = tmp_path / "installations.json"

        # Create valid JSON file
        data = {
            "installations": [sample_record.to_dict(), sample_record_2.to_dict()],
            "last_updated": "2024-01-15T12:00:00",
            "schema_version": "1.0",
        }

        tracking_file.write_text(json.dumps(data, indent=2))

        tracker = TemplateInstallationTracker(tracking_file)
        records = tracker.load_installation_records()

        assert len(records) == 2
        assert records[0].id == sample_record.id
        assert records[0].template_name == "test-command"
        assert records[1].id == sample_record_2.id
        assert records[1].template_name == "python-standards"

    def test_load_invalid_json_returns_empty(self, tmp_path, capsys):
        """Test loading invalid JSON returns empty list with warning."""
        tracking_file = tmp_path / "installations.json"
        tracking_file.write_text("not valid json{")

        tracker = TemplateInstallationTracker(tracking_file)
        records = tracker.load_installation_records()

        assert records == []

        # Check warning was printed
        captured = capsys.readouterr()
        assert "Warning: Failed to load installation records" in captured.out

    def test_load_skips_invalid_records(self, tmp_path, sample_record, capsys):
        """Test that invalid records are skipped with warning."""
        tracking_file = tmp_path / "installations.json"

        # Create data with one valid and one invalid record
        data = {
            "installations": [
                sample_record.to_dict(),
                {"invalid": "record", "missing": "required_fields"},
            ],
            "last_updated": "2024-01-15T12:00:00",
            "schema_version": "1.0",
        }

        tracking_file.write_text(json.dumps(data, indent=2))

        tracker = TemplateInstallationTracker(tracking_file)
        records = tracker.load_installation_records()

        assert len(records) == 1
        assert records[0].id == sample_record.id

        # Check warning was printed
        captured = capsys.readouterr()
        assert "Warning: Skipping invalid installation record" in captured.out


class TestSaveInstallationRecords:
    """Tests for save_installation_records method."""

    def test_save_empty_list(self, tmp_path):
        """Test saving empty list creates valid JSON."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.save_installation_records([])

        assert tracking_file.exists()

        data = json.loads(tracking_file.read_text())
        assert data["installations"] == []
        assert "last_updated" in data
        assert data["schema_version"] == "1.0"

    def test_save_records(self, tmp_path, sample_record, sample_record_2):
        """Test saving records to JSON file."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.save_installation_records([sample_record, sample_record_2])

        assert tracking_file.exists()

        data = json.loads(tracking_file.read_text())
        assert len(data["installations"]) == 2
        assert data["installations"][0]["id"] == sample_record.id
        assert data["installations"][1]["id"] == sample_record_2.id

    def test_save_creates_parent_directory(self, tmp_path):
        """Test that save creates parent directory if needed."""
        tracking_file = tmp_path / "nested" / "dir" / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.save_installation_records([])

        assert tracking_file.exists()
        assert tracking_file.parent.exists()


class TestAddInstallation:
    """Tests for add_installation method."""

    def test_add_to_empty(self, tmp_path, sample_record):
        """Test adding installation to empty tracker."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)

        records = tracker.load_installation_records()
        assert len(records) == 1
        assert records[0].id == sample_record.id

    def test_add_multiple(self, tmp_path, sample_record, sample_record_2):
        """Test adding multiple installations."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)
        tracker.add_installation(sample_record_2)

        records = tracker.load_installation_records()
        assert len(records) == 2


class TestGetInstallationById:
    """Tests for get_installation_by_id method."""

    def test_get_existing_installation(self, tmp_path, sample_record, sample_record_2):
        """Test getting existing installation by ID."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)
        tracker.add_installation(sample_record_2)

        found = tracker.get_installation_by_id(sample_record.id)

        assert found is not None
        assert found.id == sample_record.id
        assert found.template_name == "test-command"

    def test_get_nonexistent_installation(self, tmp_path):
        """Test getting non-existent installation returns None."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        found = tracker.get_installation_by_id("nonexistent-id")

        assert found is None


class TestGetInstallationsByRepo:
    """Tests for get_installations_by_repo method."""

    def test_get_by_repo(self, tmp_path, sample_record, sample_record_2, different_repo_record):
        """Test getting installations from specific repository."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)
        tracker.add_installation(sample_record_2)
        tracker.add_installation(different_repo_record)

        acme_records = tracker.get_installations_by_repo("acme-templates")

        assert len(acme_records) == 2
        assert all(r.source_repo == "acme-templates" for r in acme_records)

    def test_get_by_repo_none_found(self, tmp_path, sample_record):
        """Test getting installations when none match repository."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)

        records = tracker.get_installations_by_repo("nonexistent-repo")

        assert records == []


class TestGetInstallationsByNamespace:
    """Tests for get_installations_by_namespace method."""

    def test_get_by_namespace(self, tmp_path, sample_record, sample_record_2, different_repo_record):
        """Test getting installations from specific namespace."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)
        tracker.add_installation(sample_record_2)
        tracker.add_installation(different_repo_record)

        acme_records = tracker.get_installations_by_namespace("acme")

        assert len(acme_records) == 2
        assert all(r.namespace == "acme" for r in acme_records)

    def test_get_by_namespace_none_found(self, tmp_path, sample_record):
        """Test getting installations when none match namespace."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)

        records = tracker.get_installations_by_namespace("nonexistent")

        assert records == []


class TestRemoveInstallation:
    """Tests for remove_installation method."""

    def test_remove_existing(self, tmp_path, sample_record, sample_record_2):
        """Test removing existing installation."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)
        tracker.add_installation(sample_record_2)

        result = tracker.remove_installation(sample_record.id)

        assert result is True

        records = tracker.load_installation_records()
        assert len(records) == 1
        assert records[0].id == sample_record_2.id

    def test_remove_nonexistent(self, tmp_path, sample_record):
        """Test removing non-existent installation returns False."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)

        result = tracker.remove_installation("nonexistent-id")

        assert result is False

        records = tracker.load_installation_records()
        assert len(records) == 1


class TestRemoveInstallationsByRepo:
    """Tests for remove_installations_by_repo method."""

    def test_remove_by_repo(self, tmp_path, sample_record, sample_record_2, different_repo_record):
        """Test removing all installations from a repository."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)
        tracker.add_installation(sample_record_2)
        tracker.add_installation(different_repo_record)

        count = tracker.remove_installations_by_repo("acme-templates")

        assert count == 2

        remaining = tracker.load_installation_records()
        assert len(remaining) == 1
        assert remaining[0].source_repo == "company-templates"

    def test_remove_by_repo_none_found(self, tmp_path, sample_record):
        """Test removing installations when none match repository."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)

        count = tracker.remove_installations_by_repo("nonexistent-repo")

        assert count == 0

        records = tracker.load_installation_records()
        assert len(records) == 1


class TestUpdateInstallation:
    """Tests for update_installation method."""

    def test_update_existing(self, tmp_path, sample_record):
        """Test updating existing installation."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)

        # Create updated record
        updated_record = TemplateInstallationRecord(
            id=sample_record.id,
            template_name="updated-command",
            source_repo="acme-templates",
            source_version="2.0.0",
            namespace="acme",
            installed_path="/project/.claude/commands/acme.updated.md",
            scope=InstallationScope.PROJECT,
            installed_at=datetime(2024, 1, 16, 10, 0, 0),
            checksum="d" * 64,
            ide_type=AIToolType.CLAUDE,
        )

        result = tracker.update_installation(sample_record.id, updated_record)

        assert result is True

        records = tracker.load_installation_records()
        assert len(records) == 1
        assert records[0].template_name == "updated-command"
        assert records[0].source_version == "2.0.0"

    def test_update_nonexistent(self, tmp_path, sample_record):
        """Test updating non-existent installation returns False."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        result = tracker.update_installation("nonexistent-id", sample_record)

        assert result is False


class TestGetAllInstallations:
    """Tests for get_all_installations method."""

    def test_get_all(self, tmp_path, sample_record, sample_record_2):
        """Test getting all installations."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)
        tracker.add_installation(sample_record_2)

        all_records = tracker.get_all_installations()

        assert len(all_records) == 2

    def test_get_all_empty(self, tmp_path):
        """Test getting all installations when empty."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        all_records = tracker.get_all_installations()

        assert all_records == []


class TestClearAllInstallations:
    """Tests for clear_all_installations method."""

    def test_clear_all(self, tmp_path, sample_record, sample_record_2):
        """Test clearing all installations."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.add_installation(sample_record)
        tracker.add_installation(sample_record_2)

        tracker.clear_all_installations()

        records = tracker.load_installation_records()
        assert records == []

    def test_clear_already_empty(self, tmp_path):
        """Test clearing when already empty."""
        tracking_file = tmp_path / "installations.json"
        tracker = TemplateInstallationTracker(tracking_file)

        tracker.clear_all_installations()

        records = tracker.load_installation_records()
        assert records == []
