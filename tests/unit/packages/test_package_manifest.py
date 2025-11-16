"""Unit tests for package manifest parser."""

from pathlib import Path

import pytest
import yaml

from aiconfigkit.core.package_manifest import PackageManifestParser, ValidationError


@pytest.fixture
def temp_package_dir(tmp_path: Path) -> Path:
    """Create a temporary package directory."""
    package_dir = tmp_path / "test-package"
    package_dir.mkdir()
    return package_dir


@pytest.fixture
def valid_manifest_data() -> dict:
    """Return valid manifest data."""
    return {
        "name": "test-package",
        "version": "1.0.0",
        "description": "Test package",
        "author": "Test Author",
        "license": "MIT",
        "namespace": "test/repo",
        "components": {
            "instructions": [
                {
                    "name": "test-instruction",
                    "file": "instructions/test.md",
                    "description": "Test instruction",
                    "tags": ["test"],
                }
            ],
            "mcp_servers": [
                {
                    "name": "test-server",
                    "file": "mcp/server.json",
                    "description": "Test server",
                    "credentials": [
                        {
                            "name": "API_KEY",
                            "description": "API key",
                            "required": True,
                        }
                    ],
                }
            ],
        },
    }


class TestPackageManifestParser:
    """Test PackageManifestParser class."""

    def test_init(self, temp_package_dir: Path) -> None:
        """Test parser initialization."""
        parser = PackageManifestParser(temp_package_dir)
        assert parser.package_root == temp_package_dir
        assert parser.manifest_path == temp_package_dir / "ai-config-kit-package.yaml"

    def test_parse_missing_manifest_raises_error(self, temp_package_dir: Path) -> None:
        """Test that missing manifest raises FileNotFoundError."""
        parser = PackageManifestParser(temp_package_dir)
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            parser.parse()

    def test_parse_empty_manifest_raises_error(self, temp_package_dir: Path) -> None:
        """Test that empty manifest raises ValidationError."""
        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        manifest_path.write_text("")

        parser = PackageManifestParser(temp_package_dir)
        with pytest.raises(ValidationError, match="Manifest is empty"):
            parser.parse()

    def test_parse_missing_required_field_raises_error(self, temp_package_dir: Path) -> None:
        """Test that missing required field raises ValidationError."""
        manifest_data = {
            "name": "test",
            "version": "1.0.0",
            # Missing description, author, license
        }
        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        with pytest.raises(ValidationError, match="Missing required field"):
            parser.parse()

    def test_parse_valid_manifest(self, temp_package_dir: Path, valid_manifest_data: dict) -> None:
        """Test parsing a valid manifest."""
        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(valid_manifest_data, f)

        # Create referenced files
        (temp_package_dir / "instructions").mkdir()
        (temp_package_dir / "instructions" / "test.md").write_text("# Test")
        (temp_package_dir / "mcp").mkdir()
        (temp_package_dir / "mcp" / "server.json").write_text("{}")

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()

        assert package.name == "test-package"
        assert package.version == "1.0.0"
        assert package.description == "Test package"
        assert package.author == "Test Author"
        assert package.license == "MIT"
        assert package.namespace == "test/repo"
        assert package.components.total_count == 2

    def test_parse_instructions(self, temp_package_dir: Path, valid_manifest_data: dict) -> None:
        """Test parsing instruction components."""
        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(valid_manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()

        assert len(package.components.instructions) == 1
        inst = package.components.instructions[0]
        assert inst.name == "test-instruction"
        assert inst.file == "instructions/test.md"
        assert inst.description == "Test instruction"
        assert inst.tags == ["test"]

    def test_parse_mcp_servers_with_credentials(self, temp_package_dir: Path, valid_manifest_data: dict) -> None:
        """Test parsing MCP server components with credentials."""
        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(valid_manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()

        assert len(package.components.mcp_servers) == 1
        mcp = package.components.mcp_servers[0]
        assert mcp.name == "test-server"
        assert mcp.file == "mcp/server.json"
        assert len(mcp.credentials) == 1
        assert mcp.credentials[0].name == "API_KEY"
        assert mcp.credentials[0].required is True

    def test_parse_all_component_types(self, temp_package_dir: Path) -> None:
        """Test parsing all component types."""
        manifest_data = {
            "name": "full-package",
            "version": "1.0.0",
            "description": "Package with all components",
            "author": "Author",
            "license": "MIT",
            "components": {
                "instructions": [
                    {
                        "name": "inst",
                        "file": "instructions/inst.md",
                        "description": "Instruction",
                    }
                ],
                "mcp_servers": [
                    {
                        "name": "mcp",
                        "file": "mcp/mcp.json",
                        "description": "MCP",
                    }
                ],
                "hooks": [
                    {
                        "name": "hook",
                        "file": "hooks/hook.sh",
                        "description": "Hook",
                        "hook_type": "pre-commit",
                    }
                ],
                "commands": [
                    {
                        "name": "cmd",
                        "file": "commands/cmd.sh",
                        "description": "Command",
                        "command_type": "shell",
                    }
                ],
                "resources": [
                    {
                        "name": "res",
                        "file": "resources/res.png",
                        "description": "Resource",
                        "checksum": "sha256:abc123",
                        "size": 1024,
                    }
                ],
            },
        }

        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()

        assert len(package.components.instructions) == 1
        assert len(package.components.mcp_servers) == 1
        assert len(package.components.hooks) == 1
        assert len(package.components.commands) == 1
        assert len(package.components.resources) == 1
        assert package.components.total_count == 5

    def test_validate_all_files_exist(self, temp_package_dir: Path, valid_manifest_data: dict) -> None:
        """Test validation passes when all files exist."""
        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(valid_manifest_data, f)

        # Create all referenced files
        (temp_package_dir / "instructions").mkdir()
        (temp_package_dir / "instructions" / "test.md").write_text("# Test")
        (temp_package_dir / "mcp").mkdir()
        (temp_package_dir / "mcp" / "server.json").write_text("{}")

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()
        errors = parser.validate(package)

        assert len(errors) == 0

    def test_validate_missing_instruction_file(self, temp_package_dir: Path, valid_manifest_data: dict) -> None:
        """Test validation detects missing instruction file."""
        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(valid_manifest_data, f)

        # Create MCP file but not instruction file
        (temp_package_dir / "mcp").mkdir()
        (temp_package_dir / "mcp" / "server.json").write_text("{}")

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()
        errors = parser.validate(package)

        assert len(errors) == 1
        assert "Instruction file not found" in errors[0]

    def test_validate_missing_mcp_file(self, temp_package_dir: Path, valid_manifest_data: dict) -> None:
        """Test validation detects missing MCP file."""
        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(valid_manifest_data, f)

        # Create instruction file but not MCP file
        (temp_package_dir / "instructions").mkdir()
        (temp_package_dir / "instructions" / "test.md").write_text("# Test")

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()
        errors = parser.validate(package)

        assert len(errors) == 1
        assert "MCP config file not found" in errors[0]

    def test_validate_duplicate_instruction_names(self, temp_package_dir: Path) -> None:
        """Test validation detects duplicate instruction names."""
        manifest_data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Author",
            "license": "MIT",
            "components": {
                "instructions": [
                    {"name": "same", "file": "inst1.md", "description": "Inst 1"},
                    {"name": "same", "file": "inst2.md", "description": "Inst 2"},
                ],
            },
        }

        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        # Create files
        (temp_package_dir / "inst1.md").write_text("# 1")
        (temp_package_dir / "inst2.md").write_text("# 2")

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()
        errors = parser.validate(package)

        assert any("Duplicate instruction names" in e for e in errors)

    def test_validate_duplicate_mcp_names(self, temp_package_dir: Path) -> None:
        """Test validation detects duplicate MCP server names."""
        manifest_data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Author",
            "license": "MIT",
            "components": {
                "mcp_servers": [
                    {"name": "same", "file": "mcp1.json", "description": "MCP 1"},
                    {"name": "same", "file": "mcp2.json", "description": "MCP 2"},
                ],
            },
        }

        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        # Create files
        (temp_package_dir / "mcp1.json").write_text("{}")
        (temp_package_dir / "mcp2.json").write_text("{}")

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()
        errors = parser.validate(package)

        assert any("Duplicate MCP server names" in e for e in errors)

    def test_parse_default_namespace(self, temp_package_dir: Path) -> None:
        """Test default namespace when not provided."""
        manifest_data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Author",
            "license": "MIT",
            "components": {
                "instructions": [{"name": "inst", "file": "inst.md", "description": "Inst"}],
            },
        }

        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()

        assert package.namespace == "local/local"

    def test_parse_empty_components(self, temp_package_dir: Path) -> None:
        """Test parsing manifest with empty/None components."""
        manifest_data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Author",
            "license": "MIT",
            "components": None,  # Will be parsed as None by YAML
        }

        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()

        assert package.components.total_count == 0
        assert len(package.components.instructions) == 0
        assert len(package.components.mcp_servers) == 0

    def test_validate_invalid_version_format(self, temp_package_dir: Path) -> None:
        """Test validation detects invalid version format."""
        manifest_data = {
            "name": "test",
            "version": "invalid-version",  # Not semantic versioning
            "description": "Test",
            "author": "Author",
            "license": "MIT",
            "components": {},
        }

        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()
        errors = parser.validate(package)

        assert len(errors) == 1
        assert "Invalid version format" in errors[0]
        assert "semantic versioning" in errors[0]

    def test_validate_missing_hook_file(self, temp_package_dir: Path) -> None:
        """Test validation detects missing hook file."""
        manifest_data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Author",
            "license": "MIT",
            "components": {
                "hooks": [
                    {
                        "name": "test-hook",
                        "file": "hooks/missing.sh",
                        "description": "Test hook",
                        "hook_type": "pre-commit",
                    }
                ],
            },
        }

        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()
        errors = parser.validate(package)

        assert len(errors) == 1
        assert "Hook file not found" in errors[0]
        assert "hooks/missing.sh" in errors[0]

    def test_validate_missing_command_file(self, temp_package_dir: Path) -> None:
        """Test validation detects missing command file."""
        manifest_data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Author",
            "license": "MIT",
            "components": {
                "commands": [
                    {
                        "name": "test-command",
                        "file": "commands/missing.sh",
                        "description": "Test command",
                        "command_type": "shell",
                    }
                ],
            },
        }

        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()
        errors = parser.validate(package)

        assert len(errors) == 1
        assert "Command file not found" in errors[0]
        assert "commands/missing.sh" in errors[0]

    def test_validate_missing_resource_file(self, temp_package_dir: Path) -> None:
        """Test validation detects missing resource file."""
        manifest_data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Author",
            "license": "MIT",
            "components": {
                "resources": [
                    {
                        "name": "test-resource",
                        "file": "resources/missing.png",
                        "description": "Test resource",
                        "checksum": "sha256:abc123",
                        "size": 1024,
                    }
                ],
            },
        }

        manifest_path = temp_package_dir / "ai-config-kit-package.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f)

        parser = PackageManifestParser(temp_package_dir)
        package = parser.parse()
        errors = parser.validate(package)

        assert len(errors) == 1
        assert "Resource file not found" in errors[0]
        assert "resources/missing.png" in errors[0]
