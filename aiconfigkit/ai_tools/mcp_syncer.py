"""Cross-tool MCP server synchronization orchestration."""

import json
import logging
from pathlib import Path
from typing import Any, Optional

from aiconfigkit.ai_tools.base import AITool
from aiconfigkit.ai_tools.detector import AIToolDetector
from aiconfigkit.core.mcp.credentials import CredentialManager
from aiconfigkit.core.mcp.manager import MCPManager
from aiconfigkit.core.models import EnvironmentConfig, InstallationScope, MCPServer, MCPTemplate
from aiconfigkit.utils.atomic_write import atomic_write

logger = logging.getLogger(__name__)


class MCPSyncResult:
    """Result of MCP synchronization operation."""

    def __init__(self) -> None:
        """Initialize sync result."""
        self.synced_tools: list[str] = []
        self.skipped_tools: list[tuple[str, str]] = []  # (tool_name, reason)
        self.synced_servers: list[str] = []
        self.skipped_servers: list[tuple[str, str]] = []  # (server_name, reason)

    def add_synced_tool(self, tool_name: str) -> None:
        """Mark tool as successfully synced."""
        self.synced_tools.append(tool_name)

    def add_skipped_tool(self, tool_name: str, reason: str) -> None:
        """Mark tool as skipped with reason."""
        self.skipped_tools.append((tool_name, reason))

    def add_synced_server(self, server_name: str) -> None:
        """Mark server as successfully synced."""
        if server_name not in self.synced_servers:
            self.synced_servers.append(server_name)

    def add_skipped_server(self, server_name: str, reason: str) -> None:
        """Mark server as skipped with reason."""
        if not any(s[0] == server_name for s in self.skipped_servers):
            self.skipped_servers.append((server_name, reason))

    @property
    def success(self) -> bool:
        """Check if any tools were successfully synced."""
        return len(self.synced_tools) > 0


