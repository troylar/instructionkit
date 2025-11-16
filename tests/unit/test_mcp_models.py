"""Unit tests for MCP data models."""

from datetime import datetime

import pytest

from aiconfigkit.core.models import (
    ActiveSetState,
    EnvironmentConfig,
    InstallationScope,
    MCPServer,
    MCPSet,
    MCPTemplate,
)


class TestMCPServer:
    """Test MCPServer dataclass."""

    def test_create_valid_server(self) -> None:
        """Test creating a valid MCP server."""
        server = MCPServer(
            name="github",
            command="uvx",
            args=["mcp-server-github"],
            env={"GITHUB_TOKEN": None},
            namespace="backend",
        )

        assert server.name == "github"
        assert server.command == "uvx"
        assert server.args == ["mcp-server-github"]
        assert server.env == {"GITHUB_TOKEN": None}
        assert server.namespace == "backend"

    def test_invalid_name_with_spaces(self) -> None:
        """Test that server name with spaces is rejected."""
        with pytest.raises(ValueError, match="Invalid server name"):
            MCPServer(
                name="github server",
                command="uvx",
                args=[],
                env={},
                namespace="backend",
            )

    def test_invalid_name_with_special_chars(self) -> None:
        """Test that server name with special characters is rejected."""
        with pytest.raises(ValueError, match="Invalid server name"):
            MCPServer(
                name="github@server",
                command="uvx",
                args=[],
                env={},
                namespace="backend",
            )

    def test_invalid_env_var_name_lowercase(self) -> None:
        """Test that lowercase env var names are rejected."""
        with pytest.raises(ValueError, match="Invalid environment variable name"):
            MCPServer(
                name="github",
                command="uvx",
                args=[],
                env={"github_token": "value"},
                namespace="backend",
            )

    def test_invalid_env_var_name_with_dash(self) -> None:
        """Test that env var names with dashes are rejected."""
        with pytest.raises(ValueError, match="Invalid environment variable name"):
            MCPServer(
                name="github",
                command="uvx",
                args=[],
                env={"GITHUB-TOKEN": "value"},
                namespace="backend",
            )

    def test_empty_command(self) -> None:
        """Test that empty command is rejected."""
        with pytest.raises(ValueError, match="command cannot be empty"):
            MCPServer(
                name="github",
                command="",
                args=[],
                env={},
                namespace="backend",
            )

    def test_get_fully_qualified_name(self) -> None:
        """Test getting fully qualified name."""
        server = MCPServer(
            name="github",
            command="uvx",
            args=[],
            env={},
            namespace="backend",
        )

        assert server.get_fully_qualified_name() == "backend.github"

    def test_get_required_env_vars_none_required(self) -> None:
        """Test getting required env vars when none are required."""
        server = MCPServer(
            name="filesystem",
            command="npx",
            args=[],
            env={"PATH": "/usr/bin"},
            namespace="backend",
        )

        assert server.get_required_env_vars() == []

    def test_get_required_env_vars_some_required(self) -> None:
        """Test getting required env vars."""
        server = MCPServer(
            name="github",
            command="uvx",
            args=[],
            env={"GITHUB_TOKEN": None, "API_URL": "https://api.github.com"},
            namespace="backend",
        )

        required = server.get_required_env_vars()
        assert required == ["GITHUB_TOKEN"]

    def test_has_all_credentials_true(self) -> None:
        """Test checking credentials when all are provided."""
        server = MCPServer(
            name="github",
            command="uvx",
            args=[],
            env={"GITHUB_TOKEN": None},
            namespace="backend",
        )

        env_config = EnvironmentConfig(variables={"GITHUB_TOKEN": "token123"})

        assert server.has_all_credentials(env_config) is True

    def test_has_all_credentials_false(self) -> None:
        """Test checking credentials when some are missing."""
        server = MCPServer(
            name="github",
            command="uvx",
            args=[],
            env={"GITHUB_TOKEN": None, "API_KEY": None},
            namespace="backend",
        )

        env_config = EnvironmentConfig(variables={"GITHUB_TOKEN": "token123"})

        assert server.has_all_credentials(env_config) is False

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        server = MCPServer(
            name="github",
            command="uvx",
            args=["mcp-server-github"],
            env={"GITHUB_TOKEN": None},
            namespace="backend",
        )

        data = server.to_dict()

        assert data == {
            "name": "github",
            "command": "uvx",
            "args": ["mcp-server-github"],
            "env": {"GITHUB_TOKEN": None},
            "namespace": "backend",
        }

    def test_from_dict(self) -> None:
        """Test deserialization from dict."""
        data = {
            "name": "github",
            "command": "uvx",
            "args": ["mcp-server-github"],
            "env": {"GITHUB_TOKEN": None},
        }

        server = MCPServer.from_dict(data, "backend")

        assert server.name == "github"
        assert server.command == "uvx"
        assert server.namespace == "backend"


