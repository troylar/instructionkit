"""Unit tests for semantic version manager."""

import subprocess
from pathlib import Path

import pytest
from packaging.version import Version

from aiconfigkit.core.version import VersionError, VersionManager


@pytest.fixture
def version_manager() -> VersionManager:
    """Create a version manager without repository."""
    return VersionManager()


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Path:
    """Create a temporary Git repository with version tags."""
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()

    # Initialize Git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Create initial commit
    (repo_dir / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Create version tags
    for version in ["v1.0.0", "v1.1.0", "v1.2.0", "v2.0.0", "v2.1.0"]:
        subprocess.run(
            ["git", "tag", version],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )

    return repo_dir


class TestVersionManager:
    """Test VersionManager class."""

    def test_init_without_repository(self) -> None:
        """Test initialization without repository path."""
        manager = VersionManager()
        assert manager.repository_path is None

    def test_init_with_repository(self, tmp_path: Path) -> None:
        """Test initialization with repository path."""
        manager = VersionManager(tmp_path)
        assert manager.repository_path == tmp_path

    def test_parse_valid_version(self, version_manager: VersionManager) -> None:
        """Test parsing valid version strings."""
        version = version_manager.parse("1.0.0")
        assert isinstance(version, Version)
        assert str(version) == "1.0.0"

    def test_parse_version_with_v_prefix(self, version_manager: VersionManager) -> None:
        """Test parsing version with 'v' prefix."""
        version = version_manager.parse("v1.2.3")
        assert str(version) == "1.2.3"

    def test_parse_version_with_prerelease(self, version_manager: VersionManager) -> None:
        """Test parsing version with pre-release identifier."""
        version = version_manager.parse("1.0.0-alpha.1")
        assert version.is_prerelease

    def test_parse_invalid_version_raises_error(self, version_manager: VersionManager) -> None:
        """Test that invalid version string raises VersionError."""
        with pytest.raises(VersionError, match="Invalid version string"):
            version_manager.parse("invalid")

    def test_parse_empty_version_raises_error(self, version_manager: VersionManager) -> None:
        """Test that empty version string raises VersionError."""
        with pytest.raises(VersionError, match="Invalid version string"):
            version_manager.parse("")

    def test_compare_equal_versions(self, version_manager: VersionManager) -> None:
        """Test comparing equal versions."""
        result = version_manager.compare("1.0.0", "1.0.0")
        assert result == 0

    def test_compare_v1_less_than_v2(self, version_manager: VersionManager) -> None:
        """Test comparing v1 < v2."""
        result = version_manager.compare("1.0.0", "2.0.0")
        assert result == -1

    def test_compare_v1_greater_than_v2(self, version_manager: VersionManager) -> None:
        """Test comparing v1 > v2."""
        result = version_manager.compare("2.0.0", "1.0.0")
        assert result == 1

    def test_compare_with_v_prefix(self, version_manager: VersionManager) -> None:
        """Test comparing versions with 'v' prefix."""
        result = version_manager.compare("v1.0.0", "v1.1.0")
        assert result == -1

    def test_compare_patch_versions(self, version_manager: VersionManager) -> None:
        """Test comparing patch versions."""
        result = version_manager.compare("1.0.0", "1.0.1")
        assert result == -1

    def test_is_compatible_same_version(self, version_manager: VersionManager) -> None:
        """Test compatibility with same version."""
        assert version_manager.is_compatible("1.0.0", "1.0.0")

    def test_is_compatible_higher_minor(self, version_manager: VersionManager) -> None:
        """Test compatibility with higher minor version."""
        assert version_manager.is_compatible("1.0.0", "1.1.0")

    def test_is_compatible_higher_patch(self, version_manager: VersionManager) -> None:
        """Test compatibility with higher patch version."""
        assert version_manager.is_compatible("1.0.0", "1.0.1")

    def test_is_not_compatible_lower_version(self, version_manager: VersionManager) -> None:
        """Test incompatibility with lower version."""
        assert not version_manager.is_compatible("1.1.0", "1.0.0")

    def test_is_not_compatible_different_major(self, version_manager: VersionManager) -> None:
        """Test incompatibility with different major version."""
        assert not version_manager.is_compatible("1.0.0", "2.0.0")

    def test_get_available_versions_without_repository_raises_error(self, version_manager: VersionManager) -> None:
        """Test that querying versions without repository raises error."""
        with pytest.raises(VersionError, match="Repository path not set"):
            version_manager.get_available_versions()

    def test_get_available_versions_nonexistent_path_raises_error(self, tmp_path: Path) -> None:
        """Test that querying versions with nonexistent path raises error."""
        manager = VersionManager(tmp_path / "nonexistent")
        with pytest.raises(VersionError, match="Repository path does not exist"):
            manager.get_available_versions()

    def test_get_available_versions_from_git_tags(self, temp_git_repo: Path) -> None:
        """Test querying available versions from Git tags."""
        manager = VersionManager(temp_git_repo)
        versions = manager.get_available_versions()

        assert len(versions) == 5
        # Should be sorted in descending order
        assert versions[0] == "2.1.0"
        assert versions[1] == "2.0.0"
        assert versions[2] == "1.2.0"
        assert versions[3] == "1.1.0"
        assert versions[4] == "1.0.0"

    def test_get_available_versions_ignores_non_version_tags(self, tmp_path: Path) -> None:
        """Test that non-version tags are ignored."""
        repo_dir = tmp_path / "test-repo"
        repo_dir.mkdir()

        # Initialize Git repo
        subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )

        # Create initial commit
        (repo_dir / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )

        # Create mix of version and non-version tags
        subprocess.run(["git", "tag", "v1.0.0"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "tag", "release"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "tag", "v2.0.0"], cwd=repo_dir, check=True, capture_output=True)

        manager = VersionManager(repo_dir)
        versions = manager.get_available_versions()

        # Should only return version tags
        assert len(versions) == 2
        assert "1.0.0" in versions
        assert "2.0.0" in versions

    def test_get_latest_version(self, temp_git_repo: Path) -> None:
        """Test getting latest version."""
        manager = VersionManager(temp_git_repo)
        latest = manager.get_latest_version()

        assert latest == "2.1.0"

    def test_get_latest_version_no_tags_returns_none(self, tmp_path: Path) -> None:
        """Test getting latest version when no tags exist."""
        repo_dir = tmp_path / "test-repo"
        repo_dir.mkdir()

        # Initialize Git repo without tags
        subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )

        # Create initial commit
        (repo_dir / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )

        manager = VersionManager(repo_dir)
        latest = manager.get_latest_version()

        assert latest is None

    def test_validate_version_string_valid(self, version_manager: VersionManager) -> None:
        """Test validating valid version strings."""
        assert version_manager.validate_version_string("1.0.0")
        assert version_manager.validate_version_string("v2.1.3")
        assert version_manager.validate_version_string("0.0.1")

    def test_validate_version_string_invalid(self, version_manager: VersionManager) -> None:
        """Test validating invalid version strings."""
        assert not version_manager.validate_version_string("invalid")
        assert not version_manager.validate_version_string("")
        assert not version_manager.validate_version_string("1.0")
        assert not version_manager.validate_version_string("v1")
