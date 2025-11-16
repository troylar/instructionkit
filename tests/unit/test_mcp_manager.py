"""Unit tests for MCPManager."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from aiconfigkit.core.mcp.manager import MCPManager
from aiconfigkit.core.models import InstallationScope


class TestMCPManager:
    """Test MCPManager class."""

    @pytest.fixture
    def temp_library(self, tmp_path: Path) -> Path:
        """Create temporary library directory."""
        library = tmp_path / "library"
        library.mkdir()
        return library

    @pytest.fixture
    def manager(self, temp_library: Path) -> MCPManager:
        """Create MCPManager instance."""
        return MCPManager(temp_library)

    def test_init_creates_library_directory(self, tmp_path: Path) -> None:
        """Test that initializing manager creates library directory."""
        library = tmp_path / "new_library"
        assert not library.exists()

        manager = MCPManager(library)

        assert library.exists()
        assert manager.library_root == library

    def test_validate_namespace_valid(self, manager: MCPManager) -> None:
        """Test namespace validation with valid names."""
        # Should not raise
        manager._validate_namespace("backend")
        manager._validate_namespace("backend-tools")
        manager._validate_namespace("backend_tools")
        manager._validate_namespace("backend123")
        manager._validate_namespace("Backend-Tools_123")

    def test_validate_namespace_empty(self, manager: MCPManager) -> None:
        """Test namespace validation rejects empty string."""
        with pytest.raises(ValueError, match="cannot be empty"):
            manager._validate_namespace("")

    def test_validate_namespace_invalid_characters(self, manager: MCPManager) -> None:
        """Test namespace validation rejects invalid characters."""
        with pytest.raises(ValueError, match="alphanumeric"):
            manager._validate_namespace("backend@tools")

        with pytest.raises(ValueError, match="alphanumeric"):
            manager._validate_namespace("backend tools")

        with pytest.raises(ValueError, match="alphanumeric"):
            manager._validate_namespace("backend.tools")

    def test_validate_namespace_path_separator(self, manager: MCPManager) -> None:
        """Test namespace validation rejects path separators."""
        with pytest.raises(ValueError, match="path separators"):
            manager._validate_namespace("backend/tools")

        with pytest.raises(ValueError, match="path separators"):
            manager._validate_namespace("backend\\tools")

    def test_get_install_path_project_scope(self, manager: MCPManager) -> None:
        """Test getting install path for project scope."""
        path = manager._get_install_path("backend", InstallationScope.PROJECT)

        assert path == manager.library_root / "backend"

    def test_get_install_path_global_scope(self, manager: MCPManager) -> None:
        """Test getting install path for global scope."""
        path = manager._get_install_path("backend", InstallationScope.GLOBAL)

        assert path == manager.library_root / "global" / "backend"

    def test_install_from_local_success(self, manager: MCPManager, tmp_path: Path) -> None:
        """Test installing template from local directory."""
        # Setup
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create mock metadata
        metadata_file = source_dir / "templatekit.yaml"
        metadata_file.write_text("name: Test\nversion: 1.0.0\ndescription: Test template\n")

        # Install (no mocking - let it actually work)
        template = manager.install_template(str(source_dir), "test-template")

        # Verify
        assert template.namespace == "test-template"
        assert template.source_path == str(source_dir.resolve())
        assert template.source_url is None
        assert template.version == "1.0.0"

        # Verify files were copied
        install_path = manager.library_root / "test-template"
        assert install_path.exists()
        assert (install_path / "templatekit.yaml").exists()

    @patch("aiconfigkit.core.mcp.manager.GitOperations")
    def test_install_from_git_success(self, mock_git: Mock, manager: MCPManager, tmp_path: Path) -> None:
        """Test installing template from Git URL."""
        # Setup
        git_url = "https://github.com/test/repo"

        # Create a source directory that git will "clone"
        source_dir = tmp_path / "git_source"
        source_dir.mkdir()
        (source_dir / "templatekit.yaml").write_text("name: Test\nversion: 1.0.0\ndescription: Test\n")

        # Mock git operations to copy our source
        def mock_clone(url: str, dest: Path) -> None:
            import shutil

            shutil.copytree(source_dir, dest, dirs_exist_ok=True)

        mock_git_instance = mock_git.return_value
        mock_git_instance.clone_repository = Mock(side_effect=mock_clone)

        # Install
        template = manager.install_template(git_url, "test-template")

        # Verify
        assert template.namespace == "test-template"
        assert template.source_url == git_url
        assert template.source_path is None
        mock_git_instance.clone_repository.assert_called_once()

        # Verify files exist
        install_path = manager.library_root / "test-template"
        assert install_path.exists()

    @patch("aiconfigkit.core.mcp.manager.RepositoryParser")
    @patch("aiconfigkit.core.mcp.manager.shutil.copytree")
    def test_install_template_already_exists_no_force(
        self, mock_copytree: Mock, mock_parser: Mock, manager: MCPManager, tmp_path: Path
    ) -> None:
        """Test that installing over existing template fails without force flag."""
        # Create existing template directory
        existing_dir = manager.library_root / "test-template"
        existing_dir.mkdir(parents=True)

        # Setup source
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Attempt install without force
        with pytest.raises(ValueError, match="already exists"):
            manager.install_template(str(source_dir), "test-template", force=False)

    @patch("aiconfigkit.core.mcp.manager.RepositoryParser")
    @patch("aiconfigkit.core.mcp.manager.shutil.copytree")
    @patch("aiconfigkit.core.mcp.manager.shutil.rmtree")
    def test_install_template_force_overwrite(
        self, mock_rmtree: Mock, mock_copytree: Mock, mock_parser: Mock, manager: MCPManager, tmp_path: Path
    ) -> None:
        """Test that force flag allows overwriting existing template."""
        # Create existing template directory
        existing_dir = manager.library_root / "test-template"
        existing_dir.mkdir(parents=True)

        # Setup source
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create metadata
        metadata_file = source_dir / "templatekit.yaml"
        metadata_file.write_text("name: Test\nversion: 1.0.0\n")

        # Mock parser
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse_mcp_servers.return_value = []
        mock_parser_instance.parse_mcp_sets.return_value = []

        # Install with force
        with patch.object(manager, "_parse_metadata", return_value={"version": "1.0.0", "description": "Test"}):
            template = manager.install_template(str(source_dir), "test-template", force=True)

        # Verify old directory was removed
        mock_rmtree.assert_called_once()
        assert template.namespace == "test-template"

    def test_install_template_source_not_exists(self, manager: MCPManager) -> None:
        """Test that installing from non-existent path fails."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            manager.install_template("/nonexistent/path", "test-template")

    def test_load_template_exists(self, manager: MCPManager) -> None:
        """Test loading an existing template."""
        # Create template directory and metadata
        template_dir = manager.library_root / "test-template"
        template_dir.mkdir(parents=True)

        template_data = {
            "namespace": "test-template",
            "source_url": "https://github.com/test/repo",
            "source_path": None,
            "version": "1.0.0",
            "description": "Test template",
            "installed_at": datetime.now().isoformat(),
            "servers": [],
            "sets": [],
        }

        metadata_file = template_dir / ".mcp_template.json"
        metadata_file.write_text(json.dumps(template_data))

        # Load template
        template = manager.load_template("test-template")

        # Verify
        assert template is not None
        assert template.namespace == "test-template"
        assert template.version == "1.0.0"

    def test_load_template_not_exists(self, manager: MCPManager) -> None:
        """Test loading non-existent template returns None."""
        template = manager.load_template("nonexistent")

        assert template is None

    def test_list_templates_empty(self, manager: MCPManager) -> None:
        """Test listing templates when library is empty."""
        templates = manager.list_templates()

        assert templates == []

    def test_list_templates_multiple(self, manager: MCPManager) -> None:
        """Test listing multiple templates."""
        # Create multiple templates
        for i in range(3):
            template_dir = manager.library_root / f"template-{i}"
            template_dir.mkdir(parents=True)

            template_data = {
                "namespace": f"template-{i}",
                "source_url": f"https://github.com/test/repo-{i}",
                "source_path": None,
                "version": "1.0.0",
                "description": f"Test template {i}",
                "installed_at": datetime.now().isoformat(),
                "servers": [],
                "sets": [],
            }

            metadata_file = template_dir / ".mcp_template.json"
            metadata_file.write_text(json.dumps(template_data))

        # List templates
        templates = manager.list_templates()

        # Verify
        assert len(templates) == 3
        namespaces = {t.namespace for t in templates}
        assert namespaces == {"template-0", "template-1", "template-2"}

    def test_list_templates_global_scope(self, manager: MCPManager) -> None:
        """Test listing templates in global scope."""
        # Create global template
        global_dir = manager.library_root / "global" / "global-template"
        global_dir.mkdir(parents=True)

        template_data = {
            "namespace": "global-template",
            "source_url": "https://github.com/test/repo",
            "source_path": None,
            "version": "1.0.0",
            "description": "Global template",
            "installed_at": datetime.now().isoformat(),
            "servers": [],
            "sets": [],
        }

        metadata_file = global_dir / ".mcp_template.json"
        metadata_file.write_text(json.dumps(template_data))

        # List global templates
        templates = manager.list_templates(scope=InstallationScope.GLOBAL)

        # Verify
        assert len(templates) == 1
        assert templates[0].namespace == "global-template"

    @patch("aiconfigkit.core.mcp.manager.shutil.rmtree")
    def test_uninstall_template_exists(self, mock_rmtree: Mock, manager: MCPManager) -> None:
        """Test uninstalling an existing template."""
        # Create template directory
        template_dir = manager.library_root / "test-template"
        template_dir.mkdir(parents=True)

        # Uninstall
        result = manager.uninstall_template("test-template")

        # Verify
        assert result is True
        mock_rmtree.assert_called_once_with(template_dir)

    def test_uninstall_template_not_exists(self, manager: MCPManager) -> None:
        """Test uninstalling non-existent template returns False."""
        result = manager.uninstall_template("nonexistent")

        assert result is False

    def test_parse_metadata_instructionkit_yaml(self, manager: MCPManager, tmp_path: Path) -> None:
        """Test parsing metadata from templatekit.yaml."""
        template_dir = tmp_path / "template"
        template_dir.mkdir()

        metadata_file = template_dir / "templatekit.yaml"
        metadata_file.write_text("name: Test\nversion: 1.0.0\ndescription: Test template\nauthor: Test Author\n")

        metadata = manager._parse_metadata(template_dir)

        assert metadata["name"] == "Test"
        assert metadata["version"] == "1.0.0"
        assert metadata["description"] == "Test template"
        assert metadata["author"] == "Test Author"

    def test_parse_metadata_templatekit_yaml_fallback(self, manager: MCPManager, tmp_path: Path) -> None:
        """Test parsing metadata falls back to templatekit.yaml."""
        template_dir = tmp_path / "template"
        template_dir.mkdir()

        # No templatekit.yaml, only templatekit.yaml
        metadata_file = template_dir / "templatekit.yaml"
        metadata_file.write_text("name: Test\nversion: 2.0.0\n")

        metadata = manager._parse_metadata(template_dir)

        assert metadata["name"] == "Test"
        assert metadata["version"] == "2.0.0"

    def test_parse_metadata_no_file(self, manager: MCPManager, tmp_path: Path) -> None:
        """Test parsing metadata when no file exists returns empty dict."""
        template_dir = tmp_path / "template"
        template_dir.mkdir()

        metadata = manager._parse_metadata(template_dir)

        assert metadata == {}

    @patch("aiconfigkit.core.mcp.manager.GitOperations")
    def test_install_from_git_clone_failure(
        self, mock_git_ops_class: MagicMock, manager: MCPManager, tmp_path: Path
    ) -> None:
        """Test installation from Git when clone fails."""
        mock_git_ops = MagicMock()
        mock_git_ops.clone_repository.side_effect = RuntimeError("Clone failed")
        mock_git_ops_class.return_value = mock_git_ops

        dest_path = tmp_path / "dest"

        with pytest.raises(RuntimeError, match="Failed to clone Git repository"):
            manager._install_from_git("https://github.com/test/repo.git", dest_path)

    def test_list_templates_nonexistent_directory(self, manager: MCPManager, tmp_path: Path) -> None:
        """Test listing templates when library directory doesn't exist."""
        # Set library root to nonexistent directory
        manager.library_root = tmp_path / "nonexistent"

        templates = manager.list_templates(scope="global")

        # Should return empty list when directory doesn't exist
        assert templates == []

    def test_list_templates_invalid_metadata(self, manager: MCPManager, tmp_path: Path) -> None:
        """Test listing templates with corrupted metadata file."""
        # Create template directory with invalid metadata
        template_dir = tmp_path / "global" / "test-template"
        template_dir.mkdir(parents=True)

        metadata_file = template_dir / ".mcp_template.json"
        metadata_file.write_text("{invalid json")

        manager.library_root = tmp_path

        # Should handle exception gracefully and skip invalid template
        templates = manager.list_templates(scope="global")

        assert templates == []
