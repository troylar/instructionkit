"""Template manifest parsing and validation."""

from pathlib import Path
from typing import Any

import yaml

from instructionkit.core.models import TemplateBundle, TemplateDefinition, TemplateFile, TemplateManifest


class TemplateManifestError(Exception):
    """Raised when template manifest is invalid."""

    pass


def load_manifest(manifest_path: Path) -> TemplateManifest:
    """
    Load and validate template manifest from YAML file.

    Args:
        manifest_path: Path to templatekit.yaml

    Returns:
        Parsed and validated TemplateManifest

    Raises:
        TemplateManifestError: If manifest is invalid or missing
        FileNotFoundError: If manifest file doesn't exist

    Example:
        >>> from pathlib import Path
        >>> manifest = load_manifest(Path("repo/templatekit.yaml"))
        >>> manifest.name
        'My Templates'
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise TemplateManifestError(f"Invalid YAML in manifest: {e}") from e

    if not data:
        raise TemplateManifestError("Manifest file is empty")

    try:
        return parse_manifest(data, manifest_path)
    except (ValueError, KeyError) as e:
        raise TemplateManifestError(f"Invalid manifest structure: {e}") from e


def parse_manifest(data: dict[str, Any], manifest_path: Path) -> TemplateManifest:
    """
    Parse manifest data into TemplateManifest object.

    Args:
        data: Parsed YAML data
        manifest_path: Path to manifest (for validation context)

    Returns:
        TemplateManifest object

    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Required fields
    if "name" not in data:
        raise ValueError("Manifest missing required field: name")
    if "description" not in data:
        raise ValueError("Manifest missing required field: description")
    if "version" not in data:
        raise ValueError("Manifest missing required field: version")
    if "templates" not in data:
        raise ValueError("Manifest missing required field: templates")

    # Parse templates
    templates = []
    for template_data in data["templates"]:
        template = parse_template(template_data, manifest_path)
        templates.append(template)

    # Parse bundles (optional)
    bundles = []
    if "bundles" in data:
        for bundle_data in data["bundles"]:
            bundle = parse_bundle(bundle_data)
            bundles.append(bundle)

    # Validate bundle references
    template_names = {t.name for t in templates}
    for bundle in bundles:
        for template_ref in bundle.template_refs:
            if template_ref not in template_names:
                raise ValueError(f"Bundle '{bundle.name}' references non-existent template '{template_ref}'")

    return TemplateManifest(
        name=data["name"],
        description=data["description"],
        version=data["version"],
        author=data.get("author"),
        templates=templates,
        bundles=bundles,
    )


def parse_template(data: dict[str, Any], manifest_path: Path) -> TemplateDefinition:
    """
    Parse template definition from manifest data.

    Args:
        data: Template data from manifest
        manifest_path: Path to manifest (for file validation)

    Returns:
        TemplateDefinition object

    Raises:
        ValueError: If template data is invalid
    """
    if "name" not in data:
        raise ValueError("Template missing required field: name")
    if "description" not in data:
        raise ValueError(f"Template '{data.get('name', 'unknown')}' missing required field: description")
    if "files" not in data or not data["files"]:
        raise ValueError(f"Template '{data['name']}' must have at least one file")

    # Parse files
    files = []
    for file_data in data["files"]:
        if isinstance(file_data, str):
            # Simple format: just path string
            file_obj = TemplateFile(path=file_data, ide="all")
        elif isinstance(file_data, dict):
            # Detailed format with path and ide
            if "path" not in file_data:
                raise ValueError(f"Template '{data['name']}' file entry missing 'path'")
            file_obj = TemplateFile(path=file_data["path"], ide=file_data.get("ide", "all"))
        else:
            raise ValueError(f"Invalid file entry in template '{data['name']}': {file_data}")

        # Validate file exists in repository
        repo_path = manifest_path.parent
        file_path = repo_path / file_obj.path
        if not file_path.exists():
            raise ValueError(f"Template '{data['name']}' references non-existent file: {file_obj.path}")

        files.append(file_obj)

    return TemplateDefinition(
        name=data["name"],
        description=data["description"],
        files=files,
        tags=data.get("tags", []),
        dependencies=data.get("dependencies", []),
    )


def parse_bundle(data: dict[str, Any]) -> TemplateBundle:
    """
    Parse bundle definition from manifest data.

    Args:
        data: Bundle data from manifest

    Returns:
        TemplateBundle object

    Raises:
        ValueError: If bundle data is invalid
    """
    if "name" not in data:
        raise ValueError("Bundle missing required field: name")
    if "description" not in data:
        raise ValueError(f"Bundle '{data.get('name', 'unknown')}' missing required field: description")
    if "templates" not in data or not data["templates"]:
        raise ValueError(f"Bundle '{data['name']}' must reference at least one template")

    return TemplateBundle(
        name=data["name"],
        description=data["description"],
        template_refs=data["templates"],
        tags=data.get("tags", []),
    )


def validate_manifest_size(manifest_path: Path, template_count: int, soft_limit_templates: int = 100) -> list[str]:
    """
    Check manifest against soft limits and return warnings.

    Args:
        manifest_path: Path to manifest
        template_count: Number of templates in manifest
        soft_limit_templates: Soft limit for template count

    Returns:
        List of warning messages (empty if no warnings)

    Example:
        >>> warnings = validate_manifest_size(Path("repo/templatekit.yaml"), 150)
        >>> len(warnings) > 0
        True
    """
    warnings = []

    # Check template count
    if template_count > soft_limit_templates:
        warnings.append(
            f"⚠️  Repository contains {template_count} templates "
            f"(soft limit: {soft_limit_templates}). "
            f"Large repositories may take longer to install."
        )

    # Check repository size (approximate based on manifest directory)
    repo_path = manifest_path.parent
    total_size = 0
    for file_path in repo_path.rglob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size

    size_mb = total_size / (1024 * 1024)
    soft_limit_mb = 50

    if size_mb > soft_limit_mb:
        warnings.append(
            f"⚠️  Repository size is {size_mb:.1f}MB "
            f"(soft limit: {soft_limit_mb}MB). "
            f"Installation may take longer."
        )

    return warnings


def validate_dependencies(templates: list[TemplateDefinition]) -> list[str]:
    """
    Validate template dependencies for circular references.

    Args:
        templates: List of template definitions

    Returns:
        List of error messages (empty if valid)

    Example:
        >>> errors = validate_dependencies(templates)
        >>> len(errors) == 0
        True
    """
    errors = []
    template_names = {t.name for t in templates}

    # Build dependency graph
    dependencies = {t.name: set(t.dependencies) for t in templates}

    # Check for circular dependencies using DFS
    def has_cycle(node: str, visited: set[str], rec_stack: set[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)

        for neighbor in dependencies.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    visited: set[str] = set()
    for template in templates:
        if template.name not in visited:
            if has_cycle(template.name, visited, set()):
                errors.append(f"Circular dependency detected involving template '{template.name}'")

        # Check for non-existent dependencies
        for dep in template.dependencies:
            if dep not in template_names:
                errors.append(f"Template '{template.name}' depends on non-existent template '{dep}'")

    return errors
