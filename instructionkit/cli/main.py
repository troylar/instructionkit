"""Main CLI application entry point."""

from typing import Optional

import typer

from instructionkit.cli.delete import delete_from_library
from instructionkit.cli.download import download_instructions
from instructionkit.cli.install_new import install_instruction_unified
from instructionkit.cli.list import list_available, list_installed, list_library
from instructionkit.cli.tools import show_tools
from instructionkit.cli.uninstall import uninstall_instruction
from instructionkit.cli.update import update_repository

app = typer.Typer(
    name="instructionkit",
    help="CLI tool for managing AI coding tool instructions",
    add_completion=False,
)

# Create list subcommand group
list_app = typer.Typer(help="List instructions")
app.add_typer(list_app, name="list")


@list_app.callback(invoke_without_command=True)
def list_callback(ctx: typer.Context) -> None:
    """List instructions (available, installed, or in library)."""
    # If no subcommand was provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@app.command()
def install(
    names: Optional[list[str]] = typer.Argument(
        None,
        help="Instruction name(s) to install (use source/name for disambiguation). Can specify multiple.",
    ),
    source: Optional[str] = typer.Option(
        None,
        "--from",
        "-f",
        help="Source URL or path for direct install (bypasses library)",
    ),
    tools: Optional[list[str]] = typer.Option(
        None,
        "--tool",
        "-t",
        help="AI tool(s) to install to (cursor, copilot, windsurf, claude). Can specify multiple times.",
    ),
    conflict: str = typer.Option(
        "skip",
        "--conflict",
        "-c",
        help="Conflict resolution strategy (skip, rename, overwrite)",
    ),
    bundle: bool = typer.Option(
        False,
        "--bundle",
        "-b",
        help="Install as bundle (multiple instructions)",
    ),
) -> None:
    """
    Install instructions from your library or directly from a source.

    LIBRARY WORKFLOW (Recommended):
      # Browse and select instructions with TUI
      inskit install

      # Install specific instruction from library
      inskit install python-best-practices

      # Install from specific source (if multiple sources have same name)
      inskit install company/python-best-practices

      # Install multiple instructions at once
      inskit install python-style testing-guide api-design

      # Install to specific tools only
      inskit install python-style --tool cursor --tool windsurf

    DIRECT INSTALL (Bypasses library):
      # Install directly from source URL
      inskit install python-style --from https://github.com/company/instructions

      # Install bundle directly
      inskit install python-backend --bundle --from https://github.com/company/instructions

    TIP: Download to your library first for better management:
      inskit download --from https://github.com/company/instructions
    """
    exit_code = install_instruction_unified(
        names=names,
        repo=source,  # Keep backend param name for now
        tools=tools,
        conflict_strategy=conflict,
        bundle=bundle,
    )
    raise typer.Exit(code=exit_code)


@app.command()
def download(
    source: str = typer.Option(
        ...,
        "--from",
        "-f",
        help="Source URL or local directory path",
    ),
    alias: Optional[str] = typer.Option(
        None,
        "--as",
        "-a",
        help="Friendly alias for this source (auto-generated if not provided)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Re-download even if already in library",
    ),
) -> None:
    """
    Download instructions from a source into your local library.

    This downloads and caches instructions locally without installing them.
    After downloading, use 'inskit install' to install instructions.

    Examples:

      # Download from GitHub (auto-generates alias)
      inskit download --from github.com/company/instructions

      # Download with custom alias
      inskit download --from github.com/company/instructions --as company

      # Download from local folder
      inskit download --from ./my-instructions --as local

      # Force re-download
      inskit download --from github.com/company/instructions --force
    """
    exit_code = download_instructions(repo=source, force=force, alias=alias)
    raise typer.Exit(code=exit_code)


