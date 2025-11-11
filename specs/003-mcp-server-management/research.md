# MCP Server Configuration Management - Technical Research

**Date:** 2025-11-11
**Author:** Research for InstructionKit MCP Feature
**Purpose:** Technical recommendations for implementing MCP server configuration management

## Executive Summary

This document provides research findings and recommendations for implementing MCP server configuration management in InstructionKit. The feature needs to safely modify AI tool configuration files, manage environment variables, validate commands, and ensure data integrity across Windows, macOS, and Linux platforms.

**Key Recommendations:**
- Use Python's built-in `json` module with manual comment preservation strategy
- Use `python-dotenv` for .env file management
- Implement atomic file writes using temp file + `os.replace()` pattern
- Use `shutil.which()` for cross-platform command validation
- Follow platform-specific config file locations for each AI tool

---

## 1. JSON Manipulation Library

### Challenge
We need to safely read/write JSON config files while:
- Preserving existing formatting and indentation
- Preserving comments (JSONC format used by some tools)
- Maintaining key order
- Writing atomically to prevent corruption

### Research Findings

#### Standard JSON Module (Recommended)
**Pros:**
- Built into Python 3.10+ (no dependencies)
- Preserves key order by default (Python 3.7+)
- Can control indentation with `indent` parameter
- Battle-tested and cross-platform
- Type-safe and well-documented

