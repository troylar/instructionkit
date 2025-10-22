"""Download command for fetching instructions into the library."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from instructionkit.core.checksum import calculate_file_checksum
from instructionkit.core.git_operations import GitOperations
from instructionkit.core.models import LibraryInstruction
from instructionkit.core.repository import RepositoryParser
from instructionkit.storage.library import LibraryManager
from rich.console import Console
from instructionkit.utils.ui import print_error, print_success

console = Console()

app = typer.Typer()


def download_instructions(
    repo: str,
    force: bool = False,
) -> int:
    """
    Download instructions from a repository into the local library.

    Args:
        repo: Repository URL or local path
        force: If True, re-download even if already in library

    Returns:
        Exit code (0 = success)
    """
    library = LibraryManager()
    git_ops = GitOperations()

    console.print(f"\n[bold]Downloading from:[/bold] {repo}\n")

    # Determine if local or remote
    is_local = Path(repo).exists()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            if is_local:
                progress.add_task("Loading local repository...", total=None)
                repo_path = Path(repo).resolve()
            else:
                task = progress.add_task("Cloning repository...", total=None)
                repo_path = git_ops.clone_or_fetch(repo)
                progress.update(task, completed=True)

            # Parse repository
            task = progress.add_task("Parsing repository metadata...", total=None)
            parser = RepositoryParser(repo_path)
            repository = parser.parse()
            repository.url = repo
            progress.update(task, completed=True)

        # Check if already exists
        repo_name = repository.metadata.get('name', 'Unknown')
        repo_namespace = library.get_repo_namespace(repo, repo_name)

        existing_repo = library.get_repository(repo_namespace)
        if existing_repo and not force:
            print_error(
                f"Repository '{repo_name}' already exists in library.\n"
                f"Use --force to re-download."
            )
            return 1

        # Prepare library instructions
        library_instructions = []
        repo_dir = library.library_dir / repo_namespace / "instructions"
        repo_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"\n[bold]Copying instructions to library...[/bold]\n")

        for instruction in repository.instructions:
            # Copy instruction file to library
            source_file = repo_path / instruction.file_path
            if not source_file.exists():
                print_error(f"Warning: File not found: {instruction.file_path}")
                continue

            dest_file = repo_dir / f"{instruction.name}.md"
            shutil.copy2(source_file, dest_file)

            # Calculate checksum
            checksum = calculate_file_checksum(str(dest_file))

            # Create library instruction
            lib_inst = LibraryInstruction(
                id=f"{repo_namespace}/{instruction.name}",
                name=instruction.name,
                description=instruction.description,
                repo_namespace=repo_namespace,
                repo_url=repo,
                repo_name=repo_name,
                author=repository.metadata.get('author', 'Unknown'),
                version=repository.metadata.get('version', '1.0.0'),
                file_path=str(dest_file),
                tags=instruction.tags,
                downloaded_at=datetime.now(),
                checksum=checksum,
            )
            library_instructions.append(lib_inst)

            console.print(f"  ✓ {instruction.name}")

        # Add to library
        library.add_repository(
            repo_name=repo_name,
            repo_description=repository.metadata.get('description', ''),
            repo_url=repo,
            repo_author=repository.metadata.get('author', 'Unknown'),
            repo_version=repository.metadata.get('version', '1.0.0'),
            instructions=library_instructions,
        )

        print_success(
            f"\n✓ Downloaded {len(library_instructions)} instruction(s) from '{repo_name}'\n"
            f"  Namespace: {repo_namespace}\n"
            f"  Use 'instructionkit list library' to see all downloaded instructions\n"
            f"  Use 'instructionkit install' to install into your AI tools"
        )

        return 0

    except FileNotFoundError as e:
        print_error(f"Repository metadata file not found: {e}")
        return 1
    except Exception as e:
        print_error(f"Failed to download: {e}")
        return 1
    finally:
        # Clean up temp directory if not local
        if not is_local:
            git_ops.cleanup()


@app.command(name="download")
def download_command(
    repo: str = typer.Option(
        ...,
        "--repo",
        "-r",
        help="Repository URL or local path to download from",
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
