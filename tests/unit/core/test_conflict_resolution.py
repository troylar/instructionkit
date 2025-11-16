"""Unit tests for conflict resolution."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aiconfigkit.core.conflict_resolution import (
    ConflictResolver,
    apply_resolution,
    batch_resolve_conflicts,
    check_conflicts,
    detect_conflict,
    prompt_conflict_resolution,
    prompt_conflict_resolution_template,
)
from aiconfigkit.core.models import (
    AIToolType,
    ConflictInfo,
    ConflictResolution,
    ConflictType,
    InstallationScope,
    TemplateInstallationRecord,
)


@pytest.fixture
def template_record(tmp_path: Path) -> TemplateInstallationRecord:
    """Create a template installation record for testing."""
    return TemplateInstallationRecord(
        id="test-id",
        template_name="test",
        source_repo="test-repo",
        source_version="1.0.0",
        namespace="test/repo",
        checksum="a" * 64,  # Valid 64-char SHA-256 hash
        installed_path=str(tmp_path / "test.md"),
        scope=InstallationScope.PROJECT,
        installed_at=datetime.now(),
        ide_type=AIToolType.CLAUDE,
    )


class TestConflictResolver:
    """Test ConflictResolver class."""

    def test_init_default_strategy(self) -> None:
        """Test initialization with default strategy."""
        resolver = ConflictResolver()
        assert resolver.default_strategy == ConflictResolution.SKIP

    def test_init_custom_strategy(self) -> None:
        """Test initialization with custom strategy."""
        resolver = ConflictResolver(default_strategy=ConflictResolution.OVERWRITE)
        assert resolver.default_strategy == ConflictResolution.OVERWRITE

    def test_resolve_skip(self) -> None:
        """Test resolving conflict with SKIP strategy."""
        resolver = ConflictResolver()
        target_path = Path("/test/instruction.md")

        result = resolver.resolve("test-instruction", target_path, ConflictResolution.SKIP)

        assert result.instruction_name == "test-instruction"
        assert result.existing_path == str(target_path)
        assert result.resolution == ConflictResolution.SKIP
        assert result.new_path is None

    def test_resolve_overwrite(self) -> None:
        """Test resolving conflict with OVERWRITE strategy."""
        resolver = ConflictResolver()
        target_path = Path("/test/instruction.md")

        result = resolver.resolve("test-instruction", target_path, ConflictResolution.OVERWRITE)

        assert result.instruction_name == "test-instruction"
        assert result.existing_path == str(target_path)
        assert result.resolution == ConflictResolution.OVERWRITE
        assert result.new_path == str(target_path)

    def test_resolve_rename(self, tmp_path: Path) -> None:
        """Test resolving conflict with RENAME strategy."""
        resolver = ConflictResolver()
        target_path = tmp_path / "instruction.md"

        result = resolver.resolve("test-instruction", target_path, ConflictResolution.RENAME)

        assert result.instruction_name == "test-instruction"
        assert result.existing_path == str(target_path)
        assert result.resolution == ConflictResolution.RENAME
        assert result.new_path is not None
        assert "instruction" in result.new_path

    def test_resolve_uses_default_strategy(self) -> None:
        """Test that resolve uses default strategy when none provided."""
        resolver = ConflictResolver(default_strategy=ConflictResolution.OVERWRITE)
        target_path = Path("/test/instruction.md")

        result = resolver.resolve("test-instruction", target_path)

        assert result.resolution == ConflictResolution.OVERWRITE

    def test_resolve_invalid_strategy(self) -> None:
        """Test that invalid strategy raises error."""
        resolver = ConflictResolver()
        target_path = Path("/test/instruction.md")

        with pytest.raises(ValueError, match="Unknown conflict resolution strategy"):
            resolver.resolve("test", target_path, "invalid_strategy")  # type: ignore

    def test_should_install_skip(self) -> None:
        """Test that SKIP returns False."""
        resolver = ConflictResolver()
        conflict_info = ConflictInfo(
            instruction_name="test",
            existing_path="/test/path",
            resolution=ConflictResolution.SKIP,
            new_path=None,
        )

        assert resolver.should_install(conflict_info) is False

    def test_should_install_overwrite(self) -> None:
        """Test that OVERWRITE returns True."""
        resolver = ConflictResolver()
        conflict_info = ConflictInfo(
            instruction_name="test",
            existing_path="/test/path",
            resolution=ConflictResolution.OVERWRITE,
            new_path="/test/path",
        )

        assert resolver.should_install(conflict_info) is True

    def test_should_install_rename(self) -> None:
        """Test that RENAME returns True."""
        resolver = ConflictResolver()
        conflict_info = ConflictInfo(
            instruction_name="test",
            existing_path="/test/path",
            resolution=ConflictResolution.RENAME,
            new_path="/test/path-1",
        )

        assert resolver.should_install(conflict_info) is True

    def test_get_install_path_no_conflict(self) -> None:
        """Test get_install_path with no conflict."""
        resolver = ConflictResolver()
        original_path = Path("/test/instruction.md")

        result = resolver.get_install_path(original_path)

        assert result == original_path

    def test_get_install_path_skip(self) -> None:
        """Test get_install_path with SKIP."""
        resolver = ConflictResolver()
        original_path = Path("/test/instruction.md")
        conflict_info = ConflictInfo(
            instruction_name="test",
            existing_path=str(original_path),
            resolution=ConflictResolution.SKIP,
            new_path=None,
        )

        result = resolver.get_install_path(original_path, conflict_info)

        assert result == original_path

    def test_get_install_path_overwrite(self) -> None:
        """Test get_install_path with OVERWRITE."""
        resolver = ConflictResolver()
        original_path = Path("/test/instruction.md")
        conflict_info = ConflictInfo(
            instruction_name="test",
            existing_path=str(original_path),
            resolution=ConflictResolution.OVERWRITE,
            new_path=str(original_path),
        )

        result = resolver.get_install_path(original_path, conflict_info)

        assert result == original_path

    def test_get_install_path_rename(self) -> None:
        """Test get_install_path with RENAME."""
        resolver = ConflictResolver()
        original_path = Path("/test/instruction.md")
        new_path = Path("/test/instruction-1.md")
        conflict_info = ConflictInfo(
            instruction_name="test",
            existing_path=str(original_path),
            resolution=ConflictResolution.RENAME,
            new_path=str(new_path),
        )

        result = resolver.get_install_path(original_path, conflict_info)

        assert result == new_path

    def test_get_install_path_rename_fallback(self) -> None:
        """Test get_install_path with RENAME but no new_path (edge case)."""
        resolver = ConflictResolver()
        original_path = Path("/test/instruction.md")
        conflict_info = ConflictInfo(
            instruction_name="test",
            existing_path=str(original_path),
            resolution=ConflictResolution.RENAME,
            new_path=None,  # Edge case: no new path provided
        )

        result = resolver.get_install_path(original_path, conflict_info)

        assert result == original_path  # Fallback to original

    def test_get_install_path_prompt_fallback(self) -> None:
        """Test get_install_path with PROMPT resolution (fallback case)."""
        resolver = ConflictResolver()
        original_path = Path("/test/instruction.md")
        conflict_info = ConflictInfo(
            instruction_name="test",
            existing_path=str(original_path),
            resolution=ConflictResolution.PROMPT,  # Not handled in if/elif chain
            new_path=None,
        )

        result = resolver.get_install_path(original_path, conflict_info)

        assert result == original_path  # Fallback to original path


class TestPromptConflictResolution:
    """Test interactive conflict resolution prompt."""

    @patch("builtins.input", return_value="1")
    def test_prompt_skip(self, mock_input: MagicMock) -> None:
        """Test prompting for SKIP choice."""
        result = prompt_conflict_resolution("test-instruction")
        assert result == ConflictResolution.SKIP

    @patch("builtins.input", return_value="2")
    def test_prompt_rename(self, mock_input: MagicMock) -> None:
        """Test prompting for RENAME choice."""
        result = prompt_conflict_resolution("test-instruction")
        assert result == ConflictResolution.RENAME

    @patch("builtins.input", return_value="3")
    def test_prompt_overwrite(self, mock_input: MagicMock) -> None:
        """Test prompting for OVERWRITE choice."""
        result = prompt_conflict_resolution("test-instruction")
        assert result == ConflictResolution.OVERWRITE

    @patch("builtins.input", side_effect=["invalid", "4", "1"])
    def test_prompt_invalid_then_valid(self, mock_input: MagicMock) -> None:
        """Test prompting with invalid input then valid."""
        result = prompt_conflict_resolution("test-instruction")
        assert result == ConflictResolution.SKIP
        assert mock_input.call_count == 3  # Called 3 times


class TestCheckConflicts:
    """Test check_conflicts function."""

    def test_no_conflicts(self, tmp_path: Path) -> None:
        """Test when no files exist."""
        paths = [tmp_path / "file1.md", tmp_path / "file2.md"]

        conflicts = check_conflicts(paths)

        assert conflicts == {}

    def test_some_conflicts(self, tmp_path: Path) -> None:
        """Test when some files exist."""
        file1 = tmp_path / "file1.md"
        file2 = tmp_path / "file2.md"
        file1.write_text("content")

        paths = [file1, file2]
        conflicts = check_conflicts(paths)

        assert len(conflicts) == 1
        assert "file1" in conflicts
        assert conflicts["file1"] == file1

    def test_all_conflicts(self, tmp_path: Path) -> None:
        """Test when all files exist."""
        file1 = tmp_path / "file1.md"
        file2 = tmp_path / "file2.md"
        file1.write_text("content1")
        file2.write_text("content2")

        paths = [file1, file2]
        conflicts = check_conflicts(paths)

        assert len(conflicts) == 2
        assert "file1" in conflicts
        assert "file2" in conflicts


class TestBatchResolveConflicts:
    """Test batch_resolve_conflicts function."""

    def test_batch_resolve_skip(self) -> None:
        """Test batch resolving with SKIP."""
        conflicts = {
            "inst1": Path("/test/inst1.md"),
            "inst2": Path("/test/inst2.md"),
        }

        resolutions = batch_resolve_conflicts(conflicts, ConflictResolution.SKIP)

        assert len(resolutions) == 2
        assert resolutions["inst1"].resolution == ConflictResolution.SKIP
        assert resolutions["inst2"].resolution == ConflictResolution.SKIP

    def test_batch_resolve_overwrite(self) -> None:
        """Test batch resolving with OVERWRITE."""
        conflicts = {
            "inst1": Path("/test/inst1.md"),
            "inst2": Path("/test/inst2.md"),
        }

        resolutions = batch_resolve_conflicts(conflicts, ConflictResolution.OVERWRITE)

        assert len(resolutions) == 2
        assert resolutions["inst1"].resolution == ConflictResolution.OVERWRITE
        assert resolutions["inst2"].resolution == ConflictResolution.OVERWRITE

    def test_batch_resolve_rename(self, tmp_path: Path) -> None:
        """Test batch resolving with RENAME."""
        conflicts = {
            "inst1": tmp_path / "inst1.md",
            "inst2": tmp_path / "inst2.md",
        }

        resolutions = batch_resolve_conflicts(conflicts, ConflictResolution.RENAME)

        assert len(resolutions) == 2
        assert resolutions["inst1"].resolution == ConflictResolution.RENAME
        assert resolutions["inst2"].resolution == ConflictResolution.RENAME
        assert resolutions["inst1"].new_path is not None
        assert resolutions["inst2"].new_path is not None


class TestDetectConflict:
    """Test detect_conflict function for template sync."""

    def test_no_conflict_file_doesnt_exist(self, tmp_path: Path) -> None:
        """Test when installed file doesn't exist."""
        installed_file = tmp_path / "nonexistent.md"
        new_content = "new content"
        record = TemplateInstallationRecord(
            id="test-id",
            template_name="test",
            source_repo="test-repo",
            source_version="1.0.0",
            namespace="test/repo",
            checksum="a" * 64,  # Valid 64-char SHA-256 hash
            installed_path=str(installed_file),
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )

        result = detect_conflict(installed_file, new_content, record)

        assert result == ConflictType.NONE

    def test_no_conflict_unchanged_file(self, tmp_path: Path) -> None:
        """Test when file unchanged and template unchanged."""
        from aiconfigkit.core.checksum import sha256_string

        content = "original content"
        installed_file = tmp_path / "test.md"
        installed_file.write_text(content)

        checksum = sha256_string(content)
        record = TemplateInstallationRecord(
            id="test-id",
            template_name="test",
            source_repo="test-repo",
            source_version="1.0.0",
            namespace="test/repo",
            checksum=checksum,
            installed_path=str(installed_file),
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )

        result = detect_conflict(installed_file, content, record)

        assert result == ConflictType.NONE

    def test_no_conflict_only_remote_changed(self, tmp_path: Path) -> None:
        """Test when only remote template changed."""
        from aiconfigkit.core.checksum import sha256_string

        original_content = "original content"
        new_content = "new remote content"

        installed_file = tmp_path / "test.md"
        installed_file.write_text(original_content)

        checksum = sha256_string(original_content)
        record = TemplateInstallationRecord(
            id="test-id",
            template_name="test",
            source_repo="test-repo",
            source_version="1.0.0",
            namespace="test/repo",
            checksum=checksum,
            installed_path=str(installed_file),
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )

        result = detect_conflict(installed_file, new_content, record)

        assert result == ConflictType.NONE  # Safe to update

    def test_local_modified(self, tmp_path: Path) -> None:
        """Test when only local file was modified."""
        from aiconfigkit.core.checksum import sha256_string

        original_content = "original content"
        local_modified_content = "local changes"

        installed_file = tmp_path / "test.md"
        installed_file.write_text(local_modified_content)

        checksum = sha256_string(original_content)
        record = TemplateInstallationRecord(
            id="test-id",
            template_name="test",
            source_repo="test-repo",
            source_version="1.0.0",
            namespace="test/repo",
            checksum=checksum,
            installed_path=str(installed_file),
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )

        result = detect_conflict(installed_file, original_content, record)

        assert result == ConflictType.LOCAL_MODIFIED

    def test_both_modified(self, tmp_path: Path) -> None:
        """Test when both local and remote were modified."""
        from aiconfigkit.core.checksum import sha256_string

        original_content = "original content"
        local_modified_content = "local changes"
        remote_modified_content = "remote changes"

        installed_file = tmp_path / "test.md"
        installed_file.write_text(local_modified_content)

        checksum = sha256_string(original_content)
        record = TemplateInstallationRecord(
            id="test-id",
            template_name="test",
            source_repo="test-repo",
            source_version="1.0.0",
            namespace="test/repo",
            checksum=checksum,
            installed_path=str(installed_file),
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )

        result = detect_conflict(installed_file, remote_modified_content, record)

        assert result == ConflictType.BOTH_MODIFIED


