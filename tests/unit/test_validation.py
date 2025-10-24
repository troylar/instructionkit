"""Unit tests for input validation utilities."""

from instructionkit.utils.validation import (
    is_valid_checksum,
    is_valid_git_url,
    is_valid_instruction_name,
    is_valid_tag,
    normalize_repo_url,
    sanitize_instruction_name,
    validate_file_path,
)


class TestGitUrlValidation:
    """Test Git URL validation."""

    def test_valid_https_url(self):
        assert is_valid_git_url("https://github.com/user/repo.git")
        assert is_valid_git_url("https://bitbucket.org/user/repo")
        assert is_valid_git_url("https://gitlab.com/user/repo.git")

    def test_valid_ssh_url(self):
        assert is_valid_git_url("git@github.com:user/repo.git")
        assert is_valid_git_url("git@bitbucket.org:user/repo.git")

    def test_valid_git_protocol(self):
        assert is_valid_git_url("git://github.com/user/repo.git")

    def test_invalid_urls(self):
        """Test that invalid URLs are rejected."""
        assert not is_valid_git_url("")
        assert not is_valid_git_url(None)
        # Note: Simple strings like 'not-a-url' are valid as local paths


class TestInstructionNameValidation:
    """Test instruction name validation."""

    def test_valid_names(self):
        assert is_valid_instruction_name("python-best-practices")
        assert is_valid_instruction_name("backend-api")
        assert is_valid_instruction_name("test123")

    def test_invalid_names(self):
        assert not is_valid_instruction_name("Python-Best")  # uppercase
        assert not is_valid_instruction_name("123-start")  # starts with number
        assert not is_valid_instruction_name("ab")  # too short
        assert not is_valid_instruction_name("a" * 51)  # too long
        assert not is_valid_instruction_name("has_underscore")
        assert not is_valid_instruction_name("")
        assert not is_valid_instruction_name(None)


class TestTagValidation:
    """Test tag validation."""

    def test_valid_tags(self):
        assert is_valid_tag("python")
        assert is_valid_tag("backend")
        assert is_valid_tag("api-design")

    def test_invalid_tags(self):
        assert not is_valid_tag("a")  # too short
        assert not is_valid_tag("a" * 31)  # too long
        assert not is_valid_tag("Has-Upper")  # uppercase
        assert not is_valid_tag("")
        assert not is_valid_tag(None)


class TestChecksumValidation:
    """Test checksum validation."""

    def test_valid_sha256(self):
        checksum = "a" * 64
        assert is_valid_checksum(checksum, "sha256")

    def test_valid_sha1(self):
        checksum = "a" * 40
        assert is_valid_checksum(checksum, "sha1")

    def test_valid_md5(self):
        checksum = "a" * 32
        assert is_valid_checksum(checksum, "md5")

    def test_invalid_checksums(self):
        assert not is_valid_checksum("too-short", "sha256")
        assert not is_valid_checksum("z" * 64, "sha256")  # invalid hex
        assert not is_valid_checksum("", "sha256")
        assert not is_valid_checksum(None, "sha256")


class TestSanitizeInstructionName:
    """Test instruction name sanitization."""

    def test_basic_sanitization(self):
        assert sanitize_instruction_name("Python Best Practices") == "python-best-practices"
        assert sanitize_instruction_name("API_Design") == "api-design"

    def test_remove_invalid_chars(self):
        assert sanitize_instruction_name("test@#$%name") == "test-name"

    def test_collapse_hyphens(self):
        assert sanitize_instruction_name("test---name") == "test-name"

    def test_ensure_starts_with_letter(self):
        assert sanitize_instruction_name("123-test").startswith("inst-")

    def test_truncate_long_names(self):
        long_name = "a" * 100
        sanitized = sanitize_instruction_name(long_name)
        assert len(sanitized) <= 50


class TestFilePathValidation:
    """Test file path validation."""

    def test_valid_paths(self):
        assert validate_file_path("instructions/test.md") is None
        assert validate_file_path("test.md") is None

    def test_directory_traversal(self):
        assert validate_file_path("../test.md") is not None
        assert validate_file_path("test/../other.md") is not None

    def test_absolute_paths(self):
        assert validate_file_path("/absolute/path") is not None
        assert validate_file_path("C:\\absolute") is not None

    def test_unsafe_characters(self):
        assert validate_file_path("test<>.md") is not None
        assert validate_file_path("test|.md") is not None


class TestNormalizeRepoUrl:
    """Test repository URL normalization."""

    def test_remove_trailing_git(self):
        url = "https://github.com/user/repo.git"
        assert normalize_repo_url(url) == "https://github.com/user/repo"

    def test_remove_trailing_slash(self):
        url = "https://github.com/user/repo/"
        assert normalize_repo_url(url) == "https://github.com/user/repo"

    def test_combined_normalization(self):
        url = "https://github.com/user/repo.git/"
        assert normalize_repo_url(url) == "https://github.com/user/repo"