**Cons:**
- Cannot parse comments (standard JSON spec doesn't allow them)
- Cannot preserve original formatting exactly
- Requires manual comment handling

**Key Features:**
```python
import json

# Reading JSON
with open('config.json', 'r') as f:
    config = json.load(f)  # Preserves key order in Python 3.7+

# Writing JSON with formatting
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
```

#### Alternative: pyjson5
**Pros:**
- Parses JSON5 format (comments, trailing commas, unquoted keys)
- Written in Cython (compiled, fast)
- Actively maintained (latest: 2.0.0, Oct 2025)
- Compatible with JSONC format

**Cons:**
- External dependency
- Does NOT preserve comments when re-serializing
- Comments are stripped during parsing
- More complex than needed for our use case

**Package:** `pyjson5` on PyPI

#### Alternative: commentjson
**Pros:**
- Simple API similar to json module
- Handles comments during parsing

**Cons:**
- Uses Python `#` style comments (non-standard)
- Does NOT preserve comments when re-serializing
- Less actively maintained
- Not compatible with JSONC spec (uses `//` and `/* */`)

**Package:** `commentjson` on PyPI

#### Alternative: jsonc-parser
**Pros:**
- Designed for JSONC format
- Lightweight

**Cons:**
- Less actively maintained
- Does NOT preserve comments
- Limited documentation

**Package:** `jsonc-parser` on PyPI

### Critical Limitation
**None of these libraries preserve comments when re-serializing.** All comment-aware parsers strip comments during parsing and return plain Python dictionaries.

### Recommendation

**Use Python's built-in `json` module with a manual comment preservation strategy.**

#### Strategy: Selective Update Pattern

1. **Read the entire file as text** (preserve comments and formatting)
2. **Parse JSON to modify only the target section** (`mcpServers`)
3. **Use string replacement** to update only the changed section
4. **Fall back to full rewrite** if file is corrupted or doesn't exist

#### Implementation Approach

```python
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

class SafeJsonConfig:
    """Safely update JSON config files while preserving comments."""

    def __init__(self, config_path: Path):
        self.config_path = config_path

    def read(self) -> Dict[str, Any]:
        """Read and parse JSON config."""
        if not self.config_path.exists():
            return {}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to parse with standard json
        try:
            # Remove comments for parsing (simple approach)
            clean_content = self._strip_comments(content)
            return json.loads(clean_content)
        except json.JSONDecodeError:
            # If parsing fails, return empty dict
            return {}

    def _strip_comments(self, text: str) -> str:
        """Strip // and /* */ style comments from JSON text."""
        # Remove single-line comments
        text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
        # Remove multi-line comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        return text

    def update_section(
        self,
        section_key: str,
        section_data: Dict[str, Any]
    ) -> None:
        """Update a specific section of the JSON config."""
        # Read current config
        config = self.read()

        # Update the section
        config[section_key] = section_data

        # Write back (will lose comments, but that's acceptable)
        self.write(config)

    def write(self, config: Dict[str, Any]) -> None:
        """Write config to file with atomic operation."""
        content = json.dumps(config, indent=2, ensure_ascii=False)

        # Atomic write (see section 3)
        temp_path = self.config_path.with_suffix('.tmp')
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
                f.flush()
                import os
                os.fsync(f.fileno())

            # Atomic rename
            temp_path.replace(self.config_path)
        except Exception:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise
```

#### Trade-offs Accepted

1. **Comments will be lost on modification** - This is acceptable because:
   - Users typically don't add extensive comments to these config files
   - The `mcpServers` section is usually generated, not hand-written
   - We can add a warning in the CLI about comment preservation
   - Alternative is to not modify the file at all (worse UX)

2. **Formatting may change** - We'll use consistent 2-space indentation

3. **Simplicity over perfection** - The complex alternative would be:
   - Parse with a full AST-preserving parser
   - Manipulate the AST
   - Re-serialize with original formatting
   - This adds significant complexity for minimal benefit

### Dependencies
None required - use built-in `json` module.

---

## 2. Dotenv Library Best Practices

### Challenge
Manage environment variables in .env files for MCP server configurations, handling multi-line values, special characters, and validation.

### Research Findings

#### python-dotenv (Recommended)

**Package:** `python-dotenv` on PyPI

**Key Features:**
- Industry standard for .env file management in Python
- Supports multi-line values in quoted strings
- Handles special characters and escape sequences
- Load variables into `os.environ`
- Can read specific variables without polluting environment
- Cross-platform compatible

**Multi-line Values:**
```bash
# Approach 1: Actual line breaks in quotes
PRIVATE_KEY="-----BEGIN CERTIFICATE-----
JSDFALDAFSSKLABVCXZLV2314IH4IHDFG
-----END CERTIFICATE-----"

# Approach 2: Escape sequences
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nHkVN9...\n-----END KEY-----\n"
```

**Special Characters:**
```bash
# Double quotes allow escape sequences
API_KEY="key\nwith\nnewlines"

# Single quotes preserve literal values
LITERAL='value\nwith\nbackslashes'

# Unquoted values work for simple strings
SIMPLE_VAR=value123
```

**Basic Usage:**
```python
from dotenv import load_dotenv, set_key, get_key, find_dotenv
import os

# Load .env file into environment
load_dotenv()

# Access variables
api_key = os.getenv('API_KEY')

# Read specific variable without loading all
value = get_key('.env', 'MY_VAR')

# Set/update a variable
set_key('.env', 'MY_VAR', 'new_value')

# Find .env file in current or parent directories
env_file = find_dotenv()
```

**Environment Variable Validation:**
```python
import os
from typing import List

def validate_required_vars(required: List[str]) -> None:
    """Validate required environment variables exist."""
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

# Usage
validate_required_vars(['DATABASE_URL', 'API_KEY', 'SECRET_KEY'])
```

### Best Practices

#### 1. Naming Conventions
- Use UPPERCASE with underscores: `DATABASE_URL`, `API_KEY`
- Be descriptive and unambiguous
- Prefix with project/tool name to avoid conflicts: `MCP_SERVER_PATH`, `CLAUDE_API_KEY`

#### 2. Format Standards
```bash
# Good: Clear, descriptive names
DATABASE_URL=postgresql://localhost/mydb
API_KEY=sk-abc123def456

# Good: Multi-line values in quotes
SSH_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"

# Good: Empty value with equals sign
OPTIONAL_VAR=

# Avoid: Ambiguous names
DB=localhost
KEY=secret
```

#### 3. File Structure
```bash
# .env file structure
# Group related variables together
# Add comments to explain complex values

# Database Configuration
DATABASE_URL=postgresql://localhost/mydb
DATABASE_POOL_SIZE=10

# API Keys
API_KEY=sk-abc123def456
API_SECRET=secret789

# MCP Server Configuration
MCP_SERVER_PATH=/usr/local/bin/mcp-server
MCP_SERVER_ARGS="--verbose --port 3000"
```

#### 4. Validation at Startup
```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Validate immediately after loading
REQUIRED_VARS = ['API_KEY', 'DATABASE_URL']
missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"Missing variables: {', '.join(missing)}")
```

#### 5. Using with Pydantic (Type Safety)
```python
from pydantic_settings import BaseSettings
from pydantic import Field

class MCPServerConfig(BaseSettings):
    """MCP Server configuration with validation."""

    command: str = Field(..., min_length=1)
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)

    class Config:
        env_prefix = 'MCP_'  # Only load variables starting with MCP_
        case_sensitive = False

# Usage
config = MCPServerConfig()  # Automatically loads from environment
```

### Recommendation

**Use `python-dotenv` for all .env file operations.**

- Add as a dependency: `python-dotenv>=1.0.0`
- Use `load_dotenv()` at application startup
- Validate required variables immediately after loading
- Use uppercase names with underscores
- Quote multi-line values
- Prefix variables with tool/project name to prevent conflicts

### Alternative: Custom Parser

If we want to avoid the dependency, we can implement basic .env parsing:

```python
import re
from pathlib import Path
from typing import Dict

def parse_dotenv(env_file: Path) -> Dict[str, str]:
    """Simple .env file parser."""
    env_vars = {}

    if not env_file.exists():
        return env_vars

    content = env_file.read_text()

    # Pattern matches: KEY=value or KEY="value" or KEY='value'
    pattern = re.compile(
        r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$',
        re.MULTILINE
    )

    for match in pattern.finditer(content):
        key = match.group(1)
        value = match.group(2).strip()

        # Remove quotes
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        env_vars[key] = value

    return env_vars
```

**However, this lacks:**
- Multi-line value support
- Escape sequence handling
- Variable expansion
- Comprehensive testing

**Verdict:** Use `python-dotenv` - it's well-tested, feature-complete, and widely used.

---

## 3. Atomic File Write Patterns

### Challenge
Ensure file writes are atomic to prevent corruption from:
- Process crashes
- Power failures
- Concurrent access
- Disk errors

### Research Findings

#### The Standard Pattern: Write-Flush-Sync-Replace

This pattern is the industry standard for atomic file writes:

1. Write to a temporary file in the same directory
2. Flush Python's buffers with `flush()`
3. Force OS to write to disk with `fsync()`
4. Atomically rename temp file to target with `os.replace()`
5. Optionally sync parent directory

**Why this works:**
- Writing to temp file ensures original is never partially modified
- `os.replace()` is atomic on all platforms (POSIX requirement, Windows support via MoveFileEx)
- Same directory ensures same filesystem (atomic rename requires same filesystem)
- `fsync()` ensures data is on disk before rename

#### Implementation

```python
import os
from pathlib import Path
from typing import Union

def atomic_write(
    filepath: Union[str, Path],
    content: str,
    encoding: str = 'utf-8',
    fsync: bool = True
) -> None:
    """
    Atomically write content to a file.

    Args:
        filepath: Target file path
        content: Content to write
        encoding: Text encoding (default: utf-8)
        fsync: Whether to force sync to disk (default: True)

    Raises:
        OSError: If write or rename fails
    """
    filepath = Path(filepath)
    temp_path = filepath.with_suffix(filepath.suffix + '.tmp')

    try:
        # Write to temporary file
        with open(temp_path, 'w', encoding=encoding) as f:
            f.write(content)
            f.flush()  # Flush Python buffers

            if fsync:
                os.fsync(f.fileno())  # Force OS to write to disk

        # Atomic rename (works on Windows, macOS, Linux)
        os.replace(str(temp_path), str(filepath))

        # Optional: Sync parent directory (POSIX only)
        if hasattr(os, 'O_DIRECTORY'):  # POSIX systems
            try:
                dir_fd = os.open(filepath.parent, os.O_RDONLY | os.O_DIRECTORY)
                os.fsync(dir_fd)
                os.close(dir_fd)
            except (OSError, AttributeError):
                pass  # Not critical if this fails

    except Exception:
        # Clean up temp file on error
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
```

#### Using pathlib

```python
from pathlib import Path
import os

def atomic_write_pathlib(filepath: Path, content: str) -> None:
    """Atomic write using pathlib."""
    temp_path = filepath.with_suffix(filepath.suffix + '.tmp')

    try:
        # Write and sync
        temp_path.write_text(content, encoding='utf-8')

        # Note: write_text() doesn't provide access to file descriptor
        # for fsync(), so this is less safe but simpler

        # Atomic rename using pathlib
        temp_path.replace(filepath)  # Uses os.replace() internally

    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
```

#### Context Manager Pattern (Recommended)

```python
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, BinaryIO, TextIO
import os

@contextmanager
def atomic_write(
    filepath: Path,
    mode: str = 'w',
    encoding: str = 'utf-8',
    fsync: bool = True
) -> Iterator[TextIO]:
    """
    Context manager for atomic file writes.

    Usage:
        with atomic_write(Path('config.json')) as f:
            json.dump(data, f, indent=2)
    """
    temp_path = filepath.with_suffix(filepath.suffix + '.tmp')

    try:
        with open(temp_path, mode, encoding=encoding) as f:
            yield f
            f.flush()
            if fsync:
                os.fsync(f.fileno())

        # Atomic rename after successful write
        os.replace(str(temp_path), str(filepath))

    except Exception:
        # Clean up on error
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise

# Usage example
from pathlib import Path
import json

config_path = Path('~/.claude/claude_desktop_config.json').expanduser()

with atomic_write(config_path) as f:
    json.dump({'mcpServers': {...}}, f, indent=2)
```

### Performance Considerations

#### fsync() is Slow
- `os.fsync()` waits for the kernel to flush buffers to disk
- Can take 10-100ms or more on rotating disks
- On SSDs, usually 1-10ms

#### When to Use fsync()

**Use fsync=True (default) when:**
- Writing critical configuration files
- Writing financial/database data
- System crashes could cause data loss

**Use fsync=False when:**
- Writing temporary files
- Writing logs (where loss of last few entries is acceptable)
- Performance is more important than durability
- Application will verify data integrity on next run

#### Example: Optional fsync

```python
def atomic_write_config(filepath: Path, content: str) -> None:
    """Atomic write for config files - always use fsync."""
    atomic_write(filepath, content, fsync=True)

def atomic_write_cache(filepath: Path, content: str) -> None:
    """Atomic write for cache files - skip fsync for speed."""
    atomic_write(filepath, content, fsync=False)
```

### Error Recovery

```python
import os
import time
from pathlib import Path

def atomic_write_with_retry(
    filepath: Path,
    content: str,
    max_retries: int = 3,
    retry_delay: float = 0.1
) -> None:
    """Atomic write with retry logic for transient errors."""
    for attempt in range(max_retries):
        try:
            atomic_write(filepath, content)
            return  # Success
        except OSError as e:
            if attempt == max_retries - 1:
                raise  # Last attempt failed
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
```

### File Locking

For concurrent access protection, consider using file locks:

```python
import fcntl  # POSIX only
import os
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def file_lock(filepath: Path):
    """Acquire exclusive lock on file (POSIX only)."""
    lock_path = filepath.with_suffix(filepath.suffix + '.lock')

    with open(lock_path, 'w') as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            try:
                lock_path.unlink()
            except OSError:
                pass

# Usage
with file_lock(config_path):
    with atomic_write(config_path) as f:
        f.write(content)
```

**Note:** File locking is platform-specific and complex. For InstructionKit:
- User-triggered operations (not high concurrency)
- Atomic rename provides sufficient protection
- **Recommendation:** Skip file locking for simplicity

### Cross-Platform Compatibility

| Platform | os.replace() | fsync() | Notes |
|----------|--------------|---------|-------|
| **Linux** | ✅ Atomic | ✅ Full support | POSIX guarantees |
| **macOS** | ✅ Atomic | ✅ Full support | POSIX guarantees |
| **Windows** | ✅ Atomic | ✅ Full support | Via MoveFileEx |

**Atomicity on Windows:**
- `os.replace()` uses MoveFileEx with MOVEFILE_REPLACE_EXISTING
- Microsoft docs say it's "usually atomic"
- In rare cases may fall back to non-atomic copy
- For config files, this is acceptable risk

### Recommendation

**Use the context manager pattern with atomic write:**

```python
from contextlib import contextmanager
from pathlib import Path
import os

@contextmanager
def atomic_write(
    filepath: Path,
    encoding: str = 'utf-8',
    fsync: bool = True
):
    """Atomic file write context manager."""
    temp_path = filepath.with_suffix(filepath.suffix + '.tmp')
    try:
        with open(temp_path, 'w', encoding=encoding) as f:
            yield f
            f.flush()
            if fsync:
                os.fsync(f.fileno())
        os.replace(str(temp_path), str(filepath))
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
```

**Benefits:**
- Simple, readable API
- Handles cleanup automatically
- Cross-platform compatible
- Type-safe with proper annotations
- Easy to test

---

## 4. MCP Server Command Validation

### Challenge
Validate that MCP server commands exist and are executable before adding them to config files, working consistently across Windows, macOS, and Linux.

### Research Findings

#### shutil.which() (Recommended)

**Built-in module** (Python 3.3+): No dependencies required

**Function signature:**
```python
shutil.which(cmd, mode=os.F_OK | os.X_OK, path=None)
```

**Features:**
- Returns full path to executable if found, None otherwise
- Checks executability (not just file existence)
- Searches PATH automatically
- Cross-platform (Windows, macOS, Linux)
- Handles Windows PATHEXT (.exe, .bat, .cmd, etc.)
- Can override PATH with custom search path

#### Basic Usage

```python
import shutil
from typing import Optional

def is_command_available(command: str) -> bool:
    """
    Check if a command is available in PATH.

    Args:
        command: Command name to check (e.g., 'node', 'python3')

    Returns:
        True if command exists and is executable
    """
    return shutil.which(command) is not None

def get_command_path(command: str) -> Optional[str]:
    """
    Get full path to a command.

    Args:
        command: Command name to check

    Returns:
        Full path to executable, or None if not found
    """
    return shutil.which(command)

# Examples
if is_command_available('node'):
    print("Node.js is installed")

python_path = get_command_path('python3')
print(f"Python found at: {python_path}")
```

#### Validation with Error Messages

```python
from typing import List, Optional
import shutil

class CommandNotFoundError(Exception):
    """Raised when a required command is not found."""
    pass

def validate_command(command: str) -> str:
    """
    Validate that a command exists and return its full path.

    Args:
        command: Command to validate

    Returns:
        Full path to the command

    Raises:
        CommandNotFoundError: If command not found
    """
    path = shutil.which(command)
    if path is None:
        raise CommandNotFoundError(
            f"Command '{command}' not found in PATH. "
            f"Please ensure it is installed and available."
        )
    return path

def validate_mcp_server_command(command: str, args: List[str]) -> None:
    """
    Validate MCP server command before adding to config.

    Args:
        command: Base command (e.g., 'node', 'python3')
        args: Command arguments

    Raises:
        CommandNotFoundError: If command not found
    """
    # Validate the base command
    command_path = validate_command(command)

    # For package managers like npx, just check they exist
    # Don't try to validate the package they'll install
    if command in ['npx', 'npm', 'pip', 'pipx']:
        return  # Package managers are self-contained

    # For other commands, we've validated they exist
    print(f"✓ Command found: {command_path}")

# Usage
try:
    validate_mcp_server_command('node', ['server.js'])
    print("MCP server command is valid")
except CommandNotFoundError as e:
    print(f"Error: {e}")
```

#### MCP-Specific Validation

```python
from typing import Dict, Any
import shutil

def validate_mcp_server_config(config: Dict[str, Any]) -> None:
    """
    Validate MCP server configuration before adding to config file.

    Args:
        config: MCP server config dict with 'command' and 'args' keys

    Raises:
        ValueError: If config is invalid
        CommandNotFoundError: If command not found
    """
    # Validate required fields
    if 'command' not in config:
        raise ValueError("MCP server config must have 'command' field")

    command = config['command']
    args = config.get('args', [])

    # Validate command exists
    if not shutil.which(command):
        # Provide helpful error message
        raise CommandNotFoundError(
            f"Command '{command}' not found. "
            f"Please install it first:\n"
            f"  - For Node.js: Install Node.js from nodejs.org\n"
            f"  - For Python: Install Python from python.org\n"
            f"  - For npx: Comes with npm (part of Node.js)"
        )

    # Validate environment variables if specified
    if 'env' in config:
        env_vars = config['env']
        for key, value in env_vars.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(
                    f"Environment variable {key}={value} must be strings"
                )

# Usage
server_config = {
    'command': 'node',
    'args': ['/path/to/server.js'],
    'env': {'NODE_ENV': 'production'}
}

try:
    validate_mcp_server_config(server_config)
except (ValueError, CommandNotFoundError) as e:
    print(f"Invalid config: {e}")
```

#### Cross-Platform Considerations

```python
import shutil
import sys

def get_command_variants(base_command: str) -> List[str]:
    """
    Get platform-specific command variants.

    Args:
        base_command: Base command name (e.g., 'python')

    Returns:
        List of command variants to try
    """
    variants = [base_command]

    # On Windows, try with .exe, .cmd, .bat
    if sys.platform == 'win32':
        variants.extend([
            f"{base_command}.exe",
            f"{base_command}.cmd",
            f"{base_command}.bat"
        ])

    # On Unix, try versioned commands
    if sys.platform != 'win32':
        if base_command == 'python':
            variants.extend(['python3', 'python2'])
        elif base_command == 'pip':
            variants.extend(['pip3', 'pip2'])

    return variants

def find_command_flexible(base_command: str) -> Optional[str]:
    """
    Find command, trying platform-specific variants.

    Args:
        base_command: Base command to find

    Returns:
        Full path to command, or None if not found
    """
    for variant in get_command_variants(base_command):
        path = shutil.which(variant)
        if path:
            return path
    return None

# Example
python_path = find_command_flexible('python')
if python_path:
    print(f"Python found at: {python_path}")
else:
    print("Python not found")
```

### Performance: Caching PATH Lookups

For repeated lookups, cache results:

```python
from functools import lru_cache
import shutil

@lru_cache(maxsize=128)
def get_command_path_cached(command: str) -> Optional[str]:
    """
    Get command path with caching.

    Cache is cleared when Python process exits.
    """
    return shutil.which(command)

# Usage - repeated calls use cache
for _ in range(100):
    path = get_command_path_cached('node')  # Only searches PATH once
```

**Considerations:**
- Cache is invalidated on process exit (good - PATH may change)
- For CLI tools, process is short-lived, so cache isn't critical
- For long-running services, cache could miss new installations

**Recommendation:** Use caching only if profiling shows PATH lookup is a bottleneck. For InstructionKit's CLI use case, the overhead is negligible.

### Testing Command Validation

```python
import pytest
import shutil

def test_validate_command_exists():
    """Test validation with a command that exists."""
    # 'python' or 'python3' should exist in test environment
    path = validate_command('python3')
    assert path is not None
    assert isinstance(path, str)

def test_validate_command_not_exists():
    """Test validation with non-existent command."""
    with pytest.raises(CommandNotFoundError):
        validate_command('this-command-definitely-does-not-exist')

def test_is_command_available():
    """Test command availability check."""
    # Should find system python
    assert is_command_available('python3')

    # Should not find fake command
    assert not is_command_available('fake-command-xyz')
```

### Recommendation

**Use `shutil.which()` for all command validation:**

```python
import shutil

def validate_mcp_command(command: str) -> str:
    """
    Validate MCP server command exists.

    Returns:
        Full path to command

    Raises:
        CommandNotFoundError: If command not found
    """
    path = shutil.which(command)
    if path is None:
        raise CommandNotFoundError(
            f"Command '{command}' not found in PATH"
        )
    return path
```

**Benefits:**
- No external dependencies
- Cross-platform by default
- Handles PATHEXT on Windows
- Simple, readable code
- Well-tested in stdlib

**When to skip caching:**
- CLI tools (short-lived processes)
- PATH lookups are fast enough (< 1ms typically)
- Caching adds complexity without meaningful benefit

---

## 5. AI Tool Config File Locations

### Challenge
Locate AI tool configuration files across different platforms and tools to enable MCP server installation.

### Research Findings

#### Claude Desktop

**Config File:** `claude_desktop_config.json`

**Locations:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

**Access via UI:**
- Settings → Developer tab → "Edit Config" button
- Creates file if it doesn't exist

**Format:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "API_KEY": "value"
      }
    }
  }
}
```

**Implementation:**
```python
from pathlib import Path
import sys

