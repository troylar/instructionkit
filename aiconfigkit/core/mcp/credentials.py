"""MCP server credential management and .env file handling."""

import logging
import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt

from aiconfigkit.core.models import EnvironmentConfig, InstallationScope, MCPServer
from aiconfigkit.utils.dotenv import ensure_env_gitignored, load_env_config, save_env_config, set_env_variable

logger = logging.getLogger(__name__)
console = Console()


class CredentialManager:
    """Manages MCP server credentials and .env file operations."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize credential manager.

        Args:
            project_root: Project root directory (for project-scoped credentials)
                         If None, uses current directory
        """
        self.project_root = project_root or Path.cwd()
        self.project_env_path = self.project_root / ".instructionkit" / ".env"
        self.global_env_path = Path.home() / ".instructionkit" / "global" / ".env"

    def configure_server(
        self,
        server: MCPServer,
        scope: InstallationScope = InstallationScope.PROJECT,
        non_interactive: bool = False,
    ) -> EnvironmentConfig:
        """
        Configure credentials for an MCP server.

        Args:
            server: MCPServer to configure
            scope: Installation scope (PROJECT or GLOBAL)
            non_interactive: If True, read from environment instead of prompting

        Returns:
            EnvironmentConfig with configured credentials

        Raises:
            ValueError: If non-interactive mode and required vars are missing
        """
        # Get env path for scope
        env_path = self._get_env_path(scope)

        # Load existing config
        env_config = load_env_config(env_path, scope)

        # Get required env vars
        required_vars = server.get_required_env_vars()

        if not required_vars:
            logger.info(f"Server '{server.name}' requires no additional credentials")
            return env_config

        # Configure each required variable
        if non_interactive:
            self._configure_non_interactive(server, required_vars, env_config)
        else:
            self._configure_interactive(server, required_vars, env_config)

        # Save updated config
        save_env_config(env_config)

        logger.info(f"Configured {len(required_vars)} credential(s) for server '{server.name}'")

        return env_config

    def _configure_interactive(
        self,
        server: MCPServer,
        required_vars: list[str],
        env_config: EnvironmentConfig,
    ) -> None:
        """
        Configure credentials interactively with user prompts.

        Args:
            server: MCPServer being configured
            required_vars: List of required environment variable names
            env_config: EnvironmentConfig to update
        """
        console.print(f"\n[bold]Configuring MCP server:[/bold] {server.get_fully_qualified_name()}")
        console.print(f"[dim]Required environment variables: {len(required_vars)}[/dim]\n")

        for var_name in required_vars:
            # Check if already configured
            existing_value = env_config.get(var_name)

            if existing_value:
                # Show masked existing value
                masked_value = self._mask_value(existing_value)
                console.print(f"[dim]{var_name} is already configured: {masked_value}[/dim]")

                # Ask if they want to update
                update = Prompt.ask(
                    "Do you want to update this value?",
                    choices=["y", "n"],
                    default="n",
                )

                if update.lower() == "n":
                    continue

            # Prompt for value (masked input)
            console.print(f"[cyan]Enter value for {var_name}:[/cyan]")
            value = Prompt.ask(f"  {var_name}", password=True)

            if not value:
                console.print("[yellow]Warning: Empty value provided, skipping[/yellow]")
                continue

            # Set the value
            env_config.set(var_name, value)
            console.print(f"[green]✓[/green] Set {var_name}")

    def _configure_non_interactive(
        self,
        server: MCPServer,
        required_vars: list[str],
        env_config: EnvironmentConfig,
    ) -> None:
        """
        Configure credentials non-interactively from environment.

        Args:
            server: MCPServer being configured
            required_vars: List of required environment variable names
            env_config: EnvironmentConfig to update

        Raises:
            ValueError: If required variables are missing from environment
        """
        missing_vars = []

        for var_name in required_vars:
            # Check if already in env_config
            if env_config.has(var_name):
                continue

            # Try to read from current environment
            value = os.getenv(var_name)

            if not value:
                missing_vars.append(var_name)
                continue

            # Set the value
            env_config.set(var_name, value)

        if missing_vars:
            raise ValueError(
                f"Non-interactive mode: Missing required environment variables: {', '.join(missing_vars)}"
            )

    def show_current_credentials(
        self,
        server: MCPServer,
        scope: InstallationScope = InstallationScope.PROJECT,
    ) -> dict[str, str]:
        """
        Show current credential values (masked) for a server.

        Args:
            server: MCPServer to show credentials for
            scope: Installation scope

        Returns:
            Dictionary of variable names to masked values
        """
        env_path = self._get_env_path(scope)
        env_config = load_env_config(env_path, scope)

        required_vars = server.get_required_env_vars()
        credentials = {}

        for var_name in required_vars:
            value = env_config.get(var_name)
            if value:
                credentials[var_name] = self._mask_value(value)
            else:
                credentials[var_name] = "[NOT SET]"

        return credentials

    def validate_credentials(
        self,
        server: MCPServer,
        scope: InstallationScope = InstallationScope.PROJECT,
    ) -> tuple[bool, list[str]]:
        """
        Validate that all required credentials are configured.

        Args:
            server: MCPServer to validate
            scope: Installation scope

        Returns:
            Tuple of (is_valid, missing_vars)
        """
        env_path = self._get_env_path(scope)
        env_config = load_env_config(env_path, scope)

        missing_vars = env_config.validate_for_server(server)

        return (len(missing_vars) == 0, missing_vars)

    def _get_env_path(self, scope: InstallationScope) -> Path:
        """
        Get .env file path for scope.

        Args:
            scope: Installation scope

        Returns:
            Path to .env file
        """
        if scope == InstallationScope.GLOBAL:
            return self.global_env_path
        else:
            return self.project_env_path

    def _mask_value(self, value: str, visible_chars: int = 4) -> str:
        """
        Mask a credential value for display.

        Args:
            value: Value to mask
            visible_chars: Number of characters to show at end

        Returns:
            Masked value (e.g., "****abc123")
        """
        if len(value) <= visible_chars:
            return "*" * len(value)

        masked_part = "*" * (len(value) - visible_chars)
        visible_part = value[-visible_chars:]

        return f"{masked_part}{visible_part}"

    def get_env_config(self, scope: InstallationScope = InstallationScope.PROJECT) -> EnvironmentConfig:
        """
        Get environment configuration for scope.

        Args:
            scope: Installation scope

        Returns:
            EnvironmentConfig
        """
        env_path = self._get_env_path(scope)
        return load_env_config(env_path, scope)

    def merge_scopes(self) -> EnvironmentConfig:
        """
        Merge global and project environment configs.

        Project variables take precedence over global.

        Returns:
            Merged EnvironmentConfig
        """
        from aiconfigkit.utils.dotenv import merge_env_configs

        global_config = self.get_env_config(InstallationScope.GLOBAL)
        project_config = self.get_env_config(InstallationScope.PROJECT)

        return merge_env_configs(project_config, global_config)
