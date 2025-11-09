"""Git operations for template repositories."""

from pathlib import Path
from typing import Optional

try:
    from git import Repo
    from git.exc import GitCommandError, InvalidGitRepositoryError
except ImportError:
    # GitPython not installed - will be caught by runtime checks
    Repo = None  # type: ignore
    GitCommandError = Exception  # type: ignore
    InvalidGitRepositoryError = Exception  # type: ignore


class TemplateAuthError(Exception):
    """Raised when Git authentication fails for template repository."""

    pass


class TemplateNetworkError(Exception):
    """Raised when network/repository is unavailable."""

    pass


class GitPythonNotInstalledError(Exception):
    """Raised when GitPython is not installed."""

    pass


def _check_gitpython() -> None:
    """Check if GitPython is available."""
    if Repo is None:
        raise GitPythonNotInstalledError("GitPython is required for template sync. Install with: pip install GitPython")


def clone_template_repo(url: str, destination: Path, depth: int = 1) -> "Repo":
    """
    Clone template repository using system Git credentials.

    Uses Git credential helpers configured on the user's system.
    Supports both HTTPS and SSH URLs.

    Args:
        url: Git repository URL
        destination: Destination directory for clone
        depth: Clone depth (default 1 for shallow clone)

    Returns:
        Git Repo object

    Raises:
        TemplateAuthError: If authentication fails
        TemplateNetworkError: If network/repository unavailable
        GitPythonNotInstalledError: If GitPython not installed

    Example:
        >>> from pathlib import Path
        >>> repo = clone_template_repo(
        ...     "https://github.com/acme/templates",
        ...     Path("~/.instructionkit/templates/acme")
        ... )
    """
    _check_gitpython()

    try:
        repo = Repo.clone_from(
            url=url,
            to_path=str(destination),
            depth=depth,
            env={
                "GIT_TERMINAL_PROMPT": "0",  # Fail if credentials needed but not available
            },
        )
        return repo
    except GitCommandError as e:
        error_str = str(e).lower()

        # Check for authentication failures
        auth_keywords = ["authentication failed", "401", "403", "permission denied", "publickey"]
        if any(keyword in error_str for keyword in auth_keywords):
            raise TemplateAuthError(
                f"Authentication failed for {url}.\n\n"
                f"To configure Git credentials:\n\n"
                f"For HTTPS URLs:\n"
                f"  git config --global credential.helper store\n"
                f"  # Then perform a git clone manually to cache credentials\n\n"
                f"For SSH URLs:\n"
                f'  1. Generate SSH key: ssh-keygen -t ed25519 -C "your_email@example.com"\n'
                f"  2. Add to GitHub: cat ~/.ssh/id_ed25519.pub\n"
                f"  3. Use SSH URL: git@github.com:org/repo.git\n\n"
                f"Original error: {e}"
            ) from e

        # Check for repository not found (could be private repo without access)
        if "404" in error_str or "not found" in error_str:
            raise TemplateNetworkError(
                f"Repository not found: {url}\n\n"
                f"This could mean:\n"
                f"  - Repository doesn't exist\n"
                f"  - Repository is private and you don't have access\n"
                f"  - URL is incorrect\n\n"
                f"Original error: {e}"
            ) from e

        # Other network/Git errors
        raise TemplateNetworkError(f"Failed to clone repository from {url}: {e}") from e


def update_template_repo(repo_path: Path) -> bool:
    """
    Pull latest changes from template repository.

    Args:
        repo_path: Path to local repository

    Returns:
        True if updates were pulled, False if already up-to-date

    Raises:
        TemplateNetworkError: If update fails
        GitPythonNotInstalledError: If GitPython not installed
        InvalidGitRepositoryError: If path is not a Git repository

    Example:
        >>> from pathlib import Path
        >>> has_updates = update_template_repo(Path("~/.instructionkit/templates/acme"))
        >>> if has_updates:
        ...     print("Repository updated!")
    """
    _check_gitpython()

    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError as e:
        raise InvalidGitRepositoryError(f"Not a Git repository: {repo_path}") from e

    origin = repo.remotes.origin

    try:
        # Fetch latest changes
        fetch_info = origin.fetch()[0]

        # Check if remote has changes
        if repo.head.commit == fetch_info.commit:
            return False  # Already up-to-date

        # Pull changes
        origin.pull()
        return True

    except GitCommandError as e:
        raise TemplateNetworkError(f"Failed to update repository at {repo_path}: {e}") from e


def get_repo_version(repo_path: Path) -> Optional[str]:
    """
    Get current version of repository (latest tag or commit hash).

    Args:
        repo_path: Path to local repository

    Returns:
        Version string (tag name or short commit hash)

    Raises:
        GitPythonNotInstalledError: If GitPython not installed
        InvalidGitRepositoryError: If path is not a Git repository
    """
    _check_gitpython()

    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError as e:
        raise InvalidGitRepositoryError(f"Not a Git repository: {repo_path}") from e

    # Try to get latest tag
    if repo.tags:
        # Get most recent tag
        latest_tag = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)[-1]
        return str(latest_tag)

    # Fallback to commit hash
    return repo.head.commit.hexsha[:8]
