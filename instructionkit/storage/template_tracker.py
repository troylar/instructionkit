"""Installation tracking for templates."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from instructionkit.core.models import TemplateInstallationRecord


class TemplateInstallationTracker:
    """Tracks installed templates in projects and globally."""

    def __init__(self, tracking_file: Path):
        """
        Initialize installation tracker.

        Args:
            tracking_file: Path to installations JSON file
        """
        self.tracking_file = tracking_file

    @classmethod
    def for_project(cls, project_root: Path) -> "TemplateInstallationTracker":
        """
        Create tracker for project-level installations.

        Args:
            project_root: Project root directory

        Returns:
            TemplateInstallationTracker instance

        Example:
            >>> from pathlib import Path
            >>> tracker = TemplateInstallationTracker.for_project(Path.cwd())
        """
        tracking_dir = project_root / ".instructionkit"
        tracking_dir.mkdir(parents=True, exist_ok=True)
        tracking_file = tracking_dir / "template-installations.json"
        return cls(tracking_file)

    @classmethod
    def for_global(cls) -> "TemplateInstallationTracker":
        """
        Create tracker for global installations.

        Returns:
            TemplateInstallationTracker instance

        Example:
            >>> tracker = TemplateInstallationTracker.for_global()
        """
        tracking_dir = Path.home() / ".instructionkit"
        tracking_dir.mkdir(parents=True, exist_ok=True)
        tracking_file = tracking_dir / "global-template-installations.json"
        return cls(tracking_file)

    def load_installation_records(self) -> list[TemplateInstallationRecord]:
        """
        Load installation records from JSON file.

        Returns:
            List of installation records (empty if file doesn't exist)

        Example:
            >>> tracker = TemplateInstallationTracker.for_project(Path.cwd())
            >>> records = tracker.load_installation_records()
            >>> len(records)
            0
        """
        if not self.tracking_file.exists():
            return []

        try:
            with open(self.tracking_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            records = []
            for record_data in data.get("installations", []):
                try:
                    record = TemplateInstallationRecord.from_dict(record_data)
                    records.append(record)
                except (ValueError, KeyError) as e:
                    # Skip invalid records
                    print(f"Warning: Skipping invalid installation record: {e}")
                    continue

            return records

        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load installation records: {e}")
            return []

    def save_installation_records(self, records: list[TemplateInstallationRecord]) -> None:
        """
        Save installation records to JSON file.

        Args:
            records: List of installation records to save

        Example:
            >>> tracker = TemplateInstallationTracker.for_project(Path.cwd())
            >>> tracker.save_installation_records([record])
        """
        # Ensure directory exists
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "installations": [record.to_dict() for record in records],
            "last_updated": datetime.now().isoformat(),
            "schema_version": "1.0",
        }

        with open(self.tracking_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_installation(self, record: TemplateInstallationRecord) -> None:
        """
        Add a new installation record.

        Args:
            record: Installation record to add

        Example:
            >>> from instructionkit.core.models import AIToolType, InstallationScope
            >>> from datetime import datetime
            >>> record = TemplateInstallationRecord(
            ...     id="550e8400-e29b-41d4-a716-446655440000",
            ...     template_name="test-command",
            ...     source_repo="acme-templates",
            ...     source_version="1.0.0",
            ...     namespace="acme",
            ...     installed_path="/project/.cursor/rules/acme.test.md",
            ...     scope=InstallationScope.PROJECT,
            ...     installed_at=datetime.now(),
            ...     checksum="a" * 64,
            ...     ide_type=AIToolType.CURSOR
            ... )
            >>> tracker.add_installation(record)
        """
        records = self.load_installation_records()
        records.append(record)
        self.save_installation_records(records)

    def get_installation_by_id(self, installation_id: str) -> Optional[TemplateInstallationRecord]:
        """
        Get installation record by ID.

        Args:
            installation_id: Installation UUID

        Returns:
            Installation record or None if not found

        Example:
            >>> record = tracker.get_installation_by_id("550e8400-...")
        """
        records = self.load_installation_records()
        for record in records:
            if record.id == installation_id:
                return record
        return None

    def get_installations_by_repo(self, source_repo: str) -> list[TemplateInstallationRecord]:
        """
        Get all installations from a specific repository.

        Args:
            source_repo: Repository name

        Returns:
            List of installation records from that repository

        Example:
            >>> records = tracker.get_installations_by_repo("acme-templates")
            >>> len(records)
            3
        """
        records = self.load_installation_records()
        return [r for r in records if r.source_repo == source_repo]

    def get_installations_by_namespace(self, namespace: str) -> list[TemplateInstallationRecord]:
        """
        Get all installations from a specific namespace.

        Args:
            namespace: Repository namespace

        Returns:
            List of installation records with that namespace

        Example:
            >>> records = tracker.get_installations_by_namespace("acme")
        """
        records = self.load_installation_records()
        return [r for r in records if r.namespace == namespace]

    def remove_installation(self, installation_id: str) -> bool:
        """
        Remove an installation record.

        Args:
            installation_id: Installation UUID

        Returns:
            True if removed, False if not found

        Example:
            >>> removed = tracker.remove_installation("550e8400-...")
            >>> removed
            True
        """
        records = self.load_installation_records()
        original_count = len(records)

        records = [r for r in records if r.id != installation_id]

        if len(records) < original_count:
            self.save_installation_records(records)
            return True

        return False

    def remove_installations_by_repo(self, source_repo: str) -> int:
        """
        Remove all installations from a specific repository.

        Args:
            source_repo: Repository name

        Returns:
            Number of installations removed

        Example:
            >>> count = tracker.remove_installations_by_repo("acme-templates")
            >>> count
            3
        """
        records = self.load_installation_records()
        original_count = len(records)

        records = [r for r in records if r.source_repo != source_repo]
        removed_count = original_count - len(records)

        if removed_count > 0:
            self.save_installation_records(records)

        return removed_count

    def update_installation(self, installation_id: str, updated_record: TemplateInstallationRecord) -> bool:
        """
        Update an existing installation record.

        Args:
            installation_id: Installation UUID
            updated_record: New installation record

        Returns:
            True if updated, False if not found

        Example:
            >>> updated = tracker.update_installation("550e8400-...", new_record)
            >>> updated
            True
        """
        records = self.load_installation_records()

        for i, record in enumerate(records):
            if record.id == installation_id:
                records[i] = updated_record
                self.save_installation_records(records)
                return True

        return False

    def get_all_installations(self) -> list[TemplateInstallationRecord]:
        """
        Get all installation records.

        Returns:
            List of all installation records

        Example:
            >>> all_records = tracker.get_all_installations()
        """
        return self.load_installation_records()

    def clear_all_installations(self) -> None:
        """
        Remove all installation records.

        Example:
            >>> tracker.clear_all_installations()
        """
        self.save_installation_records([])
