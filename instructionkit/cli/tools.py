"""Tools command to show detected AI coding tools."""

import typer
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
    table.add_column("Config Directory")
    
    # Get all tools and their status
    for tool_type, tool in detector.tools.items():
        is_installed = tool.is_installed()
        status = "[green]✓ Installed[/green]" if is_installed else "[red]✗ Not found[/red]"
        
        if is_installed:
            try:
                config_dir = str(tool.get_instructions_directory())
            except Exception:
                config_dir = "[dim]Error getting directory[/dim]"
        else:
            config_dir = "[dim]N/A[/dim]"
        
        table.add_row(
            tool.tool_name,
            status,
            config_dir
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
