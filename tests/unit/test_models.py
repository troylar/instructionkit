"""Unit tests for core data models."""

from datetime import datetime

import pytest

from aiconfigkit.core.models import (
    AIToolType,
    ConflictResolution,
    InstallationRecord,
    InstallationScope,
    Instruction,
    InstructionBundle,
    RefType,
    Repository,
)


class TestInstruction:
    """Test Instruction model."""

    def test_create_valid_instruction(self):
        inst = Instruction(
            name="test-instruction",
            description="Test description",
            content="Test content",
            file_path="instructions/test.md",
            tags=["test", "python"],
            checksum="abc123",
        )

        assert inst.name == "test-instruction"
        assert inst.description == "Test description"
        assert len(inst.tags) == 2

    def test_instruction_requires_name(self):
        with pytest.raises(ValueError, match="name cannot be empty"):
            Instruction(
                name="",
                description="Test",
                content="Content",
                file_path="test.md",
            )

    def test_instruction_requires_content(self):
        with pytest.raises(ValueError, match="content cannot be empty"):
            Instruction(
                name="test",
                description="Test",
                content="",
                file_path="test.md",
            )

    def test_instruction_requires_description(self):
        with pytest.raises(ValueError, match="description cannot be empty"):
            Instruction(
                name="test",
                description="",
                content="Content",
                file_path="test.md",
            )

    def test_instruction_requires_file_path(self):
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            Instruction(
                name="test",
                description="Test",
                content="Content",
                file_path="",
            )


class TestInstructionBundle:
    """Test InstructionBundle model."""

    def test_create_valid_bundle(self):
        bundle = InstructionBundle(
            name="python-backend",
            description="Backend instructions",
            instructions=["inst1", "inst2"],
            tags=["python", "backend"],
        )

        assert bundle.name == "python-backend"
        assert len(bundle.instructions) == 2

    def test_bundle_requires_name(self):
        with pytest.raises(ValueError, match="name cannot be empty"):
            InstructionBundle(
                name="",
                description="Test",
                instructions=["inst1"],
            )

    def test_bundle_requires_description(self):
        with pytest.raises(ValueError, match="description cannot be empty"):
            InstructionBundle(
                name="test",
                description="",
                instructions=["inst1"],
            )

    def test_bundle_requires_instructions(self):
        with pytest.raises(ValueError, match="must contain at least one instruction"):
            InstructionBundle(
                name="test",
                description="Test",
                instructions=[],
            )


class TestRepository:
    """Test Repository model."""

    def test_create_valid_repository(self):
        repo = Repository(
            url="https://github.com/test/repo",
            instructions=[],
            bundles=[],
        )

        assert repo.url == "https://github.com/test/repo"

    def test_repository_allows_empty_url(self):
        """Repository allows empty URL (can be set later)."""
        repo = Repository(url="")
        assert repo.url == ""
        assert len(repo.instructions) == 0


class TestInstallationRecord:
    """Test InstallationRecord model."""

    def test_create_valid_record(self):
        record = InstallationRecord(
            instruction_name="test",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/file",
            installed_at=datetime.now(),
            checksum="abc123",
        )

        assert record.instruction_name == "test"
        assert record.ai_tool == AIToolType.CURSOR

    def test_installation_record_requires_instruction_name(self):
        with pytest.raises(ValueError, match="Instruction name cannot be empty"):
            InstallationRecord(
                instruction_name="",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",
                installed_path="/path/to/file",
                installed_at=datetime.now(),
            )

    def test_installation_record_requires_source_repo(self):
        with pytest.raises(ValueError, match="Source repository cannot be empty"):
            InstallationRecord(
                instruction_name="test",
                ai_tool=AIToolType.CURSOR,
                source_repo="",
                installed_path="/path/to/file",
                installed_at=datetime.now(),
            )

    def test_installation_record_requires_installed_path(self):
        with pytest.raises(ValueError, match="Installed path cannot be empty"):
            InstallationRecord(
                instruction_name="test",
                ai_tool=AIToolType.CURSOR,
                source_repo="https://github.com/test/repo",
                installed_path="",
                installed_at=datetime.now(),
            )

    def test_to_dict_conversion(self):
        now = datetime.now()
        record = InstallationRecord(
            instruction_name="test",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/test/repo",
            installed_path="/path/to/file",
            installed_at=now,
        )

        data = record.to_dict()

        assert data["instruction_name"] == "test"
        assert data["ai_tool"] == "cursor"
        assert data["installed_at"] == now.isoformat()

    def test_from_dict_conversion(self):
        now = datetime.now()
        data = {
            "instruction_name": "test",
            "ai_tool": "cursor",
            "source_repo": "https://github.com/test/repo",
            "installed_path": "/path/to/file",
            "installed_at": now.isoformat(),
            "checksum": "abc123",
            "bundle_name": "test-bundle",
        }

        record = InstallationRecord.from_dict(data)

        assert record.instruction_name == "test"
        assert record.ai_tool == AIToolType.CURSOR
        assert record.checksum == "abc123"


