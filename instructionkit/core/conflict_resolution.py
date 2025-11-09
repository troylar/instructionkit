"""Conflict resolution for instruction and template installations."""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt

from instructionkit.core.checksum import sha256_file, sha256_string
from instructionkit.core.models import ConflictInfo, ConflictResolution, ConflictType, TemplateInstallationRecord
from instructionkit.utils.paths import resolve_conflict_name


class ConflictResolver:
    """Handle file conflicts during instruction installation."""

    def __init__(self, default_strategy: ConflictResolution = ConflictResolution.SKIP):
        """
        Initialize conflict resolver.

        Args:
            default_strategy: Default resolution strategy
        """
        self.default_strategy = default_strategy

    def resolve(
        self, instruction_name: str, target_path: Path, strategy: Optional[ConflictResolution] = None
    ) -> ConflictInfo:
        """
        Resolve a file conflict.

        Args:
            instruction_name: Name of instruction causing conflict
            target_path: Path where file would be installed
            strategy: Resolution strategy (uses default if None)

        Returns:
            ConflictInfo with resolution details
        """
        if strategy is None:
            strategy = self.default_strategy

        # Handle each strategy
        if strategy == ConflictResolution.SKIP:
            return ConflictInfo(
                instruction_name=instruction_name,
                existing_path=str(target_path),
                resolution=ConflictResolution.SKIP,
                new_path=None,
            )

        elif strategy == ConflictResolution.OVERWRITE:
            return ConflictInfo(
                instruction_name=instruction_name,
                existing_path=str(target_path),
                resolution=ConflictResolution.OVERWRITE,
                new_path=str(target_path),  # Same path, will be overwritten
            )

        elif strategy == ConflictResolution.RENAME:
            # Generate new path with auto-increment
            new_path = resolve_conflict_name(target_path)
            return ConflictInfo(
                instruction_name=instruction_name,
                existing_path=str(target_path),
                resolution=ConflictResolution.RENAME,
                new_path=str(new_path),
            )

        else:
            raise ValueError(f"Unknown conflict resolution strategy: {strategy}")

    def should_install(self, conflict_info: ConflictInfo) -> bool:
        """
        Determine if instruction should be installed based on conflict resolution.

        Args:
            conflict_info: Conflict resolution info

        Returns:
            True if installation should proceed
        """
        return conflict_info.resolution != ConflictResolution.SKIP

    def get_install_path(self, original_path: Path, conflict_info: Optional[ConflictInfo] = None) -> Path:
        """
        Get the actual path where file should be installed.

        Args:
            original_path: Original intended path
            conflict_info: Conflict resolution info (if conflict occurred)

        Returns:
            Path where file should be installed
        """
        if conflict_info is None:
            return original_path

        if conflict_info.resolution == ConflictResolution.SKIP:
            # Should not install, but return original for reference
            return original_path

        elif conflict_info.resolution == ConflictResolution.OVERWRITE:
            return original_path

        elif conflict_info.resolution == ConflictResolution.RENAME:
            if conflict_info.new_path:
                return Path(conflict_info.new_path)
            else:
                # Fallback: should not happen
                return original_path

        return original_path


def prompt_conflict_resolution(instruction_name: str) -> ConflictResolution:
    """
    Prompt user for conflict resolution choice.

    Args:
        instruction_name: Name of conflicting instruction

    Returns:
        Selected resolution strategy
    """
    print(f"\nConflict: Instruction '{instruction_name}' already exists.")
    print("How would you like to resolve this?")
    print("  1. Skip (keep existing file)")
    print("  2. Rename (install with auto-incremented name)")
    print("  3. Overwrite (replace existing file)")

    while True:
        choice = input("Enter choice (1/2/3): ").strip()

        if choice == "1":
            return ConflictResolution.SKIP
        elif choice == "2":
            return ConflictResolution.RENAME
        elif choice == "3":
            return ConflictResolution.OVERWRITE
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def check_conflicts(target_paths: list[Path]) -> dict[str, Path]:
    """
    Check which target paths already exist.

    Args:
        target_paths: List of paths to check

    Returns:
        Dictionary mapping instruction names to conflicting paths
    """
    conflicts = {}

    for path in target_paths:
        if path.exists():
            # Extract instruction name from filename
            instruction_name = path.stem
            conflicts[instruction_name] = path

    return conflicts


