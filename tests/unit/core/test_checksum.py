"""Unit tests for checksum utilities."""

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


class TestCalculateChecksum:
    """Test checksum calculation for strings."""

    def test_sha256_checksum(self) -> None:
        """Test SHA-256 checksum calculation."""
        content = "Hello, world!"
        checksum = calculate_checksum(content, "sha256")

        # Verify it's a 64-character hex string (SHA-256)
        assert len(checksum) == 64
        assert all(c in "0123456789abcdef" for c in checksum)

    def test_sha1_checksum(self) -> None:
        """Test SHA-1 checksum calculation."""
        content = "Hello, world!"
        checksum = calculate_checksum(content, "sha1")

        # Verify it's a 40-character hex string (SHA-1)
        assert len(checksum) == 40
        assert all(c in "0123456789abcdef" for c in checksum)

    def test_md5_checksum(self) -> None:
        """Test MD5 checksum calculation."""
        content = "Hello, world!"
        checksum = calculate_checksum(content, "md5")

        # Verify it's a 32-character hex string (MD5)
        assert len(checksum) == 32
        assert all(c in "0123456789abcdef" for c in checksum)

    def test_default_algorithm_is_sha256(self) -> None:
        """Test that default algorithm is SHA-256."""
        content = "Test content"
        checksum_default = calculate_checksum(content)
        checksum_sha256 = calculate_checksum(content, "sha256")

        assert checksum_default == checksum_sha256

    def test_different_content_different_checksum(self) -> None:
        """Test that different content produces different checksums."""
        content1 = "Content A"
        content2 = "Content B"

        checksum1 = calculate_checksum(content1)
        checksum2 = calculate_checksum(content2)

        assert checksum1 != checksum2

    def test_same_content_same_checksum(self) -> None:
        """Test that same content produces same checksum."""
        content = "Same content"

        checksum1 = calculate_checksum(content)
        checksum2 = calculate_checksum(content)

        assert checksum1 == checksum2

    def test_case_insensitive_algorithm(self) -> None:
        """Test that algorithm name is case-insensitive."""
        content = "Test"

        checksum_lower = calculate_checksum(content, "sha256")
        checksum_upper = calculate_checksum(content, "SHA256")
        checksum_mixed = calculate_checksum(content, "Sha256")

        assert checksum_lower == checksum_upper == checksum_mixed

    def test_unsupported_algorithm_raises_error(self) -> None:
        """Test that unsupported algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            calculate_checksum("test", "unsupported")

    def test_empty_string(self) -> None:
        """Test checksum of empty string."""
        checksum = calculate_checksum("")
        assert len(checksum) == 64  # SHA-256 produces 64 chars

    def test_unicode_content(self) -> None:
        """Test checksum of Unicode content."""
        content = "Hello, 世界! 🌍"
        checksum = calculate_checksum(content)
        assert len(checksum) == 64

    def test_multiline_content(self) -> None:
        """Test checksum of multiline content."""
        content = """Line 1