class TestEnums:
    """Test enum types."""

    def test_ai_tool_type_values(self):
        assert AIToolType.CURSOR.value == "cursor"
        assert AIToolType.COPILOT.value == "copilot"
        assert AIToolType.WINSURF.value == "winsurf"
        assert AIToolType.CLAUDE.value == "claude"

    def test_conflict_resolution_values(self):
        assert ConflictResolution.SKIP.value == "skip"
        assert ConflictResolution.RENAME.value == "rename"
        assert ConflictResolution.OVERWRITE.value == "overwrite"


class TestRefType:
    """Test RefType enum for Git version control."""

    def test_ref_type_values(self):
        """Test RefType enum has correct values."""
        assert RefType.TAG.value == "tag"
        assert RefType.BRANCH.value == "branch"
        assert RefType.COMMIT.value == "commit"

    def test_ref_type_creation(self):
        """Test creating RefType from string values."""
        assert RefType("tag") == RefType.TAG
        assert RefType("branch") == RefType.BRANCH
        assert RefType("commit") == RefType.COMMIT

    def test_ref_type_invalid_value(self):
        """Test RefType rejects invalid values."""
        with pytest.raises(ValueError):
            RefType("invalid")


class TestInstallationRecordWithVersioning:
    """Test InstallationRecord with version control fields."""

    def test_installation_record_with_tag_ref(self):
        """Test InstallationRecord with tag reference."""
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime(2025, 10, 26, 12, 0, 0),
            scope=InstallationScope.PROJECT,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )

        assert record.source_ref == "v1.0.0"
        assert record.source_ref_type == RefType.TAG

    def test_installation_record_with_branch_ref(self):
        """Test InstallationRecord with branch reference."""
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CLAUDE,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            source_ref="main",
            source_ref_type=RefType.BRANCH,
        )

        assert record.source_ref == "main"
        assert record.source_ref_type == RefType.BRANCH

    def test_installation_record_with_commit_ref(self):
        """Test InstallationRecord with commit reference."""
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.WINSURF,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
            source_ref="abc123def456",
            source_ref_type=RefType.COMMIT,
        )

        assert record.source_ref == "abc123def456"
        assert record.source_ref_type == RefType.COMMIT

    def test_installation_record_without_ref(self):
        """Test InstallationRecord without version ref (legacy support)."""
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.COPILOT,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime.now(),
            scope=InstallationScope.PROJECT,
        )

        assert record.source_ref is None
        assert record.source_ref_type is None

    def test_installation_record_to_dict_with_ref(self):
        """Test serialization of InstallationRecord with ref fields."""
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime(2025, 10, 26, 12, 0, 0),
            scope=InstallationScope.PROJECT,
            source_ref="v1.0.0",
            source_ref_type=RefType.TAG,
        )

        data = record.to_dict()

        assert data["source_ref"] == "v1.0.0"
        assert data["source_ref_type"] == "tag"
        assert data["instruction_name"] == "test-instruction"
        assert data["ai_tool"] == "cursor"

    def test_installation_record_to_dict_without_ref(self):
        """Test serialization without ref fields."""
        record = InstallationRecord(
            instruction_name="test-instruction",
            ai_tool=AIToolType.CURSOR,
            source_repo="https://github.com/user/repo",
            installed_path="/path/to/file.md",
            installed_at=datetime(2025, 10, 26, 12, 0, 0),
            scope=InstallationScope.PROJECT,
        )

        data = record.to_dict()

        assert data["source_ref"] is None
        assert data["source_ref_type"] is None

    def test_installation_record_from_dict_with_ref(self):
        """Test deserialization of InstallationRecord with ref fields."""
        data = {
            "instruction_name": "test-instruction",
            "ai_tool": "cursor",
            "source_repo": "https://github.com/user/repo",
            "installed_path": "/path/to/file.md",
            "installed_at": "2025-10-26T12:00:00",
            "scope": "project",
            "source_ref": "v1.0.0",
            "source_ref_type": "tag",
        }

        record = InstallationRecord.from_dict(data)

        assert record.source_ref == "v1.0.0"
        assert record.source_ref_type == RefType.TAG
        assert record.instruction_name == "test-instruction"

    def test_installation_record_from_dict_without_ref(self):
        """Test deserialization without ref fields (backwards compatibility)."""
        data = {
            "instruction_name": "test-instruction",
            "ai_tool": "cursor",
            "source_repo": "https://github.com/user/repo",
            "installed_path": "/path/to/file.md",
            "installed_at": "2025-10-26T12:00:00",
            "scope": "project",
        }

        record = InstallationRecord.from_dict(data)

        assert record.source_ref is None
        assert record.source_ref_type is None

    def test_installation_record_from_dict_branch(self):
        """Test deserialization with branch ref."""
        data = {
            "instruction_name": "test-instruction",
            "ai_tool": "claude",
            "source_repo": "https://github.com/user/repo",
            "installed_path": "/path/to/file.md",
            "installed_at": "2025-10-26T12:00:00",
            "scope": "project",
            "source_ref": "main",
            "source_ref_type": "branch",
        }

        record = InstallationRecord.from_dict(data)

        assert record.source_ref == "main"
        assert record.source_ref_type == RefType.BRANCH

    def test_installation_record_from_dict_commit(self):
        """Test deserialization with commit ref."""
        data = {
            "instruction_name": "test-instruction",
            "ai_tool": "winsurf",
            "source_repo": "https://github.com/user/repo",
            "installed_path": "/path/to/file.md",
            "installed_at": "2025-10-26T12:00:00",
            "scope": "project",
            "source_ref": "abc123",
            "source_ref_type": "commit",
        }

        record = InstallationRecord.from_dict(data)

        assert record.source_ref == "abc123"
        assert record.source_ref_type == RefType.COMMIT


