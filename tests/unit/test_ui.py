"""Tests for UI utility functions."""

from datetime import datetime
from io import StringIO

from rich.console import Console
from rich.table import Table

from aiconfigkit.core.models import (
    AIToolType,
    InstallationRecord,
    InstallationScope,
    Instruction,
    InstructionBundle,
    RefType,
)
from aiconfigkit.utils.ui import (
    _shorten_url,
    format_bundle_details,
    format_installed_table,
    format_instructions_table,
    print_error,
    print_info,
    print_success,
    print_warning,
)


def test_format_instructions_table_with_instructions_only() -> None:
    """Test formatting instructions table without bundles."""
    instructions = [
        Instruction(
            name="instruction-1",
            description="First instruction",
            content="Content 1",
            file_path="inst1.md",
            tags=["python", "backend"],
        ),
        Instruction(
            name="instruction-2",
            description="Second instruction",
            content="Content 2",
            file_path="inst2.md",
            tags=["typescript"],
        ),
    ]
    bundles = []

    table = format_instructions_table(instructions, bundles, show_bundles=False)

    assert isinstance(table, Table)
    assert table.title == "Available Instructions"
    assert len(table.rows) == 2


def test_format_instructions_table_with_bundles() -> None:
    """Test formatting instructions table with bundles."""
    instructions = [
        Instruction(
            name="instruction-1",
            description="First instruction",
            content="Content 1",
            file_path="inst1.md",
            tags=["python"],
        )
    ]
    bundles = [
        InstructionBundle(
            name="bundle-1",
            description="Test bundle",
            instructions=["instruction-1", "instruction-2"],
            tags=["full-stack"],
        )
    ]

    table = format_instructions_table(instructions, bundles, show_bundles=True)

    assert isinstance(table, Table)
    # Should have both instruction and bundle
    assert len(table.rows) == 2


def test_format_instructions_table_empty() -> None:
    """Test formatting empty instructions table."""
    table = format_instructions_table([], [], show_bundles=False)

    assert isinstance(table, Table)
    assert len(table.rows) == 0


def test_format_instructions_table_without_tags() -> None:
    """Test formatting instructions table with instructions that have no tags."""
    instructions = [
        Instruction(
            name="no-tags",
            description="Instruction without tags",
            content="Content",
            file_path="notags.md",
            tags=[],
        )
    ]

    table = format_instructions_table(instructions, [], show_bundles=False)

    assert isinstance(table, Table)
    assert len(table.rows) == 1


def test_format_installed_table_grouped_by_tool() -> None:
    """Test formatting installed instructions table grouped by tool."""
    records = [
        InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            installed_path="/path/to/instruction",
            scope=InstallationScope.PROJECT,
            source_repo="https://github.com/user/repo",
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
            installed_at=datetime(2024, 1, 1),
        )
    ]

    table = format_installed_table(records, group_by_tool=True)

    assert isinstance(table, Table)
    assert len(table.rows) == 1


def test_format_installed_table_not_grouped() -> None:
    """Test formatting installed instructions table not grouped by tool."""
    records = [
        InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            installed_path="/path/to/instruction",
            scope=InstallationScope.PROJECT,
            source_repo="https://github.com/user/repo",
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
            installed_at=datetime(2024, 1, 1),
        )
    ]

    table = format_installed_table(records, group_by_tool=False)

    assert isinstance(table, Table)
    assert len(table.rows) == 1


def test_format_installed_table_multiple_tools() -> None:
    """Test formatting installed instructions table with multiple tools."""
    records = [
        InstallationRecord(
            instruction_name="instruction-1",
            ai_tool=AIToolType.CURSOR,
            installed_path="/path/1",
            scope=InstallationScope.PROJECT,
            source_repo="https://github.com/user/repo",
            installed_at=datetime(2024, 1, 1),
        ),
        InstallationRecord(
            instruction_name="instruction-2",
            ai_tool=AIToolType.CLAUDE,
            installed_path="/path/2",
            scope=InstallationScope.PROJECT,
            source_repo="https://github.com/user/repo",
            installed_at=datetime(2024, 1, 2),
        ),
    ]

    table = format_installed_table(records, group_by_tool=True)

    assert isinstance(table, Table)
    assert len(table.rows) == 2


def test_format_installed_table_with_bundle() -> None:
    """Test formatting installed instructions table with bundle information."""
    records = [
        InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            installed_path="/path/to/instruction",
            scope=InstallationScope.PROJECT,
            source_repo="https://github.com/user/repo",
            installed_at=datetime(2024, 1, 1),
            bundle_name="test-bundle",
        )
    ]

    table = format_installed_table(records, group_by_tool=False)

    assert isinstance(table, Table)
    assert len(table.rows) == 1


