"""Unit tests for validation utilities."""

from aiconfigkit.utils.validation import (
    is_valid_checksum,
    is_valid_git_url,
    is_valid_instruction_name,
    is_valid_tag,
    normalize_repo_url,
    sanitize_instruction_name,
    validate_file_path,
)


class TestIsValidGitUrl:
    """Test is_valid_git_url function."""

    def test_https_url_valid(self) -> None:
        """Test valid HTTPS URLs."""
        assert is_valid_git_url("https://github.com/user/repo.git") is True
        assert is_valid_git_url("https://github.com/user/repo") is True
        assert is_valid_git_url("http://example.com/repo.git") is True

    def test_https_url_invalid(self) -> None:
        """Test invalid HTTPS URLs."""
        assert is_valid_git_url("https://") is False
        assert is_valid_git_url("https://github.com") is False  # No path

    def test_ssh_url_valid(self) -> None:
        """Test valid SSH URLs."""
        assert is_valid_git_url("git@github.com:user/repo.git") is True
        assert is_valid_git_url("user@host.com:path/to/repo") is True

    def test_ssh_url_invalid(self) -> None:
        """Test invalid SSH format."""
        assert is_valid_git_url("git@github") is False  # No colon
        # Note: "github.com:repo" is treated as valid (local path with colon)

    def test_git_protocol_valid(self) -> None:
        """Test valid git:// protocol URLs."""
        assert is_valid_git_url("git://github.com/user/repo.git") is True

    def test_git_protocol_invalid(self) -> None:
        """Test invalid git:// URLs."""
        assert is_valid_git_url("git://") is False

    def test_file_url_valid(self) -> None:
        """Test file:// URLs."""
        assert is_valid_git_url("file:///path/to/repo") is True

    def test_absolute_path_valid(self) -> None:
        """Test absolute local paths."""
        assert is_valid_git_url("/path/to/repo") is True
        assert is_valid_git_url("/home/user/projects/repo") is True

    def test_relative_path_valid(self) -> None:
        """Test relative local paths."""
        assert is_valid_git_url("./repo") is True
        assert is_valid_git_url("../repo") is True
        assert is_valid_git_url("my-repo") is True
        assert is_valid_git_url("path/to/repo") is True

    def test_empty_or_invalid_input(self) -> None:
        """Test empty or invalid inputs."""
        assert is_valid_git_url("") is False
        assert is_valid_git_url(None) is False  # type: ignore

    def test_urlparse_exception_https(self) -> None:
        """Test exception handling in HTTPS URL parsing."""
        from unittest.mock import patch

        with patch("aiconfigkit.utils.validation.urlparse", side_effect=Exception("Parse error")):
            assert is_valid_git_url("https://example.com/repo.git") is False

    def test_urlparse_exception_git_protocol(self) -> None:
        """Test exception handling in git:// URL parsing."""
        from unittest.mock import patch

        with patch("aiconfigkit.utils.validation.urlparse", side_effect=Exception("Parse error")):
            assert is_valid_git_url("git://example.com/repo.git") is False


class TestIsValidInstructionName:
    """Test is_valid_instruction_name function."""

    def test_valid_names(self) -> None:
        """Test valid instruction names."""
        assert is_valid_instruction_name("my-instruction") is True
        assert is_valid_instruction_name("abc") is True
        assert is_valid_instruction_name("test-123") is True
        assert is_valid_instruction_name("a" * 50) is True  # Max length

    def test_invalid_too_short(self) -> None:
        """Test names that are too short."""
        assert is_valid_instruction_name("a") is False
        assert is_valid_instruction_name("ab") is False

    def test_invalid_too_long(self) -> None:
        """Test names that are too long."""
        assert is_valid_instruction_name("a" * 51) is False

    def test_invalid_uppercase(self) -> None:
        """Test names with uppercase letters."""
        assert is_valid_instruction_name("MyInstruction") is False
        assert is_valid_instruction_name("ABC") is False

    def test_invalid_starts_with_number(self) -> None:
        """Test names starting with number."""
        assert is_valid_instruction_name("123-test") is False

    def test_invalid_starts_with_hyphen(self) -> None:
        """Test names starting with hyphen."""
        assert is_valid_instruction_name("-test") is False

    def test_invalid_special_chars(self) -> None:
        """Test names with invalid characters."""
        assert is_valid_instruction_name("test_name") is False
        assert is_valid_instruction_name("test.name") is False
        assert is_valid_instruction_name("test name") is False

    def test_invalid_empty_or_none(self) -> None:
        """Test empty or None input."""
        assert is_valid_instruction_name("") is False
        assert is_valid_instruction_name(None) is False  # type: ignore


