"""Unit tests for uninstall CLI command."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from aiconfigkit.cli.uninstall import uninstall_instruction
from aiconfigkit.core.models import AIToolType, InstallationRecord, InstallationScope


class TestUninstallInstruction:
    """Test uninstall_instruction function."""

    @patch("aiconfigkit.cli.uninstall.find_project_root")
    @patch("aiconfigkit.cli.uninstall.InstallationTracker")
    def test_uninstall_not_installed(self, mock_tracker_class: MagicMock, mock_find_root: MagicMock) -> None:
        """Test uninstalling instruction that is not installed."""
        mock_find_root.return_value = Path("/project")

        mock_tracker = MagicMock()
        mock_tracker.get_installed_instructions.return_value = []
        mock_tracker_class.return_value = mock_tracker

        result = uninstall_instruction("nonexistent-instruction")

        assert result == 1  # Error code

    @patch("aiconfigkit.cli.uninstall.find_project_root")
    @patch("aiconfigkit.cli.uninstall.InstallationTracker")
    def test_uninstall_invalid_tool(self, mock_tracker_class: MagicMock, mock_find_root: MagicMock) -> None:
        """Test uninstalling with invalid tool name."""
        mock_find_root.return_value = Path("/project")

        mock_tracker = MagicMock()
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        mock_tracker.get_installed_instructions.return_value = [record]
        mock_tracker_class.return_value = mock_tracker

        result = uninstall_instruction("test-instruction", tool="invalid-tool")

        assert result == 1  # Error code for invalid tool

    @patch("aiconfigkit.cli.uninstall.get_detector")
    @patch("aiconfigkit.cli.uninstall.find_project_root")
    @patch("aiconfigkit.cli.uninstall.InstallationTracker")
    @patch("aiconfigkit.cli.uninstall.Path")
    def test_uninstall_with_force(
        self,
        mock_path_class: MagicMock,
        mock_tracker_class: MagicMock,
        mock_find_root: MagicMock,
        mock_get_detector: MagicMock,
    ) -> None:
        """Test uninstalling with force flag (no confirmation)."""
        project_root = Path("/project")
        mock_find_root.return_value = project_root

        # Setup tracker
        mock_tracker = MagicMock()
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        mock_tracker.get_installed_instructions.return_value = [record]
        mock_tracker_class.return_value = mock_tracker

        # Setup file
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_path_class.return_value = mock_file

        # Setup AI tool detector
        mock_tool = MagicMock()
        mock_tool.tool_name = "Cursor"
        mock_detector = MagicMock()
        mock_detector.get_tool_by_type.return_value = mock_tool
        mock_get_detector.return_value = mock_detector

        # Execute with force=True (should skip confirmation)
        result = uninstall_instruction("test-instruction", force=True)

        assert result == 0  # Success
        mock_file.unlink.assert_called_once()
        mock_tracker.remove_installation.assert_called_once()

    @patch("aiconfigkit.cli.uninstall.typer.confirm")
    @patch("aiconfigkit.cli.uninstall.find_project_root")
    @patch("aiconfigkit.cli.uninstall.InstallationTracker")
    def test_uninstall_cancelled_by_user(
        self,
        mock_tracker_class: MagicMock,
        mock_find_root: MagicMock,
        mock_confirm: MagicMock,
    ) -> None:
        """Test uninstalling when user cancels confirmation."""
        mock_find_root.return_value = Path("/project")

        # Setup tracker
        mock_tracker = MagicMock()
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        mock_tracker.get_installed_instructions.return_value = [record]
        mock_tracker_class.return_value = mock_tracker

        # User cancels
        mock_confirm.return_value = False

        result = uninstall_instruction("test-instruction", force=False)

        assert result == 0  # Success (cancelled, not an error)
        mock_tracker.remove_installation.assert_not_called()

    @patch("aiconfigkit.cli.uninstall.typer.confirm")
    @patch("aiconfigkit.cli.uninstall.get_detector")
    @patch("aiconfigkit.cli.uninstall.find_project_root")
    @patch("aiconfigkit.cli.uninstall.InstallationTracker")
    @patch("aiconfigkit.cli.uninstall.Path")
    def test_uninstall_file_not_found(
        self,
        mock_path_class: MagicMock,
        mock_tracker_class: MagicMock,
        mock_find_root: MagicMock,
        mock_get_detector: MagicMock,
        mock_confirm: MagicMock,
    ) -> None:
        """Test uninstalling when installed file doesn't exist (warning case)."""
        project_root = Path("/project")
        mock_find_root.return_value = project_root

        # Setup tracker
        mock_tracker = MagicMock()
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        mock_tracker.get_installed_instructions.return_value = [record]
        mock_tracker_class.return_value = mock_tracker

        # File doesn't exist
        mock_file = MagicMock()
        mock_file.exists.return_value = False
        mock_path_class.return_value = mock_file

        # Setup AI tool detector
        mock_tool = MagicMock()
        mock_tool.tool_name = "Cursor"
        mock_detector = MagicMock()
        mock_detector.get_tool_by_type.return_value = mock_tool
        mock_get_detector.return_value = mock_detector

        # User confirms
        mock_confirm.return_value = True

        result = uninstall_instruction("test-instruction", force=False)

        assert result == 0  # Success (warning, but not an error)
        mock_file.unlink.assert_not_called()  # File doesn't exist
        mock_tracker.remove_installation.assert_called_once()

    @patch("aiconfigkit.cli.uninstall.typer.confirm")
    @patch("aiconfigkit.cli.uninstall.get_detector")
    @patch("aiconfigkit.cli.uninstall.find_project_root")
    @patch("aiconfigkit.cli.uninstall.InstallationTracker")
    def test_uninstall_unknown_tool(
        self,
        mock_tracker_class: MagicMock,
        mock_find_root: MagicMock,
        mock_get_detector: MagicMock,
        mock_confirm: MagicMock,
    ) -> None:
        """Test uninstalling when AI tool is unknown."""
        project_root = Path("/project")
        mock_find_root.return_value = project_root

        # Setup tracker
        mock_tracker = MagicMock()
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        mock_tracker.get_installed_instructions.return_value = [record]
        mock_tracker_class.return_value = mock_tracker

        # Detector returns None (unknown tool)
        mock_detector = MagicMock()
        mock_detector.get_tool_by_type.return_value = None
        mock_get_detector.return_value = mock_detector

        # User confirms
        mock_confirm.return_value = True

        result = uninstall_instruction("test-instruction", force=False)

        assert result == 1  # Error because unknown tool
        mock_tracker.remove_installation.assert_not_called()

    @patch("aiconfigkit.cli.uninstall.typer.confirm")
    @patch("aiconfigkit.cli.uninstall.get_detector")
    @patch("aiconfigkit.cli.uninstall.find_project_root")
    @patch("aiconfigkit.cli.uninstall.InstallationTracker")
    @patch("aiconfigkit.cli.uninstall.Path")
    def test_uninstall_exception_during_removal(
        self,
        mock_path_class: MagicMock,
        mock_tracker_class: MagicMock,
        mock_find_root: MagicMock,
        mock_get_detector: MagicMock,
        mock_confirm: MagicMock,
    ) -> None:
        """Test uninstalling when exception occurs during removal."""
        project_root = Path("/project")
        mock_find_root.return_value = project_root

        # Setup tracker
        mock_tracker = MagicMock()
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/instruction.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        mock_tracker.get_installed_instructions.return_value = [record]
        mock_tracker_class.return_value = mock_tracker

        # File unlink raises exception
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_file.unlink.side_effect = PermissionError("Permission denied")
        mock_path_class.return_value = mock_file

        # Setup AI tool detector
        mock_tool = MagicMock()
        mock_tool.tool_name = "Cursor"
        mock_detector = MagicMock()
        mock_detector.get_tool_by_type.return_value = mock_tool
        mock_get_detector.return_value = mock_detector

        # User confirms
        mock_confirm.return_value = True

        result = uninstall_instruction("test-instruction", force=False)

        assert result == 1  # Error due to exception
        mock_tracker.remove_installation.assert_not_called()  # Should not remove from tracker if file removal failed

    @patch("aiconfigkit.cli.uninstall.typer.confirm")
    @patch("aiconfigkit.cli.uninstall.get_detector")
    @patch("aiconfigkit.cli.uninstall.find_project_root")
    @patch("aiconfigkit.cli.uninstall.InstallationTracker")
    @patch("aiconfigkit.cli.uninstall.Path")
    def test_uninstall_multiple_records(
        self,
        mock_path_class: MagicMock,
        mock_tracker_class: MagicMock,
        mock_find_root: MagicMock,
        mock_get_detector: MagicMock,
        mock_confirm: MagicMock,
    ) -> None:
        """Test uninstalling instruction from multiple tools."""
        project_root = Path("/project")
        mock_find_root.return_value = project_root

        # Setup tracker with multiple records
        mock_tracker = MagicMock()
        records = [
            InstallationRecord(
                instruction_name="test-instruction",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",
                installed_path="/path/to/cursor.mdc",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
            ),
            InstallationRecord(
                instruction_name="test-instruction",
                ai_tool=AIToolType.CLAUDE,
                source_repo="https://github.com/test/repo",
                installed_path="/path/to/claude.md",
                installed_at=datetime.now(),
                scope=InstallationScope.PROJECT,
            ),
        ]
        mock_tracker.get_installed_instructions.return_value = records
        mock_tracker_class.return_value = mock_tracker

        # Setup files
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_path_class.return_value = mock_file

        # Setup AI tool detector
        mock_cursor_tool = MagicMock()
        mock_cursor_tool.tool_name = "Cursor"
        mock_claude_tool = MagicMock()
        mock_claude_tool.tool_name = "Claude"

        mock_detector = MagicMock()
        mock_detector.get_tool_by_type.side_effect = [mock_cursor_tool, mock_claude_tool]
        mock_get_detector.return_value = mock_detector

        # User confirms
        mock_confirm.return_value = True

        result = uninstall_instruction("test-instruction", force=False)

        assert result == 0  # Success
        assert mock_file.unlink.call_count == 2  # Two files removed
        assert mock_tracker.remove_installation.call_count == 2  # Two records removed

    @patch("aiconfigkit.cli.uninstall.find_project_root")
    @patch("aiconfigkit.cli.uninstall.InstallationTracker")
    def test_uninstall_with_tool_filter(self, mock_tracker_class: MagicMock, mock_find_root: MagicMock) -> None:
        """Test uninstalling from specific tool."""
        mock_find_root.return_value = Path("/project")

        # Setup tracker with records for different tools
        mock_tracker = MagicMock()
        cursor_record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/cursor.mdc",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        claude_record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CLAUDE,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/claude.md",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )
        mock_tracker.get_installed_instructions.return_value = [cursor_record, claude_record]
        mock_tracker_class.return_value = mock_tracker

        # Try to uninstall from copilot (not installed)
        result = uninstall_instruction("test-instruction", tool="copilot")

        assert result == 1  # Error - not installed for copilot
