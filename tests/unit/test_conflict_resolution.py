"""Unit tests for conflict resolution."""

from pathlib import Path

from instructionkit.core.conflict_resolution import ConflictResolver
from instructionkit.core.models import ConflictResolution


class TestConflictResolver:
    """Test conflict resolution strategies."""

    def test_resolve_skip(self, temp_dir: Path):
        """Test skip conflict resolution."""
        resolver = ConflictResolver(default_strategy=ConflictResolution.SKIP)

        existing_file = temp_dir / "test.md"
        existing_file.write_text("existing content")

        conflict_info = resolver.resolve("test", existing_file, ConflictResolution.SKIP)

        assert conflict_info.instruction_name == "test"
        assert conflict_info.resolution == ConflictResolution.SKIP
        assert conflict_info.new_path is None

    def test_resolve_overwrite(self, temp_dir: Path):
        """Test overwrite conflict resolution."""
        resolver = ConflictResolver(default_strategy=ConflictResolution.OVERWRITE)

        existing_file = temp_dir / "test.md"
        existing_file.write_text("existing content")

        conflict_info = resolver.resolve("test", existing_file, ConflictResolution.OVERWRITE)

        assert conflict_info.instruction_name == "test"
        assert conflict_info.resolution == ConflictResolution.OVERWRITE
        # Overwrite returns the same path (where it will overwrite)
        assert conflict_info.new_path == str(existing_file)

    def test_resolve_rename(self, temp_dir: Path):
        """Test rename conflict resolution."""
        resolver = ConflictResolver(default_strategy=ConflictResolution.RENAME)

        existing_file = temp_dir / "test.md"
        existing_file.write_text("existing content")

        conflict_info = resolver.resolve("test", existing_file, ConflictResolution.RENAME)

        assert conflict_info.instruction_name == "test"
        assert conflict_info.resolution == ConflictResolution.RENAME
        assert conflict_info.new_path is not None
        assert "test" in conflict_info.new_path
        assert conflict_info.new_path != str(existing_file)

    def test_rename_generates_unique_name(self, temp_dir: Path):
        """Test that rename generates unique filenames."""
        resolver = ConflictResolver(default_strategy=ConflictResolution.RENAME)

        # Create multiple existing files
        for i in range(3):
            (temp_dir / f"test-{i}.md").write_text("content")

        existing_file = temp_dir / "test.md"
        existing_file.write_text("existing content")

        conflict_info = resolver.resolve("test", existing_file, ConflictResolution.RENAME)

        # Should generate a unique name that doesn't exist
        new_path = Path(conflict_info.new_path)
        assert not new_path.exists()
        assert new_path.parent == existing_file.parent

    def test_default_strategy_used(self, temp_dir: Path):
        """Test that default strategy is used when not specified."""
        resolver = ConflictResolver(default_strategy=ConflictResolution.RENAME)

        existing_file = temp_dir / "test.md"
        existing_file.write_text("existing content")

        # Don't specify strategy in resolve call
        conflict_info = resolver.resolve("test", existing_file)

        assert conflict_info.resolution == ConflictResolution.RENAME
