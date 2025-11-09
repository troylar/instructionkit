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

    PROMPT = "prompt"  # Interactive prompting (default)
    SKIP = "skip"
    RENAME = "rename"
    OVERWRITE = "overwrite"


class InstallationScope(Enum):
    """Installation scope."""

    GLOBAL = "global"
    PROJECT = "project"


class RefType(Enum):
    """Git reference types for version control."""

    TAG = "tag"
    BRANCH = "branch"
    COMMIT = "commit"


class ConflictType(Enum):
    """Types of conflicts during template updates."""

    NONE = "none"  # No conflict, safe to update
    LOCAL_MODIFIED = "local_modified"  # User modified local file
    BOTH_MODIFIED = "both_modified"  # Both local and remote changed


class IssueType(Enum):
    """Types of validation issues."""

    TRACKING_INCONSISTENCY = "tracking_inconsistency"  # File exists but not tracked
    MISSING_FILE = "missing_file"  # Tracked but file missing
    OUTDATED = "outdated"  # Newer version available
    BROKEN_DEPENDENCY = "broken_dependency"  # Required template not installed
    LOCAL_MODIFICATION = "local_modification"  # File changed since install
    SEMANTIC_CONFLICT = "semantic_conflict"  # AI detected conflicting guidance
    CLARITY_ISSUE = "clarity_issue"  # AI detected unclear instructions


class IssueSeverity(Enum):
    """Severity levels for validation issues."""

    ERROR = "error"  # Must fix
    WARNING = "warning"  # Should fix
    INFO = "info"  # Nice to know


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

    url: str = ""
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
        installed_path: Path where file was installed (relative to project root for PROJECT scope)
        installed_at: Installation timestamp
        checksum: File checksum at installation time
        bundle_name: If installed as part of bundle
        scope: Installation scope (global or project)
        source_ref: Git reference (tag, branch, or commit) the instruction came from
        source_ref_type: Type of Git reference (tag, branch, or commit)
    """

    instruction_name: str
    ai_tool: AIToolType
    source_repo: str
    installed_path: str
    installed_at: datetime
    checksum: Optional[str] = None
    bundle_name: Optional[str] = None
    scope: InstallationScope = InstallationScope.GLOBAL
    source_ref: Optional[str] = None
    source_ref_type: Optional[RefType] = None

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
            "instruction_name": self.instruction_name,
            "ai_tool": self.ai_tool.value,
            "source_repo": self.source_repo,
            "installed_path": self.installed_path,
            "installed_at": self.installed_at.isoformat(),
            "checksum": self.checksum,
            "bundle_name": self.bundle_name,
            "scope": self.scope.value,
            "source_ref": self.source_ref,
            "source_ref_type": self.source_ref_type.value if self.source_ref_type else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InstallationRecord":
        """Create from dictionary (JSON deserialization)."""
        # Handle backwards compatibility - old records won't have scope
        scope_value = data.get("scope", "global")
        scope = InstallationScope(scope_value) if isinstance(scope_value, str) else scope_value

        # Handle backwards compatibility - old records won't have ref fields
        source_ref = data.get("source_ref")
        source_ref_type = None
        if data.get("source_ref_type"):
            source_ref_type = RefType(data["source_ref_type"])

        return cls(
            instruction_name=data["instruction_name"],
            ai_tool=AIToolType(data["ai_tool"]),
            source_repo=data["source_repo"],
            installed_path=data["installed_path"],
            installed_at=datetime.fromisoformat(data["installed_at"]),
            checksum=data.get("checksum"),
            bundle_name=data.get("bundle_name"),
            scope=scope,
            source_ref=source_ref,
            source_ref_type=source_ref_type,
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


@dataclass
class LibraryInstruction:
    """
    Represents an instruction in the local library (downloaded but not yet installed).

    Attributes:
        id: Unique identifier (repo_namespace/name)
        name: Instruction name
        description: Human-readable description
        repo_namespace: Repository namespace (e.g., 'company-instructions')
        repo_url: Source repository URL
        repo_name: Repository display name
        author: Author or team name
        version: Instruction version
        file_path: Path to instruction file in library
        tags: Categorization tags
        downloaded_at: When it was downloaded
        checksum: SHA-256 hash for integrity
    """

    id: str
    name: str
    description: str
    repo_namespace: str
    repo_url: str
    repo_name: str
    author: str
    version: str
    file_path: str
    tags: list[str] = field(default_factory=list)
    downloaded_at: Optional[datetime] = None
    checksum: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate library instruction data."""
        if not self.id:
            raise ValueError("Instruction id cannot be empty")
        if not self.name:
            raise ValueError("Instruction name cannot be empty")
        if not self.repo_namespace:
            raise ValueError("Repository namespace cannot be empty")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "repo_namespace": self.repo_namespace,
            "repo_url": self.repo_url,
            "repo_name": self.repo_name,
            "author": self.author,
            "version": self.version,
            "file_path": self.file_path,
            "tags": self.tags,
            "downloaded_at": self.downloaded_at.isoformat() if self.downloaded_at else None,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryInstruction":
        """Create from dictionary (JSON deserialization)."""
        downloaded_at = None
        if data.get("downloaded_at"):
            downloaded_at = datetime.fromisoformat(data["downloaded_at"])

        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            repo_namespace=data["repo_namespace"],
            repo_url=data["repo_url"],
            repo_name=data["repo_name"],
            author=data["author"],
            version=data["version"],
            file_path=data["file_path"],
            tags=data.get("tags", []),
            downloaded_at=downloaded_at,
            checksum=data.get("checksum"),
        )


