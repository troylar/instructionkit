"""Refactored install command with library support."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from instructionkit.ai_tools.detector import get_detector
from instructionkit.core.conflict_resolution import ConflictResolver
from instructionkit.core.models import (
    ConflictResolution,
    InstallationRecord,
    InstallationScope,
)
from instructionkit.storage.library import LibraryManager
from instructionkit.storage.tracker import InstallationTracker
from instructionkit.tui.installer import show_installer_tui
from instructionkit.utils.project import find_project_root
from instructionkit.utils.ui import print_error, print_info, print_success

console = Console()


# ============================================================================
# Helper Functions - Shared Installation Logic
# ============================================================================

def _parse_conflict_strategy(conflict_strategy: str) -> Optional[ConflictResolution]:
    """Parse and validate conflict resolution strategy.

    Args:
        conflict_strategy: Strategy string (skip, rename, overwrite)

    Returns:
        ConflictResolution enum or None if invalid
    """
    try:
        return ConflictResolution(conflict_strategy.lower())
    except ValueError:
        print_error(
            f"Invalid conflict strategy: {conflict_strategy}. "
            "Must be 'skip', 'rename', or 'overwrite'."
        )
        return None


def _get_project_root_for_installation() -> Optional[Path]:
    """Detect and validate project root for installation.

    Returns:
        Project root path or None if not found
    """
    project_root = find_project_root()
    if not project_root:
        print_error(
            "Could not detect project root. "
            "Make sure you're running from within a project directory."
        )
        return None
    console.print(f"Detected project root: [cyan]{project_root}[/cyan]")
    return project_root


def _load_instructions_from_library(
    instruction_ids: list[str],
    library: LibraryManager
) -> Optional[list]:
    """Load instructions from library by IDs.

    Args:
        instruction_ids: List of instruction IDs to load
        library: Library manager instance

    Returns:
        List of LibraryInstruction objects or None if any not found
    """
    instructions = []
    for inst_id in instruction_ids:
        inst = library.get_instruction(inst_id)
        if not inst:
            print_error(f"Instruction not found in library: {inst_id}")
            return None
        instructions.append(inst)
    return instructions


def _resolve_name_conflicts(
    instructions: list
) -> Optional[dict[str, str]]:
    """Resolve naming conflicts for instructions with duplicate names.

    Args:
        instructions: List of LibraryInstruction objects

    Returns:
        Dict mapping instruction ID to install name, or None if cancelled
    """
    # Check for name conflicts
    name_conflicts = {}
    for inst in instructions:
        if inst.name not in name_conflicts:
            name_conflicts[inst.name] = []
        name_conflicts[inst.name].append(inst)

    # Handle conflicts
    install_names = {}  # Map instruction ID to final install name
    for name, insts in name_conflicts.items():
        if len(insts) > 1:
            console.print(
                f"\n[yellow]⚠️  Name Conflict:[/yellow] "
                f"{len(insts)} instructions named '{name}'"
            )
            console.print("\nHow should they be installed?")
            console.print("  [1] Namespace by repository (recommended)")
            for inst in insts:
                console.print(f"      → {inst.repo_namespace}/{name}")
            console.print("  [2] Skip installation (cancel)")

            choice = typer.prompt("Select (1-2)", default="1")

            if choice == "1":
                # Use namespaced names
                for inst in insts:
                    install_names[inst.id] = f"{inst.repo_namespace}/{name}"
            else:
                print_info("Installation cancelled")
                return None
        else:
            # No conflict, use simple name
            install_names[insts[0].id] = name

    return install_names


def _get_ai_tools_from_names(
    tool_names: list[str],
    detector
) -> Optional[list]:
    """Get AI tool instances from tool names.

    Args:
        tool_names: List of tool name strings
        detector: AI tool detector instance

    Returns:
        List of AITool instances or None if any invalid/not installed
    """
    ai_tools = []
    for tool_name in tool_names:
        tool = detector.get_tool_by_name(tool_name)
        if not tool:
            print_error(f"AI tool not found: {tool_name}")
            return None
        if not tool.is_installed():
            print_error(f"{tool.tool_name} is not installed")
            return None
        ai_tools.append(tool)
    return ai_tools


def _show_installation_preview(
    project_root: Path,
    instructions: list,
    ai_tools: list,
    install_names: dict[str, str]
) -> bool:
    """Show installation preview and ask for confirmation.

    Args:
        project_root: Project root path
        instructions: List of instructions to install
        ai_tools: List of AI tools to install to
        install_names: Mapping of instruction IDs to install names

    Returns:
        True if user confirms, False otherwise
    """
    console.print("\n[bold cyan]📦 Installation Preview[/bold cyan]")
    console.print(f"\n[bold]Project:[/bold] {project_root}")
    console.print(f"[bold]Instructions:[/bold] {len(instructions)} selected")
    console.print(
        f"[bold]Target tools:[/bold] {', '.join([t.tool_name for t in ai_tools])}\n"
    )

    # Show where files will be created
    console.print("[bold yellow]The following files will be created:[/bold yellow]\n")

    for ai_tool in ai_tools:
        tool_dir = ai_tool.get_project_instructions_directory(project_root)
        console.print(f"[cyan]{ai_tool.tool_name}[/cyan] → {tool_dir}")
        for inst in instructions:
            install_name = install_names[inst.id]
            filename = f"{install_name}{ai_tool.get_instruction_file_extension()}"
            console.print(f"  • {filename}")
        console.print()

    # Ask for confirmation
    from rich.prompt import Confirm
    return Confirm.ask("\n[bold]Proceed with installation?[/bold]", default=True)


def _perform_installation(
    instructions: list,
    ai_tools: list,
    install_names: dict[str, str],
    install_scope: InstallationScope,
    project_root: Optional[Path],
    strategy: ConflictResolution
) -> tuple[int, int]:
    """Perform the actual installation of instructions to tools.

    Args:
        instructions: List of instructions to install
        ai_tools: List of AI tools to install to
        install_names: Mapping of instruction IDs to install names
        install_scope: Installation scope (project/global)
        project_root: Project root path
        strategy: Conflict resolution strategy

    Returns:
        Tuple of (installed_count, skipped_count)
    """
    tracker = InstallationTracker()
    resolver = ConflictResolver(default_strategy=strategy)

    installed_count = 0
    skipped_count = 0

    for ai_tool in ai_tools:
        console.print(f"\nInstalling to [cyan]{ai_tool.tool_name}[/cyan]...")

        for inst in instructions:
            install_name = install_names[inst.id]

            # Get target path
            target_path = ai_tool.get_instruction_path(
                install_name, install_scope, project_root
            )

            # Handle existing files
            if target_path.exists():
                if strategy == ConflictResolution.SKIP:
                    console.print(
                        f"  [yellow]Skipped:[/yellow] {install_name} (already exists)"
                    )
                    skipped_count += 1
                    continue
                elif strategy == ConflictResolution.RENAME:
                    conflict_info = resolver.resolve(install_name, target_path, strategy)
                    target_path = Path(conflict_info.new_path)
                    console.print(
                        f"  [yellow]Renamed:[/yellow] {install_name} -> {target_path.name}"
                    )
                elif strategy == ConflictResolution.OVERWRITE:
                    console.print(f"  [yellow]Overwriting:[/yellow] {install_name}")

            # Copy file from library
            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Read from library
                source_path = Path(inst.file_path)
                content = source_path.read_text(encoding='utf-8')

                # Write to target
                target_path.write_text(content, encoding='utf-8')

                # Track installation
                record = InstallationRecord(
                    instruction_name=install_name,
                    ai_tool=ai_tool.tool_type,
                    source_repo=inst.repo_url,
                    installed_path=str(target_path),
                    installed_at=datetime.now(),
                    checksum=inst.checksum,
                    bundle_name=None,
                    scope=install_scope,
                    project_root=str(project_root) if project_root else None,
                )
                tracker.add_installation(record, project_root)

                console.print(f"  [green]✓[/green] Installed: {install_name}")
                installed_count += 1

            except Exception as e:
                print_error(f"Failed to install {install_name}: {e}")

    return installed_count, skipped_count


# ============================================================================
# Public Installation Functions
# ============================================================================


def install_from_library_tui(
    tool: Optional[str] = None,
) -> int:
    """
    Show TUI to select and install instructions from library.

    Args:
        tool: AI tool to install to (None = auto-detect)

    Returns:
        Exit code
    """
    library = LibraryManager()

    # Check if library is empty
    if not library.list_instructions():
        print_info(
            "Library is empty. Use 'instructionkit download --repo <url>' to add instructions."
        )
        return 1

    # Show TUI (always installs to project level)
    result = show_installer_tui(library=library, tool=tool)

    if not result:
        console.print("[dim]Cancelled[/dim]")
        return 0

    # Install selected instructions
    selected_instructions = result["instructions"]
    selected_tools = result["tools"]  # Now a list of tool names

    # Detect project root for showing paths
    from instructionkit.utils.project import find_project_root
    project_root = find_project_root()
    if not project_root:
        print_error("Could not detect project root. Make sure you're in a project directory.")
        return 1

    # Get detector to show actual install paths
    detector = get_detector()

    # Show detailed confirmation of what will be installed
    console.print("\n[bold cyan]📦 Installation Preview[/bold cyan]")
    console.print(f"\n[bold]Project:[/bold] {project_root}")
    console.print(f"[bold]Instructions:[/bold] {len(selected_instructions)} selected")
    console.print(f"[bold]Target tools:[/bold] {', '.join(selected_tools)}\n")

    # Show where files will be created
    console.print("[bold yellow]The following files will be created:[/bold yellow]\n")

    for tool_name in selected_tools:
        tool = detector.get_tool_by_name(tool_name)
        if tool:
            tool_dir = tool.get_project_instructions_directory(project_root)
            console.print(f"[cyan]{tool.tool_name}[/cyan] → {tool_dir}")
            for inst in selected_instructions:
                filename = f"{inst.name}{tool.get_instruction_file_extension()}"
                console.print(f"  • {filename}")
            console.print()

    # Ask for confirmation
    from rich.prompt import Confirm
    if not Confirm.ask("\n[bold]Proceed with installation?[/bold]", default=True):
        console.print("[dim]Installation cancelled[/dim]")
        return 0

    return install_from_library_direct_multi_tool(
        instruction_ids=[inst.id for inst in selected_instructions],
        tools=selected_tools,
        conflict_strategy="skip",
    )


def install_from_library_direct_multi_tool(
    instruction_ids: list[str],
    tools: list[str],
    conflict_strategy: str = "skip",
) -> int:
    """
    Install specific instructions from library by ID to multiple tools.

    Args:
        instruction_ids: List of instruction IDs to install
        tools: List of AI tool names to install to
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()
    install_scope = InstallationScope.PROJECT

    # Parse conflict strategy
    strategy = _parse_conflict_strategy(conflict_strategy)
    if strategy is None:
        return 1

    # Get project root
    project_root = _get_project_root_for_installation()
    if project_root is None:
        return 1

    # Load instructions from library
    instructions = _load_instructions_from_library(instruction_ids, library)
    if instructions is None:
        return 1

    # Resolve name conflicts
    install_names = _resolve_name_conflicts(instructions)
    if install_names is None:
        return 0

    # Get AI tools
    detector = get_detector()
    ai_tools = _get_ai_tools_from_names(tools, detector)
    if ai_tools is None:
        return 1

    # Show preview and confirm
    if not _show_installation_preview(project_root, instructions, ai_tools, install_names):
        console.print("[dim]Installation cancelled[/dim]")
        return 0

    # Perform installation
    installed_count, skipped_count = _perform_installation(
        instructions, ai_tools, install_names, install_scope, project_root, strategy
    )

    # Summary
    console.print()
    if installed_count > 0:
        print_success(f"✓ Successfully installed {installed_count} instruction(s)")
    if skipped_count > 0:
        print_info(f"Skipped {skipped_count} existing instruction(s)")

    return 0


