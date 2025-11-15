"""Unit tests for checksum module."""

import hashlib
from pathlib import Path

import pytest

from aiconfigkit.core.checksum import (
    ChecksumError,
    ChecksumValidator,
    calculate_checksum,
    calculate_file_checksum,
    sha256_file,
    sha256_string,
    verify_checksum,
    verify_checksum_strict,
    verify_file_checksum,
)


class TestChecksumError:
    """Test ChecksumError exception."""

    def test_exception_creation(self) -> None:
        """Test creating ChecksumError."""
        error = ChecksumError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestCalculateChecksum:
    """Test calculate_checksum function."""

    def test_calculate_sha256(self) -> None:
        """Test calculating SHA-256 checksum."""
        content = "Hello, World!"
        checksum = calculate_checksum(content, "sha256")
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert checksum == expected
        assert len(checksum) == 64  # SHA-256 produces 64 hex characters

    def test_calculate_sha1(self) -> None:
        """Test calculating SHA-1 checksum."""
        content = "Hello, World!"
        checksum = calculate_checksum(content, "sha1")
        expected = hashlib.sha1(content.encode("utf-8")).hexdigest()
        assert checksum == expected
        assert len(checksum) == 40  # SHA-1 produces 40 hex characters

    def test_calculate_md5(self) -> None:
        """Test calculating MD5 checksum."""
        content = "Hello, World!"
        checksum = calculate_checksum(content, "md5")
        expected = hashlib.md5(content.encode("utf-8")).hexdigest()
        assert checksum == expected
        assert len(checksum) == 32  # MD5 produces 32 hex characters

    def test_calculate_default_algorithm(self) -> None:
        """Test that default algorithm is sha256."""
        content = "Test content"
        checksum_default = calculate_checksum(content)
        checksum_sha256 = calculate_checksum(content, "sha256")
        assert checksum_default == checksum_sha256

    def test_calculate_case_insensitive_algorithm(self) -> None:
        """Test that algorithm name is case-insensitive."""
        content = "Test content"
        checksum_lower = calculate_checksum(content, "sha256")
        checksum_upper = calculate_checksum(content, "SHA256")
        checksum_mixed = calculate_checksum(content, "ShA256")
        assert checksum_lower == checksum_upper == checksum_mixed

    def test_calculate_unsupported_algorithm(self) -> None:
        """Test that unsupported algorithm raises error."""
        with pytest.raises(ValueError, match="Unsupported hash algorithm: sha512"):
            calculate_checksum("content", "sha512")

    def test_calculate_empty_string(self) -> None:
        """Test calculating checksum of empty string."""
        checksum = calculate_checksum("")
        # Empty string has a known SHA-256 hash
        expected = hashlib.sha256(b"").hexdigest()
        assert checksum == expected

    def test_calculate_unicode_content(self) -> None:
        """Test calculating checksum with Unicode characters."""
        content = "Hello 世界! 🌍"
        checksum = calculate_checksum(content)
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert checksum == expected


class TestVerifyChecksum:
    """Test verify_checksum function."""

    def test_verify_matching_checksum(self) -> None:
        """Test verifying matching checksum."""
        content = "Test content"
        expected = calculate_checksum(content)
        assert verify_checksum(content, expected) is True

    def test_verify_non_matching_checksum(self) -> None:
        """Test verifying non-matching checksum."""
        content = "Test content"
        wrong_checksum = calculate_checksum("Different content")
        assert verify_checksum(content, wrong_checksum) is False

    def test_verify_case_insensitive(self) -> None:
        """Test that checksum verification is case-insensitive."""
        content = "Test content"
        checksum = calculate_checksum(content)
        assert verify_checksum(content, checksum.upper()) is True
        assert verify_checksum(content, checksum.lower()) is True

    def test_verify_with_different_algorithm(self) -> None:
        """Test verifying with different hash algorithm."""
        content = "Test content"
        expected_md5 = calculate_checksum(content, "md5")
        assert verify_checksum(content, expected_md5, "md5") is True

    def test_verify_wrong_algorithm(self) -> None:
        """Test that wrong algorithm doesn't match."""
        content = "Test content"
        sha256_checksum = calculate_checksum(content, "sha256")
        # Using MD5 algorithm with SHA-256 checksum should fail
        assert verify_checksum(content, sha256_checksum, "md5") is False


