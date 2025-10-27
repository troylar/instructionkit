"""Tests for __main__ entry point."""

import subprocess
import sys


def test_main_module_execution() -> None:
    """Test that the module can be executed as python -m instructionkit."""
    result = subprocess.run(
        [sys.executable, "-m", "instructionkit", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert "inskit" in result.stdout.lower() or "instructionkit" in result.stdout.lower()


def test_main_module_version() -> None:
    """Test that version command works through module entry point."""
    result = subprocess.run(
        [sys.executable, "-m", "instructionkit", "version"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    # Should output version number
    assert any(char.isdigit() for char in result.stdout)
