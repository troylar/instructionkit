"""Unit tests for delete CLI command."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from aiconfigkit.cli.delete import delete_from_library
from aiconfigkit.core.models import (
    AIToolType,
    InstallationRecord,
    InstallationScope,
    LibraryInstruction,
    LibraryRepository,
)


class TestDeleteFromLibrary:
    """Test delete_from_library function."""

    @patch("aiconfigkit.cli.delete.InstallationTracker")
    @patch("aiconfigkit.cli.delete.LibraryManager")
    def test_delete_nonexistent_repository(self, mock_library_class: MagicMock, mock_tracker_class: MagicMock) -> None:
        """Test deleting non-existent repository."""
        mock_library = MagicMock()
        mock_library.get_repository.return_value = None
        mock_library_class.return_value = mock_library

        result = delete_from_library("nonexistent-namespace")

        assert result == 1  # Error code
        mock_library.remove_repository.assert_not_called()

    @patch("aiconfigkit.cli.delete.Confirm")
    @patch("aiconfigkit.cli.delete.InstallationTracker")
    @patch("aiconfigkit.cli.delete.LibraryManager")
    def test_delete_with_force(
        self, mock_library_class: MagicMock, mock_tracker_class: MagicMock, mock_confirm: MagicMock
    ) -> None:
        """Test deleting repository with force flag."""
        # Setup library
        mock_library = MagicMock()
        repo = LibraryRepository(
            namespace="test/repo",
            name="Test Repo",
            description="Test",
            url="https://github.com/test/repo",
            author="Author",
            version="1.0.0",
            downloaded_at=datetime.now(),
            alias="test-repo",
            instructions=[],
        )
        mock_library.get_repository.return_value = repo
        mock_library.remove_repository.return_value = True
        mock_library_class.return_value = mock_library

        # Setup tracker
        mock_tracker = MagicMock()
        mock_tracker.list_installations.return_value = []
        mock_tracker_class.return_value = mock_tracker

        # Execute with force=True (should skip confirmation)
        result = delete_from_library("test/repo", force=True)

        assert result == 0  # Success
        mock_library.remove_repository.assert_called_once_with("test/repo")
        mock_confirm.ask.assert_not_called()  # Confirmation should be skipped

    @patch("aiconfigkit.cli.delete.Confirm")
    @patch("aiconfigkit.cli.delete.InstallationTracker")
    @patch("aiconfigkit.cli.delete.LibraryManager")
    def test_delete_with_confirmation_cancelled(
        self, mock_library_class: MagicMock, mock_tracker_class: MagicMock, mock_confirm: MagicMock
    ) -> None:
        """Test deleting repository when user cancels confirmation."""
        # Setup library
        mock_library = MagicMock()
        repo = LibraryRepository(
            namespace="test/repo",
            name="Test Repo",
            description="Test",
            url="https://github.com/test/repo",
            author="Author",
            version="1.0.0",
            downloaded_at=datetime.now(),
            alias="test-repo",
            instructions=[],
        )
        mock_library.get_repository.return_value = repo
        mock_library_class.return_value = mock_library

        # Setup tracker
        mock_tracker = MagicMock()
        mock_tracker.list_installations.return_value = []
        mock_tracker_class.return_value = mock_tracker

        # User cancels confirmation
        mock_confirm.ask.return_value = False

        result = delete_from_library("test/repo", force=False)

        assert result == 0  # Success (cancelled, but not an error)
        mock_library.remove_repository.assert_not_called()

    @patch("aiconfigkit.cli.delete.Confirm")
    @patch("aiconfigkit.cli.delete.InstallationTracker")
    @patch("aiconfigkit.cli.delete.LibraryManager")
    def test_delete_with_installed_instructions_warning(
        self, mock_library_class: MagicMock, mock_tracker_class: MagicMock, mock_confirm: MagicMock
    ) -> None:
        """Test warning when deleting repository with installed instructions."""
        # Setup library
        mock_library = MagicMock()
        instructions = [
            LibraryInstruction(
                id="test/inst1",
                name="inst1",
                description="Instruction 1",
                repo_namespace="test/repo",
                repo_url="https://github.com/test/repo",
                repo_name="Test Repo",
                author="Author",
                version="1.0.0",
                file_path="/path/to/inst1.md",
            )
        ]
        repo = LibraryRepository(
            namespace="test/repo",
            name="Test Repo",
            description="Test",
            url="https://github.com/test/repo",
            author="Author",
            version="1.0.0",
            downloaded_at=datetime.now(),
            alias="test-repo",
            instructions=instructions,
        )
        mock_library.get_repository.return_value = repo
        mock_library.remove_repository.return_value = True
        mock_library_class.return_value = mock_library

        # Setup tracker with installed instructions
        mock_tracker = MagicMock()
        installed_record = InstallationRecord(
            instruction_name="inst1",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/install/inst1.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.GLOBAL,
        )
        mock_tracker.list_installations.return_value = [installed_record]
        mock_tracker_class.return_value = mock_tracker

        # User confirms deletion
        mock_confirm.ask.return_value = True

        result = delete_from_library("test/repo", force=False)

        assert result == 0  # Success
        # Should have warned about installed instructions
        mock_confirm.ask.assert_called_once()

    @patch("aiconfigkit.cli.delete.InstallationTracker")
    @patch("aiconfigkit.cli.delete.LibraryManager")
    def test_delete_failure(self, mock_library_class: MagicMock, mock_tracker_class: MagicMock) -> None:
        """Test when repository deletion fails."""
        # Setup library
        mock_library = MagicMock()
        repo = LibraryRepository(
            namespace="test/repo",
            name="Test Repo",
            description="Test",
            url="https://github.com/test/repo",
            author="Author",
            version="1.0.0",
            downloaded_at=datetime.now(),
            alias="test-repo",
            instructions=[],
        )
        mock_library.get_repository.return_value = repo
        mock_library.remove_repository.return_value = False  # Deletion fails
        mock_library_class.return_value = mock_library

        # Setup tracker
        mock_tracker = MagicMock()
        mock_tracker.list_installations.return_value = []
        mock_tracker_class.return_value = mock_tracker

        result = delete_from_library("test/repo", force=True)

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.delete.Confirm")
    @patch("aiconfigkit.cli.delete.InstallationTracker")
    @patch("aiconfigkit.cli.delete.LibraryManager")
    def test_delete_with_many_installed_instructions(
        self, mock_library_class: MagicMock, mock_tracker_class: MagicMock, mock_confirm: MagicMock
    ) -> None:
        """Test warning when deleting repository with >5 installed instructions (shows '... and X more')."""
        # Setup library
        mock_library = MagicMock()
        instructions = [
            LibraryInstruction(
                id=f"test/inst{i}",
                name=f"inst{i}",
                description=f"Instruction {i}",
                repo_namespace="test/repo",
                repo_url="https://github.com/test/repo",
                repo_name="Test Repo",
                author="Author",
                version="1.0.0",
                file_path=f"/path/to/inst{i}.md",
            )
            for i in range(7)  # Create 7 instructions (>5)
        ]
        repo = LibraryRepository(
            namespace="test/repo",
            name="Test Repo",
            description="Test",
            url="https://github.com/test/repo",
            author="Author",
            version="1.0.0",
            downloaded_at=datetime.now(),
            alias="test-repo",
            instructions=instructions,
        )
        mock_library.get_repository.return_value = repo
        mock_library.remove_repository.return_value = True
        mock_library_class.return_value = mock_library

        # Setup tracker with 7 installed instructions
        mock_tracker = MagicMock()
        installed_records = [
            InstallationRecord(
                instruction_name=f"inst{i}",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",
                installed_path=f"/path/to/install/inst{i}.mdc",
                installed_at=datetime.now(),
                scope=InstallationScope.GLOBAL,
            )
            for i in range(7)
        ]
        mock_tracker.list_installations.return_value = installed_records
        mock_tracker_class.return_value = mock_tracker

        # User confirms deletion
        mock_confirm.ask.return_value = True

        result = delete_from_library("test/repo", force=False)

        assert result == 0  # Success
        # Should have shown "... and 2 more" message (line 53 coverage)
        mock_confirm.ask.assert_called_once()