Line 2
Line 3"""
        checksum = calculate_checksum(content)
        assert len(checksum) == 64


class TestVerifyChecksum:
    """Test checksum verification."""

    def test_verify_correct_checksum(self) -> None:
        """Test verification of correct checksum."""
        content = "Test content"
        checksum = calculate_checksum(content)

        assert verify_checksum(content, checksum) is True

    def test_verify_incorrect_checksum(self) -> None:
        """Test verification of incorrect checksum."""
        content = "Test content"
        wrong_checksum = "0" * 64

        assert verify_checksum(content, wrong_checksum) is False

    def test_verify_case_insensitive(self) -> None:
        """Test that checksum verification is case-insensitive."""
        content = "Test"
        checksum = calculate_checksum(content)

        assert verify_checksum(content, checksum.upper()) is True
        assert verify_checksum(content, checksum.lower()) is True

    def test_verify_with_different_algorithm(self) -> None:
        """Test verification with different hash algorithms."""
        content = "Test content"

        sha256_checksum = calculate_checksum(content, "sha256")
        sha1_checksum = calculate_checksum(content, "sha1")
        md5_checksum = calculate_checksum(content, "md5")

        assert verify_checksum(content, sha256_checksum, "sha256") is True
        assert verify_checksum(content, sha1_checksum, "sha1") is True
        assert verify_checksum(content, md5_checksum, "md5") is True


class TestVerifyChecksumStrict:
    """Test strict checksum verification."""

    def test_verify_strict_correct_checksum(self) -> None:
        """Test strict verification of correct checksum."""
        content = "Test content"
        checksum = calculate_checksum(content)

        # Should not raise
        verify_checksum_strict(content, checksum)

    def test_verify_strict_incorrect_checksum_raises(self) -> None:
        """Test strict verification of incorrect checksum raises."""
        content = "Test content"
        wrong_checksum = "0" * 64

        with pytest.raises(ChecksumError, match="Checksum mismatch"):
            verify_checksum_strict(content, wrong_checksum)

    def test_verify_strict_shows_expected_and_actual(self) -> None:
        """Test that error message shows expected and actual checksums."""
        content = "Test content"
        wrong_checksum = "0" * 64

        with pytest.raises(ChecksumError) as exc_info:
            verify_checksum_strict(content, wrong_checksum)

        error_msg = str(exc_info.value)
        assert "Expected:" in error_msg
        assert "Actual:" in error_msg
        assert wrong_checksum in error_msg


class TestCalculateFileChecksum:
    """Test file checksum calculation."""

    def test_calculate_file_checksum(self, tmp_path: Path) -> None:
        """Test calculating checksum of a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("File content")

        checksum = calculate_file_checksum(str(test_file))
        assert len(checksum) == 64

    def test_file_checksum_matches_content_checksum(self, tmp_path: Path) -> None:
        """Test that file checksum matches content checksum."""
        content = "Test content"
        test_file = tmp_path / "test.txt"
        test_file.write_text(content)

        file_checksum = calculate_file_checksum(str(test_file))
        content_checksum = calculate_checksum(content)

        assert file_checksum == content_checksum

    def test_different_files_different_checksums(self, tmp_path: Path) -> None:
        """Test that different files produce different checksums."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"

        file1.write_text("Content A")
        file2.write_text("Content B")

        checksum1 = calculate_file_checksum(str(file1))
        checksum2 = calculate_file_checksum(str(file2))

        assert checksum1 != checksum2

    def test_file_checksum_with_algorithm(self, tmp_path: Path) -> None:
        """Test file checksum with different algorithms."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")

        sha256 = calculate_file_checksum(str(test_file), "sha256")
        sha1 = calculate_file_checksum(str(test_file), "sha1")
        md5 = calculate_file_checksum(str(test_file), "md5")

        assert len(sha256) == 64
        assert len(sha1) == 40
        assert len(md5) == 32

    def test_file_not_found_raises_error(self) -> None:
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            calculate_file_checksum("/nonexistent/file.txt")

    def test_unsupported_algorithm_raises_error(self, tmp_path: Path) -> None:
        """Test that unsupported algorithm raises ValueError."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")

        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            calculate_file_checksum(str(test_file), "unsupported")

    def test_binary_file_checksum(self, tmp_path: Path) -> None:
        """Test checksum of binary file."""
        test_file = tmp_path / "binary.dat"
        test_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe\xfd")

        checksum = calculate_file_checksum(str(test_file))
        assert len(checksum) == 64

    def test_large_file_checksum(self, tmp_path: Path) -> None:
        """Test checksum of large file (tests chunked reading)."""
        test_file = tmp_path / "large.txt"

        # Create file larger than chunk size (8192 bytes)
        large_content = "x" * 10000
        test_file.write_text(large_content)

        checksum = calculate_file_checksum(str(test_file))
        assert len(checksum) == 64

    def test_empty_file_checksum(self, tmp_path: Path) -> None:
        """Test checksum of empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        checksum = calculate_file_checksum(str(test_file))
        assert len(checksum) == 64


