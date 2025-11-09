"""Tests for Git helper functions for template repositories."""

from unittest.mock import MagicMock, patch

import pytest

from instructionkit.utils.git_helpers import (
    GitPythonNotInstalledError,
    TemplateAuthError,
    TemplateNetworkError,
    _check_gitpython,
    clone_template_repo,
    get_repo_version,
    update_template_repo,
)


class TestCheckGitpython:
    """Tests for _check_gitpython function."""

    @patch("instructionkit.utils.git_helpers.Repo", None)
    def test_raises_when_not_installed(self):
        """Test that error is raised when GitPython not installed."""
        with pytest.raises(GitPythonNotInstalledError, match="GitPython is required"):
            _check_gitpython()

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_passes_when_installed(self, mock_repo):
        """Test that no error is raised when GitPython is installed."""
        mock_repo.return_value = MagicMock()
        _check_gitpython()  # Should not raise


class TestCloneTemplateRepo:
    """Tests for clone_template_repo function."""

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_successful_clone(self, mock_repo_class, tmp_path):
        """Test successful repository clone."""
        mock_repo = MagicMock()
        mock_repo_class.clone_from.return_value = mock_repo

        destination = tmp_path / "test-repo"
        result = clone_template_repo("https://github.com/acme/templates", destination)

        assert result == mock_repo
        mock_repo_class.clone_from.assert_called_once_with(
            url="https://github.com/acme/templates",
            to_path=str(destination),
            depth=1,
            env={"GIT_TERMINAL_PROMPT": "0"},
        )

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_clone_with_custom_depth(self, mock_repo_class, tmp_path):
        """Test cloning with custom depth."""
        mock_repo = MagicMock()
        mock_repo_class.clone_from.return_value = mock_repo

        destination = tmp_path / "test-repo"
        clone_template_repo("https://github.com/acme/templates", destination, depth=5)

        mock_repo_class.clone_from.assert_called_once_with(
            url="https://github.com/acme/templates",
            to_path=str(destination),
            depth=5,
            env={"GIT_TERMINAL_PROMPT": "0"},
        )

    @patch("instructionkit.utils.git_helpers.Repo", None)
    def test_clone_without_gitpython_raises(self, tmp_path):
        """Test that cloning without GitPython raises error."""
        with pytest.raises(GitPythonNotInstalledError):
            clone_template_repo("https://github.com/acme/templates", tmp_path / "test")

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_clone_authentication_failure(self, mock_repo_class, tmp_path):
        """Test handling of authentication failures."""
        from git.exc import GitCommandError

        # Create a real GitCommandError
        error = GitCommandError("clone", "Authentication failed for repository")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateAuthError, match="Authentication failed"):
            clone_template_repo("https://github.com/acme/templates", tmp_path / "test")

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_clone_401_error(self, mock_repo_class, tmp_path):
        """Test handling of 401 errors."""
        from git.exc import GitCommandError

        error = GitCommandError("clone", "Error: 401 unauthorized")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateAuthError, match="Authentication failed"):
            clone_template_repo("https://github.com/acme/templates", tmp_path / "test")

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_clone_permission_denied(self, mock_repo_class, tmp_path):
        """Test handling of permission denied errors."""
        from git.exc import GitCommandError

        error = GitCommandError("clone", "Permission denied (publickey)")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateAuthError, match="Authentication failed"):
            clone_template_repo("https://github.com/acme/templates", tmp_path / "test")

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_clone_404_error(self, mock_repo_class, tmp_path):
        """Test handling of 404 not found errors."""
        from git.exc import GitCommandError

        error = GitCommandError("clone", "Error: 404 not found")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateNetworkError, match="Repository not found"):
            clone_template_repo("https://github.com/acme/templates", tmp_path / "test")

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_clone_repository_not_found(self, mock_repo_class, tmp_path):
        """Test handling of repository not found errors."""
        from git.exc import GitCommandError

        error = GitCommandError("clone", "Repository not found")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateNetworkError, match="Repository not found"):
            clone_template_repo("https://github.com/acme/templates", tmp_path / "test")

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_clone_network_error(self, mock_repo_class, tmp_path):
        """Test handling of generic network errors."""
        from git.exc import GitCommandError

        error = GitCommandError("clone", "Network timeout")
        mock_repo_class.clone_from.side_effect = error

        with pytest.raises(TemplateNetworkError, match="Failed to clone repository"):
            clone_template_repo("https://github.com/acme/templates", tmp_path / "test")


