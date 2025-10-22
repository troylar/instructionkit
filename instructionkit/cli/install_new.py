"""Refactored install command with library support."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from instructionkit.ai_tools.detector import get_detector
from instructionkit.core.checksum import ChecksumValidator, calculate_file_checksum
from instructionkit.core.conflict_resolution import ConflictResolver
from instructionkit.core.git_operations import GitOperations
from instructionkit.core.models import (
    AIToolType,
    ConflictResolution,
    InstallationRecord,
    InstallationScope,
    LibraryInstruction,
)
from instructionkit.core.repository import RepositoryParser
from instructionkit.storage.library import LibraryManager
from instructionkit.storage.tracker import InstallationTracker
from instructionkit.tui.installer import show_installer_tui
from instructionkit.utils.project import find_project_root
from instructionkit.utils.ui import print_error, print_info, print_success
from instructionkit.utils.validation import is_valid_git_url, normalize_repo_url

console = Console()


def install_from_library_tui(
    tool: Optional[str] = None,
    scope: str = "global",
) -> int:
    """
    Show TUI to select and install instructions from library.

    Args:
        tool: AI tool to install to (None = auto-detect)
        scope: Installation scope

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

    # Parse scope
    try:
        install_scope = InstallationScope(scope.lower())
    except ValueError:
        print_error(f"Invalid scope: {scope}. Must be 'global' or 'project'.")
        return 1

    # Show TUI
    result = show_installer_tui(library=library, scope=install_scope, tool=tool)

    if not result:
        console.print("[dim]Cancelled[/dim]")
        return 0

    # Install selected instructions
    selected_instructions = result["instructions"]
    final_scope = result["scope"]
    selected_tools = result["tools"]  # Now a list of tool names

    # Show summary before installing
    console.print("\n[bold cyan]Installation Summary[/bold cyan]")
    console.print(f"Instructions to install: [green]{len(selected_instructions)}[/green]")
    console.print(f"Target tools: [cyan]{', '.join(selected_tools)}[/cyan]")
    console.print(f"Scope: [yellow]{final_scope.value}[/yellow]")
    console.print()

    return install_from_library_direct_multi_tool(
        instruction_ids=[inst.id for inst in selected_instructions],
        tools=selected_tools,
        scope=final_scope.value,
        conflict_strategy="skip",
    )


