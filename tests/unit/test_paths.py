"""Unit tests for path utilities."""

import os
from pathlib import Path

import pytest

from instructionkit.utils.paths import (
    get_home_directory,
    get_instructionkit_data_dir,
    safe_file_name,
    resolve_conflict_name,
)


class TestHomeDirectory:
    """Test home directory retrieval."""
    
    def test_get_home_directory(self):
        home = get_home_directory()
        assert isinstance(home, Path)
        assert home.exists()


class TestInstructionKitDataDir:
    """Test InstructionKit data directory."""
    
    def test_get_data_dir(self):
        data_dir = get_instructionkit_data_dir()
        assert isinstance(data_dir, Path)
        assert '.instructionkit' in str(data_dir)


class TestSafeFileName:
    """Test safe filename generation."""
    
    def test_remove_unsafe_characters(self):
        assert safe_file_name('test<>file') == 'test__file'
        assert safe_file_name('test|file') == 'test_file'
        assert safe_file_name('test:file') == 'test_file'
    
    def test_preserve_safe_characters(self):
        assert safe_file_name('test-file-123.md') == 'test-file-123.md'


class TestResolveConflictName:
    """Test conflict name resolution."""
    
    def test_resolve_with_suffix(self):
        original = Path('/path/to/file.md')
        resolved = resolve_conflict_name(original, 'backup')
        assert str(resolved) == '/path/to/file-backup.md'
    
    def test_resolve_without_suffix(self, tmp_path):
        # Create a file
        test_file = tmp_path / 'file.md'
        test_file.touch()
        
        # Resolve conflict should return file-1.md
        resolved = resolve_conflict_name(test_file)
        assert 'file-1.md' in str(resolved)