class TestLibraryInstruction:
    """Test LibraryInstruction model."""

    def test_create_valid_library_instruction(self):
        from aiconfigkit.core.models import LibraryInstruction

        inst = LibraryInstruction(
            id="test-repo/test-instruction",
            name="test-instruction",
            description="Test description",
            repo_namespace="test-repo",
            repo_url="https://github.com/test/repo",
            repo_name="test-repo",
            author="Test Author",
            version="1.0.0",
            file_path="instructions/test.md",
        )

        assert inst.id == "test-repo/test-instruction"
        assert inst.name == "test-instruction"
        assert inst.repo_namespace == "test-repo"

    def test_library_instruction_requires_id(self):
        from aiconfigkit.core.models import LibraryInstruction

        with pytest.raises(ValueError, match="id cannot be empty"):
            LibraryInstruction(
                id="",
                name="test",
                description="Test",
                repo_namespace="test-repo",
                repo_url="https://github.com/test/repo",
                repo_name="test-repo",
                author="Test",
                version="1.0.0",
                file_path="test.md",
            )

    def test_library_instruction_requires_name(self):
        from aiconfigkit.core.models import LibraryInstruction

        with pytest.raises(ValueError, match="name cannot be empty"):
            LibraryInstruction(
                id="test-repo/test",
                name="",
                description="Test",
                repo_namespace="test-repo",
                repo_url="https://github.com/test/repo",
                repo_name="test-repo",
                author="Test",
                version="1.0.0",
                file_path="test.md",
            )

    def test_library_instruction_requires_repo_namespace(self):
        from aiconfigkit.core.models import LibraryInstruction

        with pytest.raises(ValueError, match="Repository namespace cannot be empty"):
            LibraryInstruction(
                id="test-repo/test",
                name="test",
                description="Test",
                repo_namespace="",
                repo_url="https://github.com/test/repo",
                repo_name="test-repo",
                author="Test",
                version="1.0.0",
                file_path="test.md",
            )


class TestLibraryRepository:
    """Test LibraryRepository model."""

    def test_create_valid_library_repository(self):
        from aiconfigkit.core.models import LibraryRepository

        repo = LibraryRepository(
            namespace="test-org",
            name="test-repo",
            description="Test repository",
            url="https://github.com/test-org/test-repo",
            author="Test Author",
            version="1.0.0",
            downloaded_at=datetime.now(),
        )

        assert repo.namespace == "test-org"
        assert repo.name == "test-repo"

    def test_library_repository_requires_namespace(self):
        from aiconfigkit.core.models import LibraryRepository

        with pytest.raises(ValueError, match="Repository namespace cannot be empty"):
            LibraryRepository(
                namespace="",
                name="test-repo",
                description="Test",
                url="https://github.com/test/repo",
                author="Test",
                version="1.0.0",
                downloaded_at=datetime.now(),
            )

    def test_library_repository_requires_name(self):
        from aiconfigkit.core.models import LibraryRepository

        with pytest.raises(ValueError, match="Repository name cannot be empty"):
            LibraryRepository(
                namespace="test-org",
                name="",
                description="Test",
                url="https://github.com/test/repo",
                author="Test",
                version="1.0.0",
                downloaded_at=datetime.now(),
            )


class TestTemplateFile:
    """Test TemplateFile model."""

    def test_create_valid_template_file(self):
        from aiconfigkit.core.models import TemplateFile

        template = TemplateFile(path="templates/python-style.md", ide="cursor")

        assert template.path == "templates/python-style.md"
        assert template.ide == "cursor"

    def test_template_file_requires_path(self):
        from aiconfigkit.core.models import TemplateFile

        with pytest.raises(ValueError, match="Template file path cannot be empty"):
            TemplateFile(path="", ide="cursor")

    def test_template_file_validates_ide(self):
        from aiconfigkit.core.models import TemplateFile

        with pytest.raises(ValueError, match="Invalid IDE type"):
            TemplateFile(path="test.md", ide="invalid-ide")


