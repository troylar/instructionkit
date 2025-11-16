"""Package installation command and logic."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from aiconfigkit.ai_tools.capability_registry import get_capability
from aiconfigkit.ai_tools.translator import get_translator
from aiconfigkit.core.models import (
    AIToolType,
    ComponentStatus,
    ComponentType,
    ConflictResolution,
    InstallationScope,
    InstallationStatus,
    InstalledComponent,
    Package,
    PackageInstallationRecord,
)
from aiconfigkit.core.package_manifest import PackageManifestParser
from aiconfigkit.storage.package_tracker import PackageTracker

logger = logging.getLogger(__name__)


@dataclass
class InstallationResult:
    """Result of package installation operation."""

    success: bool
    status: InstallationStatus
    package_name: str
    version: str
    installed_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    components_installed: dict[ComponentType, int] = field(default_factory=dict)
    error_message: Optional[str] = None
    is_reinstall: bool = False

    @property
    def total_components(self) -> int:
        """Total number of components processed."""
        return self.installed_count + self.skipped_count + self.failed_count


def install_package(
    package_path: Path,
    project_root: Path,
    target_ide: AIToolType,
    scope: InstallationScope = InstallationScope.PROJECT,
    conflict_resolution: ConflictResolution = ConflictResolution.SKIP,
    force: bool = False,
) -> InstallationResult:
    """
    Install a package to a project for a specific IDE.

    Args:
        package_path: Path to package directory containing manifest
        project_root: Root directory of target project
        target_ide: Target IDE for installation
        scope: Installation scope (project or global)
        conflict_resolution: How to handle file conflicts
        force: Force reinstallation even if already installed

    Returns:
        InstallationResult with details of installation

    Raises:
        FileNotFoundError: If manifest not found
        ValidationError: If manifest is invalid
    """
    logger.info(f"Installing package from {package_path} to {project_root} for {target_ide.value}")

    try:
        # Step 1: Parse and validate manifest
        parser = PackageManifestParser(package_path)
        package = parser.parse()

        # Validate manifest
        validation_errors = parser.validate(package)
        if validation_errors:
            error_msg = "; ".join(validation_errors)
            return InstallationResult(
                success=False,
                status=InstallationStatus.FAILED,
                package_name=package.name,
                version=package.version,
                error_message=f"Manifest validation failed: {error_msg}",
            )

        logger.info(f"Parsed package: {package.name} v{package.version}")

        # Step 2: Check if already installed
        tracker_file = project_root / ".ai-config-kit" / "packages.json"
        tracker = PackageTracker(tracker_file)
        is_reinstall = tracker.is_package_installed(package.name, scope)

        if is_reinstall and not force:
            logger.info(f"Package {package.name} already installed")

        # Step 3: Get IDE capabilities
        capability = get_capability(target_ide)
        logger.debug(f"Target IDE capabilities: {capability.supported_components}")

        # Step 4: Get component translator
        translator = get_translator(target_ide)

        # Step 5: Filter components by IDE capabilities and track skipped
        installable_components = _filter_components_by_capability(package, capability)

        # Calculate skipped components (filtered out by IDE capabilities)
        total_in_package = package.components.total_count
        installable_count = sum(len(comps) for comps in installable_components.values())
        capability_skipped = total_in_package - installable_count

        logger.info(
            f"Found {installable_count} installable components, {capability_skipped} filtered by IDE capabilities"
        )

        # Step 6: Install each component type
        installed_components: list[InstalledComponent] = []
        installed_count = 0
        skipped_count = capability_skipped  # Start with capability-filtered components
        failed_count = 0
        components_by_type: dict[ComponentType, int] = {}

        # Install instructions
        for instruction in installable_components.get("instructions", []):
            result = _install_instruction_component(
                instruction,
                package_path,
                project_root,
                translator,
                conflict_resolution,
            )
            if result:
                installed_components.append(result)
                installed_count += 1
                components_by_type[ComponentType.INSTRUCTION] = components_by_type.get(ComponentType.INSTRUCTION, 0) + 1
            else:
                skipped_count += 1

        # Install MCP servers
        for mcp in installable_components.get("mcp_servers", []):
            result = _install_mcp_component(mcp, package_path, project_root, translator, conflict_resolution)
            if result:
                installed_components.append(result)
                installed_count += 1
                components_by_type[ComponentType.MCP_SERVER] = components_by_type.get(ComponentType.MCP_SERVER, 0) + 1
            else:
                skipped_count += 1

        # Install hooks
        for hook in installable_components.get("hooks", []):
            result = _install_hook_component(hook, package_path, project_root, translator, conflict_resolution)
            if result:
                installed_components.append(result)
                installed_count += 1
                components_by_type[ComponentType.HOOK] = components_by_type.get(ComponentType.HOOK, 0) + 1
            else:
                skipped_count += 1

        # Install commands
        for command in installable_components.get("commands", []):
            result = _install_command_component(command, package_path, project_root, translator, conflict_resolution)
            if result:
                installed_components.append(result)
                installed_count += 1
                components_by_type[ComponentType.COMMAND] = components_by_type.get(ComponentType.COMMAND, 0) + 1
            else:
                skipped_count += 1

        # Install resources
        for resource in installable_components.get("resources", []):
            result = _install_resource_component(resource, package_path, project_root, translator, conflict_resolution)
            if result:
                installed_components.append(result)
                installed_count += 1
                components_by_type[ComponentType.RESOURCE] = components_by_type.get(ComponentType.RESOURCE, 0) + 1
            else:
                skipped_count += 1

        # Step 7: Determine installation status
        total_in_package = package.components.total_count
        if installed_count == 0:
            status = InstallationStatus.FAILED
        elif installed_count == total_in_package:
            status = InstallationStatus.COMPLETE
        else:
            status = InstallationStatus.PARTIAL

        # Step 8: Record installation
        now = datetime.now()
        # Get original install time for reinstalls
        existing_record = tracker.get_package(package.name, scope) if is_reinstall else None
        original_install_time = existing_record.installed_at if existing_record else now

        installation_record = PackageInstallationRecord(
            package_name=package.name,
            namespace=package.namespace,
            version=package.version,
            installed_at=original_install_time,
            updated_at=now,
            scope=scope,
            components=installed_components,
            status=status,
        )
        tracker.record_installation(installation_record)

        logger.info(
            f"Installation complete: {installed_count} installed, {skipped_count} skipped, {failed_count} failed"
        )

        return InstallationResult(
            success=True,
            status=status,
            package_name=package.name,
            version=package.version,
            installed_count=installed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            components_installed=components_by_type,
            is_reinstall=is_reinstall,
        )

    except Exception as e:
        logger.error(f"Installation failed: {e}", exc_info=True)
        return InstallationResult(
            success=False,
            status=InstallationStatus.FAILED,
            package_name=package_path.name if package_path else "unknown",
            version="unknown",
            error_message=str(e),
        )


def _filter_components_by_capability(package: Package, capability: Any) -> dict[str, list[Any]]:
    """Filter package components by IDE capability."""
    filtered: dict[str, list[Any]] = {}

    if capability.supports_component(ComponentType.INSTRUCTION):
        filtered["instructions"] = package.components.instructions

    if capability.supports_component(ComponentType.MCP_SERVER):
        filtered["mcp_servers"] = package.components.mcp_servers

    if capability.supports_component(ComponentType.HOOK):
        filtered["hooks"] = package.components.hooks

    if capability.supports_component(ComponentType.COMMAND):
        filtered["commands"] = package.components.commands

    if capability.supports_component(ComponentType.RESOURCE):
        filtered["resources"] = package.components.resources

    return filtered


def _install_instruction_component(
    component: Any, package_path: Path, project_root: Path, translator: Any, conflict_resolution: ConflictResolution
) -> Optional[InstalledComponent]:
    """Install instruction component."""
    try:
        # Translate component
        translated = translator.translate_instruction(component, package_path)

        # Determine target path
        target_file = project_root / translated.target_path

        # Check for conflicts
        if target_file.exists():
            if conflict_resolution == ConflictResolution.SKIP:
                logger.info(f"Skipping existing file: {target_file}")
                return None
            elif conflict_resolution == ConflictResolution.RENAME:
                # Find available numbered suffix
                counter = 1
                stem = target_file.stem
                suffix = target_file.suffix
                while target_file.exists():
                    target_file = target_file.parent / f"{stem}-{counter}{suffix}"
                    counter += 1
                logger.info(f"Renaming to avoid conflict: {target_file}")

        # Install file
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(translated.content)

        # Calculate checksum
        from aiconfigkit.core.checksum import calculate_file_checksum

        checksum = calculate_file_checksum(str(target_file), "sha256")

        return InstalledComponent(
            type=ComponentType.INSTRUCTION,
            name=component.name,
            installed_path=str(target_file.relative_to(project_root)),
            checksum=checksum,
            status=ComponentStatus.INSTALLED,
        )

    except Exception as e:
        logger.error(f"Failed to install instruction {component.name}: {e}")
        return None


def _install_mcp_component(
    component: Any, package_path: Path, project_root: Path, translator: Any, conflict_resolution: ConflictResolution
) -> Optional[InstalledComponent]:
    """Install MCP server component."""
    try:
        # Translate component
        translated = translator.translate_mcp_server(component, package_path)
        target_file = project_root / translated.target_path

        # Check for conflicts
        if target_file.exists() and conflict_resolution == ConflictResolution.SKIP:
            return None

        # Create target directory
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Write MCP config file
        target_file.write_text(translated.content)

        # Calculate checksum
        from aiconfigkit.core.checksum import calculate_file_checksum

        checksum = calculate_file_checksum(str(target_file), "sha256")

        return InstalledComponent(
            type=ComponentType.MCP_SERVER,
            name=component.name,
            installed_path=str(target_file.relative_to(project_root)),
            checksum=checksum,
            status=ComponentStatus.INSTALLED,
        )

    except Exception as e:
        logger.error(f"Failed to install MCP server {component.name}: {e}")
        return None


def _install_hook_component(
    component: Any, package_path: Path, project_root: Path, translator: Any, conflict_resolution: ConflictResolution
) -> Optional[InstalledComponent]:
    """Install hook component."""
    try:
        translated = translator.translate_hook(component, package_path)
        target_file = project_root / translated.target_path

        # Check for conflicts
        if target_file.exists():
            if conflict_resolution == ConflictResolution.SKIP:
                logger.info(f"Skipping existing file: {target_file}")
                return None
            elif conflict_resolution == ConflictResolution.RENAME:
                # Find available numbered suffix
                counter = 1
                stem = target_file.stem
                suffix = target_file.suffix
                while target_file.exists():
                    target_file = target_file.parent / f"{stem}-{counter}{suffix}"
                    counter += 1
                logger.info(f"Renaming to avoid conflict: {target_file}")

        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(translated.content)
        target_file.chmod(0o755)  # Make executable

        from aiconfigkit.core.checksum import calculate_file_checksum

        checksum = calculate_file_checksum(str(target_file), "sha256")

        return InstalledComponent(
            type=ComponentType.HOOK,
            name=component.name,
            installed_path=str(target_file.relative_to(project_root)),
            checksum=checksum,
            status=ComponentStatus.INSTALLED,
        )

    except Exception as e:
        logger.error(f"Failed to install hook {component.name}: {e}")
        return None


def _install_command_component(
    component: Any, package_path: Path, project_root: Path, translator: Any, conflict_resolution: ConflictResolution
) -> Optional[InstalledComponent]:
    """Install command component."""
    try:
        translated = translator.translate_command(component, package_path)
        target_file = project_root / translated.target_path

        # Check for conflicts
        if target_file.exists():
            if conflict_resolution == ConflictResolution.SKIP:
                logger.info(f"Skipping existing file: {target_file}")
                return None
            elif conflict_resolution == ConflictResolution.RENAME:
                # Find available numbered suffix
                counter = 1
                stem = target_file.stem
                suffix = target_file.suffix
                while target_file.exists():
                    target_file = target_file.parent / f"{stem}-{counter}{suffix}"
                    counter += 1
                logger.info(f"Renaming to avoid conflict: {target_file}")

        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(translated.content)
        target_file.chmod(0o755)  # Make executable

        from aiconfigkit.core.checksum import calculate_file_checksum

        checksum = calculate_file_checksum(str(target_file), "sha256")

        return InstalledComponent(
            type=ComponentType.COMMAND,
            name=component.name,
            installed_path=str(target_file.relative_to(project_root)),
            checksum=checksum,
            status=ComponentStatus.INSTALLED,
        )

    except Exception as e:
        logger.error(f"Failed to install command {component.name}: {e}")
        return None


def _install_resource_component(
    component: Any, package_path: Path, project_root: Path, translator: Any, conflict_resolution: ConflictResolution
) -> Optional[InstalledComponent]:
    """Install resource component."""
    try:
        import shutil

        translated = translator.translate_resource(component, package_path)
        target_file = project_root / translated.target_path

        if target_file.exists() and conflict_resolution == ConflictResolution.SKIP:
            return None

        # Copy file directly (handles both text and binary)
        source_path = translated.metadata.get("source_path")
        if source_path:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_file)
        else:
            # Fallback to writing content (for compatibility)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(translated.content)

        from aiconfigkit.core.checksum import calculate_file_checksum

        checksum = calculate_file_checksum(str(target_file), "sha256")

        return InstalledComponent(
            type=ComponentType.RESOURCE,
            name=component.name,
            installed_path=str(target_file.relative_to(project_root)),
            checksum=checksum,
            status=ComponentStatus.INSTALLED,
        )

    except Exception as e:
        logger.error(f"Failed to install resource {component.name}: {e}")
        return None
