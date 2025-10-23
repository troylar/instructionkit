"""Uninstall command implementation."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from instructionkit.ai_tools.detector import get_detector
from instructionkit.core.models import AIToolType, InstallationScope
from instructionkit.storage.tracker import InstallationTracker
from instructionkit.utils.project import find_project_root
from instructionkit.utils.ui import print_error, print_success, print_warning

console = Console()


def uninstall_instruction(
    name: str,
    tool: Optional[str] = None,
    force: bool = False,
) -> int:
    """
    Uninstall an instruction.

    Uninstalls from project level only.

    Args:
        name: Instruction name to uninstall
        tool: Specific AI tool to uninstall from (or None for all)
        force: Skip confirmation prompt

    Returns:
        Exit code (0 for success, 1 for error)
    """
    tracker = InstallationTracker()

    # Detect project root
    project_root = find_project_root()

    # Get installed instructions matching the name (project scope only)
    all_records = tracker.get_installed_instructions(project_root=project_root)
    matching_records = [
        r for r in all_records
        if r.instruction_name == name and r.scope == InstallationScope.PROJECT
    ]

    # Filter by tool if specified
    if tool:
        try:
            ai_tool_type = AIToolType(tool.lower())
            matching_records = [r for r in matching_records if r.ai_tool == ai_tool_type]
        except ValueError:
            print_error(
                f"Invalid AI tool: {tool}. Valid options: cursor, copilot, windsurf, claude",
                console
            )
            return 1

    # Check if instruction is installed
    if not matching_records:
        if tool:
            print_error(f"Instruction '{name}' is not installed for {tool}", console)
        else:
            print_error(f"Instruction '{name}' is not installed", console)
        return 1

    # Show what will be uninstalled
    console.print("\n[yellow]The following will be uninstalled:[/yellow]")
    for record in matching_records:
        console.print(f"  • {record.instruction_name} ({record.ai_tool.value}, {record.scope.value})")

    # Confirm unless --force
    if not force:
        console.print()
        confirm = typer.confirm("Continue with uninstall?", default=False)
        if not confirm:
            console.print("[yellow]Uninstall cancelled[/yellow]")
            return 0

    # Get AI tool detector
    detector = get_detector()

    # Uninstall each record
    removed_count = 0
    error_count = 0

    for record in matching_records:
        ai_tool = detector.get_tool_by_type(record.ai_tool)
        if not ai_tool:
            print_warning(f"Unknown AI tool: {record.ai_tool}", console)
            error_count += 1
            continue

        try:
            # Remove file
            file_path = Path(record.installed_path)
            if file_path.exists():
                file_path.unlink()
            else:
                print_warning(f"File not found: {file_path}", console)

            # Determine scope filter for removal
            scope_filter = record.scope.value

            # Determine project root for removal
            removal_project_root = None
            if record.scope == InstallationScope.PROJECT:
                if record.project_root:
                    removal_project_root = Path(record.project_root)
                elif project_root:
                    removal_project_root = project_root

            # Remove from tracker
            tracker.remove_installation(
                record.instruction_name,
                record.ai_tool,
                project_root=removal_project_root,
                scope_filter=scope_filter
            )

            print_success(
                f"Uninstalled {record.instruction_name} from {ai_tool.tool_name} ({record.scope.value})",
                console
            )
            removed_count += 1

        except Exception as e:
            print_error(f"Failed to uninstall {record.instruction_name}: {e}", console)
            error_count += 1

    # Summary
    console.print()
    if removed_count > 0:
        console.print(f"[green]Successfully uninstalled {removed_count} instruction(s)[/green]")
    if error_count > 0:
        console.print(f"[red]Failed to uninstall {error_count} instruction(s)[/red]")
        return 1

    return 0