def install_from_library_direct(
    instruction_ids: list[str],
    tool: Optional[str] = None,
    conflict_strategy: str = "skip",
) -> int:
    """
    Install specific instructions from library by ID.

    Args:
        instruction_ids: List of instruction IDs to install
        tool: AI tool to install to
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()
    install_scope = InstallationScope.PROJECT

    # Parse conflict strategy
    strategy = _parse_conflict_strategy(conflict_strategy)
    if strategy is None:
        return 1

    # Get project root
    project_root = _get_project_root_for_installation()
    if project_root is None:
        return 1

    # Load instructions from library
    instructions = _load_instructions_from_library(instruction_ids, library)
    if instructions is None:
        return 1

    # Resolve name conflicts
    install_names = _resolve_name_conflicts(instructions)
    if install_names is None:
        return 0

    # Determine AI tool(s)
    detector = get_detector()
    if tool:
        ai_tools = _get_ai_tools_from_names([tool], detector)
        if ai_tools is None:
            return 1
    else:
        ai_tools = detector.detect_installed_tools()
        if not ai_tools:
            print_error("No AI coding tools detected")
            return 1

    # Show preview and confirm
    if not _show_installation_preview(project_root, instructions, ai_tools, install_names):
        console.print("[dim]Installation cancelled[/dim]")
        return 0

    # Perform installation
    installed_count, skipped_count = _perform_installation(
        instructions, ai_tools, install_names, install_scope, project_root, strategy
    )

    # Summary
    console.print()
    if installed_count > 0:
        print_success(f"✓ Successfully installed {installed_count} instruction(s)")
    if skipped_count > 0:
        print_info(f"Skipped {skipped_count} existing instruction(s)")

    return 0


def install_from_library_by_name(
    name: str,
    tool: Optional[str] = None,
    conflict_strategy: str = "skip",
) -> int:
    """
    Install instruction(s) from library by name.

    Supports source/name format for disambiguation (e.g., 'company/python-best-practices').

    Args:
        name: Instruction name (or source/name format)
        tool: AI tool to install to
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()

    # Parse source/name format
    source_alias = None
    instruction_name = name
    if "/" in name:
        parts = name.split("/", 1)
        source_alias = parts[0]
        instruction_name = parts[1]

    # Find instructions with this name
    if source_alias:
        # Filter by source alias
        instructions = library.get_instructions_by_source_and_name(source_alias, instruction_name)
    else:
        instructions = library.get_instructions_by_name(instruction_name)

    if not instructions:
        print_error(f"No instruction named '{name}' found in library.")
        print_info("Use 'instructionkit list library --instructions' to see available instructions.")
        return 1

    if len(instructions) == 1:
        # Single match, install it
        return install_from_library_direct(
            instruction_ids=[instructions[0].id],
            tool=tool,
            conflict_strategy=conflict_strategy,
        )

    # Multiple matches - show options
    console.print(f"\n[yellow]Multiple instructions named '{name}' found:[/yellow]\n")
    for i, inst in enumerate(instructions, 1):
        console.print(f"  [{i}] {inst.repo_name} (v{inst.version}) - {inst.author}")
        console.print(f"      {inst.description}")
        console.print()

    console.print("  [A] Install all")
    console.print("  [C] Cancel")
    console.print()

    choice = typer.prompt("Select", default="C")

    if choice.upper() == "C":
        print_info("Installation cancelled")
        return 0
    elif choice.upper() == "A":
        # Install all
        return install_from_library_direct(
            instruction_ids=[inst.id for inst in instructions],
            tool=tool,
            conflict_strategy=conflict_strategy,
        )
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(instructions):
            return install_from_library_direct(
                instruction_ids=[instructions[idx].id],
                tool=tool,
                conflict_strategy=conflict_strategy,
            )

    print_error("Invalid selection")
    return 1


