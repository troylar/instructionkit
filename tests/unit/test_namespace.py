"""Tests for namespace utilities."""

from pathlib import Path

import pytest

from aiconfigkit.utils.namespace import (
    derive_namespace,
    extract_repo_name_from_url,
    get_install_path,
    validate_namespace,
)


class TestExtractRepoNameFromUrl:
    """Tests for extract_repo_name_from_url function."""

    def test_github_https_url(self):
        """Test extracting repo name from GitHub HTTPS URL."""
        url = "https://github.com/acme/templates"
        assert extract_repo_name_from_url(url) == "templates"

    def test_github_https_url_with_git_suffix(self):
        """Test extracting repo name from GitHub HTTPS URL with .git suffix."""
        url = "https://github.com/acme/templates.git"
        assert extract_repo_name_from_url(url) == "templates"

    def test_github_ssh_url(self):
        """Test extracting repo name from GitHub SSH URL."""
        url = "git@github.com:acme/templates.git"
        assert extract_repo_name_from_url(url) == "templates"

    def test_gitlab_https_url(self):
        """Test extracting repo name from GitLab HTTPS URL."""
        url = "https://gitlab.com/acme/templates"
        assert extract_repo_name_from_url(url) == "templates"

    def test_gitlab_ssh_url(self):
        """Test extracting repo name from GitLab SSH URL."""
        url = "git@gitlab.com:acme/templates.git"
        assert extract_repo_name_from_url(url) == "templates"

    def test_self_hosted_https_url(self):
        """Test extracting repo name from self-hosted HTTPS URL."""
        url = "https://git.company.com/team/templates"
        assert extract_repo_name_from_url(url) == "templates"

    def test_nested_path(self):
        """Test extracting repo name from URL with nested path."""
        url = "https://github.com/org/team/templates"
        assert extract_repo_name_from_url(url) == "templates"

    def test_url_with_trailing_slash(self):
        """Test extracting repo name from URL with trailing slash."""
        url = "https://github.com/acme/templates/"
        assert extract_repo_name_from_url(url) == "templates"

    def test_complex_repo_name(self):
        """Test extracting complex repo name with hyphens."""
        url = "https://github.com/acme/my-awesome-templates"
        assert extract_repo_name_from_url(url) == "my-awesome-templates"


class TestValidateNamespace:
    """Tests for validate_namespace function."""

    def test_valid_namespace(self):
        """Test valid namespace passes validation."""
        validate_namespace("acme-templates")  # Should not raise

    def test_empty_namespace_raises(self):
        """Test empty namespace raises ValueError."""
        with pytest.raises(ValueError, match="Namespace cannot be empty"):
            validate_namespace("")

    def test_whitespace_only_raises(self):
        """Test whitespace-only namespace raises ValueError."""
        with pytest.raises(ValueError, match="Namespace cannot be empty"):
            validate_namespace("   ")

    def test_invalid_characters_raises(self):
        """Test namespace with invalid characters raises ValueError."""
        with pytest.raises(ValueError, match="Invalid namespace"):
            validate_namespace("acme@templates")

    def test_uppercase_allowed(self):
        """Test uppercase letters are allowed."""
        validate_namespace("ACME-Templates")  # Should not raise

    def test_spaces_rejected(self):
        """Test spaces are rejected."""
        with pytest.raises(ValueError, match="Invalid namespace"):
            validate_namespace("acme templates")

    def test_underscores_rejected(self):
        """Test underscores are rejected."""
        with pytest.raises(ValueError, match="Invalid namespace"):
            validate_namespace("acme_templates")

    def test_dots_rejected(self):
        """Test dots are rejected."""
        with pytest.raises(ValueError, match="Invalid namespace"):
            validate_namespace("acme.templates")

    def test_too_long_raises(self):
        """Test namespace exceeding max length raises ValueError."""
        long_namespace = "a" * 51
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validate_namespace(long_namespace)

    def test_valid_with_numbers(self):
        """Test valid namespace with numbers."""
        validate_namespace("team-2024")  # Should not raise

    def test_valid_alphanumeric_with_hyphens(self):
        """Test valid namespace with alphanumeric and hyphens."""
        validate_namespace("acme-eng-123")  # Should not raise


