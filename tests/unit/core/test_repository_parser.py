"""Unit tests for repository parsing."""

from pathlib import Path

import pytest
import yaml

from aiconfigkit.core.models import AIToolType
from aiconfigkit.core.repository import RepositoryParser, validate_repository_structure


class TestRepositoryParser:
    """Test RepositoryParser class."""

    def test_parse_basic_repository(self, tmp_path: Path) -> None:
        """Test parsing basic repository."""
        # Create metadata file
        metadata = {
            "name": "Test Repository",
            "description": "Test description",
            "version": "1.0.0",
            "instructions": [
                {
                    "name": "test-instruction",
                    "description": "Test instruction",
                    "file": "instructions/test.md",
                    "tags": ["test", "example"],
                }
            ],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        metadata_file = repo_path / "templatekit.yaml"
        metadata_file.write_text(yaml.dump(metadata))

        # Create instruction file
        inst_dir = repo_path / "instructions"
        inst_dir.mkdir()
        (inst_dir / "test.md").write_text("# Test Instruction\nContent here")

        # Parse repository
        parser = RepositoryParser(repo_path)
        repo = parser.parse()

        assert repo.metadata["name"] == "Test Repository"
        assert repo.metadata["description"] == "Test description"
        assert repo.metadata["version"] == "1.0.0"
        assert len(repo.instructions) == 1
        assert repo.instructions[0].name == "test-instruction"
        assert repo.instructions[0].description == "Test instruction"
        assert repo.instructions[0].tags == ["test", "example"]

    def test_parse_with_bundles(self, tmp_path: Path) -> None:
        """Test parsing repository with bundles."""
        metadata = {
            "name": "Test Repository",
            "instructions": [
                {"name": "inst1", "description": "Instruction 1", "file": "inst1.md"},
                {"name": "inst2", "description": "Instruction 2", "file": "inst2.md"},
            ],
            "bundles": [
                {
                    "name": "test-bundle",
                    "description": "Bundle description",
                    "instructions": ["inst1", "inst2"],
                    "tags": ["bundle"],
                }
            ],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "inst1.md").write_text("Instruction 1")
        (repo_path / "inst2.md").write_text("Instruction 2")

        parser = RepositoryParser(repo_path)
        repo = parser.parse()

        assert len(repo.bundles) == 1
        assert repo.bundles[0].name == "test-bundle"
        assert repo.bundles[0].description == "Bundle description"
        assert repo.bundles[0].instructions == ["inst1", "inst2"]
        assert repo.bundles[0].tags == ["bundle"]

    def test_parse_missing_metadata_file(self, tmp_path: Path) -> None:
        """Test parsing with missing metadata file."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        parser = RepositoryParser(repo_path)

        with pytest.raises(FileNotFoundError, match="Repository metadata file not found"):
            parser.parse()

    def test_parse_empty_metadata_file(self, tmp_path: Path) -> None:
        """Test parsing with empty metadata file."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text("")

        parser = RepositoryParser(repo_path)

        with pytest.raises(ValueError, match="Repository metadata file is empty"):
            parser.parse()

    def test_parse_instruction_missing_name(self, tmp_path: Path) -> None:
        """Test parsing instruction without name."""
        metadata = {
            "name": "Test",
            "instructions": [{"file": "test.md"}],  # Missing name
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        parser = RepositoryParser(repo_path)

        with pytest.raises(ValueError, match="Instruction missing required 'name' field"):
            parser.parse()

    def test_parse_instruction_missing_file(self, tmp_path: Path) -> None:
        """Test parsing instruction without file."""
        metadata = {
            "name": "Test",
            "instructions": [{"name": "test-inst"}],  # Missing file
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        parser = RepositoryParser(repo_path)

        with pytest.raises(ValueError, match="missing 'file' field"):
            parser.parse()

    def test_parse_instruction_file_not_found(self, tmp_path: Path) -> None:
        """Test parsing instruction with non-existent file."""
        metadata = {
            "name": "Test",
            "instructions": [{"name": "test", "file": "nonexistent.md"}],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        parser = RepositoryParser(repo_path)

        with pytest.raises(FileNotFoundError, match="Instruction file not found"):
            parser.parse()

    def test_parse_instruction_with_ai_tools(self, tmp_path: Path) -> None:
        """Test parsing instruction with AI tools."""
        metadata = {
            "name": "Test",
            "instructions": [
                {
                    "name": "test",
                    "description": "Test instruction",
                    "file": "test.md",
                    "ai_tools": ["claude", "cursor", "winsurf"],
                }
            ],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "test.md").write_text("Content")

        parser = RepositoryParser(repo_path)
        repo = parser.parse()

        assert len(repo.instructions[0].ai_tools) == 3
        assert AIToolType.CLAUDE in repo.instructions[0].ai_tools
        assert AIToolType.CURSOR in repo.instructions[0].ai_tools
        assert AIToolType.WINSURF in repo.instructions[0].ai_tools

    def test_parse_instruction_with_unknown_ai_tools(self, tmp_path: Path) -> None:
        """Test parsing instruction with unknown AI tools (should skip them)."""
        metadata = {
            "name": "Test",
            "instructions": [
                {
                    "name": "test",
                    "description": "Test instruction",
                    "file": "test.md",
                    "ai_tools": ["claude", "unknown-tool", "cursor"],
                }
            ],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "test.md").write_text("Content")

        parser = RepositoryParser(repo_path)
        repo = parser.parse()

        # Should skip unknown-tool
        assert len(repo.instructions[0].ai_tools) == 2
        assert AIToolType.CLAUDE in repo.instructions[0].ai_tools
        assert AIToolType.CURSOR in repo.instructions[0].ai_tools

    def test_parse_bundle_missing_name(self, tmp_path: Path) -> None:
        """Test parsing bundle without name."""
        metadata = {
            "name": "Test",
            "bundles": [{"instructions": ["inst1"]}],  # Missing name
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        parser = RepositoryParser(repo_path)

        with pytest.raises(ValueError, match="Bundle missing required 'name' field"):
            parser.parse()

    def test_parse_bundle_no_instructions(self, tmp_path: Path) -> None:
        """Test parsing bundle with no instructions."""
        metadata = {
            "name": "Test",
            "bundles": [{"name": "test-bundle", "instructions": []}],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        parser = RepositoryParser(repo_path)

        with pytest.raises(ValueError, match="has no instructions"):
            parser.parse()

    def test_get_instruction_by_name(self, tmp_path: Path) -> None:
        """Test getting instruction by name."""
        metadata = {
            "name": "Test",
            "instructions": [
                {"name": "inst1", "description": "Instruction 1", "file": "inst1.md"},
                {"name": "inst2", "description": "Instruction 2", "file": "inst2.md"},
            ],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "inst1.md").write_text("Content 1")
        (repo_path / "inst2.md").write_text("Content 2")

        parser = RepositoryParser(repo_path)
        instruction = parser.get_instruction_by_name("inst2")

        assert instruction is not None
        assert instruction.name == "inst2"
        assert instruction.content == "Content 2"

    def test_get_instruction_by_name_not_found(self, tmp_path: Path) -> None:
        """Test getting non-existent instruction by name."""
        metadata = {
            "name": "Test",
            "instructions": [{"name": "inst1", "description": "Instruction 1", "file": "inst1.md"}],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "inst1.md").write_text("Content")

        parser = RepositoryParser(repo_path)
        instruction = parser.get_instruction_by_name("nonexistent")

        assert instruction is None

    def test_get_bundle_by_name(self, tmp_path: Path) -> None:
        """Test getting bundle by name."""
        metadata = {
            "name": "Test",
            "instructions": [{"name": "inst1", "description": "Instruction 1", "file": "inst1.md"}],
            "bundles": [
                {"name": "bundle1", "description": "Bundle 1", "instructions": ["inst1"]},
                {"name": "bundle2", "description": "Bundle 2", "instructions": ["inst1"]},
            ],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "inst1.md").write_text("Content")

        parser = RepositoryParser(repo_path)
        bundle = parser.get_bundle_by_name("bundle2")

        assert bundle is not None
        assert bundle.name == "bundle2"

    def test_get_bundle_by_name_not_found(self, tmp_path: Path) -> None:
        """Test getting non-existent bundle by name."""
        metadata = {
            "name": "Test",
            "instructions": [{"name": "inst1", "description": "Instruction 1", "file": "inst1.md"}],
            "bundles": [{"name": "bundle1", "description": "Bundle 1", "instructions": ["inst1"]}],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "inst1.md").write_text("Content")

        parser = RepositoryParser(repo_path)
        bundle = parser.get_bundle_by_name("nonexistent")

        assert bundle is None

    def test_get_instructions_for_bundle(self, tmp_path: Path) -> None:
        """Test getting instructions for a bundle."""
        metadata = {
            "name": "Test",
            "instructions": [
                {"name": "inst1", "description": "Instruction 1", "file": "inst1.md"},
                {"name": "inst2", "description": "Instruction 2", "file": "inst2.md"},
                {"name": "inst3", "description": "Instruction 3", "file": "inst3.md"},
            ],
            "bundles": [{"name": "bundle1", "description": "Bundle 1", "instructions": ["inst1", "inst3"]}],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "inst1.md").write_text("Content 1")
        (repo_path / "inst2.md").write_text("Content 2")
        (repo_path / "inst3.md").write_text("Content 3")

        parser = RepositoryParser(repo_path)
        instructions = parser.get_instructions_for_bundle("bundle1")

        assert len(instructions) == 2
        assert instructions[0].name == "inst1"
        assert instructions[1].name == "inst3"

    def test_get_instructions_for_bundle_not_found(self, tmp_path: Path) -> None:
        """Test getting instructions for non-existent bundle."""
        metadata = {
            "name": "Test",
            "instructions": [{"name": "inst1", "description": "Instruction 1", "file": "inst1.md"}],
            "bundles": [{"name": "bundle1", "description": "Bundle 1", "instructions": ["inst1"]}],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "inst1.md").write_text("Content")

        parser = RepositoryParser(repo_path)

        with pytest.raises(ValueError, match="Bundle not found"):
            parser.get_instructions_for_bundle("nonexistent")

    def test_get_instructions_for_bundle_missing_instruction(self, tmp_path: Path) -> None:
        """Test bundle referencing non-existent instruction."""
        metadata = {
            "name": "Test",
            "instructions": [{"name": "inst1", "description": "Instruction 1", "file": "inst1.md"}],
            "bundles": [{"name": "bundle1", "description": "Bundle 1", "instructions": ["inst1", "nonexistent"]}],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "inst1.md").write_text("Content")

        parser = RepositoryParser(repo_path)

        with pytest.raises(ValueError, match="references unknown instruction"):
            parser.get_instructions_for_bundle("bundle1")

    def test_parse_mcp_servers(self, tmp_path: Path) -> None:
        """Test parsing MCP servers."""
        metadata = {
            "name": "Test",
            "mcp_servers": [
                {
                    "name": "test-server",
                    "command": "node",
                    "args": ["server.js"],
                    "env": {"API_KEY": "test"},
                }
            ],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        parser = RepositoryParser(repo_path)
        servers = parser.parse_mcp_servers("test-namespace")

        assert len(servers) == 1
        assert servers[0].name == "test-server"
        assert servers[0].namespace == "test-namespace"

    def test_parse_mcp_servers_no_metadata(self, tmp_path: Path) -> None:
        """Test parsing MCP servers with no metadata file."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        parser = RepositoryParser(repo_path)
        servers = parser.parse_mcp_servers("test-namespace")

        assert servers == []

    def test_parse_mcp_servers_empty_metadata(self, tmp_path: Path) -> None:
        """Test parsing MCP servers with empty metadata."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text("")

        parser = RepositoryParser(repo_path)
        servers = parser.parse_mcp_servers("test-namespace")

        assert servers == []

    def test_parse_mcp_servers_invalid_server(self, tmp_path: Path) -> None:
        """Test parsing MCP servers with invalid server data."""
        metadata = {
            "name": "Test",
            "mcp_servers": [
                {"name": "valid-server", "command": "node"},
                {"invalid": "data"},  # Missing required fields
            ],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        parser = RepositoryParser(repo_path)
        servers = parser.parse_mcp_servers("test-namespace")

        # Should skip invalid server and only include valid one
        assert len(servers) == 1
        assert servers[0].name == "valid-server"

    def test_parse_mcp_sets(self, tmp_path: Path) -> None:
        """Test parsing MCP sets."""
        metadata = {
            "name": "Test",
            "mcp_sets": [{"name": "test-set", "description": "Test set", "servers": ["server1", "server2"]}],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        parser = RepositoryParser(repo_path)
        sets = parser.parse_mcp_sets("test-namespace")

        assert len(sets) == 1
        assert sets[0].name == "test-set"
        assert sets[0].namespace == "test-namespace"

    def test_parse_mcp_sets_no_metadata(self, tmp_path: Path) -> None:
        """Test parsing MCP sets with no metadata file."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        parser = RepositoryParser(repo_path)
        sets = parser.parse_mcp_sets("test-namespace")

        assert sets == []

    def test_parse_mcp_sets_empty_metadata(self, tmp_path: Path) -> None:
        """Test parsing MCP sets with empty metadata."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text("")

        parser = RepositoryParser(repo_path)
        sets = parser.parse_mcp_sets("test-namespace")

        assert sets == []

    def test_parse_mcp_sets_invalid_set(self, tmp_path: Path) -> None:
        """Test parsing MCP sets with invalid set data."""
        metadata = {
            "name": "Test",
            "mcp_sets": [
                {"name": "valid-set", "description": "Valid set", "servers": ["server1"]},
                {"invalid": "data"},  # Missing required fields
            ],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        parser = RepositoryParser(repo_path)
        sets = parser.parse_mcp_sets("test-namespace")

        # Should skip invalid set and only include valid one
        assert len(sets) == 1
        assert sets[0].name == "valid-set"


class TestValidateRepositoryStructure:
    """Test validate_repository_structure function."""

    def test_validate_valid_repository(self, tmp_path: Path) -> None:
        """Test validating a valid repository."""
        metadata = {
            "name": "Test",
            "instructions": [{"name": "test", "description": "Test instruction", "file": "test.md"}],
        }

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))
        (repo_path / "test.md").write_text("Content")

        result = validate_repository_structure(repo_path)

        assert result is None

    def test_validate_missing_metadata_file(self, tmp_path: Path) -> None:
        """Test validating repository with missing metadata."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        result = validate_repository_structure(repo_path)

        assert result == "Missing templatekit.yaml metadata file"

    def test_validate_no_instructions_or_bundles(self, tmp_path: Path) -> None:
        """Test validating repository with no content."""
        metadata = {"name": "Test", "instructions": [], "bundles": []}

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text(yaml.dump(metadata))

        result = validate_repository_structure(repo_path)

        assert result == "Repository has no instructions or bundles"

    def test_validate_invalid_metadata(self, tmp_path: Path) -> None:
        """Test validating repository with invalid metadata."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / "templatekit.yaml").write_text("invalid: yaml: content:")

        result = validate_repository_structure(repo_path)

        assert result is not None
        assert "Invalid repository metadata" in result
