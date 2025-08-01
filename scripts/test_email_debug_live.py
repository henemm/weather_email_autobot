#!/usr/bin/env python3
"""
Live test script for email debug functionality.

This script tests the new debug output with a real email to ensure
the implementation works correctly in production.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notification.email_client import EmailClient, generate_gr20_report_text
from config.config_loader import load_config


def test_email_debug_live():
    """Test email debug functionality with a real email."""
    print("📧 Live Email Debug Test")
    print("=" * 50)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()
        
        # Check if debug is enabled
        debug_enabled = config.get("debug", {}).get("enabled", False)
        print(f"🔧 Debug enabled: {debug_enabled}")
        
        if not debug_enabled:
            print("⚠️  Debug is disabled. Enabling for test...")
            config["debug"]["enabled"] = True
        
        # Create sample report data
        report_data = {
            "report_type": "morning",
            "location": "Test Location",
            "stage_names": ["Test Stage 1", "Test Stage 2"],
            "weather_data": {
                "max_temperature": 25.0,
                "min_temperature": 15.0,
                "max_rain_probability": 30.0,
                "max_wind_speed": 20.0
            }
        }
        
        print(f"📊 Report type: {report_data['report_type']}")
        print(f"📍 Location: {report_data['location']}")
        
        # Generate email text with debug info
        print("\n🔄 Generating email text with debug info...")
        email_text = generate_gr20_report_text(report_data, config)
        
        print(f"\n📏 Email text length: {len(email_text)} characters")
        
        # Check if debug info is present
        if "DEBUG DATENEXPORT – Rohdatenübersicht MeteoFrance" in email_text:
            print("✅ Debug information found in email!")
            
            # Extract debug section
            debug_start = email_text.find("DEBUG DATENEXPORT")
            if debug_start != -1:
                debug_section = email_text[debug_start:debug_start + 500]  # First 500 chars
                print("\n🔍 DEBUG SECTION PREVIEW:")
                print("-" * 40)
                print(debug_section)
                print("-" * 40)
                print("... (truncated)")
        else:
            print("❌ No debug information found in email")
            print("\n📄 EMAIL CONTENT PREVIEW:")
            print("-" * 40)
            print(email_text[:500])
            print("-" * 40)
            print("... (truncated)")
        
        # Test email sending (optional)
        print("\n📤 Testing email sending...")
        email_client = EmailClient(config)
        
        # Create a test subject
        subject = f"TEST: Weather Debug Output - {report_data['report_type']}"
        
        # Send email
        success = email_client.send_email(email_text, subject)
        
        if success:
            print("✅ Email sent successfully!")
            print(f"📧 Subject: {subject}")
            print(f"📏 Content length: {len(email_text)} characters")
            
            # Show email configuration
            smtp_config = config.get("smtp", {})
            print(f"📮 To: {smtp_config.get('to', 'Not configured')}")
            print(f"📮 From: {smtp_config.get('user', 'Not configured')}")
            
        else:
            print("❌ Failed to send email")
            
    except Exception as e:
        print(f"❌ Error in live test: {e}")
        import traceback
        traceback.print_exc()


def test_debug_only():
    """Test debug output generation only."""
    print("\n🔍 Debug Output Only Test")
    print("=" * 50)
    
    try:
        config = load_config()
        config["debug"]["enabled"] = True
        
        report_data = {
            "report_type": "morning",
            "location": "Debug Test",
            "stage_names": ["Stage 1", "Stage 2"]
        }
        
        from notification.email_client import generate_debug_email_append
        debug_output = generate_debug_email_append(report_data, config)
        
        print(f"📏 Debug output length: {len(debug_output)} characters")
        
        if debug_output:
            print("✅ Debug output generated successfully")
            print("\n📄 DEBUG OUTPUT PREVIEW:")
            print("-" * 40)
            print(debug_output[:1000])
            print("-" * 40)
            print("... (truncated)")
        else:
            print("❌ No debug output generated")
            
    except Exception as e:
        print(f"❌ Error in debug test: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function."""
    print("🚀 Starting Live Email Debug Test")
    print("=" * 60)
    
    # Test debug output generation
    test_debug_only()
    
    # Test full email with debug
    test_email_debug_live()
    
    print("\n✅ Live test completed!")
    print("\n📝 Summary:")
    print("   - Debug output generation tested")
    print("   - Email integration tested")
    print("   - Real email sent (if successful)")
    print("   - Check your email inbox for the test message")


if __name__ == "__main__":
    main() 