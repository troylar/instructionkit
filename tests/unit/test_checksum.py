"""Unit tests for checksum validation."""

import pytest

from instructionkit.core.checksum import ChecksumError, ChecksumValidator, calculate_file_checksum


class TestChecksumValidator:
    """Test checksum validation."""

    def test_validate_matching_checksum(self):
        """Test validation with matching checksum."""
        validator = ChecksumValidator()
        content = "Hello, World!"

        # Calculate correct checksum
        import hashlib
        expected_checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Should not raise exception
        validator.validate(content, expected_checksum)

    def test_validate_mismatched_checksum(self):
        """Test validation with mismatched checksum."""
        validator = ChecksumValidator()
        content = "Hello, World!"
        wrong_checksum = "0" * 64

        with pytest.raises(ChecksumError, match="Checksum"):
            validator.validate(content, wrong_checksum)

    def test_validate_none_checksum(self):
        """Test validation when checksum is None (should skip validation)."""
        validator = ChecksumValidator()
        content = "Hello, World!"

        # Should not raise exception when checksum is None
        validator.validate(content, None)

    def test_calculate_file_checksum(self, tmp_path):
        """Test calculating checksum from file."""
        test_file = tmp_path / "test.txt"
        content = "Test content for checksum"
        test_file.write_text(content)

        checksum = calculate_file_checksum(test_file)

        # Verify it's a valid SHA-256 hash
        assert len(checksum) == 64
        assert all(c in '0123456789abcdef' for c in checksum)

        # Verify same content gives same checksum
        import hashlib
        expected = hashlib.sha256(content.encode('utf-8')).hexdigest()
        assert checksum == expected

    def test_calculate_checksum_consistent(self, tmp_path):
        """Test that same content always gives same checksum."""
        test_file = tmp_path / "test.txt"
        content = "Consistent content"
        test_file.write_text(content)

        checksum1 = calculate_file_checksum(test_file)
        checksum2 = calculate_file_checksum(test_file)

        assert checksum1 == checksum2

    def test_calculate_checksum_different_content(self, tmp_path):
        """Test that different content gives different checksum."""
        file1 = tmp_path / "test1.txt"
        file2 = tmp_path / "test2.txt"

        file1.write_text("Content 1")
        file2.write_text("Content 2")

        checksum1 = calculate_file_checksum(file1)
        checksum2 = calculate_file_checksum(file2)

        assert checksum1 != checksum2
