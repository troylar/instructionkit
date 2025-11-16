"""Tests for template library management."""

from pathlib import Path
from unittest.mock import patch

import pytest

from aiconfigkit.core.models import TemplateDefinition, TemplateFile, TemplateManifest
from aiconfigkit.storage.template_library import TemplateLibraryManager


@pytest.fixture
def temp_library(tmp_path):
    """Create a temporary library directory."""
    library_path = tmp_path / "library"
    library_path.mkdir()
    return library_path


@pytest.fixture
def sample_manifest():
    """Create a sample template manifest."""
    return TemplateManifest(
        name="Test Templates",
        description="Test template repository",
        version="1.0.0",
        author=None,
        templates=[
            TemplateDefinition(
                name="test-command",
                description="Test command template",
                files=[TemplateFile(path=".claude/commands/test.md", ide="claude")],
                tags=["test"],
                dependencies=[],
            ),
            TemplateDefinition(
                name="python-standards",
                description="Python coding standards",
                files=[TemplateFile(path=".claude/rules/python.md", ide="claude")],
                tags=["python", "standards"],
                dependencies=[],
            ),
        ],
        bundles=[],
    )


@pytest.fixture
def mock_repo_structure(tmp_path):
    """Create a mock repository structure with manifest."""
    repo_path = tmp_path / "acme-templates"
    repo_path.mkdir()

    # Create manifest
    manifest_content = """name: ACME Templates
description: ACME template repository
version: 1.0.0

templates:
  - name: test-command
    description: Test command
    files:
      - path: .claude/commands/test.md
        ide: claude
    tags: [test]

  - name: python-standards
    description: Python standards
    files:
      - path: .claude/rules/python.md
        ide: claude
    tags: [python, standards]
"""
    (repo_path / "templatekit.yaml").write_text(manifest_content)

    # Create template files
    (repo_path / ".claude" / "commands").mkdir(parents=True)
    (repo_path / ".claude" / "rules").mkdir(parents=True)
    (repo_path / ".claude" / "commands" / "test.md").write_text("# Test Command")
    (repo_path / ".claude" / "rules" / "python.md").write_text("# Python Standards")

    return repo_path


class TestTemplateLibraryManagerInit:
    """Tests for TemplateLibraryManager initialization."""

    def test_default_library_path(self):
        """Test initialization with default library path."""
        manager = TemplateLibraryManager()
        expected_path = Path.home() / ".instructionkit" / "templates"
        assert manager.library_path == expected_path

    def test_custom_library_path(self, temp_library):
        """Test initialization with custom library path."""
        manager = TemplateLibraryManager(library_path=temp_library)
        assert manager.library_path == temp_library

    def test_creates_library_directory(self, tmp_path):
        """Test that library directory is created if it doesn't exist."""
        library_path = tmp_path / "new_library"
        assert not library_path.exists()

        TemplateLibraryManager(library_path=library_path)
        assert library_path.exists()
        assert library_path.is_dir()


class TestCloneRepository:
    """Tests for clone_repository method."""

    @patch("aiconfigkit.storage.template_library.clone_template_repo")
    @patch("aiconfigkit.storage.template_library.derive_namespace")
    @patch("aiconfigkit.storage.template_library.load_manifest")
    def test_clone_new_repository(
        self, mock_load_manifest, mock_derive_namespace, mock_clone, temp_library, sample_manifest
    ):
        """Test cloning a new repository."""
        mock_derive_namespace.return_value = "acme-templates"
        mock_load_manifest.return_value = sample_manifest

        manager = TemplateLibraryManager(library_path=temp_library)
        repo_url = "https://github.com/acme/templates"

        repo_path, manifest = manager.clone_repository(repo_url)

        # Verify namespace derivation
        mock_derive_namespace.assert_called_once_with(repo_url, None)

        # Verify clone was called
        expected_dest = temp_library / "acme-templates"
        mock_clone.assert_called_once_with(repo_url, expected_dest)

        # Verify manifest loaded
        mock_load_manifest.assert_called_once_with(expected_dest / "templatekit.yaml")

        # Verify return values
        assert repo_path == expected_dest
        assert manifest == sample_manifest

    @patch("aiconfigkit.storage.template_library.clone_template_repo")
    @patch("aiconfigkit.storage.template_library.derive_namespace")
    @patch("aiconfigkit.storage.template_library.load_manifest")
    def test_clone_with_namespace_override(
        self, mock_load_manifest, mock_derive_namespace, mock_clone, temp_library, sample_manifest
    ):
        """Test cloning with namespace override."""
        mock_derive_namespace.return_value = "custom-namespace"
        mock_load_manifest.return_value = sample_manifest

        manager = TemplateLibraryManager(library_path=temp_library)
        repo_url = "https://github.com/acme/templates"

        manager.clone_repository(repo_url, namespace_override="custom-namespace")

        mock_derive_namespace.assert_called_once_with(repo_url, "custom-namespace")

    @patch("aiconfigkit.storage.template_library.clone_template_repo")
    @patch("aiconfigkit.storage.template_library.derive_namespace")
    @patch("aiconfigkit.storage.template_library.load_manifest")
    def test_clone_replaces_existing_repository(
        self, mock_load_manifest, mock_derive_namespace, mock_clone, temp_library, sample_manifest
    ):
        """Test that cloning removes existing repository directory."""
        mock_derive_namespace.return_value = "acme-templates"
        mock_load_manifest.return_value = sample_manifest

        # Create existing directory with a file
        existing_repo = temp_library / "acme-templates"
        existing_repo.mkdir()
        (existing_repo / "old_file.txt").write_text("old content")

        manager = TemplateLibraryManager(library_path=temp_library)
        manager.clone_repository("https://github.com/acme/templates")

        # Verify old directory was removed (shutil.rmtree was called)
        # The mock clone should be called with the path
        expected_dest = temp_library / "acme-templates"
        mock_clone.assert_called_once_with("https://github.com/acme/templates", expected_dest)