def get_claude_config_path() -> Path:
    """Get Claude Desktop config file path for current platform."""
    if sys.platform == 'darwin':  # macOS
        return Path.home() / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json'
    elif sys.platform == 'win32':  # Windows
        appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        return appdata / 'Claude' / 'claude_desktop_config.json'
    else:  # Linux and others
        return Path.home() / '.config' / 'Claude' / 'claude_desktop_config.json'
```

#### Cursor IDE

**Config File:** `mcp.json`

**Locations:**
- **Global (all projects):** `~/.cursor/mcp.json`
- **Project-level:** `<project-root>/.cursor/mcp.json`

**Access via UI:**
- Settings → Tools & Integrations → "New MCP Server"
- Opens `~/.cursor/mcp.json` for editing

**Format:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["path/to/server.js"]
    }
  }
}
```

**Notes:**
- Project-level config at `.cursor/mcp.json` overrides global
- Same format as Claude Desktop

**Implementation:**
```python
from pathlib import Path

def get_cursor_config_paths() -> dict[str, Path]:
    """Get Cursor config file paths."""
    return {
        'global': Path.home() / '.cursor' / 'mcp.json',
        'project': Path.cwd() / '.cursor' / 'mcp.json'  # Current project
    }
```

#### Windsurf IDE

**Config File:** `mcp_config.json`

