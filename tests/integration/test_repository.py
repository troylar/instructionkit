"""Integration tests for repository parsing and management."""

from pathlib import Path

import pytest

from aiconfigkit.core.models import Repository
from aiconfigkit.core.repository import RepositoryParser, validate_repository_structure


class TestRepositoryParser:
    """Test repository parsing functionality."""

    def test_parse_valid_repository(self, mock_instruction_repo: Path):
        """Test parsing a valid instruction repository."""
        parser = RepositoryParser(mock_instruction_repo)
        repo = parser.parse()

        assert isinstance(repo, Repository)
        assert len(repo.instructions) == 2
        assert len(repo.bundles) == 1
        assert repo.metadata["name"] == "Test Instructions"
        assert repo.metadata["version"] == "1.0.0"

    def test_parse_instructions(self, mock_instruction_repo: Path):
        """Test that instructions are parsed correctly."""
        parser = RepositoryParser(mock_instruction_repo)
        repo = parser.parse()

        # Check first instruction
        python_style = next((i for i in repo.instructions if i.name == "python-style"), None)
        assert python_style is not None
        assert python_style.description == "Python style guidelines"
        assert "python" in python_style.tags
        assert "Follow PEP 8" in python_style.content
        assert python_style.checksum is not None

    def test_parse_bundles(self, mock_instruction_repo: Path):
        """Test that bundles are parsed correctly."""
        parser = RepositoryParser(mock_instruction_repo)
        repo = parser.parse()

        bundle = repo.bundles[0]
        assert bundle.name == "python-stack"
        assert len(bundle.instructions) == 2
        assert "python-style" in bundle.instructions
        assert "testing-guide" in bundle.instructions

    def test_get_instruction_by_name(self, mock_instruction_repo: Path):
        """Test getting instruction by name."""
        parser = RepositoryParser(mock_instruction_repo)

        instruction = parser.get_instruction_by_name("python-style")
        assert instruction is not None
        assert instruction.name == "python-style"

    def test_get_instruction_by_name_not_found(self, mock_instruction_repo: Path):
        """Test getting non-existent instruction."""
        parser = RepositoryParser(mock_instruction_repo)

        instruction = parser.get_instruction_by_name("nonexistent")
        assert instruction is None

    def test_get_bundle_by_name(self, mock_instruction_repo: Path):
        """Test getting bundle by name."""
        parser = RepositoryParser(mock_instruction_repo)

        bundle = parser.get_bundle_by_name("python-stack")
        assert bundle is not None
        assert bundle.name == "python-stack"

    def test_get_instructions_for_bundle(self, mock_instruction_repo: Path):
        """Test getting all instructions in a bundle."""
        parser = RepositoryParser(mock_instruction_repo)

        instructions = parser.get_instructions_for_bundle("python-stack")
        assert len(instructions) == 2
        names = [inst.name for inst in instructions]
        assert "python-style" in names
        assert "testing-guide" in names

    def test_get_instructions_for_nonexistent_bundle(self, mock_instruction_repo: Path):
        """Test getting instructions for non-existent bundle."""
        parser = RepositoryParser(mock_instruction_repo)

        with pytest.raises(ValueError, match="Bundle not found"):
            parser.get_instructions_for_bundle("nonexistent")

    def test_missing_metadata_file(self, temp_dir: Path):
        """Test error when metadata file is missing."""
        parser = RepositoryParser(temp_dir)

        with pytest.raises(FileNotFoundError, match="metadata file not found"):
            parser.parse()

    def test_missing_instruction_file(self, temp_dir: Path):
        """Test error when instruction file is missing."""
        # Create repo with metadata but missing instruction file
        yaml_content = """name: Test
description: Test
version: 1.0.0

instructions:
  - name: test
    description: Test
    file: instructions/missing.md
"""
        (temp_dir / "templatekit.yaml").write_text(yaml_content)

        parser = RepositoryParser(temp_dir)

        with pytest.raises(FileNotFoundError, match="Instruction file not found"):
            parser.parse()


class TestRepositoryValidation:
    """Test repository structure validation."""

    def test_validate_valid_repository(self, mock_instruction_repo: Path):
        """Test validation of valid repository."""
        error = validate_repository_structure(mock_instruction_repo)
        assert error is None

    def test_validate_missing_metadata(self, temp_dir: Path):
        """Test validation when metadata file is missing."""
        error = validate_repository_structure(temp_dir)
        assert error is not None
        assert "Missing templatekit.yaml" in error

    def test_validate_empty_repository(self, temp_dir: Path):
        """Test validation when repository has no instructions."""
        yaml_content = """name: Empty Repo
description: No instructions
version: 1.0.0

instructions: []
bundles: []
"""
        (temp_dir / "templatekit.yaml").write_text(yaml_content)

        error = validate_repository_structure(temp_dir)
        assert error is not None
        assert "no instructions or bundles" in error
