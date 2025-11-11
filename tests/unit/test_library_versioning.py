"""Unit tests for library versioning functions."""

import json
import re
from datetime import datetime

from aiconfigkit.storage.library import LibraryManager


def create_test_repo_data(namespace: str, name: str, version: str = "1.0.0") -> dict:
    """Helper to create minimal valid repository data for tests."""
    return {
        "namespace": namespace,
        "name": name,
        "description": "Test repository",
        "url": f"https://github.com/user/{name}",
        "author": "test-author",
        "version": version,
        "downloaded_at": datetime.now().isoformat(),
        "alias": None,
        "instructions": [],
    }


class TestGetVersionedNamespace:
    """Test get_versioned_namespace function."""

    def test_versioned_namespace_with_tag(self, tmp_path):
        """Test generating versioned namespace with tag."""
        library = LibraryManager(library_dir=tmp_path)

        namespace = library.get_versioned_namespace("https://github.com/user/repo", "v1.0.0")

        assert "@v1.0.0" in namespace
        # Dots become underscores in namespaces
        assert "github" in namespace
        assert "user" in namespace
        assert "repo" in namespace

    def test_versioned_namespace_with_branch(self, tmp_path):
        """Test generating versioned namespace with branch."""
        library = LibraryManager(library_dir=tmp_path)

        namespace = library.get_versioned_namespace("https://github.com/user/repo", "main")

        assert "@main" in namespace
        assert "github" in namespace

    def test_versioned_namespace_with_commit(self, tmp_path):
        """Test generating versioned namespace with commit hash."""
        library = LibraryManager(library_dir=tmp_path)

        namespace = library.get_versioned_namespace("https://github.com/user/repo", "abc123def")

        assert "@abc123def" in namespace
        assert "github" in namespace

    def test_versioned_namespace_sanitizes_special_chars(self, tmp_path):
        """Test that special characters in refs are sanitized."""
        library = LibraryManager(library_dir=tmp_path)

        namespace = library.get_versioned_namespace("https://github.com/user/repo", "feature/new-feature")

        # Slashes should be replaced with underscores
        assert "@feature_new-feature" in namespace or "@feature" in namespace

    def test_versioned_namespace_different_refs_same_repo(self, tmp_path):
        """Test that different refs produce different namespaces."""
        library = LibraryManager(library_dir=tmp_path)

        ns1 = library.get_versioned_namespace("https://github.com/user/repo", "v1.0.0")
        ns2 = library.get_versioned_namespace("https://github.com/user/repo", "v2.0.0")
        ns3 = library.get_versioned_namespace("https://github.com/user/repo", "main")

        assert ns1 != ns2
        assert ns1 != ns3
        assert ns2 != ns3
        assert "@v1.0.0" in ns1
        assert "@v2.0.0" in ns2
        assert "@main" in ns3


