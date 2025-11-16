"""Integration tests for library management."""

from pathlib import Path

from aiconfigkit.core.models import LibraryInstruction
from aiconfigkit.storage.library import LibraryManager


class TestLibraryManager:
    """Test library management functionality."""

    def test_create_library_manager(self, temp_dir: Path):
        """Test creating library manager."""
        library_dir = temp_dir / "library"
        manager = LibraryManager(library_dir)

        assert manager.library_dir == library_dir
        assert library_dir.exists()

    def test_generate_namespace(self, temp_dir: Path):
        """Test namespace generation from URLs."""
        manager = LibraryManager(temp_dir)

        # Test GitHub URL
        namespace = manager.get_repo_namespace("https://github.com/company/instructions", "Company Instructions")
        assert "github" in namespace
        assert "company" in namespace

        # Test local path
        local_namespace = manager.get_repo_namespace("/local/path/instructions", "Local Instructions")
        assert "local" in local_namespace

    def test_add_repository(self, temp_dir: Path):
        """Test adding a repository to library."""
        manager = LibraryManager(temp_dir / "library")

        instructions = [
            LibraryInstruction(
                id="test/python-style",
                name="python-style",
                description="Python style guide",
                repo_namespace="test_repo",
                repo_url="https://github.com/test/repo",
                repo_name="Test Repo",
                author="Test Author",
                version="1.0.0",
                file_path="/path/to/file.md",
                tags=["python", "style"],
            )
        ]

        repo = manager.add_repository(
            repo_name="Test Repo",
            repo_description="Test repository",
            repo_url="https://github.com/test/repo",
            repo_author="Test Author",
            repo_version="1.0.0",
            instructions=instructions,
        )

        assert repo.name == "Test Repo"
        assert len(repo.instructions) == 1
        assert repo.namespace is not None

    def test_list_repositories(self, temp_dir: Path):
        """Test listing repositories."""
        manager = LibraryManager(temp_dir / "library")

        # Add two repositories
        for i in range(2):
            manager.add_repository(
                repo_name=f"Repo {i}",
                repo_description=f"Description {i}",
                repo_url=f"https://github.com/test/repo{i}",
                repo_author="Author",
                repo_version="1.0.0",
                instructions=[],
            )

        repos = manager.list_repositories()
        assert len(repos) == 2

    def test_get_repository(self, temp_dir: Path):
        """Test getting repository by namespace."""
        manager = LibraryManager(temp_dir / "library")

        repo = manager.add_repository(
            repo_name="Test Repo",
            repo_description="Test",
            repo_url="https://github.com/test/repo",
            repo_author="Author",
            repo_version="1.0.0",
            instructions=[],
        )

        retrieved = manager.get_repository(repo.namespace)
        assert retrieved is not None
        assert retrieved.name == "Test Repo"

    def test_remove_repository(self, temp_dir: Path):
        """Test removing repository from library."""
        manager = LibraryManager(temp_dir / "library")

        repo = manager.add_repository(
            repo_name="Test Repo",
            repo_description="Test",
            repo_url="https://github.com/test/repo",
            repo_author="Author",
            repo_version="1.0.0",
            instructions=[],
        )

        result = manager.remove_repository(repo.namespace)
        assert result is True

        retrieved = manager.get_repository(repo.namespace)
        assert retrieved is None

    def test_list_instructions(self, temp_dir: Path):
        """Test listing all instructions across repositories."""
        manager = LibraryManager(temp_dir / "library")

        instructions1 = [
            LibraryInstruction(
                id="repo1/inst1",
                name="inst1",
                description="Instruction 1",
                repo_namespace="repo1",
                repo_url="https://github.com/test/repo1",
                repo_name="Repo 1",
                author="Author",
                version="1.0.0",
                file_path="/path/to/inst1.md",
            )
        ]

        instructions2 = [
            LibraryInstruction(
                id="repo2/inst2",
                name="inst2",
                description="Instruction 2",
                repo_namespace="repo2",
                repo_url="https://github.com/test/repo2",
                repo_name="Repo 2",
                author="Author",
                version="1.0.0",
                file_path="/path/to/inst2.md",
            )
        ]

        manager.add_repository(
            repo_name="Repo 1",
            repo_description="First repo",
            repo_url="https://github.com/test/repo1",
            repo_author="Author",
            repo_version="1.0.0",
            instructions=instructions1,
        )

        manager.add_repository(
            repo_name="Repo 2",
            repo_description="Second repo",
            repo_url="https://github.com/test/repo2",
            repo_author="Author",
            repo_version="1.0.0",
            instructions=instructions2,
        )

        all_instructions = manager.list_instructions()
        assert len(all_instructions) == 2

    def test_get_instruction(self, temp_dir: Path):
        """Test getting instruction by ID."""
        manager = LibraryManager(temp_dir / "library")

        instructions = [
            LibraryInstruction(
                id="test/python-style",
                name="python-style",
                description="Python style guide",
                repo_namespace="test",
                repo_url="https://github.com/test/repo",
                repo_name="Test Repo",
                author="Author",
                version="1.0.0",
                file_path="/path/to/file.md",
            )
        ]

        manager.add_repository(
            repo_name="Test Repo",
            repo_description="Test",
            repo_url="https://github.com/test/repo",
            repo_author="Author",
            repo_version="1.0.0",
            instructions=instructions,
        )

        inst = manager.get_instruction("test/python-style")
        assert inst is not None
        assert inst.name == "python-style"

    def test_get_instructions_by_name(self, temp_dir: Path):
        """Test getting instructions by name (may be multiple)."""
        manager = LibraryManager(temp_dir / "library")

        # Add same instruction name from different repos
        for i in range(2):
            instructions = [
                LibraryInstruction(
                    id=f"repo{i}/python-style",
                    name="python-style",
                    description=f"Python style guide {i}",
                    repo_namespace=f"repo{i}",
                    repo_url=f"https://github.com/test/repo{i}",
                    repo_name=f"Repo {i}",
                    author="Author",
                    version="1.0.0",
                    file_path=f"/path/to/file{i}.md",
                )
            ]

            manager.add_repository(
                repo_name=f"Repo {i}",
                repo_description=f"Repo {i}",
                repo_url=f"https://github.com/test/repo{i}",
                repo_author="Author",
                repo_version="1.0.0",
                instructions=instructions,
            )

        matches = manager.get_instructions_by_name("python-style")
        assert len(matches) == 2

    def test_search_instructions(self, temp_dir: Path):
        """Test searching instructions with filters."""
        manager = LibraryManager(temp_dir / "library")

        instructions = [
            LibraryInstruction(
                id="test/python-style",
                name="python-style",
                description="Python style guidelines",
                repo_namespace="test",
                repo_url="https://github.com/test/repo",
                repo_name="Test Repo",
                author="Author",
                version="1.0.0",
                file_path="/path/to/file.md",
                tags=["python", "style"],
            ),
            LibraryInstruction(
                id="test/javascript-style",
                name="javascript-style",
                description="JavaScript style guidelines",
                repo_namespace="test",
                repo_url="https://github.com/test/repo",
                repo_name="Test Repo",
                author="Author",
                version="1.0.0",
                file_path="/path/to/file2.md",
                tags=["javascript", "style"],
            ),
        ]

        manager.add_repository(
            repo_name="Test Repo",
            repo_description="Test",
            repo_url="https://github.com/test/repo",
            repo_author="Author",
            repo_version="1.0.0",
            instructions=instructions,
        )

        # Search by query
        results = manager.search_instructions(query="python")
        assert len(results) == 1
        assert results[0].name == "python-style"

        # Search by tag
        results = manager.search_instructions(tags=["javascript"])
        assert len(results) == 1
        assert results[0].name == "javascript-style"

        # Search by repo namespace
        results = manager.search_instructions(repo_namespace="test")
        assert len(results) == 2

    def test_generate_alias_fallback(self, temp_dir: Path):
        """Test generate_alias fallback for non-URL repo names."""
        manager = LibraryManager(temp_dir / "library")

        # Test with git@ URL (non-https)
        alias = manager.generate_alias("git@github.com:company/repo.git", "My Repo")
        # Should fallback to sanitized repo name
        assert alias == "my-repo"

    def test_remove_repository_not_found(self, temp_dir: Path):
        """Test removing non-existent repository."""
        manager = LibraryManager(temp_dir / "library")

        # Try to remove non-existent namespace
        result = manager.remove_repository("nonexistent-namespace")
        assert result is False

    def test_get_repository_by_url(self, temp_dir: Path):
        """Test getting repository by source URL."""
        manager = LibraryManager(temp_dir / "library")

        # Add repository with URL
        _repo = manager.add_repository(
            repo_name="Test Repo",
            repo_description="Test",
            repo_url="https://github.com/test/repo",
            repo_author="Author",
            repo_version="1.0.0",
            instructions=[],
        )

        # Find by URL
        found = manager.get_repository_by_url("https://github.com/test/repo")
        assert found is not None
        assert found.name == "Test Repo"

    def test_get_repository_by_url_local_path(self, temp_dir: Path):
        """Test getting repository by local path URL."""
        manager = LibraryManager(temp_dir / "library")

        # Add repository with local path
        local_path = temp_dir / "my-repo"
        local_path.mkdir()

        _repo = manager.add_repository(
            repo_name="Local Repo",
            repo_description="Test",
            repo_url=str(local_path),
            repo_author="Author",
            repo_version="1.0.0",
            instructions=[],
        )

        # Find by path (should normalize to absolute)
        found = manager.get_repository_by_url(str(local_path))
        assert found is not None
        assert found.name == "Local Repo"

    def test_get_repository_by_url_not_found(self, temp_dir: Path):
        """Test get_repository_by_url returns None when URL not found."""
        manager = LibraryManager(temp_dir / "library")

        # Try to find non-existent repository
        found = manager.get_repository_by_url("https://github.com/nonexistent/repo")
        assert found is None

    def test_get_instruction_not_found(self, temp_dir: Path):
        """Test get_instruction returns None when not found."""
        manager = LibraryManager(temp_dir / "library")

        # No repositories added
        inst = manager.get_instruction("nonexistent/instruction")
        assert inst is None

    def test_get_instructions_by_source_and_name(self, temp_dir: Path):
        """Test getting instructions by source alias and name."""
        manager = LibraryManager(temp_dir / "library")

        instructions = [
            LibraryInstruction(
                id="test/python-style",
                name="python-style",
                description="Python style guide",
                repo_namespace="test",
                repo_url="https://github.com/test/repo",
                repo_name="Test Repo",
                author="Author",
                version="1.0.0",
                file_path="/path/to/file.md",
            )
        ]

        # Add repository with specific alias
        manager.add_repository(
            repo_name="Test Repo",
            repo_description="Test",
            repo_url="https://github.com/test/repo",
            repo_author="Author",
            repo_version="1.0.0",
            instructions=instructions,
            alias="test-repo",
        )

        # Find by source alias and name
        found = manager.get_instructions_by_source_and_name("test-repo", "python-style")
        assert len(found) == 1
        assert found[0].name == "python-style"

    def test_get_instructions_by_source_and_name_not_found(self, temp_dir: Path):
        """Test get_instructions_by_source_and_name with no matches."""
        manager = LibraryManager(temp_dir / "library")

        # No repositories added
        found = manager.get_instructions_by_source_and_name("nonexistent", "python-style")
        assert len(found) == 0

    def test_get_instruction_file_path(self, temp_dir: Path):
        """Test getting instruction file path."""
        manager = LibraryManager(temp_dir / "library")

        instructions = [
            LibraryInstruction(
                id="test/python-style",
                name="python-style",
                description="Python style guide",
                repo_namespace="test",
                repo_url="https://github.com/test/repo",
                repo_name="Test Repo",
                author="Author",
                version="1.0.0",
                file_path="/path/to/file.md",
            )
        ]

        manager.add_repository(
            repo_name="Test Repo",
            repo_description="Test",
            repo_url="https://github.com/test/repo",
            repo_author="Author",
            repo_version="1.0.0",
            instructions=instructions,
        )

        # Get file path
        path = manager.get_instruction_file_path("test/python-style")
        assert path is not None
        assert path.as_posix() == "/path/to/file.md"

    def test_get_instruction_file_path_not_found(self, temp_dir: Path):
        """Test get_instruction_file_path returns None when not found."""
        manager = LibraryManager(temp_dir / "library")

        # No repositories added
        path = manager.get_instruction_file_path("nonexistent/instruction")
        assert path is None

    def test_get_versioned_namespace(self, temp_dir: Path):
        """Test generating versioned namespace."""
        manager = LibraryManager(temp_dir / "library")

        # Test with tag
        namespace = manager.get_versioned_namespace("https://github.com/test/repo", "v1.0.0")
        assert "@v1.0.0" in namespace
        assert "github" in namespace

        # Test with branch with slashes
        namespace = manager.get_versioned_namespace("https://github.com/test/repo", "feature/new-feature")
        assert "@feature_new-feature" in namespace

    def test_list_repository_versions(self, temp_dir: Path):
        """Test listing all versions of a repository."""
        manager = LibraryManager(temp_dir / "library")

        # Add multiple versions of same repo
        base_url = "https://github.com/test/repo"

        # Add v1.0.0
        manager.add_repository(
            repo_name="Test Repo v1",
            repo_description="Version 1",
            repo_url=base_url,
            repo_author="Author",
            repo_version="1.0.0",
            instructions=[],
            namespace=manager.get_versioned_namespace(base_url, "v1.0.0"),
        )

        # Add v2.0.0
        manager.add_repository(
            repo_name="Test Repo v2",
            repo_description="Version 2",
            repo_url=base_url,
            repo_author="Author",
            repo_version="2.0.0",
            instructions=[],
            namespace=manager.get_versioned_namespace(base_url, "v2.0.0"),
        )

        # List versions
        versions = manager.list_repository_versions(base_url)
        assert len(versions) == 2
        assert any("v1.0.0" in ref for ref, _ in versions)
        assert any("v2.0.0" in ref for ref, _ in versions)
