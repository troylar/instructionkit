"""Checksum verification for instruction files."""

import hashlib
from typing import Optional


class ChecksumError(Exception):
    """Raised when checksum verification fails."""
    pass


def calculate_checksum(content: str, algorithm: str = 'sha256') -> str:
    """
    Calculate checksum of content.

    Args:
        content: Content to hash
        algorithm: Hash algorithm (sha256, sha1, md5)

    Returns:
        Hex digest of checksum

    Raises:
        ValueError: If algorithm is not supported
    """
    algorithms = {
        'sha256': hashlib.sha256,
        'sha1': hashlib.sha1,
        'md5': hashlib.md5,
    }

    if algorithm.lower() not in algorithms:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    hash_func = algorithms[algorithm.lower()]
    return hash_func(content.encode('utf-8')).hexdigest()


def verify_checksum(
    content: str,
    expected_checksum: str,
    algorithm: str = 'sha256'
) -> bool:
    """
    Verify content matches expected checksum.

    Args:
        content: Content to verify
        expected_checksum: Expected checksum value
        algorithm: Hash algorithm used

    Returns:
        True if checksum matches
    """
    actual_checksum = calculate_checksum(content, algorithm)
    return actual_checksum.lower() == expected_checksum.lower()


def verify_checksum_strict(
    content: str,
    expected_checksum: str,
    algorithm: str = 'sha256'
) -> None:
    """
    Verify content matches expected checksum, raise on mismatch.

    Args:
        content: Content to verify
        expected_checksum: Expected checksum value
        algorithm: Hash algorithm used

    Raises:
        ChecksumError: If checksum does not match
    """
    if not verify_checksum(content, expected_checksum, algorithm):
        actual = calculate_checksum(content, algorithm)
        raise ChecksumError(
            f"Checksum mismatch! Expected: {expected_checksum}, "
            f"Actual: {actual}"
        )


def calculate_file_checksum(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate checksum of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, sha1, md5)

    Returns:
        Hex digest of checksum

    Raises:
        ValueError: If algorithm is not supported
        FileNotFoundError: If file does not exist
    """
    algorithms = {
        'sha256': hashlib.sha256,
        'sha1': hashlib.sha1,
        'md5': hashlib.md5,
    }

    if algorithm.lower() not in algorithms:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    hash_func = algorithms[algorithm.lower()]()

    with open(file_path, 'rb') as f:
        # Read file in chunks for memory efficiency
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def verify_file_checksum(
    file_path: str,
    expected_checksum: str,
    algorithm: str = 'sha256'
) -> bool:
    """
    Verify file matches expected checksum.

    Args:
        file_path: Path to file
        expected_checksum: Expected checksum value
        algorithm: Hash algorithm used

    Returns:
        True if checksum matches
    """
    actual_checksum = calculate_file_checksum(file_path, algorithm)
    return actual_checksum.lower() == expected_checksum.lower()


class ChecksumValidator:
    """Helper class for checksum validation with configuration."""

    def __init__(self, algorithm: str = 'sha256', strict: bool = True):
        """
        Initialize validator.

        Args:
            algorithm: Hash algorithm to use
            strict: Whether to raise exceptions on mismatch
        """
        self.algorithm = algorithm
        self.strict = strict

    def validate(self, content: str, expected_checksum: Optional[str]) -> bool:
        """
        Validate content against expected checksum.

        Args:
            content: Content to validate
            expected_checksum: Expected checksum (None to skip validation)

        Returns:
            True if valid or checksum not provided

        Raises:
            ChecksumError: If strict mode and checksum mismatch
        """
        # Skip validation if no checksum provided
        if expected_checksum is None:
            return True

        matches = verify_checksum(content, expected_checksum, self.algorithm)

        if not matches and self.strict:
            actual = calculate_checksum(content, self.algorithm)
            raise ChecksumError(
                f"Checksum validation failed!\n"
                f"Expected: {expected_checksum}\n"
                f"Actual:   {actual}\n"
                f"Algorithm: {self.algorithm}"
            )

        return matches
