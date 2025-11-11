"""Tests for install_new CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aiconfigkit.cli.install_new import (
    _check_for_upgrades,
    _detect_installed_collisions,
    _prompt_for_upgrade,
    install_from_library_direct_multi_tool,
    install_from_library_tui,
)
from aiconfigkit.core.models import AIToolType, InstallationRecord, LibraryInstruction, RefType


@pytest.fixture
def mock_library_instruction():
    """Create a mock LibraryInstruction."""
    return LibraryInstruction(
        id="test-repo/python-style",
        name="python-style",
        description="Python style guidelines",
        file_path="/fake/path/python-style.md",
        checksum="abc123",
        tags=["python", "style"],
        repo_name="test-repo",
        repo_namespace="test",
        repo_url="https://github.com/test/test-repo.git",
        version="1.0.0",
        author="Test Author",
    )


@pytest.fixture
def mock_library_instructions(mock_library_instruction):
    """Create a list of mock LibraryInstructions."""
    inst1 = mock_library_instruction
    inst2 = LibraryInstruction(
        id="test-repo/testing-guide",
        name="testing-guide",
        description="Testing best practices",
        file_path="/fake/path/testing-guide.md",
        checksum="def456",
        tags=["testing"],
        repo_name="test-repo",
        repo_namespace="test",
        repo_url="https://github.com/test/test-repo.git",
        version="1.0.0",
        author="Test Author",
    )
    return [inst1, inst2]


@pytest.fixture
def mock_project_with_git(temp_dir):
    """Create a mock project with .git directory."""
    project = temp_dir / "test-project"
    project.mkdir()
    (project / ".git").mkdir()
    return project


class TestInstallFromLibraryTUI:
    """Tests for install_from_library_tui function."""

    @patch("aiconfigkit.cli.install_new.install_from_library_direct_multi_tool")
    @patch("aiconfigkit.cli.install_new.show_installer_tui")
    @patch("aiconfigkit.cli.install_new.LibraryManager")
    def test_install_from_tui_no_duplicate_confirmation(
        self,
        mock_library_manager,
        mock_tui,
        mock_install_direct,
        mock_library_instructions,
    ):
        """Test that install_from_library_tui doesn't show duplicate confirmation.

        This is the main test for issue #1. It verifies that when the TUI returns
        selected instructions, the function doesn't show its own confirmation dialog
        but instead delegates to install_from_library_direct_multi_tool which
        handles the single confirmation.
        """
        # Setup mocks
        mock_library_manager.return_value.list_instructions.return_value = mock_library_instructions

        # Mock TUI to return selected instructions and tools
        mock_tui.return_value = {
            "instructions": mock_library_instructions,
            "tools": ["copilot", "cursor"],
        }

        # Mock the direct install to return success
        mock_install_direct.return_value = 0

        # Call the function
        result = install_from_library_tui(tool=None)

        # Verify TUI was shown
        mock_tui.assert_called_once()

        # Verify that install_from_library_direct_multi_tool was called
        # with the selected instructions and tools
        mock_install_direct.assert_called_once_with(
            instruction_ids=[inst.id for inst in mock_library_instructions],
            tools=["copilot", "cursor"],
            conflict_strategy="skip",
        )

        # Verify success
        assert result == 0

    @patch("aiconfigkit.cli.install_new.show_installer_tui")
    @patch("aiconfigkit.cli.install_new.LibraryManager")
    def test_install_from_tui_cancelled(self, mock_library_manager, mock_tui, mock_library_instructions):
        """Test that cancelling from TUI returns gracefully."""
        mock_library_manager.return_value.list_instructions.return_value = mock_library_instructions

        # Mock TUI to return None (cancelled)
        mock_tui.return_value = None

        result = install_from_library_tui(tool=None)

        # Should return 0 (success, just cancelled)
        assert result == 0

    @patch("aiconfigkit.cli.install_new.LibraryManager")
    def test_install_from_tui_empty_library(self, mock_library_manager):
        """Test that empty library shows info message."""
        mock_library_manager.return_value.list_instructions.return_value = []

        result = install_from_library_tui(tool=None)

        # Should return 1 (error - no instructions)
        assert result == 1

    @patch("aiconfigkit.cli.install_new.install_from_library_direct_multi_tool")
    @patch("aiconfigkit.cli.install_new.show_installer_tui")
    @patch("aiconfigkit.cli.install_new.LibraryManager")
    def test_install_from_tui_delegates_to_direct_install(
        self, mock_library_manager, mock_tui, mock_install_direct, mock_library_instructions
    ):
        """Test that TUI delegates to direct install function."""
        mock_library_manager.return_value.list_instructions.return_value = mock_library_instructions

        # Mock TUI to return selections
        mock_tui.return_value = {
            "instructions": mock_library_instructions,
            "tools": ["copilot"],
        }

        # Mock direct install handles project root checking
        mock_install_direct.return_value = 1

        result = install_from_library_tui(tool=None)

        # Should delegate to direct install
        mock_install_direct.assert_called_once()
        assert result == 1


class TestInstallFromLibraryDirectMultiTool:
    """Tests for install_from_library_direct_multi_tool function."""

    @patch("aiconfigkit.cli.install_new._show_installation_preview")
    @patch("aiconfigkit.cli.install_new._perform_installation")
    @patch("aiconfigkit.cli.install_new._get_ai_tools_from_names")
    @patch("aiconfigkit.cli.install_new._resolve_name_conflicts")
    @patch("aiconfigkit.cli.install_new._load_instructions_from_library")
    @patch("aiconfigkit.cli.install_new._get_project_root_for_installation")
    @patch("aiconfigkit.cli.install_new.get_detector")
    @patch("aiconfigkit.cli.install_new.LibraryManager")
    def test_confirmation_prompt_called_once(
        self,
        mock_library_manager,
        mock_get_detector,
        mock_get_root,
        mock_load_instructions,
        mock_resolve_conflicts,
        mock_get_tools,
        mock_perform_install,
        mock_show_preview,
        mock_library_instructions,
        mock_project_with_git,
    ):
        """Test that confirmation prompt is called exactly once.

        This test verifies that _show_installation_preview (which contains
        the confirmation prompt) is called exactly once, not twice.
        """
        # Setup mocks
        mock_get_root.return_value = mock_project_with_git
        mock_load_instructions.return_value = mock_library_instructions
        mock_resolve_conflicts.return_value = {inst.id: inst.name for inst in mock_library_instructions}

        # Mock AI tools
        mock_tool = MagicMock()
        mock_tool.tool_name = "copilot"
        mock_get_tools.return_value = [mock_tool]

        # Mock preview to return True (confirmed)
        mock_show_preview.return_value = True

        # Mock installation
        mock_perform_install.return_value = (2, 0)  # 2 installed, 0 skipped

        # Call the function
        result = install_from_library_direct_multi_tool(
            instruction_ids=[inst.id for inst in mock_library_instructions],
            tools=["copilot"],
            conflict_strategy="skip",
        )

        # Verify preview/confirmation was called EXACTLY ONCE
        assert mock_show_preview.call_count == 1

        # Verify success
        assert result == 0

    @patch("aiconfigkit.cli.install_new._show_installation_preview")
    @patch("aiconfigkit.cli.install_new._get_ai_tools_from_names")
    @patch("aiconfigkit.cli.install_new._resolve_name_conflicts")
    @patch("aiconfigkit.cli.install_new._load_instructions_from_library")
    @patch("aiconfigkit.cli.install_new._get_project_root_for_installation")
    @patch("aiconfigkit.cli.install_new.get_detector")
    @patch("aiconfigkit.cli.install_new.LibraryManager")
    def test_confirmation_denied_cancels_installation(
        self,
        mock_library_manager,
        mock_get_detector,
        mock_get_root,
        mock_load_instructions,
        mock_resolve_conflicts,
        mock_get_tools,
        mock_show_preview,
        mock_library_instructions,
        mock_project_with_git,
    ):
        """Test that denying confirmation cancels installation."""
        # Setup mocks
        mock_get_root.return_value = mock_project_with_git
        mock_load_instructions.return_value = mock_library_instructions
        mock_resolve_conflicts.return_value = {inst.id: inst.name for inst in mock_library_instructions}

        mock_tool = MagicMock()
        mock_tool.tool_name = "copilot"
        mock_get_tools.return_value = [mock_tool]

        # Mock preview to return False (not confirmed)
        mock_show_preview.return_value = False

        # Call the function
        result = install_from_library_direct_multi_tool(
            instruction_ids=[inst.id for inst in mock_library_instructions],
            tools=["copilot"],
            conflict_strategy="skip",
        )

        # Verify preview was called
        assert mock_show_preview.call_count == 1

        # Should return 0 (cancelled, not error)
        assert result == 0

    @patch("aiconfigkit.cli.install_new._get_project_root_for_installation")
    @patch("aiconfigkit.cli.install_new.LibraryManager")
    def test_invalid_conflict_strategy(self, mock_library_manager, mock_get_root):
        """Test that invalid conflict strategy returns error."""
        result = install_from_library_direct_multi_tool(
            instruction_ids=["test-id"],
            tools=["copilot"],
            conflict_strategy="invalid",
        )

        # Should return 1 (error)
        assert result == 1

    @patch("aiconfigkit.cli.install_new._load_instructions_from_library")
    @patch("aiconfigkit.cli.install_new._get_project_root_for_installation")
    @patch("aiconfigkit.cli.install_new.LibraryManager")
    def test_instruction_not_found(self, mock_library_manager, mock_get_root, mock_load_instructions):
        """Test that missing instruction returns error."""
        mock_get_root.return_value = Path("/fake/project")
        mock_load_instructions.return_value = None  # Not found

        result = install_from_library_direct_multi_tool(
            instruction_ids=["nonexistent"],
            tools=["copilot"],
            conflict_strategy="skip",
        )

        # Should return 1 (error)
        assert result == 1


class TestInstallationFlow:
    """Integration tests for the full installation flow."""

    @patch("rich.prompt.Confirm.ask")
    @patch("aiconfigkit.cli.install_new.show_installer_tui")
    @patch("aiconfigkit.cli.install_new.find_project_root")
    @patch("aiconfigkit.cli.install_new.get_detector")
    @patch("aiconfigkit.cli.install_new.LibraryManager")
    @patch("aiconfigkit.cli.install_new.InstallationTracker")
    def test_full_flow_single_confirmation(
        self,
        mock_tracker,
        mock_library_manager,
        mock_get_detector,
        mock_find_root,
        mock_tui,
        mock_confirm,
        mock_library_instructions,
        mock_project_with_git,
        temp_dir,
    ):
        """Test the full installation flow to ensure confirmation is asked only once."""
        # Setup project
        mock_find_root.return_value = mock_project_with_git

        # Setup library with instructions
        mock_library = MagicMock()
        mock_library.list_instructions.return_value = mock_library_instructions

        def get_instruction(inst_id):
            for inst in mock_library_instructions:
                if inst.id == inst_id:
                    return inst
            return None

        mock_library.get_instruction.side_effect = get_instruction
        mock_library_manager.return_value = mock_library

        # Setup AI tool
        mock_tool = MagicMock()
        mock_tool.tool_name = "copilot"
        mock_tool.tool_type = AIToolType.COPILOT
        mock_tool.get_project_instructions_directory.return_value = mock_project_with_git / ".github" / "instructions"
        mock_tool.get_instruction_file_extension.return_value = ".md"
        mock_tool.get_instruction_path.return_value = (
            mock_project_with_git / ".github" / "instructions" / "python-style.md"
        )

        mock_detector = MagicMock()
        mock_detector.get_tool_by_name.return_value = mock_tool
        mock_get_detector.return_value = mock_detector

        # Setup TUI result
        mock_tui.return_value = {
            "instructions": mock_library_instructions,
            "tools": ["copilot"],
        }

        # Mock confirmation - should be called ONCE
        mock_confirm.return_value = True

        # Create instruction files in temp dir
        for inst in mock_library_instructions:
            fake_path = temp_dir / f"{inst.name}.md"
            fake_path.write_text(f"# {inst.name}")
            inst.file_path = str(fake_path)

        # Setup tracker
        mock_tracker_instance = MagicMock()
        mock_tracker.return_value = mock_tracker_instance

        # Call install_from_library_tui
        result = install_from_library_tui(tool=None)

        # Verify Confirm.ask was called exactly ONCE
        # This is the key assertion for issue #1 - before the fix, this would be 2
        assert mock_confirm.call_count == 1, f"Expected confirmation prompt once, but got {mock_confirm.call_count}"

        # Verify the confirmation message
        call_args = mock_confirm.call_args
        assert "Proceed with installation?" in str(call_args)

        # Verify success
        assert result == 0


class TestUpgradeDetection:
    """Tests for upgrade detection functionality."""

    def test_check_for_upgrades_detects_version_change(self, mock_library_instruction, mock_project_with_git):
        """Test that upgrade detection finds when version changes."""
        # Create instruction with new version
        new_instruction = LibraryInstruction(
            id="test-repo@v2.0.0/python-style",
            name="python-style",
            description="Python style guidelines",
            file_path="/fake/path/python-style.md",
            checksum="xyz789",
            tags=["python"],
            repo_name="test-repo",
            repo_namespace="test-repo@v2.0.0",
            repo_url="https://github.com/test/test-repo.git",
            version="2.0.0",
            author="Test Author",
        )

        # Mock existing installation
        existing_record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.COPILOT,
            source_repo="https://github.com/test/test-repo.git",
            installed_path=".github/instructions/python-style.md",
            installed_at=None,
            checksum="abc123",
            bundle_name=None,
            scope=None,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )

        # Mock AI tool
        mock_tool = MagicMock()
        mock_tool.tool_type = AIToolType.COPILOT

        with patch("aiconfigkit.cli.install_new.InstallationTracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.get_installation.return_value = existing_record
            mock_tracker_class.return_value = mock_tracker

            upgrades = _check_for_upgrades(
                instructions=[new_instruction],
                ai_tools=[mock_tool],
                install_names={new_instruction.id: "python-style"},
                project_root=mock_project_with_git,
            )

            # Should detect upgrade
            assert len(upgrades) == 1
            key = f"{new_instruction.id}_{AIToolType.COPILOT.value}"
            assert key in upgrades
            assert upgrades[key][0] == existing_record
            assert upgrades[key][1] == new_instruction

    def test_check_for_upgrades_no_existing_installation(self, mock_library_instruction, mock_project_with_git):
        """Test that no upgrade detected when instruction not installed."""
        mock_tool = MagicMock()
        mock_tool.tool_type = AIToolType.COPILOT

        with patch("aiconfigkit.cli.install_new.InstallationTracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.get_installation.return_value = None  # Not installed
            mock_tracker_class.return_value = mock_tracker

            upgrades = _check_for_upgrades(
                instructions=[mock_library_instruction],
                ai_tools=[mock_tool],
                install_names={mock_library_instruction.id: "python-style"},
                project_root=mock_project_with_git,
            )

            # No upgrades
            assert len(upgrades) == 0

    def test_check_for_upgrades_same_version(self, mock_library_instruction, mock_project_with_git):
        """Test that no upgrade detected when version is same."""
        existing_record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.COPILOT,
            source_repo="https://github.com/test/test-repo.git",
            installed_path=".github/instructions/python-style.md",
            installed_at=None,
            checksum="abc123",
            bundle_name=None,
            scope=None,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )

        mock_tool = MagicMock()
        mock_tool.tool_type = AIToolType.COPILOT

        # Create instruction with same version in namespace
        same_version_inst = LibraryInstruction(
            id="test-repo@v1.0.0/python-style",
            name="python-style",
            description="Python style guidelines",
            file_path="/fake/path/python-style.md",
            checksum="abc123",
            tags=["python"],
            repo_name="test-repo",
            repo_namespace="test-repo@v1.0.0",
            repo_url="https://github.com/test/test-repo.git",
            version="1.0.0",
            author="Test Author",
        )

        with patch("aiconfigkit.cli.install_new.InstallationTracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.get_installation.return_value = existing_record
            mock_tracker_class.return_value = mock_tracker

            upgrades = _check_for_upgrades(
                instructions=[same_version_inst],
                ai_tools=[mock_tool],
                install_names={same_version_inst.id: "python-style"},
                project_root=mock_project_with_git,
            )

            # No upgrades (same version)
            assert len(upgrades) == 0

    @patch("rich.prompt.Confirm.ask")
    def test_prompt_for_upgrade_user_confirms(self, mock_confirm):
        """Test upgrade prompt when user confirms."""
        mock_confirm.return_value = True

        existing = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.COPILOT,
            source_repo="https://github.com/test/test-repo.git",
            installed_path=".github/instructions/python-style.md",
            installed_at=None,
            checksum="abc123",
            bundle_name=None,
            scope=None,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )

        new_inst = LibraryInstruction(
            id="test-repo@v2.0.0/python-style",
            name="python-style",
            description="Python style guidelines",
            file_path="/fake/path/python-style.md",
            checksum="xyz789",
            tags=["python"],
            repo_name="test-repo",
            repo_namespace="test-repo@v2.0.0",
            repo_url="https://github.com/test/test-repo.git",
            version="2.0.0",
            author="Test Author",
        )

        result = _prompt_for_upgrade(existing, new_inst)

        assert result is True
        mock_confirm.assert_called_once()

    @patch("rich.prompt.Confirm.ask")
    def test_prompt_for_upgrade_user_declines(self, mock_confirm):
        """Test upgrade prompt when user declines."""
        mock_confirm.return_value = False

        existing = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.COPILOT,
            source_repo="https://github.com/test/test-repo.git",
            installed_path=".github/instructions/python-style.md",
            installed_at=None,
            checksum="abc123",
            bundle_name=None,
            scope=None,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )

        new_inst = LibraryInstruction(
            id="test-repo@v2.0.0/python-style",
            name="python-style",
            description="Python style guidelines",
            file_path="/fake/path/python-style.md",
            checksum="xyz789",
            tags=["python"],
            repo_name="test-repo",
            repo_namespace="test-repo@v2.0.0",
            repo_url="https://github.com/test/test-repo.git",
            version="2.0.0",
            author="Test Author",
        )

        result = _prompt_for_upgrade(existing, new_inst)

        assert result is False


class TestCollisionDetection:
    """Tests for name collision detection."""

    def test_detect_collision_different_repo(self, mock_library_instruction, mock_project_with_git):
        """Test that collision detected when same name from different repo."""
        # Existing installation from different repo
        existing_record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.COPILOT,
            source_repo="https://github.com/other/other-repo.git",
            installed_path=".github/instructions/python-style.md",
            installed_at=None,
            checksum="different123",
            bundle_name=None,
            scope=None,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )

        mock_tool = MagicMock()
        mock_tool.tool_type = AIToolType.COPILOT

        with patch("aiconfigkit.cli.install_new.InstallationTracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.find_instructions_by_name.return_value = [existing_record]
            mock_tracker_class.return_value = mock_tracker

            collisions = _detect_installed_collisions(
                instructions=[mock_library_instruction],
                ai_tools=[mock_tool],
                install_names={mock_library_instruction.id: "python-style"},
                project_root=mock_project_with_git,
            )

            # Should detect collision
            assert len(collisions) == 1
            assert mock_library_instruction.id in collisions
            assert collisions[mock_library_instruction.id] == [existing_record]

    def test_no_collision_same_repo(self, mock_library_instruction, mock_project_with_git):
        """Test that no collision when same name from same repo."""
        # Existing installation from same repo
        existing_record = InstallationRecord(
            instruction_name="python-style",
            ai_tool=AIToolType.COPILOT,
            source_repo="https://github.com/test/test-repo.git",  # Same repo
            installed_path=".github/instructions/python-style.md",
            installed_at=None,
            checksum="abc123",
            bundle_name=None,
            scope=None,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )

        mock_tool = MagicMock()
        mock_tool.tool_type = AIToolType.COPILOT

        with patch("aiconfigkit.cli.install_new.InstallationTracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.find_instructions_by_name.return_value = [existing_record]
            mock_tracker_class.return_value = mock_tracker

            collisions = _detect_installed_collisions(
                instructions=[mock_library_instruction],
                ai_tools=[mock_tool],
                install_names={mock_library_instruction.id: "python-style"},
                project_root=mock_project_with_git,
            )

            # No collision (same repo)
            assert len(collisions) == 0

    def test_no_collision_when_not_installed(self, mock_library_instruction, mock_project_with_git):
        """Test that no collision when instruction not installed."""
        mock_tool = MagicMock()
        mock_tool.tool_type = AIToolType.COPILOT

        with patch("aiconfigkit.cli.install_new.InstallationTracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.find_instructions_by_name.return_value = []  # Not installed
            mock_tracker_class.return_value = mock_tracker

            collisions = _detect_installed_collisions(
                instructions=[mock_library_instruction],
                ai_tools=[mock_tool],
                install_names={mock_library_instruction.id: "python-style"},
                project_root=mock_project_with_git,
            )

            # No collisions
            assert len(collisions) == 0
