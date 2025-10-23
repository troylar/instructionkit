"""Cursor AI tool integration."""

from pathlib import Path

from instructionkit.ai_tools.base import AITool
from instructionkit.core.models import AIToolType
from instructionkit.utils.paths import get_cursor_config_dir


class CursorTool(AITool):
    """Integration for Cursor AI coding tool."""

    @property
    def tool_type(self) -> AIToolType:
        """Return the AI tool type identifier."""
        return AIToolType.CURSOR

    @property
    def tool_name(self) -> str:
        """Return human-readable tool name."""
        return "Cursor"

    def is_installed(self) -> bool:
        """
        Check if Cursor is installed on the system.

        Checks for existence of Cursor configuration directory.

        Returns:
            True if Cursor is detected
        """
        try:
            config_dir = get_cursor_config_dir()
            # Check if parent directory exists (not necessarily the full path)
            # Cursor config dir structure: .../Cursor/User/globalStorage
            cursor_base = config_dir.parent.parent
            return cursor_base.exists()
        except Exception:
            return False

    def get_instructions_directory(self) -> Path:
        """
        Get the directory where Cursor instructions should be installed.

        Note: Cursor uses .cursorrules as a single file for global rules.
        This tool currently only supports project-level installations.

        Returns:
            Path to Cursor instructions directory

        Raises:
            NotImplementedError: Global installation not supported for Cursor
        """
        raise NotImplementedError(
            f"{self.tool_name} global installation is not supported. "
            "Cursor uses a single .cursorrules file for global rules. "
            "Please use project-level installation instead (--scope project)."
        )

    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Cursor instructions.

        Cursor uses .mdc files (markdown with metadata) for rules.

        Returns:
            File extension including the dot
        """
        return '.mdc'

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Cursor instructions.

        Cursor stores project-specific rules in .cursor/rules/ directory
        in the project root. It supports multiple .mdc files in this directory.

        Reference:
        - Recommended: .cursor/rules/*.mdc (multiple files with metadata)
        - Alternative: .cursorrules (single file, not used by this tool)

        .mdc files can include metadata like:
        ---
        description: Rule description
        globs: ["src/**/*.tsx"]
        alwaysApply: true
        ---

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory (.cursor/rules/)
        """
        instructions_dir = project_root / '.cursor' / 'rules'
        instructions_dir.mkdir(parents=True, exist_ok=True)
        return instructions_dir
