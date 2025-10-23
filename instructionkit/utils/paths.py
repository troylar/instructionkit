"""Cross-platform path utilities for AI coding tool directories."""

import os
from pathlib import Path
from typing import Optional


def get_home_directory() -> Path:
    """Get user's home directory in a cross-platform way."""
    return Path.home()


def get_cursor_config_dir() -> Path:
    """Get Cursor configuration directory based on platform."""
    home = get_home_directory()

    if os.name == 'nt':  # Windows
        return home / 'AppData' / 'Roaming' / 'Cursor' / 'User' / 'globalStorage'
    elif os.name == 'posix':
        if 'darwin' in os.uname().sysname.lower():  # macOS
            return home / 'Library' / 'Application Support' / 'Cursor' / 'User' / 'globalStorage'
        else:  # Linux
            return home / '.config' / 'Cursor' / 'User' / 'globalStorage'

    raise OSError(f"Unsupported operating system: {os.name}")


def get_copilot_config_dir() -> Path:
    """Get GitHub Copilot (VS Code) configuration directory based on platform."""
    home = get_home_directory()

    if os.name == 'nt':  # Windows
        return home / 'AppData' / 'Roaming' / 'Code' / 'User' / 'globalStorage' / 'github.copilot'
    elif os.name == 'posix':
        if 'darwin' in os.uname().sysname.lower():  # macOS
            return home / 'Library' / 'Application Support' / 'Code' / 'User' / 'globalStorage' / 'github.copilot'
        else:  # Linux
            return home / '.config' / 'Code' / 'User' / 'globalStorage' / 'github.copilot'

    raise OSError(f"Unsupported operating system: {os.name}")


def get_winsurf_config_dir() -> Path:
    """Get Windsurf configuration directory based on platform."""
    home = get_home_directory()

    if os.name == 'nt':  # Windows
        return home / 'AppData' / 'Roaming' / 'Windsurf' / 'User' / 'globalStorage'
    elif os.name == 'posix':
        if 'darwin' in os.uname().sysname.lower():  # macOS
            return home / 'Library' / 'Application Support' / 'Windsurf' / 'User' / 'globalStorage'
        else:  # Linux
            return home / '.config' / 'Windsurf' / 'User' / 'globalStorage'

    raise OSError(f"Unsupported operating system: {os.name}")


def get_claude_config_dir() -> Path:
    """Get Claude Code configuration directory based on platform."""
    home = get_home_directory()

    # Claude Code uses ~/.claude/rules/ for global rules
    # This is consistent across all platforms
    return home / '.claude' / 'rules'


def get_instructionkit_data_dir() -> Path:
    """Get InstructionKit data directory for tracking installations."""
    home = get_home_directory()
    data_dir = home / '.instructionkit'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_library_dir() -> Path:
    """Get InstructionKit library directory for downloaded instructions."""
    library_dir = get_instructionkit_data_dir() / 'library'
    library_dir.mkdir(parents=True, exist_ok=True)
    return library_dir


def get_installation_tracker_path() -> Path:
    """Get path to installation tracking JSON file."""
    return get_instructionkit_data_dir() / 'installations.json'


def ensure_directory_exists(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)


def safe_file_name(name: str) -> str:
    """Sanitize a string to be safe as a filename."""
    # Replace unsafe characters with underscores
    unsafe_chars = '<>:"/\\|?*'
    safe_name = name
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    return safe_name


def resolve_conflict_name(original_path: Path, suffix: Optional[str] = None) -> Path:
    """Generate a new path for conflict resolution with optional suffix."""
    if suffix:
        stem = original_path.stem
        extension = original_path.suffix
        new_name = f"{stem}-{suffix}{extension}"
        return original_path.parent / new_name

    # Auto-increment: file.md -> file-1.md -> file-2.md
    counter = 1
    while True:
        stem = original_path.stem
        extension = original_path.suffix
        new_name = f"{stem}-{counter}{extension}"
        new_path = original_path.parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1