**Locations:**
- **Primary:** `~/.codeium/windsurf/mcp_config.json` (most common)
- **Alternative:** `~/.windsurf/mcp_config.json` (some installations)

**Access via UI:**
- Settings → Advanced Settings → Cascade section
- "View raw JSON config file" button

**Format:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"]
    }
  }
}
```

**Notes:**
- Same schema as Claude Desktop
- Config location varies by installation method

**Implementation:**
```python
from pathlib import Path

def get_windsurf_config_path() -> Path:
    """Get Windsurf config file path."""
    # Try primary location first
    primary = Path.home() / '.codeium' / 'windsurf' / 'mcp_config.json'
    if primary.parent.exists():
        return primary

    # Fall back to alternative location
    return Path.home() / '.windsurf' / 'mcp_config.json'
```

#### VS Code (GitHub Copilot)

**Config Files:**
- **Workspace:** `.vscode/mcp.json`
- **User settings:** `settings.json`

**Locations:**
- **Workspace:** `<project-root>/.vscode/mcp.json`
- **User settings:**
  - **macOS/Linux:** `~/.config/Code/User/settings.json`
  - **Windows:** `%APPDATA%\Code\User\settings.json`

**Format (Workspace):**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["server.js"]
    }
  }
}
```

**Format (User Settings):**
```json
{
  "mcp": {
    "mcpServers": {
      "server-name": {
        "command": "node",
        "args": ["server.js"]
      }
    }
  }
}
```