class TestTemplateDefinition:
    """Test TemplateDefinition model."""

    def test_template_definition_requires_name(self):
        from aiconfigkit.core.models import TemplateDefinition, TemplateFile

        with pytest.raises(ValueError, match="Template name cannot be empty"):
            TemplateDefinition(
                name="",
                description="Test template",
                files=[TemplateFile(path="test.md")],
            )

    def test_template_definition_requires_description(self):
        from aiconfigkit.core.models import TemplateDefinition, TemplateFile

        with pytest.raises(ValueError, match="Template description cannot be empty"):
            TemplateDefinition(
                name="test-template",
                description="",
                files=[TemplateFile(path="test.md")],
            )

    def test_template_definition_requires_files(self):
        from aiconfigkit.core.models import TemplateDefinition

        with pytest.raises(ValueError, match="Template must have at least one file"):
            TemplateDefinition(
                name="test-template",
                description="Test",
                files=[],
            )


class TestTemplateBundle:
    """Test TemplateBundle model."""

    def test_template_bundle_requires_name(self):
        from aiconfigkit.core.models import TemplateBundle

        with pytest.raises(ValueError, match="Bundle name cannot be empty"):
            TemplateBundle(
                name="",
                description="Test bundle",
                template_refs=["template1", "template2"],
            )

    def test_template_bundle_requires_description(self):
        from aiconfigkit.core.models import TemplateBundle

        with pytest.raises(ValueError, match="Bundle description cannot be empty"):
            TemplateBundle(
                name="test-bundle",
                description="",
                template_refs=["template1", "template2"],
            )

    def test_template_bundle_requires_multiple_templates(self):
        from aiconfigkit.core.models import TemplateBundle

        with pytest.raises(ValueError, match="Bundle must contain at least 2 templates"):
            TemplateBundle(
                name="test-bundle",
                description="Test",
                template_refs=["template1"],
            )


class TestTemplateManifest:
    """Test TemplateManifest model."""

    def test_template_manifest_requires_name(self):
        from aiconfigkit.core.models import TemplateDefinition, TemplateFile, TemplateManifest

        with pytest.raises(ValueError, match="Manifest name cannot be empty"):
            TemplateManifest(
                name="",
                description="Test manifest",
                version="1.0.0",
                templates=[
                    TemplateDefinition(
                        name="test",
                        description="Test",
                        files=[TemplateFile(path="test.md")],
                    )
                ],
            )

    def test_template_manifest_requires_description(self):
        from aiconfigkit.core.models import TemplateDefinition, TemplateFile, TemplateManifest

        with pytest.raises(ValueError, match="Manifest description cannot be empty"):
            TemplateManifest(
                name="test-manifest",
                description="",
                version="1.0.0",
                templates=[
                    TemplateDefinition(
                        name="test",
                        description="Test",
                        files=[TemplateFile(path="test.md")],
                    )
                ],
            )

    def test_template_manifest_requires_version(self):
        from aiconfigkit.core.models import TemplateDefinition, TemplateFile, TemplateManifest

        with pytest.raises(ValueError, match="Manifest version cannot be empty"):
            TemplateManifest(
                name="test-manifest",
                description="Test",
                version="",
                templates=[
                    TemplateDefinition(
                        name="test",
                        description="Test",
                        files=[TemplateFile(path="test.md")],
                    )
                ],
            )

    def test_template_manifest_requires_templates(self):
        from aiconfigkit.core.models import TemplateManifest

        with pytest.raises(ValueError, match="Manifest must contain at least one template"):
            TemplateManifest(
                name="test-manifest",
                description="Test",
                version="1.0.0",
                templates=[],
            )


