"""Unit tests for component translators."""

from pathlib import Path

import pytest

from aiconfigkit.ai_tools.translator import (
    ClaudeCodeTranslator,
    CopilotTranslator,
    CursorTranslator,
    TranslatedComponent,
    WindsurfTranslator,
    get_translator,
)
from aiconfigkit.core.models import (
    AIToolType,
    CommandComponent,
    ComponentType,
    CredentialDescriptor,
    HookComponent,
    InstructionComponent,
    MCPServerComponent,
    ResourceComponent,
)


@pytest.fixture
def temp_package(tmp_path: Path) -> Path:
    """Create a temporary package directory with sample files."""
    package_dir = tmp_path / "test-package"
    package_dir.mkdir()

    # Create instruction file
    (package_dir / "instructions").mkdir()
    (package_dir / "instructions" / "test.md").write_text("# Test Instruction\n\nThis is a test.")

    # Create MCP config file
    (package_dir / "mcp").mkdir()
    (package_dir / "mcp" / "server.json").write_text('{"mcpServers": {}}')

    # Create hook file
    (package_dir / "hooks").mkdir()
    (package_dir / "hooks" / "pre-commit.sh").write_text("#!/bin/bash\necho 'hook'")

    # Create command file
    (package_dir / "commands").mkdir()
    (package_dir / "commands" / "test-cmd.sh").write_text("#!/bin/bash\necho 'command'")

    # Create resource file
    (package_dir / "resources").mkdir()
    (package_dir / "resources" / "config.json").write_text('{"setting": "value"}')

    return package_dir


class TestTranslatedComponent:
    """Test TranslatedComponent dataclass."""

    def test_create_translated_component(self) -> None:
        """Test creating a translated component."""
        component = TranslatedComponent(
            component_type=ComponentType.INSTRUCTION,
            component_name="test",
            target_path=".cursor/rules/test.mdc",
            content="# Test",
        )

        assert component.component_type == ComponentType.INSTRUCTION
        assert component.component_name == "test"
        assert component.target_path == ".cursor/rules/test.mdc"
        assert component.content == "# Test"
        assert component.metadata is None
        assert component.needs_processing is False

    def test_empty_name_raises_error(self) -> None:
        """Test that empty component name raises ValueError."""
        with pytest.raises(ValueError, match="Component name cannot be empty"):
            TranslatedComponent(
                component_type=ComponentType.INSTRUCTION,
                component_name="",
                target_path=".cursor/rules/test.mdc",
                content="# Test",
            )

    def test_empty_target_path_raises_error(self) -> None:
        """Test that empty target path raises ValueError."""
        with pytest.raises(ValueError, match="Target path cannot be empty"):
            TranslatedComponent(
                component_type=ComponentType.INSTRUCTION,
                component_name="test",
                target_path="",
                content="# Test",
            )


class TestCursorTranslator:
    """Test CursorTranslator."""

    def test_tool_type(self) -> None:
        """Test translator tool type."""
        translator = CursorTranslator()
        assert translator.tool_type == AIToolType.CURSOR

    def test_translate_instruction(self, temp_package: Path) -> None:
        """Test translating instruction to Cursor format."""
        translator = CursorTranslator()
        component = InstructionComponent(
            name="test-instruction",
            file="instructions/test.md",
            description="Test instruction",
            tags=["test", "demo"],
        )

        result = translator.translate_instruction(component, temp_package)

        assert result.component_type == ComponentType.INSTRUCTION
        assert result.component_name == "test-instruction"
        assert result.target_path == ".cursor/rules/test-instruction.mdc"
        assert "Test Instruction" in result.content
        assert "tags: [test, demo]" in result.content

    def test_translate_instruction_no_tags(self, temp_package: Path) -> None:
        """Test translating instruction without tags."""
        translator = CursorTranslator()
        component = InstructionComponent(
            name="test",
            file="instructions/test.md",
            description="Test",
        )

        result = translator.translate_instruction(component, temp_package)

        assert "Test Instruction" in result.content
        # No frontmatter added when no tags
        assert not result.content.startswith("---")

    def test_translate_mcp_server_raises_error(self, temp_package: Path) -> None:
        """Test that translating MCP server raises NotImplementedError."""
        translator = CursorTranslator()
        component = MCPServerComponent(
            name="test-server",
            file="mcp/server.json",
            description="Test server",
        )

        with pytest.raises(NotImplementedError, match="does not support MCP"):
            translator.translate_mcp_server(component, temp_package)

    def test_translate_hook_raises_error(self, temp_package: Path) -> None:
        """Test that translating hook raises NotImplementedError."""
        translator = CursorTranslator()
        component = HookComponent(
            name="pre-commit",
            file="hooks/pre-commit.sh",
            description="Pre-commit hook",
            hook_type="pre-commit",
        )

        with pytest.raises(NotImplementedError, match="does not support hooks"):
            translator.translate_hook(component, temp_package)

    def test_translate_command_raises_error(self, temp_package: Path) -> None:
        """Test that translating command raises NotImplementedError."""
        translator = CursorTranslator()
        component = CommandComponent(
            name="test-cmd",
            file="commands/test-cmd.sh",
            description="Test command",
            command_type="shell",
        )

        with pytest.raises(NotImplementedError, match="does not support commands"):
            translator.translate_command(component, temp_package)

    def test_translate_resource(self, temp_package: Path) -> None:
        """Test translating resource file."""
        translator = CursorTranslator()
        component = ResourceComponent(
            name="config",
            file="resources/config.json",
            description="Config file",
            install_path=".editorconfig",  # Custom install path
            checksum="sha256:abc123",
            size=1024,
        )

        result = translator.translate_resource(component, temp_package)

        assert result.component_type == ComponentType.RESOURCE
        assert result.component_name == "config"
        assert result.target_path == ".editorconfig"  # Uses install_path
        assert result.content == ""  # Content not read, file copied directly
        assert result.metadata["checksum"] == "sha256:abc123"
        assert result.metadata["source_path"] == str(temp_package / "resources/config.json")