class TestPromptConflictResolutionTemplate:
    """Test prompt_conflict_resolution_template function."""

    @patch("rich.prompt.Prompt.ask", return_value="k")
    def test_prompt_keep_local(self, mock_ask: MagicMock) -> None:
        """Test prompting for keep local (skip)."""
        result = prompt_conflict_resolution_template("test", ConflictType.LOCAL_MODIFIED)
        assert result == ConflictResolution.SKIP

    @patch("rich.prompt.Prompt.ask", return_value="K")
    def test_prompt_keep_local_uppercase(self, mock_ask: MagicMock) -> None:
        """Test prompting for keep local with uppercase."""
        result = prompt_conflict_resolution_template("test", ConflictType.LOCAL_MODIFIED)
        assert result == ConflictResolution.SKIP

    @patch("rich.prompt.Prompt.ask", return_value="o")
    def test_prompt_overwrite(self, mock_ask: MagicMock) -> None:
        """Test prompting for overwrite."""
        result = prompt_conflict_resolution_template("test", ConflictType.BOTH_MODIFIED)
        assert result == ConflictResolution.OVERWRITE

    @patch("rich.prompt.Prompt.ask", return_value="O")
    def test_prompt_overwrite_uppercase(self, mock_ask: MagicMock) -> None:
        """Test prompting for overwrite with uppercase."""
        result = prompt_conflict_resolution_template("test", ConflictType.BOTH_MODIFIED)
        assert result == ConflictResolution.OVERWRITE

    @patch("rich.prompt.Prompt.ask", return_value="r")
    def test_prompt_rename(self, mock_ask: MagicMock) -> None:
        """Test prompting for rename."""
        result = prompt_conflict_resolution_template("test", ConflictType.LOCAL_MODIFIED)
        assert result == ConflictResolution.RENAME

    @patch("rich.prompt.Prompt.ask", return_value="R")
    def test_prompt_rename_uppercase(self, mock_ask: MagicMock) -> None:
        """Test prompting for rename with uppercase."""
        result = prompt_conflict_resolution_template("test", ConflictType.LOCAL_MODIFIED)
        assert result == ConflictResolution.RENAME