class TestTemplateInstallationRecord:
    """Test TemplateInstallationRecord model."""

    def test_template_installation_record_requires_id(self):
        from aiconfigkit.core.models import TemplateInstallationRecord

        with pytest.raises(ValueError, match="Installation ID cannot be empty"):
            TemplateInstallationRecord(
                id="",
                template_name="test-template",
                source_repo="https://github.com/test/repo",
                source_version="1.0.0",
                namespace="test/repo",
                installed_path="/path/to/file",
                scope=InstallationScope.PROJECT,
                installed_at=datetime.now(),
                checksum="a" * 64,
                ide_type=AIToolType.CURSOR,
            )

    def test_template_installation_record_requires_template_name(self):
        from aiconfigkit.core.models import TemplateInstallationRecord

        with pytest.raises(ValueError, match="Template name cannot be empty"):
            TemplateInstallationRecord(
                id="test-id",
                template_name="",
                source_repo="https://github.com/test/repo",
                source_version="1.0.0",
                namespace="test/repo",
                installed_path="/path/to/file",
                scope=InstallationScope.PROJECT,
                installed_at=datetime.now(),
                checksum="a" * 64,
                ide_type=AIToolType.CURSOR,
            )

    def test_template_installation_record_requires_source_repo(self):
        from aiconfigkit.core.models import TemplateInstallationRecord

        with pytest.raises(ValueError, match="Source repository cannot be empty"):
            TemplateInstallationRecord(
                id="test-id",
                template_name="test-template",
                source_repo="",
                source_version="1.0.0",
                namespace="test/repo",
                installed_path="/path/to/file",
                scope=InstallationScope.PROJECT,
                installed_at=datetime.now(),
                checksum="a" * 64,
                ide_type=AIToolType.CURSOR,
            )

    def test_template_installation_record_requires_namespace(self):
        from aiconfigkit.core.models import TemplateInstallationRecord

        with pytest.raises(ValueError, match="Namespace cannot be empty"):
            TemplateInstallationRecord(
                id="test-id",
                template_name="test-template",
                source_repo="https://github.com/test/repo",
                source_version="1.0.0",
                namespace="",
                installed_path="/path/to/file",
                scope=InstallationScope.PROJECT,
                installed_at=datetime.now(),
                checksum="a" * 64,
                ide_type=AIToolType.CURSOR,
            )

    def test_template_installation_record_requires_installed_path(self):
        from aiconfigkit.core.models import TemplateInstallationRecord

        with pytest.raises(ValueError, match="Installed path cannot be empty"):
            TemplateInstallationRecord(
                id="test-id",
                template_name="test-template",
                source_repo="https://github.com/test/repo",
                source_version="1.0.0",
                namespace="test/repo",
                installed_path="",
                scope=InstallationScope.PROJECT,
                installed_at=datetime.now(),
                checksum="a" * 64,
                ide_type=AIToolType.CURSOR,
            )

    def test_template_installation_record_validates_checksum_length(self):
        from aiconfigkit.core.models import TemplateInstallationRecord

        with pytest.raises(ValueError, match="Checksum must be a valid SHA-256 hash"):
            TemplateInstallationRecord(
                id="test-id",
                template_name="test-template",
                source_repo="https://github.com/test/repo",
                source_version="1.0.0",
                namespace="test/repo",
                installed_path="/path/to/file",
                scope=InstallationScope.PROJECT,
                installed_at=datetime.now(),
                checksum="invalid-short-checksum",
                ide_type=AIToolType.CURSOR,
            )


class TestAIAnalysis:
    """Test AIAnalysis model."""

    def test_ai_analysis_validates_confidence_range_too_low(self):
        from aiconfigkit.core.models import AIAnalysis

        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            AIAnalysis(
                confidence=-0.1,
                explanation="Test explanation",
            )

    def test_ai_analysis_validates_confidence_range_too_high(self):
        from aiconfigkit.core.models import AIAnalysis

        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            AIAnalysis(
                confidence=1.5,
                explanation="Test explanation",
            )

    def test_ai_analysis_requires_explanation(self):
        from aiconfigkit.core.models import AIAnalysis

        with pytest.raises(ValueError, match="Explanation cannot be empty"):
            AIAnalysis(
                confidence=0.8,
                explanation="",
            )


class TestValidationIssue:
    """Test ValidationIssue model."""

    def test_validation_issue_requires_title(self):
        from aiconfigkit.core.models import IssueSeverity, IssueType, ValidationIssue

        with pytest.raises(ValueError, match="Issue title cannot be empty"):
            ValidationIssue(
                issue_type=IssueType.CLARITY_ISSUE,
                severity=IssueSeverity.ERROR,
                title="",
                description="Test description",
                affected_items=["item1"],
                recommendation="Fix this",
                auto_fixable=False,
            )

    def test_validation_issue_requires_description(self):
        from aiconfigkit.core.models import IssueSeverity, IssueType, ValidationIssue

        with pytest.raises(ValueError, match="Issue description cannot be empty"):
            ValidationIssue(
                issue_type=IssueType.CLARITY_ISSUE,
                severity=IssueSeverity.ERROR,
                title="Test Issue",
                description="",
                affected_items=["item1"],
                recommendation="Fix this",
                auto_fixable=False,
            )

    def test_validation_issue_requires_affected_items(self):
        from aiconfigkit.core.models import IssueSeverity, IssueType, ValidationIssue

        with pytest.raises(ValueError, match="Issue must affect at least one item"):
            ValidationIssue(
                issue_type=IssueType.CLARITY_ISSUE,
                severity=IssueSeverity.ERROR,
                title="Test Issue",
                description="Test description",
                affected_items=[],
                recommendation="Fix this",
                auto_fixable=False,
            )

    def test_validation_issue_requires_recommendation(self):
        from aiconfigkit.core.models import IssueSeverity, IssueType, ValidationIssue

        with pytest.raises(ValueError, match="Issue recommendation cannot be empty"):
            ValidationIssue(
                issue_type=IssueType.CLARITY_ISSUE,
                severity=IssueSeverity.ERROR,
                title="Test Issue",
                description="Test description",
                affected_items=["item1"],
                recommendation="",
                auto_fixable=False,
            )