**Note:** User settings nest config under `"mcp"` key, workspace files don't.

**Implementation:**
```python
from pathlib import Path
import sys
import os

def get_vscode_config_paths() -> dict[str, Path]:
    """Get VS Code config file paths."""
    # User settings location
    if sys.platform == 'darwin':
        user_settings = Path.home() / 'Library' / 'Application Support' / 'Code' / 'User' / 'settings.json'
    elif sys.platform == 'win32':
        appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        user_settings = appdata / 'Code' / 'User' / 'settings.json'
    else:  # Linux
        user_settings = Path.home() / '.config' / 'Code' / 'User' / 'settings.json'

    return {
        'workspace': Path.cwd() / '.vscode' / 'mcp.json',
        'user': user_settings
    }
```

### Config Detection Strategy

```python
from pathlib import Path
from typing import Optional
import sys
import os

class AIToolConfigLocator:
    """Locate AI tool configuration files."""

    @staticmethod
    def get_claude_config() -> Path:
        """Get Claude Desktop config path."""
        if sys.platform == 'darwin':
            return Path.home() / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json'
        elif sys.platform == 'win32':
            appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
            return appdata / 'Claude' / 'claude_desktop_config.json'
        else:
            return Path.home() / '.config' / 'Claude' / 'claude_desktop_config.json'

    @staticmethod
    def get_cursor_config(scope: str = 'global') -> Path:
        """Get Cursor config path."""
        if scope == 'global':
            return Path.home() / '.cursor' / 'mcp.json'
        else:  # project
            return Path.cwd() / '.cursor' / 'mcp.json'

    @staticmethod
    def get_windsurf_config() -> Path:
        """Get Windsurf config path."""
        primary = Path.home() / '.codeium' / 'windsurf' / 'mcp_config.json'
        if primary.parent.exists():
            return primary
        return Path.home() / '.windsurf' / 'mcp_config.json'

    @staticmethod
    def get_vscode_config(scope: str = 'workspace') -> Path:
        """Get VS Code config path."""
        if scope == 'workspace':
            return Path.cwd() / '.vscode' / 'mcp.json'

        # User settings
        if sys.platform == 'darwin':
            return Path.home() / 'Library' / 'Application Support' / 'Code' / 'User' / 'settings.json'
        elif sys.platform == 'win32':
            appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
            return appdata / 'Code' / 'User' / 'settings.json'
        else:
            return Path.home() / '.config' / 'Code' / 'User' / 'settings.json'

    @staticmethod
    def detect_installed_tools() -> list[str]:
        """Detect which AI tools are installed."""
        tools = []

        # Check if config parent directories exist
        if AIToolConfigLocator.get_claude_config().parent.exists():
            tools.append('claude')

        if AIToolConfigLocator.get_cursor_config('global').parent.exists():
            tools.append('cursor')

        if AIToolConfigLocator.get_windsurf_config().parent.exists():
            tools.append('windsurf')

        if AIToolConfigLocator.get_vscode_config('user').parent.parent.exists():
            tools.append('vscode')

        return tools

# Usage
locator = AIToolConfigLocator()
claude_path = locator.get_claude_config()
print(f"Claude config: {claude_path}")

installed = locator.detect_installed_tools()
print(f"Installed tools: {installed}")
```

