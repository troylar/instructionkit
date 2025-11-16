"""Unit tests for PackageTracker."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from aiconfigkit.core.models import (
    ComponentStatus,
    ComponentType,
    InstallationScope,
    InstallationStatus,
    InstalledComponent,
    PackageInstallationRecord,
)
from aiconfigkit.storage.package_tracker import PackageTracker


@pytest.fixture
def temp_tracker(tmp_path: Path) -> PackageTracker:
    """Create a temporary package tracker."""
    tracker_file = tmp_path / ".ai-config-kit" / "packages.json"
    return PackageTracker(tracker_file)


@pytest.fixture
def sample_record() -> PackageInstallationRecord:
    """Create a sample package installation record."""
    component = InstalledComponent(
        type=ComponentType.INSTRUCTION,
        name="test-instruction",
        installed_path=".claude/rules/test.md",
        checksum="sha256:abc123",
        status=ComponentStatus.INSTALLED,
    )

    return PackageInstallationRecord(
        package_name="test-package",
        namespace="test/repo",
        version="1.0.0",
        installed_at=datetime.now(),
        updated_at=datetime.now(),
        scope=InstallationScope.PROJECT,
        components=[component],
        status=InstallationStatus.COMPLETE,
    )


class TestPackageTrackerInitialization:
    """Test PackageTracker initialization."""

    def test_creates_tracker_file(self, tmp_path: Path) -> None:
        """Test that tracker file is created on initialization."""
        tracker_file = tmp_path / ".ai-config-kit" / "packages.json"
        _tracker = PackageTracker(tracker_file)

        assert tracker_file.exists()
        assert tracker_file.parent.exists()

    def test_creates_empty_tracker_file(self, tmp_path: Path) -> None:
        """Test that empty tracker file contains empty array."""
        tracker_file = tmp_path / ".ai-config-kit" / "packages.json"
        PackageTracker(tracker_file)

        with open(tracker_file, "r") as f:
            data = json.load(f)

        assert data == []

    def test_existing_tracker_file_not_overwritten(self, tmp_path: Path) -> None:
        """Test that existing tracker file is preserved."""
        tracker_file = tmp_path / ".ai-config-kit" / "packages.json"
        tracker_file.parent.mkdir(parents=True)

        # Create existing file with data
        existing_data = [
            {
                "package_name": "existing",
                "namespace": "test/existing",
                "version": "1.0.0",
                "installed_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "scope": "project",
                "components": [],
                "status": "complete",
            }
        ]
        tracker_file.write_text(json.dumps(existing_data))

        # Initialize tracker
        tracker = PackageTracker(tracker_file)

        # Verify existing data is preserved
        records = tracker.get_installed_packages()
        assert len(records) == 1
        assert records[0].package_name == "existing"


class TestRecordInstallation:
    """Test recording package installations."""

    def test_record_new_installation(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test recording a new package installation."""
        temp_tracker.record_installation(sample_record)

        records = temp_tracker.get_installed_packages()
        assert len(records) == 1
        assert records[0].package_name == "test-package"
        assert records[0].version == "1.0.0"

    def test_record_multiple_installations(self, temp_tracker: PackageTracker) -> None:
        """Test recording multiple package installations."""
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".claude/rules/test.md",
            checksum="checksum",
            status=ComponentStatus.INSTALLED,
        )

        record1 = PackageInstallationRecord(
            package_name="package1",
            namespace="test/package1",
            version="1.0.0",
            installed_at=datetime.now(),
            updated_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )

        record2 = PackageInstallationRecord(
            package_name="package2",
            namespace="test/package2",
            version="2.0.0",
            installed_at=datetime.now(),
            updated_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )

        temp_tracker.record_installation(record1)
        temp_tracker.record_installation(record2)

        records = temp_tracker.get_installed_packages()
        assert len(records) == 2
        assert {r.package_name for r in records} == {"package1", "package2"}

    def test_update_existing_installation(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test updating an existing package installation."""
        # Record initial installation
        temp_tracker.record_installation(sample_record)

        # Update with new version
        updated_record = PackageInstallationRecord(
            package_name="test-package",
            namespace="test/repo",
            version="2.0.0",  # Changed version
            installed_at=sample_record.installed_at,
            updated_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            components=sample_record.components,
            status=InstallationStatus.COMPLETE,
        )

        temp_tracker.record_installation(updated_record)

        # Should still have only one record
        records = temp_tracker.get_installed_packages()
        assert len(records) == 1
        assert records[0].version == "2.0.0"


class TestGetInstalledPackages:
    """Test retrieving installed packages."""

    def test_get_all_packages(self, temp_tracker: PackageTracker) -> None:
        """Test getting all installed packages."""
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".claude/rules/test.md",
            checksum="checksum",
            status=ComponentStatus.INSTALLED,
        )

        # Add multiple packages
        for i in range(3):
            record = PackageInstallationRecord(
                package_name=f"package{i}",
                namespace=f"test/package{i}",
                version="1.0.0",
                installed_at=datetime.now(),
                updated_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                components=[component],
                status=InstallationStatus.COMPLETE,
            )
            temp_tracker.record_installation(record)

        records = temp_tracker.get_installed_packages()
        assert len(records) == 3

    def test_get_packages_by_scope(self, temp_tracker: PackageTracker) -> None:
        """Test filtering packages by scope."""
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".claude/rules/test.md",
            checksum="checksum",
            status=ComponentStatus.INSTALLED,
        )

        # Add project-scoped package
        project_record = PackageInstallationRecord(
            package_name="project-pkg",
            namespace="test/project",
            version="1.0.0",
            installed_at=datetime.now(),
            updated_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )
        temp_tracker.record_installation(project_record)

        # Add global-scoped package
        global_record = PackageInstallationRecord(
            package_name="global-pkg",
            namespace="test/global",
            version="1.0.0",
            installed_at=datetime.now(),
            updated_at=datetime.now(),
            scope=InstallationScope.GLOBAL,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )
        temp_tracker.record_installation(global_record)

        # Filter by project scope
        project_records = temp_tracker.get_installed_packages(scope=InstallationScope.PROJECT)
        assert len(project_records) == 1
        assert project_records[0].package_name == "project-pkg"

        # Filter by global scope
        global_records = temp_tracker.get_installed_packages(scope=InstallationScope.GLOBAL)
        assert len(global_records) == 1
        assert global_records[0].package_name == "global-pkg"

    def test_get_packages_empty_tracker(self, temp_tracker: PackageTracker) -> None:
        """Test getting packages from empty tracker."""
        records = temp_tracker.get_installed_packages()
        assert records == []


class TestGetPackage:
    """Test getting a specific package."""

    def test_get_existing_package(self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord) -> None:
        """Test getting an existing package."""
        temp_tracker.record_installation(sample_record)

        record = temp_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert record is not None
        assert record.package_name == "test-package"
        assert record.version == "1.0.0"

    def test_get_nonexistent_package(self, temp_tracker: PackageTracker) -> None:
        """Test getting a package that doesn't exist."""
        record = temp_tracker.get_package("nonexistent", InstallationScope.PROJECT)
        assert record is None

    def test_get_package_wrong_scope(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test getting a package with wrong scope."""
        # Record with project scope
        temp_tracker.record_installation(sample_record)

        # Try to get with global scope
        record = temp_tracker.get_package("test-package", InstallationScope.GLOBAL)
        assert record is None


class TestUpdatePackage:
    """Test updating package records."""

    def test_update_package_status(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test updating package status."""
        temp_tracker.record_installation(sample_record)

        result = temp_tracker.update_package(
            "test-package",
            InstallationScope.PROJECT,
            status=InstallationStatus.PARTIAL,
        )

        assert result is True
        updated = temp_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert updated is not None
        assert updated.status == InstallationStatus.PARTIAL

    def test_update_package_version(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test updating package version."""
        temp_tracker.record_installation(sample_record)

        result = temp_tracker.update_package(
            "test-package",
            InstallationScope.PROJECT,
            version="2.0.0",
        )

        assert result is True
        updated = temp_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert updated is not None
        assert updated.version == "2.0.0"

    def test_update_package_both_fields(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test updating both status and version."""
        temp_tracker.record_installation(sample_record)

        result = temp_tracker.update_package(
            "test-package",
            InstallationScope.PROJECT,
            status=InstallationStatus.FAILED,
            version="3.0.0",
        )

        assert result is True
        updated = temp_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert updated is not None
        assert updated.status == InstallationStatus.FAILED
        assert updated.version == "3.0.0"

    def test_update_updates_timestamp(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test that update changes the updated_at timestamp."""
        temp_tracker.record_installation(sample_record)
        original = temp_tracker.get_package("test-package", InstallationScope.PROJECT)
        original_timestamp = original.updated_at if original else None

        # Small delay to ensure timestamp changes
        import time

        time.sleep(0.01)

        temp_tracker.update_package(
            "test-package",
            InstallationScope.PROJECT,
            status=InstallationStatus.COMPLETE,
        )

        updated = temp_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert updated is not None
        assert updated.updated_at > original_timestamp

    def test_update_nonexistent_package(self, temp_tracker: PackageTracker) -> None:
        """Test updating a package that doesn't exist."""
        result = temp_tracker.update_package(
            "nonexistent",
            InstallationScope.PROJECT,
            status=InstallationStatus.COMPLETE,
        )
        assert result is False


class TestRemovePackage:
    """Test removing package records."""

    def test_remove_existing_package(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test removing an existing package."""
        temp_tracker.record_installation(sample_record)

        result = temp_tracker.remove_package("test-package", InstallationScope.PROJECT)
        assert result is True

        # Verify package is removed
        record = temp_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert record is None

    def test_remove_nonexistent_package(self, temp_tracker: PackageTracker) -> None:
        """Test removing a package that doesn't exist."""
        result = temp_tracker.remove_package("nonexistent", InstallationScope.PROJECT)
        assert result is False

    def test_remove_package_wrong_scope(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test removing a package with wrong scope."""
        # Record with project scope
        temp_tracker.record_installation(sample_record)

        # Try to remove with global scope
        result = temp_tracker.remove_package("test-package", InstallationScope.GLOBAL)
        assert result is False

        # Verify original package still exists
        record = temp_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert record is not None

    def test_remove_one_of_many_packages(self, temp_tracker: PackageTracker) -> None:
        """Test removing one package when multiple exist."""
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".claude/rules/test.md",
            checksum="checksum",
            status=ComponentStatus.INSTALLED,
        )

        # Add multiple packages
        for i in range(3):
            record = PackageInstallationRecord(
                package_name=f"package{i}",
                namespace=f"test/package{i}",
                version="1.0.0",
                installed_at=datetime.now(),
                updated_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                components=[component],
                status=InstallationStatus.COMPLETE,
            )
            temp_tracker.record_installation(record)

        # Remove one package
        temp_tracker.remove_package("package1", InstallationScope.PROJECT)

        # Verify only that package was removed
        records = temp_tracker.get_installed_packages()
        assert len(records) == 2
        assert {r.package_name for r in records} == {"package0", "package2"}


class TestIsPackageInstalled:
    """Test checking if package is installed."""

    def test_installed_package_returns_true(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test that installed package returns True."""
        temp_tracker.record_installation(sample_record)

        assert temp_tracker.is_package_installed("test-package", InstallationScope.PROJECT) is True

    def test_nonexistent_package_returns_false(self, temp_tracker: PackageTracker) -> None:
        """Test that nonexistent package returns False."""
        assert temp_tracker.is_package_installed("nonexistent", InstallationScope.PROJECT) is False

    def test_wrong_scope_returns_false(
        self, temp_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test that package with wrong scope returns False."""
        # Record with project scope
        temp_tracker.record_installation(sample_record)

        # Check with global scope
        assert temp_tracker.is_package_installed("test-package", InstallationScope.GLOBAL) is False


class TestGetPackageCount:
    """Test getting package count."""

    def test_count_all_packages(self, temp_tracker: PackageTracker) -> None:
        """Test counting all packages."""
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".claude/rules/test.md",
            checksum="checksum",
            status=ComponentStatus.INSTALLED,
        )

        # Add multiple packages
        for i in range(5):
            record = PackageInstallationRecord(
                package_name=f"package{i}",
                namespace=f"test/package{i}",
                version="1.0.0",
                installed_at=datetime.now(),
                updated_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                components=[component],
                status=InstallationStatus.COMPLETE,
            )
            temp_tracker.record_installation(record)

        assert temp_tracker.get_package_count() == 5

    def test_count_by_scope(self, temp_tracker: PackageTracker) -> None:
        """Test counting packages by scope."""
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".claude/rules/test.md",
            checksum="checksum",
            status=ComponentStatus.INSTALLED,
        )

        # Add project-scoped packages
        for i in range(3):
            record = PackageInstallationRecord(
                package_name=f"project{i}",
                namespace=f"test/project{i}",
                version="1.0.0",
                installed_at=datetime.now(),
                updated_at=datetime.now(),
                scope=InstallationScope.PROJECT,
                components=[component],
                status=InstallationStatus.COMPLETE,
            )
            temp_tracker.record_installation(record)

        # Add global-scoped packages
        for i in range(2):
            record = PackageInstallationRecord(
                package_name=f"global{i}",
                namespace=f"test/global{i}",
                version="1.0.0",
                installed_at=datetime.now(),
                updated_at=datetime.now(),
                scope=InstallationScope.GLOBAL,
                components=[component],
                status=InstallationStatus.COMPLETE,
            )
            temp_tracker.record_installation(record)

        assert temp_tracker.get_package_count(scope=InstallationScope.PROJECT) == 3
        assert temp_tracker.get_package_count(scope=InstallationScope.GLOBAL) == 2
        assert temp_tracker.get_package_count() == 5

    def test_count_empty_tracker(self, temp_tracker: PackageTracker) -> None:
        """Test counting packages in empty tracker."""
        assert temp_tracker.get_package_count() == 0


class TestErrorHandling:
    """Test error handling in PackageTracker."""

    def test_invalid_json_in_tracker_file(self, tmp_path: Path) -> None:
        """Test handling of invalid JSON in tracker file."""
        tracker_file = tmp_path / ".ai-config-kit" / "packages.json"
        tracker_file.parent.mkdir(parents=True)

        # Write invalid JSON
        tracker_file.write_text("{invalid json}")

        tracker = PackageTracker(tracker_file)

        # Should return empty list instead of crashing
        records = tracker.get_installed_packages()
        assert records == []

    def test_invalid_record_in_tracker_file(self, tmp_path: Path) -> None:
        """Test handling of invalid record in tracker file."""
        tracker_file = tmp_path / ".ai-config-kit" / "packages.json"
        tracker_file.parent.mkdir(parents=True)

        # Write valid JSON but invalid record (missing required fields)
        invalid_data = [
            {
                "package_name": "valid-package",
                "namespace": "test/valid",
                "version": "1.0.0",
                "installed_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "scope": "project",
                "components": [],
                "status": "complete",
            },
            {
                "package_name": "invalid-package",
                # Missing required fields
            },
        ]
        tracker_file.write_text(json.dumps(invalid_data))

        tracker = PackageTracker(tracker_file)

        # Should skip invalid record and return only valid ones
        records = tracker.get_installed_packages()
        assert len(records) == 1
        assert records[0].package_name == "valid-package"

    def test_missing_tracker_file(self, tmp_path: Path) -> None:
        """Test handling of missing tracker file."""
        tracker_file = tmp_path / ".ai-config-kit" / "packages.json"

        # Don't create the file
        tracker = PackageTracker(tracker_file)

        # Should handle gracefully and return empty list
        records = tracker.get_installed_packages()
        assert records == []

    def test_file_deleted_after_init(self, tmp_path: Path) -> None:
        """Test handling when tracker file is deleted after initialization."""
        import shutil

        tracker_file = tmp_path / ".ai-config-kit" / "packages.json"
        tracker = PackageTracker(tracker_file)

        # File should be created by __init__
        assert tracker_file.exists()

        # Delete the file and its parent directory
        shutil.rmtree(tracker_file.parent)

        # Should handle FileNotFoundError gracefully
        records = tracker._read_records()
        assert records == []

    def test_write_failure_permission_error(self, tmp_path: Path) -> None:
        """Test handling write failures due to permissions."""
        from unittest.mock import mock_open, patch

        tracker_file = tmp_path / ".ai-config-kit" / "packages.json"
        tracker = PackageTracker(tracker_file)

        sample_record = PackageInstallationRecord(
            package_name="test-package",
            version="1.0.0",
            namespace="test/repo",
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            updated_at=datetime.now(),
            components=[],
            status=InstallationStatus.COMPLETE,
        )

        # Mock open to raise PermissionError
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")

            with pytest.raises(PermissionError):
                tracker._write_records([sample_record])