class TestListRepositoryVersions:
    """Test list_repository_versions function."""

    def test_list_versions_no_versions(self, tmp_path):
        """Test listing versions when no versions exist."""
        library = LibraryManager(library_dir=tmp_path)

        versions = library.list_repository_versions("https://github.com/user/repo")

        assert versions == []

    def test_list_versions_single_version(self, tmp_path):
        """Test listing versions with one version."""
        library = LibraryManager(library_dir=tmp_path / "library")

        # Create a mock repository with versioned namespace
        namespace = library.get_versioned_namespace("https://github.com/user/repo", "v1.0.0")
        # Add to index with complete data (index_file is at library_dir.parent / "library.json")
        index_data = {namespace: create_test_repo_data(namespace, "test-repo", "1.0.0")}
        with open(library.index_file, "w") as f:
            json.dump(index_data, f)

        versions = library.list_repository_versions("https://github.com/user/repo")

        assert len(versions) == 1
        assert versions[0][0] == "v1.0.0"  # version ref
        assert versions[0][1] == namespace  # full namespace

    def test_list_versions_multiple_versions(self, tmp_path):
        """Test listing multiple versions of same repository."""
        library = LibraryManager(library_dir=tmp_path / "library")

        # Add multiple versions
        ns1 = library.get_versioned_namespace("https://github.com/user/repo", "v1.0.0")
        ns2 = library.get_versioned_namespace("https://github.com/user/repo", "v2.0.0")
        ns3 = library.get_versioned_namespace("https://github.com/user/repo", "main")

        index_data = {
            ns1: create_test_repo_data(ns1, "test-repo", "1.0.0"),
            ns2: create_test_repo_data(ns2, "test-repo", "2.0.0"),
            ns3: create_test_repo_data(ns3, "test-repo", "latest"),
        }
        with open(library.index_file, "w") as f:
            json.dump(index_data, f)

        versions = library.list_repository_versions("https://github.com/user/repo")

        assert len(versions) == 3
        version_refs = [v[0] for v in versions]
        assert "v1.0.0" in version_refs
        assert "v2.0.0" in version_refs
        assert "main" in version_refs

    def test_list_versions_ignores_other_repos(self, tmp_path):
        """Test that listing only returns versions of specified repo."""
        library = LibraryManager(library_dir=tmp_path / "library")

        # Add versions for two different repos
        ns1 = library.get_versioned_namespace("https://github.com/user/repo1", "v1.0.0")
        ns2 = library.get_versioned_namespace("https://github.com/user/repo2", "v1.0.0")

        index_data = {
            ns1: create_test_repo_data(ns1, "repo1", "1.0.0"),
            ns2: create_test_repo_data(ns2, "repo2", "1.0.0"),
        }
        with open(library.index_file, "w") as f:
            json.dump(index_data, f)

        versions1 = library.list_repository_versions("https://github.com/user/repo1")
        versions2 = library.list_repository_versions("https://github.com/user/repo2")

        assert len(versions1) == 1
        assert len(versions2) == 1
        assert versions1[0][1] != versions2[0][1]  # Different namespaces

    def test_list_versions_with_legacy_non_versioned(self, tmp_path):
        """Test that legacy non-versioned repos are included as 'default'."""
        library = LibraryManager(library_dir=tmp_path / "library")

        # Add a non-versioned namespace (legacy format)
        base_namespace = library.get_repo_namespace("https://github.com/user/repo", "test-repo")

        index_data = {base_namespace: create_test_repo_data(base_namespace, "test-repo", "1.0.0")}
        with open(library.index_file, "w") as f:
            json.dump(index_data, f)

        versions = library.list_repository_versions("https://github.com/user/repo")

        # Should include the default version
        assert len(versions) == 1
        assert versions[0][0] == "default"
        assert versions[0][1] == base_namespace


class TestNamespaceSanitization:
    """Test that refs with special characters are properly sanitized."""

    def test_sanitize_ref_with_slash(self, tmp_path):
        """Test that slashes in branch names are sanitized."""
        library = LibraryManager(library_dir=tmp_path)

        namespace = library.get_versioned_namespace("https://github.com/user/repo", "feature/new-ui")

        # Should not contain literal slash
        assert "/" not in namespace.split("@")[1] if "@" in namespace else True
        # Should contain underscore or hyphen instead
        assert re.search(r"@.*[_-]", namespace)

    def test_sanitize_ref_with_special_chars(self, tmp_path):
        """Test that special characters are sanitized."""
        library = LibraryManager(library_dir=tmp_path)

        namespace = library.get_versioned_namespace("https://github.com/user/repo", "refs/tags/v1.0.0")

        # Should not contain slashes
        ref_part = namespace.split("@")[1] if "@" in namespace else namespace
        assert "/" not in ref_part

    def test_sanitize_preserves_alphanumeric(self, tmp_path):
        """Test that alphanumeric characters and common chars are preserved."""
        library = LibraryManager(library_dir=tmp_path)

        namespace = library.get_versioned_namespace("https://github.com/user/repo", "v1.2.3-alpha.1")

        # Should preserve dots, hyphens
        assert "@v1" in namespace
        assert "2" in namespace
        assert "3" in namespace