@list_app.command("available")
def list_available_cmd(
    source: str = typer.Option(..., "--from", "-f", help="Source URL or local directory path"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    bundles_only: bool = typer.Option(False, "--bundles-only", help="Show only bundles"),
    instructions_only: bool = typer.Option(False, "--instructions-only", help="Show only instructions"),
) -> None:
    """
    List available instructions from a source (without downloading).

    Examples:

      # List from Git repository
      inskit list available --from github.com/company/instructions

      # List from local folder
      inskit list available --from ./my-instructions

      # Filter by tag
      inskit list available --from github.com/company/instructions --tag python

      # Show only bundles
      inskit list available --from github.com/company/instructions --bundles-only
    """
    exit_code = list_available(
        repo=source,  # Keep backend param name for now
        tag=tag,
        bundles_only=bundles_only,
        instructions_only=instructions_only,
    )
    raise typer.Exit(code=exit_code)


@list_app.command("installed")
def list_installed_cmd(
    tool: Optional[str] = typer.Option(
        None,
        "--tool",
        "-t",
        help="Filter by AI tool (cursor, copilot, windsurf, claude)",
    ),
    source: Optional[str] = typer.Option(
        None,
        "--source",
        "-s",
        help="Filter by source alias or name",
    ),
) -> None:
    """
    List installed instructions in your AI tools.

    Examples:

      # List all installed instructions
      inskit list installed

      # Filter by AI tool
      inskit list installed --tool cursor

      # Filter by source
      inskit list installed --source company
    """
    exit_code = list_installed(tool=tool, repo=source)  # Keep backend param name for now
    raise typer.Exit(code=exit_code)


@list_app.command("library")
def list_library_cmd(
    source: Optional[str] = typer.Option(
        None,
        "--source",
        "-s",
        help="Filter by source alias",
    ),
    instructions: bool = typer.Option(
        False,
        "--instructions",
        "-i",
        help="Show individual instructions instead of repositories",
    ),
) -> None:
    """
    List sources and instructions in your local library.

    Examples:

      # List all sources in library
      inskit list library

      # Show individual instructions
      inskit list library --instructions

      # Filter by source
      inskit list library --source company
    """
    exit_code = list_library(repo_filter=source, show_instructions=instructions)
    raise typer.Exit(code=exit_code)


@app.command()
def update(
    namespace: Optional[str] = typer.Option(
        None,
        "--namespace",
        "-n",
        help="Repository namespace to update",
    ),
    all_repos: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Update all repositories in library",
    ),
) -> None:
    """
    Update downloaded instructions to their latest versions.

    This re-downloads instructions from their sources,
    ensuring you have the latest versions in your library.

    Examples:

      # Update a specific source
      inskit update --namespace github.com_company_instructions

      # Update all sources
      inskit update --all

      # List sources to find namespace
      inskit list library
    """
    exit_code = update_repository(namespace=namespace, all_repos=all_repos)
    raise typer.Exit(code=exit_code)


@app.command()
def delete(
    namespace: str = typer.Argument(
        ...,
        help="Repository namespace to delete from library",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Delete a source from your local library.

    This removes the downloaded instructions from your library but does NOT
    uninstall them from your AI tools. To uninstall, use 'inskit uninstall'.

    Examples:

      # Delete a source
      inskit delete github.com_company_instructions

      # Skip confirmation
      inskit delete github.com_company_instructions --force

      # List sources to find namespace
      inskit list library
    """
    exit_code = delete_from_library(namespace=namespace, force=force)
    raise typer.Exit(code=exit_code)


@app.command()
def uninstall(
    name: str = typer.Argument(..., help="Instruction name to uninstall"),
    tool: Optional[str] = typer.Option(
        None,
        "--tool",
        "-t",
        help="AI tool to uninstall from (cursor, copilot, windsurf, claude)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Uninstall an instruction from your AI tools.

    Removes instructions from project level only.

    Examples:

      # Uninstall from all tools
      inskit uninstall python-best-practices

      # Uninstall from specific tool
      inskit uninstall python-best-practices --tool cursor

      # Skip confirmation
      inskit uninstall python-best-practices --force
    """
    exit_code = uninstall_instruction(name=name, tool=tool, force=force)
    raise typer.Exit(code=exit_code)


@app.command()
def tools() -> None:
    """
    Show detected AI coding tools.

    Display which AI coding tools are installed on your system
    and where their configuration directories are located.
    """
    exit_code = show_tools()
    raise typer.Exit(code=exit_code)


@app.command()
def version() -> None:
    """Show InstructionKit version."""
    from importlib.metadata import version as get_version

    try:
        version = get_version("instructionkit")
    except Exception:
        version = "unknown"

    typer.echo(f"InstructionKit version {version}")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    InstructionKit - Manage AI coding tool instructions from Git repositories.

    Install instructions for Cursor, GitHub Copilot, Windsurf, and Claude Code
    from any Git repository (public or private).
    """
    # If no command was provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


if __name__ == "__main__":
    app()
