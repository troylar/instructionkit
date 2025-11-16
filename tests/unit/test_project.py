"""Unit tests for project detection utilities."""

from pathlib import Path

from aiconfigkit.utils.project import (
    find_project_root,
    get_project_installation_tracker_path,
    get_project_instructions_dir,
    is_in_project,
)


class TestProjectDetection:
    """Test project root detection."""

    def test_find_project_root_with_git(self, temp_dir: Path):
        """Test finding project root with .git directory."""
        project = temp_dir / "project"
        project.mkdir()
        (project / ".git").mkdir()

        # Create subdirectory
        subdir = project / "src" / "module"
        subdir.mkdir(parents=True)

        # Should find project root from subdirectory
        root = find_project_root(subdir)
        # Resolve both paths to handle symlinks (macOS /var -> /private/var)
        assert root.resolve() == project.resolve()

    def test_find_project_root_with_pyproject(self, temp_dir: Path):
        """Test finding project root with pyproject.toml."""
        project = temp_dir / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("[project]\nname = 'test'")

        subdir = project / "src"
        subdir.mkdir()

        root = find_project_root(subdir)
        assert root.resolve() == project.resolve()

    def test_find_project_root_with_package_json(self, temp_dir: Path):
        """Test finding project root with package.json."""
        project = temp_dir / "project"
        project.mkdir()
        (project / "package.json").write_text('{"name": "test"}')

        root = find_project_root(project)
        assert root.resolve() == project.resolve()

    def test_find_project_root_not_found(self, temp_dir: Path):
        """Test when no project root is found."""
        # Empty directory with no markers
        root = find_project_root(temp_dir)
        assert root is None

    def test_find_project_root_multiple_markers(self, temp_dir: Path):
        """Test with multiple project markers (should find first)."""
        project = temp_dir / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / "pyproject.toml").write_text("[project]\nname = 'test'")
        (project / "package.json").write_text('{"name": "test"}')

        root = find_project_root(project)
        assert root.resolve() == project.resolve()

    def test_find_project_root_nested_projects(self, temp_dir: Path):
        """Test finding nearest project root with nested projects."""
        outer = temp_dir / "outer"
        outer.mkdir()
        (outer / ".git").mkdir()

        inner = outer / "inner"
        inner.mkdir()
        (inner / "pyproject.toml").write_text("[project]\nname = 'inner'")

        # Should find inner project from within inner
        root = find_project_root(inner)
        assert root.resolve() == inner.resolve()

    def test_is_in_project(self, temp_dir: Path, monkeypatch):
        """Test checking if currently in a project."""
        project = temp_dir / "project"
        project.mkdir()
        (project / ".git").mkdir()

        # Mock current directory
        monkeypatch.chdir(project)

        assert is_in_project() is True

    def test_is_not_in_project(self, temp_dir: Path, monkeypatch):
        """Test checking when not in a project."""
        # Mock current directory to temp without markers
        monkeypatch.chdir(temp_dir)

        assert is_in_project() is False


class TestProjectInstructionsDir:
    """Test project instructions directory management."""

    def test_get_project_instructions_dir(self, temp_dir: Path):
        """Test getting project instructions directory."""
        project = temp_dir / "project"
        project.mkdir()

        instructions_dir = get_project_instructions_dir(project)

        assert instructions_dir == project / ".instructionkit"
        assert instructions_dir.exists()

    def test_get_project_instructions_dir_no_create(self, temp_dir: Path):
        """Test getting directory without creating it."""
        project = temp_dir / "project"
        project.mkdir()

        instructions_dir = get_project_instructions_dir(project, create=False)

        assert instructions_dir == project / ".instructionkit"
        assert not instructions_dir.exists()

    def test_get_project_installation_tracker_path(self, temp_dir: Path):
        """Test getting installation tracker path."""
        project = temp_dir / "project"
        project.mkdir()

        tracker_path = get_project_installation_tracker_path(project)

        assert tracker_path == project / ".instructionkit" / "installations.json"
        assert tracker_path.parent.exists()
