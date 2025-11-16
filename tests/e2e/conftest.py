"""Fixtures for end-to-end package tests."""

import hashlib
import subprocess
from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture
def git_repo(tmp_path: Path) -> Callable[[str, dict[str, str] | None], Path]:
    """Create a git repository with optional initial files.

    Returns a function that creates a git repo at a given path with optional files.
    """

    def _create_repo(name: str, files: dict[str, str] | None = None) -> Path:
        """Create a git repository.

        Args:
            name: Repository name
            files: Optional dict of filename -> content to initialize

        Returns:
            Path to the repository
        """
        repo_path = tmp_path / name
        repo_path.mkdir(parents=True, exist_ok=True)

        # Initialize git repo
        subprocess.run(
            ["git", "init"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        # Configure git user
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        # Add initial files if provided
        if files:
            for filename, content in files.items():
                file_path = repo_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)

        # Initial commit if there are files
        if files:
            subprocess.run(
                ["git", "add", "."],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

        return repo_path

    return _create_repo


@pytest.fixture
def package_builder(tmp_path: Path) -> Callable:
    """Build a package with specified components.

    Returns a function that creates a complete package directory.
    """

    def _build_package(
        name: str,
        version: str,
        instructions: list[dict[str, str]] | None = None,
        mcp_servers: list[dict[str, str]] | None = None,
        hooks: list[dict[str, str]] | None = None,
        commands: list[dict[str, str]] | None = None,
        resources: list[dict[str, str]] | None = None,
        as_git: bool = False,
    ) -> Path:
        """Build a package.

        Args:
            name: Package name
            version: Package version
            instructions: List of instruction dicts with 'name', 'description', 'content'
            mcp_servers: List of MCP server dicts
            hooks: List of hook dicts
            commands: List of command dicts
            resources: List of resource dicts
            as_git: If True, initialize as git repository with version tag

        Returns:
            Path to package directory
        """
        # Include version in path to avoid conflicts when building multiple versions
        pkg_path = tmp_path / f"packages/{name}-{version}"
        pkg_path.mkdir(parents=True, exist_ok=True)

        # Build manifest
        manifest = f"""name: {name}
version: {version}
description: Test package {name}
author: Test Author
namespace: test/{name}
license: MIT

components:
"""

        # Add instructions
        if instructions:
            manifest += "  instructions:\n"
            (pkg_path / "instructions").mkdir(exist_ok=True)
            for inst in instructions:
                inst_name = inst["name"]
                inst_desc = inst.get("description", f"{inst_name} instruction")
                inst_content = inst.get("content", f"# {inst_name}\n\nTest instruction content.")
                inst_tags = inst.get("tags", ["test"])

                manifest += f"""    - name: {inst_name}
      description: {inst_desc}
      file: instructions/{inst_name}.md
      tags: {inst_tags}
"""
                (pkg_path / "instructions" / f"{inst_name}.md").write_text(inst_content)

        # Add MCP servers
        if mcp_servers:
            manifest += "  mcp_servers:\n"
            (pkg_path / "mcp").mkdir(exist_ok=True)
            for mcp in mcp_servers:
                mcp_name = mcp["name"]
                mcp_desc = mcp.get("description", f"{mcp_name} MCP server")
                mcp_config = mcp.get(
                    "config",
                    {"mcpServers": {mcp_name: {"command": "npx", "args": ["-y", f"@test/{mcp_name}"], "env": {}}}},
                )
                mcp_creds = mcp.get("requires_credentials", [])

                manifest += f"""    - name: {mcp_name}
      description: {mcp_desc}
      file: mcp/{mcp_name}.json
      tags: [mcp, test]
"""
                if mcp_creds:
                    manifest += "      requires_credentials:\n"
                    for cred in mcp_creds:
                        manifest += f"        - {cred}\n"

                import json

                (pkg_path / "mcp" / f"{mcp_name}.json").write_text(json.dumps(mcp_config, indent=2))

        # Add hooks
        if hooks:
            manifest += "  hooks:\n"
            (pkg_path / "hooks").mkdir(exist_ok=True)
            for hook in hooks:
                hook_name = hook["name"]
                hook_desc = hook.get("description", f"{hook_name} hook")
                hook_type = hook.get("hook_type", hook_name)  # Default to hook name
                hook_content = hook.get(
                    "content",
                    f"""#!/usr/bin/env bash
# {hook_name} hook
echo "Running {hook_name}"
exit 0
""",
                )

                manifest += f"""    - name: {hook_name}
      description: {hook_desc}
      file: hooks/{hook_name}.sh
      hook_type: {hook_type}
      tags: [git, test]
"""
                hook_file = pkg_path / "hooks" / f"{hook_name}.sh"
                hook_file.write_text(hook_content)
                hook_file.chmod(0o755)

        # Add commands
        if commands:
            manifest += "  commands:\n"
            (pkg_path / "commands").mkdir(exist_ok=True)
            for cmd in commands:
                cmd_name = cmd["name"]
                cmd_desc = cmd.get("description", f"{cmd_name} command")
                cmd_type = cmd.get("command_type", "shell")  # Default to shell
                cmd_content = cmd.get(
                    "content",
                    f"""#!/usr/bin/env bash
# {cmd_name} command
echo "Running {cmd_name}"
exit 0
""",
                )

                manifest += f"""    - name: {cmd_name}
      description: {cmd_desc}
      file: commands/{cmd_name}.sh
      command_type: {cmd_type}
      tags: [automation, test]
"""
                cmd_file = pkg_path / "commands" / f"{cmd_name}.sh"
                cmd_file.write_text(cmd_content)
                cmd_file.chmod(0o755)

        # Add resources
        if resources:
            manifest += "  resources:\n"
            (pkg_path / "resources").mkdir(exist_ok=True)
            for res in resources:
                res_name = res["name"]
                res_desc = res.get("description", f"{res_name} resource")
                res_content = res.get("content", f"# {res_name} resource\nTest content")
                res_install_path = res.get("install_path", res_name)

                # Write the file first so we can calculate its checksum
                resource_file = pkg_path / "resources" / res_name
                resource_file.write_text(res_content)

                # Calculate checksum
                checksum = hashlib.sha256(res_content.encode()).hexdigest()

                manifest += f"""    - name: {res_name}
      description: {res_desc}
      file: resources/{res_name}
      install_path: {res_install_path}
      checksum: sha256:{checksum}
      size: {len(res_content)}
      tags: [config, test]
"""

        # Write manifest
        (pkg_path / "ai-config-kit-package.yaml").write_text(manifest)

        # Create README
        readme = f"""# {name}

Test package v{version}

## Components

"""
        if instructions:
            readme += f"- {len(instructions)} instruction(s)\n"
        if mcp_servers:
            readme += f"- {len(mcp_servers)} MCP server(s)\n"
        if hooks:
            readme += f"- {len(hooks)} hook(s)\n"
        if commands:
            readme += f"- {len(commands)} command(s)\n"
        if resources:
            readme += f"- {len(resources)} resource(s)\n"

        (pkg_path / "README.md").write_text(readme)

        # Initialize as git repo if requested
        if as_git:
            subprocess.run(
                ["git", "init"],
                cwd=pkg_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=pkg_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=pkg_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "add", "."],
                cwd=pkg_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"Release v{version}"],
                cwd=pkg_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "tag", f"v{version}"],
                cwd=pkg_path,
                check=True,
                capture_output=True,
            )

        return pkg_path

    return _build_package


@pytest.fixture
def test_project(tmp_path: Path) -> Path:
    """Create a test project directory with git initialized."""
    project_path = tmp_path / "test-project"
    project_path.mkdir(parents=True)

    # Initialize git
    subprocess.run(
        ["git", "init"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )

    # Create a basic file
    (project_path / "README.md").write_text("# Test Project\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )

    return project_path