class MCPSyncer:
    """Orchestrates MCP server synchronization to AI tools."""

    def __init__(
        self,
        library_root: Optional[Path] = None,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize MCP syncer.

        Args:
            library_root: Root directory for MCP library (defaults to ~/.instructionkit/library/)
            project_root: Project root directory (defaults to current directory)
        """
        self.library_root = library_root or Path.home() / ".instructionkit" / "library"
        self.project_root = project_root or Path.cwd()

        self.mcp_manager = MCPManager(self.library_root)
        self.cred_manager = CredentialManager(self.project_root)
        self.tool_detector = AIToolDetector()

    def sync_all(
        self,
        tool_names: Optional[list[str]] = None,
        scope: InstallationScope = InstallationScope.PROJECT,
        create_backup: bool = True,
        dry_run: bool = False,
    ) -> MCPSyncResult:
        """
        Sync all MCP servers to AI tools.

        Args:
            tool_names: List of tool names to sync to (None = all detected tools)
            scope: Scope to load configurations from (PROJECT, GLOBAL, or merge)
            create_backup: Create backup of config files before modifying
            dry_run: Don't actually write configs, just report what would be done

        Returns:
            MCPSyncResult with sync status
        """
        result = MCPSyncResult()

        # Load all installed MCP templates
        templates = self._load_templates(scope)

        if not templates:
            logger.info("No MCP templates installed")
            return result

        # Collect all MCP servers from templates
        all_servers: list[MCPServer] = []
        for template in templates:
            all_servers.extend(template.servers)

        if not all_servers:
            logger.info("No MCP servers found in installed templates")
            return result

        # Load environment configuration
        env_config = self.cred_manager.merge_scopes()

        # Validate servers have required credentials
        validated_servers = []
        for server in all_servers:
            is_valid, missing = self._validate_server_credentials(server, env_config)
            if is_valid:
                validated_servers.append(server)
                result.add_synced_server(server.get_fully_qualified_name())
            else:
                reason = f"Missing credentials: {', '.join(missing)}"
                result.add_skipped_server(server.get_fully_qualified_name(), reason)
                logger.warning(f"Skipping {server.get_fully_qualified_name()}: {reason}")

        if not validated_servers:
            logger.warning("No servers have complete credentials configured")
            return result

        # Resolve environment variables in server configurations
        resolved_servers = self._resolve_env_vars(validated_servers, env_config)

        # Get tools to sync to
        if tool_names and "all" not in tool_names:
            tools = []
            for name in tool_names:
                tool = self.tool_detector.get_tool_by_name(name)
                if tool:
                    tools.append(tool)
                else:
                    result.add_skipped_tool(name, "Unknown tool")
        else:
            tools = self.tool_detector.detect_installed_tools()

        if not tools:
            logger.warning("No AI tools detected")
            return result

        # Sync to each tool
        for tool in tools:
            tool_name = tool.tool_type.value
            try:
                logger.info(f"Syncing MCP servers to {tool.tool_name}")

                if dry_run:
                    logger.info(f"[DRY RUN] Would sync {len(resolved_servers)} servers to {tool.tool_name}")
                    result.add_synced_tool(tool_name)
                else:
                    # Check if tool has MCP config support
                    if not hasattr(tool, "get_mcp_config_path"):
                        result.add_skipped_tool(tool_name, "MCP config not supported")
                        logger.warning(f"{tool.tool_name} does not support MCP configuration sync")
                        continue

                    # Sync servers to tool
                    self._sync_to_tool(tool, resolved_servers, create_backup)
                    result.add_synced_tool(tool_name)
                    logger.info(f"Successfully synced to {tool.tool_name}")

            except Exception as e:
                result.add_skipped_tool(tool_name, str(e))
                logger.error(f"Failed to sync to {tool.tool_name}: {e}")

        return result

    def _load_templates(self, scope: InstallationScope) -> list[MCPTemplate]:
        """
        Load all installed MCP templates.

        Args:
            scope: Scope to load from

        Returns:
            List of MCPTemplate objects
        """
        templates = []

        # Load project templates
        if scope in (InstallationScope.PROJECT, InstallationScope.PROJECT):
            templates.extend(self.mcp_manager.list_templates(InstallationScope.PROJECT))

        # Load global templates
        if scope == InstallationScope.GLOBAL:
            templates.extend(self.mcp_manager.list_templates(InstallationScope.GLOBAL))

        return templates

    def _validate_server_credentials(self, server: MCPServer, env_config: EnvironmentConfig) -> tuple[bool, list[str]]:
        """
        Validate that server has all required credentials.

        Args:
            server: MCP server to validate
            env_config: Environment configuration

        Returns:
            Tuple of (is_valid, missing_vars)
        """
        required_vars = server.get_required_env_vars()
        missing_vars = []

        for var_name in required_vars:
            if not env_config.has(var_name):
                missing_vars.append(var_name)

        return (len(missing_vars) == 0, missing_vars)

    def _resolve_env_vars(self, servers: list[MCPServer], env_config: EnvironmentConfig) -> list[dict[str, Any]]:
        """
        Resolve environment variables in server configurations.

        Args:
            servers: List of MCP servers
            env_config: Environment configuration

        Returns:
            List of resolved server configurations as dicts
        """
        resolved = []

        for server in servers:
            # Build server config dict
            config: dict[str, Any] = {
                "command": server.command,
                "args": server.args,
            }

            # Resolve environment variables
            if server.env:
                resolved_env = {}
                for var_name, var_value in server.env.items():
                    # Get value from env_config
                    actual_value = env_config.get(var_name)
                    if actual_value:
                        resolved_env[var_name] = actual_value

                if resolved_env:
                    config["env"] = resolved_env

            # Add to resolved list with server name
            resolved.append(
                {
                    "name": server.get_fully_qualified_name(),
                    "config": config,
                }
            )

        return resolved

    def _sync_to_tool(self, tool: AITool, servers: list[dict[str, Any]], create_backup: bool) -> None:
        """
        Sync MCP servers to a specific AI tool.

        Args:
            tool: AITool instance
            servers: List of resolved server configurations
            create_backup: Create backup before modifying

        Raises:
            RuntimeError: If sync fails
        """
        config_path = tool.get_mcp_config_path()

        # Load existing config if it exists
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {}

        # Ensure mcpServers section exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Update mcpServers with our servers
        for server in servers:
            config["mcpServers"][server["name"]] = server["config"]

        # Write config atomically
        with atomic_write(config_path, create_backup=create_backup) as f:
            json.dump(config, f, indent=2)