class TestClaudeCodeTranslator:
    """Test ClaudeCodeTranslator."""

    def test_tool_type(self) -> None:
        """Test translator tool type."""
        translator = ClaudeCodeTranslator()
        assert translator.tool_type == AIToolType.CLAUDE

    def test_translate_instruction(self, temp_package: Path) -> None:
        """Test translating instruction to Claude Code format."""
        translator = ClaudeCodeTranslator()
        component = InstructionComponent(
            name="test-instruction",
            file="instructions/test.md",
            description="Test instruction",
            tags=["test"],
        )

        result = translator.translate_instruction(component, temp_package)

        assert result.component_type == ComponentType.INSTRUCTION
        assert result.component_name == "test-instruction"
        assert result.target_path == ".claude/rules/test-instruction.md"
        assert "Test Instruction" in result.content
        assert result.metadata["tags"] == ["test"]

    def test_translate_mcp_server(self, temp_package: Path) -> None:
        """Test translating MCP server to Claude Code format."""
        translator = ClaudeCodeTranslator()
        cred = CredentialDescriptor(
            name="API_KEY",
            description="API key",
            required=True,
        )
        component = MCPServerComponent(
            name="test-server",
            file="mcp/server.json",
            description="Test server",
            credentials=[cred],
        )

        result = translator.translate_mcp_server(component, temp_package)

        assert result.component_type == ComponentType.MCP_SERVER
        assert result.component_name == "test-server"
        assert result.target_path == ".claude/mcp/test-server.json"  # Project-specific path
        assert result.needs_processing is False  # No longer needs merging
        assert len(result.metadata["credentials"]) == 1

    def test_translate_hook(self, temp_package: Path) -> None:
        """Test translating hook to Claude Code format."""
        translator = ClaudeCodeTranslator()
        component = HookComponent(
            name="pre-commit",
            file="hooks/pre-commit.sh",
            description="Pre-commit hook",
            hook_type="pre-commit",
        )

        result = translator.translate_hook(component, temp_package)

        assert result.component_type == ComponentType.HOOK
        assert result.component_name == "pre-commit"
        assert result.target_path == ".claude/hooks/pre-commit.sh"
        assert "echo 'hook'" in result.content
        assert result.metadata["hook_type"] == "pre-commit"

    def test_translate_command(self, temp_package: Path) -> None:
        """Test translating command to Claude Code format."""
        translator = ClaudeCodeTranslator()
        component = CommandComponent(
            name="test-cmd",
            file="commands/test-cmd.sh",
            description="Test command",
            command_type="shell",
        )

        result = translator.translate_command(component, temp_package)

        assert result.component_type == ComponentType.COMMAND
        assert result.component_name == "test-cmd"
        assert result.target_path == ".claude/commands/test-cmd.sh"
        assert "echo 'command'" in result.content
        assert result.metadata["command_type"] == "shell"


