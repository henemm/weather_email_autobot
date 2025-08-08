#!/usr/bin/env python3
"""
Test script for Day function - sends real emails for both Morning and Evening reports
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
from datetime import date
import logging

def test_day_function():
    """Test Day function for both Morning and Evening reports with real email sending"""
    
    print("🌞 DAY FUNCTION - BOTH REPORTS TEST")
    print("=" * 50)
    
    # Initialize
    config = {
        'startdatum': '2025-07-27',
        'wind_speed': 10,
        'wind_gust_threshold': 20,
        'rain_threshold': 0.2,
        'rain_probability_threshold': 20,
        'thunderstorm_threshold': 'med'
    }
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    target_date = date(2025, 8, 2)
    stage_name = "Vergio"
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {target_date}")
    print()
    
    # Test MORNING report
    print("🔍 Testing MORNING report...")
    try:
        morning_report = refactor.generate_morning_report(stage_name, target_date)
        
        # Extract Day section from debug output
        debug_output = refactor.generate_debug_output(stage_name, target_date, "morning")
        day_section = ""
        in_day_section = False
        
        for line in debug_output.split('\n'):
            if "DAY" in line and "temp_max" in line:
                in_day_section = True
                day_section += line + '\n'
            elif in_day_section and line.strip() == "":
                in_day_section = False
                break
            elif in_day_section:
                day_section += line + '\n'
        
        # Create email content
        email_content = f"""N21

# DEBUG DATENEXPORT

{day_section}"""
        
        # Send real email
        print("📧 Sending morning report email...")
        email_client.send_email(
            subject="🌞 Day Function Test - Morning Report",
            body=email_content,
            to_email="test@example.com"  # Replace with actual test email
        )
        print("✅ MORNING email sent successfully!")
        
    except Exception as e:
        print(f"❌ MORNING report failed: {e}")
        logging.error(f"MORNING report error: {e}")
    
    print()
    
    # Test EVENING report
    print("🔍 Testing EVENING report...")
    try:
        evening_report = refactor.generate_evening_report(stage_name, target_date)
        
        # Extract Day section from debug output
        debug_output = refactor.generate_debug_output(stage_name, target_date, "evening")
        day_section = ""
        in_day_section = False
        
        for line in debug_output.split('\n'):
            if "DAY" in line and "temp_max" in line:
                in_day_section = True
                day_section += line + '\n'
            elif in_day_section and line.strip() == "":
                in_day_section = False
                break
            elif in_day_section:
                day_section += line + '\n'
        
        # Create email content
        email_content = f"""N21

# DEBUG DATENEXPORT

{day_section}"""
        
        # Send real email
        print("📧 Sending evening report email...")
        email_client.send_email(
            subject="🌞 Day Function Test - Evening Report",
            body=email_content,
            to_email="test@example.com"  # Replace with actual test email
        )
        print("✅ EVENING email sent successfully!")
        
    except Exception as e:
        print(f"❌ EVENING report failed: {e}")
        logging.error(f"EVENING report error: {e}")
    
    print()
    print("🎯 Both reports completed!")

if __name__ == "__main__":
    test_day_function() 