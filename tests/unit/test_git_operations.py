"""Unit tests for Git operations."""

from unittest.mock import MagicMock, patch

import pytest
from git.exc import GitCommandError

from instructionkit.core.git_operations import GitOperations, RepositoryOperationError
from instructionkit.core.models import RefType


class TestDetectRefType:
    """Test detect_ref_type function."""

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_detect_ref_type_tag(self, mock_git_class):
        """Test detecting a tag reference."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git
        mock_git.ls_remote.return_value = (
            "abc123\trefs/heads/main\n" "def456\trefs/tags/v1.0.0\n" "ghi789\trefs/heads/develop\n"
        )

        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo", "v1.0.0")

        assert ref == "v1.0.0"
        assert ref_type == RefType.TAG

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_detect_ref_type_branch(self, mock_git_class):
        """Test detecting a branch reference."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git
        mock_git.ls_remote.return_value = (
            "abc123\trefs/heads/main\n" "def456\trefs/tags/v1.0.0\n" "ghi789\trefs/heads/develop\n"
        )

        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo", "main")

        assert ref == "main"
        assert ref_type == RefType.BRANCH

    def test_detect_ref_type_commit_hash(self):
        """Test detecting a commit hash (40 chars)."""
        commit = "abc123def456789012345678901234567890abcd"

        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo", commit)

        assert ref == commit
        assert ref_type == RefType.COMMIT

    def test_detect_ref_type_short_commit_hash(self):
        """Test detecting a short commit hash (7+ chars)."""
        commit = "abc123d"

        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo", commit)

        assert ref == commit
        assert ref_type == RefType.COMMIT

    def test_detect_ref_type_none(self):
        """Test default branch when ref is None."""
        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo", None)

        assert ref is None
        assert ref_type == RefType.BRANCH

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_detect_ref_type_tag_priority_over_branch(self, mock_git_class):
        """Test that tags take priority over branches with same name."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git
        # Both tag and branch named 'release'
        mock_git.ls_remote.return_value = (
            "abc123\trefs/heads/release\n" "def456\trefs/tags/release\n" "ghi789\trefs/heads/main\n"
        )

        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo", "release")

        assert ref == "release"
        assert ref_type == RefType.TAG

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_detect_ref_type_invalid_ref(self, mock_git_class):
        """Test error handling for invalid reference."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git
        mock_git.ls_remote.return_value = "abc123\trefs/heads/main\n"

        with pytest.raises(RepositoryOperationError, match="Reference 'nonexistent' not found"):
            GitOperations.detect_ref_type("https://github.com/user/repo", "nonexistent")

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_detect_ref_type_network_error(self, mock_git_class):
        """Test error handling for network issues."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git
        mock_git.ls_remote.side_effect = GitCommandError("ls-remote", 128)

        with pytest.raises(RepositoryOperationError, match="Failed to access repository"):
            GitOperations.detect_ref_type("https://github.com/user/repo", "main")


class TestValidateRemoteRef:
    """Test validate_remote_ref function."""

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_validate_branch_ref(self, mock_git_class):
        """Test validating a branch reference."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git

        result = GitOperations.validate_remote_ref("https://github.com/user/repo", "main", RefType.BRANCH)

        assert result is True
        mock_git.ls_remote.assert_called_once_with("--exit-code", "--heads", "https://github.com/user/repo", "main")

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_validate_tag_ref(self, mock_git_class):
        """Test validating a tag reference."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git

        result = GitOperations.validate_remote_ref("https://github.com/user/repo", "v1.0.0", RefType.TAG)

        assert result is True
        mock_git.ls_remote.assert_called_once_with("--exit-code", "--tags", "https://github.com/user/repo", "v1.0.0")

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_validate_commit_ref(self, mock_git_class):
        """Test validating a commit reference (always returns True)."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git

        result = GitOperations.validate_remote_ref("https://github.com/user/repo", "abc123", RefType.COMMIT)

        assert result is True
        # ls-remote not called for commits
        mock_git.ls_remote.assert_not_called()

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_validate_ref_not_found(self, mock_git_class):
        """Test validation returns False for non-existent ref."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git
        error = GitCommandError("ls-remote", 2)  # exit code 2 = not found
        mock_git.ls_remote.side_effect = error

        result = GitOperations.validate_remote_ref("https://github.com/user/repo", "nonexistent", RefType.BRANCH)

        assert result is False

    @patch("instructionkit.core.git_operations.git.cmd.Git")
    def test_validate_ref_network_error(self, mock_git_class):
        """Test validation raises error for network issues."""
        mock_git = MagicMock()
        mock_git_class.return_value = mock_git
        error = GitCommandError("ls-remote", 128)  # other error
        mock_git.ls_remote.side_effect = error

        with pytest.raises(RepositoryOperationError, match="Failed to validate reference"):
            GitOperations.validate_remote_ref("https://github.com/user/repo", "main", RefType.BRANCH)


class TestRepositoryOperationError:
    """Test RepositoryOperationError exception."""

    def test_repository_operation_error_basic(self):
        """Test basic error creation."""
        error = RepositoryOperationError("Test error", "test_error")

        assert str(error) == "Test error"
        assert error.error_type == "test_error"
        assert error.original_error is None

    def test_repository_operation_error_with_original(self):
        """Test error with original exception."""
        original = ValueError("Original error")
        error = RepositoryOperationError("Test error", "test_error", original)

        assert str(error) == "Test error"
        assert error.error_type == "test_error"
        assert error.original_error == original

    def test_repository_operation_error_types(self):
        """Test different error types."""
        network_error = RepositoryOperationError("Network failed", "network_error")
        ref_error = RepositoryOperationError("Ref not found", "invalid_reference")
        git_error = RepositoryOperationError("Git command failed", "git_command_error")

        assert network_error.error_type == "network_error"
        assert ref_error.error_type == "invalid_reference"
        assert git_error.error_type == "git_command_error"