@dataclass
class LibraryRepository:
    """
    Represents a downloaded repository in the library.

    Attributes:
        namespace: Repository namespace identifier (e.g., 'github.com_company_instructions')
        name: Repository display name
        description: Repository description
        url: Source repository URL
        author: Author or team name
        version: Repository version
        downloaded_at: When it was downloaded
        alias: User-friendly alias for this source (optional)
        instructions: List of instructions in this repository
    """

    namespace: str
    name: str
    description: str
    url: str
    author: str
    version: str
    downloaded_at: datetime
    alias: Optional[str] = None
    instructions: list[LibraryInstruction] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate library repository data."""
        if not self.namespace:
            raise ValueError("Repository namespace cannot be empty")
        if not self.name:
            raise ValueError("Repository name cannot be empty")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "namespace": self.namespace,
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "author": self.author,
            "version": self.version,
            "downloaded_at": self.downloaded_at.isoformat(),
            "alias": self.alias,
            "instructions": [inst.to_dict() for inst in self.instructions],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryRepository":
        """Create from dictionary (JSON deserialization)."""
        instructions = [LibraryInstruction.from_dict(inst) for inst in data.get("instructions", [])]

        return cls(
            namespace=data["namespace"],
            name=data["name"],
            description=data["description"],
            url=data["url"],
            author=data["author"],
            version=data["version"],
            downloaded_at=datetime.fromisoformat(data["downloaded_at"]),
            alias=data.get("alias"),  # Optional field, may not exist in old data
            instructions=instructions,
        )


# Template Sync System Models


@dataclass
class TemplateFile:
    """
    Represents a template file with IDE targeting.

    Attributes:
        path: Relative path from repository root
        ide: Target IDE ("all", "cursor", "claude", "windsurf", "copilot")
    """

    path: str
    ide: str = "all"

    def __post_init__(self) -> None:
        """Validate template file data."""
        if not self.path:
            raise ValueError("Template file path cannot be empty")
        valid_ides = ["all", "cursor", "claude", "windsurf", "copilot"]
        if self.ide not in valid_ides:
            raise ValueError(f"Invalid IDE type: {self.ide}. Must be one of {valid_ides}")


@dataclass
class TemplateDefinition:
    """
    Represents a single template definition from manifest.

    Attributes:
        name: Template identifier
        description: What this template provides
        files: List of template files
        tags: Categorization tags
        dependencies: Other templates required by this one
    """

    name: str
    description: str
    files: list[TemplateFile]
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate template definition."""
        if not self.name:
            raise ValueError("Template name cannot be empty")
        if not self.description:
            raise ValueError("Template description cannot be empty")
        if not self.files:
            raise ValueError("Template must have at least one file")


