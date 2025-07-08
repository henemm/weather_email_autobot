"""
SMS Configuration Processor.

This module provides functionality to process incoming SMS commands
and update configuration values in config.yaml based on a predefined
whitelist of allowed keys and value types.
"""

import yaml
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import os # Added for backup file handling

logger = logging.getLogger(__name__)


class SMSConfigProcessor:
    """
    Processor for SMS-based configuration updates.
    
    This class handles incoming SMS commands in the format "### <key>: <value>"
    and updates the corresponding values in config.yaml if they are in the
    whitelist and pass type validation.
    """
    
    def __init__(self, config_file_path: str = "config.yaml"):
        """
        Initialize the SMS configuration processor.
        
        Args:
            config_file_path: Path to the configuration file to update
        """
        self.config_file_path = config_file_path
        
        # Whitelist of allowed configuration keys
        self.whitelist = [
            "startdatum",
            "sms.enabled",
            "sms.mode",
            "sms.production_number",
            "sms.test_number",
            "thresholds.cloud_cover",
            "thresholds.rain_amount",
            "thresholds.rain_probability",
            "thresholds.temperature",
            "thresholds.thunderstorm_probability",
            "thresholds.wind_speed",
            "delta_thresholds.rain_probability",
            "delta_thresholds.temperature",
            "delta_thresholds.thunderstorm_probability",
            "delta_thresholds.wind_speed",
            "max_daily_reports",
            "min_interval_min"
        ]
        
        # Type validation rules
        self.type_rules = {
            "startdatum": "date",
            "sms.enabled": "boolean",
            "sms.mode": "sms_mode",
            "sms.production_number": "phone_number",
            "sms.test_number": "phone_number",
            "thresholds.cloud_cover": "float",
            "thresholds.rain_amount": "float",
            "thresholds.rain_probability": "float",
            "thresholds.temperature": "float",
            "thresholds.thunderstorm_probability": "float",
            "thresholds.wind_speed": "float",
            "delta_thresholds.rain_probability": "float",
            "delta_thresholds.temperature": "float",
            "delta_thresholds.thunderstorm_probability": "float",
            "delta_thresholds.wind_speed": "float",
            "max_daily_reports": "integer",
            "min_interval_min": "integer"
        }
    
    def process_sms_command(self, sms_text: str) -> Dict[str, Any]:
        """
        Process an incoming SMS command and update configuration if valid.
        
        Args:
            sms_text: The SMS text to process
            
        Returns:
            Dictionary containing:
                - success: Boolean indicating if update was successful
                - key: The configuration key that was updated (if successful)
                - value: The new value (if successful)
                - message: Human-readable message about the result
        """
        try:
            # Check if SMS starts with ###
            if not sms_text.startswith("### "):
                return {
                    "success": False,
                    "key": None,
                    "value": None,
                    "message": "INVALID FORMAT: Command must start with ###"
                }
            
            # Extract key and value
            command_part = sms_text[4:].strip()  # Remove "### "
            
            if ":" not in command_part:
                return {
                    "success": False,
                    "key": None,
                    "value": None,
                    "message": "INVALID FORMAT: Missing colon separator"
                }
            
            key, value = command_part.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            if not value:
                return {
                    "success": False,
                    "key": None,
                    "value": None,
                    "message": "INVALID FORMAT: Empty value"
                }
            
            # Validate key is in whitelist
            if not self._validate_key(key):
                return {
                    "success": False,
                    "key": None,
                    "value": None,
                    "message": f"INVALID FORMAT: Key '{key}' not in whitelist"
                }
            
            # Validate value type
            if not self._validate_value_type(key, value):
                expected_type = self.type_rules.get(key, "unknown")
                return {
                    "success": False,
                    "key": None,
                    "value": None,
                    "message": f"INVALID FORMAT: Invalid {expected_type} value for {key}"
                }
            
            # Convert value to appropriate type
            converted_value = self._convert_value(key, value)
            
            # Update configuration file
            if self._update_config_file(key, converted_value):
                # Log the successful update
                self._log_config_update(key, converted_value, True, "Configuration updated successfully")
                
                return {
                    "success": True,
                    "key": key,
                    "value": converted_value,
                    "message": "Configuration updated successfully"
                }
            else:
                # Log the failed update
                self._log_config_update(key, converted_value, False, "Failed to update configuration file")
                
                return {
                    "success": False,
                    "key": None,
                    "value": None,
                    "message": "Failed to update configuration file"
                }
                
        except Exception as e:
            logger.error(f"Error processing SMS command '{sms_text}': {e}")
            return {
                "success": False,
                "key": None,
                "value": None,
                "message": f"Error processing command: {str(e)}"
            }
    
    def _validate_key(self, key: str) -> bool:
        """
        Validate that the key is in the whitelist.
        
        Args:
            key: The configuration key to validate
            
        Returns:
            True if key is in whitelist, False otherwise
        """
        return key in self.whitelist
    
    def _validate_value_type(self, key: str, value: str) -> bool:
        """
        Validate that the value matches the expected type for the key.
        
        Args:
            key: The configuration key
            value: The value to validate
            
        Returns:
            True if value is valid for the key type, False otherwise
        """
        expected_type = self.type_rules.get(key)
        if not expected_type:
            return False
        
        if expected_type == "date":
            return self._is_valid_date(value)
        elif expected_type == "phone_number":
            return self._is_valid_phone_number(value)
        elif expected_type == "float":
            return self._is_valid_float(value)
        elif expected_type == "integer":
            return self._is_valid_integer(value)
        elif expected_type == "boolean":
            return self._is_valid_boolean(value)
        elif expected_type == "sms_mode":
            return value in ["test", "production"]
        else:
            return False
    
    def _is_valid_date(self, value: str) -> bool:
        """
        Check if value is a valid date in YYYY-MM-DD format.
        
        Args:
            value: The date string to validate
            
        Returns:
            True if valid date format, False otherwise
        """
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _is_valid_phone_number(self, value: str) -> bool:
        """
        Check if value is a valid phone number format.
        
        Args:
            value: The phone number string to validate
            
        Returns:
            True if valid phone number format, False otherwise
        """
        # Basic phone number validation: starts with + and contains only digits
        return bool(re.match(r'^\+[0-9]+$', value))
    
    def _is_valid_float(self, value: str) -> bool:
        """
        Check if value is a valid float.
        
        Args:
            value: The string to validate as float
            
        Returns:
            True if valid float, False otherwise
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _is_valid_integer(self, value: str) -> bool:
        """
        Check if value is a valid integer.
        
        Args:
            value: The string to validate as integer
            
        Returns:
            True if valid integer, False otherwise
        """
        try:
            int_value = int(value)
            # Check that it's actually an integer (no decimal part)
            return float(int_value) == float(value)
        except ValueError:
            return False
    
    def _is_valid_boolean(self, value: str) -> bool:
        """
        Check if value is a valid boolean (True or False).
        
        Args:
            value: The string to validate as boolean
            
        Returns:
            True if valid boolean, False otherwise
        """
        return value.lower() in ["true", "false"]
    
    def _convert_value(self, key: str, value: str) -> Any:
        """
        Convert value string to appropriate type based on key.
        
        Args:
            key: The configuration key
            value: The value string to convert
            
        Returns:
            Converted value of appropriate type
        """
        expected_type = self.type_rules.get(key)
        
        if expected_type == "date":
            return value  # Keep as string for YAML
        elif expected_type == "phone_number":
            return value  # Keep as string for YAML
        elif expected_type == "float":
            return float(value)
        elif expected_type == "integer":
            return int(value)
        elif expected_type == "boolean":
            return value.lower() == "true"
        elif expected_type == "sms_mode":
            return value
        else:
            return value
    
    def _update_config_file(self, key: str, value: Any) -> bool:
        """
        Update the configuration file with the new value using ruamel.yaml for comment preservation.
        
        Args:
            key: The configuration key to update
            value: The new value to set
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            from .config_preserver import update_yaml_preserving_comments
            return update_yaml_preserving_comments(self.config_file_path, key, value)
        except ImportError:
            # Fallback to old method if config_preserver not available
            logger.warning("config_preserver not available, using fallback method")
            return self._update_config_file_fallback(key, value)
        except Exception as e:
            logger.error(f"Failed to update configuration file: {e}")
            return False
    
    def _update_config_file_fallback(self, key: str, value: Any) -> bool:
        """
        Fallback method for updating configuration file (old implementation).
        
        Args:
            key: The configuration key to update
            value: The new value to set
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Load current configuration
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Navigate to the nested key and update
            keys = key.split('.')
            current = config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Update the target key
            current[keys[-1]] = value
            
            # Write back to file
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Configuration updated: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration file: {e}")
            return False
    
    def _log_config_update(self, key: str, value: Any, success: bool, message: str) -> bool:
        """
        Log configuration update attempts to a dedicated log file.
        
        Args:
            key: The configuration key that was attempted to update
            value: The value that was attempted to set
            success: Whether the update was successful
            message: Additional message about the result
            
        Returns:
            True if logging was successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} | {key} | {value} | {'SUCCESS' if success else 'FAILED'} | {message}\n"
            
            with open("logs/sms_config_updates.log", "a", encoding="utf-8") as f:
                f.write(log_entry)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to log configuration update: {e}")
            return False 