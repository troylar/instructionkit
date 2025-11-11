"""Unit tests for repository module."""

from pathlib import Path

import pytest

from aiconfigkit.core.repository import RepositoryParser


class TestRepositoryParserUnit:
    """Unit tests for RepositoryParser class methods."""

    def test_calculate_checksum(self, temp_dir: Path):
        """Test checksum calculation."""
        # Create minimal repo structure
        (temp_dir / "templatekit.yaml").write_text("name: Test\nversion: 1.0.0")

        parser = RepositoryParser(temp_dir)

        # Test checksum calculation
        content1 = "Hello, World!"
        checksum1 = parser._calculate_checksum(content1)

        # Same content should give same checksum
        checksum2 = parser._calculate_checksum(content1)
        assert checksum1 == checksum2

        # Different content should give different checksum
        content2 = "Hello, World!!"
        checksum3 = parser._calculate_checksum(content2)
        assert checksum1 != checksum3

        # Checksum should be SHA-256 (64 hex characters)
        assert len(checksum1) == 64

    def test_parse_bundle_validation(self, temp_dir: Path):
        """Test bundle validation during parsing."""
        yaml_content = """name: Test
version: 1.0.0

bundles:
  - name: test-bundle
    description: Test bundle
    instructions: []
"""
        (temp_dir / "templatekit.yaml").write_text(yaml_content)

        parser = RepositoryParser(temp_dir)

        with pytest.raises(ValueError, match="has no instructions"):
            parser.parse()

    def test_parse_instruction_validation(self, temp_dir: Path):
        """Test instruction validation during parsing."""
        yaml_content = """name: Test
version: 1.0.0

instructions:
  - name: test
    description: Test
"""
        (temp_dir / "templatekit.yaml").write_text(yaml_content)

        parser = RepositoryParser(temp_dir)

        with pytest.raises(ValueError, match="missing 'file' field"):
            parser.parse()

    def test_parse_empty_metadata(self, temp_dir: Path):
        """Test parsing empty metadata file."""
        (temp_dir / "templatekit.yaml").write_text("")

        parser = RepositoryParser(temp_dir)

        with pytest.raises(ValueError, match="empty"):
            parser.parse()

    def test_parse_instruction_without_name(self, temp_dir: Path):
        """Test parsing instruction without name."""
        yaml_content = """name: Test
version: 1.0.0

instructions:
  - description: Test
    file: test.md
"""
        (temp_dir / "templatekit.yaml").write_text(yaml_content)

        parser = RepositoryParser(temp_dir)

        with pytest.raises(ValueError, match="missing required 'name' field"):
            parser.parse()

    def test_parse_bundle_without_name(self, temp_dir: Path):
        """Test parsing bundle without name."""
        yaml_content = """name: Test
version: 1.0.0

bundles:
  - description: Test bundle
    instructions:
      - test
"""
        (temp_dir / "templatekit.yaml").write_text(yaml_content)

        parser = RepositoryParser(temp_dir)

        with pytest.raises(ValueError, match="missing required 'name' field"):
            parser.parse()
