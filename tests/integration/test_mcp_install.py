"""Integration tests for MCP template installation."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from aiconfigkit.core.mcp.manager import MCPManager
from aiconfigkit.core.models import InstallationScope


class TestMCPInstallIntegration:
    """Integration tests for MCP template installation."""

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

    @pytest.fixture
    def sample_template_repo(self, tmp_path: Path) -> Path:
        """Create a sample template repository."""
        repo = tmp_path / "sample-repo"
        repo.mkdir()

        # Create templatekit.yaml
        metadata = {
            "name": "Backend Tools",
            "version": "1.0.0",
            "description": "MCP servers for backend development",
            "mcp_servers": [
                {
                    "name": "github",
                    "command": "uvx",
                    "args": ["mcp-server-github"],
                    "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": None},
                },
                {
                    "name": "filesystem",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
                    "env": {},
                },
            ],
            "mcp_sets": [
                {
                    "name": "backend-dev",
                    "description": "Backend development servers",
                    "servers": ["github", "filesystem"],
                }
            ],
        }

        with open(repo / "templatekit.yaml", "w") as f:
            yaml.dump(metadata, f)

        return repo

    def test_install_from_local_path_success(self, manager: MCPManager, sample_template_repo: Path) -> None:
        """Test installing MCP template from local directory."""
        # Install
        template = manager.install_template(
            str(sample_template_repo),
            "backend-tools",
            scope=InstallationScope.PROJECT,
        )

        # Verify template
        assert template.namespace == "backend-tools"
        assert template.source_path == str(sample_template_repo.resolve())
        assert template.source_url is None
        assert template.version == "1.0.0"
        assert template.description == "MCP servers for backend development"

        # Verify servers
        assert len(template.servers) == 2
        github_server = next(s for s in template.servers if s.name == "github")
        assert github_server.command == "uvx"
        assert github_server.get_required_env_vars() == ["GITHUB_PERSONAL_ACCESS_TOKEN"]

        filesystem_server = next(s for s in template.servers if s.name == "filesystem")
        assert filesystem_server.command == "npx"
        assert filesystem_server.get_required_env_vars() == []

        # Verify sets
        assert len(template.sets) == 1
        assert template.sets[0].name == "backend-dev"
        assert template.sets[0].server_names == ["github", "filesystem"]

        # Verify files were copied
        install_path = manager.library_root / "backend-tools"
        assert install_path.exists()
        assert (install_path / "templatekit.yaml").exists()
        assert (install_path / ".mcp_template.json").exists()

    def test_install_from_local_path_minimal_config(self, manager: MCPManager, tmp_path: Path) -> None:
        """Test installing with minimal configuration (no MCP servers or sets)."""
        repo = tmp_path / "minimal-repo"
        repo.mkdir()

        # Create minimal templatekit.yaml
        metadata = {
            "name": "Minimal Template",
            "version": "0.1.0",
            "description": "Minimal template for testing",
        }

        with open(repo / "templatekit.yaml", "w") as f:
            yaml.dump(metadata, f)

        # Install
        template = manager.install_template(str(repo), "minimal")

        # Verify
        assert template.namespace == "minimal"
        assert len(template.servers) == 0
        assert len(template.sets) == 0

    def test_install_conflict_skip(self, manager: MCPManager, sample_template_repo: Path) -> None:
        """Test that installing over existing template without force fails."""
        # First install
        manager.install_template(str(sample_template_repo), "backend-tools")

        # Attempt second install without force
        with pytest.raises(ValueError, match="already exists"):
            manager.install_template(str(sample_template_repo), "backend-tools", force=False)

        # Verify original template is intact
        template = manager.load_template("backend-tools")
        assert template is not None
        assert template.version == "1.0.0"

    def test_install_conflict_overwrite(self, manager: MCPManager, sample_template_repo: Path, tmp_path: Path) -> None:
        """Test that force flag overwrites existing template."""
        # First install (version 1.0.0)
        manager.install_template(str(sample_template_repo), "backend-tools")

        # Create updated repo (version 2.0.0)
        updated_repo = tmp_path / "updated-repo"
        updated_repo.mkdir()

        metadata = {
            "name": "Backend Tools",
            "version": "2.0.0",
            "description": "Updated backend tools",
            "mcp_servers": [
                {
                    "name": "database",
                    "command": "python",
                    "args": ["-m", "mcp_server_postgres"],
                    "env": {"DATABASE_URL": None},
                }
            ],
        }

        with open(updated_repo / "templatekit.yaml", "w") as f:
            yaml.dump(metadata, f)

        # Install with force
        template = manager.install_template(
            str(updated_repo),
            "backend-tools",
            force=True,
        )

        # Verify template was replaced
        assert template.version == "2.0.0"
        assert template.description == "Updated backend tools"
        assert len(template.servers) == 1
        assert template.servers[0].name == "database"

    def test_install_global_scope(self, manager: MCPManager, sample_template_repo: Path) -> None:
        """Test installing template with global scope."""
        # Install globally
        template = manager.install_template(
            str(sample_template_repo),
            "personal-tools",
            scope=InstallationScope.GLOBAL,
        )

        # Verify scope
        assert template.namespace == "personal-tools"

        # Verify installed in global directory
        global_path = manager.library_root / "global" / "personal-tools"
        assert global_path.exists()

        # Verify can load with global scope
        loaded = manager.load_template("personal-tools", scope=InstallationScope.GLOBAL)
        assert loaded is not None
        assert loaded.namespace == "personal-tools"

    def test_install_multiple_templates(self, manager: MCPManager, sample_template_repo: Path, tmp_path: Path) -> None:
        """Test installing multiple templates in same library."""
        # Install first template
        manager.install_template(str(sample_template_repo), "backend-tools")

        # Create second template
        frontend_repo = tmp_path / "frontend-repo"
        frontend_repo.mkdir()

        metadata = {
            "name": "Frontend Tools",
            "version": "1.0.0",
            "description": "Frontend MCP servers",
            "mcp_servers": [
                {
                    "name": "browser",
                    "command": "node",
                    "args": ["browser-mcp-server"],
                    "env": {},
                }
            ],
        }

        with open(frontend_repo / "templatekit.yaml", "w") as f:
            yaml.dump(metadata, f)

        # Install second template
        manager.install_template(str(frontend_repo), "frontend-tools")

        # Verify both templates exist
        templates = manager.list_templates()
        assert len(templates) == 2

        namespaces = {t.namespace for t in templates}
        assert namespaces == {"backend-tools", "frontend-tools"}

    def test_install_and_reload(self, manager: MCPManager, sample_template_repo: Path) -> None:
        """Test that installed template can be reloaded from disk."""
        # Install
        original = manager.install_template(str(sample_template_repo), "backend-tools")

        # Create new manager instance (simulating restart)
        new_manager = MCPManager(manager.library_root)

        # Load template
        loaded = new_manager.load_template("backend-tools")

        # Verify
        assert loaded is not None
        assert loaded.namespace == original.namespace
        assert loaded.version == original.version
        assert len(loaded.servers) == len(original.servers)
        assert len(loaded.sets) == len(original.sets)

    @patch("aiconfigkit.core.mcp.manager.GitOperations")
    def test_install_from_git_url(self, mock_git: Mock, manager: MCPManager, sample_template_repo: Path) -> None:
        """Test installing from Git URL (with mocked Git operations)."""

        # Setup mock to copy sample repo when clone is called
        def mock_clone(url: str, dest: Path) -> None:
            # Copy sample repo to destination
            import shutil

            shutil.copytree(sample_template_repo, dest, dirs_exist_ok=True)

        mock_git_instance = mock_git.return_value
        mock_git_instance.clone_repository = Mock(side_effect=mock_clone)

        # Install from "Git URL"
        git_url = "https://github.com/test/backend-tools"
        template = manager.install_template(git_url, "backend-tools")

        # Verify Git operations were called
        mock_git_instance.clone_repository.assert_called_once()

        # Verify template
        assert template.namespace == "backend-tools"
        assert template.source_url == git_url
        assert template.source_path is None
        assert len(template.servers) == 2

    def test_uninstall_template(self, manager: MCPManager, sample_template_repo: Path) -> None:
        """Test uninstalling a template."""
        # Install
        manager.install_template(str(sample_template_repo), "backend-tools")

        # Verify exists
        assert manager.load_template("backend-tools") is not None

        # Uninstall
        result = manager.uninstall_template("backend-tools")

        # Verify
        assert result is True
        assert manager.load_template("backend-tools") is None

        # Verify directory removed
        install_path = manager.library_root / "backend-tools"
        assert not install_path.exists()

    def test_template_metadata_persistence(self, manager: MCPManager, sample_template_repo: Path) -> None:
        """Test that template metadata is correctly persisted."""
        # Install
        manager.install_template(str(sample_template_repo), "backend-tools")

        # Read metadata file directly
        metadata_file = manager.library_root / "backend-tools" / ".mcp_template.json"
        assert metadata_file.exists()

        with open(metadata_file) as f:
            data = json.load(f)

        # Verify all fields are present
        assert data["namespace"] == "backend-tools"
        assert data["version"] == "1.0.0"
        assert data["description"] == "MCP servers for backend development"
        assert data["source_path"] is not None
        assert data["source_url"] is None
        assert "installed_at" in data
        assert len(data["servers"]) == 2
        assert len(data["sets"]) == 1

        # Verify server data
        github_server = next(s for s in data["servers"] if s["name"] == "github")
        assert github_server["command"] == "uvx"
        assert github_server["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"] is None

    def test_install_invalid_namespace(self, manager: MCPManager, sample_template_repo: Path) -> None:
        """Test that installing with invalid namespace fails."""
        with pytest.raises(ValueError, match="alphanumeric"):
            manager.install_template(str(sample_template_repo), "backend tools")

        with pytest.raises(ValueError, match="path separators"):
            manager.install_template(str(sample_template_repo), "backend/tools")

    def test_install_nonexistent_path(self, manager: MCPManager) -> None:
        """Test that installing from non-existent path fails."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            manager.install_template("/nonexistent/path", "backend-tools")

    def test_templatekit_yaml_fallback(self, manager: MCPManager, tmp_path: Path) -> None:
        """Test that templatekit.yaml works (InstructionKit uses templatekit.yaml as primary name)."""
        repo = tmp_path / "repo"
        repo.mkdir()

        # Create templatekit.yaml (standard name)
        metadata = {
            "name": "Test Template",
            "version": "1.5.0",
            "description": "Using templatekit.yaml",
            "mcp_servers": [
                {
                    "name": "test-server",
                    "command": "test",
                    "args": [],
                    "env": {},
                }
            ],
        }

        with open(repo / "templatekit.yaml", "w") as f:
            yaml.dump(metadata, f)

        # Install
        template = manager.install_template(str(repo), "test-template")

        # Verify
        assert template.version == "1.5.0"
        assert template.description == "Using templatekit.yaml"
        assert len(template.servers) == 1
