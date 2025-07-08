"""
Tests for SMS configuration processor.

This module tests the functionality to process incoming SMS commands
and update configuration values in config.yaml.
"""

import pytest
import tempfile
import os
import yaml
from datetime import datetime
from unittest.mock import patch, mock_open
from src.config.sms_config_processor import SMSConfigProcessor


class TestSMSConfigProcessor:
    """Test cases for SMS configuration processor."""

    def test_process_sms_command_valid_format(self):
        """Test processing a valid SMS command format."""
        processor = SMSConfigProcessor("config.yaml")
        
        # Test valid command
        result = processor.process_sms_command("### thresholds.temperature: 25.0")
        
        assert result["success"] is True
        assert result["key"] == "thresholds.temperature"
        assert result["value"] == 25.0
        assert result["message"] == "Configuration updated successfully"

    def test_process_sms_command_invalid_format(self):
        """Test processing an invalid SMS command format."""
        processor = SMSConfigProcessor("config.yaml")
        
        # Test invalid command (no ### prefix)
        result = processor.process_sms_command("thresholds.temperature: 25.0")
        
        assert result["success"] is False
        assert result["message"] == "INVALID FORMAT: Command must start with ###"

    def test_process_sms_command_missing_colon(self):
        """Test processing SMS command without colon separator."""
        processor = SMSConfigProcessor("config.yaml")
        
        result = processor.process_sms_command("### thresholds.temperature 25.0")
        
        assert result["success"] is False
        assert result["message"] == "INVALID FORMAT: Missing colon separator"

    def test_process_sms_command_empty_value(self):
        """Test processing SMS command with empty value."""
        processor = SMSConfigProcessor("config.yaml")
        
        result = processor.process_sms_command("### thresholds.temperature: ")
        
        assert result["success"] is False
        assert result["message"] == "INVALID FORMAT: Empty value"

    def test_process_sms_command_whitelist_violation(self):
        """Test processing SMS command with non-whitelisted key."""
        processor = SMSConfigProcessor("config.yaml")
        
        result = processor.process_sms_command("### smtp.host: smtp.gmail.com")
        
        assert result["success"] is False
        assert result["message"] == "INVALID FORMAT: Key 'smtp.host' not in whitelist"

    def test_process_sms_command_invalid_date_format(self):
        """Test processing SMS command with invalid date format."""
        processor = SMSConfigProcessor("config.yaml")
        
        result = processor.process_sms_command("### startdatum: 2025/07/07")
        
        assert result["success"] is False
        assert result["message"] == "INVALID FORMAT: Invalid date value for startdatum"

    def test_process_sms_command_valid_date_format(self):
        """Test processing SMS command with valid date format."""
        processor = SMSConfigProcessor("config.yaml")
        
        result = processor.process_sms_command("### startdatum: 2025-07-08")
        
        assert result["success"] is True
        assert result["key"] == "startdatum"
        assert result["value"] == "2025-07-08"

    def test_process_sms_command_invalid_float(self):
        """Test processing SMS command with invalid float value."""
        processor = SMSConfigProcessor("config.yaml")
        
        result = processor.process_sms_command("### thresholds.temperature: invalid")
        
        assert result["success"] is False
        assert result["message"] == "INVALID FORMAT: Invalid float value for thresholds.temperature"

    def test_process_sms_command_invalid_integer(self):
        """Test processing SMS command with invalid integer value."""
        processor = SMSConfigProcessor("config.yaml")
        
        result = processor.process_sms_command("### max_daily_reports: 3.5")
        
        assert result["success"] is False
        assert result["message"] == "INVALID FORMAT: Invalid integer value for max_daily_reports"

    def test_process_sms_command_valid_phone_number(self):
        """Test processing SMS command with valid phone number."""
        processor = SMSConfigProcessor("config.yaml")
        
        result = processor.process_sms_command("### sms.test_number: +49123456789")
        
        assert result["success"] is True
        assert result["key"] == "sms.test_number"
        assert result["value"] == "+49123456789"

    def test_process_sms_command_invalid_phone_number(self):
        """Test processing SMS command with invalid phone number."""
        processor = SMSConfigProcessor("config.yaml")
        
        result = processor.process_sms_command("### sms.test_number: invalid")
        
        assert result["success"] is False
        assert result["message"] == "INVALID FORMAT: Invalid phone_number value for sms.test_number"

    def test_validate_key_whitelist(self):
        """Test key validation against whitelist."""
        processor = SMSConfigProcessor("config.yaml")
        
        # Valid keys
        assert processor._validate_key("startdatum") is True
        assert processor._validate_key("sms.production_number") is True
        assert processor._validate_key("thresholds.temperature") is True
        assert processor._validate_key("delta_thresholds.rain_probability") is True
        assert processor._validate_key("max_daily_reports") is True
        assert processor._validate_key("min_interval_min") is True
        
        # Invalid keys
        assert processor._validate_key("smtp.host") is False
        assert processor._validate_key("debug.enabled") is False
        assert processor._validate_key("invalid.key") is False

    def test_validate_value_type(self):
        """Test value type validation."""
        processor = SMSConfigProcessor("config.yaml")
        
        # Date validation
        assert processor._validate_value_type("startdatum", "2025-07-07") is True
        assert processor._validate_value_type("startdatum", "2025/07/07") is False
        assert processor._validate_value_type("startdatum", "invalid") is False
        
        # Phone number validation
        assert processor._validate_value_type("sms.test_number", "+49123456789") is True
        assert processor._validate_value_type("sms.production_number", "+49987654321") is True
        assert processor._validate_value_type("sms.test_number", "invalid") is False
        
        # Float validation
        assert processor._validate_value_type("thresholds.temperature", "25.0") is True
        assert processor._validate_value_type("thresholds.temperature", "25") is True
        assert processor._validate_value_type("thresholds.temperature", "invalid") is False
        
        # Integer validation
        assert processor._validate_value_type("max_daily_reports", "3") is True
        assert processor._validate_value_type("max_daily_reports", "3.5") is False
        assert processor._validate_value_type("max_daily_reports", "invalid") is False

    @patch('builtins.open', new_callable=mock_open, read_data='')
    @patch('yaml.safe_load')
    @patch('yaml.dump')
    def test_update_config_file_success(self, mock_yaml_dump, mock_yaml_load, mock_file):
        """Test successful configuration file update."""
        # Mock existing config
        mock_config = {
            "thresholds": {
                "temperature": 30.0
            }
        }
        mock_yaml_load.return_value = mock_config
        
        processor = SMSConfigProcessor("config.yaml")
        result = processor._update_config_file("thresholds.temperature", 25.0)
        
        assert result is True
        mock_yaml_dump.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='')
    @patch('yaml.safe_load')
    def test_update_config_file_yaml_error(self, mock_yaml_load, mock_file):
        """Test configuration file update with YAML error."""
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")
        
        processor = SMSConfigProcessor("config.yaml")
        result = processor._update_config_file("thresholds.temperature", 25.0)
        
        assert result is False

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_update_config_file_file_not_found(self, mock_file):
        """Test configuration file update with file not found."""
        processor = SMSConfigProcessor("config.yaml")
        result = processor._update_config_file("thresholds.temperature", 25.0)
        
        assert result is False

    def test_log_config_update(self):
        """Test logging of configuration updates."""
        processor = SMSConfigProcessor("config.yaml")
        
        # Test successful update logging
        result = processor._log_config_update(
            "thresholds.temperature", 25.0, True, "Success"
        )
        
        assert result is True

    def test_log_config_update_failure(self):
        """Test logging of configuration update failures."""
        processor = SMSConfigProcessor("config.yaml")
        
        # Test failed update logging
        result = processor._log_config_update(
            "invalid.key", "invalid", False, "INVALID FORMAT"
        )
        
        assert result is True


