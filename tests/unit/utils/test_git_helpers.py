"""Unit tests for git helper utilities."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

try:
    from git.exc import GitCommandError, InvalidGitRepositoryError
except ImportError:
    # Create mock exceptions for testing when GitPython not available
    class GitCommandError(Exception):  # type: ignore
        pass

    class InvalidGitRepositoryError(Exception):  # type: ignore
        pass


from aiconfigkit.utils.git_helpers import (
    GitPythonNotInstalledError,
    TemplateAuthError,
    TemplateNetworkError,
    clone_template_repo,
    get_repo_version,
    update_template_repo,
)


class TestCloneTemplateRepo:
    """Test clone_template_repo function."""

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_clone_basic(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test basic repository cloning."""
        mock_repo = MagicMock()
        mock_repo_class.clone_from.return_value = mock_repo

        url = "https://github.com/test/repo.git"
        destination = tmp_path / "repo"

        result = clone_template_repo(url, destination)

        assert result == mock_repo
        mock_repo_class.clone_from.assert_called_once_with(
            url=url, to_path=str(destination), depth=1, env={"GIT_TERMINAL_PROMPT": "0"}
        )

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_clone_custom_depth(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test cloning with custom depth."""
        mock_repo = MagicMock()
        mock_repo_class.clone_from.return_value = mock_repo

        url = "https://github.com/test/repo.git"
        destination = tmp_path / "repo"

        clone_template_repo(url, destination, depth=10)

        mock_repo_class.clone_from.assert_called_once()
        call_args = mock_repo_class.clone_from.call_args
        assert call_args[1]["depth"] == 10

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_clone_auth_failed_401(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test cloning with 401 authentication failure."""
        error = GitCommandError("authentication failed 401", "git")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateAuthError, match="Authentication failed"):
            clone_template_repo("https://github.com/test/repo.git", tmp_path / "repo")

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_clone_auth_failed_403(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test cloning with 403 forbidden error."""
        error = GitCommandError("403 forbidden", "git")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateAuthError, match="Authentication failed"):
            clone_template_repo("https://github.com/test/repo.git", tmp_path / "repo")

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_clone_auth_failed_permission_denied(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test cloning with permission denied error."""
        error = GitCommandError("permission denied", "git")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateAuthError, match="Authentication failed"):
            clone_template_repo("git@github.com:test/repo.git", tmp_path / "repo")

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_clone_auth_failed_publickey(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test cloning with publickey error."""
        error = GitCommandError("publickey", "git")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateAuthError, match="Authentication failed"):
            clone_template_repo("git@github.com:test/repo.git", tmp_path / "repo")

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_clone_repo_not_found_404(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test cloning non-existent repository (404)."""
        error = GitCommandError("404 not found", "git")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateNetworkError, match="Repository not found"):
            clone_template_repo("https://github.com/test/nonexistent.git", tmp_path / "repo")

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_clone_network_error(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test cloning with generic network error."""
        error = GitCommandError("network timeout", "git")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateNetworkError, match="Failed to clone repository"):
            clone_template_repo("https://github.com/test/repo.git", tmp_path / "repo")

    @patch("aiconfigkit.utils.git_helpers.Repo", None)
    def test_clone_gitpython_not_installed(self, tmp_path: Path) -> None:
        """Test cloning when GitPython is not installed."""
        with pytest.raises(GitPythonNotInstalledError, match="GitPython is required"):
            clone_template_repo("https://github.com/test/repo.git", tmp_path / "repo")


class TestUpdateTemplateRepo:
    """Test update_template_repo function."""

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_update_has_changes(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test updating repository with remote changes."""
        mock_repo = MagicMock()
        mock_origin = MagicMock()
        mock_fetch_info = MagicMock()

        # Simulate remote has changes
        mock_repo.head.commit = "old_commit"
        mock_fetch_info.commit = "new_commit"
        mock_origin.fetch.return_value = [mock_fetch_info]
        mock_repo.remotes.origin = mock_origin

        mock_repo_class.return_value = mock_repo

        result = update_template_repo(tmp_path)

        assert result is True
        mock_origin.fetch.assert_called_once()
        mock_origin.pull.assert_called_once()

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_update_already_up_to_date(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test updating repository that is already up-to-date."""
        mock_repo = MagicMock()
        mock_origin = MagicMock()
        mock_fetch_info = MagicMock()

        # Simulate no changes (same commit)
        same_commit = "same_commit_hash"
        mock_repo.head.commit = same_commit
        mock_fetch_info.commit = same_commit
        mock_origin.fetch.return_value = [mock_fetch_info]
        mock_repo.remotes.origin = mock_origin

        mock_repo_class.return_value = mock_repo

        result = update_template_repo(tmp_path)

        assert result is False
        mock_origin.fetch.assert_called_once()
        mock_origin.pull.assert_not_called()  # Should not pull if up-to-date

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_update_invalid_repo(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test updating invalid/non-existent repository."""
        error = InvalidGitRepositoryError(f"Not a Git repository: {tmp_path}")
        mock_repo_class.side_effect = error

        with pytest.raises(InvalidGitRepositoryError, match="Not a Git repository"):
            update_template_repo(tmp_path)

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_update_network_error(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test updating with network failure."""
        mock_repo = MagicMock()
        mock_origin = MagicMock()

        error = GitCommandError("network error", "git")
        mock_origin.fetch.side_effect = error
        mock_repo.remotes.origin = mock_origin

        mock_repo_class.return_value = mock_repo

        with pytest.raises(TemplateNetworkError, match="Failed to update repository"):
            update_template_repo(tmp_path)

    @patch("aiconfigkit.utils.git_helpers.Repo", None)
    def test_update_gitpython_not_installed(self, tmp_path: Path) -> None:
        """Test updating when GitPython is not installed."""
        with pytest.raises(GitPythonNotInstalledError, match="GitPython is required"):
            update_template_repo(tmp_path)


class TestGetRepoVersion:
    """Test get_repo_version function."""

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_get_version_with_tags(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test getting version when repository has tags."""
        mock_repo = MagicMock()

        # Create mock tags with different commit dates
        tag1 = MagicMock()
        tag1.__str__ = lambda self: "v1.0.0"
        tag1.commit.committed_datetime = 100

        tag2 = MagicMock()
        tag2.__str__ = lambda self: "v2.0.0"
        tag2.commit.committed_datetime = 200

        tag3 = MagicMock()
        tag3.__str__ = lambda self: "v1.5.0"
        tag3.commit.committed_datetime = 150

        mock_repo.tags = [tag1, tag3, tag2]  # Unsorted
        mock_repo_class.return_value = mock_repo

        version = get_repo_version(tmp_path)

        # Should return most recent tag (v2.0.0)
        assert version == "v2.0.0"

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_get_version_no_tags(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test getting version when repository has no tags."""
        mock_repo = MagicMock()
        mock_repo.tags = []
        mock_repo.head.commit.hexsha = "1234567890abcdef"

        mock_repo_class.return_value = mock_repo

        version = get_repo_version(tmp_path)

        # Should return short commit hash (first 8 chars)
        assert version == "12345678"

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_get_version_single_tag(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test getting version with single tag."""
        mock_repo = MagicMock()

        tag = MagicMock()
        tag.__str__ = lambda self: "v1.0.0"
        tag.commit.committed_datetime = 100

        mock_repo.tags = [tag]
        mock_repo_class.return_value = mock_repo

        version = get_repo_version(tmp_path)

        assert version == "v1.0.0"

    @patch("aiconfigkit.utils.git_helpers.Repo")
    def test_get_version_invalid_repo(self, mock_repo_class: MagicMock, tmp_path: Path) -> None:
        """Test getting version from invalid repository."""
        error = InvalidGitRepositoryError(f"Not a Git repository: {tmp_path}")
        mock_repo_class.side_effect = error

        with pytest.raises(InvalidGitRepositoryError, match="Not a Git repository"):
            get_repo_version(tmp_path)

    @patch("aiconfigkit.utils.git_helpers.Repo", None)
    def test_get_version_gitpython_not_installed(self, tmp_path: Path) -> None:
        """Test getting version when GitPython is not installed."""
        with pytest.raises(GitPythonNotInstalledError, match="GitPython is required"):
            get_repo_version(tmp_path)


class TestExceptions:
    """Test custom exceptions."""

    def test_template_auth_error(self) -> None:
        """Test TemplateAuthError exception."""
        error = TemplateAuthError("Auth failed")
        assert str(error) == "Auth failed"
        assert isinstance(error, Exception)

    def test_template_network_error(self) -> None:
        """Test TemplateNetworkError exception."""
        error = TemplateNetworkError("Network error")
        assert str(error) == "Network error"
        assert isinstance(error, Exception)

    def test_gitpython_not_installed_error(self) -> None:
        """Test GitPythonNotInstalledError exception."""
        error = GitPythonNotInstalledError("GitPython not found")
        assert str(error) == "GitPython not found"
        assert isinstance(error, Exception)