class TestApplyResolution:
    """Test apply_resolution function."""

    def test_apply_skip(self, tmp_path: Path) -> None:
        """Test applying SKIP resolution."""
        template_path = tmp_path / "test.md"
        template_path.write_text("original")
        new_content = "new content"

        result_path = apply_resolution(template_path, new_content, ConflictResolution.SKIP)

        assert result_path == template_path
        assert template_path.read_text() == "original"  # Unchanged

    def test_apply_overwrite_no_backup_needed(self, tmp_path: Path) -> None:
        """Test applying OVERWRITE when file doesn't exist."""
        template_path = tmp_path / "test.md"
        new_content = "new content"

        result_path = apply_resolution(template_path, new_content, ConflictResolution.OVERWRITE)

        assert result_path == template_path
        assert template_path.read_text() == "new content"

    @patch("aiconfigkit.utils.backup.create_backup")
    def test_apply_overwrite_with_backup(self, mock_backup: MagicMock, tmp_path: Path) -> None:
        """Test applying OVERWRITE creates backup."""
        template_path = tmp_path / "test.md"
        template_path.write_text("original")
        new_content = "new content"

        mock_backup.return_value = tmp_path / "backup" / "test.md"

        result_path = apply_resolution(template_path, new_content, ConflictResolution.OVERWRITE)

        assert result_path == template_path
        assert template_path.read_text() == "new content"
        mock_backup.assert_called_once_with(template_path)

    def test_apply_rename(self, tmp_path: Path) -> None:
        """Test applying RENAME resolution."""
        template_path = tmp_path / "test.md"
        template_path.write_text("original")
        new_content = "new content"

        result_path = apply_resolution(template_path, new_content, ConflictResolution.RENAME)

        assert result_path == template_path
        assert template_path.read_text() == "new content"
        # Original should be renamed
        renamed_file = tmp_path / "test-1.md"
        assert renamed_file.exists()
        assert renamed_file.read_text() == "original"

    def test_apply_rename_no_existing_file(self, tmp_path: Path) -> None:
        """Test applying RENAME when file doesn't exist."""
        template_path = tmp_path / "test.md"
        new_content = "new content"

        result_path = apply_resolution(template_path, new_content, ConflictResolution.RENAME)

        assert result_path == template_path
        assert template_path.read_text() == "new content"

    def test_apply_invalid_resolution(self, tmp_path: Path) -> None:
        """Test applying invalid resolution raises error."""
        template_path = tmp_path / "test.md"
        new_content = "new content"

        with pytest.raises(ValueError, match="Unknown conflict resolution strategy"):
            apply_resolution(template_path, new_content, "invalid")  # type: ignore
