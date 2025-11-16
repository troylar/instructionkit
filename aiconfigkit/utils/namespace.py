"""Namespace utilities for template repositories."""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


def extract_repo_name_from_url(repo_url: str) -> str:
    """
    Extract repository name from Git URL.

    Handles both HTTPS and SSH URLs.

    Args:
        repo_url: Git repository URL

    Returns:
        Repository name (e.g., "coding-standards" from "github.com/org/coding-standards")

    Examples:
        >>> extract_repo_name_from_url("https://github.com/acme/coding-standards")
        'coding-standards'
        >>> extract_repo_name_from_url("git@github.com:acme/coding-standards.git")
        'coding-standards'
        >>> extract_repo_name_from_url("https://github.com/acme/coding-standards.git")
        'coding-standards'
    """
    # Handle SSH URLs (git@github.com:org/repo.git)
    if repo_url.startswith("git@"):
        # Extract the path after the colon
        _, _, path = repo_url.partition(":")
        repo_name = path.rstrip(".git").split("/")[-1]
        return repo_name

    # Handle HTTPS URLs
    parsed = urlparse(repo_url)
    path = parsed.path.strip("/")

    # Remove .git suffix if present
    if path.endswith(".git"):
        path = path[:-4]

    # Get the last component (repository name)
    repo_name = path.split("/")[-1]

    return repo_name


def derive_namespace(repo_url: str, override: Optional[str] = None) -> str:
    """
    Derive namespace from repository URL or use override.

    Always returns a valid namespace. If override provided, validates and returns it.
    Otherwise, derives from repository URL.

    Args:
        repo_url: Git repository URL
        override: Optional namespace override

    Returns:
        Valid namespace string

    Raises:
        ValueError: If override is invalid (empty or contains invalid characters)

    Examples:
        >>> derive_namespace("https://github.com/acme/coding-standards")
        'coding-standards'
        >>> derive_namespace("https://github.com/acme/coding-standards", "acme")
        'acme'
    """
    if override:
        # Validate override namespace
        if not override.strip():
            raise ValueError("Namespace override cannot be empty")

        # Namespace must be alphanumeric with hyphens only
        if not re.match(r"^[a-zA-Z0-9-]+$", override):
            raise ValueError(f"Invalid namespace '{override}': must contain only alphanumeric characters and hyphens")

        if len(override) > 50:
            raise ValueError(f"Namespace '{override}' exceeds maximum length of 50 characters")

        return override

    # Derive from repository URL
    return extract_repo_name_from_url(repo_url)


def get_install_path(namespace: str, template_name: str, ide_base_path: Path, extension: str) -> Path:
    """
    Construct namespaced installation path using dot notation.

    Format: {ide_base_path}/{namespace}.{template-name}.{ext}

    Args:
        namespace: Repository namespace
        template_name: Template identifier
        ide_base_path: Base directory for IDE templates (e.g., .cursor/rules/)
        extension: File extension (e.g., "md", "mdc")

    Returns:
        Full installation path

    Examples:
        >>> from pathlib import Path
        >>> path = get_install_path("acme", "test-command", Path(".cursor/rules"), "md")
        >>> str(path)
        '.cursor/rules/acme.test-command.md'
    """
    # Construct namespaced filename: namespace.template-name.ext
    filename = f"{namespace}.{template_name}.{extension}"
    return ide_base_path / filename


def validate_namespace(namespace: str) -> None:
    """
    Validate namespace format.

    Args:
        namespace: Namespace to validate

    Raises:
        ValueError: If namespace is invalid
    """
    if not namespace.strip():
        raise ValueError("Namespace cannot be empty")

    if not re.match(r"^[a-zA-Z0-9-]+$", namespace):
        raise ValueError(f"Invalid namespace '{namespace}': must contain only alphanumeric characters and hyphens")

    if len(namespace) > 50:
        raise ValueError(f"Namespace '{namespace}' exceeds maximum length of 50 characters")
