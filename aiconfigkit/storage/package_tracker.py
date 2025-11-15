"""Package installation tracking and persistence."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from aiconfigkit.core.models import (
    InstallationScope,
    InstallationStatus,
    PackageInstallationRecord,
)

logger = logging.getLogger(__name__)


class PackageTracker:
    """
    Manages tracking of installed packages.

    Stores package installation records in <project-root>/.ai-config-kit/packages.json
    for project-level tracking.
    """

    def __init__(self, tracker_file: Path):
        """
        Initialize package tracker.

        Args:
            tracker_file: Path to package tracker JSON file
        """
        self.tracker_file = tracker_file
        self._ensure_tracker_file()

    def _ensure_tracker_file(self) -> None:
        """Ensure tracker file and directory exist."""
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.tracker_file.exists():
            # Create empty tracker file
            self._write_records([])

    def _read_records(self) -> list[PackageInstallationRecord]:
        """Read all package installation records from file."""
        try:
            with open(self.tracker_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            records = []
            for item in data:
                try:
                    record = PackageInstallationRecord.from_dict(item)
                    records.append(record)
                except Exception as e:
                    logger.warning(f"Skipping invalid package record: {e}")
                    continue

            return records

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in tracker file {self.tracker_file}: {e}")
            return []
        except FileNotFoundError:
            logger.debug(f"Tracker file not found: {self.tracker_file}, will create on first write")
            return []

    def _write_records(self, records: list[PackageInstallationRecord]) -> None:
        """Write all package installation records to file."""
        try:
            data = [record.to_dict() for record in records]

            self.tracker_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.tracker_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Wrote {len(records)} package records to {self.tracker_file}")

        except Exception as e:
            logger.error(f"Failed to write package tracker: {e}")
            raise

    def record_installation(self, record: PackageInstallationRecord) -> None:
        """
        Record a new package installation.

        If a package with the same name and scope already exists, it will be updated.

        Args:
            record: Package installation record to save
        """
        records = self._read_records()

        # Check if package already exists (same name and scope)
        existing_index = None
        for i, existing in enumerate(records):
            if existing.package_name == record.package_name and existing.scope == record.scope:
                existing_index = i
                break

        if existing_index is not None:
            # Update existing record
            logger.info(f"Updating existing package installation: {record.package_name}")
            records[existing_index] = record
        else:
            # Add new record
            logger.info(f"Recording new package installation: {record.package_name}")
            records.append(record)

        self._write_records(records)

    def get_installed_packages(self, scope: Optional[InstallationScope] = None) -> list[PackageInstallationRecord]:
        """
        Get all installed packages.

        Args:
            scope: Filter by installation scope (optional)

        Returns:
            List of package installation records
        """
        records = self._read_records()

        if scope:
            records = [r for r in records if r.scope == scope]

        return records

    def get_package(self, package_name: str, scope: InstallationScope) -> Optional[PackageInstallationRecord]:
        """
        Get installation record for a specific package.

        Args:
            package_name: Name of the package
            scope: Installation scope

        Returns:
            Package installation record, or None if not found
        """
        records = self._read_records()

        for record in records:
            if record.package_name == package_name and record.scope == scope:
                return record

        return None

    def update_package(
        self,
        package_name: str,
        scope: InstallationScope,
        status: Optional[InstallationStatus] = None,
        version: Optional[str] = None,
    ) -> bool:
        """
        Update an existing package installation record.

        Args:
            package_name: Name of the package to update
            scope: Installation scope
            status: New installation status (optional)
            version: New version (optional)

        Returns:
            True if package was found and updated, False otherwise
        """
        records = self._read_records()

        for record in records:
            if record.package_name == package_name and record.scope == scope:
                # Update fields
                if status:
                    record.status = status
                if version:
                    record.version = version
                record.updated_at = datetime.now()

                self._write_records(records)
                logger.info(f"Updated package installation: {package_name}")
                return True

        logger.warning(f"Package not found for update: {package_name} (scope: {scope.value})")
        return False

    def remove_package(self, package_name: str, scope: InstallationScope) -> bool:
        """
        Remove a package installation record.

        Args:
            package_name: Name of the package to remove
            scope: Installation scope

        Returns:
            True if package was found and removed, False otherwise
        """
        records = self._read_records()
        original_count = len(records)

        # Filter out the package to remove
        records = [r for r in records if not (r.package_name == package_name and r.scope == scope)]

        if len(records) < original_count:
            self._write_records(records)
            logger.info(f"Removed package installation: {package_name}")
            return True

        logger.warning(f"Package not found for removal: {package_name} (scope: {scope.value})")
        return False

    def is_package_installed(self, package_name: str, scope: InstallationScope) -> bool:
        """
        Check if a package is installed.

        Args:
            package_name: Name of the package
            scope: Installation scope

        Returns:
            True if package is installed, False otherwise
        """
        return self.get_package(package_name, scope) is not None

    def get_package_count(self, scope: Optional[InstallationScope] = None) -> int:
        """
        Get count of installed packages.

        Args:
            scope: Filter by installation scope (optional)

        Returns:
            Number of installed packages
        """
        return len(self.get_installed_packages(scope))
