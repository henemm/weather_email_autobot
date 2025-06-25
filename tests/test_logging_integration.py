"""
Integration tests for logging functionality across main modules.
"""

import tempfile
import os
from datetime import datetime
from unittest.mock import patch

import pytest

from src.utils.logging_setup import setup_logging, get_logger
from src.wetter.analyse import analysiere_regen_risiko, RegenRisiko, WetterDaten
from src.logic.report_scheduler import ReportScheduler, should_send_scheduled_report


class TestLoggingIntegration:
    """Test logging integration across main modules."""
    
    def test_weather_analysis_logging(self):
        """Test that weather analysis functions produce expected log entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            setup_logging(log_level="DEBUG", log_file=log_file, console_output=False)
            
            # Create test weather data
            wetter_daten = [
                WetterDaten(
                    datum=datetime.now(),
                    temperatur=20.0,
                    niederschlag_prozent=80.0,  # High rain probability
                    niederschlag_mm=5.0,  # High rain amount
                    wind_geschwindigkeit=35.0,  # High wind
                    luftfeuchtigkeit=85.0  # High humidity
                )
            ]
            
            config = {
                "schwellen": {
                    "regen": 25,
                    "regenmenge": 2
                }
            }
            
            # Run analysis
            result = analysiere_regen_risiko(wetter_daten, config)
            
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Check for expected log entries
            assert "Starting rain risk analysis" in log_content
            assert "Using thresholds" in log_content
            assert "High rain probability detected" in log_content
            assert "High rain amount detected" in log_content
            assert "High wind speed detected" in log_content
            assert "High humidity detected" in log_content
            assert "Rain risk analysis completed" in log_content
            assert "src.wetter.analyse" in log_content
    
    def test_report_scheduler_logging(self):
        """Test that report scheduler produces expected log entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            setup_logging(log_file=log_file, console_output=False)
            
            # Create test config
            config = {
                "send_schedule": {
                    "morning_time": "04:30",
                    "evening_time": "19:00"
                },
                "dynamic_reports": {
                    "risk_threshold": 0.3,
                    "min_interval_minutes": 60,
                    "max_daily": 5
                }
            }
            
            state_file = os.path.join(temp_dir, "state.json")
            scheduler = ReportScheduler(state_file, config)
            
            # Test scheduled report check
            test_time = datetime(2025, 1, 1, 4, 30)  # Morning time
            should_send = should_send_scheduled_report(test_time, config)
            
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Check for expected log entries
            assert "Report scheduler initialized" in log_content
            assert "State file" in log_content
            assert "Scheduled report time matched" in log_content
            assert "src.logic.report_scheduler" in log_content
    
    def test_logging_format_consistency(self):
        """Test that all modules use consistent logging format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            setup_logging(log_file=log_file, console_output=False)
            
            logger = get_logger("test_module")
            logger.info("Test message")
            
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
            
            # Check format consistency
            for line in log_lines:
                if line.strip() and not line.startswith('#'):
                    # Should follow format: [timestamp] [module] [level] message
                    parts = line.strip().split("] [")
                    assert len(parts) >= 3, f"Invalid log format: {line.strip()}"
                    
                    # Check timestamp format
                    timestamp_part = parts[0]
                    assert timestamp_part.startswith("[")
                    assert ":" in timestamp_part
                    
                    # Check module name (with src prefix)
                    module_name = parts[1]
                    assert any(name in module_name for name in ["test_module", "src.wetter.analyse", "src.logic.report_scheduler", "src.utils.logging_setup"])
                    
                    # Check level
                    assert any(level in parts[2] for level in ["INFO", "WARNING", "ERROR", "DEBUG"])
    
    def test_error_logging(self):
        """Test that errors are properly logged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            setup_logging(log_file=log_file, console_output=False)
            
            logger = get_logger("test_module")
            
            # Test error logging
            try:
                raise ValueError("Test error")
            except ValueError as e:
                logger.error(f"Caught error: {e}")
            
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Check for error log entry
            assert "Caught error: Test error" in log_content
            assert "[ERROR]" in log_content
    
    def test_warning_logging(self):
        """Test that warnings are properly logged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            setup_logging(log_file=log_file, console_output=False)
            
            logger = get_logger("test_module")
            
            # Test warning logging
            logger.warning("Test warning message")
            
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Check for warning log entry
            assert "Test warning message" in log_content
            assert "[WARNING]" in log_content 