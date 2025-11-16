"""Unit tests for download CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from aiconfigkit.cli.download import download_instructions
from aiconfigkit.core.git_operations import RepositoryOperationError
from aiconfigkit.core.models import Instruction


class TestDownloadInstructions:
    """Test download_instructions function."""

    @patch("aiconfigkit.cli.download.GitOperations.is_local_path")
    @patch("aiconfigkit.cli.download.GitOperations.detect_ref_type")
    def test_download_remote_invalid_reference(self, mock_detect_ref: MagicMock, mock_is_local: MagicMock) -> None:
        """Test downloading with invalid reference."""
        mock_is_local.return_value = False
        mock_detect_ref.side_effect = RepositoryOperationError("invalid_reference", "Ref not found")

        result = download_instructions("https://github.com/test/repo", ref="invalid-tag")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.download.GitOperations.is_local_path")
    @patch("aiconfigkit.cli.download.GitOperations.detect_ref_type")
    def test_download_remote_network_error(self, mock_detect_ref: MagicMock, mock_is_local: MagicMock) -> None:
        """Test downloading with network error."""
        mock_is_local.return_value = False
        mock_detect_ref.side_effect = RepositoryOperationError("network_error", "Connection failed")

        result = download_instructions("https://github.com/test/repo", ref="v1.0.0")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.download.GitOperations.is_local_path")
    @patch("aiconfigkit.cli.download.GitOperations.detect_ref_type")
    def test_download_remote_generic_ref_error(self, mock_detect_ref: MagicMock, mock_is_local: MagicMock) -> None:
        """Test downloading with generic ref validation error."""
        mock_is_local.return_value = False
        mock_detect_ref.side_effect = RepositoryOperationError("unknown", "Unknown error")

        result = download_instructions("https://github.com/test/repo", ref="v1.0.0")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.download.GitOperations.is_local_path")
    def test_download_local_with_ref(self, mock_is_local: MagicMock) -> None:
        """Test downloading from local path with ref (should error)."""
        mock_is_local.return_value = True

        result = download_instructions("/local/path", ref="v1.0.0")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.download.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.download.LibraryManager")
    @patch("aiconfigkit.cli.download.RepositoryParser")
    @patch("aiconfigkit.cli.download.GitOperations")
    def test_download_local_success(
        self,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_library_class: MagicMock,
        mock_cleanup: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test downloading from local path successfully."""
        repo_path = tmp_path / "local_repo"
        repo_path.mkdir()

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = True
        mock_git_ops_class.is_local_path.return_value = True

        # Setup repository parser
        inst_file = repo_path / "test.md"
        inst_file.write_text("# Test")

        instruction = Instruction(name="test", description="Test", content="# Test", file_path="test.md", tags=[])

        mock_repo = MagicMock()
        mock_repo.instructions = [instruction]
        mock_repo.metadata = {"name": "Test Repo", "version": "1.0.0", "author": "Test", "description": "Test"}

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        # Setup library
        library_dir = tmp_path / "library"
        library_dir.mkdir()

        mock_library = MagicMock()
        mock_library.library_dir = library_dir
        mock_library.get_repo_namespace.return_value = "test/repo"
        mock_library.get_repository.return_value = None
        mock_library.add_repository.return_value = MagicMock(alias="test-repo", namespace="test/repo")
        mock_library_class.return_value = mock_library

        result = download_instructions(str(repo_path))

        assert result == 0  # Success
        mock_library.add_repository.assert_called_once()

    @patch("aiconfigkit.cli.download.shutil.rmtree")
    @patch("tempfile.mkdtemp")
    @patch("aiconfigkit.cli.download.GitOperations")
    def test_download_remote_clone_failure(
        self, mock_git_ops_class: MagicMock, mock_mkdtemp: MagicMock, mock_rmtree: MagicMock, tmp_path: Path
    ) -> None:
        """Test downloading when clone fails."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()

        mock_mkdtemp.return_value = str(temp_dir)

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops_class.is_local_path.return_value = False
        mock_git_ops_class.detect_ref_type.return_value = ("v1.0.0", MagicMock(value="tag"))
        mock_git_ops_class.clone_at_ref.side_effect = RepositoryOperationError("clone_failed", "Clone failed")

        result = download_instructions("https://github.com/test/repo", ref="v1.0.0")

        assert result == 1  # Error code
        mock_rmtree.assert_called_once()

    @patch("aiconfigkit.cli.download.LibraryManager")
    @patch("aiconfigkit.cli.download.RepositoryParser")
    @patch("aiconfigkit.cli.download.GitOperations.is_local_path")
    def test_download_already_exists_no_force(
        self, mock_is_local: MagicMock, mock_parser_class: MagicMock, mock_library_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test downloading when repository already exists without force."""
        mock_is_local.return_value = True

        # Setup repository parser
        mock_repo = MagicMock()
        mock_repo.instructions = []
        mock_repo.metadata = {"name": "Test Repo"}

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        # Setup library with existing repository
        existing_repo = MagicMock(alias="test-repo")
        mock_library = MagicMock()
        mock_library.get_repo_namespace.return_value = "test/repo"
        mock_library.get_repository.return_value = existing_repo
        mock_library_class.return_value = mock_library

        result = download_instructions(str(tmp_path), force=False)

        assert result == 1  # Error code
        mock_library.add_repository.assert_not_called()

    @patch("aiconfigkit.cli.download.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.download.LibraryManager")
    @patch("aiconfigkit.cli.download.RepositoryParser")
    @patch("aiconfigkit.cli.download.GitOperations.is_local_path")
    def test_download_file_not_found_warning(
        self,
        mock_is_local: MagicMock,
        mock_parser_class: MagicMock,
        mock_library_class: MagicMock,
        mock_cleanup: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test downloading when instruction file doesn't exist (warning)."""
        mock_is_local.return_value = True

        # Setup repository parser with instruction pointing to non-existent file
        instruction = Instruction(
            name="test", description="Test", content="# Test", file_path="nonexistent.md", tags=[]
        )

        mock_repo = MagicMock()
        mock_repo.instructions = [instruction]
        mock_repo.metadata = {"name": "Test Repo", "version": "1.0.0"}

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        # Setup library
        library_dir = tmp_path / "library"
        library_dir.mkdir()

        mock_library = MagicMock()
        mock_library.library_dir = library_dir
        mock_library.get_repo_namespace.return_value = "test/repo"
        mock_library.get_repository.return_value = None
        mock_library.add_repository.return_value = MagicMock(alias="test-repo")
        mock_library_class.return_value = mock_library

        result = download_instructions(str(tmp_path))

        # Should succeed but with warning (no instructions added)
        assert result == 0  # Success
        # Verify add_repository was called with empty instructions list
        call_args = mock_library.add_repository.call_args
        assert call_args[1]["instructions"] == []

    @patch("aiconfigkit.cli.download.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.download.shutil.copytree")
    @patch("aiconfigkit.cli.download.shutil.rmtree")
    @patch("aiconfigkit.cli.download.LibraryManager")
    @patch("aiconfigkit.cli.download.RepositoryParser")
    @patch("tempfile.mkdtemp")
    @patch("aiconfigkit.cli.download.GitOperations")
    def test_download_remote_with_git_dir(
        self,
        mock_git_ops_class: MagicMock,
        mock_mkdtemp: MagicMock,
        mock_parser_class: MagicMock,
        mock_library_class: MagicMock,
        mock_rmtree: MagicMock,
        mock_copytree: MagicMock,
        mock_cleanup: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test downloading remote repository preserves .git directory."""
        # Setup temp directory
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        git_dir = temp_dir / ".git"
        git_dir.mkdir()

        mock_mkdtemp.return_value = str(temp_dir)

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops_class.is_local_path.return_value = False
        mock_git_ops_class.detect_ref_type.return_value = ("v1.0.0", MagicMock(value="tag"))
        mock_git_ops_class.clone_at_ref.return_value = None

        # Setup instruction file
        inst_file = temp_dir / "test.md"
        inst_file.write_text("# Test")

        # Setup repository parser
        instruction = Instruction(name="test", description="Test", content="# Test", file_path="test.md", tags=[])

        mock_repo = MagicMock()
        mock_repo.instructions = [instruction]
        mock_repo.metadata = {"name": "Test Repo", "version": "1.0.0"}

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        # Setup library
        library_dir = tmp_path / "library"
        library_dir.mkdir()

        mock_library = MagicMock()
        mock_library.library_dir = library_dir
        mock_library.get_versioned_namespace.return_value = "test/repo@v1.0.0"
        mock_library.get_repository.return_value = None
        mock_library.add_repository.return_value = MagicMock(alias="test-repo", namespace="test/repo@v1.0.0")
        mock_library_class.return_value = mock_library

        result = download_instructions("https://github.com/test/repo", ref="v1.0.0")

        assert result == 0  # Success
        # Verify .git directory was copied
        mock_copytree.assert_called()

    @patch("aiconfigkit.cli.download.GitOperations.is_local_path")
    @patch("aiconfigkit.cli.download.RepositoryParser")
    def test_download_parse_error(self, mock_parser_class: MagicMock, mock_is_local: MagicMock) -> None:
        """Test downloading when parsing fails."""
        mock_is_local.return_value = True

        # Parser raises FileNotFoundError
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = FileNotFoundError("templatekit.yaml not found")
        mock_parser_class.return_value = mock_parser

        result = download_instructions("/local/path")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.download.GitOperations.is_local_path")
    @patch("aiconfigkit.cli.download.RepositoryParser")
    def test_download_generic_exception(self, mock_parser_class: MagicMock, mock_is_local: MagicMock) -> None:
        """Test downloading with generic exception."""
        mock_is_local.return_value = True

        # Parser raises generic exception
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = RuntimeError("Unexpected error")
        mock_parser_class.return_value = mock_parser

        result = download_instructions("/local/path")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.download.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.download.LibraryManager")
    @patch("aiconfigkit.cli.download.RepositoryParser")
    @patch("tempfile.mkdtemp")
    @patch("aiconfigkit.cli.download.GitOperations")
    def test_download_remote_with_branch_ref(
        self,
        mock_git_ops_class: MagicMock,
        mock_mkdtemp: MagicMock,
        mock_parser_class: MagicMock,
        mock_library_class: MagicMock,
        mock_cleanup: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test downloading from remote repository with branch reference."""
        # Setup temp directory
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()

        mock_mkdtemp.return_value = str(temp_dir)

        # Setup Git operations
        ref_type_mock = MagicMock()
        ref_type_mock.value = "branch"

        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops_class.is_local_path.return_value = False
        mock_git_ops_class.detect_ref_type.return_value = ("main", ref_type_mock)
        mock_git_ops_class.clone_at_ref.return_value = None

        # Setup instruction file
        inst_file = temp_dir / "test.md"
        inst_file.write_text("# Test")

        # Setup repository parser
        instruction = Instruction(name="test", description="Test", content="# Test", file_path="test.md", tags=[])

        mock_repo = MagicMock()
        mock_repo.instructions = [instruction]
        mock_repo.metadata = {"name": "Test Repo", "version": "1.0.0"}

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_repo
        mock_parser_class.return_value = mock_parser

        # Setup library
        library_dir = tmp_path / "library"
        library_dir.mkdir()

        mock_library = MagicMock()
        mock_library.library_dir = library_dir
        mock_library.get_versioned_namespace.return_value = "test/repo@main"
        mock_library.get_repository.return_value = None
        mock_library.add_repository.return_value = MagicMock(alias="test-repo", namespace="test/repo@main")
        mock_library_class.return_value = mock_library

        result = download_instructions("https://github.com/test/repo", ref="main")

        assert result == 0  # Success
        mock_cleanup.assert_called_once()
