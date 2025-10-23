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
            # Claude Code config dir structure: ~/.claude/rules/
            claude_base = config_dir.parent
            return claude_base.exists()
        except Exception:
            return False

    def get_instructions_directory(self) -> Path:
        """
        Get the directory where Claude Code instructions should be installed.

        Note: Global installation is not supported. Claude Code supports both
        single-file (~/.claude/rules.md) and multi-file approaches, but for
        consistency with our multi-file installation pattern, we only support
        project-level installations.

        Returns:
            Path to Claude Code instructions directory

        Raises:
            NotImplementedError: Global installation not supported for Claude Code
        """
        raise NotImplementedError(
            f"{self.tool_name} global installation is not supported. "
            "Please use project-level installation instead (--scope project)."
        )

    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Claude Code instructions.

        Claude Code uses markdown (.md) files for rules.

        Returns:
            File extension including the dot
        """
        return '.md'

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Claude Code instructions.

        Claude Code stores project-specific rules in .claude/rules/ directory
        in the project root. It supports multiple .md files in this directory.

        Reference:
        - Recommended: .claude/rules/*.md (multiple files)
        - Alternative: .claude/rules.md (single file, not used by this tool)

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory (.claude/rules/)
        """
        instructions_dir = project_root / '.claude' / 'rules'
        instructions_dir.mkdir(parents=True, exist_ok=True)
        return instructions_dir