def test_format_installed_table_different_ref_types() -> None:
    """Test formatting installed instructions with different ref types."""
    records = [
        InstallationRecord(
            instruction_name="with-tag",
            ai_tool=AIToolType.CURSOR,
            installed_path="/path/1",
            scope=InstallationScope.PROJECT,
            source_repo="https://github.com/user/repo",
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
            installed_at=datetime(2024, 1, 1),
        ),
        InstallationRecord(
            instruction_name="with-branch",
            ai_tool=AIToolType.CURSOR,
            installed_path="/path/2",
            scope=InstallationScope.PROJECT,
            source_repo="https://github.com/user/repo",
            source_ref="main",
            source_ref_type=RefType.BRANCH,
            installed_at=datetime(2024, 1, 2),
        ),
        InstallationRecord(
            instruction_name="with-commit",
            ai_tool=AIToolType.CURSOR,
            installed_path="/path/3",
            scope=InstallationScope.PROJECT,
            source_repo="https://github.com/user/repo",
            source_ref="abc123",
            source_ref_type=RefType.COMMIT,
            installed_at=datetime(2024, 1, 3),
        ),
    ]

    table = format_installed_table(records, group_by_tool=False)

    assert isinstance(table, Table)
    assert len(table.rows) == 3


def test_format_bundle_details() -> None:
    """Test formatting bundle details table."""
    bundle = InstructionBundle(
        name="test-bundle",
        description="Test bundle description",
        instructions=["inst1", "inst2"],
        tags=["python", "backend"],
    )
    instructions = [
        Instruction(
            name="inst1",
            description="First instruction",
            content="Content 1",
            file_path="inst1.md",
            tags=["python"],
        ),
        Instruction(
            name="inst2",
            description="Second instruction",
            content="Content 2",
            file_path="inst2.md",
            tags=["backend"],
        ),
    ]

    table = format_bundle_details(bundle, instructions)

    assert isinstance(table, Table)
    assert table.title == "Bundle: test-bundle"
    assert len(table.rows) == 2


def test_print_success() -> None:
    """Test printing success message."""
    console = Console(file=StringIO())
    print_success("Operation succeeded", console=console)
    output = console.file.getvalue()
    assert "Operation succeeded" in output


def test_print_success_default_console() -> None:
    """Test printing success with default console."""
    # Should not raise an error
    print_success("Test message")


def test_print_error() -> None:
    """Test printing error message."""
    console = Console(file=StringIO())
    print_error("Operation failed", console=console)
    output = console.file.getvalue()
    assert "Operation failed" in output
    assert "Error" in output


def test_print_error_default_console() -> None:
    """Test printing error with default console."""
    # Should not raise an error
    print_error("Test error")


def test_print_warning() -> None:
    """Test printing warning message."""
    console = Console(file=StringIO())
    print_warning("Warning message", console=console)
    output = console.file.getvalue()
    assert "Warning message" in output
    assert "Warning" in output


def test_print_warning_default_console() -> None:
    """Test printing warning with default console."""
    # Should not raise an error
    print_warning("Test warning")


def test_print_info() -> None:
    """Test printing info message."""
    console = Console(file=StringIO())
    print_info("Info message", console=console)
    output = console.file.getvalue()
    assert "Info message" in output


def test_print_info_default_console() -> None:
    """Test printing info with default console."""
    # Should not raise an error
    print_info("Test info")


def test_shorten_url_short_url() -> None:
    """Test shortening a URL that is already short."""
    url = "https://github.com/user/repo"
    assert _shorten_url(url, max_length=50) == url


def test_shorten_url_long_url() -> None:
    """Test shortening a long URL."""
    url = "https://github.com/organization/very-long-repository-name-that-exceeds-limit"
    shortened = _shorten_url(url, max_length=40)
    # The function tries to keep domain and last 2 parts, which may still be longer than max_length
    # It only truncates if it can't intelligently shorten
    assert "github.com" in shortened
    assert "..." in shortened


def test_shorten_url_with_deep_path() -> None:
    """Test shortening a URL with deep path."""
    url = "https://github.com/org/repo/tree/main/path/to/deep/file"
    shortened = _shorten_url(url, max_length=50)
    # Should keep domain and last 2 parts
    assert "github.com" in shortened
    assert "..." in shortened


def test_shorten_url_no_protocol() -> None:
    """Test shortening a URL without protocol."""
    url = "this-is-a-very-long-string-without-protocol-that-needs-truncation"
    shortened = _shorten_url(url, max_length=30)
    assert len(shortened) <= 30
    assert shortened.endswith("...")


def test_shorten_url_exact_length() -> None:
    """Test shortening a URL that is exactly at max length."""
    url = "https://example.com/exact"
    max_len = len(url)
    assert _shorten_url(url, max_length=max_len) == url
