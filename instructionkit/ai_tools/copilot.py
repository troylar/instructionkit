"""GitHub Copilot AI tool integration."""

from pathlib import Path

from instructionkit.ai_tools.base import AITool
from instructionkit.core.models import AIToolType
from instructionkit.utils.paths import get_copilot_config_dir


class CopilotTool(AITool):
    """Integration for GitHub Copilot (VS Code extension)."""

    @property
    def tool_type(self) -> AIToolType:
        """Return the AI tool type identifier."""
        return AIToolType.COPILOT

    @property
    def tool_name(self) -> str:
        """Return human-readable tool name."""
        return "GitHub Copilot"

    def is_installed(self) -> bool:
        """
        Check if GitHub Copilot is installed on the system.

        Checks for existence of VS Code and Copilot extension directory.

        Returns:
            True if Copilot is detected
        """
        try:
            config_dir = get_copilot_config_dir()
            # Check if the Copilot extension directory exists
            # VS Code structure: .../Code/User/globalStorage/github.copilot
            return config_dir.parent.exists()
        except Exception:
            return False

    def get_instructions_directory(self) -> Path:
        """
        Get the directory where Copilot instructions should be installed.

        Note: GitHub Copilot uses .github/copilot-instructions.md as a single file
        for project-level instructions. Global instructions are not officially supported.
        This tool currently only supports project-level installations.

        Returns:
            Path to Copilot instructions directory

        Raises:
            NotImplementedError: Global installation not supported for GitHub Copilot
        """
        raise NotImplementedError(
            f"{self.tool_name} global installation is not supported. "
            "GitHub Copilot uses project-level instructions only. "
            "Please use project-level installation instead (--scope project)."
        )

    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Copilot instructions.

        Copilot uses markdown (.md) files for instructions.

        Returns:
            File extension including the dot
        """
        return '.md'

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Copilot instructions.

        GitHub Copilot stores project-specific instructions in .github/instructions/
        directory in the project root. It supports multiple .md files in this directory.

        Reference:
        - Path-specific: .github/instructions/*.instructions.md (multiple files)
        - Alternative: .github/copilot-instructions.md (single file, not used by this tool)

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory (.github/instructions/)
        """
        instructions_dir = project_root / '.github' / 'instructions'
        instructions_dir.mkdir(parents=True, exist_ok=True)
        return instructions_dir
