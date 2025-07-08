#!/usr/bin/env python3
"""
Test SMS Configuration Commands.

This script demonstrates the SMS configuration command functionality
by simulating incoming SMS messages and processing them.
"""

import sys
import os
import tempfile
import yaml
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.sms_config_processor import SMSConfigProcessor
from src.notification.sms_webhook_handler import SMSWebhookHandler


def create_test_config():
    """
    Create a temporary test configuration file.
    
    Returns:
        Path to the temporary config file
    """
    config_content = {
        "startdatum": "2025-07-07",
        "sms": {
            "test_number": "+49123456789",
            "production_number": "+49987654321"
        },
        "thresholds": {
            "temperature": 30.0,
            "rain_probability": 10.0,
            "wind_speed": 40.0
        },
        "delta_thresholds": {
            "temperature": 1.0,
            "rain_probability": 1.0
        },
        "max_daily_reports": 3,
        "min_interval_min": 60
    }
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config_content, temp_file, default_flow_style=False)
    temp_file.close()
    
    return temp_file.name


def print_config(config_path):
    """
    Print the current configuration.
    
    Args:
        config_path: Path to the configuration file
    """
    print("\n" + "="*50)
    print("CURRENT CONFIGURATION")
    print("="*50)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(yaml.dump(config, default_flow_style=False, indent=2))
    print("="*50)


def test_sms_commands():
    """Test various SMS configuration commands."""
    print("Testing SMS Configuration Commands")
    print("="*50)
    
    # Create test config
    config_path = create_test_config()
    print(f"Created test configuration file: {config_path}")
    
    try:
        # Initialize processor
        processor = SMSConfigProcessor(config_path)
        webhook_handler = SMSWebhookHandler(config_path)
        
        # Show initial config
        print_config(config_path)
        
        # Test commands
        test_commands = [
            # Valid commands
            "### thresholds.temperature: 25.0",
            "### startdatum: 2025-07-08",
            "### sms.test_number: +4915158450319",
            "### max_daily_reports: 5",
            "### delta_thresholds.temperature: 2.0",
            
            # Invalid commands
            "thresholds.temperature: 25.0",  # No ###
            "### invalid.key: value",        # Not in whitelist
            "### thresholds.temperature: invalid",  # Invalid value
            "### startdatum: 2025/07/07",    # Invalid date format
            "### sms.test_number: invalid",  # Invalid phone number
        ]
        
        print("\nTesting SMS Commands:")
        print("-" * 30)
        
        for i, command in enumerate(test_commands, 1):
            print(f"\n{i}. Testing: {command}")
            
            # Test direct processor
            result = processor.process_sms_command(command)
            print(f"   Result: {result['success']} - {result['message']}")
            
            if result['success']:
                print(f"   Updated: {result['key']} = {result['value']}")
        
        # Show final config
        print_config(config_path)
        
        # Test webhook processing
        print("\nTesting Webhook Processing:")
        print("-" * 30)
        
        # Seven.io webhook
        seven_webhook = {
            "to": "+49123456789",
            "from": "+49987654321",
            "text": "### thresholds.wind_speed: 50.0",
            "timestamp": datetime.now().isoformat()
        }
        
        result = webhook_handler.process_seven_webhook(seven_webhook)
        print(f"Seven.io webhook: {result['success']} - {result['message']}")
        
        # Twilio webhook
        twilio_webhook = {
            "To": "+49123456789",
            "From": "+49987654321",
            "Body": "### min_interval_min: 90",
            "MessageSid": "SM1234567890",
            "Timestamp": datetime.now().isoformat()
        }
        
        result = webhook_handler.process_twilio_webhook(twilio_webhook)
        print(f"Twilio webhook: {result['success']} - {result['message']}")
        
        # Show final config after webhook processing
        print_config(config_path)
        
    finally:
        # Clean up
        os.unlink(config_path)
        print(f"\nCleaned up test configuration file: {config_path}")


def test_whitelist_validation():
    """Test whitelist validation for configuration keys."""
    print("\nTesting Whitelist Validation:")
    print("-" * 30)
    
    processor = SMSConfigProcessor("config.yaml")
    
    test_keys = [
        # Valid keys
        "startdatum",
        "sms.production_number",
        "thresholds.temperature",
        "delta_thresholds.rain_probability",
        "max_daily_reports",
        "min_interval_min",
        
        # Invalid keys
        "smtp.host",
        "debug.enabled",
        "invalid.key",
        "thresholds.invalid_field"
    ]
    
    for key in test_keys:
        is_valid = processor._validate_key(key)
        status = "✓" if is_valid else "✗"
        print(f"{status} {key}")


def test_type_validation():
    """Test type validation for configuration values."""
    print("\nTesting Type Validation:")
    print("-" * 30)
    
    processor = SMSConfigProcessor("config.yaml")
    
    test_cases = [
        # Date validation
        ("startdatum", "2025-07-07", True),
        ("startdatum", "2025/07/07", False),
        ("startdatum", "invalid", False),
        
        # Phone number validation
        ("sms.test_number", "+49123456789", True),
        ("sms.test_number", "invalid", False),
        ("sms.test_number", "123456789", False),  # No +
        
        # Float validation
        ("thresholds.temperature", "25.0", True),
        ("thresholds.temperature", "25", True),
        ("thresholds.temperature", "invalid", False),
        
        # Integer validation
        ("max_daily_reports", "3", True),
        ("max_daily_reports", "3.5", False),
        ("max_daily_reports", "invalid", False),
    ]
    
    for key, value, expected in test_cases:
        is_valid = processor._validate_value_type(key, value)
        status = "✓" if is_valid == expected else "✗"
        print(f"{status} {key}: {value} (expected: {expected}, got: {is_valid})")


def main():
    """Main function to run all tests."""
    print("SMS Configuration Command Test Suite")
    print("=" * 50)
    
    try:
        # Test whitelist validation
        test_whitelist_validation()
        
        # Test type validation
        test_type_validation()
        
        # Test SMS commands
        test_sms_commands()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 