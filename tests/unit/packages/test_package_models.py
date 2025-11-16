"""Unit tests for package-related data models."""

from datetime import datetime

import pytest

from aiconfigkit.core.models import (
    ComponentStatus,
    # Enums
    ComponentType,
    # Components
    CredentialDescriptor,
    InstallationScope,
    InstallationStatus,
    InstalledComponent,
    InstructionComponent,
    MCPServerComponent,
    Package,
    PackageComponents,
    PackageInstallationRecord,
    SecretConfidence,
)


class TestComponentType:
    """Test ComponentType enumeration."""

    def test_enum_values(self) -> None:
        """Test all enum values are defined."""
        assert ComponentType.INSTRUCTION.value == "instruction"
        assert ComponentType.MCP_SERVER.value == "mcp_server"
        assert ComponentType.HOOK.value == "hook"
        assert ComponentType.COMMAND.value == "command"
        assert ComponentType.RESOURCE.value == "resource"


class TestInstallationStatus:
    """Test InstallationStatus enumeration."""

    def test_enum_values(self) -> None:
        """Test all enum values are defined."""
        assert InstallationStatus.INSTALLING.value == "installing"
        assert InstallationStatus.COMPLETE.value == "complete"
        assert InstallationStatus.PARTIAL.value == "partial"
        assert InstallationStatus.UPDATING.value == "updating"
        assert InstallationStatus.FAILED.value == "failed"


class TestComponentStatus:
    """Test ComponentStatus enumeration."""

    def test_enum_values(self) -> None:
        """Test all enum values are defined."""
        assert ComponentStatus.INSTALLED.value == "installed"
        assert ComponentStatus.FAILED.value == "failed"
        assert ComponentStatus.SKIPPED.value == "skipped"
        assert ComponentStatus.PENDING_CREDENTIALS.value == "pending_credentials"


class TestSecretConfidence:
    """Test SecretConfidence enumeration."""

    def test_enum_values(self) -> None:
        """Test all enum values are defined."""
        assert SecretConfidence.HIGH.value == "high"
        assert SecretConfidence.MEDIUM.value == "medium"
        assert SecretConfidence.SAFE.value == "safe"


class TestCredentialDescriptor:
    """Test CredentialDescriptor dataclass."""

    def test_valid_credential(self) -> None:
        """Test creating a valid credential descriptor."""
        cred = CredentialDescriptor(
            name="API_KEY", description="API key for service", required=True, example="sk-abc123"
        )
        assert cred.name == "API_KEY"
        assert cred.description == "API key for service"
        assert cred.required is True
        assert cred.example == "sk-abc123"

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Credential name cannot be empty"):
            CredentialDescriptor(name="", description="test")

    def test_lowercase_name_raises_error(self) -> None:
        """Test that lowercase name raises ValueError."""
        with pytest.raises(ValueError, match="must be UPPER_SNAKE_CASE"):
            CredentialDescriptor(name="api_key", description="test")

    def test_required_with_default_raises_error(self) -> None:
        """Test that required credential cannot have default value."""
        with pytest.raises(ValueError, match="Required credentials cannot have default values"):
            CredentialDescriptor(name="API_KEY", description="test", required=True, default="value")

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        cred = CredentialDescriptor(name="API_KEY", description="test", required=False, default="default_val")
        data = cred.to_dict()
        assert data["name"] == "API_KEY"
        assert data["description"] == "test"
        assert data["required"] is False
        assert data["default"] == "default_val"

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"name": "API_KEY", "description": "test", "required": True}
        cred = CredentialDescriptor.from_dict(data)
        assert cred.name == "API_KEY"
        assert cred.description == "test"
        assert cred.required is True


class TestInstructionComponent:
    """Test InstructionComponent dataclass."""

    def test_valid_instruction_component(self) -> None:
        """Test creating a valid instruction component."""
        comp = InstructionComponent(
            name="test-instruction",
            file="instructions/test.md",
            description="Test instruction",
            tags=["test", "demo"],
            ide_support=["cursor", "claude_code"],
        )
        assert comp.name == "test-instruction"
        assert comp.file == "instructions/test.md"
        assert comp.tags == ["test", "demo"]
        assert comp.ide_support == ["cursor", "claude_code"]

    def test_to_dict(self) -> None:
        """Test serialization."""
        comp = InstructionComponent(name="test", file="test.md", description="desc")
        data = comp.to_dict()
        assert data["name"] == "test"
        assert data["file"] == "test.md"
        assert data["description"] == "desc"

    def test_from_dict(self) -> None:
        """Test deserialization."""
        data = {"name": "test", "file": "test.md", "description": "desc", "tags": ["tag1"]}
        comp = InstructionComponent.from_dict(data)
        assert comp.name == "test"
        assert comp.tags == ["tag1"]