class TestIsValidTag:
    """Test is_valid_tag function."""

    def test_valid_tags(self) -> None:
        """Test valid tags."""
        assert is_valid_tag("python") is True
        assert is_valid_tag("test-tag") is True
        assert is_valid_tag("ab") is True  # Min length
        assert is_valid_tag("a" * 30) is True  # Max length
        assert is_valid_tag("123") is True  # Can start with number

    def test_invalid_too_short(self) -> None:
        """Test tags that are too short."""
        assert is_valid_tag("a") is False

    def test_invalid_too_long(self) -> None:
        """Test tags that are too long."""
        assert is_valid_tag("a" * 31) is False

    def test_invalid_uppercase(self) -> None:
        """Test tags with uppercase."""
        assert is_valid_tag("Python") is False

    def test_invalid_special_chars(self) -> None:
        """Test tags with invalid characters."""
        assert is_valid_tag("test_tag") is False
        assert is_valid_tag("test.tag") is False

    def test_invalid_empty_or_none(self) -> None:
        """Test empty or None input."""
        assert is_valid_tag("") is False
        assert is_valid_tag(None) is False  # type: ignore


class TestIsValidChecksum:
    """Test is_valid_checksum function."""

    def test_valid_sha256(self) -> None:
        """Test valid SHA-256 checksum."""
        valid_sha256 = "a" * 64
        assert is_valid_checksum(valid_sha256, "sha256") is True
        assert is_valid_checksum(valid_sha256.upper(), "sha256") is True  # Case insensitive

    def test_valid_sha1(self) -> None:
        """Test valid SHA-1 checksum."""
        valid_sha1 = "a" * 40
        assert is_valid_checksum(valid_sha1, "sha1") is True

    def test_valid_md5(self) -> None:
        """Test valid MD5 checksum."""
        valid_md5 = "a" * 32
        assert is_valid_checksum(valid_md5, "md5") is True

    def test_invalid_length(self) -> None:
        """Test checksums with wrong length."""
        assert is_valid_checksum("a" * 63, "sha256") is False
        assert is_valid_checksum("a" * 65, "sha256") is False
        assert is_valid_checksum("a" * 39, "sha1") is False
        assert is_valid_checksum("a" * 31, "md5") is False

    def test_invalid_characters(self) -> None:
        """Test checksums with non-hex characters."""
        assert is_valid_checksum("g" * 64, "sha256") is False
        assert is_valid_checksum("z" * 64, "sha256") is False

    def test_invalid_algorithm(self) -> None:
        """Test with unsupported algorithm."""
        assert is_valid_checksum("a" * 64, "sha512") is False

    def test_invalid_empty_or_none(self) -> None:
        """Test empty or None input."""
        assert is_valid_checksum("", "sha256") is False
        assert is_valid_checksum(None, "sha256") is False  # type: ignore