def install_from_library_direct_multi_tool(
    instruction_ids: list[str],
    tools: list[str],
    scope: str = "global",
    conflict_strategy: str = "skip",
) -> int:
    """
    Install specific instructions from library by ID to multiple tools.

    Args:
        instruction_ids: List of instruction IDs to install
        tools: List of AI tool names to install to
        scope: Installation scope
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()

    # Parse scope
    try:
        install_scope = InstallationScope(scope.lower())
    except ValueError:
        print_error(f"Invalid scope: {scope}. Must be 'global' or 'project'.")
        return 1

    # Parse conflict strategy
    try:
        strategy = ConflictResolution(conflict_strategy.lower())
    except ValueError:
        print_error(
            f"Invalid conflict strategy: {conflict_strategy}. "
            "Must be 'skip', 'rename', or 'overwrite'."
        )
        return 1

    # Detect project root if needed
    project_root: Optional[Path] = None
    if install_scope == InstallationScope.PROJECT:
        project_root = find_project_root()
        if not project_root:
            print_error(
                "Could not detect project root. "
                "Make sure you're running from within a project directory."
            )
            return 1
        console.print(f"Detected project root: [cyan]{project_root}[/cyan]")

    # Get instructions from library
    instructions = []
    for inst_id in instruction_ids:
        inst = library.get_instruction(inst_id)
        if not inst:
            print_error(f"Instruction not found in library: {inst_id}")
            return 1
        instructions.append(inst)

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
            console.print(f"\n[yellow]⚠️  Name Conflict:[/yellow] {len(insts)} instructions named '{name}'")
            console.print("\nHow should they be installed?")
            console.print("  [1] Namespace by repository (recommended)")
            for i, inst in enumerate(insts, 1):
                console.print(f"      → {inst.repo_namespace}/{name}")
            console.print("  [2] Skip installation (cancel)")

            choice = typer.prompt("Select (1-2)", default="1")

            if choice == "1":
                # Use namespaced names
                for inst in insts:
                    install_names[inst.id] = f"{inst.repo_namespace}/{name}"
            else:
                print_info("Installation cancelled")
                return 0
        else:
            # No conflict, use simple name
            install_names[insts[0].id] = name

    # Get AI tools from the provided list
    detector = get_detector()
    ai_tools = []
    for tool_name in tools:
        tool = detector.get_tool_by_name(tool_name)
        if not tool:
            print_error(f"AI tool not found: {tool_name}")
            return 1
        if not tool.is_installed():
            print_error(f"{tool.tool_name} is not installed")
            return 1
        ai_tools.append(tool)

    # Install to each tool
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
                    console.print(f"  [yellow]Skipped:[/yellow] {install_name} (already exists)")
                    skipped_count += 1
                    continue
                elif strategy == ConflictResolution.RENAME:
                    conflict_info = resolver.resolve(install_name, target_path, strategy)
                    target_path = Path(conflict_info.new_path)
                    console.print(f"  [yellow]Renamed:[/yellow] {install_name} -> {target_path.name}")
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
    scope: str = "global",
    conflict_strategy: str = "skip",
) -> int:
    """
    Install specific instructions from library by ID.

    Args:
        instruction_ids: List of instruction IDs to install
        tool: AI tool to install to
        scope: Installation scope
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()

    # Parse scope
    try:
        install_scope = InstallationScope(scope.lower())
    except ValueError:
        print_error(f"Invalid scope: {scope}. Must be 'global' or 'project'.")
        return 1

    # Parse conflict strategy
    try:
        strategy = ConflictResolution(conflict_strategy.lower())
    except ValueError:
        print_error(
            f"Invalid conflict strategy: {conflict_strategy}. "
            "Must be 'skip', 'rename', or 'overwrite'."
        )
        return 1

    # Detect project root if needed
    project_root: Optional[Path] = None
    if install_scope == InstallationScope.PROJECT:
        project_root = find_project_root()
        if not project_root:
            print_error(
                "Could not detect project root. "
                "Make sure you're running from within a project directory."
            )
            return 1
        console.print(f"Detected project root: [cyan]{project_root}[/cyan]")

    # Get instructions from library
    instructions = []
    for inst_id in instruction_ids:
        inst = library.get_instruction(inst_id)
        if not inst:
            print_error(f"Instruction not found in library: {inst_id}")
            return 1
        instructions.append(inst)

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
            console.print(f"\n[yellow]⚠️  Name Conflict:[/yellow] {len(insts)} instructions named '{name}'")
            console.print("\nHow should they be installed?")
            console.print("  [1] Namespace by repository (recommended)")
            for i, inst in enumerate(insts, 1):
                console.print(f"      → {inst.repo_namespace}/{name}")
            console.print("  [2] Skip installation (cancel)")

            choice = typer.prompt("Select (1-2)", default="1")

            if choice == "1":
                # Use namespaced names
                for inst in insts:
                    install_names[inst.id] = f"{inst.repo_namespace}/{name}"
            else:
                print_info("Installation cancelled")
                return 0
        else:
            # No conflict, use simple name
            install_names[insts[0].id] = name

    # Determine AI tool(s)
    detector = get_detector()
    if tool:
        ai_tools = [detector.get_tool_by_name(tool)]
        if not ai_tools[0]:
            print_error(f"AI tool not found: {tool}")
            return 1
        if not ai_tools[0].is_installed():
            print_error(f"{ai_tools[0].tool_name} is not installed")
            return 1
    else:
        ai_tools = detector.detect_installed_tools()
        if not ai_tools:
            print_error("No AI coding tools detected")
            return 1

    # Install to each tool
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
                    console.print(f"  [yellow]Skipped:[/yellow] {install_name} (already exists)")
                    skipped_count += 1
                    continue
                elif strategy == ConflictResolution.RENAME:
                    conflict_info = resolver.resolve(install_name, target_path, strategy)
                    target_path = Path(conflict_info.new_path)
                    console.print(f"  [yellow]Renamed:[/yellow] {install_name} -> {target_path.name}")
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
    scope: str = "global",
    conflict_strategy: str = "skip",
) -> int:
    """
    Install instruction(s) from library by name.

    Args:
        name: Instruction name
        tool: AI tool to install to
        scope: Installation scope
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()

    # Find instructions with this name
    instructions = library.get_instructions_by_name(name)

    if not instructions:
        print_error(f"No instruction named '{name}' found in library.")
        print_info("Use 'instructionkit list library --instructions' to see available instructions.")
        return 1

    if len(instructions) == 1:
        # Single match, install it
        return install_from_library_direct(
            instruction_ids=[instructions[0].id],
            tool=tool,
            scope=scope,
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
            scope=scope,
            conflict_strategy=conflict_strategy,
        )
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(instructions):
            return install_from_library_direct(
                instruction_ids=[instructions[idx].id],
                tool=tool,
                scope=scope,
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
    scope: str = "global",
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
        scope=scope,
    )


def install_multiple_from_library(
    names: list[str],
    tools: Optional[list[str]],
    scope: str,
    conflict_strategy: str,
) -> int:
    """
    Install multiple instructions from library.

    Args:
        names: List of instruction names
        tools: List of AI tool names (None = all detected tools)
        scope: Installation scope
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
            scope=scope,
            conflict_strategy=conflict_strategy,
        )
    else:
        # Use existing single-tool logic (all tools)
        return install_from_library_direct(
            instruction_ids=instruction_ids,
            tool=None,  # Will install to all detected tools
            scope=scope,
            conflict_strategy=conflict_strategy,
        )


def install_instruction_unified(
    names: Optional[list[str]] = None,
    repo: Optional[str] = None,
    tools: Optional[list[str]] = None,
    conflict_strategy: str = "skip",
    bundle: bool = False,
    scope: str = "global",
) -> int:
    """
    Unified install function that routes to appropriate implementation.

    Args:
        names: Instruction name(s) (optional, can be multiple)
        repo: Repository URL (optional)
        tools: AI tool(s) to install to (optional, can be multiple)
        conflict_strategy: Conflict resolution strategy
        bundle: Whether installing a bundle
        scope: Installation scope

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
            scope=scope,
        )

    # Case 2: Install from library with TUI
    if not names or len(names) == 0:
        return install_from_library_tui(tool=tool, scope=scope)

    # Case 3: Install multiple instructions from library
    if len(names) > 1 or (tools and len(tools) > 1):
        return install_multiple_from_library(
            names=names,
            tools=tools,
            scope=scope,
            conflict_strategy=conflict_strategy,
        )

    # Case 4: Install single instruction from library by name
    return install_from_library_by_name(
        name=names[0],
        tool=tool,
        scope=scope,
        conflict_strategy=conflict_strategy,
    )