class TestMCPServerComponent:
    """Test MCPServerComponent dataclass."""

    def test_valid_mcp_component(self) -> None:
        """Test creating a valid MCP server component."""
        cred = CredentialDescriptor(name="API_KEY", description="test")
        comp = MCPServerComponent(
            name="test-server",
            file="mcp/server.json",
            description="Test server",
            credentials=[cred],
            ide_support=["claude_code"],
        )
        assert comp.name == "test-server"
        assert len(comp.credentials) == 1
        assert comp.ide_support == ["claude_code"]

    def test_default_ide_support(self) -> None:
        """Test default IDE support for MCP."""
        comp = MCPServerComponent(name="test", file="test.json", description="desc")
        assert "claude_code" in comp.ide_support
        assert "windsurf" in comp.ide_support

    def test_to_dict_with_credentials(self) -> None:
        """Test serialization with credentials."""
        cred = CredentialDescriptor(name="API_KEY", description="test")
        comp = MCPServerComponent(name="test", file="test.json", description="desc", credentials=[cred])
        data = comp.to_dict()
        assert len(data["credentials"]) == 1
        assert data["credentials"][0]["name"] == "API_KEY"


class TestPackageComponents:
    """Test PackageComponents container."""

    def test_empty_components_allowed(self) -> None:
        """Test that empty components are allowed (for edge case testing)."""
        # Empty packages are now allowed
        components = PackageComponents()
        assert components.total_count == 0
        assert len(components.instructions) == 0
        assert len(components.mcp_servers) == 0
        assert len(components.hooks) == 0
        assert len(components.commands) == 0
        assert len(components.resources) == 0

    def test_total_count(self) -> None:
        """Test total component count calculation."""
        inst1 = InstructionComponent(name="i1", file="f1", description="d1")
        inst2 = InstructionComponent(name="i2", file="f2", description="d2")
        mcp = MCPServerComponent(name="m1", file="mf1", description="md1")

        components = PackageComponents(instructions=[inst1, inst2], mcp_servers=[mcp])
        assert components.total_count == 3

    def test_component_types(self) -> None:
        """Test component types property."""
        inst = InstructionComponent(name="i1", file="f1", description="d1")
        mcp = MCPServerComponent(name="m1", file="mf1", description="md1")

        components = PackageComponents(instructions=[inst], mcp_servers=[mcp])
        types = components.component_types
        assert "instructions" in types
        assert "mcp_servers" in types
        assert len(types) == 2

    def test_to_dict_and_from_dict(self) -> None:
        """Test round-trip serialization."""
        inst = InstructionComponent(name="i1", file="f1", description="d1")
        components = PackageComponents(instructions=[inst])

        data = components.to_dict()
        restored = PackageComponents.from_dict(data)

        assert restored.total_count == 1
        assert restored.instructions[0].name == "i1"


