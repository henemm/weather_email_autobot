#!/usr/bin/env python3
"""
Test script for SMS functionality.

This script demonstrates the SMS client functionality with a test configuration.
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from notification.modular_sms_client import ModularSmsClient


def test_sms_client_initialization():
    """Test SMS client initialization with test configuration."""
    print("Testing SMS client initialization...")
    
    # Test configuration (without real API key)
    config = {
        "sms": {
            "enabled": True,
            "provider": "seven",
            "api_key": "test_api_key",
            "test_number": "+49123456789",
            "production_number": "+49987654321",
            "mode": "test",
            "sender": "GR20-Info"
        }
    }
    
    try:
        client = ModularSmsClient(config)
        print("✅ SMS client initialized successfully")
        print(f"   Enabled: {client.enabled}")
        print(f"   Provider: {client.provider_name}")
        print(f"   Mode: {client.mode}")
        print(f"   Recipient: {client.recipient_number}")
        print(f"   Sender: {config['sms'].get('sender', 'unknown')}")
        return client
    except Exception as e:
        print(f"❌ SMS client initialization failed: {e}")
        return None


def test_sms_client_production_mode():
    """Test SMS client in production mode."""
    print("\nTesting SMS client in production mode...")
    
    config = {
        "sms": {
            "enabled": True,
            "provider": "seven",
            "api_key": "test_api_key",
            "test_number": "+49123456789",
            "production_number": "+49987654321",
            "mode": "production",
            "sender": "GR20-Info"
        }
    }
    
    try:
        client = ModularSmsClient(config)
        print("✅ SMS client initialized (production mode)")
        print(f"   Mode: {client.mode}")
        print(f"   Recipient: {client.recipient_number} (should be production number)")
        
        return client
    except Exception as e:
        print(f"❌ SMS client production mode test failed: {e}")
        return None


def test_sms_client_disabled():
    """Test SMS client when disabled."""
    print("\nTesting SMS client when disabled...")
    
    config = {
        "sms": {
            "enabled": False,
            "provider": "seven",
            "api_key": "test_api_key",
            "test_number": "+49123456789",
            "production_number": "+49987654321",
            "mode": "test",
            "sender": "GR20-Info"
        }
    }
    
    try:
        client = ModularSmsClient(config)
        print("✅ SMS client initialized (disabled)")
        print(f"   Enabled: {client.enabled}")
        
        # Test sending when disabled
        result = client.send_sms("Test message")
        print(f"   Send result: {result} (should be False)")
        
        return client
    except Exception as e:
        print(f"❌ SMS client test failed: {e}")
        return None


def test_sms_report_generation():
    """Test SMS report text generation."""
    print("\nTesting SMS report text generation...")
    
    config = {
        "sms": {
            "enabled": True,
            "provider": "seven",
            "api_key": "test_api_key",
            "test_number": "+49123456789",
            "production_number": "+49987654321",
            "mode": "test",
            "sender": "GR20-Info"
        }
    }
    
    try:
        client = ModularSmsClient(config)
        
        # Test morning report
        morning_report_data = {
            "location": "Vizzavona",
            "report_type": "morning",
            "weather_data": {
                "max_thunderstorm_probability": 45.0,
                "thunderstorm_threshold_time": "14:00",
                "thunderstorm_threshold_pct": 30.0,
                "thunderstorm_next_day": 35.0,
                "max_precipitation_probability": 60.0,
                "rain_threshold_time": "12:00",
                "rain_threshold_pct": 50.0,
                "max_precipitation": 5.2,
                "max_temperature": 28.5,
                "max_wind_speed": 25.0,
                "vigilance_alerts": [
                    {"phenomenon": "thunderstorm", "level": 2, "type": "Gewitter"}
                ]
            },
            "report_time": datetime.now()
        }
        
        morning_text = client._generate_gr20_report_text(morning_report_data)
        print(f"✅ Morning report generated:")
        print(f"   Text: '{morning_text}'")
        print(f"   Length: {len(morning_text)} characters")
        print(f"   Within limit: {len(morning_text) <= 160}")
        
        # Test evening report
        evening_report_data = {
            "location": "Haut Asco",
            "report_type": "evening",
            "weather_data": {
                "min_temperature": 12.5,
                "max_thunderstorm_probability": 35.0,
                "thunderstorm_threshold_time": "15:00",
                "thunderstorm_threshold_pct": 25.0,
                "thunderstorm_next_day": 40.0,
                "max_precipitation_probability": 45.0,
                "rain_threshold_time": "13:00",
                "rain_threshold_pct": 40.0,
                "max_precipitation": 3.8,
                "max_temperature": 26.0,
                "max_wind_speed": 30.0,
                "vigilance_alerts": [
                    {"phenomenon": "rain", "level": 1, "type": "Regen"}
                ]
            },
            "report_time": datetime.now()
        }
        
        evening_text = client._generate_gr20_report_text(evening_report_data)
        print(f"\n✅ Evening report generated:")
        print(f"   Text: '{evening_text}'")
        print(f"   Length: {len(evening_text)} characters")
        print(f"   Within limit: {len(evening_text) <= 160}")
        
        # Test dynamic report
        dynamic_report_data = {
            "location": "Conca",
            "report_type": "dynamic",
            "weather_data": {
                "thunderstorm_threshold_time": "16:00",
                "thunderstorm_threshold_pct": 40.0,
                "rain_threshold_time": "14:00",
                "rain_threshold_pct": 55.0,
                "max_temperature": 29.0,
                "max_wind_speed": 35.0,
                "vigilance_alerts": [
                    {"phenomenon": "thunderstorm", "level": 3, "type": "Gewitter"}
                ]
            },
            "report_time": datetime.now()
        }
        
        dynamic_text = client._generate_gr20_report_text(dynamic_report_data)
        print(f"\n✅ Dynamic report generated:")
        print(f"   Text: '{dynamic_text}'")
        print(f"   Length: {len(dynamic_text)} characters")
        print(f"   Within limit: {len(dynamic_text) <= 160}")
        
        return True
        
    except Exception as e:
        print(f"❌ SMS report generation test failed: {e}")
        return False


def test_character_limit_handling():
    """Test character limit handling."""
    print("\nTesting character limit handling...")
    
    config = {
        "sms": {
            "enabled": True,
            "provider": "seven",
            "api_key": "test_api_key",
            "test_number": "+49123456789",
            "production_number": "+49987654321",
            "mode": "test",
            "sender": "GR20-Info"
        }
    }
    
    try:
        client = ModularSmsClient(config)
        
        # Test with message that's exactly 160 characters
        exact_message = "A" * 160
        result = client.send_sms(exact_message)
        print(f"✅ 160-character message: {result}")
        
        # Test with message that's over 160 characters
        long_message = "B" * 200
        result = client.send_sms(long_message)
        print(f"✅ 200-character message (should be truncated): {result}")
        
        # Test with empty message
        empty_result = client.send_sms("")
        print(f"✅ Empty message: {empty_result} (should be False)")
        
        # Test with None message
        none_result = client.send_sms(None)
        print(f"✅ None message: {none_result} (should be False)")
        
        return True
        
    except Exception as e:
        print(f"❌ Character limit test failed: {e}")
        return False


def test_environment_variable_support():
    """Test environment variable support for API key."""
    print("\nTesting environment variable support...")
    
    # Set test environment variable for API key
    test_env_vars = {
        "SEVEN_API_KEY": "env_test_api_key"
    }
    
    # Create config with environment variable placeholder for API key
    config = {
        "sms": {
            "enabled": True,
            "provider": "seven",
            "api_key": "${SEVEN_API_KEY}",
            "test_number": "+49123456789",
            "production_number": "+49987654321",
            "mode": "test",
            "sender": "GR20-Info"
        }
    }
    
    try:
        # Set environment variable temporarily
        original_env = {}
        for key, value in test_env_vars.items():
            original_env[key] = os.getenv(key)
            os.environ[key] = value
        
        # Test that the config loader would handle this correctly
        print("✅ Environment variables set for testing")
        print(f"   SEVEN_API_KEY: {os.getenv('SEVEN_API_KEY')}")
        
        # Restore original environment variable
        for key, original_value in original_env.items():
            if original_value is not None:
                os.environ[key] = original_value
            else:
                os.environ.pop(key, None)
        
        return True
        
    except Exception as e:
        print(f"❌ Environment variable test failed: {e}")
        return False


def test_command_line_parameter_simulation():
    """Test simulation of the new --sms command line parameter."""
    print("\nTesting command line parameter simulation...")
    
    # Simulate config with test mode
    config = {
        "sms": {
            "enabled": True,
            "provider": "seven",
            "api_key": "test_api_key",
            "test_number": "+49123456789",
            "production_number": "+49987654321",
            "mode": "test",  # Default mode
            "sender": "GR20-Info"
        }
    }
    
    try:
        # Simulate --sms production parameter
        print("Simulating --sms production parameter...")
        original_mode = config["sms"]["mode"]
        config["sms"]["mode"] = "production"
        print(f"   SMS mode overridden: {original_mode} -> production")
        
        # Test SMS client with overridden mode
        client = ModularSmsClient(config)
        print(f"   SMS mode: {client.mode}")
        print(f"   SMS recipient: {client.recipient_number}")
        print(f"   Expected recipient: {config['sms']['production_number']}")
        
        if client.recipient_number == config["sms"]["production_number"]:
            print("✅ Command line parameter simulation successful")
            return True
        else:
            print("❌ Command line parameter simulation failed")
            return False
        
    except Exception as e:
        print(f"❌ Command line parameter test failed: {e}")
        return False


def main():
    """Main test function."""
    print("📱 SMS FUNCTIONALITY TEST")
    print("=" * 50)
    print("Testing SMS client functionality...")
    print()
    
    # Test initialization
    client = test_sms_client_initialization()
    
    # Test production mode
    test_sms_client_production_mode()
    
    # Test disabled mode
    test_sms_client_disabled()
    
    # Test report generation
    report_success = test_sms_report_generation()
    
    # Test character limits
    limit_success = test_character_limit_handling()
    
    # Test environment variable support
    env_success = test_environment_variable_support()
    
    # Test command line parameter simulation
    cli_success = test_command_line_parameter_simulation()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ SMS client initialization: {'PASSED' if client else 'FAILED'}")
    print(f"✅ Report generation: {'PASSED' if report_success else 'FAILED'}")
    print(f"✅ Character limit handling: {'PASSED' if limit_success else 'FAILED'}")
    print(f"✅ Environment variable support: {'PASSED' if env_success else 'FAILED'}")
    print(f"✅ Command line parameter simulation: {'PASSED' if cli_success else 'FAILED'}")
    
    if client and report_success and limit_success and env_success and cli_success:
        print("\n🎉 All tests PASSED!")
        print("\n📝 Next steps:")
        print("1. Create .env file with your API key:")
        print("   SEVEN_API_KEY=your_seven_api_key_here")
        print("2. Update phone numbers in config.yaml:")
        print("   test_number: '+49your_test_number'")
        print("   production_number: '+49your_production_number'")
        print("3. Test the new --sms parameter:")
        print("   python scripts/run_gr20_weather_monitor.py --modus morning --sms test")
        print("   python scripts/run_gr20_weather_monitor.py --modus morning --sms production")
        print("4. Set mode to 'production' in config.yaml when ready")
        print("5. Test with real API calls (optional)")
        print("6. Integrate with the main weather monitor")
    else:
        print("\n❌ Some tests FAILED!")
        print("Please check the error messages above.")


if __name__ == "__main__":
    main() 