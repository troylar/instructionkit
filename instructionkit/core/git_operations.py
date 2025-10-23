"""Git operations for cloning and managing instruction repositories."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from instructionkit.utils.validation import is_valid_git_url


class GitOperationError(Exception):
    """Raised when a Git operation fails."""
    pass


class GitOperations:
    """Handle Git repository operations."""

    @staticmethod
    def is_local_path(repo_url: str) -> bool:
        """
        Check if the repository URL is a local file path.

        Args:
            repo_url: Repository URL or path

        Returns:
            True if it's a local path, False if it's a remote Git URL
        """
        # Remote URLs have protocols or SSH format
        if repo_url.startswith(('https://', 'http://', 'git://', 'ssh://')):
            return False

        # SSH format (git@host:path)
        if '@' in repo_url and ':' in repo_url and not repo_url.startswith('/'):
            return False

        # Everything else is treated as a local path
        return True

    @staticmethod
    def clone_repository(
        repo_url: str,
        target_dir: Optional[Path] = None,
        branch: Optional[str] = None,
        depth: int = 1
    ) -> Path:
        """
        Clone a Git repository or use a local directory.

        Args:
            repo_url: URL of Git repository to clone or path to local directory
            target_dir: Directory to clone into (creates temp dir if None)
            branch: Specific branch to clone (defaults to default branch)
            depth: Clone depth (1 for shallow clone)

        Returns:
            Path to repository

        Raises:
            GitOperationError: If clone fails
            ValueError: If repo_url is invalid
        """
        # Validate URL
        if not is_valid_git_url(repo_url):
            raise ValueError(f"Invalid Git repository URL: {repo_url}")

        # Handle local directories
        if GitOperations.is_local_path(repo_url):
            local_path = Path(repo_url).resolve()
            if not local_path.exists():
                raise GitOperationError(f"Local directory does not exist: {local_path}")
            if not local_path.is_dir():
                raise GitOperationError(f"Path is not a directory: {local_path}")
            return local_path

        # Create target directory if not provided
        if target_dir is None:
            target_dir = Path(tempfile.mkdtemp(prefix='instructionkit-'))
        else:
            target_dir.mkdir(parents=True, exist_ok=True)

        # Build git clone command
        cmd = ['git', 'clone']

        # Add depth for shallow clone
        if depth > 0:
            cmd.extend(['--depth', str(depth)])

        # Add branch if specified
        if branch:
            cmd.extend(['--branch', branch])

        # Add URL and target directory
        cmd.extend([repo_url, str(target_dir)])

        try:
            # Execute git clone
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )

            return target_dir

        except subprocess.CalledProcessError as e:
            # Clean up target directory on failure
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)

            error_msg = e.stderr if e.stderr else str(e)
            raise GitOperationError(f"Failed to clone repository: {error_msg}")

        except subprocess.TimeoutExpired:
            # Clean up on timeout
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)

            raise GitOperationError("Repository clone timed out after 5 minutes")

        except Exception as e:
            # Clean up on any other error
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)

            raise GitOperationError(f"Unexpected error during clone: {str(e)}")

    @staticmethod
    def is_git_installed() -> bool:
        """
        Check if Git is installed and accessible.

        Returns:
            True if git command is available
        """
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    def get_git_version() -> Optional[str]:
        """
        Get installed Git version.

        Returns:
            Git version string or None if not installed
        """
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Output format: "git version 2.x.x"
                return result.stdout.strip()
            return None
        except (subprocess.SubprocessError, FileNotFoundError):
            return None

    @staticmethod
    def cleanup_repository(repo_path: Path, is_temp: bool = True) -> None:
        """
        Clean up a cloned repository directory.

        Args:
            repo_path: Path to repository to clean up
            is_temp: Whether this is a temporary directory (safe to delete)
        """
        # Only delete if it's a temporary directory
        if is_temp and repo_path.exists() and repo_path.is_dir():
            # Safety check: only delete if it's in temp directory
            if 'instructionkit-' in str(repo_path) or '/tmp/' in str(repo_path):
                shutil.rmtree(repo_path, ignore_errors=True)


def with_temporary_clone(repo_url: str, branch: Optional[str] = None):
    """
    Context manager for temporary repository clones.

    Usage:
        with with_temporary_clone(repo_url) as repo_path:
            # Use repo_path
            pass
        # Repository is automatically cleaned up

    Args:
        repo_url: URL of repository to clone
        branch: Optional branch to clone

    Yields:
        Path to cloned repository
    """
    from contextlib import contextmanager

    @contextmanager
    def _clone_context():
        repo_path = None
        try:
            git_ops = GitOperations()
            repo_path = git_ops.clone_repository(repo_url, branch=branch)
            yield repo_path
        finally:
            if repo_path and repo_path.exists():
                GitOperations.cleanup_repository(repo_path)

    return _clone_context()