class TestSanitizeInstructionName:
    """Test sanitize_instruction_name function."""

    def test_already_valid(self) -> None:
        """Test sanitizing already valid names."""
        assert sanitize_instruction_name("my-instruction") == "my-instruction"
        assert sanitize_instruction_name("test123") == "test123"

    def test_uppercase_to_lowercase(self) -> None:
        """Test converting uppercase to lowercase."""
        assert sanitize_instruction_name("MyInstruction") == "myinstruction"
        assert sanitize_instruction_name("TEST") == "test"

    def test_replace_invalid_chars(self) -> None:
        """Test replacing invalid characters."""
        assert sanitize_instruction_name("my_instruction") == "my-instruction"
        assert sanitize_instruction_name("test.name") == "test-name"
        assert sanitize_instruction_name("test name") == "test-name"

    def test_remove_leading_trailing_hyphens(self) -> None:
        """Test removing leading/trailing hyphens."""
        assert sanitize_instruction_name("-test-") == "test"
        assert sanitize_instruction_name("--test--") == "test"

    def test_collapse_multiple_hyphens(self) -> None:
        """Test collapsing multiple consecutive hyphens."""
        assert sanitize_instruction_name("test---name") == "test-name"
        assert sanitize_instruction_name("a--b--c") == "a-b-c"

    def test_starts_with_number(self) -> None:
        """Test handling names that start with number."""
        assert sanitize_instruction_name("123test") == "inst-123test"
        assert sanitize_instruction_name("9abc") == "inst-9abc"

    def test_truncate_long_names(self) -> None:
        """Test truncating names longer than 50 chars."""
        long_name = "a" * 60
        result = sanitize_instruction_name(long_name)
        assert len(result) <= 50
        assert result == "a" * 50

    def test_truncate_removes_trailing_hyphen(self) -> None:
        """Test that truncation removes trailing hyphens."""
        long_name = "a" * 49 + "-" + "b" * 10
        result = sanitize_instruction_name(long_name)
        assert len(result) <= 50
        assert not result.endswith("-")


class TestValidateFilePath:
    """Test validate_file_path function."""

    def test_valid_paths(self) -> None:
        """Test valid file paths."""
        assert validate_file_path("file.txt") is None
        assert validate_file_path("path/to/file.txt") is None
        assert validate_file_path("my-file-123.md") is None

    def test_empty_or_none(self) -> None:
        """Test empty or None paths."""
        assert validate_file_path("") == "Path must be a non-empty string"
        assert validate_file_path(None) == "Path must be a non-empty string"  # type: ignore

    def test_directory_traversal(self) -> None:
        """Test paths with directory traversal."""
        assert validate_file_path("../file.txt") == "Path cannot contain '..' (directory traversal)"
        assert validate_file_path("path/../file.txt") == "Path cannot contain '..' (directory traversal)"

    def test_absolute_paths(self) -> None:
        """Test absolute paths."""
        assert validate_file_path("/etc/passwd") == "Path must be relative (not absolute)"
        assert validate_file_path("C:\\Windows\\System32") == "Path must be relative (not absolute)"

    def test_unsafe_characters(self) -> None:
        """Test paths with unsafe characters."""
        assert "unsafe character" in validate_file_path("file<.txt")
        assert "unsafe character" in validate_file_path("file>.txt")
        assert "unsafe character" in validate_file_path("file|.txt")
        assert "unsafe character" in validate_file_path("file\0.txt")


class TestNormalizeRepoUrl:
    """Test normalize_repo_url function."""

    def test_remove_trailing_git(self) -> None:
        """Test removing .git extension."""
        assert normalize_repo_url("https://github.com/user/repo.git") == "https://github.com/user/repo"

    def test_remove_trailing_slashes(self) -> None:
        """Test removing trailing slashes."""
        assert normalize_repo_url("https://github.com/user/repo/") == "https://github.com/user/repo"
        assert normalize_repo_url("https://github.com/user/repo///") == "https://github.com/user/repo"

    def test_remove_both_git_and_slashes(self) -> None:
        """Test removing both .git and slashes."""
        assert normalize_repo_url("https://github.com/user/repo.git/") == "https://github.com/user/repo"

    def test_strip_whitespace(self) -> None:
        """Test stripping whitespace."""
        assert normalize_repo_url("  https://github.com/user/repo  ") == "https://github.com/user/repo"

    def test_no_changes_needed(self) -> None:
        """Test URLs that don't need normalization."""
        url = "https://github.com/user/repo"
        assert normalize_repo_url(url) == url

    def test_complex_normalization(self) -> None:
        """Test complex normalization with all patterns."""
        url = "  https://github.com/user/repo.git///  "
        expected = "https://github.com/user/repo"
        assert normalize_repo_url(url) == expected
