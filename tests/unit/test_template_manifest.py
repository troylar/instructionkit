"""Tests for template manifest parsing and validation."""

import pytest

from aiconfigkit.core.models import TemplateDefinition
from aiconfigkit.core.template_manifest import (
    TemplateManifestError,
    load_manifest,
    parse_bundle,
    parse_manifest,
    parse_template,
    validate_dependencies,
    validate_manifest_size,
)


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository structure."""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()

    # Create template files
    (repo_path / ".claude").mkdir(parents=True)
    (repo_path / ".claude" / "rules").mkdir()
    (repo_path / ".claude" / "commands").mkdir()

    (repo_path / ".claude" / "rules" / "python-standards.md").write_text("# Python Standards")
    (repo_path / ".claude" / "commands" / "test-api.md").write_text("# Test API")

    return repo_path


@pytest.fixture
def minimal_manifest(temp_repo):
    """Create minimal valid manifest."""
    manifest_path = temp_repo / "templatekit.yaml"
    manifest_path.write_text(
        """
name: Test Templates
description: Test template repository
version: 1.0.0
templates:
  - name: python-standards
    description: Python coding standards
    files:
      - path: .claude/rules/python-standards.md
"""
    )
    return manifest_path


class TestLoadManifest:
    """Tests for load_manifest function."""

    def test_load_valid_manifest(self, minimal_manifest):
        """Test loading a valid manifest."""
        manifest = load_manifest(minimal_manifest)
        assert manifest.name == "Test Templates"
        assert manifest.version == "1.0.0"
        assert len(manifest.templates) == 1

    def test_missing_file_raises(self, tmp_path):
        """Test that missing manifest file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_manifest(tmp_path / "nonexistent.yaml")

    def test_empty_file_raises(self, tmp_path):
        """Test that empty manifest file raises error."""
        manifest_path = tmp_path / "templatekit.yaml"
        manifest_path.write_text("")

        with pytest.raises(TemplateManifestError, match="empty"):
            load_manifest(manifest_path)

    def test_invalid_yaml_raises(self, tmp_path):
        """Test that invalid YAML raises error."""
        manifest_path = tmp_path / "templatekit.yaml"
        manifest_path.write_text("name: Test\n  invalid: yaml: syntax")

        with pytest.raises(TemplateManifestError, match="Invalid YAML"):
            load_manifest(manifest_path)

    def test_manifest_with_author(self, temp_repo):
        """Test manifest with optional author field."""
        manifest_path = temp_repo / "templatekit.yaml"
        manifest_path.write_text(
            """
name: Test Templates
description: Test repository
version: 1.0.0
author: Test Author
templates:
  - name: python-standards
    description: Python standards
    files:
      - path: .claude/rules/python-standards.md
"""
        )
        manifest = load_manifest(manifest_path)
        assert manifest.author == "Test Author"

    def test_manifest_with_bundles(self, temp_repo):
        """Test manifest with bundles."""
        manifest_path = temp_repo / "templatekit.yaml"
        manifest_path.write_text(
            """
name: Test Templates
description: Test repository
version: 1.0.0
templates:
  - name: python-standards
    description: Python standards
    files:
      - path: .claude/rules/python-standards.md
  - name: test-api
    description: Test API command
    files:
      - path: .claude/commands/test-api.md
bundles:
  - name: python-stack
    description: Complete Python setup
    templates:
      - python-standards
      - test-api
    tags: [python]
"""
        )
        manifest = load_manifest(manifest_path)
        assert len(manifest.bundles) == 1
        assert manifest.bundles[0].name == "python-stack"
        assert len(manifest.bundles[0].template_refs) == 2

    def test_manifest_with_invalid_structure_raises(self, temp_repo):
        """Test that invalid manifest structure raises TemplateManifestError."""
        manifest_path = temp_repo / "templatekit.yaml"
        # Create a manifest that will cause ValueError in parse_manifest
        manifest_path.write_text(
            """
name: 123
description: Test
version: 1.0.0
templates: not_a_list
"""
        )

        with pytest.raises(TemplateManifestError, match="Invalid manifest structure"):
            load_manifest(manifest_path)


