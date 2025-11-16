"""Tests for conflict resolution module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from aiconfigkit.core.conflict_resolution import (
    ConflictResolver,
    batch_resolve_conflicts,
    check_conflicts,
    prompt_conflict_resolution,
)
from aiconfigkit.core.models import ConflictInfo, ConflictResolution


def test_conflict_resolver_default_strategy() -> None:
    """Test conflict resolver with default strategy."""
    resolver = ConflictResolver()
    assert resolver.default_strategy == ConflictResolution.SKIP


def test_conflict_resolver_custom_strategy() -> None:
    """Test conflict resolver with custom default strategy."""
    resolver = ConflictResolver(default_strategy=ConflictResolution.OVERWRITE)
    assert resolver.default_strategy == ConflictResolution.OVERWRITE


def test_resolve_skip_strategy() -> None:
    """Test resolving conflict with SKIP strategy."""
    resolver = ConflictResolver(default_strategy=ConflictResolution.SKIP)
    target_path = Path("/tmp/instruction.md")

    result = resolver.resolve("test-instruction", target_path)

    assert isinstance(result, ConflictInfo)
    assert result.instruction_name == "test-instruction"
    assert result.existing_path == str(target_path)
    assert result.resolution == ConflictResolution.SKIP
    assert result.new_path is None


def test_resolve_overwrite_strategy() -> None:
    """Test resolving conflict with OVERWRITE strategy."""
    resolver = ConflictResolver(default_strategy=ConflictResolution.OVERWRITE)
    target_path = Path("/tmp/instruction.md")

    result = resolver.resolve("test-instruction", target_path)

    assert isinstance(result, ConflictInfo)
    assert result.instruction_name == "test-instruction"
    assert result.existing_path == str(target_path)
    assert result.resolution == ConflictResolution.OVERWRITE
    assert result.new_path == str(target_path)


def test_resolve_rename_strategy(tmp_path: Path) -> None:
    """Test resolving conflict with RENAME strategy."""
    resolver = ConflictResolver(default_strategy=ConflictResolution.RENAME)
    target_path = tmp_path / "instruction.md"
    target_path.touch()  # Create the file so rename logic can work

    result = resolver.resolve("test-instruction", target_path)

    assert isinstance(result, ConflictInfo)
    assert result.instruction_name == "test-instruction"
    assert result.existing_path == str(target_path)
    assert result.resolution == ConflictResolution.RENAME
    assert result.new_path is not None
    assert result.new_path != str(target_path)


def test_resolve_explicit_strategy() -> None:
    """Test resolving conflict with explicit strategy override."""
    resolver = ConflictResolver(default_strategy=ConflictResolution.SKIP)
    target_path = Path("/tmp/instruction.md")

    # Override with explicit strategy
    result = resolver.resolve("test-instruction", target_path, strategy=ConflictResolution.OVERWRITE)

    assert result.resolution == ConflictResolution.OVERWRITE


def test_resolve_invalid_strategy() -> None:
    """Test resolving conflict with invalid strategy raises error."""
    resolver = ConflictResolver()
    target_path = Path("/tmp/instruction.md")

    # Create a mock invalid strategy (this is a bit hacky but tests error handling)
    with pytest.raises((ValueError, AttributeError)):
        # Using an invalid value that's not a ConflictResolution enum
        resolver.resolve("test-instruction", target_path, strategy="invalid")  # type: ignore


def test_should_install_skip() -> None:
    """Test should_install returns False for SKIP resolution."""
    resolver = ConflictResolver()
    conflict_info = ConflictInfo(
        instruction_name="test",
        existing_path="/tmp/test.md",
        resolution=ConflictResolution.SKIP,
        new_path=None,
    )

    assert resolver.should_install(conflict_info) is False


def test_should_install_overwrite() -> None:
    """Test should_install returns True for OVERWRITE resolution."""
    resolver = ConflictResolver()
    conflict_info = ConflictInfo(
        instruction_name="test",
        existing_path="/tmp/test.md",
        resolution=ConflictResolution.OVERWRITE,
        new_path="/tmp/test.md",
    )

    assert resolver.should_install(conflict_info) is True


def test_should_install_rename() -> None:
    """Test should_install returns True for RENAME resolution."""
    resolver = ConflictResolver()
    conflict_info = ConflictInfo(
        instruction_name="test",
        existing_path="/tmp/test.md",
        resolution=ConflictResolution.RENAME,
        new_path="/tmp/test-1.md",
    )

    assert resolver.should_install(conflict_info) is True


def test_get_install_path_no_conflict() -> None:
    """Test get_install_path with no conflict."""
    resolver = ConflictResolver()
    original_path = Path("/tmp/instruction.md")

    result = resolver.get_install_path(original_path, conflict_info=None)

    assert result == original_path


def test_get_install_path_skip() -> None:
    """Test get_install_path with SKIP resolution."""
    resolver = ConflictResolver()
    original_path = Path("/tmp/instruction.md")
    conflict_info = ConflictInfo(
        instruction_name="test",
        existing_path="/tmp/instruction.md",
        resolution=ConflictResolution.SKIP,
        new_path=None,
    )

    result = resolver.get_install_path(original_path, conflict_info)

    assert result == original_path


def test_get_install_path_overwrite() -> None:
    """Test get_install_path with OVERWRITE resolution."""
    resolver = ConflictResolver()
    original_path = Path("/tmp/instruction.md")
    conflict_info = ConflictInfo(
        instruction_name="test",
        existing_path="/tmp/instruction.md",
        resolution=ConflictResolution.OVERWRITE,
        new_path="/tmp/instruction.md",
    )

    result = resolver.get_install_path(original_path, conflict_info)

    assert result == original_path


def test_get_install_path_rename() -> None:
    """Test get_install_path with RENAME resolution."""
    resolver = ConflictResolver()
    original_path = Path("/tmp/instruction.md")
    conflict_info = ConflictInfo(
        instruction_name="test",
        existing_path="/tmp/instruction.md",
        resolution=ConflictResolution.RENAME,
        new_path="/tmp/instruction-1.md",
    )

    result = resolver.get_install_path(original_path, conflict_info)

    assert result == Path("/tmp/instruction-1.md")


def test_get_install_path_rename_no_new_path() -> None:
    """Test get_install_path with RENAME but no new_path (fallback)."""
    resolver = ConflictResolver()
    original_path = Path("/tmp/instruction.md")
    conflict_info = ConflictInfo(
        instruction_name="test",
        existing_path="/tmp/instruction.md",
        resolution=ConflictResolution.RENAME,
        new_path=None,  # Missing new_path
    )

    result = resolver.get_install_path(original_path, conflict_info)

    # Should fallback to original path
    assert result == original_path


@patch("builtins.input", return_value="1")
def test_prompt_conflict_resolution_skip(mock_input) -> None:
    """Test prompting user for conflict resolution - SKIP."""
    result = prompt_conflict_resolution("test-instruction")
    assert result == ConflictResolution.SKIP


@patch("builtins.input", return_value="2")
def test_prompt_conflict_resolution_rename(mock_input) -> None:
    """Test prompting user for conflict resolution - RENAME."""
    result = prompt_conflict_resolution("test-instruction")
    assert result == ConflictResolution.RENAME


@patch("builtins.input", return_value="3")
def test_prompt_conflict_resolution_overwrite(mock_input) -> None:
    """Test prompting user for conflict resolution - OVERWRITE."""
    result = prompt_conflict_resolution("test-instruction")
    assert result == ConflictResolution.OVERWRITE


@patch("builtins.input", side_effect=["invalid", "0", "4", "1"])
def test_prompt_conflict_resolution_invalid_then_valid(mock_input) -> None:
    """Test prompting user with invalid inputs then valid choice."""
    result = prompt_conflict_resolution("test-instruction")
    assert result == ConflictResolution.SKIP
    # Should have been called 4 times (3 invalid + 1 valid)
    assert mock_input.call_count == 4


def test_check_conflicts_no_existing_files(tmp_path: Path) -> None:
    """Test checking conflicts when no files exist."""
    target_paths = [
        tmp_path / "instruction1.md",
        tmp_path / "instruction2.md",
    ]

    conflicts = check_conflicts(target_paths)

    assert len(conflicts) == 0


def test_check_conflicts_some_existing_files(tmp_path: Path) -> None:
    """Test checking conflicts when some files exist."""
    # Create one file
    existing_file = tmp_path / "instruction1.md"
    existing_file.touch()

    target_paths = [
        existing_file,
        tmp_path / "instruction2.md",
    ]

    conflicts = check_conflicts(target_paths)

    assert len(conflicts) == 1
    assert "instruction1" in conflicts
    assert conflicts["instruction1"] == existing_file


def test_check_conflicts_all_existing_files(tmp_path: Path) -> None:
    """Test checking conflicts when all files exist."""
    # Create all files
    file1 = tmp_path / "instruction1.md"
    file2 = tmp_path / "instruction2.md"
    file1.touch()
    file2.touch()

    target_paths = [file1, file2]

    conflicts = check_conflicts(target_paths)

    assert len(conflicts) == 2
    assert "instruction1" in conflicts
    assert "instruction2" in conflicts


def test_batch_resolve_conflicts_skip() -> None:
    """Test batch resolving conflicts with SKIP strategy."""
    conflicts = {
        "inst1": Path("/tmp/inst1.md"),
        "inst2": Path("/tmp/inst2.md"),
    }

    resolutions = batch_resolve_conflicts(conflicts, ConflictResolution.SKIP)

    assert len(resolutions) == 2
    assert all(r.resolution == ConflictResolution.SKIP for r in resolutions.values())


def test_batch_resolve_conflicts_overwrite() -> None:
    """Test batch resolving conflicts with OVERWRITE strategy."""
    conflicts = {
        "inst1": Path("/tmp/inst1.md"),
        "inst2": Path("/tmp/inst2.md"),
    }

    resolutions = batch_resolve_conflicts(conflicts, ConflictResolution.OVERWRITE)

    assert len(resolutions) == 2
    assert all(r.resolution == ConflictResolution.OVERWRITE for r in resolutions.values())


def test_batch_resolve_conflicts_rename(tmp_path: Path) -> None:
    """Test batch resolving conflicts with RENAME strategy."""
    # Create files so rename logic works
    file1 = tmp_path / "inst1.md"
    file2 = tmp_path / "inst2.md"
    file1.touch()
    file2.touch()

    conflicts = {
        "inst1": file1,
        "inst2": file2,
    }

    resolutions = batch_resolve_conflicts(conflicts, ConflictResolution.RENAME)

    assert len(resolutions) == 2
    assert all(r.resolution == ConflictResolution.RENAME for r in resolutions.values())
    assert all(r.new_path is not None for r in resolutions.values())


def test_batch_resolve_conflicts_empty() -> None:
    """Test batch resolving with no conflicts."""
    conflicts = {}

    resolutions = batch_resolve_conflicts(conflicts, ConflictResolution.SKIP)

    assert len(resolutions) == 0