class TestMCPSet:
    """Test MCPSet dataclass."""

    def test_create_valid_set(self) -> None:
        """Test creating a valid MCP set."""
        mcp_set = MCPSet(
            name="backend-dev",
            description="Backend development servers",
            server_names=["github", "database"],
            namespace="backend",
        )

        assert mcp_set.name == "backend-dev"
        assert mcp_set.description == "Backend development servers"
        assert mcp_set.server_names == ["github", "database"]

    def test_invalid_name(self) -> None:
        """Test that invalid set name is rejected."""
        with pytest.raises(ValueError, match="Invalid set name"):
            MCPSet(
                name="backend dev",
                description="Test",
                server_names=["github"],
                namespace="backend",
            )

    def test_empty_server_names(self) -> None:
        """Test that empty server list is rejected."""
        with pytest.raises(ValueError, match="at least one server"):
            MCPSet(
                name="backend-dev",
                description="Test",
                server_names=[],
                namespace="backend",
            )

    def test_get_fully_qualified_name(self) -> None:
        """Test getting fully qualified name."""
        mcp_set = MCPSet(
            name="backend-dev",
            description="Test",
            server_names=["github"],
            namespace="backend",
        )

        assert mcp_set.get_fully_qualified_name() == "backend.backend-dev"

    def test_resolve_servers_success(self) -> None:
        """Test resolving server references."""
        servers = [
            MCPServer("github", "uvx", [], {}, "backend"),
            MCPServer("database", "python", [], {}, "backend"),
        ]

        mcp_set = MCPSet(
            name="backend-dev",
            description="Test",
            server_names=["github", "database"],
            namespace="backend",
        )

        resolved = mcp_set.resolve_servers(servers)

        assert len(resolved) == 2
        assert resolved[0].name == "github"
        assert resolved[1].name == "database"

    def test_resolve_servers_unknown_reference(self) -> None:
        """Test that resolving unknown server fails."""
        servers = [
            MCPServer("github", "uvx", [], {}, "backend"),
        ]

        mcp_set = MCPSet(
            name="backend-dev",
            description="Test",
            server_names=["github", "unknown"],
            namespace="backend",
        )

        with pytest.raises(ValueError, match="unknown server"):
            mcp_set.resolve_servers(servers)


class TestMCPTemplate:
    """Test MCPTemplate dataclass."""

    def test_create_valid_template(self) -> None:
        """Test creating a valid MCP template."""
        template = MCPTemplate(
            namespace="backend",
            source_url="https://github.com/test/repo",
            source_path=None,
            version="1.0.0",
            description="Test template",
            installed_at=datetime.now(),
            servers=[],
            sets=[],
        )

        assert template.namespace == "backend"
        assert template.source_url == "https://github.com/test/repo"
        assert template.version == "1.0.0"

    def test_both_source_url_and_path(self) -> None:
        """Test that having both source_url and source_path fails."""
        with pytest.raises(ValueError, match="cannot have both"):
            MCPTemplate(
                namespace="backend",
                source_url="https://github.com/test/repo",
                source_path="/local/path",
                version="1.0.0",
                description="Test",
                installed_at=datetime.now(),
            )

    def test_neither_source_url_nor_path(self) -> None:
        """Test that having neither source_url nor source_path fails."""
        with pytest.raises(ValueError, match="must have either"):
            MCPTemplate(
                namespace="backend",
                source_url=None,
                source_path=None,
                version="1.0.0",
                description="Test",
                installed_at=datetime.now(),
            )

    def test_get_server_by_name_found(self) -> None:
        """Test finding server by name."""
        server = MCPServer("github", "uvx", [], {}, "backend")
        template = MCPTemplate(
            namespace="backend",
            source_url="https://github.com/test/repo",
            source_path=None,
            version="1.0.0",
            description="Test",
            installed_at=datetime.now(),
            servers=[server],
        )

        found = template.get_server_by_name("github")

        assert found is not None
        assert found.name == "github"

    def test_get_server_by_name_not_found(self) -> None:
        """Test finding non-existent server returns None."""
        template = MCPTemplate(
            namespace="backend",
            source_url="https://github.com/test/repo",
            source_path=None,
            version="1.0.0",
            description="Test",
            installed_at=datetime.now(),
            servers=[],
        )

        found = template.get_server_by_name("github")

        assert found is None