class TestParseManifest:
    """Tests for parse_manifest function."""

    def test_missing_name_raises(self, temp_repo):
        """Test that missing name field raises error."""
        data = {"description": "Test", "version": "1.0.0", "templates": []}
        with pytest.raises(ValueError, match="name"):
            parse_manifest(data, temp_repo / "templatekit.yaml")

    def test_missing_description_raises(self, temp_repo):
        """Test that missing description field raises error."""
        data = {"name": "Test", "version": "1.0.0", "templates": []}
        with pytest.raises(ValueError, match="description"):
            parse_manifest(data, temp_repo / "templatekit.yaml")

    def test_missing_version_raises(self, temp_repo):
        """Test that missing version field raises error."""
        data = {"name": "Test", "description": "Test", "templates": []}
        with pytest.raises(ValueError, match="version"):
            parse_manifest(data, temp_repo / "templatekit.yaml")

    def test_missing_templates_raises(self, temp_repo):
        """Test that missing templates field raises error."""
        data = {"name": "Test", "description": "Test", "version": "1.0.0"}
        with pytest.raises(ValueError, match="templates"):
            parse_manifest(data, temp_repo / "templatekit.yaml")

    def test_bundle_with_invalid_template_reference(self, temp_repo):
        """Test that bundle referencing non-existent template raises error."""
        data = {
            "name": "Test",
            "description": "Test",
            "version": "1.0.0",
            "templates": [
                {
                    "name": "template1",
                    "description": "Test",
                    "files": [{"path": ".claude/rules/python-standards.md"}],
                }
            ],
            "bundles": [
                {
                    "name": "bundle1",
                    "description": "Test bundle",
                    "templates": ["template1", "nonexistent"],
                }
            ],
        }

        with pytest.raises(ValueError, match="non-existent template"):
            parse_manifest(data, temp_repo / "templatekit.yaml")


class TestParseTemplate:
    """Tests for parse_template function."""

    def test_parse_minimal_template(self, temp_repo):
        """Test parsing minimal template definition."""
        data = {
            "name": "python-standards",
            "description": "Python coding standards",
            "files": [{"path": ".claude/rules/python-standards.md"}],
        }

        template = parse_template(data, temp_repo / "templatekit.yaml")
        assert template.name == "python-standards"
        assert template.description == "Python coding standards"
        assert len(template.files) == 1
        assert template.tags == []
        assert template.dependencies == []

    def test_parse_template_with_tags(self, temp_repo):
        """Test parsing template with tags."""
        data = {
            "name": "python-standards",
            "description": "Python standards",
            "files": [{"path": ".claude/rules/python-standards.md"}],
            "tags": ["python", "standards"],
        }

        template = parse_template(data, temp_repo / "templatekit.yaml")
        assert template.tags == ["python", "standards"]

    def test_parse_template_with_dependencies(self, temp_repo):
        """Test parsing template with dependencies."""
        data = {
            "name": "python-standards",
            "description": "Python standards",
            "files": [{"path": ".claude/rules/python-standards.md"}],
            "dependencies": ["base-standards"],
        }

        template = parse_template(data, temp_repo / "templatekit.yaml")
        assert template.dependencies == ["base-standards"]

    def test_missing_name_raises(self, temp_repo):
        """Test that template missing name raises error."""
        data = {
            "description": "Test",
            "files": [{"path": ".claude/rules/python-standards.md"}],
        }

        with pytest.raises(ValueError, match="name"):
            parse_template(data, temp_repo / "templatekit.yaml")

    def test_missing_description_raises(self, temp_repo):
        """Test that template missing description raises error."""
        data = {
            "name": "test",
            "files": [{"path": ".claude/rules/python-standards.md"}],
        }

        with pytest.raises(ValueError, match="description"):
            parse_template(data, temp_repo / "templatekit.yaml")

    def test_missing_files_raises(self, temp_repo):
        """Test that template missing files raises error."""
        data = {"name": "test", "description": "Test"}

        with pytest.raises(ValueError, match="at least one file"):
            parse_template(data, temp_repo / "templatekit.yaml")

    def test_empty_files_list_raises(self, temp_repo):
        """Test that template with empty files list raises error."""
        data = {"name": "test", "description": "Test", "files": []}

        with pytest.raises(ValueError, match="at least one file"):
            parse_template(data, temp_repo / "templatekit.yaml")

    def test_nonexistent_file_raises(self, temp_repo):
        """Test that reference to non-existent file raises error."""
        data = {
            "name": "test",
            "description": "Test",
            "files": [{"path": ".claude/rules/nonexistent.md"}],
        }

        with pytest.raises(ValueError, match="non-existent file"):
            parse_template(data, temp_repo / "templatekit.yaml")

    def test_simple_file_format(self, temp_repo):
        """Test parsing template with simple file format (just path string)."""
        data = {
            "name": "python-standards",
            "description": "Python standards",
            "files": [".claude/rules/python-standards.md"],
        }

        template = parse_template(data, temp_repo / "templatekit.yaml")
        assert len(template.files) == 1
        assert template.files[0].path == ".claude/rules/python-standards.md"
        assert template.files[0].ide == "all"

    def test_detailed_file_format(self, temp_repo):
        """Test parsing template with detailed file format."""
        data = {
            "name": "python-standards",
            "description": "Python standards",
            "files": [{"path": ".claude/rules/python-standards.md", "ide": "claude"}],
        }

        template = parse_template(data, temp_repo / "templatekit.yaml")
        assert template.files[0].ide == "claude"

    def test_file_without_path_raises(self, temp_repo):
        """Test that file entry without path raises error."""
        data = {
            "name": "test",
            "description": "Test",
            "files": [{"ide": "claude"}],
        }

        with pytest.raises(ValueError, match="missing 'path'"):
            parse_template(data, temp_repo / "templatekit.yaml")

    def test_invalid_file_entry_type_raises(self, temp_repo):
        """Test that invalid file entry type raises error."""
        data = {
            "name": "test",
            "description": "Test",
            "files": [123],  # Invalid: not string or dict
        }

        with pytest.raises(ValueError, match="Invalid file entry"):
            parse_template(data, temp_repo / "templatekit.yaml")


