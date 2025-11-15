"""IDE capability registry for package component support."""

from dataclasses import dataclass

from aiconfigkit.core.models import AIToolType, ComponentType


@dataclass
class IDECapability:
    """
    Defines what component types an IDE supports.

    Tracks which package components (instructions, MCP servers, hooks, etc.)
    can be installed to each AI coding tool.
    """

    tool_type: AIToolType
    tool_name: str
    supported_components: set[ComponentType]
    instructions_directory: str
    instruction_file_extension: str
    supports_project_scope: bool = True
    supports_global_scope: bool = False
    mcp_config_path: str | None = None
    hooks_directory: str | None = None
    commands_directory: str | None = None
    notes: str = ""

    def supports_component(self, component_type: ComponentType) -> bool:
        """
        Check if IDE supports a specific component type.

        Args:
            component_type: Component type to check

        Returns:
            True if supported, False otherwise
        """
        return component_type in self.supported_components


# IDE Capability Registry
# Maps each AI tool to its supported component types and installation paths

CAPABILITY_REGISTRY: dict[AIToolType, IDECapability] = {
    AIToolType.CURSOR: IDECapability(
        tool_type=AIToolType.CURSOR,
        tool_name="Cursor",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.RESOURCE,
        },
        instructions_directory=".cursor/rules/",
        instruction_file_extension=".mdc",
        supports_project_scope=True,
        supports_global_scope=False,
        mcp_config_path=None,  # MCP not yet natively supported
        hooks_directory=None,  # Hooks not supported
        commands_directory=None,  # Commands not supported
        notes=(
            "Cursor uses .mdc (markdown with metadata) files in .cursor/rules/. "
            "Supports project-level only. Global rules use single .cursorrules file."
        ),
    ),
    AIToolType.CLAUDE: IDECapability(
        tool_type=AIToolType.CLAUDE,
        tool_name="Claude Code",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.MCP_SERVER,
            ComponentType.HOOK,
            ComponentType.COMMAND,
            ComponentType.RESOURCE,
        },
        instructions_directory=".claude/rules/",
        instruction_file_extension=".md",
        supports_project_scope=True,
        supports_global_scope=False,
        mcp_config_path="~/.config/claude/config.json",
        hooks_directory=".claude/hooks/",
        commands_directory=".claude/commands/",
        notes=(
            "Claude Code uses .md files in .claude/rules/. "
            "Full support for MCP servers, hooks, and slash commands. "
            "Supports project-level only."
        ),
    ),
    AIToolType.WINSURF: IDECapability(
        tool_type=AIToolType.WINSURF,
        tool_name="Windsurf",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.MCP_SERVER,
            ComponentType.RESOURCE,
        },
        instructions_directory=".windsurf/rules/",
        instruction_file_extension=".md",
        supports_project_scope=True,
        supports_global_scope=False,
        mcp_config_path="~/.config/windsurf/mcp.json",
        hooks_directory=None,  # Hooks not supported
        commands_directory=None,  # Commands not supported
        notes=("Windsurf uses .md files in .windsurf/rules/. " "Supports MCP servers. Project-level only."),
    ),
    AIToolType.COPILOT: IDECapability(
        tool_type=AIToolType.COPILOT,
        tool_name="GitHub Copilot",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.RESOURCE,
        },
        instructions_directory=".github/copilot-instructions.md",
        instruction_file_extension=".md",
        supports_project_scope=True,
        supports_global_scope=False,
        mcp_config_path=None,  # MCP not supported
        hooks_directory=None,  # Hooks not supported
        commands_directory=None,  # Commands not supported
        notes=(
            "GitHub Copilot uses .github/copilot-instructions.md for project-level. "
            "Single file approach, not multi-file. Limited component support."
        ),
    ),
}


def get_capability(tool_type: AIToolType) -> IDECapability:
    """
    Get capability information for an IDE.

    Args:
        tool_type: AI tool type

    Returns:
        IDECapability for the tool

    Raises:
        KeyError: If tool type is not in registry
    """
    return CAPABILITY_REGISTRY[tool_type]


def get_supported_tools_for_component(component_type: ComponentType) -> list[AIToolType]:
    """
    Get list of IDEs that support a specific component type.

    Args:
        component_type: Component type to check

    Returns:
        List of AI tool types that support this component
    """
    supported_tools = []
    for tool_type, capability in CAPABILITY_REGISTRY.items():
        if capability.supports_component(component_type):
            supported_tools.append(tool_type)
    return supported_tools


def validate_component_support(tool_type: AIToolType, component_type: ComponentType) -> bool:
    """
    Validate that an IDE supports a component type.

    Args:
        tool_type: AI tool type
        component_type: Component type to validate

    Returns:
        True if supported, False otherwise
    """
    try:
        capability = get_capability(tool_type)
        return capability.supports_component(component_type)
    except KeyError:
        return False