class TestMCPServer:
    """Test MCPServer model."""

    def test_mcp_server_validates_name_pattern(self):
        from aiconfigkit.core.models import MCPServer

        with pytest.raises(ValueError, match="Invalid server name"):
            MCPServer(
                name="invalid name with spaces",
                command="python",
                args=["-m", "server"],
                env={},
                namespace="test/repo",
            )

    def test_mcp_server_requires_command(self):
        from aiconfigkit.core.models import MCPServer

        with pytest.raises(ValueError, match="Server command cannot be empty"):
            MCPServer(
                name="test-server",
                command="",
                args=[],
                env={},
                namespace="test/repo",
            )

    def test_mcp_server_validates_env_var_names(self):
        from aiconfigkit.core.models import MCPServer

        with pytest.raises(ValueError, match="Invalid environment variable name"):
            MCPServer(
                name="test-server",
                command="python",
                args=[],
                env={"invalid-var-name": "value"},
                namespace="test/repo",
            )


class TestMCPSet:
    """Test MCPSet model."""

    def test_mcp_set_validates_name_pattern(self):
        from aiconfigkit.core.models import MCPSet

        with pytest.raises(ValueError, match="Invalid set name"):
            MCPSet(
                name="invalid name with spaces",
                description="Test set",
                server_names=["server1"],
                namespace="test/repo",
            )

    def test_mcp_set_requires_at_least_one_server(self):
        from aiconfigkit.core.models import MCPSet

        with pytest.raises(ValueError, match="Set must contain at least one server"):
            MCPSet(
                name="test-set",
                description="Test set",
                server_names=[],
                namespace="test/repo",
            )


class TestMCPTemplate:
    """Test MCPTemplate model."""

    def test_mcp_template_requires_namespace(self):
        from datetime import datetime

        from aiconfigkit.core.models import MCPTemplate

        with pytest.raises(ValueError, match="Template namespace cannot be empty"):
            MCPTemplate(
                namespace="",
                source_url="https://github.com/user/repo",
                source_path=None,
                version="1.0.0",
                description="Test template",
                installed_at=datetime.now(),
            )

    def test_mcp_template_cannot_have_both_sources(self):
        from datetime import datetime

        from aiconfigkit.core.models import MCPTemplate

        with pytest.raises(ValueError, match="Template cannot have both source_url and source_path"):
            MCPTemplate(
                namespace="test/repo",
                source_url="https://github.com/user/repo",
                source_path="/local/path",
                version="1.0.0",
                description="Test template",
                installed_at=datetime.now(),
            )

    def test_mcp_template_requires_at_least_one_source(self):
        from datetime import datetime

        from aiconfigkit.core.models import MCPTemplate

        with pytest.raises(ValueError, match="Template must have either source_url or source_path"):
            MCPTemplate(
                namespace="test/repo",
                source_url=None,
                source_path=None,
                version="1.0.0",
                description="Test template",
                installed_at=datetime.now(),
            )


class TestEnvironmentConfig:
    """Test EnvironmentConfig model."""

    def test_environment_config_validates_var_name_lowercase(self):
        from aiconfigkit.core.models import EnvironmentConfig

        config = EnvironmentConfig()
        with pytest.raises(ValueError, match="Invalid environment variable name"):
            config.set("lowercase", "value")

    def test_environment_config_validates_var_name_with_hyphen(self):
        from aiconfigkit.core.models import EnvironmentConfig

        config = EnvironmentConfig()
        with pytest.raises(ValueError, match="Invalid environment variable name"):
            config.set("INVALID-NAME", "value")

    def test_environment_config_validates_var_name_starting_with_number(self):
        from aiconfigkit.core.models import EnvironmentConfig

        config = EnvironmentConfig()
        with pytest.raises(ValueError, match="Invalid environment variable name"):
            config.set("1INVALID", "value")


class TestLibraryInstructionSerialization:
    """Test LibraryInstruction serialization/deserialization."""

    def test_from_dict_with_downloaded_at(self):
        """Test from_dict with downloaded_at field (line 312)."""
        from datetime import datetime

        from aiconfigkit.core.models import LibraryInstruction

        data = {
            "id": "test/instruction",
            "name": "test",
            "description": "Test instruction",
            "repo_namespace": "test",
            "repo_url": "https://github.com/test/repo",
            "repo_name": "Test Repo",
            "author": "Author",
            "version": "1.0.0",
            "file_path": "/path/to/file.md",
            "downloaded_at": "2025-01-01T12:00:00",
            "tags": [],
        }

        inst = LibraryInstruction.from_dict(data)
        assert inst.downloaded_at == datetime.fromisoformat("2025-01-01T12:00:00")


