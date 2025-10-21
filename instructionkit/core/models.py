"""Core data models for InstructionKit."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AIToolType(Enum):
    """Supported AI coding tool types."""
    CURSOR = "cursor"
    COPILOT = "copilot"
    WINSURF = "winsurf"
    CLAUDE = "claude"


class ConflictResolution(Enum):
    """Conflict resolution strategies."""
    SKIP = "skip"
    RENAME = "rename"
    OVERWRITE = "overwrite"


class InstallationScope(Enum):
    """Installation scope."""
    GLOBAL = "global"
    PROJECT = "project"


@dataclass
class Instruction:
    """
    Represents a single instruction file.
    
    Attributes:
        name: Unique identifier (e.g., 'python-best-practices')
        description: Human-readable description
        content: The actual instruction text
        file_path: Relative path in repository (e.g., 'instructions/python-best-practices.md')
        tags: Categorization tags (e.g., ['python', 'backend'])
        checksum: SHA-256 hash for integrity validation
        ai_tools: List of compatible AI tools (empty = all compatible)
    """
    name: str
    description: str
    content: str
    file_path: str
    tags: list[str] = field(default_factory=list)
    checksum: Optional[str] = None
    ai_tools: list[AIToolType] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate instruction data."""
        if not self.name:
            raise ValueError("Instruction name cannot be empty")
        if not self.description:
            raise ValueError("Instruction description cannot be empty")
        if not self.content:
            raise ValueError("Instruction content cannot be empty")
        if not self.file_path:
            raise ValueError("Instruction file_path cannot be empty")


@dataclass
class InstructionBundle:
    """
    Represents a bundle of related instructions.
    
    Attributes:
        name: Bundle identifier (e.g., 'python-backend')
        description: What this bundle provides
        instructions: List of instruction names in this bundle
        tags: Bundle-level tags
    """
    name: str
    description: str
    instructions: list[str]
    tags: list[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate bundle data."""
        if not self.name:
            raise ValueError("Bundle name cannot be empty")
        if not self.description:
            raise ValueError("Bundle description cannot be empty")
        if not self.instructions:
            raise ValueError("Bundle must contain at least one instruction")


@dataclass
class Repository:
    """
    Represents an instruction repository.

    Attributes:
        url: Git repository URL (empty string if not yet set)
        instructions: Available instructions
        bundles: Available bundles
        metadata: Additional repository metadata
    """
    url: str = ''
    instructions: list[Instruction] = field(default_factory=list)
    bundles: list[InstructionBundle] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class InstallationRecord:
    """
    Tracks an installed instruction.

    Attributes:
        instruction_name: Name of installed instruction
        ai_tool: Which AI tool it's installed to
        source_repo: Repository URL it came from
        installed_path: Absolute path where file was installed
        installed_at: Installation timestamp
        checksum: File checksum at installation time
        bundle_name: If installed as part of bundle
        scope: Installation scope (global or project)
        project_root: Project root path if scope is PROJECT
    """
    instruction_name: str
    ai_tool: AIToolType
    source_repo: str
    installed_path: str
    installed_at: datetime
    checksum: Optional[str] = None
    bundle_name: Optional[str] = None
    scope: InstallationScope = InstallationScope.GLOBAL
    project_root: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate installation record."""
        if not self.instruction_name:
            raise ValueError("Instruction name cannot be empty")
        if not self.source_repo:
            raise ValueError("Source repository cannot be empty")
        if not self.installed_path:
            raise ValueError("Installed path cannot be empty")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'instruction_name': self.instruction_name,
            'ai_tool': self.ai_tool.value,
            'source_repo': self.source_repo,
            'installed_path': self.installed_path,
            'installed_at': self.installed_at.isoformat(),
            'checksum': self.checksum,
            'bundle_name': self.bundle_name,
            'scope': self.scope.value,
            'project_root': self.project_root,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InstallationRecord':
        """Create from dictionary (JSON deserialization)."""
        # Handle backwards compatibility - old records won't have scope
        scope_value = data.get('scope', 'global')
        scope = InstallationScope(scope_value) if isinstance(scope_value, str) else scope_value

        return cls(
            instruction_name=data['instruction_name'],
            ai_tool=AIToolType(data['ai_tool']),
            source_repo=data['source_repo'],
            installed_path=data['installed_path'],
            installed_at=datetime.fromisoformat(data['installed_at']),
            checksum=data.get('checksum'),
            bundle_name=data.get('bundle_name'),
            scope=scope,
            project_root=data.get('project_root'),
        )


@dataclass
class ConflictInfo:
    """
    Information about a file conflict.
    
    Attributes:
        instruction_name: Name of conflicting instruction
        existing_path: Path to existing file
        resolution: How the conflict was resolved
        new_path: New path if renamed
    """
    instruction_name: str
    existing_path: str
    resolution: ConflictResolution
    new_path: Optional[str] = None
