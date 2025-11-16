"""Unit tests for install CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from aiconfigkit.cli.install import _get_ai_tool, install_instruction
from aiconfigkit.core.models import Instruction


class TestInstallInstruction:
    """Test install_instruction function."""

    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_invalid_git_url(self, mock_valid: MagicMock) -> None:
        """Test installing with invalid Git URL."""
        mock_valid.return_value = False

        result = install_instruction("test", "invalid-url")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_invalid_conflict_strategy(self, mock_valid: MagicMock) -> None:
        """Test installing with invalid conflict strategy."""
        mock_valid.return_value = True

        result = install_instruction("test", "https://github.com/test/repo", conflict_strategy="invalid")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_no_project_root(self, mock_valid: MagicMock, mock_find_root: MagicMock) -> None:
        """Test installing when project root cannot be detected."""
        mock_valid.return_value = True
        mock_find_root.return_value = None

        result = install_instruction("test", "https://github.com/test/repo")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.install.GitOperations.is_git_installed")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_git_not_installed(
        self, mock_valid: MagicMock, mock_find_root: MagicMock, mock_git_installed: MagicMock
    ) -> None:
        """Test installing when Git is not installed."""
        mock_valid.return_value = True
        mock_find_root.return_value = Path("/project")
        mock_git_installed.return_value = False

        result = install_instruction("test", "https://github.com/test/repo")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.install._get_ai_tool")
    @patch("aiconfigkit.cli.install.GitOperations.is_git_installed")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_no_ai_tool(
        self,
        mock_valid: MagicMock,
        mock_find_root: MagicMock,
        mock_git_installed: MagicMock,
        mock_get_tool: MagicMock,
    ) -> None:
        """Test installing when AI tool cannot be determined."""
        mock_valid.return_value = True
        mock_find_root.return_value = Path("/project")
        mock_git_installed.return_value = True
        mock_get_tool.return_value = None

        result = install_instruction("test", "https://github.com/test/repo")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.install._get_ai_tool")
    @patch("aiconfigkit.cli.install.GitOperations.is_git_installed")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_ai_tool_validation_error(
        self,
        mock_valid: MagicMock,
        mock_find_root: MagicMock,
        mock_git_installed: MagicMock,
        mock_get_tool: MagicMock,
    ) -> None:
        """Test installing when AI tool validation fails."""
        mock_valid.return_value = True
        mock_find_root.return_value = Path("/project")
        mock_git_installed.return_value = True

        mock_tool = MagicMock()
        mock_tool.validate_installation.return_value = "Tool not configured properly"
        mock_get_tool.return_value = mock_tool

        result = install_instruction("test", "https://github.com/test/repo")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.install.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.install.RepositoryParser")
    @patch("aiconfigkit.cli.install.GitOperations")
    @patch("aiconfigkit.cli.install._get_ai_tool")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_local_directory(
        self,
        mock_valid: MagicMock,
        mock_find_root: MagicMock,
        mock_get_tool: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test installing from local directory."""
        mock_valid.return_value = True
        project_root = tmp_path / "project"
        project_root.mkdir()
        mock_find_root.return_value = project_root

        # Setup AI tool
        mock_tool = MagicMock()
        mock_tool.tool_name = "Cursor"
        mock_tool.validate_installation.return_value = None
        mock_tool.get_instruction_path.return_value = project_root / ".cursor" / "rules" / "test.mdc"
        mock_tool.tool_type = "cursor"
        mock_get_tool.return_value = mock_tool

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_git_installed.return_value = True
        mock_git_ops.is_local_path.return_value = True
        mock_git_ops.clone_repository.return_value = Path("/local/path")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser
        mock_instruction = Instruction(
            name="test", description="Test", content="# Test content", file_path="test.md", checksum="abc123"
        )
        mock_parser = MagicMock()
        mock_parser.parse.return_value = MagicMock(url="file:///local/path")
        mock_parser.get_instruction_by_name.return_value = mock_instruction
        mock_parser_class.return_value = mock_parser

        # Run installation
        result = install_instruction("test", "/local/path")

        assert result == 0  # Success
        mock_cleanup.assert_called_once_with(Path("/local/path"), is_temp=False)

    @patch("aiconfigkit.cli.install.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.install.GitOperations")
    @patch("aiconfigkit.cli.install._get_ai_tool")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_clone_failure(
        self,
        mock_valid: MagicMock,
        mock_find_root: MagicMock,
        mock_get_tool: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_cleanup: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test installing when repository clone fails."""
        mock_valid.return_value = True
        mock_find_root.return_value = tmp_path

        # Setup AI tool
        mock_tool = MagicMock()
        mock_tool.validate_installation.return_value = None
        mock_get_tool.return_value = mock_tool

        # Setup Git operations to fail
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.side_effect = RuntimeError("Clone failed")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        result = install_instruction("test", "https://github.com/test/repo")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.install.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.install.RepositoryParser")
    @patch("aiconfigkit.cli.install.GitOperations")
    @patch("aiconfigkit.cli.install._get_ai_tool")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_instruction_not_found(
        self,
        mock_valid: MagicMock,
        mock_find_root: MagicMock,
        mock_get_tool: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test installing when instruction is not found in repository."""
        mock_valid.return_value = True
        mock_find_root.return_value = tmp_path

        # Setup AI tool
        mock_tool = MagicMock()
        mock_tool.validate_installation.return_value = None
        mock_get_tool.return_value = mock_tool

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser - instruction not found
        mock_parser = MagicMock()
        mock_parser.parse.return_value = MagicMock(url="https://github.com/test/repo")
        mock_parser.get_instruction_by_name.return_value = None
        mock_parser_class.return_value = mock_parser

        result = install_instruction("nonexistent", "https://github.com/test/repo")

        assert result == 1  # Error code
        mock_cleanup.assert_called_once()

    @patch("aiconfigkit.cli.install.InstallationTracker")
    @patch("aiconfigkit.cli.install.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.install.RepositoryParser")
    @patch("aiconfigkit.cli.install.GitOperations")
    @patch("aiconfigkit.cli.install._get_ai_tool")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_skip_existing(
        self,
        mock_valid: MagicMock,
        mock_find_root: MagicMock,
        mock_get_tool: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
        mock_tracker_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test installing with SKIP strategy when instruction exists."""
        mock_valid.return_value = True
        project_root = tmp_path / "project"
        project_root.mkdir()
        mock_find_root.return_value = project_root

        # Create existing file
        existing_file = project_root / ".cursor" / "rules" / "test.mdc"
        existing_file.parent.mkdir(parents=True)
        existing_file.write_text("existing")

        # Setup AI tool
        mock_tool = MagicMock()
        mock_tool.validate_installation.return_value = None
        mock_tool.get_instruction_path.return_value = existing_file
        mock_get_tool.return_value = mock_tool

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser
        mock_instruction = Instruction(
            name="test", description="Test", content="# Test content", file_path="test.md", checksum="abc123"
        )
        mock_parser = MagicMock()
        mock_parser.parse.return_value = MagicMock(url="https://github.com/test/repo")
        mock_parser.get_instruction_by_name.return_value = mock_instruction
        mock_parser_class.return_value = mock_parser

        # Setup tracker
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        result = install_instruction("test", "https://github.com/test/repo", conflict_strategy="skip")

        assert result == 0  # Success (but skipped)
        # File content should remain unchanged
        assert existing_file.read_text() == "existing"
        mock_tracker.add_installation.assert_not_called()

    @patch("aiconfigkit.cli.install.ChecksumValidator")
    @patch("aiconfigkit.cli.install.InstallationTracker")
    @patch("aiconfigkit.cli.install.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.install.RepositoryParser")
    @patch("aiconfigkit.cli.install.GitOperations")
    @patch("aiconfigkit.cli.install._get_ai_tool")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_rename_existing(
        self,
        mock_valid: MagicMock,
        mock_find_root: MagicMock,
        mock_get_tool: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
        mock_tracker_class: MagicMock,
        mock_checksum_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test installing with RENAME strategy when instruction exists."""
        mock_valid.return_value = True
        project_root = tmp_path / "project"
        project_root.mkdir()
        mock_find_root.return_value = project_root

        # Create existing file
        existing_file = project_root / ".cursor" / "rules" / "test.mdc"
        existing_file.parent.mkdir(parents=True)
        existing_file.write_text("existing")

        # Setup AI tool - use real Path objects for proper file operations
        mock_tool = MagicMock()
        mock_tool.validate_installation.return_value = None
        mock_tool.tool_type = "cursor"
        # First call returns existing file, second call will be used after rename
        mock_tool.get_instruction_path.return_value = existing_file
        mock_get_tool.return_value = mock_tool

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser
        mock_instruction = Instruction(
            name="test", description="Test", content="# Test content", file_path="test.md", checksum="abc123"
        )
        mock_parser = MagicMock()
        mock_parser.parse.return_value = MagicMock(url="https://github.com/test/repo")
        mock_parser.get_instruction_by_name.return_value = mock_instruction
        mock_parser_class.return_value = mock_parser

        # Setup checksum validator to pass
        mock_checksum = MagicMock()
        mock_checksum.validate.return_value = None  # No exception = valid
        mock_checksum_class.return_value = mock_checksum

        # Setup tracker
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        result = install_instruction("test", "https://github.com/test/repo", conflict_strategy="rename")

        assert result == 0  # Success
        # With real ConflictResolver, a renamed file should be created (test-1.mdc)
        # Check that tracker was called (file was installed somewhere)
        mock_tracker.add_installation.assert_called_once()

    @patch("aiconfigkit.cli.install.ChecksumValidator")
    @patch("aiconfigkit.cli.install.InstallationTracker")
    @patch("aiconfigkit.cli.install.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.install.RepositoryParser")
    @patch("aiconfigkit.cli.install.GitOperations")
    @patch("aiconfigkit.cli.install._get_ai_tool")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_checksum_validation_failure(
        self,
        mock_valid: MagicMock,
        mock_find_root: MagicMock,
        mock_get_tool: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
        mock_tracker_class: MagicMock,
        mock_checksum_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test installing when checksum validation fails."""
        mock_valid.return_value = True
        project_root = tmp_path / "project"
        project_root.mkdir()
        mock_find_root.return_value = project_root

        # Setup AI tool
        mock_tool = MagicMock()
        mock_tool.validate_installation.return_value = None
        target_file = project_root / ".cursor" / "rules" / "test.mdc"
        mock_tool.get_instruction_path.return_value = target_file
        mock_get_tool.return_value = mock_tool

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser
        mock_instruction = Instruction(
            name="test", description="Test", content="# Test content", file_path="test.md", checksum="abc123"
        )
        mock_parser = MagicMock()
        mock_parser.parse.return_value = MagicMock(url="https://github.com/test/repo")
        mock_parser.get_instruction_by_name.return_value = mock_instruction
        mock_parser_class.return_value = mock_parser

        # Setup checksum validator to fail
        mock_checksum = MagicMock()
        mock_checksum.validate.side_effect = ValueError("Checksum mismatch")
        mock_checksum_class.return_value = mock_checksum

        # Setup tracker
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        result = install_instruction("test", "https://github.com/test/repo")

        assert result == 0  # Success (but no instructions installed)
        # File should not be created due to checksum failure
        assert not target_file.exists()
        mock_tracker.add_installation.assert_not_called()

    @patch("aiconfigkit.cli.install.ChecksumValidator")
    @patch("aiconfigkit.cli.install.InstallationTracker")
    @patch("aiconfigkit.cli.install.GitOperations.cleanup_repository")
    @patch("aiconfigkit.cli.install.RepositoryParser")
    @patch("aiconfigkit.cli.install.GitOperations")
    @patch("aiconfigkit.cli.install._get_ai_tool")
    @patch("aiconfigkit.cli.install.find_project_root")
    @patch("aiconfigkit.cli.install.is_valid_git_url")
    def test_install_bundle(
        self,
        mock_valid: MagicMock,
        mock_find_root: MagicMock,
        mock_get_tool: MagicMock,
        mock_git_ops_class: MagicMock,
        mock_parser_class: MagicMock,
        mock_cleanup: MagicMock,
        mock_tracker_class: MagicMock,
        mock_checksum_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test installing a bundle of instructions."""
        mock_valid.return_value = True
        project_root = tmp_path / "project"
        project_root.mkdir()
        mock_find_root.return_value = project_root

        # Setup AI tool with real path generation
        mock_tool = MagicMock()
        mock_tool.validate_installation.return_value = None
        mock_tool.tool_type = "cursor"

        def get_path(name, scope, root):
            return root / ".cursor" / "rules" / f"{name}.mdc"

        mock_tool.get_instruction_path.side_effect = get_path
        mock_get_tool.return_value = mock_tool

        # Setup Git operations
        mock_git_ops = MagicMock()
        mock_git_ops.is_local_path.return_value = False
        mock_git_ops.clone_repository.return_value = Path("/tmp/repo")
        mock_git_ops_class.return_value = mock_git_ops
        mock_git_ops_class.is_git_installed.return_value = True

        # Setup repository parser with bundle
        instructions = [
            Instruction(name="test1", description="Test 1", content="# Test 1", file_path="test1.md", checksum="abc"),
            Instruction(name="test2", description="Test 2", content="# Test 2", file_path="test2.md", checksum="def"),
        ]
        mock_parser = MagicMock()
        mock_parser.parse.return_value = MagicMock(url="https://github.com/test/repo")
        mock_parser.get_instructions_for_bundle.return_value = instructions
        mock_parser_class.return_value = mock_parser

        # Setup checksum validator to pass
        mock_checksum = MagicMock()
        mock_checksum.validate.return_value = None  # No exception = valid
        mock_checksum_class.return_value = mock_checksum

        # Setup tracker
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        result = install_instruction("test-bundle", "https://github.com/test/repo", bundle=True)

        assert result == 0  # Success
        # Both instructions should be installed (verify via tracker calls)
        assert mock_tracker.add_installation.call_count == 2
        # Files should exist in the project
        assert (project_root / ".cursor" / "rules" / "test1.mdc").exists()
        assert (project_root / ".cursor" / "rules" / "test2.mdc").exists()
        # Verify content
        assert (project_root / ".cursor" / "rules" / "test1.mdc").read_text() == "# Test 1"
        assert (project_root / ".cursor" / "rules" / "test2.mdc").read_text() == "# Test 2"


class TestGetAITool:
    """Test _get_ai_tool helper function."""

    @patch("aiconfigkit.cli.install.get_detector")
    def test_get_ai_tool_by_name(self, mock_get_detector: MagicMock) -> None:
        """Test getting AI tool by name."""
        mock_tool = MagicMock()
        mock_tool.is_installed.return_value = True

        mock_detector = MagicMock()
        mock_detector.get_tool_by_name.return_value = mock_tool
        mock_get_detector.return_value = mock_detector

        result = _get_ai_tool("cursor")

        assert result == mock_tool
        mock_detector.get_tool_by_name.assert_called_once_with("cursor")

    @patch("aiconfigkit.cli.install.get_detector")
    def test_get_ai_tool_not_installed(self, mock_get_detector: MagicMock) -> None:
        """Test getting AI tool that is not installed."""
        mock_tool = MagicMock()
        mock_tool.is_installed.return_value = False
        mock_tool.tool_name = "Cursor"

        mock_detector = MagicMock()
        mock_detector.get_tool_by_name.return_value = mock_tool
        mock_get_detector.return_value = mock_detector

        result = _get_ai_tool("cursor")

        assert result is None

    @patch("aiconfigkit.cli.install.get_detector")
    def test_get_ai_tool_auto_detect(self, mock_get_detector: MagicMock) -> None:
        """Test auto-detecting primary AI tool."""
        mock_tool = MagicMock()

        mock_detector = MagicMock()
        mock_detector.get_primary_tool.return_value = mock_tool
        mock_get_detector.return_value = mock_detector

        result = _get_ai_tool(None)

        assert result == mock_tool
        mock_detector.get_primary_tool.assert_called_once()
