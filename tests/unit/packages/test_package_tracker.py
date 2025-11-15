"""Unit tests for package installation tracker."""

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
def tracker_file(tmp_path: Path) -> Path:
    """Create a temporary tracker file path."""
    return tmp_path / ".ai-config-kit" / "packages.json"


@pytest.fixture
def package_tracker(tracker_file: Path) -> PackageTracker:
    """Create a package tracker with temporary file."""
    return PackageTracker(tracker_file)


@pytest.fixture
def sample_record() -> PackageInstallationRecord:
    """Create a sample package installation record."""
    now = datetime.now()
    component = InstalledComponent(
        type=ComponentType.INSTRUCTION,
        name="test-instruction",
        installed_path=".cursor/rules/test.mdc",
        checksum="sha256:abc123",
        status=ComponentStatus.INSTALLED,
    )

    return PackageInstallationRecord(
        package_name="test-package",
        namespace="test/repo",
        version="1.0.0",
        installed_at=now,
        updated_at=now,
        scope=InstallationScope.PROJECT,
        components=[component],
        status=InstallationStatus.COMPLETE,
    )


class TestPackageTracker:
    """Test PackageTracker class."""

    def test_init_creates_tracker_file(self, tracker_file: Path) -> None:
        """Test that initialization creates tracker file."""
        tracker = PackageTracker(tracker_file)

        assert tracker_file.exists()
        assert tracker.tracker_file == tracker_file

    def test_init_creates_parent_directory(self, tmp_path: Path) -> None:
        """Test that initialization creates parent directory."""
        tracker_file = tmp_path / "nested" / "dir" / "packages.json"
        tracker = PackageTracker(tracker_file)

        assert tracker_file.parent.exists()
        assert tracker_file.exists()
        assert tracker.tracker_file == tracker_file

    def test_record_installation_new_package(
        self, package_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test recording a new package installation."""
        package_tracker.record_installation(sample_record)

        packages = package_tracker.get_installed_packages()
        assert len(packages) == 1
        assert packages[0].package_name == "test-package"
        assert packages[0].version == "1.0.0"
        assert packages[0].status == InstallationStatus.COMPLETE

    def test_record_installation_updates_existing(
        self, package_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test that recording existing package updates it."""
        # Record initial installation
        package_tracker.record_installation(sample_record)

        # Update the record
        updated_record = sample_record
        updated_record.version = "2.0.0"
        updated_record.status = InstallationStatus.UPDATING

        package_tracker.record_installation(updated_record)

        # Should still have only one record, but updated
        packages = package_tracker.get_installed_packages()
        assert len(packages) == 1
        assert packages[0].version == "2.0.0"
        assert packages[0].status == InstallationStatus.UPDATING

    def test_record_installation_multiple_packages(self, package_tracker: PackageTracker) -> None:
        """Test recording multiple different packages."""
        now = datetime.now()

        # Create two different packages
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".cursor/rules/test.mdc",
            checksum="sha256:abc",
            status=ComponentStatus.INSTALLED,
        )

        record1 = PackageInstallationRecord(
            package_name="package-1",
            namespace="test/repo1",
            version="1.0.0",
            installed_at=now,
            updated_at=now,
            scope=InstallationScope.PROJECT,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )

        record2 = PackageInstallationRecord(
            package_name="package-2",
            namespace="test/repo2",
            version="1.0.0",
            installed_at=now,
            updated_at=now,
            scope=InstallationScope.PROJECT,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )

        package_tracker.record_installation(record1)
        package_tracker.record_installation(record2)

        packages = package_tracker.get_installed_packages()
        assert len(packages) == 2
        assert {p.package_name for p in packages} == {"package-1", "package-2"}

    def test_get_installed_packages_empty(self, package_tracker: PackageTracker) -> None:
        """Test getting packages when none are installed."""
        packages = package_tracker.get_installed_packages()
        assert len(packages) == 0

    def test_get_installed_packages_filtered_by_scope(self, package_tracker: PackageTracker) -> None:
        """Test filtering packages by scope."""
        now = datetime.now()
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".cursor/rules/test.mdc",
            checksum="sha256:abc",
            status=ComponentStatus.INSTALLED,
        )

        # Create records with different scopes
        record1 = PackageInstallationRecord(
            package_name="package-1",
            namespace="test/repo",
            version="1.0.0",
            installed_at=now,
            updated_at=now,
            scope=InstallationScope.PROJECT,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )

        record2 = PackageInstallationRecord(
            package_name="package-2",
            namespace="test/repo",
            version="1.0.0",
            installed_at=now,
            updated_at=now,
            scope=InstallationScope.GLOBAL,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )

        package_tracker.record_installation(record1)
        package_tracker.record_installation(record2)

        # Filter by project scope
        project_packages = package_tracker.get_installed_packages(InstallationScope.PROJECT)
        assert len(project_packages) == 1
        assert project_packages[0].package_name == "package-1"

        # Filter by global scope
        global_packages = package_tracker.get_installed_packages(InstallationScope.GLOBAL)
        assert len(global_packages) == 1
        assert global_packages[0].package_name == "package-2"

    def test_get_package_found(self, package_tracker: PackageTracker, sample_record: PackageInstallationRecord) -> None:
        """Test getting a specific package that exists."""
        package_tracker.record_installation(sample_record)

        package = package_tracker.get_package("test-package", InstallationScope.PROJECT)

        assert package is not None
        assert package.package_name == "test-package"
        assert package.version == "1.0.0"

    def test_get_package_not_found(self, package_tracker: PackageTracker) -> None:
        """Test getting a package that doesn't exist."""
        package = package_tracker.get_package("nonexistent", InstallationScope.PROJECT)

        assert package is None

    def test_update_package_status(
        self, package_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test updating package status."""
        package_tracker.record_installation(sample_record)

        result = package_tracker.update_package(
            "test-package",
            InstallationScope.PROJECT,
            status=InstallationStatus.UPDATING,
        )

        assert result is True

        package = package_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert package.status == InstallationStatus.UPDATING

    def test_update_package_version(
        self, package_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test updating package version."""
        package_tracker.record_installation(sample_record)

        result = package_tracker.update_package(
            "test-package",
            InstallationScope.PROJECT,
            version="2.0.0",
        )

        assert result is True

        package = package_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert package.version == "2.0.0"

    def test_update_package_both_fields(
        self, package_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test updating both status and version."""
        package_tracker.record_installation(sample_record)

        result = package_tracker.update_package(
            "test-package",
            InstallationScope.PROJECT,
            status=InstallationStatus.PARTIAL,
            version="1.5.0",
        )

        assert result is True

        package = package_tracker.get_package("test-package", InstallationScope.PROJECT)
        assert package.status == InstallationStatus.PARTIAL
        assert package.version == "1.5.0"

    def test_update_package_not_found(self, package_tracker: PackageTracker) -> None:
        """Test updating a package that doesn't exist."""
        result = package_tracker.update_package(
            "nonexistent",
            InstallationScope.PROJECT,
            status=InstallationStatus.FAILED,
        )

        assert result is False

    def test_remove_package_found(
        self, package_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test removing a package that exists."""
        package_tracker.record_installation(sample_record)

        result = package_tracker.remove_package("test-package", InstallationScope.PROJECT)

        assert result is True
        assert package_tracker.get_package_count() == 0

    def test_remove_package_not_found(self, package_tracker: PackageTracker) -> None:
        """Test removing a package that doesn't exist."""
        result = package_tracker.remove_package("nonexistent", InstallationScope.PROJECT)

        assert result is False

    def test_is_package_installed_true(
        self, package_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test checking if package is installed (true case)."""
        package_tracker.record_installation(sample_record)

        assert package_tracker.is_package_installed("test-package", InstallationScope.PROJECT)

    def test_is_package_installed_false(self, package_tracker: PackageTracker) -> None:
        """Test checking if package is installed (false case)."""
        assert not package_tracker.is_package_installed("nonexistent", InstallationScope.PROJECT)

    def test_get_package_count_empty(self, package_tracker: PackageTracker) -> None:
        """Test getting package count when empty."""
        assert package_tracker.get_package_count() == 0

    def test_get_package_count_with_packages(
        self, package_tracker: PackageTracker, sample_record: PackageInstallationRecord
    ) -> None:
        """Test getting package count with packages."""
        package_tracker.record_installation(sample_record)

        # Add another package
        now = datetime.now()
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test2",
            installed_path=".cursor/rules/test2.mdc",
            checksum="sha256:def",
            status=ComponentStatus.INSTALLED,
        )

        record2 = PackageInstallationRecord(
            package_name="package-2",
            namespace="test/repo",
            version="1.0.0",
            installed_at=now,
            updated_at=now,
            scope=InstallationScope.PROJECT,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )

        package_tracker.record_installation(record2)

        assert package_tracker.get_package_count() == 2

    def test_get_package_count_filtered_by_scope(self, package_tracker: PackageTracker) -> None:
        """Test getting package count filtered by scope."""
        now = datetime.now()
        component = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".cursor/rules/test.mdc",
            checksum="sha256:abc",
            status=ComponentStatus.INSTALLED,
        )

        # Add project-scoped package
        record1 = PackageInstallationRecord(
            package_name="package-1",
            namespace="test/repo",
            version="1.0.0",
            installed_at=now,
            updated_at=now,
            scope=InstallationScope.PROJECT,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )

        # Add global-scoped package
        record2 = PackageInstallationRecord(
            package_name="package-2",
            namespace="test/repo",
            version="1.0.0",
            installed_at=now,
            updated_at=now,
            scope=InstallationScope.GLOBAL,
            components=[component],
            status=InstallationStatus.COMPLETE,
        )

        package_tracker.record_installation(record1)
        package_tracker.record_installation(record2)

        assert package_tracker.get_package_count() == 2
        assert package_tracker.get_package_count(InstallationScope.PROJECT) == 1
        assert package_tracker.get_package_count(InstallationScope.GLOBAL) == 1

    def test_persistence_across_instances(self, tracker_file: Path, sample_record: PackageInstallationRecord) -> None:
        """Test that data persists across tracker instances."""
        # Create first tracker and record installation
        tracker1 = PackageTracker(tracker_file)
        tracker1.record_installation(sample_record)

        # Create second tracker with same file
        tracker2 = PackageTracker(tracker_file)
        packages = tracker2.get_installed_packages()

        assert len(packages) == 1
        assert packages[0].package_name == "test-package"
