"""Unit tests for core data models."""

from datetime import datetime

import pytest

from instructionkit.core.models import (
    AIToolType,
    ConflictResolution,
    InstallationRecord,
    Instruction,
    InstructionBundle,
    Repository,
)


class TestInstruction:
    """Test Instruction model."""

    def test_create_valid_instruction(self):
        inst = Instruction(
            name='test-instruction',
            description='Test description',
            content='Test content',
            file_path='instructions/test.md',
            tags=['test', 'python'],
            checksum='abc123',
        )

        assert inst.name == 'test-instruction'
        assert inst.description == 'Test description'
        assert len(inst.tags) == 2

    def test_instruction_requires_name(self):
        with pytest.raises(ValueError, match="name cannot be empty"):
            Instruction(
                name='',
                description='Test',
                content='Content',
                file_path='test.md',
            )

    def test_instruction_requires_content(self):
        with pytest.raises(ValueError, match="content cannot be empty"):
            Instruction(
                name='test',
                description='Test',
                content='',
                file_path='test.md',
            )


class TestInstructionBundle:
    """Test InstructionBundle model."""

    def test_create_valid_bundle(self):
        bundle = InstructionBundle(
            name='python-backend',
            description='Backend instructions',
            instructions=['inst1', 'inst2'],
            tags=['python', 'backend'],
        )

        assert bundle.name == 'python-backend'
        assert len(bundle.instructions) == 2

    def test_bundle_requires_instructions(self):
        with pytest.raises(ValueError, match="must contain at least one instruction"):
            InstructionBundle(
                name='test',
                description='Test',
                instructions=[],
            )


class TestRepository:
    """Test Repository model."""

    def test_create_valid_repository(self):
        repo = Repository(
            url='https://github.com/test/repo',
            instructions=[],
            bundles=[],
        )

        assert repo.url == 'https://github.com/test/repo'

    def test_repository_allows_empty_url(self):
        """Repository allows empty URL (can be set later)."""
        repo = Repository(url='')
        assert repo.url == ''
        assert len(repo.instructions) == 0


class TestInstallationRecord:
    """Test InstallationRecord model."""

    def test_create_valid_record(self):
        record = InstallationRecord(
            instruction_name='test',
            ai_tool=AIToolType.CURSOR,
            source_repo='https://github.com/test/repo',
            installed_path='/path/to/file',
            installed_at=datetime.now(),
            checksum='abc123',
        )

        assert record.instruction_name == 'test'
        assert record.ai_tool == AIToolType.CURSOR

    def test_to_dict_conversion(self):
        now = datetime.now()
        record = InstallationRecord(
            instruction_name='test',
            ai_tool=AIToolType.CURSOR,
            source_repo='https://github.com/test/repo',
            installed_path='/path/to/file',
            installed_at=now,
        )

        data = record.to_dict()

        assert data['instruction_name'] == 'test'
        assert data['ai_tool'] == 'cursor'
        assert data['installed_at'] == now.isoformat()

    def test_from_dict_conversion(self):
        now = datetime.now()
        data = {
            'instruction_name': 'test',
            'ai_tool': 'cursor',
            'source_repo': 'https://github.com/test/repo',
            'installed_path': '/path/to/file',
            'installed_at': now.isoformat(),
            'checksum': 'abc123',
            'bundle_name': 'test-bundle',
        }

        record = InstallationRecord.from_dict(data)

        assert record.instruction_name == 'test'
        assert record.ai_tool == AIToolType.CURSOR
        assert record.checksum == 'abc123'


class TestEnums:
    """Test enum types."""

    def test_ai_tool_type_values(self):
        assert AIToolType.CURSOR.value == 'cursor'
        assert AIToolType.COPILOT.value == 'copilot'
        assert AIToolType.WINSURF.value == 'winsurf'
        assert AIToolType.CLAUDE.value == 'claude'

    def test_conflict_resolution_values(self):
        assert ConflictResolution.SKIP.value == 'skip'
        assert ConflictResolution.RENAME.value == 'rename'
        assert ConflictResolution.OVERWRITE.value == 'overwrite'