def batch_resolve_conflicts(conflicts: dict[str, Path], strategy: ConflictResolution) -> dict[str, ConflictInfo]:
    """
    Resolve multiple conflicts with the same strategy.

    Args:
        conflicts: Dictionary of instruction names to conflicting paths
        strategy: Resolution strategy to apply to all

    Returns:
        Dictionary mapping instruction names to conflict resolutions
    """
    resolver = ConflictResolver(default_strategy=strategy)
    resolutions = {}

    for instruction_name, path in conflicts.items():
        resolution = resolver.resolve(instruction_name, path)
        resolutions[instruction_name] = resolution

    return resolutions


# Template Sync System - Checksum-based conflict detection


def detect_conflict(
    installed_file: Path, new_template_content: str, installation_record: TemplateInstallationRecord
) -> ConflictType:
    """
    Detect if conflict exists between installed and new template using checksums.

    Args:
        installed_file: Path to currently installed file
        new_template_content: Content of new template version
        installation_record: Original installation record with checksum

    Returns:
        ConflictType indicating conflict status

    Example:
        >>> from pathlib import Path
        >>> conflict = detect_conflict(
        ...     Path(".cursor/rules/acme.test.md"),
        ...     "new template content",
        ...     installation_record
        ... )
        >>> conflict == ConflictType.NONE
        True
    """
    if not installed_file.exists():
        # File doesn't exist, no conflict
        return ConflictType.NONE

    # Calculate current file checksum
    current_checksum = sha256_file(installed_file)

    # Get original checksum at installation
    original_checksum = installation_record.checksum

    # Calculate new template checksum
    new_checksum = sha256_string(new_template_content)

    # Decision matrix:
    if current_checksum == original_checksum:
        # File unchanged since installation
        if new_checksum == original_checksum:
            return ConflictType.NONE  # No changes anywhere
        else:
            return ConflictType.NONE  # Only remote changed, safe to update
    else:
        # File modified locally
        if new_checksum == original_checksum:
            return ConflictType.LOCAL_MODIFIED  # Only local changed
        else:
            return ConflictType.BOTH_MODIFIED  # Both changed


def prompt_conflict_resolution_template(template_name: str, conflict_type: ConflictType) -> ConflictResolution:
    """
    Interactive prompt for template conflict resolution using Rich.

    Args:
        template_name: Name of conflicting template
        conflict_type: Type of conflict detected

    Returns:
        User's resolution choice

    Example:
        >>> resolution = prompt_conflict_resolution_template(
        ...     "test-command",
        ...     ConflictType.BOTH_MODIFIED
        ... )
    """
    console = Console()

    console.print(f"\n[yellow]⚠️  Conflict detected for '{template_name}'[/yellow]")

    if conflict_type == ConflictType.LOCAL_MODIFIED:
        console.print("Local file was modified since installation")
    elif conflict_type == ConflictType.BOTH_MODIFIED:
        console.print("Both local and remote versions have changes")

    console.print("\nChoose action:")
    console.print("  [K]eep local version (ignore remote update)")
    console.print("  [O]verwrite with remote version (discard local changes)")
    console.print("  [R]ename local and install remote")

    choice = Prompt.ask("Your choice", choices=["k", "o", "r", "K", "O", "R"], default="k").lower()

    return {"k": ConflictResolution.SKIP, "o": ConflictResolution.OVERWRITE, "r": ConflictResolution.RENAME}[choice]


def apply_resolution(template_path: Path, new_content: str, resolution: ConflictResolution) -> Path:
    """
    Apply conflict resolution and install template.

    SAFETY: Automatically creates backups before overwriting files.
    Backups stored in .instructionkit/backups/<timestamp>/

    Args:
        template_path: Original template path
        new_content: New template content
        resolution: How to resolve the conflict

    Returns:
        Path where template was actually installed

    Raises:
        ValueError: If resolution strategy is unknown
    """
    if resolution == ConflictResolution.SKIP:
        # Keep existing file, don't install
        return template_path

    elif resolution == ConflictResolution.OVERWRITE:
        # SAFETY: Create backup before overwriting
        if template_path.exists():
            from instructionkit.utils.backup import create_backup

            backup_path = create_backup(template_path)
            from rich.console import Console

            console = Console()
            console.print(f"[dim]  Backup created: {backup_path.relative_to(backup_path.parent.parent)}[/dim]")

        # Overwrite existing file
        template_path.write_text(new_content, encoding="utf-8")
        return template_path

    elif resolution == ConflictResolution.RENAME:
        # Rename local file and install new one
        # Generate new path with suffix
        renamed_path = resolve_conflict_name(template_path)

        # Rename existing file (this preserves the original)
        if template_path.exists():
            template_path.rename(renamed_path)

        # Install new content at original path
        template_path.write_text(new_content, encoding="utf-8")
        return template_path

    else:
        raise ValueError(f"Unknown conflict resolution strategy: {resolution}")
