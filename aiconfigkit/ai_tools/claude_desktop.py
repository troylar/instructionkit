"""Claude Desktop MCP integration."""

from pathlib import Path

from aiconfigkit.ai_tools.base import AITool
from aiconfigkit.core.models import AIToolType
from aiconfigkit.utils.paths import get_claude_desktop_config_path


class ClaudeDesktopTool(AITool):
    """Integration for Claude Desktop MCP server configuration."""

    @property
    def tool_type(self) -> AIToolType:
        """Return the AI tool type identifier."""
        return AIToolType.CLAUDE

    @property
    def tool_name(self) -> str:
        """Return human-readable tool name."""
        return "Claude Desktop"

    def is_installed(self) -> bool:
        """
        Check if Claude Desktop is installed on the system.

        Checks for existence of Claude Desktop config directory.

        Returns:
            True if Claude Desktop is detected
        """
        try:
            config_path = get_claude_desktop_config_path()
            # Check if parent directory exists (Claude Desktop install directory)
            return config_path.parent.exists()
        except Exception:
            return False

    def get_instructions_directory(self) -> Path:
        """
        Get the directory where Claude Desktop instructions should be installed.

        Note: Claude Desktop doesn't use instruction files like Claude Code.
        This method is not applicable for MCP configuration.

        Returns:
            Path to instructions directory

        Raises:
            NotImplementedError: Claude Desktop uses MCP config, not instruction files
        """
        raise NotImplementedError(
            f"{self.tool_name} uses MCP configuration instead of instruction files. "
            "Use get_mcp_config_path() instead."
        )

    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Claude Desktop instructions.

        Returns:
            File extension including the dot

        Raises:
            NotImplementedError: Claude Desktop uses MCP config, not instruction files
        """
        raise NotImplementedError(f"{self.tool_name} uses MCP configuration instead of instruction files.")

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Claude Desktop instructions.

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory

        Raises:
            NotImplementedError: Claude Desktop uses MCP config, not instruction files
        """
        raise NotImplementedError(f"{self.tool_name} uses MCP configuration instead of instruction files.")

    def get_mcp_config_path(self) -> Path:
        """
        Get the path to the Claude Desktop MCP configuration file.

        Claude Desktop stores MCP server configurations in claude_desktop_config.json.
        The file location is platform-specific:
        - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
        - Linux: ~/.config/Claude/claude_desktop_config.json
        - Windows: %APPDATA%\\Claude\\claude_desktop_config.json

        Returns:
            Path to claude_desktop_config.json
        """
        return get_claude_desktop_config_path()