class TestSMSConfigProcessorIntegration:
    """Integration tests for SMS configuration processor."""

    def test_full_command_processing_workflow(self):
        """Test complete workflow of processing a valid SMS command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            # Create temporary config file
            config_content = """
thresholds:
  temperature: 30.0
  rain_probability: 10.0
sms:
  test_number: "+49123456789"
  production_number: "+49987654321"
max_daily_reports: 3
"""
            temp_file.write(config_content)
            temp_file.flush()
            
            try:
                processor = SMSConfigProcessor(temp_file.name)
                
                # Process a valid command
                result = processor.process_sms_command("### thresholds.temperature: 25.0")
                
                assert result["success"] is True
                assert result["key"] == "thresholds.temperature"
                assert result["value"] == 25.0
                
                # Verify the file was actually updated
                with open(temp_file.name, 'r') as f:
                    updated_config = yaml.safe_load(f)
                
                assert updated_config["thresholds"]["temperature"] == 25.0
                
            finally:
                os.unlink(temp_file.name)

    def test_multiple_commands_processing(self):
        """Test processing multiple SMS commands."""
        processor = SMSConfigProcessor("config.yaml")
        
        commands = [
            "### thresholds.temperature: 25.0",
            "### thresholds.rain_probability: 15.0",
            "### max_daily_reports: 5"
        ]
        
        results = []
        for command in commands:
            result = processor.process_sms_command(command)
            results.append(result)
        
        # All commands should be valid
        assert all(result["success"] for result in results)
        assert len(results) == 3

    def test_mixed_valid_invalid_commands(self):
        """Test processing mix of valid and invalid commands."""
        processor = SMSConfigProcessor("config.yaml")
        
        commands = [
            "### thresholds.temperature: 25.0",  # Valid
            "thresholds.rain_probability: 15.0",  # Invalid (no ###)
            "### smtp.host: smtp.gmail.com",      # Invalid (not in whitelist)
            "### max_daily_reports: 5"            # Valid
        ]
        
        results = []
        for command in commands:
            result = processor.process_sms_command(command)
            results.append(result)
        
        # Only first and last should be valid
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert results[2]["success"] is False
        assert results[3]["success"] is True 