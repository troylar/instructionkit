"""Installation tracking and persistence."""

import json
import logging
from pathlib import Path
from typing import Optional

from instructionkit.core.models import AIToolType, InstallationRecord
from instructionkit.utils.paths import get_installation_tracker_path
from instructionkit.utils.project import get_project_installation_tracker_path

logger = logging.getLogger(__name__)


def _make_path_relative(absolute_path: Path, project_root: Path) -> str:
    """
    Convert absolute path to relative path from project root.

    Args:
        absolute_path: Absolute file path
        project_root: Project root directory

    Returns:
        Relative path string (e.g., ".github/instructions/file.md")
    """
    try:
        return str(absolute_path.relative_to(project_root))
    except ValueError:
        # Path is not relative to project root, return as-is
        logger.warning(f"Path {absolute_path} is not relative to project root {project_root}")
        return str(absolute_path)


def _make_path_absolute(relative_path: str, project_root: Path) -> Path:
    """
    Convert relative path to absolute path using project root.

    Args:
        relative_path: Relative path string
        project_root: Project root directory

    Returns:
        Absolute Path object
    """
    path = Path(relative_path)
    if path.is_absolute():
        # Already absolute (old format), return as-is
        return path
    # Make relative path absolute
    return project_root / path


class InstallationTracker:
    """
    Manages tracking of installed instructions.

    Stores installation records in ~/.instructionkit/installations.json
    """

    def __init__(self, tracker_file: Optional[Path] = None):
        """
        Initialize installation tracker.

        Args:
            tracker_file: Path to tracker JSON file (defaults to standard location)
        """
        self.tracker_file = tracker_file or get_installation_tracker_path()
        self._ensure_tracker_file()

    def _ensure_tracker_file(self) -> None:
        """Ensure tracker file and directory exist."""
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.tracker_file.exists():
            # Create empty tracker file
            self._write_records([])

    def _read_records(self) -> list[InstallationRecord]:
        """Read all installation records from file."""
        try:
            with open(self.tracker_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            records = []
            for item in data:
                try:
                    record = InstallationRecord.from_dict(item)
                    records.append(record)
                except Exception as e:
                    logger.warning(f"Skipping invalid installation record: {e}")
                    continue

            return records

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in tracker file {self.tracker_file}: {e}")
            return []
        except FileNotFoundError:
            logger.debug(f"Tracker file not found: {self.tracker_file}, will create on first write")
            return []

    def _write_records(self, records: list[InstallationRecord]) -> None:
        """Write installation records to file."""
        data = [record.to_dict() for record in records]

        with open(self.tracker_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_installation(self, record: InstallationRecord, project_root: Optional[Path] = None) -> None:
        """
        Add an installation record.

        Args:
            record: Installation record to add
            project_root: Project root for project-scoped installations
        """
        # Determine which tracker file to use
        if project_root:
            tracker_file = get_project_installation_tracker_path(project_root)
            # Ensure project tracker file exists
            tracker_file.parent.mkdir(parents=True, exist_ok=True)
            if not tracker_file.exists():
                tracker_file.write_text("[]", encoding="utf-8")

            # Convert installed_path to relative for project-scoped installations
            # Create a new record with relative path for storage
            installed_path_abs = Path(record.installed_path)
            relative_path = _make_path_relative(installed_path_abs, project_root)

            # Create a copy of the record with relative path for storage
            storage_record = InstallationRecord(
                instruction_name=record.instruction_name,
                ai_tool=record.ai_tool,
                source_repo=record.source_repo,
                installed_path=relative_path,
                installed_at=record.installed_at,
                checksum=record.checksum,
                bundle_name=record.bundle_name,
                scope=record.scope,
                source_ref=record.source_ref,
                source_ref_type=record.source_ref_type,
            )
        else:
            tracker_file = self.tracker_file
            storage_record = record  # For global scope, use absolute paths

        # Read records from appropriate file
        try:
            with open(tracker_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            records = [InstallationRecord.from_dict(item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            records = []

        # Remove any existing record for same instruction + tool + scope
        records = [
            r
            for r in records
            if not (
                r.instruction_name == storage_record.instruction_name
                and r.ai_tool == storage_record.ai_tool
                and r.scope == storage_record.scope
            )
        ]

        # Add new record (with relative path if project-scoped)
        records.append(storage_record)

        # Write back to appropriate file
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in records], f, indent=2, ensure_ascii=False)

    def remove_installation(
        self,
        instruction_name: str,
        ai_tool: Optional[AIToolType] = None,
        project_root: Optional[Path] = None,
        scope_filter: Optional[str] = None,
    ) -> list[InstallationRecord]:
        """
        Remove installation record(s).

        Args:
            instruction_name: Name of instruction to remove
            ai_tool: Specific AI tool (if None, removes from all tools)
            project_root: Project root for project-scoped removals
            scope_filter: Filter by scope ('global', 'project', or None for both)

        Returns:
            List of removed records
        """

        removed = []

        # Handle global installations
        if scope_filter is None or scope_filter == "global":
            records = self._read_records()
            global_removed = []
            remaining = []

            for record in records:
                if record.instruction_name == instruction_name:
                    if ai_tool is None or record.ai_tool == ai_tool:
                        global_removed.append(record)
                    else:
                        remaining.append(record)
                else:
                    remaining.append(record)

            self._write_records(remaining)
            removed.extend(global_removed)

        # Handle project installations
        if project_root and (scope_filter is None or scope_filter == "project"):
            tracker_file = get_project_installation_tracker_path(project_root)
            if tracker_file.exists():
                try:
                    with open(tracker_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    records = [InstallationRecord.from_dict(item) for item in data]

                    project_removed = []
                    remaining = []

                    for record in records:
                        if record.instruction_name == instruction_name:
                            if ai_tool is None or record.ai_tool == ai_tool:
                                project_removed.append(record)
                            else:
                                remaining.append(record)
                        else:
                            remaining.append(record)

                    with open(tracker_file, "w", encoding="utf-8") as f:
                        json.dump([r.to_dict() for r in remaining], f, indent=2, ensure_ascii=False)

                    removed.extend(project_removed)
                except (json.JSONDecodeError, FileNotFoundError):
                    pass

        return removed

    def get_installed_instructions(
        self,
        ai_tool: Optional[AIToolType] = None,
        project_root: Optional[Path] = None,
        include_project: bool = True,
        include_global: bool = True,
    ) -> list[InstallationRecord]:
        """
        Get all installed instructions.

        Args:
            ai_tool: Filter by AI tool (if None, returns all)
            project_root: Project root to include project-scoped installations
            include_project: Whether to include project-scoped installations
            include_global: Whether to include global installations

        Returns:
            List of installation records (paths converted to absolute for project-scoped records)
        """
        all_records = []

        # Get global installations
        if include_global:
            global_records = self._read_records()
            all_records.extend(global_records)

        # Get project installations
        if include_project and project_root:
            tracker_file = get_project_installation_tracker_path(project_root)
            if tracker_file.exists():
                try:
                    with open(tracker_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    project_records = [InstallationRecord.from_dict(item) for item in data]

                    # Convert relative paths to absolute for project-scoped records
                    for record in project_records:
                        abs_path = _make_path_absolute(record.installed_path, project_root)
                        # Update the record with absolute path for compatibility
                        record.installed_path = str(abs_path)

                    all_records.extend(project_records)
                except (json.JSONDecodeError, FileNotFoundError):
                    pass

        # Filter by AI tool if specified
        if ai_tool is not None:
            all_records = [r for r in all_records if r.ai_tool == ai_tool]

        return all_records

    def is_installed(self, instruction_name: str, ai_tool: Optional[AIToolType] = None) -> bool:
        """
        Check if an instruction is installed.

        Args:
            instruction_name: Name of instruction
            ai_tool: Specific AI tool (if None, checks any tool)

        Returns:
            True if instruction is installed
        """
        records = self._read_records()

        for record in records:
            if record.instruction_name == instruction_name:
                if ai_tool is None or record.ai_tool == ai_tool:
                    return True

        return False

    def get_installation(
        self, instruction_name: str, ai_tool: AIToolType, project_root: Optional[Path] = None
    ) -> Optional[InstallationRecord]:
        """
        Get installation record for specific instruction and tool.

        Args:
            instruction_name: Name of instruction
            ai_tool: AI tool type
            project_root: Project root for project-scoped search

        Returns:
            Installation record if found, None otherwise
        """
        records = self.get_installed_instructions(project_root=project_root)

        for record in records:
            if record.instruction_name == instruction_name and record.ai_tool == ai_tool:
                return record

        return None

    def get_installations_from_repo(self, repo_url: str) -> list[InstallationRecord]:
        """
        Get all installations from a specific repository.

        Args:
            repo_url: Repository URL

        Returns:
            List of installation records from this repo
        """
        records = self._read_records()
        return [r for r in records if r.source_repo == repo_url]

    def get_bundle_installations(self, bundle_name: str) -> list[InstallationRecord]:
        """
        Get all installations that were part of a bundle.

        Args:
            bundle_name: Name of bundle

        Returns:
            List of installation records from this bundle
        """
        records = self._read_records()
        return [r for r in records if r.bundle_name == bundle_name]

    def find_instructions_by_name(
        self, instruction_name: str, project_root: Optional[Path] = None
    ) -> list[InstallationRecord]:
        """
        Find all installations with a specific instruction name.

        Args:
            instruction_name: Name of instruction to search for
            project_root: Project root for project-scoped search (None for all scopes)

        Returns:
            List of installation records with this name
        """
        records = self.get_installed_instructions(project_root=project_root)
        return [r for r in records if r.instruction_name == instruction_name]

    def list_installations(self) -> list[InstallationRecord]:
        """
        Get all installation records.

        Returns:
            List of all installation records
        """
        return self._read_records()

    def clear_all(self) -> None:
        """Clear all installation records (for testing)."""
        self._write_records([])

    def get_updatable_instructions(self, project_root: Optional[Path] = None) -> list[InstallationRecord]:
        """
        Get installations that can be updated (from mutable refs like branches).

        Args:
            project_root: Project root to include project-scoped installations

        Returns:
            List of installation records with mutable source refs (branches)
        """
        from instructionkit.core.models import RefType

        all_records = self.get_installed_instructions(project_root=project_root)

        # Filter to only branch-based installations (mutable)
        updatable = []
        for record in all_records:
            # If no ref type specified, assume it's updatable (old format or default branch)
            if not record.source_ref_type:
                updatable.append(record)
            # Only branches are updatable
            elif record.source_ref_type == RefType.BRANCH:
                updatable.append(record)
            # Tags and commits are immutable, skip them

        return updatable