class TestParseBundle:
    """Tests for parse_bundle function."""

    def test_parse_minimal_bundle(self):
        """Test parsing minimal bundle definition."""
        data = {
            "name": "python-stack",
            "description": "Complete Python setup",
            "templates": ["python-standards", "test-api"],
        }

        bundle = parse_bundle(data)
        assert bundle.name == "python-stack"
        assert bundle.description == "Complete Python setup"
        assert bundle.template_refs == ["python-standards", "test-api"]
        assert bundle.tags == []

    def test_parse_bundle_with_tags(self):
        """Test parsing bundle with tags."""
        data = {
            "name": "python-stack",
            "description": "Complete Python setup",
            "templates": ["python-standards", "test-api"],
            "tags": ["python", "backend"],
        }

        bundle = parse_bundle(data)
        assert bundle.tags == ["python", "backend"]

    def test_missing_name_raises(self):
        """Test that bundle missing name raises error."""
        data = {
            "description": "Test",
            "templates": ["template1"],
        }

        with pytest.raises(ValueError, match="name"):
            parse_bundle(data)

    def test_missing_description_raises(self):
        """Test that bundle missing description raises error."""
        data = {
            "name": "test",
            "templates": ["template1"],
        }

        with pytest.raises(ValueError, match="description"):
            parse_bundle(data)

    def test_missing_templates_raises(self):
        """Test that bundle missing templates field raises error."""
        data = {
            "name": "test",
            "description": "Test",
        }

        with pytest.raises(ValueError, match="at least one template"):
            parse_bundle(data)

    def test_empty_templates_list_raises(self):
        """Test that bundle with empty templates list raises error."""
        data = {
            "name": "test",
            "description": "Test",
            "templates": [],
        }

        with pytest.raises(ValueError, match="at least one template"):
            parse_bundle(data)


class TestValidateManifestSize:
    """Tests for validate_manifest_size function."""

    def test_small_manifest_no_warnings(self, temp_repo):
        """Test that small manifest produces no warnings."""
        manifest_path = temp_repo / "templatekit.yaml"
        manifest_path.write_text("test: content")

        warnings = validate_manifest_size(manifest_path, 50)
        assert len(warnings) == 0

    def test_large_template_count_warning(self, temp_repo):
        """Test that large template count produces warning."""
        manifest_path = temp_repo / "templatekit.yaml"
        manifest_path.write_text("test: content")

        warnings = validate_manifest_size(manifest_path, 150)
        assert len(warnings) > 0
        assert any("150 templates" in w for w in warnings)

    def test_large_repository_size_warning(self, temp_repo):
        """Test that large repository size produces warning."""
        manifest_path = temp_repo / "templatekit.yaml"

        # Create large file (>50MB worth of content)
        large_file = temp_repo / "large.dat"
        large_file.write_bytes(b"x" * (51 * 1024 * 1024))

        warnings = validate_manifest_size(manifest_path, 10)
        assert len(warnings) > 0
        assert any("MB" in w for w in warnings)

    def test_custom_soft_limit(self, temp_repo):
        """Test using custom soft limit for template count."""
        manifest_path = temp_repo / "templatekit.yaml"
        manifest_path.write_text("test: content")

        warnings = validate_manifest_size(manifest_path, 60, soft_limit_templates=50)
        assert len(warnings) > 0


