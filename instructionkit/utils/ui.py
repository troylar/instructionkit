"""UI utilities for terminal output."""

from typing import Optional

from rich.console import Console
from rich.table import Table

from instructionkit.core.models import InstallationRecord, Instruction, InstructionBundle


def format_instructions_table(
    instructions: list[Instruction],
    bundles: list[InstructionBundle],
    show_bundles: bool = True
) -> Table:
    """
    Format instructions and bundles as a Rich table.

    Args:
        instructions: List of instructions to display
        bundles: List of bundles to display
        show_bundles: Whether to show bundles section

    Returns:
        Rich Table object
    """
    table = Table(title="Available Instructions", show_header=True, header_style="bold cyan")

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Description")
    table.add_column("Tags", style="yellow")

    # Add instructions
    for inst in sorted(instructions, key=lambda x: x.name):
        tags_str = ", ".join(inst.tags) if inst.tags else "-"
        table.add_row(
            inst.name,
            "Instruction",
            inst.description,
            tags_str
        )

    # Add bundles
    if show_bundles:
        for bundle in sorted(bundles, key=lambda x: x.name):
            tags_str = ", ".join(bundle.tags) if bundle.tags else "-"
            inst_count = f"{len(bundle.instructions)} instructions"
            table.add_row(
                bundle.name,
                "Bundle",
                f"{bundle.description} ({inst_count})",
                tags_str
            )

    return table


def format_installed_table(
    records: list[InstallationRecord],
    group_by_tool: bool = True
) -> Table:
    """
    Format installed instructions as a Rich table.

    Args:
        records: List of installation records
        group_by_tool: Whether to group by AI tool

    Returns:
        Rich Table object
    """
    table = Table(title="Installed Instructions", show_header=True, header_style="bold green")

    if group_by_tool:
        table.add_column("AI Tool", style="cyan", no_wrap=True)

    table.add_column("Instruction", style="green", no_wrap=True)
    table.add_column("Scope", style="blue", no_wrap=True)
    table.add_column("Source Repository")
    table.add_column("Installed", style="yellow")
    table.add_column("Bundle", style="magenta")

    # Sort records
    if group_by_tool:
        sorted_records = sorted(records, key=lambda x: (x.ai_tool.value, x.instruction_name))
    else:
        sorted_records = sorted(records, key=lambda x: x.instruction_name)

    # Add rows
    current_tool = None
    for record in sorted_records:
        # Format installed date
        installed_date = record.installed_at.strftime("%Y-%m-%d")

        # Shorten repo URL for display
        repo_display = _shorten_url(record.source_repo, max_length=50)

        # Bundle name or "-"
        bundle_display = record.bundle_name if record.bundle_name else "-"

        # Scope display
        scope_display = record.scope.value.capitalize()

        if group_by_tool:
            # Show tool name only on first occurrence
            tool_display = record.ai_tool.value.capitalize() if record.ai_tool != current_tool else ""
            current_tool = record.ai_tool

            table.add_row(
                tool_display,
                record.instruction_name,
                scope_display,
                repo_display,
                installed_date,
                bundle_display
            )
        else:
            table.add_row(
                record.instruction_name,
                scope_display,
                repo_display,
                installed_date,
                bundle_display
            )

    return table


def format_bundle_details(
    bundle: InstructionBundle,
    instructions: list[Instruction]
) -> Table:
    """
    Format bundle details with its instructions.

    Args:
        bundle: Bundle to display
        instructions: Instructions in the bundle

    Returns:
        Rich Table object
    """
    table = Table(
        title=f"Bundle: {bundle.name}",
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("#", style="dim", width=4)
    table.add_column("Instruction", style="cyan")
    table.add_column("Description")
    table.add_column("Tags", style="yellow")

    for idx, inst in enumerate(instructions, 1):
        tags_str = ", ".join(inst.tags) if inst.tags else "-"
        table.add_row(
            str(idx),
            inst.name,
            inst.description,
            tags_str
        )

    return table


def print_success(message: str, console: Optional[Console] = None) -> None:
    """Print success message."""
    if console is None:
        console = Console()
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str, console: Optional[Console] = None) -> None:
    """Print error message."""
    if console is None:
        console = Console()
    console.print(f"[red]Error:[/red] {message}")


def print_warning(message: str, console: Optional[Console] = None) -> None:
    """Print warning message."""
    if console is None:
        console = Console()
    console.print(f"[yellow]Warning:[/yellow] {message}")


def print_info(message: str, console: Optional[Console] = None) -> None:
    """Print info message."""
    if console is None:
        console = Console()
    console.print(f"[cyan]ℹ[/cyan] {message}")


def _shorten_url(url: str, max_length: int = 50) -> str:
    """Shorten URL for display."""
    if len(url) <= max_length:
        return url

    # Try to keep the important parts: domain and repo name
    if "://" in url:
        protocol, rest = url.split("://", 1)
        if "/" in rest:
            parts = rest.split("/")
            if len(parts) >= 3:
                # Keep domain and last 2 parts
                shortened = f"{parts[0]}/.../{'/'.join(parts[-2:])}"
                return shortened

    # Fallback: truncate with ellipsis
    return url[:max_length-3] + "..."
