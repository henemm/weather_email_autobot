#!/usr/bin/env python3
"""
Live test script for Day function - sends real emails for both Morning and Evening reports
Tests the complete Day function implementation according to specification.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
from datetime import date
import logging
import yaml

def load_config():
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def test_day_function_live():
    """Test Day function for both Morning and Evening reports with real email sending."""
    
    print("🌞 DAY FUNCTION - LIVE TEST WITH REAL EMAILS")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    target_date = date(2025, 8, 2)
    stage_name = "Vergio"
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {target_date}")
    print(f"📧 Email: {config.get('smtp', {}).get('to', 'Not configured')}")
    print()
    
    # Test MORNING report
    print("🔍 Testing MORNING report...")
    try:
        # Generate morning report
        morning_result, morning_debug = refactor.generate_report(stage_name, "morning", target_date.strftime('%Y-%m-%d'))
        
        # Extract Day section from debug output
        day_section = ""
        in_day_section = False
        for line in morning_debug.split('\n'):
            if line.strip() == "DAY":
                in_day_section = True
                day_section += line + '\n'
            elif in_day_section and line.strip() == "":
                in_day_section = False
                break
            elif in_day_section:
                day_section += line + '\n'
        
        # Create email content with Result-Output and Debug-Output
        email_content = f"""{morning_result}

# DEBUG DATENEXPORT

{day_section}"""
        
        # Send real email
        print("📧 Sending morning report email...")
        email_client.send_email(
            email_content,
            "🌞 Day Function Test - Morning Report"
        )
        print("✅ MORNING email sent successfully!")
        print(f"📊 Result Output: {morning_result}")
        print(f"🔍 Day Section found: {'DAY' in day_section}")
        
    except Exception as e:
        print(f"❌ MORNING report failed: {e}")
        logging.error(f"MORNING report error: {e}")
    
    print()
    
    # Test EVENING report
    print("🔍 Testing EVENING report...")
    try:
        # Generate evening report
        evening_result, evening_debug = refactor.generate_report(stage_name, "evening", target_date.strftime('%Y-%m-%d'))
        
        # Extract Day section from debug output
        day_section = ""
        in_day_section = False
        for line in evening_debug.split('\n'):
            if line.strip() == "DAY":
                in_day_section = True
                day_section += line + '\n'
            elif in_day_section and line.strip() == "":
                in_day_section = False
                break
            elif in_day_section:
                day_section += line + '\n'
        
        # Create email content with Result-Output and Debug-Output
        email_content = f"""{evening_result}

# DEBUG DATENEXPORT

{day_section}"""
        
        # Send real email
        print("📧 Sending evening report email...")
        email_client.send_email(
            email_content,
            "🌞 Day Function Test - Evening Report"
        )
        print("✅ EVENING email sent successfully!")
        print(f"📊 Result Output: {evening_result}")
        print(f"🔍 Day Section found: {'DAY' in day_section}")
        
    except Exception as e:
        print(f"❌ EVENING report failed: {e}")
        logging.error(f"EVENING report error: {e}")
    
    print()
    print("🎯 Both reports completed!")
    print("📋 Check your email for the test results")
    print("📊 Verify that:")
    print("   - Result Output contains 'D{max_temp_rounded}' format")
    print("   - Debug Output contains 'DAY' section with T-G references")
    print("   - T-G references are correct (T1G1, T1G2, T1G3 for morning; T2G1, T2G2, T2G3 for evening)")
    print("   - MAX value is correctly calculated and displayed")

if __name__ == "__main__":
    test_day_function_live() 