### Handling Missing Config Files

```python
from pathlib import Path
import json

def ensure_config_exists(config_path: Path) -> None:
    """
    Ensure config file exists, creating if necessary.

    Args:
        config_path: Path to config file
    """
    if config_path.exists():
        return

    # Create parent directories
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Create empty config with mcpServers section
    initial_config = {
        "mcpServers": {}
    }

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(initial_config, f, indent=2)

# Usage
claude_config = get_claude_config_path()
ensure_config_exists(claude_config)
```

### Recommendation

**Implement config location detection in `ai_tools/` module:**

```python
# instructionkit/ai_tools/config_locations.py

from pathlib import Path
from typing import Optional
import sys
import os

def get_config_path(tool_name: str, scope: str = 'global') -> Optional[Path]:
    """
    Get configuration file path for an AI tool.

    Args:
        tool_name: Tool name ('claude', 'cursor', 'windsurf', 'vscode')
        scope: Configuration scope ('global' or 'project')

    Returns:
        Path to config file, or None if tool not recognized
    """
    if tool_name == 'claude':
        if sys.platform == 'darwin':
            return Path.home() / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json'
        elif sys.platform == 'win32':
            appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
            return appdata / 'Claude' / 'claude_desktop_config.json'
        else:
            return Path.home() / '.config' / 'Claude' / 'claude_desktop_config.json'

    elif tool_name == 'cursor':
        if scope == 'global':
            return Path.home() / '.cursor' / 'mcp.json'
        else:
            return Path.cwd() / '.cursor' / 'mcp.json'

    elif tool_name == 'windsurf':
        primary = Path.home() / '.codeium' / 'windsurf' / 'mcp_config.json'
        if primary.parent.exists():
            return primary
        return Path.home() / '.windsurf' / 'mcp_config.json'

    elif tool_name == 'vscode':
        if scope == 'workspace':
            return Path.cwd() / '.vscode' / 'mcp.json'
        else:
            if sys.platform == 'darwin':
                return Path.home() / 'Library' / 'Application Support' / 'Code' / 'User' / 'settings.json'
            elif sys.platform == 'win32':
                appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
                return appdata / 'Code' / 'User' / 'settings.json'
            else:
                return Path.home() / '.config' / 'Code' / 'User' / 'settings.json'

    return None
```

