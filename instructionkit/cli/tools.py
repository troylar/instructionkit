"""Tools command to show detected AI coding tools."""

from rich.console import Console
from rich.table import Table

from instructionkit.ai_tools.detector import get_detector

console = Console()


def show_tools() -> int:
    """
    Show detected AI coding tools.

    Returns:
        Exit code (0 for success)
    """
    detector = get_detector()

    # Create table
    table = Table(title="AI Coding Tools", show_header=True, header_style="bold cyan")
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")

    # Get all tools and their status
    for tool_type, tool in detector.tools.items():
        is_installed = tool.is_installed()
        status = "[green]✓ Installed[/green]" if is_installed else "[red]✗ Not found[/red]"

        table.add_row(
            tool.tool_name,
            status
        )

    # Display table
    console.print()
    console.print(table)
    console.print()

    # Summary
    installed = detector.detect_installed_tools()
    if installed:
        tool_names = ", ".join([t.tool_name for t in installed])
        console.print(f"[green]Found {len(installed)} installed tool(s):[/green] {tool_names}")
    else:
        console.print("[yellow]No AI coding tools detected[/yellow]")
        console.print("\nSupported tools: Cursor, GitHub Copilot, Winsurf, Claude Code")

    console.print()
    return 0
