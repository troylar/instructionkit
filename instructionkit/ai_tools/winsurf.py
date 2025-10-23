"""Winsurf AI tool integration."""

from pathlib import Path

from instructionkit.ai_tools.base import AITool
from instructionkit.core.models import AIToolType
from instructionkit.utils.paths import get_winsurf_config_dir


class WinsurfTool(AITool):
    """Integration for Winsurf AI coding tool."""

    @property
    def tool_type(self) -> AIToolType:
        """Return the AI tool type identifier."""
        return AIToolType.WINSURF

    @property
    def tool_name(self) -> str:
        """Return human-readable tool name."""
        return "Windsurf"

    def is_installed(self) -> bool:
        """
        Check if Windsurf is installed on the system.

        Checks for existence of Windsurf configuration directory.

        Returns:
            True if Windsurf is detected
        """
        try:
            config_dir = get_winsurf_config_dir()
            # Check if parent directory exists
            # Windsurf config dir structure: .../Windsurf/User/globalStorage
            winsurf_base = config_dir.parent.parent
            return winsurf_base.exists()
        except Exception:
            return False

    def get_instructions_directory(self) -> Path:
        """
        Get the directory where Windsurf instructions should be installed.

        Note: Windsurf uses ~/.windsurfrules as a single file for global rules.
        This tool currently only supports project-level installations.

        Returns:
            Path to Windsurf instructions directory

        Raises:
            NotImplementedError: Global installation not supported for Windsurf
        """
        raise NotImplementedError(
            f"{self.tool_name} global installation is not supported. "
            "Windsurf uses a single ~/.windsurfrules file for global rules. "
            "Please use project-level installation instead (--scope project)."
        )

    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Windsurf instructions.

        Windsurf uses markdown (.md) files for rules.

        Returns:
            File extension including the dot
        """
        return '.md'

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Windsurf instructions.

        Windsurf stores project-specific rules in .windsurf/rules/ directory
        in the project root. It supports multiple .md files in this directory.

        Reference:
        - Per-Project: .windsurf/rules/*.md (multiple files)
        - Alternative: .windsurfrules (single file, not used by this tool)

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory (.windsurf/rules/)
        """
        instructions_dir = project_root / '.windsurf' / 'rules'
        instructions_dir.mkdir(parents=True, exist_ok=True)
        return instructions_dir
