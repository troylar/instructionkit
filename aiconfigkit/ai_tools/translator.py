"""Component translators for converting package components to IDE-specific formats."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aiconfigkit.core.models import (
    AIToolType,
    CommandComponent,
    ComponentType,
    HookComponent,
    InstructionComponent,
    MCPServerComponent,
    ResourceComponent,
)


@dataclass
class TranslatedComponent:
    """
    Result of translating a package component to IDE-specific format.

    Contains the file content, target path, and any metadata needed
    for installing the component to a specific IDE.
    """

    component_type: ComponentType
    component_name: str
    target_path: str
    content: str
    metadata: dict[str, Any] | None = None
    needs_processing: bool = False

    def __post_init__(self) -> None:
        """Validate translated component."""
        if not self.component_name:
            raise ValueError("Component name cannot be empty")
        if not self.target_path:
            raise ValueError("Target path cannot be empty")


class ComponentTranslator(ABC):
    """
    Abstract base class for translating package components to IDE-specific formats.

    Each IDE (Cursor, Claude Code, Windsurf, Copilot) has a translator that
    converts IDE-agnostic package components into the format expected by that IDE.
    """

    @property
    @abstractmethod
    def tool_type(self) -> AIToolType:
        """Return the AI tool type this translator targets."""
        pass

    @abstractmethod
    def translate_instruction(self, component: InstructionComponent, package_root: Path) -> TranslatedComponent:
        """
        Translate instruction component to IDE-specific format.

        Args:
            component: Instruction component from package
            package_root: Root directory of the package

        Returns:
            Translated component ready for installation
        """
        pass

    @abstractmethod
    def translate_mcp_server(self, component: MCPServerComponent, package_root: Path) -> TranslatedComponent:
        """
        Translate MCP server component to IDE-specific format.

        Args:
            component: MCP server component from package
            package_root: Root directory of the package

        Returns:
            Translated component ready for installation
        """
        pass

    def translate_hook(self, component: HookComponent, package_root: Path) -> TranslatedComponent:
        """
        Translate hook component to IDE-specific format.

        Args:
            component: Hook component from package
            package_root: Root directory of the package

        Returns:
            Translated component ready for installation

        Raises:
            NotImplementedError: If IDE doesn't support hooks
        """
        raise NotImplementedError(f"{self.tool_type.value} does not support hooks")

    def translate_command(self, component: CommandComponent, package_root: Path) -> TranslatedComponent:
        """
        Translate command component to IDE-specific format.

        Args:
            component: Command component from package
            package_root: Root directory of the package

        Returns:
            Translated component ready for installation

        Raises:
            NotImplementedError: If IDE doesn't support commands
        """
        raise NotImplementedError(f"{self.tool_type.value} does not support commands")

    def translate_resource(self, component: ResourceComponent, package_root: Path) -> TranslatedComponent:
        """
        Translate resource component (generic file copy).

        Args:
            component: Resource component from package
            package_root: Root directory of the package

        Returns:
            Translated component ready for installation
        """
        # Read resource file
        resource_path = package_root / component.file
        with open(resource_path, "r") as f:
            content = f.read()

        return TranslatedComponent(
            component_type=ComponentType.RESOURCE,
            component_name=component.name,
            target_path=component.file,
            content=content,
            metadata={"checksum": component.checksum, "size": component.size},
        )


class CursorTranslator(ComponentTranslator):
    """Translator for Cursor IDE (.cursor/rules/*.mdc)."""

    @property
    def tool_type(self) -> AIToolType:
        return AIToolType.CURSOR

    def translate_instruction(self, component: InstructionComponent, package_root: Path) -> TranslatedComponent:
        """Translate instruction to Cursor .mdc format."""
        # Read instruction content
        instruction_path = package_root / component.file
        with open(instruction_path, "r") as f:
            content = f.read()

        # Cursor uses .mdc files with optional frontmatter
        # If instruction has tags, add them as metadata
        if component.tags:
            frontmatter = "---\n"
            frontmatter += f"description: {component.description}\n"
            frontmatter += f"tags: [{', '.join(component.tags)}]\n"
            frontmatter += "---\n\n"
            content = frontmatter + content

        # Target path: .cursor/rules/name.mdc
        target_path = f".cursor/rules/{component.name}.mdc"

        return TranslatedComponent(
            component_type=ComponentType.INSTRUCTION,
            component_name=component.name,
            target_path=target_path,
            content=content,
        )

    def translate_mcp_server(self, component: MCPServerComponent, package_root: Path) -> TranslatedComponent:
        """Cursor doesn't support MCP natively yet."""
        raise NotImplementedError("Cursor does not support MCP servers yet")


class ClaudeCodeTranslator(ComponentTranslator):
    """Translator for Claude Code (.claude/rules/*.md, .claude/hooks/, .claude/commands/)."""

    @property
    def tool_type(self) -> AIToolType:
        return AIToolType.CLAUDE

    def translate_instruction(self, component: InstructionComponent, package_root: Path) -> TranslatedComponent:
        """Translate instruction to Claude Code .md format."""
        # Read instruction content
        instruction_path = package_root / component.file
        with open(instruction_path, "r") as f:
            content = f.read()

        # Target path: .claude/rules/name.md
        target_path = f".claude/rules/{component.name}.md"

        return TranslatedComponent(
            component_type=ComponentType.INSTRUCTION,
            component_name=component.name,
            target_path=target_path,
            content=content,
            metadata={"tags": component.tags} if component.tags else None,
        )

    def translate_mcp_server(self, component: MCPServerComponent, package_root: Path) -> TranslatedComponent:
        """Translate MCP server config to Claude Code format."""
        # Read MCP config
        mcp_path = package_root / component.file
        with open(mcp_path, "r") as f:
            content = f.read()

        # Claude Code MCP config goes in ~/.config/claude/config.json
        # This is a global config, so we mark it for special processing
        return TranslatedComponent(
            component_type=ComponentType.MCP_SERVER,
            component_name=component.name,
            target_path="~/.config/claude/config.json",
            content=content,
            metadata={"credentials": [c.to_dict() for c in component.credentials]},
            needs_processing=True,  # Needs to be merged into existing config
        )

    def translate_hook(self, component: HookComponent, package_root: Path) -> TranslatedComponent:
        """Translate hook script to Claude Code format."""
        # Read hook script
        hook_path = package_root / component.file
        with open(hook_path, "r") as f:
            content = f.read()

        # Target path: .claude/hooks/name.sh (or appropriate extension)
        file_ext = Path(component.file).suffix
        target_path = f".claude/hooks/{component.name}{file_ext}"

        return TranslatedComponent(
            component_type=ComponentType.HOOK,
            component_name=component.name,
            target_path=target_path,
            content=content,
            metadata={"hook_type": component.hook_type},
        )

    def translate_command(self, component: CommandComponent, package_root: Path) -> TranslatedComponent:
        """Translate command script to Claude Code format."""
        # Read command script
        command_path = package_root / component.file
        with open(command_path, "r") as f:
            content = f.read()

        # Target path: .claude/commands/name.sh (or appropriate extension)
        file_ext = Path(component.file).suffix
        target_path = f".claude/commands/{component.name}{file_ext}"

        return TranslatedComponent(
            component_type=ComponentType.COMMAND,
            component_name=component.name,
            target_path=target_path,
            content=content,
            metadata={"command_type": component.command_type},
        )


class WindsurfTranslator(ComponentTranslator):
    """Translator for Windsurf (.windsurf/rules/*.md)."""

    @property
    def tool_type(self) -> AIToolType:
        return AIToolType.WINSURF

    def translate_instruction(self, component: InstructionComponent, package_root: Path) -> TranslatedComponent:
        """Translate instruction to Windsurf .md format."""
        # Read instruction content
        instruction_path = package_root / component.file
        with open(instruction_path, "r") as f:
            content = f.read()

        # Target path: .windsurf/rules/name.md
        target_path = f".windsurf/rules/{component.name}.md"

        return TranslatedComponent(
            component_type=ComponentType.INSTRUCTION,
            component_name=component.name,
            target_path=target_path,
            content=content,
        )

    def translate_mcp_server(self, component: MCPServerComponent, package_root: Path) -> TranslatedComponent:
        """Translate MCP server config to Windsurf format."""
        # Read MCP config
        mcp_path = package_root / component.file
        with open(mcp_path, "r") as f:
            content = f.read()

        # Windsurf MCP config goes in ~/.config/windsurf/mcp.json
        return TranslatedComponent(
            component_type=ComponentType.MCP_SERVER,
            component_name=component.name,
            target_path="~/.config/windsurf/mcp.json",
            content=content,
            metadata={"credentials": [c.to_dict() for c in component.credentials]},
            needs_processing=True,  # Needs to be merged into existing config
        )


class CopilotTranslator(ComponentTranslator):
    """Translator for GitHub Copilot (.github/copilot-instructions.md)."""

    @property
    def tool_type(self) -> AIToolType:
        return AIToolType.COPILOT

    def translate_instruction(self, component: InstructionComponent, package_root: Path) -> TranslatedComponent:
        """Translate instruction to GitHub Copilot format."""
        # Read instruction content
        instruction_path = package_root / component.file
        with open(instruction_path, "r") as f:
            content = f.read()

        # GitHub Copilot uses single file approach
        # Target path: .github/copilot-instructions.md
        target_path = ".github/copilot-instructions.md"

        return TranslatedComponent(
            component_type=ComponentType.INSTRUCTION,
            component_name=component.name,
            target_path=target_path,
            content=content,
            needs_processing=True,  # Needs to be appended to existing file
        )

    def translate_mcp_server(self, component: MCPServerComponent, package_root: Path) -> TranslatedComponent:
        """GitHub Copilot doesn't support MCP."""
        raise NotImplementedError("GitHub Copilot does not support MCP servers")


def get_translator(tool_type: AIToolType) -> ComponentTranslator:
    """
    Factory function to get translator for an AI tool.

    Args:
        tool_type: AI tool type

    Returns:
        ComponentTranslator instance for the tool

    Raises:
        ValueError: If tool type is not supported
    """
    translators: dict[AIToolType, type[ComponentTranslator]] = {
        AIToolType.CURSOR: CursorTranslator,
        AIToolType.CLAUDE: ClaudeCodeTranslator,
        AIToolType.WINSURF: WindsurfTranslator,
        AIToolType.COPILOT: CopilotTranslator,
    }

    translator_class = translators.get(tool_type)
    if not translator_class:
        raise ValueError(f"No translator found for tool type: {tool_type}")

    return translator_class()