class TestVerifyFileChecksum:
    """Test file checksum verification."""

    def test_verify_correct_file_checksum(self, tmp_path: Path) -> None:
        """Test verification of correct file checksum."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        checksum = calculate_file_checksum(str(test_file))
        assert verify_file_checksum(str(test_file), checksum) is True

    def test_verify_incorrect_file_checksum(self, tmp_path: Path) -> None:
        """Test verification of incorrect file checksum."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        wrong_checksum = "0" * 64
        assert verify_file_checksum(str(test_file), wrong_checksum) is False

    def test_verify_file_checksum_case_insensitive(self, tmp_path: Path) -> None:
        """Test that file checksum verification is case-insensitive."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")

        checksum = calculate_file_checksum(str(test_file))
        assert verify_file_checksum(str(test_file), checksum.upper()) is True


class TestChecksumValidator:
    """Test ChecksumValidator class."""

    def test_validator_default_algorithm(self) -> None:
        """Test validator with default algorithm."""
        validator = ChecksumValidator()
        assert validator.algorithm == "sha256"

    def test_validator_custom_algorithm(self) -> None:
        """Test validator with custom algorithm."""
        validator = ChecksumValidator(algorithm="sha1")
        assert validator.algorithm == "sha1"

    def test_validator_strict_mode_default(self) -> None:
        """Test validator strict mode is True by default."""
        validator = ChecksumValidator()
        assert validator.strict is True

    def test_validator_non_strict_mode(self) -> None:
        """Test validator with strict=False."""
        validator = ChecksumValidator(strict=False)
        assert validator.strict is False

    def test_validate_correct_checksum(self) -> None:
        """Test validation of correct checksum."""
        content = "Test content"
        checksum = calculate_checksum(content)

        validator = ChecksumValidator()
        assert validator.validate(content, checksum) is True

    def test_validate_incorrect_checksum_strict_mode(self) -> None:
        """Test validation of incorrect checksum in strict mode raises."""
        content = "Test content"
        wrong_checksum = "0" * 64

        validator = ChecksumValidator(strict=True)
        with pytest.raises(ChecksumError, match="Checksum validation failed"):
            validator.validate(content, wrong_checksum)

    def test_validate_incorrect_checksum_non_strict_mode(self) -> None:
        """Test validation of incorrect checksum in non-strict mode."""
        content = "Test content"
        wrong_checksum = "0" * 64

        validator = ChecksumValidator(strict=False)
        assert validator.validate(content, wrong_checksum) is False

    def test_validate_none_checksum_returns_true(self) -> None:
        """Test that None checksum skips validation."""
        content = "Test content"

        validator = ChecksumValidator()
        assert validator.validate(content, None) is True

    def test_validate_with_different_algorithm(self) -> None:
        """Test validation with different hash algorithm."""
        content = "Test content"
        checksum = calculate_checksum(content, "sha1")

        validator = ChecksumValidator(algorithm="sha1")
        assert validator.validate(content, checksum) is True

    def test_validate_error_message_includes_details(self) -> None:
        """Test that validation error includes expected, actual, and algorithm."""
        content = "Test"
        wrong_checksum = "0" * 64

        validator = ChecksumValidator(algorithm="sha256")
        with pytest.raises(ChecksumError) as exc_info:
            validator.validate(content, wrong_checksum)

        error_msg = str(exc_info.value)
        assert "Expected:" in error_msg
        assert "Actual:" in error_msg
        assert "Algorithm:" in error_msg
        assert "sha256" in error_msg


class TestTemplateHelpers:
    """Test template-specific helper functions."""

    def test_sha256_string(self) -> None:
        """Test SHA-256 string helper."""
        content = "Hello, world!"
        checksum = sha256_string(content)

        # Should match calculate_checksum with sha256
        expected = calculate_checksum(content, "sha256")
        assert checksum == expected
        assert len(checksum) == 64

    def test_sha256_file(self, tmp_path: Path) -> None:
        """Test SHA-256 file helper."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("File content")

        checksum = sha256_file(test_file)

        # Should match calculate_file_checksum with sha256
        expected = calculate_file_checksum(str(test_file), "sha256")
        assert checksum == expected
        assert len(checksum) == 64

    def test_sha256_file_accepts_path_object(self, tmp_path: Path) -> None:
        """Test that sha256_file accepts Path object."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")

        # Should accept Path object (not just string)
        checksum = sha256_file(test_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64

    def test_sha256_helpers_consistency(self, tmp_path: Path) -> None:
        """Test that string and file helpers produce same result."""
        content = "Test content"

        # Calculate using string helper
        string_checksum = sha256_string(content)

        # Write to file and calculate using file helper
        test_file = tmp_path / "test.txt"
        test_file.write_text(content)
        file_checksum = sha256_file(test_file)

        assert string_checksum == file_checksum


class TestChecksumError:
    """Test ChecksumError exception."""

    def test_checksum_error_is_exception(self) -> None:
        """Test that ChecksumError is an Exception."""
        error = ChecksumError("Test error")
        assert isinstance(error, Exception)

    def test_checksum_error_message(self) -> None:
        """Test ChecksumError message."""
        message = "Checksum failed"
        error = ChecksumError(message)
        assert str(error) == message

    def test_raise_checksum_error(self) -> None:
        """Test raising ChecksumError."""
        with pytest.raises(ChecksumError, match="Test"):
            raise ChecksumError("Test")


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_very_long_content(self) -> None:
        """Test checksum of very long content."""
        content = "x" * 1000000  # 1MB of 'x'
        checksum = calculate_checksum(content)
        assert len(checksum) == 64

    def test_special_characters(self) -> None:
        """Test checksum of content with special characters."""
        content = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        checksum = calculate_checksum(content)
        assert len(checksum) == 64

    def test_newline_variations(self) -> None:
        """Test that different newline styles produce different checksums."""
        content_lf = "Line1\nLine2"
        content_crlf = "Line1\r\nLine2"
        content_cr = "Line1\rLine2"

        checksum_lf = calculate_checksum(content_lf)
        checksum_crlf = calculate_checksum(content_crlf)
        checksum_cr = calculate_checksum(content_cr)

        # All should be different
        assert checksum_lf != checksum_crlf
        assert checksum_lf != checksum_cr
        assert checksum_crlf != checksum_cr

    def test_whitespace_sensitivity(self) -> None:
        """Test that checksums are sensitive to whitespace."""
        content1 = "Hello World"
        content2 = "Hello  World"  # Extra space
        content3 = "Hello World "  # Trailing space

        checksum1 = calculate_checksum(content1)
        checksum2 = calculate_checksum(content2)
        checksum3 = calculate_checksum(content3)

        # All should be different
        assert checksum1 != checksum2
        assert checksum1 != checksum3
        assert checksum2 != checksum3
