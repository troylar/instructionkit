"""Repository parsing and management."""

import hashlib
import logging
from pathlib import Path
from typing import Optional

import yaml

from instructionkit.core.models import (
    AIToolType,
    Instruction,
    InstructionBundle,
    Repository,
)

logger = logging.getLogger(__name__)


class RepositoryParser:
    """Parse instruction repository metadata and files."""

    def __init__(self, repo_path: Path):
        """
        Initialize repository parser.

        Args:
            repo_path: Path to cloned repository
        """
        self.repo_path = repo_path
        self.metadata_file = repo_path / 'instructionkit.yaml'

    def parse(self) -> Repository:
        """
        Parse repository and return Repository object.

        Returns:
            Repository with instructions and bundles loaded

        Raises:
            FileNotFoundError: If instructionkit.yaml not found
            ValueError: If metadata is invalid
        """
        if not self.metadata_file.exists():
            raise FileNotFoundError(
                f"Repository metadata file not found: {self.metadata_file}"
            )

        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            metadata = yaml.safe_load(f)

        if not metadata:
            raise ValueError("Repository metadata file is empty")

        # Parse instructions
        instructions = []
        for inst_data in metadata.get('instructions', []):
            instruction = self._parse_instruction(inst_data)
            instructions.append(instruction)

        # Parse bundles
        bundles = []
        for bundle_data in metadata.get('bundles', []):
            bundle = self._parse_bundle(bundle_data)
            bundles.append(bundle)

        # Extract repository-level metadata
        repo_metadata = {
            'name': metadata.get('name', ''),
            'description': metadata.get('description', ''),
            'version': metadata.get('version', ''),
        }

        return Repository(
            url='',  # Will be set by caller
            instructions=instructions,
            bundles=bundles,
            metadata=repo_metadata,
        )

    def _parse_instruction(self, data: dict) -> Instruction:
        """Parse instruction from metadata dictionary."""
        name = data.get('name')
        if not name:
            raise ValueError("Instruction missing required 'name' field")

        description = data.get('description', '')
        file_path = data.get('file', '')

        if not file_path:
            raise ValueError(f"Instruction '{name}' missing 'file' field")

        # Load instruction content
        full_path = self.repo_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"Instruction file not found: {full_path}")

        content = full_path.read_text(encoding='utf-8')

        # Calculate checksum
        checksum = self._calculate_checksum(content)

        # Parse AI tools
        ai_tools = []
        for tool_str in data.get('ai_tools', []):
            try:
                ai_tools.append(AIToolType(tool_str.lower()))
            except ValueError:
                # Skip unknown AI tool types
                pass

        return Instruction(
            name=name,
            description=description,
            content=content,
            file_path=file_path,
            tags=data.get('tags', []),
            checksum=checksum,
            ai_tools=ai_tools,
        )

    def _parse_bundle(self, data: dict) -> InstructionBundle:
        """Parse bundle from metadata dictionary."""
        name = data.get('name')
        if not name:
            raise ValueError("Bundle missing required 'name' field")

        description = data.get('description', '')
        instructions = data.get('instructions', [])

        if not instructions:
            raise ValueError(f"Bundle '{name}' has no instructions")

        return InstructionBundle(
            name=name,
            description=description,
            instructions=instructions,
            tags=data.get('tags', []),
        )

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA-256 checksum of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_instruction_by_name(self, name: str) -> Optional[Instruction]:
        """
        Find instruction by name in repository.

        Args:
            name: Instruction name

        Returns:
            Instruction if found, None otherwise
        """
        repo = self.parse()
        for instruction in repo.instructions:
            if instruction.name == name:
                return instruction
        return None

    def get_bundle_by_name(self, name: str) -> Optional[InstructionBundle]:
        """
        Find bundle by name in repository.

        Args:
            name: Bundle name

        Returns:
            Bundle if found, None otherwise
        """
        repo = self.parse()
        for bundle in repo.bundles:
            if bundle.name == name:
                return bundle
        return None

    def get_instructions_for_bundle(self, bundle_name: str) -> list[Instruction]:
        """
        Get all instructions for a bundle.

        Args:
            bundle_name: Name of bundle

        Returns:
            List of Instruction objects

        Raises:
            ValueError: If bundle not found or instruction in bundle not found
        """
        bundle = self.get_bundle_by_name(bundle_name)
        if not bundle:
            raise ValueError(f"Bundle not found: {bundle_name}")

        repo = self.parse()
        instructions = []

        for inst_name in bundle.instructions:
            # Find instruction
            instruction = None
            for inst in repo.instructions:
                if inst.name == inst_name:
                    instruction = inst
                    break

            if not instruction:
                raise ValueError(
                    f"Bundle '{bundle_name}' references unknown instruction: {inst_name}"
                )

            instructions.append(instruction)

        return instructions


def validate_repository_structure(repo_path: Path) -> Optional[str]:
    """
    Validate repository has correct structure.

    Args:
        repo_path: Path to repository

    Returns:
        None if valid, error message if invalid
    """
    # Check for metadata file
    metadata_file = repo_path / 'instructionkit.yaml'
    if not metadata_file.exists():
        return "Missing instructionkit.yaml metadata file"

    # Try to parse metadata
    try:
        parser = RepositoryParser(repo_path)
        repo = parser.parse()

        # Validate at least one instruction or bundle
        if not repo.instructions and not repo.bundles:
            return "Repository has no instructions or bundles"

    except Exception as e:
        return f"Invalid repository metadata: {str(e)}"

    return None