class TestVerifyChecksumStrict:
    """Test verify_checksum_strict function."""

    def test_verify_strict_matching(self) -> None:
        """Test strict verification with matching checksum."""
        content = "Test content"
        expected = calculate_checksum(content)
        # Should not raise error
        verify_checksum_strict(content, expected)

    def test_verify_strict_non_matching_raises_error(self) -> None:
        """Test strict verification raises error on mismatch."""
        content = "Test content"
        wrong_checksum = calculate_checksum("Different content")

        with pytest.raises(ChecksumError, match="Checksum mismatch"):
            verify_checksum_strict(content, wrong_checksum)

    def test_verify_strict_error_includes_checksums(self) -> None:
        """Test that error message includes expected and actual checksums."""
        content = "Test content"
        wrong_checksum = "a" * 64

        try:
            verify_checksum_strict(content, wrong_checksum)
            pytest.fail("Should have raised ChecksumError")
        except ChecksumError as e:
            error_msg = str(e)
            assert wrong_checksum in error_msg
            assert calculate_checksum(content) in error_msg


class TestCalculateFileChecksum:
    """Test calculate_file_checksum function."""

    def test_calculate_file_sha256(self, tmp_path: Path) -> None:
        """Test calculating file checksum."""
        test_file = tmp_path / "test.txt"
        content = "Hello, World!"
        test_file.write_text(content)

        checksum = calculate_file_checksum(str(test_file))
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert checksum == expected

    def test_calculate_file_different_algorithms(self, tmp_path: Path) -> None:
        """Test file checksum with different algorithms."""
        test_file = tmp_path / "test.txt"
        content = "Test content"
        test_file.write_bytes(content.encode("utf-8"))

        sha256_sum = calculate_file_checksum(str(test_file), "sha256")
        sha1_sum = calculate_file_checksum(str(test_file), "sha1")
        md5_sum = calculate_file_checksum(str(test_file), "md5")

        assert len(sha256_sum) == 64
        assert len(sha1_sum) == 40
        assert len(md5_sum) == 32

    def test_calculate_file_nonexistent(self, tmp_path: Path) -> None:
        """Test calculating checksum of nonexistent file."""
        nonexistent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            calculate_file_checksum(str(nonexistent))

    def test_calculate_file_empty(self, tmp_path: Path) -> None:
        """Test calculating checksum of empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        checksum = calculate_file_checksum(str(test_file))
        expected = hashlib.sha256(b"").hexdigest()
        assert checksum == expected

    def test_calculate_file_large(self, tmp_path: Path) -> None:
        """Test calculating checksum of large file (tests chunking)."""
        test_file = tmp_path / "large.txt"
        # Create file larger than chunk size (8192 bytes)
        content = "x" * 20000
        test_file.write_text(content)

        checksum = calculate_file_checksum(str(test_file))
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert checksum == expected

    def test_calculate_file_binary(self, tmp_path: Path) -> None:
        """Test calculating checksum of binary file."""
        test_file = tmp_path / "binary.dat"
        binary_content = bytes(range(256))
        test_file.write_bytes(binary_content)

        checksum = calculate_file_checksum(str(test_file))
        expected = hashlib.sha256(binary_content).hexdigest()
        assert checksum == expected

    def test_calculate_file_unsupported_algorithm(self, tmp_path: Path) -> None:
        """Test that unsupported algorithm raises error."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            calculate_file_checksum(str(test_file), "sha512")


class TestVerifyFileChecksum:
    """Test verify_file_checksum function."""

    def test_verify_file_matching(self, tmp_path: Path) -> None:
        """Test verifying file with matching checksum."""
        test_file = tmp_path / "test.txt"
        content = "Test content"
        test_file.write_text(content)

        expected = calculate_file_checksum(str(test_file))
        assert verify_file_checksum(str(test_file), expected) is True

    def test_verify_file_non_matching(self, tmp_path: Path) -> None:
        """Test verifying file with non-matching checksum."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        wrong_checksum = "a" * 64
        assert verify_file_checksum(str(test_file), wrong_checksum) is False

    def test_verify_file_case_insensitive(self, tmp_path: Path) -> None:
        """Test file verification is case-insensitive."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        checksum = calculate_file_checksum(str(test_file))
        assert verify_file_checksum(str(test_file), checksum.upper()) is True
        assert verify_file_checksum(str(test_file), checksum.lower()) is True