class TestPackage:
    """Test Package dataclass."""

    def test_valid_package(self) -> None:
        """Test creating a valid package."""
        inst = InstructionComponent(name="i1", file="f1", description="d1")
        components = PackageComponents(instructions=[inst])

        pkg = Package(
            name="test-package",
            version="1.0.0",
            description="Test package",
            author="Test Author",
            license="MIT",
            namespace="test/repo",
            components=components,
        )
        assert pkg.name == "test-package"
        assert pkg.version == "1.0.0"

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises ValueError."""
        inst = InstructionComponent(name="i1", file="f1", description="d1")
        components = PackageComponents(instructions=[inst])

        with pytest.raises(ValueError, match="Package name cannot be empty"):
            Package(
                name="",
                version="1.0.0",
                description="desc",
                author="author",
                license="MIT",
                namespace="ns",
                components=components,
            )

    def test_invalid_name_raises_error(self) -> None:
        """Test that invalid name raises ValueError."""
        inst = InstructionComponent(name="i1", file="f1", description="d1")
        components = PackageComponents(instructions=[inst])

        with pytest.raises(ValueError, match="must be lowercase alphanumeric"):
            Package(
                name="Test Package!",
                version="1.0.0",
                description="desc",
                author="author",
                license="MIT",
                namespace="ns",
                components=components,
            )

    def test_to_dict_with_timestamps(self) -> None:
        """Test serialization with timestamps."""
        inst = InstructionComponent(name="i1", file="f1", description="d1")
        components = PackageComponents(instructions=[inst])
        now = datetime.now()

        pkg = Package(
            name="test-package",
            version="1.0.0",
            description="desc",
            author="author",
            license="MIT",
            namespace="ns",
            components=components,
            created_at=now,
            updated_at=now,
        )

        data = pkg.to_dict()
        assert "created_at" in data
        assert "updated_at" in data

    def test_from_dict(self) -> None:
        """Test deserialization."""
        inst_data = {"name": "i1", "file": "f1", "description": "d1"}
        data = {
            "name": "test",
            "version": "1.0.0",
            "description": "desc",
            "author": "author",
            "license": "MIT",
            "namespace": "ns",
            "components": {
                "instructions": [inst_data],
                "mcp_servers": [],
                "hooks": [],
                "commands": [],
                "resources": [],
            },
        }

        pkg = Package.from_dict(data)
        assert pkg.name == "test"
        assert pkg.components.total_count == 1


class TestInstalledComponent:
    """Test InstalledComponent dataclass."""

    def test_valid_installed_component(self) -> None:
        """Test creating a valid installed component."""
        comp = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path=".claude/rules/test.md",
            checksum="sha256:abc123",
            status=ComponentStatus.INSTALLED,
        )
        assert comp.type == ComponentType.INSTRUCTION
        assert comp.status == ComponentStatus.INSTALLED

    def test_to_dict(self) -> None:
        """Test serialization."""
        comp = InstalledComponent(
            type=ComponentType.MCP_SERVER,
            name="test",
            installed_path="path",
            checksum="checksum",
            status=ComponentStatus.PENDING_CREDENTIALS,
        )
        data = comp.to_dict()
        assert data["type"] == "mcp_server"
        assert data["status"] == "pending_credentials"

    def test_from_dict(self) -> None:
        """Test deserialization."""
        data = {
            "type": "instruction",
            "name": "test",
            "installed_path": "path",
            "checksum": "checksum",
            "status": "installed",
        }
        comp = InstalledComponent.from_dict(data)
        assert comp.type == ComponentType.INSTRUCTION
        assert comp.status == ComponentStatus.INSTALLED


class TestPackageInstallationRecord:
    """Test PackageInstallationRecord dataclass."""

    def test_valid_installation_record(self) -> None:
        """Test creating a valid installation record."""
        now = datetime.now()
        comp = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path="path",
            checksum="checksum",
            status=ComponentStatus.INSTALLED,
        )

        record = PackageInstallationRecord(
            package_name="test-package",
            namespace="test/repo",
            version="1.0.0",
            installed_at=now,
            updated_at=now,
            scope=InstallationScope.PROJECT,
            components=[comp],
            status=InstallationStatus.COMPLETE,
        )
        assert record.package_name == "test-package"
        assert record.status == InstallationStatus.COMPLETE
        assert len(record.components) == 1

    def test_to_dict(self) -> None:
        """Test serialization."""
        now = datetime.now()
        comp = InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name="test",
            installed_path="path",
            checksum="checksum",
            status=ComponentStatus.INSTALLED,
        )

        record = PackageInstallationRecord(
            package_name="test",
            namespace="ns",
            version="1.0.0",
            installed_at=now,
            updated_at=now,
            scope=InstallationScope.PROJECT,
            components=[comp],
            status=InstallationStatus.COMPLETE,
        )

        data = record.to_dict()
        assert data["package_name"] == "test"
        assert data["scope"] == "project"
        assert len(data["components"]) == 1

    def test_from_dict(self) -> None:
        """Test deserialization."""
        now = datetime.now()
        data = {
            "package_name": "test",
            "namespace": "ns",
            "version": "1.0.0",
            "installed_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "scope": "project",
            "components": [
                {
                    "type": "instruction",
                    "name": "test",
                    "installed_path": "path",
                    "checksum": "checksum",
                    "status": "installed",
                }
            ],
            "status": "complete",
        }

        record = PackageInstallationRecord.from_dict(data)
        assert record.package_name == "test"
        assert record.status == InstallationStatus.COMPLETE
        assert len(record.components) == 1
