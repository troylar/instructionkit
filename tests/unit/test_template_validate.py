"""Tests for template validation command."""

import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
import typer

from aiconfigkit.cli.template_validate import (
    ValidationIssue,
    _display_validation_results,
    _validate_installations,
    validate_command,
)
from aiconfigkit.core.models import AIToolType, InstallationScope, TemplateInstallationRecord


class TestValidationIssue:
    """Tests for ValidationIssue class."""

    def test_initialization(self):
        """Test ValidationIssue initialization."""
        issue = ValidationIssue(
            severity="error",
            template="test-template",
            issue_type="missing_file",
            description="File not found",
            remediation="Reinstall template",
        )

        assert issue.severity == "error"
        assert issue.template == "test-template"
        assert issue.issue_type == "missing_file"
        assert issue.description == "File not found"
        assert issue.remediation == "Reinstall template"

    def test_initialization_with_default_remediation(self):
        """Test ValidationIssue with empty remediation."""
        issue = ValidationIssue(severity="warning", template="test", issue_type="modified", description="File modified")

        assert issue.remediation == ""


class TestValidateInstallations:
    """Tests for _validate_installations function."""

    def test_no_installations(self, tmp_path):
        """Test validation with no installations."""
        from aiconfigkit.storage.template_tracker import TemplateInstallationTracker

        tracker = TemplateInstallationTracker.for_project(tmp_path)
        issues = _validate_installations(tracker, "project", verbose=False)

        assert issues == []

    @patch("aiconfigkit.cli.template_validate.calculate_file_checksum")
    def test_missing_file_issue(self, mock_checksum, tmp_path):
        """Test detection of missing installed files."""
        from aiconfigkit.storage.template_tracker import TemplateInstallationTracker

        # Create tracker with installation record pointing to non-existent file
        tracker = TemplateInstallationTracker.for_project(tmp_path)
        record = TemplateInstallationRecord(
            id=str(uuid.uuid4()),
            namespace="acme",
            template_name="test",
            installed_path=str(tmp_path / "nonexistent.md"),
            source_repo="https://github.com/acme/templates",
            source_version="1.0.0",
            checksum="a" * 64,  # Valid SHA-256 checksum (64 hex chars)
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )
        tracker.save_installation_records([record])

        issues = _validate_installations(tracker, "project", verbose=False)

        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert issues[0].issue_type == "missing_file"
        assert issues[0].template == "acme.test"

    @patch("aiconfigkit.cli.template_validate.calculate_file_checksum")
    @patch("aiconfigkit.cli.template_validate.TemplateLibraryManager")
    def test_modified_file_issue(self, mock_library, mock_checksum, tmp_path):
        """Test detection of locally modified files."""
        from aiconfigkit.storage.template_tracker import TemplateInstallationTracker

        # Create installed file
        installed_file = tmp_path / "installed.md"
        installed_file.write_text("modified content")

        # Setup tracker
        tracker = TemplateInstallationTracker.for_project(tmp_path)
        record = TemplateInstallationRecord(
            id=str(uuid.uuid4()),
            namespace="acme",
            template_name="test",
            installed_path=str(installed_file),
            source_repo="https://github.com/acme/templates",
            source_version="1.0.0",
            checksum="b" * 64,  # Valid original checksum
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )
        tracker.save_installation_records([record])

        # Mock checksum to return different value (indicating modification)
        mock_checksum.return_value = "c" * 64  # Different checksum
        mock_library.return_value.get_repository_version.return_value = "1.0.0"

        issues = _validate_installations(tracker, "project", verbose=False)

        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert issues[0].issue_type == "modified"
        assert "modified locally" in issues[0].description

    @patch("aiconfigkit.cli.template_validate.calculate_file_checksum")
    @patch("aiconfigkit.cli.template_validate.TemplateLibraryManager")
    def test_outdated_version_issue(self, mock_library, mock_checksum, tmp_path):
        """Test detection of outdated template versions."""
        from aiconfigkit.storage.template_tracker import TemplateInstallationTracker

        # Create installed file
        installed_file = tmp_path / "installed.md"
        installed_file.write_text("content")

        # Setup tracker
        tracker = TemplateInstallationTracker.for_project(tmp_path)
        record = TemplateInstallationRecord(
            id=str(uuid.uuid4()),
            namespace="acme",
            template_name="test",
            installed_path=str(installed_file),
            source_repo="https://github.com/acme/templates",
            source_version="1.0.0",
            checksum="d" * 64,  # Valid checksum
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )
        tracker.save_installation_records([record])

        # Mock to indicate newer version available
        mock_checksum.return_value = "d" * 64  # Unchanged
        mock_library.return_value.get_repository_version.return_value = "2.0.0"

        issues = _validate_installations(tracker, "project", verbose=False)

        assert len(issues) == 1
        assert issues[0].severity == "info"
        assert issues[0].issue_type == "outdated"
        assert "Newer version available" in issues[0].description

    @patch("aiconfigkit.cli.template_validate.calculate_file_checksum")
    @patch("aiconfigkit.cli.template_validate.TemplateLibraryManager")
    @patch("aiconfigkit.cli.template_validate.console")
    def test_checksum_exception_with_verbose(self, mock_console, mock_library, mock_checksum, tmp_path):
        """Test verbose output when checksum verification fails."""
        from aiconfigkit.storage.template_tracker import TemplateInstallationTracker

        # Create installed file
        installed_file = tmp_path / "installed.md"
        installed_file.write_text("content")

        # Setup tracker
        tracker = TemplateInstallationTracker.for_project(tmp_path)
        record = TemplateInstallationRecord(
            id=str(uuid.uuid4()),
            namespace="acme",
            template_name="test",
            installed_path=str(installed_file),
            source_repo="https://github.com/acme/templates",
            source_version="1.0.0",
            checksum="e" * 64,
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )
        tracker.save_installation_records([record])

        # Mock checksum to raise exception
        mock_checksum.side_effect = RuntimeError("Checksum error")
        mock_library.return_value.get_repository_version.return_value = "1.0.0"

        issues = _validate_installations(tracker, "project", verbose=True)

        # Should handle exception gracefully and show verbose message
        # No modified issue should be created
        assert all(issue.issue_type != "modified" for issue in issues)

    @patch("aiconfigkit.cli.template_validate.calculate_file_checksum")
    @patch("aiconfigkit.cli.template_validate.TemplateLibraryManager")
    @patch("aiconfigkit.cli.template_validate.console")
    def test_version_check_exception_with_verbose(self, mock_console, mock_library, mock_checksum, tmp_path):
        """Test verbose output when version check fails."""
        from aiconfigkit.storage.template_tracker import TemplateInstallationTracker

        # Create installed file
        installed_file = tmp_path / "installed.md"
        installed_file.write_text("content")

        # Setup tracker
        tracker = TemplateInstallationTracker.for_project(tmp_path)
        record = TemplateInstallationRecord(
            id=str(uuid.uuid4()),
            namespace="acme",
            template_name="test",
            installed_path=str(installed_file),
            source_repo="https://github.com/acme/templates",
            source_version="1.0.0",
            checksum="f" * 64,
            scope=InstallationScope.PROJECT,
            installed_at=datetime.now(),
            ide_type=AIToolType.CLAUDE,
        )
        tracker.save_installation_records([record])

        # Mock to pass checksum but fail version check
        mock_checksum.return_value = "f" * 64
        mock_library.return_value.get_repository_version.side_effect = RuntimeError("Version check error")

        issues = _validate_installations(tracker, "project", verbose=True)

        # Should handle exception gracefully and show verbose message
        # No outdated issue should be created
        assert all(issue.issue_type != "outdated" for issue in issues)