class TestEnvironmentConfig:
    """Test EnvironmentConfig dataclass."""

    def test_create_empty(self) -> None:
        """Test creating empty environment config."""
        config = EnvironmentConfig()

        assert config.variables == {}
        assert config.scope == InstallationScope.PROJECT

    def test_get_existing_variable(self) -> None:
        """Test getting existing variable."""
        config = EnvironmentConfig(variables={"API_KEY": "secret123"})

        value = config.get("API_KEY")

        assert value == "secret123"

    def test_get_missing_variable_default(self) -> None:
        """Test getting missing variable with default."""
        config = EnvironmentConfig()

        value = config.get("API_KEY", "default")

        assert value == "default"

    def test_set_valid_variable(self) -> None:
        """Test setting a valid variable."""
        config = EnvironmentConfig()

        config.set("API_KEY", "secret123")

        assert config.variables["API_KEY"] == "secret123"

    def test_set_invalid_variable_name(self) -> None:
        """Test setting variable with invalid name."""
        config = EnvironmentConfig()

        with pytest.raises(ValueError, match="Invalid environment variable name"):
            config.set("api_key", "value")

    def test_has_existing_variable(self) -> None:
        """Test checking if variable exists."""
        config = EnvironmentConfig(variables={"API_KEY": "secret"})

        assert config.has("API_KEY") is True
        assert config.has("OTHER_KEY") is False

    def test_validate_for_server_all_present(self) -> None:
        """Test validation when all required vars are present."""
        config = EnvironmentConfig(variables={"GITHUB_TOKEN": "token123", "API_KEY": "key456"})

        server = MCPServer(
            "github",
            "uvx",
            [],
            {"GITHUB_TOKEN": None, "API_KEY": None},
            "backend",
        )

        missing = config.validate_for_server(server)

        assert missing == []

    def test_validate_for_server_some_missing(self) -> None:
        """Test validation when some required vars are missing."""
        config = EnvironmentConfig(variables={"GITHUB_TOKEN": "token123"})

        server = MCPServer(
            "github",
            "uvx",
            [],
            {"GITHUB_TOKEN": None, "API_KEY": None},
            "backend",
        )

        missing = config.validate_for_server(server)

        assert missing == ["API_KEY"]


class TestActiveSetState:
    """Test ActiveSetState dataclass."""

    def test_create_inactive_state(self) -> None:
        """Test creating inactive state."""
        state = ActiveSetState()

        assert state.namespace is None
        assert state.set_name is None
        assert state.is_active() is False

    def test_activate_set(self) -> None:
        """Test activating a set."""
        mcp_set = MCPSet("backend-dev", "Test", ["github"], "backend")
        servers = [MCPServer("github", "uvx", [], {}, "backend")]

        state = ActiveSetState()
        state.activate_set(mcp_set, servers)

        assert state.namespace == "backend"
        assert state.set_name == "backend-dev"
        assert state.is_active() is True
        assert state.active_servers == ["backend.github"]
        assert state.activated_at is not None

    def test_deactivate(self) -> None:
        """Test deactivating a set."""
        mcp_set = MCPSet("backend-dev", "Test", ["github"], "backend")
        servers = [MCPServer("github", "uvx", [], {}, "backend")]

        state = ActiveSetState()
        state.activate_set(mcp_set, servers)
        state.deactivate()

        assert state.namespace is None
        assert state.set_name is None
        assert state.is_active() is False
        assert state.active_servers == []

    def test_get_active_set_fqn_active(self) -> None:
        """Test getting FQN when set is active."""
        state = ActiveSetState(namespace="backend", set_name="backend-dev")

        assert state.get_active_set_fqn() == "backend.backend-dev"

    def test_get_active_set_fqn_inactive(self) -> None:
        """Test getting FQN when no set is active."""
        state = ActiveSetState()

        assert state.get_active_set_fqn() is None

    def test_invalid_state_namespace_without_set_name(self) -> None:
        """Test that having namespace without set_name is invalid."""
        with pytest.raises(ValueError, match="both be set or both be None"):
            ActiveSetState(namespace="backend", set_name=None)

    def test_invalid_state_servers_without_active_set(self) -> None:
        """Test that having active_servers without active set is invalid."""
        with pytest.raises(ValueError, match="active_servers must be empty"):
            ActiveSetState(active_servers=["backend.github"])
