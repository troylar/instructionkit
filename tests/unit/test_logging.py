"""Tests for logging configuration."""

import logging
from pathlib import Path

from aiconfigkit.utils.logging import get_logger, setup_logging


def test_setup_logging_default() -> None:
    """Test logging setup with default configuration."""
    setup_logging()
    logger = logging.getLogger()
    assert logger.level == logging.INFO


def test_setup_logging_debug_level() -> None:
    """Test logging setup with DEBUG level."""
    setup_logging(level="DEBUG")
    logger = logging.getLogger()
    assert logger.level == logging.DEBUG


def test_setup_logging_warning_level() -> None:
    """Test logging setup with WARNING level."""
    setup_logging(level="WARNING")
    logger = logging.getLogger()
    assert logger.level == logging.WARNING


def test_setup_logging_error_level() -> None:
    """Test logging setup with ERROR level."""
    setup_logging(level="ERROR")
    logger = logging.getLogger()
    assert logger.level == logging.ERROR


def test_setup_logging_critical_level() -> None:
    """Test logging setup with CRITICAL level."""
    setup_logging(level="CRITICAL")
    logger = logging.getLogger()
    assert logger.level == logging.CRITICAL


def test_setup_logging_invalid_level() -> None:
    """Test logging setup with invalid level defaults to INFO."""
    setup_logging(level="INVALID")
    logger = logging.getLogger()
    assert logger.level == logging.INFO


def test_setup_logging_with_file(tmp_path: Path) -> None:
    """Test logging setup with file output."""
    log_file = tmp_path / "logs" / "test.log"
    setup_logging(level="INFO", log_file=log_file)

    # Log file parent directory should be created
    assert log_file.parent.exists()

    # Test that logging to file works
    logger = logging.getLogger("test")
    logger.info("Test message")

    assert log_file.exists()
    content = log_file.read_text()
    assert "Test message" in content


def test_setup_logging_custom_format(tmp_path: Path) -> None:
    """Test logging setup with custom format string."""
    log_file = tmp_path / "test.log"
    custom_format = "%(levelname)s - %(message)s"
    setup_logging(level="INFO", log_file=log_file, format_string=custom_format)

    logger = logging.getLogger("test")
    logger.info("Custom format test")

    content = log_file.read_text()
    assert "Custom format test" in content


def test_setup_logging_case_insensitive() -> None:
    """Test that log level is case insensitive."""
    setup_logging(level="info")
    logger = logging.getLogger()
    assert logger.level == logging.INFO

    setup_logging(level="Debug")
    assert logger.level == logging.DEBUG


def test_get_logger() -> None:
    """Test getting a logger instance."""
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_get_logger_different_names() -> None:
    """Test that different names return different logger instances."""
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    assert logger1.name != logger2.name
    assert logger1.name == "module1"
    assert logger2.name == "module2"


def test_get_logger_same_name() -> None:
    """Test that same name returns the same logger instance."""
    logger1 = get_logger("same_module")
    logger2 = get_logger("same_module")
    assert logger1 is logger2


def test_setup_logging_console_handler() -> None:
    """Test that console handler is configured."""
    setup_logging(level="INFO")
    logger = logging.getLogger()

    # Should have at least one handler (console)
    assert len(logger.handlers) > 0

    # Check for StreamHandler
    has_console_handler = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    assert has_console_handler


def test_setup_logging_multiple_handlers(tmp_path: Path) -> None:
    """Test that both console and file handlers are configured."""
    log_file = tmp_path / "test.log"
    setup_logging(level="INFO", log_file=log_file)
    logger = logging.getLogger()

    # Should have both console and file handlers
    handler_types = [type(h) for h in logger.handlers]
    assert logging.StreamHandler in handler_types
    assert logging.FileHandler in handler_types