class TestDisplayValidationResults:
    """Tests for _display_validation_results function."""

    @patch("aiconfigkit.cli.template_validate.console")
    def test_display_no_issues(self, mock_console):
        """Test display with no validation issues."""
        _display_validation_results([], fix=False, verbose=False)

        # Should print success message
        assert any("All templates are valid" in str(call) for call in mock_console.print.call_args_list)

    @patch("aiconfigkit.cli.template_validate.console")
    def test_display_with_errors(self, mock_console):
        """Test display with error-level issues."""
        issues = [
            ValidationIssue(
                severity="error",
                template="test",
                issue_type="missing_file",
                description="File not found",
                remediation="Reinstall",
            )
        ]

        with pytest.raises(typer.Exit) as exc_info:
            _display_validation_results(issues, fix=False, verbose=False)

        assert exc_info.value.exit_code == 1

    @patch("aiconfigkit.cli.template_validate.console")
    def test_display_with_warnings_only(self, mock_console):
        """Test display with warning-level issues (no exit)."""
        issues = [
            ValidationIssue(
                severity="warning",
                template="test",
                issue_type="modified",
                description="File modified",
                remediation="Update",
            )
        ]

        # Should not raise SystemExit for warnings
        _display_validation_results(issues, fix=False, verbose=False)

    @patch("aiconfigkit.cli.template_validate.console")
    def test_display_summary(self, mock_console):
        """Test that summary is displayed correctly."""
        issues = [
            ValidationIssue("error", "test1", "missing_file", "File not found", "Reinstall"),
            ValidationIssue("warning", "test2", "modified", "Modified", "Update"),
            ValidationIssue("info", "test3", "outdated", "Outdated", "Upgrade"),
        ]

        with pytest.raises(typer.Exit):
            _display_validation_results(issues, fix=False, verbose=False)

        # Check summary was printed
        print_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Validation Summary" in call for call in print_calls)


