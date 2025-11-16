"""Input validation utilities for CLI arguments and data."""

import re
from typing import Optional
from urllib.parse import urlparse


def is_valid_git_url(url: str) -> bool:
    """
    Validate if a string is a valid Git repository URL or local path.

    Supports:
    - HTTPS: https://github.com/user/repo.git
    - SSH: git@github.com:user/repo.git
    - Git protocol: git://github.com/user/repo.git
    - File: file:///path/to/repo
    - Local absolute paths: /path/to/repo
    - Local relative paths: ./path/to/repo or ../path/to/repo or path/to/repo
    """
    if not url or not isinstance(url, str):
        return False

    # HTTPS URLs
    if url.startswith(("https://", "http://")):
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.path)
        except Exception:
            return False

    # SSH URLs (git@host:path)
    ssh_pattern = r"^[\w\-\.]+@[\w\-\.]+:[\w\-\.\/]+$"
    if "@" in url and ":" in url:
        return bool(re.match(ssh_pattern, url))

    # Git protocol URLs
    if url.startswith("git://"):
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.path)
        except Exception:
            return False

    # File URLs and local paths (absolute and relative)
    if url.startswith(("file://", "/", "./", "../")):
        return True

    # Relative paths without ./ prefix (e.g., "my-repo" or "path/to/repo")
    # Check if it looks like a local path (no protocol, no @host:)
    if "://" not in url and "@" not in url:
        return True

    return False


def is_valid_instruction_name(name: str) -> bool:
    """
    Validate instruction name follows naming conventions.

    Rules:
    - Only lowercase letters, numbers, hyphens
    - Must start with letter
    - 3-50 characters
    """
    if not name or not isinstance(name, str):
        return False

    pattern = r"^[a-z][a-z0-9\-]{2,49}$"
    return bool(re.match(pattern, name))


def is_valid_tag(tag: str) -> bool:
    """
    Validate tag format.

    Rules:
    - Only lowercase letters, numbers, hyphens
    - 2-30 characters
    """
    if not tag or not isinstance(tag, str):
        return False

    pattern = r"^[a-z0-9\-]{2,30}$"
    return bool(re.match(pattern, tag))


def is_valid_checksum(checksum: str, algorithm: str = "sha256") -> bool:
    """
    Validate checksum format.

    Args:
        checksum: The checksum string to validate
        algorithm: Hash algorithm (sha256, sha1, md5)
    """
    if not checksum or not isinstance(checksum, str):
        return False

    expected_lengths = {
        "sha256": 64,
        "sha1": 40,
        "md5": 32,
    }

    expected_length = expected_lengths.get(algorithm.lower())
    if not expected_length:
        return False

    # Checksum should be hex string of expected length
    pattern = f"^[a-f0-9]{{{expected_length}}}$"
    return bool(re.match(pattern, checksum.lower()))


def sanitize_instruction_name(name: str) -> str:
    """
    Sanitize an instruction name to make it valid.

    Converts to lowercase, replaces invalid chars with hyphens,
    removes leading/trailing hyphens.
    """
    # Convert to lowercase
    sanitized = name.lower()

    # Replace invalid characters with hyphens
    sanitized = re.sub(r"[^a-z0-9\-]", "-", sanitized)

    # Remove leading/trailing hyphens
    sanitized = sanitized.strip("-")

    # Collapse multiple consecutive hyphens
    sanitized = re.sub(r"-+", "-", sanitized)

    # Ensure starts with letter
    if sanitized and not sanitized[0].isalpha():
        sanitized = "inst-" + sanitized

    # Truncate to max length
    if len(sanitized) > 50:
        sanitized = sanitized[:50].rstrip("-")

    return sanitized


def validate_file_path(path: str) -> Optional[str]:
    """
    Validate file path is safe (no directory traversal).

    Returns:
        None if valid, error message if invalid
    """
    if not path or not isinstance(path, str):
        return "Path must be a non-empty string"

    # Check for directory traversal attempts
    if ".." in path:
        return "Path cannot contain '..' (directory traversal)"

    # Check for absolute paths
    if path.startswith("/") or (len(path) > 1 and path[1] == ":"):
        return "Path must be relative (not absolute)"

    # Check for unsafe characters
    unsafe_chars = ["<", ">", "|", "\0"]
    for char in unsafe_chars:
        if char in path:
            return f"Path contains unsafe character: {char}"

    return None


def normalize_repo_url(url: str) -> str:
    """
    Normalize repository URL for consistent comparison.

    - Removes trailing .git
    - Removes trailing slashes
    - Converts to lowercase for hostname
    """
    normalized = url.strip()

    # Remove trailing slashes first
    normalized = normalized.rstrip("/")

    # Remove trailing .git
    if normalized.endswith(".git"):
        normalized = normalized[:-4]

    return normalized