class TestValidateDependencies:
    """Tests for validate_dependencies function."""

    @pytest.fixture
    def dummy_file(self):
        """Create a dummy template file for testing."""
        from aiconfigkit.core.models import TemplateFile

        return [TemplateFile(path="test.md", ide="all")]

    def test_no_dependencies_valid(self, dummy_file):
        """Test that templates without dependencies are valid."""
        templates = [
            TemplateDefinition(name="template1", description="Test 1", files=dummy_file, tags=[], dependencies=[]),
            TemplateDefinition(name="template2", description="Test 2", files=dummy_file, tags=[], dependencies=[]),
        ]

        errors = validate_dependencies(templates)
        assert len(errors) == 0

    def test_valid_dependencies(self, dummy_file):
        """Test that valid dependencies pass validation."""
        templates = [
            TemplateDefinition(name="base", description="Base", files=dummy_file, tags=[], dependencies=[]),
            TemplateDefinition(
                name="extended", description="Extended", files=dummy_file, tags=[], dependencies=["base"]
            ),
        ]

        errors = validate_dependencies(templates)
        assert len(errors) == 0

    def test_circular_dependency_detected(self, dummy_file):
        """Test that circular dependencies are detected."""
        templates = [
            TemplateDefinition(
                name="template1", description="Test 1", files=dummy_file, tags=[], dependencies=["template2"]
            ),
            TemplateDefinition(
                name="template2", description="Test 2", files=dummy_file, tags=[], dependencies=["template1"]
            ),
        ]

        errors = validate_dependencies(templates)
        assert len(errors) > 0
        assert any("Circular dependency" in e for e in errors)

    def test_self_circular_dependency(self, dummy_file):
        """Test that self-referencing template is detected."""
        templates = [
            TemplateDefinition(
                name="template1", description="Test", files=dummy_file, tags=[], dependencies=["template1"]
            ),
        ]

        errors = validate_dependencies(templates)
        assert len(errors) > 0

    def test_nonexistent_dependency_detected(self, dummy_file):
        """Test that non-existent dependency is detected."""
        templates = [
            TemplateDefinition(
                name="template1", description="Test", files=dummy_file, tags=[], dependencies=["nonexistent"]
            ),
        ]

        errors = validate_dependencies(templates)
        assert len(errors) > 0
        assert any("non-existent template" in e for e in errors)

    def test_complex_dependency_chain(self, dummy_file):
        """Test complex but valid dependency chain."""
        templates = [
            TemplateDefinition(name="base", description="Base", files=dummy_file, tags=[], dependencies=[]),
            TemplateDefinition(name="layer1", description="Layer 1", files=dummy_file, tags=[], dependencies=["base"]),
            TemplateDefinition(
                name="layer2", description="Layer 2", files=dummy_file, tags=[], dependencies=["layer1"]
            ),
            TemplateDefinition(
                name="layer3", description="Layer 3", files=dummy_file, tags=[], dependencies=["layer2"]
            ),
        ]

        errors = validate_dependencies(templates)
        assert len(errors) == 0

    def test_indirect_circular_dependency(self, dummy_file):
        """Test that indirect circular dependency is detected."""
        templates = [
            TemplateDefinition(
                name="template1", description="Test 1", files=dummy_file, tags=[], dependencies=["template2"]
            ),
            TemplateDefinition(
                name="template2", description="Test 2", files=dummy_file, tags=[], dependencies=["template3"]
            ),
            TemplateDefinition(
                name="template3", description="Test 3", files=dummy_file, tags=[], dependencies=["template1"]
            ),
        ]

        errors = validate_dependencies(templates)
        assert len(errors) > 0
        assert any("Circular dependency" in e for e in errors)