class TestValidateCommand:
    """Tests for validate_command function."""

    @patch("aiconfigkit.cli.template_validate.find_project_root")
    @patch("aiconfigkit.cli.template_validate._validate_installations")
    @patch("aiconfigkit.cli.template_validate._display_validation_results")
    def test_validate_project_scope(self, mock_display, mock_validate, mock_find_root, tmp_path):
        """Test validation with project scope."""
        mock_find_root.return_value = tmp_path
        mock_validate.return_value = []

        validate_command(scope="project", fix=False, verbose=False)

        mock_validate.assert_called_once()
        mock_display.assert_called_once()

    @patch("aiconfigkit.cli.template_validate._validate_installations")
    @patch("aiconfigkit.cli.template_validate._display_validation_results")
    def test_validate_global_scope(self, mock_display, mock_validate):
        """Test validation with global scope."""
        mock_validate.return_value = []

        validate_command(scope="global", fix=False, verbose=False)

        mock_validate.assert_called_once()
        mock_display.assert_called_once()

    @patch("aiconfigkit.cli.template_validate.find_project_root")
    @patch("aiconfigkit.cli.template_validate._validate_installations")
    @patch("aiconfigkit.cli.template_validate._display_validation_results")
    def test_validate_all_scope(self, mock_display, mock_validate, mock_find_root, tmp_path):
        """Test validation with 'all' scope."""
        mock_find_root.return_value = tmp_path
        mock_validate.return_value = []

        validate_command(scope="all", fix=False, verbose=False)

        # Should call validate twice (project + global)
        assert mock_validate.call_count == 2
        mock_display.assert_called_once()

    @patch("aiconfigkit.cli.template_validate.console")
    def test_validate_invalid_scope(self, mock_console):
        """Test validation with invalid scope raises error."""
        with pytest.raises(typer.Exit) as exc_info:
            validate_command(scope="invalid", fix=False, verbose=False)

        assert exc_info.value.exit_code == 1

    @patch("aiconfigkit.cli.template_validate.find_project_root")
    @patch("aiconfigkit.cli.template_validate.console")
    def test_validate_project_scope_no_project(self, mock_console, mock_find_root):
        """Test project scope when not in a project directory."""
        mock_find_root.return_value = None

        with pytest.raises(typer.Exit) as exc_info:
            validate_command(scope="project", fix=False, verbose=False)

        assert exc_info.value.exit_code == 1

    @patch("aiconfigkit.cli.template_validate.find_project_root")
    @patch("aiconfigkit.cli.template_validate._validate_installations")
    def test_validate_keyboard_interrupt(self, mock_validate, mock_find_root, tmp_path):
        """Test handling of keyboard interrupt during validation."""
        mock_find_root.return_value = tmp_path
        mock_validate.side_effect = KeyboardInterrupt()

        with pytest.raises(typer.Exit) as exc_info:
            validate_command(scope="project", fix=False, verbose=False)

        assert exc_info.value.exit_code == 130  # Standard SIGINT exit code

    @patch("aiconfigkit.cli.template_validate.find_project_root")
    @patch("aiconfigkit.cli.template_validate._validate_installations")
    def test_validate_generic_exception(self, mock_validate, mock_find_root, tmp_path):
        """Test handling of unexpected exception during validation."""
        mock_find_root.return_value = tmp_path
        mock_validate.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(typer.Exit) as exc_info:
            validate_command(scope="project", fix=False, verbose=False)

        assert exc_info.value.exit_code == 1
