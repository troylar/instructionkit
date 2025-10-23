"""Conflict resolution for instruction installations."""

from pathlib import Path
from typing import Optional

from instructionkit.core.models import ConflictInfo, ConflictResolution
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
        self,
        instruction_name: str,
        target_path: Path,
        strategy: Optional[ConflictResolution] = None
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
                new_path=None
            )

        elif strategy == ConflictResolution.OVERWRITE:
            return ConflictInfo(
                instruction_name=instruction_name,
                existing_path=str(target_path),
                resolution=ConflictResolution.OVERWRITE,
                new_path=str(target_path)  # Same path, will be overwritten
            )

        elif strategy == ConflictResolution.RENAME:
            # Generate new path with auto-increment
            new_path = resolve_conflict_name(target_path)
            return ConflictInfo(
                instruction_name=instruction_name,
                existing_path=str(target_path),
                resolution=ConflictResolution.RENAME,
                new_path=str(new_path)
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

    def get_install_path(
        self,
        original_path: Path,
        conflict_info: Optional[ConflictInfo] = None
    ) -> Path:
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

        if choice == '1':
            return ConflictResolution.SKIP
        elif choice == '2':
            return ConflictResolution.RENAME
        elif choice == '3':
            return ConflictResolution.OVERWRITE
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def check_conflicts(
    target_paths: list[Path]
) -> dict[str, Path]:
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


def batch_resolve_conflicts(
    conflicts: dict[str, Path],
    strategy: ConflictResolution
) -> dict[str, ConflictInfo]:
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
