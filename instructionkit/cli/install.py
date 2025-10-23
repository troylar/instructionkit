"""Install command implementation."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from instructionkit.ai_tools.detector import get_detector
from instructionkit.core.checksum import ChecksumValidator
from instructionkit.core.conflict_resolution import (
    ConflictResolver,
)
from instructionkit.core.git_operations import GitOperations
from instructionkit.core.models import (
    ConflictResolution,
    InstallationRecord,
    InstallationScope,
)
from instructionkit.core.repository import RepositoryParser
from instructionkit.storage.tracker import InstallationTracker
from instructionkit.utils.project import find_project_root
from instructionkit.utils.validation import is_valid_git_url, normalize_repo_url

console = Console()


def install_instruction(
    name: str,
    repo: str,
    tool: Optional[str] = None,
    conflict_strategy: str = "skip",
    bundle: bool = False,
) -> int:
    """
    Install an instruction from a Git repository.

    All installations are at project level.

    Args:
        name: Instruction or bundle name to install
        repo: Git repository URL
        tool: AI tool to install to (cursor, copilot, etc.)
        conflict_strategy: How to handle conflicts (skip, rename, overwrite)
        bundle: Whether this is a bundle installation

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Validate repository URL
    if not is_valid_git_url(repo):
        console.print(f"[red]Error:[/red] Invalid Git repository URL: {repo}")
        return 1

    # Parse conflict strategy
    try:
        strategy = ConflictResolution(conflict_strategy.lower())
    except ValueError:
        console.print(
            f"[red]Error:[/red] Invalid conflict strategy: {conflict_strategy}. "
            f"Must be 'skip', 'rename', or 'overwrite'."
        )
        return 1

    # Always use project scope
    install_scope = InstallationScope.PROJECT

    # Detect project root
    project_root = find_project_root()
    if project_root is None:
        console.print(
            "[red]Error:[/red] Could not detect project root. "
            "Make sure you're running this command from within a project directory."
        )
        return 1
    console.print(f"Detected project root: [cyan]{project_root}[/cyan]")

    # Check Git is installed
    if not GitOperations.is_git_installed():
        console.print(
            "[red]Error:[/red] Git is not installed. "
            "Please install Git and try again."
        )
        return 1

    # Determine AI tool
    ai_tool = _get_ai_tool(tool)
    if ai_tool is None:
        console.print(
            "[red]Error:[/red] Could not determine AI coding tool. "
            "Please specify with --tool flag."
        )
        return 1

    # Validate AI tool
    validation_error = ai_tool.validate_installation()
    if validation_error:
        console.print(f"[red]Error:[/red] {validation_error}")
        return 1

    console.print(f"Installing to [cyan]{ai_tool.tool_name}[/cyan]...")

    # Clone repository or use local path
    git_ops = GitOperations()
    is_local = git_ops.is_local_path(repo)

    if is_local:
        # Use local directory directly
        try:
            repo_path = git_ops.clone_repository(repo)
            console.print(f"Using local directory: [cyan]{repo_path}[/cyan]")
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to access local directory: {e}")
            return 1
    else:
        # Clone remote repository
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Cloning repository...", total=None)

            try:
                repo_path = git_ops.clone_repository(repo)
            except Exception as e:
                console.print(f"[red]Error:[/red] Failed to clone repository: {e}")
                return 1

    try:
        # Parse repository
        parser = RepositoryParser(repo_path)
        repository = parser.parse()
        repository.url = normalize_repo_url(repo)

        # Get instructions to install
        if bundle:
            instructions = parser.get_instructions_for_bundle(name)
            console.print(
                f"Installing bundle '[cyan]{name}[/cyan]' "
                f"with {len(instructions)} instruction(s)..."
            )
        else:
            instruction = parser.get_instruction_by_name(name)
            if not instruction:
                console.print(f"[red]Error:[/red] Instruction '{name}' not found in repository")
                return 1
            instructions = [instruction]

        # Install instructions
        tracker = InstallationTracker()
        resolver = ConflictResolver(default_strategy=strategy)
        checksum_validator = ChecksumValidator()

        installed_count = 0
        skipped_count = 0

        for instruction in instructions:
            # Check if already exists
            target_path = ai_tool.get_instruction_path(
                instruction.name, install_scope, project_root
            )

            if target_path.exists():
                # Handle conflict
                if strategy == ConflictResolution.SKIP:
                    console.print(
                        f"  [yellow]Skipped:[/yellow] {instruction.name} (already exists)"
                    )
                    skipped_count += 1
                    continue
                elif strategy == ConflictResolution.RENAME:
                    conflict_info = resolver.resolve(instruction.name, target_path, strategy)
                    target_path = Path(conflict_info.new_path)
                    console.print(
                        f"  [yellow]Renamed:[/yellow] {instruction.name} -> "
                        f"{target_path.name}"
                    )
                elif strategy == ConflictResolution.OVERWRITE:
                    console.print(
                        f"  [yellow]Overwriting:[/yellow] {instruction.name}"
                    )

            # Validate checksum
            try:
                checksum_validator.validate(instruction.content, instruction.checksum)
            except Exception as e:
                console.print(f"  [red]Error:[/red] {instruction.name}: {e}")
                continue

            # Install instruction
            try:
                # Write file
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(instruction.content, encoding='utf-8')

                # Track installation
                record = InstallationRecord(
                    instruction_name=instruction.name,
                    ai_tool=ai_tool.tool_type,
                    source_repo=repository.url,
                    installed_path=str(target_path),
                    installed_at=datetime.now(),
                    checksum=instruction.checksum,
                    bundle_name=name if bundle else None,
                    scope=install_scope,
                    project_root=str(project_root) if project_root else None,
                )
                tracker.add_installation(record, project_root)

                console.print(f"  [green]✓[/green] Installed: {instruction.name}")
                installed_count += 1

            except Exception as e:
                console.print(f"  [red]Error:[/red] {instruction.name}: {e}")

        # Summary
        console.print()
        console.print(f"[green]Successfully installed {installed_count} instruction(s)[/green]")
        if skipped_count > 0:
            console.print(f"[yellow]Skipped {skipped_count} existing instruction(s)[/yellow]")

        return 0

    finally:
        # Clean up cloned repository (but not local directories)
        GitOperations.cleanup_repository(repo_path, is_temp=not is_local)


def _get_ai_tool(tool_name: Optional[str]):
    """
    Get AI tool instance from name.

    Args:
        tool_name: Name of AI tool (or None to auto-detect)

    Returns:
        AITool instance or None if not found
    """
    detector = get_detector()

    if tool_name:
        # Use specified tool
        tool = detector.get_tool_by_name(tool_name)
        if tool and not tool.is_installed():
            console.print(f"[yellow]Warning:[/yellow] {tool.tool_name} is not installed")
            return None
        return tool

    # Auto-detect: find first installed tool
    return detector.get_primary_tool()