class TestUpdateTemplateRepo:
    """Tests for update_template_repo function."""

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_update_with_changes(self, mock_repo_class, tmp_path):
        """Test updating repository with new changes."""
        # Create mock repo
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Mock commits (different commits means changes available)
        mock_head_commit = MagicMock()
        mock_head_commit.hexsha = "abc123"
        mock_repo.head.commit = mock_head_commit

        mock_fetch_commit = MagicMock()
        mock_fetch_commit.hexsha = "def456"

        mock_fetch_info = MagicMock()
        mock_fetch_info.commit = mock_fetch_commit

        mock_origin = MagicMock()
        mock_origin.fetch.return_value = [mock_fetch_info]
        mock_repo.remotes.origin = mock_origin

        result = update_template_repo(tmp_path)

        assert result is True
        mock_origin.fetch.assert_called_once()
        mock_origin.pull.assert_called_once()

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_update_already_up_to_date(self, mock_repo_class, tmp_path):
        """Test updating repository that's already up-to-date."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Mock commits (same commit means up-to-date)
        mock_commit = MagicMock()
        mock_commit.hexsha = "abc123"
        mock_repo.head.commit = mock_commit

        mock_fetch_info = MagicMock()
        mock_fetch_info.commit = mock_commit

        mock_origin = MagicMock()
        mock_origin.fetch.return_value = [mock_fetch_info]
        mock_repo.remotes.origin = mock_origin

        result = update_template_repo(tmp_path)

        assert result is False
        mock_origin.fetch.assert_called_once()
        mock_origin.pull.assert_not_called()  # Should not pull if already up-to-date

    @patch("instructionkit.utils.git_helpers.Repo", None)
    def test_update_without_gitpython_raises(self, tmp_path):
        """Test that updating without GitPython raises error."""
        with pytest.raises(GitPythonNotInstalledError):
            update_template_repo(tmp_path)

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_update_invalid_repository(self, mock_repo_class, tmp_path):
        """Test updating invalid Git repository raises error."""
        from git.exc import InvalidGitRepositoryError

        error = InvalidGitRepositoryError(str(tmp_path))
        mock_repo_class.side_effect = error

        with pytest.raises(InvalidGitRepositoryError, match="Not a Git repository"):
            update_template_repo(tmp_path)

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_update_network_error(self, mock_repo_class, tmp_path):
        """Test handling of network errors during update."""
        from git.exc import GitCommandError

        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        error = GitCommandError("fetch", "Network timeout")
        mock_origin = MagicMock()
        mock_origin.fetch.side_effect = error
        mock_repo.remotes.origin = mock_origin

        with pytest.raises(TemplateNetworkError, match="Failed to update repository"):
            update_template_repo(tmp_path)


class TestGetRepoVersion:
    """Tests for get_repo_version function."""

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_get_version_with_tags(self, mock_repo_class, tmp_path):
        """Test getting version when repository has tags."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Create mock tags
        mock_tag1 = MagicMock()
        mock_tag1.__str__ = lambda self: "v1.0.0"
        mock_tag1.commit.committed_datetime = "2024-01-01"

        mock_tag2 = MagicMock()
        mock_tag2.__str__ = lambda self: "v1.1.0"
        mock_tag2.commit.committed_datetime = "2024-01-15"

        mock_repo.tags = [mock_tag1, mock_tag2]

        version = get_repo_version(tmp_path)

        # Should return most recent tag
        assert version == "v1.1.0"

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_get_version_without_tags(self, mock_repo_class, tmp_path):
        """Test getting version when repository has no tags (returns commit hash)."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # No tags
        mock_repo.tags = []

        # Mock commit hash
        mock_commit = MagicMock()
        mock_commit.hexsha = "abc123def456789012345678901234567890"
        mock_repo.head.commit = mock_commit

        version = get_repo_version(tmp_path)

        # Should return first 8 characters of commit hash
        assert version == "abc123de"

    @patch("instructionkit.utils.git_helpers.Repo", None)
    def test_get_version_without_gitpython_raises(self, tmp_path):
        """Test that getting version without GitPython raises error."""
        with pytest.raises(GitPythonNotInstalledError):
            get_repo_version(tmp_path)

    @patch("instructionkit.utils.git_helpers.Repo")
    def test_get_version_invalid_repository(self, mock_repo_class, tmp_path):
        """Test getting version of invalid Git repository raises error."""
        from git.exc import InvalidGitRepositoryError

        error = InvalidGitRepositoryError(str(tmp_path))
        mock_repo_class.side_effect = error

        with pytest.raises(InvalidGitRepositoryError, match="Not a Git repository"):
            get_repo_version(tmp_path)