class TestChecksumValidator:
    """Test ChecksumValidator class."""

    def test_validator_init_defaults(self) -> None:
        """Test validator initialization with defaults."""
        validator = ChecksumValidator()
        assert validator.algorithm == "sha256"
        assert validator.strict is True

    def test_validator_init_custom(self) -> None:
        """Test validator initialization with custom values."""
        validator = ChecksumValidator(algorithm="md5", strict=False)
        assert validator.algorithm == "md5"
        assert validator.strict is False

    def test_validator_valid_checksum(self) -> None:
        """Test validation with valid checksum."""
        content = "Test content"
        expected = calculate_checksum(content)

        validator = ChecksumValidator()
        assert validator.validate(content, expected) is True

    def test_validator_invalid_checksum_strict(self) -> None:
        """Test validation with invalid checksum in strict mode."""
        content = "Test content"
        wrong_checksum = "a" * 64

        validator = ChecksumValidator(strict=True)
        with pytest.raises(ChecksumError, match="Checksum validation failed"):
            validator.validate(content, wrong_checksum)

    def test_validator_invalid_checksum_non_strict(self) -> None:
        """Test validation with invalid checksum in non-strict mode."""
        content = "Test content"
        wrong_checksum = "a" * 64

        validator = ChecksumValidator(strict=False)
        assert validator.validate(content, wrong_checksum) is False

    def test_validator_none_checksum(self) -> None:
        """Test validation with None checksum (skip validation)."""
        content = "Test content"

        validator_strict = ChecksumValidator(strict=True)
        validator_non_strict = ChecksumValidator(strict=False)

        # Both should return True when checksum is None
        assert validator_strict.validate(content, None) is True
        assert validator_non_strict.validate(content, None) is True

    def test_validator_different_algorithm(self) -> None:
        """Test validator with different algorithm."""
        content = "Test content"
        expected_md5 = calculate_checksum(content, "md5")

        validator = ChecksumValidator(algorithm="md5")
        assert validator.validate(content, expected_md5) is True

    def test_validator_strict_error_message(self) -> None:
        """Test that strict mode error includes helpful information."""
        content = "Test content"
        wrong_checksum = "a" * 64

        validator = ChecksumValidator(algorithm="sha256", strict=True)

        try:
            validator.validate(content, wrong_checksum)
            pytest.fail("Should have raised ChecksumError")
        except ChecksumError as e:
            error_msg = str(e)
            assert "Checksum validation failed" in error_msg
            assert wrong_checksum in error_msg
            assert "sha256" in error_msg


class TestSHA256File:
    """Test sha256_file function."""

    def test_sha256_file_basic(self, tmp_path: Path) -> None:
        """Test SHA-256 file checksum calculation."""
        test_file = tmp_path / "test.txt"
        content = "Test content"
        test_file.write_text(content)

        checksum = sha256_file(test_file)
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert checksum == expected
        assert len(checksum) == 64

    def test_sha256_file_path_object(self, tmp_path: Path) -> None:
        """Test that sha256_file accepts Path objects."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Should accept Path object
        checksum = sha256_file(test_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64

    def test_sha256_file_matches_calculate_file_checksum(self, tmp_path: Path) -> None:
        """Test that sha256_file matches calculate_file_checksum."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        checksum1 = sha256_file(test_file)
        checksum2 = calculate_file_checksum(str(test_file), "sha256")
        assert checksum1 == checksum2


class TestSHA256String:
    """Test sha256_string function."""

    def test_sha256_string_basic(self) -> None:
        """Test SHA-256 string checksum calculation."""
        content = "Test content"
        checksum = sha256_string(content)
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert checksum == expected
        assert len(checksum) == 64

    def test_sha256_string_empty(self) -> None:
        """Test SHA-256 of empty string."""
        checksum = sha256_string("")
        expected = hashlib.sha256(b"").hexdigest()
        assert checksum == expected

    def test_sha256_string_unicode(self) -> None:
        """Test SHA-256 with Unicode content."""
        content = "Hello 世界! 🌍"
        checksum = sha256_string(content)
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert checksum == expected

    def test_sha256_string_matches_calculate_checksum(self) -> None:
        """Test that sha256_string matches calculate_checksum."""
        content = "Test content"
        checksum1 = sha256_string(content)
        checksum2 = calculate_checksum(content, "sha256")
        assert checksum1 == checksum2
