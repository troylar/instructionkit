"""Main CLI application entry point."""

import typer
from typing import Optional

from instructionkit.cli.delete import delete_from_library
from instructionkit.cli.download import download_instructions
from instructionkit.cli.install import install_instruction
from instructionkit.cli.list import list_available, list_installed, list_library
from instructionkit.cli.uninstall import uninstall_instruction
from instructionkit.cli.tools import show_tools
from instructionkit.cli.update import update_repository

app = typer.Typer(
    name="instructionkit",
    help="CLI tool for managing AI coding tool instructions",
    add_completion=False,
)

# Create list subcommand group
list_app = typer.Typer(help="List instructions")
app.add_typer(list_app, name="list")


@app.command()
def install(
    name: str = typer.Argument(..., help="Instruction or bundle name to install"),
    repo: str = typer.Option(..., "--repo", "-r", help="Git repository URL or local directory path"),
    tool: Optional[str] = typer.Option(
        None,
        "--tool",
        "-t",
        help="AI tool to install to (cursor, copilot, windsurf, claude)",
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
    scope: str = typer.Option(
        "global",
        "--scope",
        "-s",
        help="Installation scope (global or project)",
    ),
) -> None:
    """
    Install an instruction from a Git repository or local folder.

    Examples:

      # Install globally (default)
      instructionkit install python-best-practices --repo https://github.com/company/instructions

      # Install to current project
      instructionkit install python-best-practices --repo https://github.com/company/instructions --scope project

      # Install from local folder
      instructionkit install python-best-practices --repo ./my-instructions
      instructionkit install python-best-practices --repo /path/to/instructions

      # Install to specific tool
      instructionkit install python-best-practices --repo https://github.com/company/instructions --tool cursor

      # Install bundle
      instructionkit install python-backend --bundle --repo https://github.com/company/instructions

      # Handle conflicts by renaming
      instructionkit install python-best-practices --repo https://github.com/company/instructions --conflict rename
    """
    exit_code = install_instruction(
        name=name,
        repo=repo,
        tool=tool,
        conflict_strategy=conflict,
        bundle=bundle,
        scope=scope,
    )
    raise typer.Exit(code=exit_code)


@app.command()
def download(
    repo: str = typer.Option(
        ...,
        "--repo",
        "-r",
        help="Git repository URL or local directory path",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Re-download even if already in library",
    ),
) -> None:
    """
    Download instructions from a repository into your local library.

    This downloads and caches instructions locally without installing them.
    After downloading, use 'instructionkit install' to select and install
    instructions into your AI coding tools.

    Examples:

      # Download from GitHub
      instructionkit download --repo https://github.com/company/instructions

      # Download from local folder
      instructionkit download --repo ./my-instructions

      # Force re-download
      instructionkit download --repo https://github.com/company/instructions --force
    """
    exit_code = download_instructions(repo=repo, force=force)
    raise typer.Exit(code=exit_code)


@list_app.command("available")
def list_available_cmd(
    repo: str = typer.Option(..., "--repo", "-r", help="Git repository URL or local directory path"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    bundles_only: bool = typer.Option(False, "--bundles-only", help="Show only bundles"),
    instructions_only: bool = typer.Option(False, "--instructions-only", help="Show only instructions"),
) -> None:
    """
    List available instructions from a repository or local folder.

    Examples:

      # List from Git repository
      instructionkit list available --repo https://github.com/company/instructions

      # List from local folder
      instructionkit list available --repo ./my-instructions

      # Filter by tag
      instructionkit list available --repo https://github.com/company/instructions --tag python

      # Show only bundles
      instructionkit list available --repo https://github.com/company/instructions --bundles-only
    """
    exit_code = list_available(
        repo=repo,
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
    repo: Optional[str] = typer.Option(
        None,
        "--repo",
        "-r",
        help="Filter by source repository URL",
    ),
) -> None:
    """
    List installed instructions.

    Examples:

      # List all installed instructions
      instructionkit list installed

      # Filter by AI tool
      instructionkit list installed --tool cursor

      # Filter by repository
      instructionkit list installed --repo https://github.com/company/instructions
    """
    exit_code = list_installed(tool=tool, repo=repo)
    raise typer.Exit(code=exit_code)


@list_app.command("library")
def list_library_cmd(
    repo: Optional[str] = typer.Option(
        None,
        "--repo",
        "-r",
        help="Filter by repository namespace",
    ),
    instructions: bool = typer.Option(
        False,
        "--instructions",
        "-i",
        help="Show individual instructions instead of repositories",
    ),
) -> None:
    """
    List repositories and instructions in your local library.

    Examples:

      # List all repositories in library
      instructionkit list library

      # Show individual instructions
      instructionkit list library --instructions

      # Filter by repository
      instructionkit list library --repo company
    """
    exit_code = list_library(repo_filter=repo, show_instructions=instructions)
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

    This re-downloads instructions from their source repositories,
    ensuring you have the latest versions in your library.

    Examples:

      # Update a specific repository
      instructionkit update --namespace github.com_company_instructions

      # Update all repositories
      instructionkit update --all

      # List repositories to find namespace
      instructionkit list library
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
    Delete a repository from your local library.

    This removes the downloaded instructions from your library but does NOT
    uninstall them from your AI tools. To uninstall, use 'instructionkit uninstall'.

    Examples:

      # Delete a repository
      instructionkit delete github.com_company_instructions

      # Skip confirmation
      instructionkit delete github.com_company_instructions --force

      # List repositories to find namespace
      instructionkit list library
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
    scope: Optional[str] = typer.Option(
        None,
        "--scope",
        "-s",
        help="Installation scope to uninstall from (global, project, or all)",
    ),
) -> None:
    """
    Uninstall an instruction.

    Examples:

      # Uninstall from all tools and scopes
      instructionkit uninstall python-best-practices

      # Uninstall from specific tool
      instructionkit uninstall python-best-practices --tool cursor

      # Uninstall only from project scope
      instructionkit uninstall python-best-practices --scope project

      # Skip confirmation
      instructionkit uninstall python-best-practices --force
    """
    exit_code = uninstall_instruction(name=name, tool=tool, force=force, scope=scope)
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


@app.callback()
def main() -> None:
    """
    InstructionKit - Manage AI coding tool instructions from Git repositories.

    Install instructions for Cursor, GitHub Copilot, Windsurf, and Claude Code
    from any Git repository (public or private).
    """
    pass


if __name__ == "__main__":
    app()