class TestMCPTemplateMethods:
    """Test MCPTemplate helper methods."""

    def test_get_set_by_name_found(self):
        """Test get_set_by_name when set exists (lines 829-831)."""
        from datetime import datetime

        from aiconfigkit.core.models import MCPSet, MCPTemplate

        mcp_set = MCPSet(name="test-set", description="Test", server_names=["server1"], namespace="test")
        template = MCPTemplate(
            namespace="test",
            source_url="https://test.com",
            source_path=None,
            version="1.0.0",
            description="Test",
            installed_at=datetime.now(),
            servers=[],
            sets=[mcp_set],
        )

        found = template.get_set_by_name("test-set")
        assert found == mcp_set

    def test_get_set_by_name_not_found(self):
        """Test get_set_by_name when set doesn't exist (line 832)."""
        from datetime import datetime

        from aiconfigkit.core.models import MCPTemplate

        template = MCPTemplate(
            namespace="test",
            source_url="https://test.com",
            source_path=None,
            version="1.0.0",
            description="Test",
            installed_at=datetime.now(),
            servers=[],
            sets=[],
        )

        found = template.get_set_by_name("nonexistent")
        assert found is None


class TestEnvironmentConfigMethods:
    """Test EnvironmentConfig methods."""

    def test_to_dict(self):
        """Test EnvironmentConfig.to_dict (line 901)."""
        from aiconfigkit.core.models import EnvironmentConfig

        config = EnvironmentConfig()
        config.variables = {"API_KEY": "secret", "USERNAME": "user"}

        result = config.to_dict()
        assert result == {"API_KEY": "secret", "USERNAME": "user"}
        # Verify it's a copy
        result["NEW_VAR"] = "value"
        assert "NEW_VAR" not in config.variables


class TestActiveSetStateSerialization:
    """Test ActiveSetState serialization."""

    def test_to_dict(self):
        """Test ActiveSetState.to_dict (line 954)."""
        from datetime import datetime

        from aiconfigkit.core.models import ActiveSetState

        activated_at = datetime.fromisoformat("2025-01-01T12:00:00")
        state = ActiveSetState(
            namespace="test",
            set_name="my-set",
            activated_at=activated_at,
            active_servers=["server1", "server2"],
        )

        result = state.to_dict()
        assert result["activated_at"] == "2025-01-01T12:00:00"

    def test_from_dict_with_activated_at(self):
        """Test ActiveSetState.from_dict with activated_at (lines 964-967)."""
        from datetime import datetime

        from aiconfigkit.core.models import ActiveSetState

        data = {
            "namespace": "test",
            "set_name": "my-set",
            "activated_at": "2025-01-01T12:00:00",
            "active_servers": ["server1"],
        }

        state = ActiveSetState.from_dict(data)
        assert state.activated_at == datetime.fromisoformat("2025-01-01T12:00:00")


class TestMCPServerComponentSerialization:
    """Test MCPServerComponent serialization."""

    def test_from_dict_with_credentials(self):
        """Test MCPServerComponent.from_dict with credentials (line 1140)."""
        from aiconfigkit.core.models import MCPServerComponent

        data = {
            "name": "test-server",
            "file": "server.json",
            "description": "Test server",
            "credentials": [
                {"name": "API_KEY", "description": "API key", "required": True},
                {"name": "USERNAME", "description": "Username", "required": False, "default": "user"},
            ],
        }

        component = MCPServerComponent.from_dict(data)
        assert len(component.credentials) == 2
        assert component.credentials[0].name == "API_KEY"
        assert component.credentials[1].default == "user"


class TestHookComponentSerialization:
    """Test HookComponent serialization."""

    def test_to_dict(self):
        """Test HookComponent.to_dict (line 1170)."""
        from aiconfigkit.core.models import HookComponent

        hook = HookComponent(name="test-hook", file="hook.sh", description="Test hook", hook_type="pre-commit")

        result = hook.to_dict()
        assert result["name"] == "test-hook"
        assert result["hook_type"] == "pre-commit"

    def test_from_dict(self):
        """Test HookComponent.from_dict (line 1181)."""
        from aiconfigkit.core.models import HookComponent

        data = {
            "name": "test-hook",
            "file": "hook.sh",
            "description": "Test hook",
            "hook_type": "pre-commit",
            "ide_support": ["claude_code"],
        }

        hook = HookComponent.from_dict(data)
        assert hook.name == "test-hook"
        assert hook.hook_type == "pre-commit"


class TestCommandComponentSerialization:
    """Test CommandComponent serialization methods."""

    def test_to_dict(self):
        """Test CommandComponent.to_dict (lines 1211-1217)."""
        from aiconfigkit.core.models import CommandComponent

        component = CommandComponent(
            name="test-command",
            file="command.sh",
            description="Test command",
            command_type="shell",
            ide_support=["claude_code"],
        )

        data = component.to_dict()
        assert data["name"] == "test-command"
        assert data["file"] == "command.sh"
        assert data["command_type"] == "shell"
        assert data["ide_support"] == ["claude_code"]

    def test_from_dict(self):
        """Test CommandComponent.from_dict (lines 1222-1228)."""
        from aiconfigkit.core.models import CommandComponent

        data = {
            "name": "test-command",
            "file": "command.sh",
            "description": "Test command",
            "command_type": "shell",
            "ide_support": ["claude_code"],
        }

        component = CommandComponent.from_dict(data)
        assert component.name == "test-command"
        assert component.command_type == "shell"
        assert component.ide_support == ["claude_code"]


