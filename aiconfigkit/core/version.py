"""Semantic version management for packages."""

import subprocess
from pathlib import Path
from typing import Optional

from packaging.version import InvalidVersion, Version
from packaging.version import parse as parse_version


class VersionError(Exception):
    """Raised when version operations fail."""

    pass


class VersionManager:
    """
    Manager for semantic versioning operations.

    Handles parsing, comparison, and validation of package versions
    using semantic versioning (major.minor.patch).
    """

    def __init__(self, repository_path: Optional[Path] = None):
        """
        Initialize version manager.

        Args:
            repository_path: Path to Git repository for querying versions from tags
        """
        self.repository_path = repository_path

    def parse(self, version_string: str) -> Version:
        """
        Parse version string into Version object.

        Args:
            version_string: Version string (e.g., "1.0.0", "v2.1.3")

        Returns:
            Version object

        Raises:
            VersionError: If version string is invalid
        """
        # Strip leading 'v' if present
        if version_string.startswith("v"):
            version_string = version_string[1:]

        try:
            return parse_version(version_string)
        except InvalidVersion as e:
            raise VersionError(f"Invalid version string '{version_string}': {e}")

    def compare(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2

        Raises:
            VersionError: If either version string is invalid
        """
        v1 = self.parse(version1)
        v2 = self.parse(version2)

        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0

    def is_compatible(self, required_version: str, available_version: str) -> bool:
        """
        Check if available version satisfies required version.

        Uses semantic versioning compatibility rules:
        - Major version must match exactly (breaking changes)
        - Minor version must be >= required (backwards compatible features)
        - Patch version must be >= required (backwards compatible fixes)

        Args:
            required_version: Minimum required version
            available_version: Available version to check

        Returns:
            True if compatible, False otherwise
        """
        required = self.parse(required_version)
        available = self.parse(available_version)

        # Major version must match (breaking changes)
        if required.major != available.major:
            return False

        # Available must be >= required
        return available >= required

    def get_available_versions(self) -> list[str]:
        """
        Query available versions from Git tags.

        Looks for tags matching semantic version format (with or without 'v' prefix).

        Returns:
            List of version strings sorted in descending order (newest first)

        Raises:
            VersionError: If repository path not set or Git operation fails
        """
        if not self.repository_path:
            raise VersionError("Repository path not set")

        if not self.repository_path.exists():
            raise VersionError(f"Repository path does not exist: {self.repository_path}")

        try:
            # Run git tag command
            result = subprocess.run(
                ["git", "tag", "--list"],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse tags into versions
            versions = []
            for tag in result.stdout.strip().split("\n"):
                if not tag:
                    continue

                try:
                    # Try to parse as version (strip 'v' prefix if present)
                    version = self.parse(tag)
                    versions.append(str(version))
                except VersionError:
                    # Skip non-version tags
                    continue

            # Sort in descending order (newest first)
            versions.sort(key=lambda v: self.parse(v), reverse=True)

            return versions

        except subprocess.CalledProcessError as e:
            raise VersionError(f"Failed to query Git tags: {e}")

    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest version from Git tags.

        Returns:
            Latest version string, or None if no versions found

        Raises:
            VersionError: If repository path not set or Git operation fails
        """
        versions = self.get_available_versions()
        return versions[0] if versions else None

    def validate_version_string(self, version_string: str) -> bool:
        """
        Validate that version string follows semantic versioning format.

        Enforces strict semantic versioning: major.minor.patch (three components).

        Args:
            version_string: Version string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            version = self.parse(version_string)
            # Enforce strict semantic versioning: major.minor.patch
            # Check that the version has exactly 3 numeric components
            version_str = str(version)
            parts = version_str.split(".")
            # Must have at least major.minor.patch
            if len(parts) < 3:
                return False
            # First three parts must be numeric
            try:
                int(parts[0])
                int(parts[1])
                int(parts[2])
            except (ValueError, IndexError):
                return False
            return True
        except VersionError:
            return False
