"""Project detection utilities."""

from pathlib import Path
from typing import Optional


def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the project root directory by looking for common project markers.

    Searches upward from the start path for files/directories that indicate
    a project root:
    - .git directory (Git repository)
    - pyproject.toml (Python project)
    - package.json (Node.js project)
    - Cargo.toml (Rust project)
    - go.mod (Go project)
    - pom.xml (Java/Maven project)
    - build.gradle (Java/Gradle project)
    - composer.json (PHP project)
    - Gemfile (Ruby project)

    Args:
        start_path: Directory to start searching from. Defaults to current directory.

    Returns:
        Path to project root if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    # Common project markers
    markers = [
        '.git',
        'pyproject.toml',
        'package.json',
        'Cargo.toml',
        'go.mod',
        'pom.xml',
        'build.gradle',
        'composer.json',
        'Gemfile',
        '.project',  # Eclipse project
        'Makefile',
    ]

    current = start_path

    # Search upward through parent directories
    while True:
        for marker in markers:
            marker_path = current / marker
            if marker_path.exists():
                return current

        # Check if we've reached the filesystem root
        parent = current.parent
        if parent == current:
            # No project root found
            return None

        current = parent


def is_in_project() -> bool:
    """
    Check if the current directory is within a project.

    Returns:
        True if a project root can be found
    """
    return find_project_root() is not None


def get_project_instructions_dir(project_root: Path, create: bool = True) -> Path:
    """
    Get the directory for project-specific instructions.

    Creates a .instructionkit directory in the project root for storing
    project-specific instructions and metadata.

    Args:
        project_root: Path to the project root directory
        create: Whether to create the directory if it doesn't exist

    Returns:
        Path to project instructions directory
    """
    instructions_dir = project_root / '.instructionkit'

    if create:
        instructions_dir.mkdir(parents=True, exist_ok=True)

    return instructions_dir


def get_project_installation_tracker_path(project_root: Path) -> Path:
    """
    Get path to project-specific installation tracking file.

    Args:
        project_root: Path to the project root directory

    Returns:
        Path to project installation tracking JSON file
    """
    return get_project_instructions_dir(project_root) / 'installations.json'