# Keep the original direct install function for backward compatibility
def install_from_repo_direct(
    name: str,
    repo: str,
    tool: Optional[str] = None,
    conflict_strategy: str = "skip",
    bundle: bool = False,
) -> int:
    """
    Install directly from a repository (backward compatibility).

    This is the original install function, preserved for --repo usage.
    """
    # Import the original function
    from instructionkit.cli.install import install_instruction as original_install

    return original_install(
        name=name,
        repo=repo,
        tool=tool,
        conflict_strategy=conflict_strategy,
        bundle=bundle,
    )


def install_multiple_from_library(
    names: list[str],
    tools: Optional[list[str]],
    conflict_strategy: str,
) -> int:
    """
    Install multiple instructions from library.

    Args:
        names: List of instruction names
        tools: List of AI tool names (None = all detected tools)
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()

    # Get all instructions by name
    all_instructions = []
    for name in names:
        insts = library.get_instructions_by_name(name)
        if not insts:
            print_error(f"No instruction named '{name}' found in library.")
            return 1

        if len(insts) > 1:
            # Multiple matches - show options
            console.print(f"\n[yellow]Multiple instructions named '{name}' found:[/yellow]\n")
            for i, inst in enumerate(insts, 1):
                console.print(f"  [{i}] {inst.repo_name} (v{inst.version}) - {inst.author}")
            console.print()

            choice = typer.prompt(f"Select which '{name}' to install (1-{len(insts)})", default="1")

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(insts):
                    all_instructions.append(insts[idx])
                else:
                    print_error("Invalid selection")
                    return 1
            else:
                print_error("Invalid selection")
                return 1
        else:
            all_instructions.append(insts[0])

    # Get instruction IDs
    instruction_ids = [inst.id for inst in all_instructions]

    # Install using the multi-tool function
    if tools:
        return install_from_library_direct_multi_tool(
            instruction_ids=instruction_ids,
            tools=tools,
            conflict_strategy=conflict_strategy,
        )
    else:
        # Use existing single-tool logic (all tools)
        return install_from_library_direct(
            instruction_ids=instruction_ids,
            tool=None,  # Will install to all detected tools
            conflict_strategy=conflict_strategy,
        )


def install_instruction_unified(
    names: Optional[list[str]] = None,
    repo: Optional[str] = None,
    tools: Optional[list[str]] = None,
    conflict_strategy: str = "skip",
    bundle: bool = False,
) -> int:
    """
    Unified install function that routes to appropriate implementation.

    All installations are at project level.

    Args:
        names: Instruction name(s) (optional, can be multiple)
        repo: Repository URL (optional)
        tools: AI tool(s) to install to (optional, can be multiple)
        conflict_strategy: Conflict resolution strategy
        bundle: Whether installing a bundle

    Returns:
        Exit code
    """
    # Convert single tool format (backward compat)
    tool = tools[0] if tools and len(tools) == 1 else None

    # Case 1: Direct install from repo (backward compat)
    if repo:
        if not names or len(names) == 0:
            print_error("When using --repo, you must specify an instruction name")
            return 1

        # Only support single name with --repo for now
        if len(names) > 1:
            print_error("Cannot install multiple instructions with --repo. Install one at a time or use the library.")
            return 1

        return install_from_repo_direct(
            name=names[0],
            repo=repo,
            tool=tool,
            conflict_strategy=conflict_strategy,
            bundle=bundle,
        )

    # Case 2: Install from library with TUI
    if not names or len(names) == 0:
        return install_from_library_tui(tool=tool)

    # Case 3: Install multiple instructions from library
    if len(names) > 1 or (tools and len(tools) > 1):
        return install_multiple_from_library(
            names=names,
            tools=tools,
            conflict_strategy=conflict_strategy,
        )

    # Case 4: Install single instruction from library by name
    return install_from_library_by_name(
        name=names[0],
        tool=tool,
        conflict_strategy=conflict_strategy,
    )