class TestDeriveNamespace:
    """Tests for derive_namespace function."""

    def test_with_override(self):
        """Test using namespace override."""
        namespace = derive_namespace("https://github.com/acme/templates", override="custom")
        assert namespace == "custom"

    def test_without_override(self):
        """Test deriving namespace from URL."""
        namespace = derive_namespace("https://github.com/acme/templates")
        assert namespace == "templates"

    def test_override_with_invalid_characters(self):
        """Test override with invalid characters raises error."""
        with pytest.raises(ValueError, match="Invalid namespace"):
            derive_namespace("https://github.com/acme/templates", override="custom@name")

    def test_override_with_spaces(self):
        """Test override with spaces raises error."""
        with pytest.raises(ValueError, match="Invalid namespace"):
            derive_namespace("https://github.com/acme/templates", override="custom name")

    def test_override_with_uppercase(self):
        """Test override with uppercase is allowed."""
        namespace = derive_namespace("https://github.com/acme/templates", override="CustomName")
        assert namespace == "CustomName"

    def test_valid_override_with_hyphens(self):
        """Test valid override with hyphens."""
        namespace = derive_namespace("https://github.com/acme/templates", override="acme-eng")
        assert namespace == "acme-eng"

    def test_valid_override_with_numbers(self):
        """Test valid override with numbers."""
        namespace = derive_namespace("https://github.com/acme/templates", override="team-2024")
        assert namespace == "team-2024"

    def test_override_whitespace_only_raises(self):
        """Test override with only whitespace raises error."""
        with pytest.raises(ValueError, match="Namespace override cannot be empty"):
            derive_namespace("https://github.com/acme/templates", override="   ")

    def test_override_too_long_raises(self):
        """Test override exceeding max length raises error."""
        long_override = "a" * 51
        with pytest.raises(ValueError, match="exceeds maximum length"):
            derive_namespace("https://github.com/acme/templates", override=long_override)


class TestGetInstallPath:
    """Tests for get_install_path function."""

    def test_basic_path_construction(self):
        """Test basic install path construction."""
        base_path = Path("/project/.claude/commands")
        install_path = get_install_path("acme", "test-api", base_path, "md")
        assert install_path == base_path / "acme.test-api.md"

    def test_with_different_extension(self):
        """Test install path with different extension."""
        base_path = Path("/project/.cursor/rules")
        install_path = get_install_path("acme", "test-api", base_path, "mdc")
        assert install_path == base_path / "acme.test-api.mdc"

    def test_complex_namespace(self):
        """Test install path with complex namespace."""
        base_path = Path("/project/.claude/commands")
        install_path = get_install_path("acme-engineering", "test-api", base_path, "md")
        assert install_path == base_path / "acme-engineering.test-api.md"

    def test_complex_template_name(self):
        """Test install path with complex template name."""
        base_path = Path("/project/.claude/commands")
        install_path = get_install_path("acme", "setup-fastapi-project", base_path, "md")
        assert install_path == base_path / "acme.setup-fastapi-project.md"

    def test_path_is_absolute(self):
        """Test that returned path maintains absolute status if base is absolute."""
        # Use Path.cwd() to get a platform-independent absolute path
        base_path = Path.cwd() / "absolute" / "path"
        install_path = get_install_path("acme", "test", base_path, "md")
        assert install_path.is_absolute()

    def test_path_is_relative(self):
        """Test that returned path maintains relative status if base is relative."""
        base_path = Path("relative/path")
        install_path = get_install_path("acme", "test", base_path, "md")
        assert not install_path.is_absolute()

    def test_filename_format(self):
        """Test that filename follows namespace.template-name.ext format."""
        base_path = Path("/project")
        install_path = get_install_path("ns", "template", base_path, "txt")
        assert install_path.name == "ns.template.txt"

    def test_multiple_extensions(self):
        """Test with various file extensions."""
        base_path = Path("/project")

        for ext in ["md", "mdc", "txt", "py"]:
            install_path = get_install_path("acme", "test", base_path, ext)
            assert install_path.suffix == f".{ext}"
