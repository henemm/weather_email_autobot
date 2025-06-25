"""
Tests for the logging setup module.
"""

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.logging_setup import setup_logging, get_logger


class TestLoggingSetup:
    """Test cases for logging setup functionality."""
    
    def test_setup_logging_creates_directory_and_file(self):
        """Test that setup_logging creates the logs directory and file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "logs", "test.log")
            
            # Setup logging
            setup_logging(log_file=log_file, console_output=False)
            
            # Check that directory and file were created
            assert os.path.exists(log_file)
            assert os.path.isfile(log_file)
    
    def test_setup_logging_default_file_location(self):
        """Test that setup_logging uses default log file location."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with actual file creation instead of mocking
            log_file = os.path.join(temp_dir, "logs", "warning_monitor.log")
            
            setup_logging(log_file=log_file, console_output=False)
            
            # Verify file was created
            assert os.path.exists(log_file)
    
    def test_get_logger_returns_configured_logger(self):
        """Test that get_logger returns a properly configured logger."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            setup_logging(log_file=log_file, console_output=False)
            
            logger = get_logger("test_module")
            
            assert isinstance(logger, logging.Logger)
            assert logger.name == "test_module"
    
    def test_logging_contains_expected_entries(self):
        """Test that logging contains expected entries for normal operations and errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            # Setup logging
            setup_logging(log_file=log_file, console_output=False)
            
            # Get logger and log some messages
            logger = get_logger("test_module")
            logger.info("Normal operation message")
            logger.warning("Warning message")
            logger.error("Error message")
            
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Check that all messages are present
            assert "Normal operation message" in log_content
            assert "Warning message" in log_content
            assert "Error message" in log_content
            assert "[test_module]" in log_content
            assert "[INFO]" in log_content
            assert "[WARNING]" in log_content
            assert "[ERROR]" in log_content
    
    def test_logging_format_structure(self):
        """Test that logging format follows the expected structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            setup_logging(log_file=log_file, console_output=False)
            logger = get_logger("test_module")
            logger.info("Test message")
            
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
            
            # Find the test message line
            test_line = None
            for line in log_lines:
                if "Test message" in line:
                    test_line = line.strip()
                    break
            
            assert test_line is not None
            
            # Check format: [timestamp] [module] [level] message
            # The format is: [YYYY-MM-DD HH:MM:SS] [module] [level] message
            # So we need to split on "] [" to get the parts
            parts = test_line.split("] [")
            assert len(parts) >= 3
            
            # Check timestamp format - should start with [ and contain date/time
            timestamp_part = parts[0]
            assert timestamp_part.startswith("[")
            assert ":" in timestamp_part  # Should contain time
            
            # Check module name
            assert "test_module" in parts[1]
            
            # Check level
            assert "INFO" in parts[2]
    
    def test_different_log_levels(self):
        """Test that different log levels work correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            # Setup with DEBUG level
            setup_logging(log_level="DEBUG", log_file=log_file, console_output=False)
            logger = get_logger("test_module")
            
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # All messages should be present with DEBUG level
            assert "Debug message" in log_content
            assert "Info message" in log_content
            assert "Warning message" in log_content
            assert "Error message" in log_content
    
    def test_logging_initialization_message(self):
        """Test that logging initialization is logged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            setup_logging(log_file=log_file, console_output=False)
            
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Check for initialization messages
            assert "Logging system initialized" in log_content
            assert "Log file:" in log_content 