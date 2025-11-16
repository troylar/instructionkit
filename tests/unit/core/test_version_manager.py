"""Unit tests for version management."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aiconfigkit.core.version import VersionError, VersionManager


class TestVersionManager:
    """Test VersionManager class."""

    def test_init_no_repository(self) -> None:
        """Test initialization without repository path."""
        vm = VersionManager()
        assert vm.repository_path is None

    def test_init_with_repository(self, tmp_path: Path) -> None:
        """Test initialization with repository path."""
        vm = VersionManager(tmp_path)
        assert vm.repository_path == tmp_path

    def test_parse_basic_version(self) -> None:
        """Test parsing basic semantic version."""
        vm = VersionManager()
        version = vm.parse("1.2.3")
        assert str(version) == "1.2.3"

    def test_parse_version_with_v_prefix(self) -> None:
        """Test parsing version with 'v' prefix."""
        vm = VersionManager()
        version = vm.parse("v2.5.10")
        assert str(version) == "2.5.10"

    def test_parse_version_with_prerelease(self) -> None:
        """Test parsing version with prerelease."""
        vm = VersionManager()
        version = vm.parse("1.0.0-alpha")
        assert str(version) == "1.0.0a0"

    def test_parse_version_with_build_metadata(self) -> None:
        """Test parsing version with build metadata."""
        vm = VersionManager()
        version = vm.parse("1.0.0+build.123")
        assert "1.0.0" in str(version)

    def test_parse_invalid_version(self) -> None:
        """Test parsing invalid version raises error."""
        vm = VersionManager()
        with pytest.raises(VersionError, match="Invalid version string"):
            vm.parse("not.a.version")

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string raises error."""
        vm = VersionManager()
        with pytest.raises(VersionError, match="Invalid version string"):
            vm.parse("")

    def test_compare_versions_less_than(self) -> None:
        """Test comparing versions (less than)."""
        vm = VersionManager()
        result = vm.compare("1.0.0", "2.0.0")
        assert result == -1

    def test_compare_versions_equal(self) -> None:
        """Test comparing versions (equal)."""
        vm = VersionManager()
        result = vm.compare("1.2.3", "1.2.3")
        assert result == 0

    def test_compare_versions_greater_than(self) -> None:
        """Test comparing versions (greater than)."""
        vm = VersionManager()
        result = vm.compare("2.0.0", "1.0.0")
        assert result == 1

    def test_compare_with_v_prefix(self) -> None:
        """Test comparing versions with 'v' prefix."""
        vm = VersionManager()
        result = vm.compare("v1.0.0", "v2.0.0")
        assert result == -1

    def test_compare_patch_versions(self) -> None:
        """Test comparing patch versions."""
        vm = VersionManager()
        result = vm.compare("1.2.3", "1.2.4")
        assert result == -1

    def test_compare_minor_versions(self) -> None:
        """Test comparing minor versions."""
        vm = VersionManager()
        result = vm.compare("1.5.0", "1.3.0")
        assert result == 1

    def test_is_compatible_same_version(self) -> None:
        """Test compatibility with same version."""
        vm = VersionManager()
        assert vm.is_compatible("1.0.0", "1.0.0") is True

    def test_is_compatible_newer_patch(self) -> None:
        """Test compatibility with newer patch version."""
        vm = VersionManager()
        assert vm.is_compatible("1.0.0", "1.0.5") is True

    def test_is_compatible_newer_minor(self) -> None:
        """Test compatibility with newer minor version."""
        vm = VersionManager()
        assert vm.is_compatible("1.2.0", "1.5.0") is True

    def test_is_compatible_older_version(self) -> None:
        """Test incompatibility with older version."""
        vm = VersionManager()
        assert vm.is_compatible("1.5.0", "1.2.0") is False

    def test_is_compatible_different_major(self) -> None:
        """Test incompatibility with different major version."""
        vm = VersionManager()
        assert vm.is_compatible("1.0.0", "2.0.0") is False

    def test_is_compatible_major_version_must_match(self) -> None:
        """Test that major version must match exactly."""
        vm = VersionManager()
        # Even if newer, different major version is incompatible
        assert vm.is_compatible("2.0.0", "1.9.9") is False

    def test_get_available_versions_no_repository(self) -> None:
        """Test getting versions without repository raises error."""
        vm = VersionManager()
        with pytest.raises(VersionError, match="Repository path not set"):
            vm.get_available_versions()

    def test_get_available_versions_nonexistent_repository(self, tmp_path: Path) -> None:
        """Test getting versions from nonexistent repository."""
        vm = VersionManager(tmp_path / "nonexistent")
        with pytest.raises(VersionError, match="Repository path does not exist"):
            vm.get_available_versions()

    @patch("subprocess.run")
    def test_get_available_versions_basic(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test getting available versions from Git tags."""
        mock_result = MagicMock()
        mock_result.stdout = "v1.0.0\nv1.1.0\nv2.0.0\n"
        mock_run.return_value = mock_result

        vm = VersionManager(tmp_path)
        versions = vm.get_available_versions()

        assert len(versions) == 3
        # Should be sorted in descending order
        assert versions[0] == "2.0.0"
        assert versions[1] == "1.1.0"
        assert versions[2] == "1.0.0"

    @patch("subprocess.run")
    def test_get_available_versions_filters_non_versions(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test that non-version tags are filtered out."""
        mock_result = MagicMock()
        mock_result.stdout = "v1.0.0\nrelease-candidate\nv2.0.0\nfeature-branch\n"
        mock_run.return_value = mock_result

        vm = VersionManager(tmp_path)
        versions = vm.get_available_versions()

        # Should only include valid versions
        assert len(versions) == 2
        assert "2.0.0" in versions
        assert "1.0.0" in versions

    @patch("subprocess.run")
    def test_get_available_versions_empty_output(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test getting versions when no tags exist."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        vm = VersionManager(tmp_path)
        versions = vm.get_available_versions()

        assert versions == []

    @patch("subprocess.run")
    def test_get_available_versions_git_error(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test getting versions when Git command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        vm = VersionManager(tmp_path)
        with pytest.raises(VersionError, match="Failed to query Git tags"):
            vm.get_available_versions()

    @patch("subprocess.run")
    def test_get_latest_version(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test getting latest version."""
        mock_result = MagicMock()
        mock_result.stdout = "v1.0.0\nv1.5.0\nv2.0.0\n"
        mock_run.return_value = mock_result

        vm = VersionManager(tmp_path)
        latest = vm.get_latest_version()

        assert latest == "2.0.0"

    @patch("subprocess.run")
    def test_get_latest_version_no_versions(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test getting latest version when no versions exist."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        vm = VersionManager(tmp_path)
        latest = vm.get_latest_version()

        assert latest is None

    def test_validate_version_string_valid(self) -> None:
        """Test validating valid semantic version."""
        vm = VersionManager()
        assert vm.validate_version_string("1.2.3") is True

    def test_validate_version_string_with_v_prefix(self) -> None:
        """Test validating version with 'v' prefix."""
        vm = VersionManager()
        assert vm.validate_version_string("v1.2.3") is True

    def test_validate_version_string_large_numbers(self) -> None:
        """Test validating version with large version numbers."""
        vm = VersionManager()
        assert vm.validate_version_string("100.200.300") is True

    def test_validate_version_string_missing_patch(self) -> None:
        """Test validating version missing patch number."""
        vm = VersionManager()
        # Only major.minor is not valid for strict semver
        assert vm.validate_version_string("1.2") is False

    def test_validate_version_string_only_major(self) -> None:
        """Test validating version with only major number."""
        vm = VersionManager()
        assert vm.validate_version_string("1") is False

    def test_validate_version_string_invalid(self) -> None:
        """Test validating invalid version string."""
        vm = VersionManager()
        assert vm.validate_version_string("not.a.version") is False

    def test_validate_version_string_empty(self) -> None:
        """Test validating empty version string."""
        vm = VersionManager()
        assert vm.validate_version_string("") is False

    def test_validate_version_string_with_prerelease(self) -> None:
        """Test validating version with prerelease."""
        vm = VersionManager()
        # Prerelease versions don't pass strict semver validation (non-numeric in parts)
        assert vm.validate_version_string("1.2.3-alpha") is False

    def test_validate_version_string_non_numeric_parts(self) -> None:
        """Test validating version with non-numeric parts in major.minor.patch."""
        vm = VersionManager()
        # This should be invalid (non-numeric in first three parts)
        result = vm.validate_version_string("a.b.c")
        assert result is False


class TestVersionError:
    """Test VersionError exception."""

    def test_version_error_creation(self) -> None:
        """Test creating VersionError."""
        error = VersionError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_version_error_raise(self) -> None:
        """Test raising VersionError."""
        with pytest.raises(VersionError):
            raise VersionError("Something went wrong")
