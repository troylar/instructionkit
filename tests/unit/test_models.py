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