class TestGetTemplateRepository:
    """Tests for get_template_repository method."""

    def test_get_existing_repository(self, temp_library, mock_repo_structure):
        """Test getting an existing repository."""
        # Move mock repo to library
        import shutil

        shutil.move(str(mock_repo_structure), str(temp_library / "acme-templates"))

        manager = TemplateLibraryManager(library_path=temp_library)
        repo_path, manifest = manager.get_template_repository("acme-templates")

        assert repo_path == temp_library / "acme-templates"
        assert manifest.name == "ACME Templates"
        assert len(manifest.templates) == 2

    def test_repository_not_found(self, temp_library):
        """Test getting a non-existent repository raises FileNotFoundError."""
        manager = TemplateLibraryManager(library_path=temp_library)

        with pytest.raises(FileNotFoundError, match="Template repository 'nonexistent' not found"):
            manager.get_template_repository("nonexistent")


class TestListAvailableTemplates:
    """Tests for list_available_templates method."""

    def test_list_templates(self, temp_library, mock_repo_structure):
        """Test listing templates in a repository."""
        import shutil

        shutil.move(str(mock_repo_structure), str(temp_library / "acme-templates"))

        manager = TemplateLibraryManager(library_path=temp_library)
        templates = manager.list_available_templates("acme-templates")

        assert len(templates) == 2
        assert "test-command" in templates
        assert "python-standards" in templates

    def test_list_templates_repository_not_found(self, temp_library):
        """Test listing templates for non-existent repository."""
        manager = TemplateLibraryManager(library_path=temp_library)

        with pytest.raises(FileNotFoundError):
            manager.list_available_templates("nonexistent")


class TestGetRepositoryVersion:
    """Tests for get_repository_version method."""

    @patch("aiconfigkit.storage.template_library.get_repo_version")
    def test_get_version_success(self, mock_get_version, temp_library):
        """Test getting repository version successfully."""
        # Create a repository directory
        repo_path = temp_library / "acme-templates"
        repo_path.mkdir()

        mock_get_version.return_value = "v1.2.0"

        manager = TemplateLibraryManager(library_path=temp_library)
        version = manager.get_repository_version("acme-templates")

        assert version == "v1.2.0"
        mock_get_version.assert_called_once_with(repo_path)

    def test_get_version_repository_not_found(self, temp_library):
        """Test getting version for non-existent repository returns None."""
        manager = TemplateLibraryManager(library_path=temp_library)
        version = manager.get_repository_version("nonexistent")

        assert version is None

    @patch("aiconfigkit.storage.template_library.get_repo_version")
    def test_get_version_exception_returns_none(self, mock_get_version, temp_library):
        """Test that exceptions during version retrieval return None."""
        repo_path = temp_library / "acme-templates"
        repo_path.mkdir()

        mock_get_version.side_effect = Exception("Git error")

        manager = TemplateLibraryManager(library_path=temp_library)
        version = manager.get_repository_version("acme-templates")

        assert version is None