class TestWindsurfTranslator:
    """Test WindsurfTranslator."""

    def test_tool_type(self) -> None:
        """Test translator tool type."""
        translator = WindsurfTranslator()
        assert translator.tool_type == AIToolType.WINSURF

    def test_translate_instruction(self, temp_package: Path) -> None:
        """Test translating instruction to Windsurf format."""
        translator = WindsurfTranslator()
        component = InstructionComponent(
            name="test-instruction",
            file="instructions/test.md",
            description="Test instruction",
        )

        result = translator.translate_instruction(component, temp_package)

        assert result.component_type == ComponentType.INSTRUCTION
        assert result.component_name == "test-instruction"
        assert result.target_path == ".windsurf/rules/test-instruction.md"
        assert "Test Instruction" in result.content

    def test_translate_mcp_server(self, temp_package: Path) -> None:
        """Test translating MCP server to Windsurf format."""
        translator = WindsurfTranslator()
        component = MCPServerComponent(
            name="test-server",
            file="mcp/server.json",
            description="Test server",
        )

        result = translator.translate_mcp_server(component, temp_package)

        assert result.component_type == ComponentType.MCP_SERVER
        assert result.component_name == "test-server"
        assert result.target_path == ".windsurf/mcp/test-server.json"  # Project-specific path
        assert result.needs_processing is False  # No longer needs merging

    def test_translate_hook_raises_error(self, temp_package: Path) -> None:
        """Test that translating hook raises NotImplementedError."""
        translator = WindsurfTranslator()
        component = HookComponent(
            name="pre-commit",
            file="hooks/pre-commit.sh",
            description="Pre-commit hook",
            hook_type="pre-commit",
        )

        with pytest.raises(NotImplementedError, match="does not support hooks"):
            translator.translate_hook(component, temp_package)

    def test_translate_command_raises_error(self, temp_package: Path) -> None:
        """Test that translating command raises NotImplementedError."""
        translator = WindsurfTranslator()
        component = CommandComponent(
            name="test-cmd",
            file="commands/test-cmd.sh",
            description="Test command",
            command_type="shell",
        )

        with pytest.raises(NotImplementedError, match="does not support commands"):
            translator.translate_command(component, temp_package)


class TestCopilotTranslator:
    """Test CopilotTranslator."""

    def test_tool_type(self) -> None:
        """Test translator tool type."""
        translator = CopilotTranslator()
        assert translator.tool_type == AIToolType.COPILOT

    def test_translate_instruction(self, temp_package: Path) -> None:
        """Test translating instruction to GitHub Copilot format."""
        translator = CopilotTranslator()
        component = InstructionComponent(
            name="test-instruction",
            file="instructions/test.md",
            description="Test instruction",
        )

        result = translator.translate_instruction(component, temp_package)

        assert result.component_type == ComponentType.INSTRUCTION
        assert result.component_name == "test-instruction"
        assert result.target_path == ".github/instructions/test-instruction.md"  # Directory structure
        assert "Test Instruction" in result.content
        assert result.needs_processing is False  # Multi-file approach

    def test_translate_mcp_server_raises_error(self, temp_package: Path) -> None:
        """Test that translating MCP server raises NotImplementedError."""
        translator = CopilotTranslator()
        component = MCPServerComponent(
            name="test-server",
            file="mcp/server.json",
            description="Test server",
        )

        with pytest.raises(NotImplementedError, match="does not support MCP"):
            translator.translate_mcp_server(component, temp_package)

    def test_translate_command_raises_error(self, temp_package: Path) -> None:
        """Test that translating command raises NotImplementedError."""
        translator = CopilotTranslator()
        component = CommandComponent(
            name="test-cmd",
            file="commands/test-cmd.sh",
            description="Test command",
            command_type="shell",
        )

        with pytest.raises(NotImplementedError, match="does not support commands"):
            translator.translate_command(component, temp_package)


class TestGetTranslator:
    """Test get_translator factory function."""

    def test_get_cursor_translator(self) -> None:
        """Test getting Cursor translator."""
        translator = get_translator(AIToolType.CURSOR)
        assert isinstance(translator, CursorTranslator)
        assert translator.tool_type == AIToolType.CURSOR

    def test_get_claude_translator(self) -> None:
        """Test getting Claude Code translator."""
        translator = get_translator(AIToolType.CLAUDE)
        assert isinstance(translator, ClaudeCodeTranslator)
        assert translator.tool_type == AIToolType.CLAUDE

    def test_get_windsurf_translator(self) -> None:
        """Test getting Windsurf translator."""
        translator = get_translator(AIToolType.WINSURF)
        assert isinstance(translator, WindsurfTranslator)
        assert translator.tool_type == AIToolType.WINSURF

    def test_get_copilot_translator(self) -> None:
        """Test getting GitHub Copilot translator."""
        translator = get_translator(AIToolType.COPILOT)
        assert isinstance(translator, CopilotTranslator)
        assert translator.tool_type == AIToolType.COPILOT

    def test_get_invalid_translator_raises_error(self) -> None:
        """Test that getting translator for invalid tool raises ValueError."""
        with pytest.raises(ValueError, match="No translator found"):
            get_translator("INVALID_TOOL")  # type: ignore