@dataclass
class TemplateBundle:
    """
    Represents a predefined bundle of templates.

    Attributes:
        name: Bundle identifier
        description: What this bundle provides
        template_refs: Template names in this bundle
        tags: Categorization tags
    """

    name: str
    description: str
    template_refs: list[str]
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate template bundle."""
        if not self.name:
            raise ValueError("Bundle name cannot be empty")
        if not self.description:
            raise ValueError("Bundle description cannot be empty")
        if len(self.template_refs) < 2:
            raise ValueError("Bundle must contain at least 2 templates")


@dataclass
class TemplateManifest:
    """
    Represents a template repository manifest (templatekit.yaml).

    Attributes:
        name: Repository name
        description: Repository description
        version: Semantic version
        author: Author or team name
        templates: Available templates
        bundles: Predefined bundles
    """

    name: str
    description: str
    version: str
    author: Optional[str] = None
    templates: list[TemplateDefinition] = field(default_factory=list)
    bundles: list[TemplateBundle] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate manifest data."""
        if not self.name:
            raise ValueError("Manifest name cannot be empty")
        if not self.description:
            raise ValueError("Manifest description cannot be empty")
        if not self.version:
            raise ValueError("Manifest version cannot be empty")
        if not self.templates:
            raise ValueError("Manifest must contain at least one template")


@dataclass
class TemplateInstallationRecord:
    """
    Tracks an installed template.

    Attributes:
        id: Unique installation ID (UUID)
        template_name: Installed template identifier
        source_repo: Source repository name
        source_version: Repository version at install
        namespace: Repository namespace (derived from repo name)
        installed_path: Absolute path to installed file
        scope: Installation scope (project or global)
        installed_at: Installation timestamp
        checksum: SHA-256 of installed content
        ide_type: Target IDE for this installation
        custom_metadata: User-defined metadata
    """

    id: str
    template_name: str
    source_repo: str
    source_version: str
    namespace: str
    installed_path: str
    scope: InstallationScope
    installed_at: datetime
    checksum: str
    ide_type: AIToolType
    custom_metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate installation record."""
        if not self.id:
            raise ValueError("Installation ID cannot be empty")
        if not self.template_name:
            raise ValueError("Template name cannot be empty")
        if not self.source_repo:
            raise ValueError("Source repository cannot be empty")
        if not self.namespace:
            raise ValueError("Namespace cannot be empty")
        if not self.installed_path:
            raise ValueError("Installed path cannot be empty")
        if len(self.checksum) != 64:  # SHA-256 is always 64 hex characters
            raise ValueError("Checksum must be a valid SHA-256 hash (64 characters)")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "template_name": self.template_name,
            "source_repo": self.source_repo,
            "source_version": self.source_version,
            "namespace": self.namespace,
            "installed_path": self.installed_path,
            "scope": self.scope.value,
            "installed_at": self.installed_at.isoformat(),
            "checksum": self.checksum,
            "ide_type": self.ide_type.value,
            "custom_metadata": self.custom_metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TemplateInstallationRecord":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            id=data["id"],
            template_name=data["template_name"],
            source_repo=data["source_repo"],
            source_version=data["source_version"],
            namespace=data["namespace"],
            installed_path=data["installed_path"],
            scope=InstallationScope(data["scope"]),
            installed_at=datetime.fromisoformat(data["installed_at"]),
            checksum=data["checksum"],
            ide_type=AIToolType(data["ide_type"]),
            custom_metadata=data.get("custom_metadata", {}),
        )


@dataclass
class AIAnalysis:
    """
    AI-provided analysis for validation issues.

    Attributes:
        confidence: AI confidence (0.0-1.0)
        explanation: Why AI flagged this
        suggested_fix: AI-generated fix
        can_merge: For conflicts: is merge possible?
        merge_suggestion: Merged version if applicable
    """

    confidence: float
    explanation: str
    suggested_fix: Optional[str] = None
    can_merge: Optional[bool] = None
    merge_suggestion: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate AI analysis data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if not self.explanation:
            raise ValueError("Explanation cannot be empty")


@dataclass
class ValidationIssue:
    """
    Represents a problem detected during template validation.

    Attributes:
        issue_type: Type of validation issue
        severity: How critical the issue is
        title: Short description of issue
        description: Detailed explanation
        affected_items: Templates/repos affected
        recommendation: How to fix the issue
        auto_fixable: Can system auto-fix this?
        fix_command: Command to fix issue
        ai_analysis: AI-provided insights
    """

    issue_type: IssueType
    severity: IssueSeverity
    title: str
    description: str
    affected_items: list[str]
    recommendation: str
    auto_fixable: bool
    fix_command: Optional[str] = None
    ai_analysis: Optional[AIAnalysis] = None

    def __post_init__(self) -> None:
        """Validate validation issue data."""
        if not self.title:
            raise ValueError("Issue title cannot be empty")
        if not self.description:
            raise ValueError("Issue description cannot be empty")
        if not self.affected_items:
            raise ValueError("Issue must affect at least one item")
        if not self.recommendation:
            raise ValueError("Issue recommendation cannot be empty")