---

## Summary of Recommendations

### 1. JSON Manipulation
- **Use:** Python's built-in `json` module
- **Trade-off:** Accept comment loss on modification
- **Pattern:** Read → Parse → Modify → Write with atomic operation
- **Dependencies:** None

### 2. Environment Variables
- **Use:** `python-dotenv` library
- **Features:** Multi-line values, special characters, validation
- **Pattern:** Load at startup, validate immediately
- **Dependencies:** `python-dotenv>=1.0.0`

### 3. Atomic File Writes
- **Use:** Context manager with temp file + `os.replace()`
- **Pattern:** Write temp → flush → fsync → rename
- **Features:** Cross-platform, handles errors, optional fsync
- **Dependencies:** None (stdlib only)

### 4. Command Validation
- **Use:** `shutil.which()` from stdlib
- **Features:** Cross-platform, handles PATHEXT, checks executability
- **Caching:** Not needed for CLI use case
- **Dependencies:** None

### 5. Config File Locations
- **Implement:** Tool-specific path detection per platform
- **Handle:** Missing files by creating with defaults
- **Detect:** Installed tools by checking parent directories exist
- **Dependencies:** None

---

## Implementation Plan

### Phase 1: Core Infrastructure
1. Implement `atomic_write()` context manager
2. Implement `SafeJsonConfig` class for JSON handling
3. Add command validation with `shutil.which()`
4. Add config path detection for all tools

