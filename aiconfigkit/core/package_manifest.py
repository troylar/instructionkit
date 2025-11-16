"""Package manifest parsing and validation."""

from pathlib import Path

import yaml

from aiconfigkit.core.models import (
    CommandComponent,
    CredentialDescriptor,
    HookComponent,
    InstructionComponent,
    MCPServerComponent,
    Package,
    PackageComponents,
    ResourceComponent,
)


class ValidationError(Exception):
    """Raised when manifest validation fails."""

    pass


class PackageManifestParser:
    """
    Parser and validator for package manifest files.

    Parses ai-config-kit-package.yaml files and validates their structure
    and component references.
    """

    def __init__(self, package_root: Path):
        """
        Initialize parser.

        Args:
            package_root: Root directory of the package
        """
        self.package_root = package_root
        self.manifest_path = package_root / "ai-config-kit-package.yaml"

    def parse(self) -> Package:
        """
        Parse package manifest YAML file.

        Returns:
            Package object with all components

        Raises:
            FileNotFoundError: If manifest file doesn't exist
            yaml.YAMLError: If YAML is invalid
            ValidationError: If manifest structure is invalid
        """
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")

        with open(self.manifest_path, "r") as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValidationError("Manifest is empty")

        # Extract required fields
        try:
            name = data["name"]
            version = data["version"]
            description = data["description"]
            author = data["author"]
            license_type = data["license"]
            namespace = data.get("namespace", "local/local")
        except KeyError as e:
            raise ValidationError(f"Missing required field: {e}")

        # Parse components
        components_data = data.get("components", {})
        # Handle case where components: is specified but empty (parses to None)
        if components_data is None:
            components_data = {}
        components = self._parse_components(components_data)

        # Create package
        package = Package(
            name=name,
            version=version,
            description=description,
            author=author,
            license=license_type,
            namespace=namespace,
            components=components,
        )

        return package

    def _parse_components(self, components_data: dict) -> PackageComponents:
        """
        Parse components section of manifest.

        Args:
            components_data: Components dictionary from manifest

        Returns:
            PackageComponents object
        """
        # Parse instructions
        instructions = []
        for inst_data in components_data.get("instructions", []):
            instructions.append(
                InstructionComponent(
                    name=inst_data["name"],
                    file=inst_data["file"],
                    description=inst_data["description"],
                    tags=inst_data.get("tags", []),
                    ide_support=inst_data.get("ide_support"),
                )
            )

        # Parse MCP servers
        mcp_servers = []
        for mcp_data in components_data.get("mcp_servers", []):
            credentials = []
            for cred_data in mcp_data.get("credentials", []):
                credentials.append(
                    CredentialDescriptor(
                        name=cred_data["name"],
                        description=cred_data["description"],
                        required=cred_data.get("required", True),
                        default=cred_data.get("default"),
                        example=cred_data.get("example"),
                    )
                )

            mcp_servers.append(
                MCPServerComponent(
                    name=mcp_data["name"],
                    file=mcp_data["file"],
                    description=mcp_data["description"],
                    credentials=credentials,
                    ide_support=mcp_data.get("ide_support", ["claude_code", "windsurf"]),
                )
            )

        # Parse hooks
        hooks = []
        for hook_data in components_data.get("hooks", []):
            hooks.append(
                HookComponent(
                    name=hook_data["name"],
                    file=hook_data["file"],
                    description=hook_data["description"],
                    hook_type=hook_data["hook_type"],
                    ide_support=hook_data.get("ide_support", ["claude_code"]),
                )
            )

        # Parse commands
        commands = []
        for cmd_data in components_data.get("commands", []):
            commands.append(
                CommandComponent(
                    name=cmd_data["name"],
                    file=cmd_data["file"],
                    description=cmd_data["description"],
                    command_type=cmd_data["command_type"],
                    ide_support=cmd_data.get("ide_support", []),
                )
            )

        # Parse resources
        resources = []
        for res_data in components_data.get("resources", []):
            resources.append(
                ResourceComponent(
                    name=res_data["name"],
                    file=res_data["file"],
                    description=res_data["description"],
                    install_path=res_data.get("install_path", res_data["file"]),  # Default to file path
                    checksum=res_data["checksum"],
                    size=res_data["size"],
                )
            )

        return PackageComponents(
            instructions=instructions,
            mcp_servers=mcp_servers,
            hooks=hooks,
            commands=commands,
            resources=resources,
        )

    def validate(self, package: Package) -> list[str]:
        """
        Validate package manifest completeness and file references.

        Args:
            package: Package object to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        import re

        errors = []

        # Validate version format (semantic versioning: X.Y.Z)
        version_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$"
        if not re.match(version_pattern, package.version):
            errors.append(f"Invalid version format: {package.version}. Must follow semantic versioning (X.Y.Z)")

        # Validate all component files exist
        for instruction in package.components.instructions:
            file_path = self.package_root / instruction.file
            if not file_path.exists():
                errors.append(f"Instruction file not found: {instruction.file}")

        for mcp in package.components.mcp_servers:
            file_path = self.package_root / mcp.file
            if not file_path.exists():
                errors.append(f"MCP config file not found: {mcp.file}")

        for hook in package.components.hooks:
            file_path = self.package_root / hook.file
            if not file_path.exists():
                errors.append(f"Hook file not found: {hook.file}")

        for command in package.components.commands:
            file_path = self.package_root / command.file
            if not file_path.exists():
                errors.append(f"Command file not found: {command.file}")

        for resource in package.components.resources:
            file_path = self.package_root / resource.file
            if not file_path.exists():
                errors.append(f"Resource file not found: {resource.file}")

        # Validate component name uniqueness within each type
        inst_names = [i.name for i in package.components.instructions]
        if len(inst_names) != len(set(inst_names)):
            errors.append("Duplicate instruction names found")

        mcp_names = [m.name for m in package.components.mcp_servers]
        if len(mcp_names) != len(set(mcp_names)):
            errors.append("Duplicate MCP server names found")

        # Note: We allow empty packages (for edge case testing)
        # In practice, most packages should have at least one component

        return errors
