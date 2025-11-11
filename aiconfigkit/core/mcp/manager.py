"""MCP template installation and library management."""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from aiconfigkit.core.git_operations import GitOperations
from aiconfigkit.core.models import InstallationScope, MCPTemplate
from aiconfigkit.core.repository import RepositoryParser

logger = logging.getLogger(__name__)


class MCPManager:
    """Manages MCP template installation and library operations."""

    def __init__(self, library_root: Path):
        """
        Initialize MCP manager.

        Args:
            library_root: Root directory for MCP library (e.g., ~/.instructionkit/library/)
        """
        self.library_root = library_root
        self.library_root.mkdir(parents=True, exist_ok=True)

    def install_template(
        self,
        source: str,
        namespace: str,
        scope: InstallationScope = InstallationScope.PROJECT,
        force: bool = False,
    ) -> MCPTemplate:
        """
        Install MCP template from source URL or local path.

        Args:
            source: Git URL or local directory path
            namespace: Unique identifier for this template
            scope: Installation scope (PROJECT or GLOBAL)
            force: Overwrite existing template if it exists

        Returns:
            MCPTemplate object representing the installed template

        Raises:
            ValueError: If namespace is invalid or already exists (without force)
            FileNotFoundError: If source path doesn't exist
            RuntimeError: If Git clone/copy fails
        """
        # Validate namespace
        self._validate_namespace(namespace)

        # Get installation path
        install_path = self._get_install_path(namespace, scope)

        # Check if already exists
        if install_path.exists() and not force:
            raise ValueError(
                f"Template namespace '{namespace}' already exists at {install_path}. " f"Use --force to overwrite."
            )

        # Remove existing if force
        if install_path.exists() and force:
            logger.info(f"Removing existing template at {install_path}")
            shutil.rmtree(install_path)

        # Install from source
        source_url: Optional[str] = None
        source_path: Optional[str] = None

        if source.startswith(("http://", "https://", "git@")):
            # Git URL
            source_url = source
            self._install_from_git(source, install_path)
        else:
            # Local path
            source_path_obj = Path(source).resolve()
            if not source_path_obj.exists():
                raise FileNotFoundError(f"Source path does not exist: {source}")
            source_path = str(source_path_obj)
            self._install_from_local(source_path_obj, install_path)

        # Parse template
        parser = RepositoryParser(install_path)
        metadata = self._parse_metadata(install_path)

        # Parse MCP servers and sets
        servers = parser.parse_mcp_servers(namespace)
        sets = parser.parse_mcp_sets(namespace)

        # Create MCPTemplate
        template = MCPTemplate(
            namespace=namespace,
            source_url=source_url,
            source_path=source_path,
            version=metadata.get("version", "unknown"),
            description=metadata.get("description", ""),
            installed_at=datetime.now(),
            servers=servers,
            sets=sets,
        )

        # Save template metadata
        self._save_template_metadata(template, install_path)

        logger.info(f"Installed MCP template '{namespace}' with {len(servers)} servers and {len(sets)} sets")

        return template

    def _validate_namespace(self, namespace: str) -> None:
        """
        Validate namespace format.

        Args:
            namespace: Namespace to validate

        Raises:
            ValueError: If namespace is invalid
        """
        import re

        if not namespace:
            raise ValueError("Namespace cannot be empty")

        # Check for path separators first (security)
        if "/" in namespace or "\\" in namespace:
            raise ValueError(f"Namespace cannot contain path separators: {namespace}")

        if not re.match(r"^[a-zA-Z0-9_-]+$", namespace):
            raise ValueError(
                f"Invalid namespace: {namespace}. "
                f"Must contain only alphanumeric characters, hyphens, and underscores."
            )

    def _get_install_path(self, namespace: str, scope: InstallationScope) -> Path:
        """
        Get installation path for template.

        Args:
            namespace: Template namespace
            scope: Installation scope

        Returns:
            Path to install location
        """
        if scope == InstallationScope.GLOBAL:
            return self.library_root / "global" / namespace
        else:
            return self.library_root / namespace

    def _install_from_git(self, git_url: str, dest_path: Path) -> None:
        """
        Install template from Git repository.

        Args:
            git_url: Git repository URL
            dest_path: Destination path

        Raises:
            RuntimeError: If Git clone fails
        """
        logger.info(f"Cloning Git repository: {git_url}")

        try:
            git_ops = GitOperations()
            git_ops.clone_repository(git_url, dest_path)
        except Exception as e:
            raise RuntimeError(f"Failed to clone Git repository: {e}") from e

    def _install_from_local(self, source_path: Path, dest_path: Path) -> None:
        """
        Install template from local directory.

        Args:
            source_path: Source directory path
            dest_path: Destination path
        """
        logger.info(f"Copying from local path: {source_path}")

        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy directory contents
        shutil.copytree(source_path, dest_path, dirs_exist_ok=False)

    def _parse_metadata(self, template_path: Path) -> dict:
        """
        Parse template metadata from aiconfigkit.yaml.

        Args:
            template_path: Path to template directory

        Returns:
            Dictionary with metadata
        """
        import yaml

        metadata_file = template_path / "templatekit.yaml"
        if not metadata_file.exists():
            # Try templatekit.yaml as alternative
            metadata_file = template_path / "templatekit.yaml"

        if not metadata_file.exists():
            logger.warning(f"No metadata file found in {template_path}")
            return {}

        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        return metadata or {}

    def _save_template_metadata(self, template: MCPTemplate, install_path: Path) -> None:
        """
        Save template metadata to .mcp_template.json.

        Args:
            template: MCPTemplate to save
            install_path: Installation path
        """
        import json

        metadata_file = install_path / ".mcp_template.json"

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(template.to_dict(), f, indent=2)

    def load_template(
        self, namespace: str, scope: InstallationScope = InstallationScope.PROJECT
    ) -> Optional[MCPTemplate]:
        """
        Load installed template by namespace.

        Args:
            namespace: Template namespace
            scope: Installation scope

        Returns:
            MCPTemplate if found, None otherwise
        """
        import json

        install_path = self._get_install_path(namespace, scope)
        metadata_file = install_path / ".mcp_template.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return MCPTemplate.from_dict(data)

    def list_templates(self, scope: InstallationScope = InstallationScope.PROJECT) -> list[MCPTemplate]:
        """
        List all installed MCP templates.

        Args:
            scope: Installation scope to list

        Returns:
            List of MCPTemplate objects
        """
        templates = []

        if scope == InstallationScope.GLOBAL:
            search_path = self.library_root / "global"
        else:
            search_path = self.library_root

        if not search_path.exists():
            return []

        # Find all .mcp_template.json files
        for metadata_file in search_path.glob("**/.mcp_template.json"):
            try:
                import json

                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                template = MCPTemplate.from_dict(data)
                templates.append(template)
            except Exception as e:
                logger.warning(f"Failed to load template from {metadata_file}: {e}")

        return templates

    def uninstall_template(self, namespace: str, scope: InstallationScope = InstallationScope.PROJECT) -> bool:
        """
        Uninstall MCP template.

        Args:
            namespace: Template namespace
            scope: Installation scope

        Returns:
            True if uninstalled, False if not found
        """
        install_path = self._get_install_path(namespace, scope)

        if not install_path.exists():
            return False

        shutil.rmtree(install_path)
        logger.info(f"Uninstalled MCP template '{namespace}'")

        return True
