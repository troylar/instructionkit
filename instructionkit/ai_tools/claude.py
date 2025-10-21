"""Claude Code AI tool integration."""

from pathlib import Path

from instructionkit.ai_tools.base import AITool
from instructionkit.core.models import AIToolType
from instructionkit.utils.paths import get_claude_config_dir


class ClaudeTool(AITool):
    """Integration for Claude Code AI coding tool."""
    
    @property
    def tool_type(self) -> AIToolType:
        """Return the AI tool type identifier."""
        return AIToolType.CLAUDE
    
    @property
    def tool_name(self) -> str:
        """Return human-readable tool name."""
        return "Claude Code"
    
    def is_installed(self) -> bool:
        """
        Check if Claude Code is installed on the system.
        
        Checks for existence of Claude configuration directory.
        
        Returns:
            True if Claude Code is detected
        """
        try:
            config_dir = get_claude_config_dir()
            # Check if parent directory exists
            # Claude config dir structure: .../Claude/instructions
            claude_base = config_dir.parent
            return claude_base.exists()
        except Exception:
            return False
    
    def get_instructions_directory(self) -> Path:
        """
        Get the directory where Claude Code instructions should be installed.
        
        Returns:
            Path to Claude Code instructions directory
            
        Raises:
            FileNotFoundError: If Claude Code is not installed
        """
        if not self.is_installed():
            raise FileNotFoundError(f"{self.tool_name} is not installed")
        
        # Claude instructions go in instructions directory
        instructions_dir = get_claude_config_dir()
        
        # Ensure directory exists
        instructions_dir.mkdir(parents=True, exist_ok=True)
        
        return instructions_dir
    
    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Claude Code instructions.

        Claude Code uses markdown (.md) files for instructions.

        Returns:
            File extension including the dot
        """
        return '.md'

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Claude Code instructions.

        Claude Code stores project-specific instructions in a .claude directory
        in the project root.

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory
        """
        instructions_dir = project_root / '.claude' / 'instructions'
        instructions_dir.mkdir(parents=True, exist_ok=True)
        return instructions_dir