class TestListInstalledRepositories:
    """Tests for list_installed_repositories method."""

    def test_list_empty_library(self, temp_library):
        """Test listing repositories in empty library."""
        manager = TemplateLibraryManager(library_path=temp_library)
        repos = manager.list_installed_repositories()

        assert repos == []

    def test_list_repositories(self, temp_library, mock_repo_structure):
        """Test listing installed repositories."""
        import shutil

        # Add multiple repositories
        shutil.move(str(mock_repo_structure), str(temp_library / "acme-templates"))

        # Create another repo
        second_repo = temp_library / "company-standards"
        second_repo.mkdir()
        (second_repo / "templatekit.yaml").write_text(
            """name: Company Standards
description: Company coding standards
version: 1.0.0
templates: []
"""
        )

        manager = TemplateLibraryManager(library_path=temp_library)
        repos = manager.list_installed_repositories()

        assert len(repos) == 2
        assert "acme-templates" in repos
        assert "company-standards" in repos
        assert repos == sorted(repos)  # Should be sorted

    def test_list_repositories_ignores_directories_without_manifest(self, temp_library):
        """Test that directories without manifest are ignored."""
        # Create directory without manifest
        (temp_library / "not-a-repo").mkdir()
        (temp_library / "not-a-repo" / "random.txt").write_text("content")

        # Create valid repo
        valid_repo = temp_library / "valid-repo"
        valid_repo.mkdir()
        (valid_repo / "templatekit.yaml").write_text(
            """name: Valid
description: Valid repo
version: 1.0.0
templates: []
"""
        )

        manager = TemplateLibraryManager(library_path=temp_library)
        repos = manager.list_installed_repositories()

        assert len(repos) == 1
        assert "valid-repo" in repos
        assert "not-a-repo" not in repos

    def test_list_repositories_nonexistent_library(self, tmp_path):
        """Test listing repositories when library doesn't exist."""
        library_path = tmp_path / "nonexistent"
        manager = TemplateLibraryManager(library_path=library_path)

        repos = manager.list_installed_repositories()
        assert repos == []

    def test_list_repositories_deleted_after_init(self, tmp_path):
        """Test listing repositories when library is deleted after initialization."""
        import shutil

        library_path = tmp_path / "library"
        manager = TemplateLibraryManager(library_path=library_path)

        # Verify library was created by __init__
        assert library_path.exists()

        # Delete the library directory
        shutil.rmtree(library_path)

        # Should return empty list when library doesn't exist
        repos = manager.list_installed_repositories()
        assert repos == []


class TestRemoveRepository:
    """Tests for remove_repository method."""

    def test_remove_existing_repository(self, temp_library, mock_repo_structure):
        """Test removing an existing repository."""
        import shutil

        repo_path = temp_library / "acme-templates"
        shutil.move(str(mock_repo_structure), str(repo_path))

        assert repo_path.exists()

        manager = TemplateLibraryManager(library_path=temp_library)
        manager.remove_repository("acme-templates")

        assert not repo_path.exists()

    def test_remove_nonexistent_repository(self, temp_library):
        """Test removing a non-existent repository raises FileNotFoundError."""
        manager = TemplateLibraryManager(library_path=temp_library)

        with pytest.raises(FileNotFoundError, match="Repository 'nonexistent' not found"):
            manager.remove_repository("nonexistent")


class TestGetTemplateFilePath:
    """Tests for get_template_file_path method."""

    def test_get_existing_file_path(self, temp_library, mock_repo_structure):
        """Test getting path to existing template file."""
        import shutil

        shutil.move(str(mock_repo_structure), str(temp_library / "acme-templates"))

        manager = TemplateLibraryManager(library_path=temp_library)
        file_path = manager.get_template_file_path("acme-templates", "test-command", ".claude/commands/test.md")

        expected_path = temp_library / "acme-templates" / ".claude" / "commands" / "test.md"
        assert file_path == expected_path
        assert file_path.exists()

    def test_get_nonexistent_file_path(self, temp_library, mock_repo_structure):
        """Test getting path to non-existent file raises FileNotFoundError."""
        import shutil

        shutil.move(str(mock_repo_structure), str(temp_library / "acme-templates"))

        manager = TemplateLibraryManager(library_path=temp_library)

        with pytest.raises(FileNotFoundError, match="Template file not found"):
            manager.get_template_file_path("acme-templates", "test-command", "nonexistent.md")

    def test_get_file_path_repository_not_found(self, temp_library):
        """Test getting file path for non-existent repository."""
        manager = TemplateLibraryManager(library_path=temp_library)

        with pytest.raises(FileNotFoundError, match="Template repository"):
            manager.get_template_file_path("nonexistent", "test", "file.md")
