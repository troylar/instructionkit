"""Unit tests for list CLI command."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from aiconfigkit.cli.list import list_available, list_installed, list_library
from aiconfigkit.core.models import (
    AIToolType,
    InstallationRecord,
    InstallationScope,
    Instruction,
    InstructionBundle,
    LibraryInstruction,
    LibraryRepository,
)


class TestListAvailable:
    """Test list_available function."""

    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_invalid_url(self, mock_valid: MagicMock) -> None:
        """Test listing available with invalid Git URL."""
        mock_valid.return_value = False

        result = list_available("invalid-url")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.list.GitOperations.is_git_installed")
    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_git_not_installed(self, mock_valid: MagicMock, mock_git_installed: MagicMock) -> None:
        """Test listing when Git is not installed."""
        mock_valid.return_value = True
        mock_git_installed.return_value = False

        result = list_available("https://github.com/test/repo")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.list.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.list.GitOperations")
    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_local_path_error(
        self, mock_valid: MagicMock, mock_git_ops_class: MagicMock, mock_cleanup: MagicMock
    ) -> None:
        """Test listing when local path access fails."""
        mock_valid.return_value = True

        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = True
        mock_git_ops.clone_repository.side_effect = RuntimeError("Access denied")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        result = list_available("/local/path")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.list.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.list.GitOperations")
    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_clone_failure(
        self, mock_valid: MagicMock, mock_git_ops_class: MagicMock, mock_cleanup: MagicMock
    ) -> None:
        """Test listing when repository clone fails."""
        mock_valid.return_value = True

        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.side_effect = RuntimeError("Clone failed")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        result = list_available("https://github.com/test/repo")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.list.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.list.RepositoryParser")
    @patch("aiconfigkit.cli.list.GitOperations")
    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_success(
        self,
        mock_valid: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
    ) -> None:
        """Test listing available instructions successfully."""
        mock_valid.return_value = True

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser with instructions and bundles
        instructions = [
            Instruction(name="test1", description="Test 1", content="# Test 1", file_path="test1.md", tags=["python"])
        ]
        bundles = [InstructionBundle(name="bundle1", description="Bundle 1", instructions=["test1"], tags=["python"])]

        mock_repo = MagicMock()
        mock_repo.instructions = instructions
        mock_repo.bundles = bundles

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        result = list_available("https://github.com/test/repo")

        assert result == 0  # Success
        mock_cleanup.assert_called_once()

    @patch("aiconfigkit.cli.list.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.list.RepositoryParser")
    @patch("aiconfigkit.cli.list.GitOperations")
    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_with_tag_filter(
        self,
        mock_valid: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
    ) -> None:
        """Test listing with tag filter."""
        mock_valid.return_value = True

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser with mixed tags
        instructions = [
            Instruction(name="test1", description="Test 1", content="# Test 1", file_path="test1.md", tags=["python"]),
            Instruction(
                name="test2", description="Test 2", content="# Test 2", file_path="test2.md", tags=["javascript"]
            ),
        ]

        mock_repo = MagicMock()
        mock_repo.instructions = instructions
        mock_repo.bundles = []

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        result = list_available("https://github.com/test/repo", tag="python")

        assert result == 0  # Success

    @patch("aiconfigkit.cli.list.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.list.RepositoryParser")
    @patch("aiconfigkit.cli.list.GitOperations")
    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_bundles_only(
        self,
        mock_valid: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
    ) -> None:
        """Test listing bundles only."""
        mock_valid.return_value = True

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser
        bundles = [InstructionBundle(name="bundle1", description="Bundle 1", instructions=["test1"], tags=[])]

        mock_repo = MagicMock()
        mock_repo.instructions = []
        mock_repo.bundles = bundles

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        result = list_available("https://github.com/test/repo", bundles_only=True)

        assert result == 0  # Success

    @patch("aiconfigkit.cli.list.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.list.RepositoryParser")
    @patch("aiconfigkit.cli.list.GitOperations")
    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_empty_result(
        self,
        mock_valid: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
    ) -> None:
        """Test listing with no results."""
        mock_valid.return_value = True

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser with empty content
        mock_repo = MagicMock()
        mock_repo.instructions = []
        mock_repo.bundles = []

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        result = list_available("https://github.com/test/repo")

        assert result == 0  # Success (empty is not an error)

    @patch("aiconfigkit.cli.list.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.list.RepositoryParser")
    @patch("aiconfigkit.cli.list.GitOperations")
    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_instructions_only_with_only_bundles(
        self,
        mock_valid: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
    ) -> None:
        """Test instructions_only filter when repo only has bundles (line 98)."""
        mock_valid.return_value = True

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository with only bundles (no instructions)
        bundles = [InstructionBundle(name="bundle1", description="Bundle 1", instructions=["test1"], tags=[])]

        mock_repo = MagicMock()
        mock_repo.instructions = []
        mock_repo.bundles = bundles

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        result = list_available("https://github.com/test/repo", instructions_only=True)

        assert result == 0  # Success (bundles filtered out, empty result)

    @patch("aiconfigkit.cli.list.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.list.RepositoryParser")
    @patch("aiconfigkit.cli.list.GitOperations")
    @patch("aiconfigkit.cli.list.is_valid_git_url")
    def test_list_available_with_tag_no_results(
        self,
        mock_valid: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
    ) -> None:
        """Test filtering by tag with no matching results (line 103)."""
        mock_valid.return_value = True

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository with instructions that don't match tag filter
        instructions = [
            Instruction(
                name="inst1", description="Instruction 1", content="Some content", file_path="inst1.md", tags=["python"]
            )
        ]

        mock_repo = MagicMock()
        mock_repo.instructions = instructions
        mock_repo.bundles = []

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        # Filter by tag that doesn't exist
        result = list_available("https://github.com/test/repo", tag="javascript")

        assert result == 0  # Success (no matches for tag)


class TestListInstalled:
    """Test list_installed function."""

    @patch("aiconfigkit.cli.list.find_project_root")
    @patch("aiconfigkit.cli.list.InstallationTracker")
    def test_list_installed_no_results(self, mock_tracker_class: MagicMock, mock_find_root: MagicMock) -> None:
        """Test listing installed with no results."""
        mock_find_root.return_value = Path("/project")

        mock_tracker = MagicMock()
        mock_tracker.get_installed_instructions.return_value = []
        mock_tracker_class.return_value = mock_tracker

        result = list_installed()

        assert result == 0  # Success (empty is not an error)

    @patch("aiconfigkit.cli.list.find_project_root")
    @patch("aiconfigkit.cli.list.InstallationTracker")
    def test_list_installed_invalid_tool(self, mock_tracker_class: MagicMock, mock_find_root: MagicMock) -> None:
        """Test listing with invalid tool name."""
        mock_find_root.return_value = Path("/project")

        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        result = list_installed(tool="invalid-tool")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.list.find_project_root")
    @patch("aiconfigkit.cli.list.InstallationTracker")
    def test_list_installed_with_tool_filter(self, mock_tracker_class: MagicMock, mock_find_root: MagicMock) -> None:
        """Test listing with tool filter."""
        mock_find_root.return_value = Path("/project")

        # Setup tracker with cursor installation
        records = [
            InstallationRecord(
                instruction_name="test1",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",
                installed_path="/path/to/test1.mdc",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
            )
        ]

        mock_tracker = MagicMock()
        mock_tracker.get_installed_instructions.return_value = records
        mock_tracker_class.return_value = mock_tracker

        result = list_installed(tool="cursor")

        assert result == 0  # Success
        mock_tracker.get_installed_instructions.assert_called_once()

    @patch("aiconfigkit.cli.list.normalize_repo_url")
    @patch("aiconfigkit.cli.list.find_project_root")
    @patch("aiconfigkit.cli.list.InstallationTracker")
    def test_list_installed_with_repo_filter(
        self, mock_tracker_class: MagicMock, mock_find_root: MagicMock, mock_normalize: MagicMock
    ) -> None:
        """Test listing with repository filter."""
        mock_find_root.return_value = Path("/project")
        mock_normalize.return_value = "https://github.com/test/repo"

        # Setup tracker with installation from specific repo
        records = [
            InstallationRecord(
                instruction_name="test1",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",
                installed_path="/path/to/test1.mdc",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
            )
        ]

        mock_tracker = MagicMock()
        mock_tracker.get_installed_instructions.return_value = records
        mock_tracker_class.return_value = mock_tracker

        result = list_installed(repo="https://github.com/test/repo")

        assert result == 0  # Success

    @patch("aiconfigkit.cli.list.normalize_repo_url")
    @patch("aiconfigkit.cli.list.find_project_root")
    @patch("aiconfigkit.cli.list.InstallationTracker")
    def test_list_installed_no_results_for_tool_and_repo(
        self, mock_tracker_class: MagicMock, mock_find_root: MagicMock, mock_normalize: MagicMock
    ) -> None:
        """Test no results for specific tool and repo filter (line 164)."""
        mock_find_root.return_value = Path("/project")
        mock_normalize.return_value = "https://github.com/test/repo"

        # Setup tracker with empty results
        mock_tracker = MagicMock()
        mock_tracker.get_installed_instructions.return_value = []
        mock_tracker_class.return_value = mock_tracker

        result = list_installed(tool="cursor", repo="https://github.com/test/repo")

        assert result == 0  # Success (no matches)

    @patch("aiconfigkit.cli.list.find_project_root")
    @patch("aiconfigkit.cli.list.InstallationTracker")
    def test_list_installed_no_results_for_tool_only(
        self, mock_tracker_class: MagicMock, mock_find_root: MagicMock
    ) -> None:
        """Test no results for specific tool filter (line 166)."""
        mock_find_root.return_value = Path("/project")

        # Setup tracker to return empty list when queried for claude
        mock_tracker = MagicMock()
        mock_tracker.get_installed_instructions.return_value = []  # No results for claude
        mock_tracker_class.return_value = mock_tracker

        # Filter for tool with no installations
        result = list_installed(tool="claude")

        assert result == 0  # Success (no matches for claude)

    @patch("aiconfigkit.cli.list.normalize_repo_url")
    @patch("aiconfigkit.cli.list.find_project_root")
    @patch("aiconfigkit.cli.list.InstallationTracker")
    def test_list_installed_no_results_for_repo_only(
        self, mock_tracker_class: MagicMock, mock_find_root: MagicMock, mock_normalize: MagicMock
    ) -> None:
        """Test no results for specific repo filter (line 168)."""
        mock_find_root.return_value = Path("/project")

        # Setup normalize_repo_url to return different values for different repos
        def normalize_side_effect(url):
            return url  # Just return as-is for testing

        mock_normalize.side_effect = normalize_side_effect

        # Setup tracker with installation from different repo
        records = [
            InstallationRecord(
                instruction_name="test1",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",  # Different repo
                installed_path="/path/to/test1.mdc",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
            )
        ]

        mock_tracker = MagicMock()
        mock_tracker.get_installed_instructions.return_value = records
        mock_tracker_class.return_value = mock_tracker

        # Filter for different repo (will filter out all records)
        result = list_installed(repo="https://github.com/other/repo")

        assert result == 0  # Success (no matches for that repo)


class TestListLibrary:
    """Test list_library function."""

    @patch("aiconfigkit.cli.list.LibraryManager")
    def test_list_library_empty(self, mock_library_class: MagicMock) -> None:
        """Test listing empty library."""
        mock_library = MagicMock()
        mock_library.list_repositories.return_value = []
        mock_library_class.return_value = mock_library

        result = list_library()

        assert result == 0  # Success

    @patch("aiconfigkit.cli.list.LibraryManager")
    def test_list_library_with_sources(self, mock_library_class: MagicMock) -> None:
        """Test listing library sources."""
        # Create library repositories
        repos = [
            LibraryRepository(
                namespace="test/repo1",
                name="Test Repo 1",
                description="Test",
                url="https://github.com/test/repo1",
                author="Author",
                version="1.0.0",
                downloaded_at=datetime.now(),
                alias="repo1",
                instructions=[],
            ),
            LibraryRepository(
                namespace="test/repo2",
                name="Test Repo 2",
                description="Test",
                url="https://github.com/test/repo2",
                author="Author",
                version="2.0.0",
                downloaded_at=datetime.now(),
                alias="repo2",
                instructions=[],
            ),
        ]

        mock_library = MagicMock()
        mock_library.list_repositories.return_value = repos
        mock_library_class.return_value = mock_library

        result = list_library()

        assert result == 0  # Success

    @patch("aiconfigkit.cli.list.LibraryManager")
    def test_list_library_with_filter_match(self, mock_library_class: MagicMock) -> None:
        """Test listing library with matching filter."""
        repos = [
            LibraryRepository(
                namespace="test/repo1",
                name="Test Repo 1",
                description="Test",
                url="https://github.com/test/repo1",
                author="Author",
                version="1.0.0",
                downloaded_at=datetime.now(),
                alias="repo1",
                instructions=[],
            )
        ]

        mock_library = MagicMock()
        mock_library.list_repositories.return_value = repos
        mock_library_class.return_value = mock_library

        result = list_library(repo_filter="repo1")

        assert result == 0  # Success

    @patch("aiconfigkit.cli.list.LibraryManager")
    def test_list_library_with_filter_no_match(self, mock_library_class: MagicMock) -> None:
        """Test listing library with non-matching filter."""
        repos = [
            LibraryRepository(
                namespace="test/repo1",
                name="Test Repo 1",
                description="Test",
                url="https://github.com/test/repo1",
                author="Author",
                version="1.0.0",
                downloaded_at=datetime.now(),
                alias="repo1",
                instructions=[],
            )
        ]

        mock_library = MagicMock()
        mock_library.list_repositories.return_value = repos
        mock_library_class.return_value = mock_library

        result = list_library(repo_filter="nonexistent")

        assert result == 1  # Error - no match

    @patch("aiconfigkit.cli.list.LibraryManager")
    def test_list_library_with_instructions(self, mock_library_class: MagicMock) -> None:
        """Test listing library with instructions view."""
        instructions = [
            LibraryInstruction(
                id="test/repo1/inst1",
                name="inst1",
                description="Instruction 1",
                repo_namespace="test/repo1",
                repo_url="https://github.com/test/repo1",
                repo_name="Test Repo 1",
                author="Author",
                version="1.0.0",
                file_path="/path/to/inst1.md",
                tags=["python", "testing", "debug", "extra"],
            )
        ]

        repos = [
            LibraryRepository(
                namespace="test/repo1",
                name="Test Repo 1",
                description="Test",
                url="https://github.com/test/repo1",
                author="Author",
                version="1.0.0",
                downloaded_at=datetime.now(),
                alias="repo1",
                instructions=instructions,
            )
        ]

        mock_library = MagicMock()
        mock_library.list_repositories.return_value = repos
        mock_library_class.return_value = mock_library

        result = list_library(show_instructions=True)

        assert result == 0  # Success