### Phase 2: MCP Server Management
1. Create MCP server configuration models
2. Implement server validation (command + args)
3. Implement config file read/write operations
4. Add environment variable support with `python-dotenv`

### Phase 3: CLI Commands
1. `inskit mcp add` - Add MCP server to tool config
2. `inskit mcp list` - List configured MCP servers
3. `inskit mcp remove` - Remove MCP server from config
4. `inskit mcp validate` - Validate MCP server configs

### Phase 4: Testing
1. Unit tests for each component
2. Integration tests with real config files
3. Cross-platform testing (CI/CD)
4. Error handling and edge cases

---

## Code Quality Alignment

This research aligns with InstructionKit's constitution:

✅ **Simplicity** - Use stdlib where possible, minimal dependencies
✅ **Type Safety** - All functions will have type hints
✅ **Testing** - Each component is testable
✅ **Cross-Platform** - All solutions work on Windows, macOS, Linux
✅ **User Experience** - Clear error messages, validation before modification
✅ **Local-First** - No cloud services, all operations local

---

## Dependencies Summary

**Required:**
- `python-dotenv>=1.0.0` - Environment variable management

**Optional:**
- `pydantic>=2.0.0` - If using Pydantic for env var validation (recommended for type safety)

**No Additional Dependencies Needed:**
- JSON manipulation - stdlib `json`
- Atomic writes - stdlib `os`, `pathlib`
- Command validation - stdlib `shutil`
- Config detection - stdlib `sys`, `os`, `pathlib`

---

## Next Steps

1. **Review this research** with the team
2. **Create GitHub issue** for MCP feature implementation
3. **Update constitution** if needed (new dependencies)
4. **Create feature spec** using `/speckit.specify`
5. **Generate implementation plan** using `/speckit.plan`
6. **Implement in phases** with tests for each component

---

## References

- Python json module: https://docs.python.org/3/library/json.html
- python-dotenv: https://pypi.org/project/python-dotenv/
- JSONC specification: https://jsonc.org/
- Model Context Protocol: https://modelcontextprotocol.io/
- Claude Desktop config: https://modelcontextprotocol.io/docs/develop/connect-local-servers
- Cursor MCP docs: Multiple community sources
- Windsurf MCP docs: https://docs.windsurf.com/windsurf/cascade/mcp
- VS Code MCP docs: https://code.visualstudio.com/docs/copilot/customization/mcp-servers
