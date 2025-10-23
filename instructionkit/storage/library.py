"""Library management for downloaded instructions."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from instructionkit.core.models import LibraryInstruction, LibraryRepository
from instructionkit.utils.paths import get_library_dir


class LibraryManager:
    """
    Manages the local library of downloaded instructions.

    The library structure:
    ~/.instructionkit/
    ├── library/
    │   ├── repo-namespace-1/
    │   │   └── instructions/
    │   │       └── instruction.md
    │   └── repo-namespace-2/
    │       └── instructions/
    └── library.json  (index of all repositories)
    """

    def __init__(self, library_dir: Optional[Path] = None):
        """
        Initialize library manager.

        Args:
            library_dir: Path to library directory (default: ~/.instructionkit/library)
        """
        self.library_dir = library_dir or get_library_dir()
        self.library_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.library_dir.parent / "library.json"

    def get_repo_namespace(self, url: str, repo_name: str) -> str:
        """
        Generate a unique namespace for a repository.

        Args:
            url: Repository URL
            repo_name: Repository name

        Returns:
            Namespace string (e.g., 'github.com_company_instructions')
        """
        # Parse URL to extract host and path
        # For local paths, use the folder name
        if url.startswith(('http://', 'https://', 'git@')):
            # Extract domain and repo path
            # https://github.com/company/instructions -> github.com_company_instructions
            import re

            # Remove protocol
            clean_url = re.sub(r'^(https?://|git@)', '', url)
            # Remove .git suffix
            clean_url = re.sub(r'\.git$', '', clean_url)
            # Replace special chars with underscore
            namespace = re.sub(r'[^a-zA-Z0-9]', '_', clean_url)
        else:
            # Local path - use folder name + sanitized path
            path = Path(url).resolve()
            namespace = f"local_{path.name}_{abs(hash(str(path))) % 100000}"

        return namespace

    def generate_alias(self, url: str, repo_name: str) -> str:
        """
        Auto-generate a friendly alias from URL or repo name.

        Args:
            url: Repository URL
            repo_name: Repository name

        Returns:
            Friendly alias (e.g., 'company-instructions' from github.com/company/instructions)
        """
        import re

        if url.startswith(('http://', 'https://')):
            # Extract repo path from URL
            # https://github.com/company/instructions -> company-instructions
            match = re.search(r'/([^/]+)/([^/]+?)(?:\.git)?$', url)
            if match:
                org, repo = match.groups()
                return f"{org}-{repo}".lower()

        # Fallback to sanitized repo name
        return re.sub(r'[^a-z0-9-]', '-', repo_name.lower()).strip('-')

    def load_index(self) -> dict[str, LibraryRepository]:
        """
        Load the library index.

        Returns:
            Dictionary mapping namespace to LibraryRepository
        """
        if not self.index_file.exists():
            return {}

        with open(self.index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            namespace: LibraryRepository.from_dict(repo_data)
            for namespace, repo_data in data.items()
        }

    def save_index(self, repositories: dict[str, LibraryRepository]) -> None:
        """
        Save the library index.

        Args:
            repositories: Dictionary mapping namespace to LibraryRepository
        """
        data = {
            namespace: repo.to_dict()
            for namespace, repo in repositories.items()
        }

        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_repository(
        self,
        repo_name: str,
        repo_description: str,
        repo_url: str,
        repo_author: str,
        repo_version: str,
        instructions: list[LibraryInstruction],
        alias: Optional[str] = None,
    ) -> LibraryRepository:
        """
        Add a repository to the library.

        Args:
            repo_name: Repository display name
            repo_description: Repository description
            repo_url: Repository URL
            repo_author: Repository author
            repo_version: Repository version
            instructions: List of instructions to add
            alias: User-friendly alias (auto-generated if not provided)

        Returns:
            Created LibraryRepository
        """
        # Generate namespace
        namespace = self.get_repo_namespace(repo_url, repo_name)

        # Auto-generate alias if not provided
        if alias is None:
            alias = self.generate_alias(repo_url, repo_name)

        # Create repository directory
        repo_dir = self.library_dir / namespace
        repo_dir.mkdir(parents=True, exist_ok=True)

        # Create instructions directory
        instructions_dir = repo_dir / "instructions"
        instructions_dir.mkdir(exist_ok=True)

        # Create repository object
        library_repo = LibraryRepository(
            namespace=namespace,
            name=repo_name,
            description=repo_description,
            url=repo_url,
            author=repo_author,
            version=repo_version,
            downloaded_at=datetime.now(),
            alias=alias,
            instructions=instructions,
        )

        # Update index
        index = self.load_index()
        index[namespace] = library_repo
        self.save_index(index)

        return library_repo

    def remove_repository(self, namespace: str) -> bool:
        """
        Remove a repository from the library.

        Args:
            namespace: Repository namespace to remove

        Returns:
            True if removed, False if not found
        """
        # Load index
        index = self.load_index()

        if namespace not in index:
            return False

        # Remove from index
        del index[namespace]
        self.save_index(index)

        # Remove directory
        repo_dir = self.library_dir / namespace
        if repo_dir.exists():
            shutil.rmtree(repo_dir)

        return True

    def get_repository(self, namespace: str) -> Optional[LibraryRepository]:
        """
        Get a repository by namespace.

        Args:
            namespace: Repository namespace

        Returns:
            LibraryRepository or None if not found
        """
        index = self.load_index()
        return index.get(namespace)

    def get_repository_by_url(self, url: str) -> Optional[LibraryRepository]:
        """
        Find a repository by its source URL.

        Args:
            url: Repository URL (will be normalized for comparison)

        Returns:
            LibraryRepository or None if not found
        """
        # Normalize path for comparison
        if not url.startswith(('http://', 'https://', 'git@')):
            url = str(Path(url).resolve())

        index = self.load_index()
        for repo in index.values():
            repo_url = repo.url
            # Normalize repo URL for comparison
            if not repo_url.startswith(('http://', 'https://', 'git@')):
                repo_url = str(Path(repo_url).resolve())

            if repo_url == url:
                return repo

        return None

    def list_repositories(self) -> list[LibraryRepository]:
        """
        List all repositories in the library.

        Returns:
            List of LibraryRepository objects
        """
        index = self.load_index()
        return list(index.values())

    def list_instructions(self) -> list[LibraryInstruction]:
        """
        List all instructions across all repositories.

        Returns:
            Flattened list of all LibraryInstruction objects
        """
        instructions = []
        for repo in self.list_repositories():
            instructions.extend(repo.instructions)
        return instructions

    def get_instruction(self, instruction_id: str) -> Optional[LibraryInstruction]:
        """
        Get an instruction by ID.

        Args:
            instruction_id: Instruction ID (namespace/name)

        Returns:
            LibraryInstruction or None if not found
        """
        for instruction in self.list_instructions():
            if instruction.id == instruction_id:
                return instruction
        return None

    def get_instructions_by_name(self, name: str) -> list[LibraryInstruction]:
        """
        Get all instructions with a given name (may be multiple from different repos).

        Args:
            name: Instruction name

        Returns:
            List of LibraryInstruction objects with matching name
        """
        return [
            inst for inst in self.list_instructions()
            if inst.name == name
        ]

    def get_instructions_by_source_and_name(
        self, source_alias: str, name: str
    ) -> list[LibraryInstruction]:
        """
        Get instructions by source alias and name.

        Args:
            source_alias: Source alias to filter by
            name: Instruction name

        Returns:
            List of LibraryInstruction objects matching source and name
        """
        # Find repositories matching the source alias
        matching_repos = []
        for repo in self.list_repositories():
            if repo.alias and repo.alias.lower() == source_alias.lower():
                matching_repos.append(repo)

        # Get instructions from matching repos
        return [
            inst
            for repo in matching_repos
            for inst in repo.instructions
            if inst.name == name
        ]

    def search_instructions(
        self,
        query: Optional[str] = None,
        repo_namespace: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list[LibraryInstruction]:
        """
        Search instructions with filters.

        Args:
            query: Search query (matches name or description)
            repo_namespace: Filter by repository namespace
            tags: Filter by tags (instruction must have at least one matching tag)

        Returns:
            List of matching LibraryInstruction objects
        """
        instructions = self.list_instructions()

        # Filter by query
        if query:
            query_lower = query.lower()
            instructions = [
                inst for inst in instructions
                if query_lower in inst.name.lower() or query_lower in inst.description.lower()
            ]

        # Filter by repo
        if repo_namespace:
            instructions = [
                inst for inst in instructions
                if inst.repo_namespace == repo_namespace
            ]

        # Filter by tags
        if tags:
            instructions = [
                inst for inst in instructions
                if any(tag in inst.tags for tag in tags)
            ]

        return instructions

    def get_instruction_file_path(self, instruction_id: str) -> Optional[Path]:
        """
        Get the absolute path to an instruction file.

        Args:
            instruction_id: Instruction ID (namespace/name)

        Returns:
            Path to instruction file or None if not found
        """
        instruction = self.get_instruction(instruction_id)
        if not instruction:
            return None

        return Path(instruction.file_path)
