"""Tests for delete CLI command."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from aiconfigkit.cli.delete import delete_from_library
from aiconfigkit.core.models import LibraryInstruction, LibraryRepository
from aiconfigkit.storage.library import LibraryManager
from aiconfigkit.storage.tracker import InstallationTracker


@pytest.fixture
def mock_library_manager(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Create a mock library manager."""
    mock = Mock(spec=LibraryManager)
    monkeypatch.setattr("aiconfigkit.cli.delete.LibraryManager", lambda: mock)
    return mock


@pytest.fixture
def mock_tracker(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Create a mock installation tracker."""
    mock = Mock(spec=InstallationTracker)
    monkeypatch.setattr("aiconfigkit.cli.delete.InstallationTracker", lambda: mock)
    return mock


def test_delete_repository_not_found(mock_library_manager: Mock, mock_tracker: Mock) -> None:
    """Test deleting a repository that doesn't exist."""
    mock_library_manager.get_repository.return_value = None

    exit_code = delete_from_library("nonexistent", force=True)

    assert exit_code == 1
    mock_library_manager.get_repository.assert_called_once_with("nonexistent")


def test_delete_repository_with_force(mock_library_manager: Mock, mock_tracker: Mock) -> None:
    """Test deleting a repository with force flag (no confirmation)."""
    # Create mock repository
    repo = LibraryRepository(
        name="Test Repo",
        namespace="test-namespace",
        version="1.0.0",
        description="Test repository",
        instructions=[],
        url="https://test.com/repo",
        author="Test Author",
        downloaded_at=datetime.now(),
    )
    mock_library_manager.get_repository.return_value = repo
    mock_library_manager.remove_repository.return_value = True
    mock_tracker.list_installations.return_value = []

    exit_code = delete_from_library("test-namespace", force=True)

    assert exit_code == 0
    mock_library_manager.remove_repository.assert_called_once_with("test-namespace")


def test_delete_repository_with_installed_instructions(mock_library_manager: Mock, mock_tracker: Mock) -> None:
    """Test deleting a repository that has installed instructions."""
    # Create mock repository with instructions
    instruction = LibraryInstruction(
        id="test-namespace/test-instruction",
        name="test-instruction",
        description="Test instruction",
        file_path="/tmp/instruction.md",
        tags=["test"],
        repo_namespace="test-namespace",
        repo_url="https://test.com/repo",
        repo_name="Test Repo",
        author="Test Author",
        version="1.0.0",
    )
    repo = LibraryRepository(
        name="Test Repo",
        namespace="test-namespace",
        version="1.0.0",
        description="Test repository",
        instructions=[instruction],
        url="https://test.com/repo",
        author="Test Author",
        downloaded_at=datetime.now(),
    )
    mock_library_manager.get_repository.return_value = repo
    mock_library_manager.remove_repository.return_value = True

    # Mock installed instructions (empty for force delete)
    mock_tracker.list_installations.return_value = []

    exit_code = delete_from_library("test-namespace", force=True)

    assert exit_code == 0


def test_delete_repository_failure(mock_library_manager: Mock, mock_tracker: Mock) -> None:
    """Test when repository deletion fails."""
    repo = LibraryRepository(
        name="Test Repo",
        namespace="test-namespace",
        version="1.0.0",
        description="Test repository",
        instructions=[],
        url="https://test.com/repo",
        author="Test Author",
        downloaded_at=datetime.now(),
    )
    mock_library_manager.get_repository.return_value = repo
    mock_library_manager.remove_repository.return_value = False
    mock_tracker.list_installations.return_value = []

    exit_code = delete_from_library("test-namespace", force=True)

    assert exit_code == 1


@patch("aiconfigkit.cli.delete.Confirm.ask")
def test_delete_repository_with_confirmation_cancelled(
    mock_confirm: Mock, mock_library_manager: Mock, mock_tracker: Mock
) -> None:
    """Test deleting a repository when user cancels confirmation."""
    mock_confirm.return_value = False

    repo = LibraryRepository(
        name="Test Repo",
        namespace="test-namespace",
        version="1.0.0",
        description="Test repository",
        instructions=[],
        url="https://test.com/repo",
        author="Test Author",
        downloaded_at=datetime.now(),
    )
    mock_library_manager.get_repository.return_value = repo
    mock_tracker.list_installations.return_value = []

    exit_code = delete_from_library("test-namespace", force=False)

    assert exit_code == 0
    mock_library_manager.remove_repository.assert_not_called()


@patch("aiconfigkit.cli.delete.Confirm.ask")
def test_delete_repository_with_confirmation_accepted(
    mock_confirm: Mock, mock_library_manager: Mock, mock_tracker: Mock
) -> None:
    """Test deleting a repository when user confirms."""
    mock_confirm.return_value = True

    repo = LibraryRepository(
        name="Test Repo",
        namespace="test-namespace",
        version="1.0.0",
        description="Test repository",
        instructions=[],
        url="https://test.com/repo",
        author="Test Author",
        downloaded_at=datetime.now(),
    )
    mock_library_manager.get_repository.return_value = repo
    mock_library_manager.remove_repository.return_value = True
    mock_tracker.list_installations.return_value = []

    exit_code = delete_from_library("test-namespace", force=False)

    assert exit_code == 0
    mock_library_manager.remove_repository.assert_called_once_with("test-namespace")
