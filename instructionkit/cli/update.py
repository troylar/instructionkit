"""Update command for refreshing library instructions."""

from typing import Optional

import typer
from rich.console import Console

from instructionkit.cli.download import download_instructions
from instructionkit.storage.library import LibraryManager
from instructionkit.utils.ui import print_error, print_info, print_success

console = Console()

app = typer.Typer()


def update_repository(
    namespace: Optional[str] = None,
    all_repos: bool = False,
) -> int:
    """
    Update instructions from their source repositories.

    Args:
        namespace: Specific repository namespace to update
        all_repos: Update all repositories

    Returns:
        Exit code (0 = success)
    """
    library = LibraryManager()

    if not all_repos and not namespace:
        print_error("Must specify either --namespace or --all")
        return 1

    # Get repositories to update
    if all_repos:
        repositories = library.list_repositories()
        if not repositories:
            print_info("No repositories in library to update")
            return 0
    else:
        repo = library.get_repository(namespace)
        if not repo:
            print_error(f"Repository not found: {namespace}")
            print_info("Use 'instructionkit list library' to see available repositories")
            return 1
        repositories = [repo]

    console.print(f"\n[bold]Updating {len(repositories)} repository(ies)...[/bold]\n")

    success_count = 0
    error_count = 0

    for repo in repositories:
        console.print(f"[cyan]Updating:[/cyan] {repo.name} ({repo.namespace})")

        # Re-download with force flag
        exit_code = download_instructions(repo=repo.url, force=True)

        if exit_code == 0:
            success_count += 1
        else:
            error_count += 1
            print_error(f"Failed to update: {repo.name}")

        console.print()

    # Summary
    if error_count == 0:
        print_success(f"✓ Successfully updated {success_count} repository(ies)")
        return 0
    else:
        print_error(
            f"Updated {success_count} repository(ies), {error_count} failed"
        )
        return 1


@app.command(name="update")
def update_command(
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
