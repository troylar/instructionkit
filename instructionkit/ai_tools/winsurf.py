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

        Returns:
            Path to Windsurf instructions directory

        Raises:
            FileNotFoundError: If Windsurf is not installed
        """
        if not self.is_installed():
            raise FileNotFoundError(f"{self.tool_name} is not installed")

        # Windsurf instructions go in globalStorage directory
        instructions_dir = get_winsurf_config_dir()

        # Ensure directory exists
        instructions_dir.mkdir(parents=True, exist_ok=True)

        return instructions_dir
    
    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Windsurf instructions.

        Windsurf uses markdown (.md) files for instructions.

        Returns:
            File extension including the dot
        """
        return '.md'

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Windsurf instructions.

        Windsurf stores project-specific instructions in a .windsurf directory
        in the project root.

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory
        """
        instructions_dir = project_root / '.windsurf' / 'instructions'
        instructions_dir.mkdir(parents=True, exist_ok=True)
        return instructions_dir