class TestResourceComponentSerialization:
    """Test ResourceComponent serialization methods."""

    def test_to_dict(self):
        """Test ResourceComponent.to_dict (lines 1254-1261)."""
        from aiconfigkit.core.models import ResourceComponent

        component = ResourceComponent(
            name="test-resource",
            file="resource.txt",
            description="Test resource",
            install_path=".testfile",
            checksum="sha256:abc123",
            size=1024,
        )

        data = component.to_dict()
        assert data["name"] == "test-resource"
        assert data["file"] == "resource.txt"
        assert data["install_path"] == ".testfile"
        assert data["checksum"] == "sha256:abc123"
        assert data["size"] == 1024

    def test_from_dict(self):
        """Test ResourceComponent.from_dict (lines 1266-1273)."""
        from aiconfigkit.core.models import ResourceComponent

        data = {
            "name": "test-resource",
            "file": "resource.txt",
            "description": "Test resource",
            "install_path": ".testfile",
            "checksum": "sha256:abc123",
            "size": 1024,
        }

        component = ResourceComponent.from_dict(data)
        assert component.name == "test-resource"
        assert component.install_path == ".testfile"
        assert component.checksum == "sha256:abc123"


class TestPackageValidation:
    """Test Package validation errors."""

    def test_empty_version_validation(self):
        """Test Package validation error for empty version (line 1380)."""
        from aiconfigkit.core.models import Package, PackageComponents

        with pytest.raises(ValueError, match="Package version cannot be empty"):
            Package(
                name="test",
                version="",  # Empty version should fail
                description="Test",
                author="Test",
                license="MIT",
                namespace="test/test",
                components=PackageComponents(),
            )

    def test_empty_namespace_validation(self):
        """Test Package validation error for empty namespace (line 1382)."""
        from aiconfigkit.core.models import Package, PackageComponents

        with pytest.raises(ValueError, match="Package namespace cannot be empty"):
            Package(
                name="test",
                version="1.0.0",
                description="Test",
                author="Test",
                license="MIT",
                namespace="",  # Empty namespace should fail
                components=PackageComponents(),
            )


class TestPackageDatetimeDeserialization:
    """Test Package.from_dict with datetime fields."""

    def test_from_dict_with_created_at(self):
        """Test Package.from_dict with created_at (line 1403)."""
        from datetime import datetime

        from aiconfigkit.core.models import Package

        data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Test",
            "license": "MIT",
            "namespace": "test/test",
            "components": {},
            "created_at": "2025-10-24T12:00:00",
        }

        package = Package.from_dict(data)
        assert package.created_at is not None
        assert isinstance(package.created_at, datetime)

    def test_from_dict_with_updated_at(self):
        """Test Package.from_dict with updated_at (line 1406)."""
        from datetime import datetime

        from aiconfigkit.core.models import Package

        data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Test",
            "license": "MIT",
            "namespace": "test/test",
            "components": {},
            "updated_at": "2025-10-24T13:00:00",
        }

        package = Package.from_dict(data)
        assert package.updated_at is not None
        assert isinstance(package.updated_at, datetime)


class TestPackageComponentsMethods:
    """Test PackageComponents helper methods."""

    def test_component_types_with_all_types(self):
        """Test component_types property with all component types (lines 1307-1315)."""
        from aiconfigkit.core.models import (
            CommandComponent,
            HookComponent,
            InstructionComponent,
            MCPServerComponent,
            PackageComponents,
            ResourceComponent,
        )

        components = PackageComponents(
            instructions=[InstructionComponent(name="i", file="i.md", description="I")],
            mcp_servers=[MCPServerComponent(name="m", file="m.json", description="M")],
            hooks=[HookComponent(name="h", file="h.sh", description="H", hook_type="pre-commit")],
            commands=[CommandComponent(name="c", file="c.sh", description="C", command_type="shell")],
            resources=[
                ResourceComponent(
                    name="r", file="r.txt", description="R", install_path="r", checksum="sha256:abc", size=100
                )
            ],
        )

        types = components.component_types
        assert types == ["instructions", "mcp_servers", "hooks", "commands", "resources"]

    def test_component_types_partial(self):
        """Test component_types property with some component types (lines 1311, 1313, 1315)."""
        from aiconfigkit.core.models import CommandComponent, HookComponent, PackageComponents

        components = PackageComponents(
            hooks=[HookComponent(name="h", file="h.sh", description="H", hook_type="pre-commit")],
            commands=[CommandComponent(name="c", file="c.sh", description="C", command_type="shell")],
        )

        types = components.component_types
        assert types == ["hooks", "commands"]
