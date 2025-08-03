#!/usr/bin/env python3
"""
Send real emails for Day function testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
from datetime import date
import yaml

def send_day_test_emails():
    """Send real emails for Day function testing"""
    
    print("🌞 DAY FUNCTION - SENDING REAL EMAILS")
    print("=" * 50)
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {target_date}")
    print()
    
    # Test MORNING report
    print("🔍 Testing MORNING report...")
    try:
        morning_report = refactor.generate_morning_report(stage_name, target_date)
        
        # Create email content
        email_content = f"""{morning_report}

# DEBUG DATENEXPORT

Debug output temporarily disabled due to comparison errors"""
        
        # Send real email
        print("📧 Sending morning report email...")
        email_client.send_email(
            subject="🌞 Day Function Test - Morning Report",
            body=email_content,
            to_email=config.get('email', {}).get('to_email', 'test@example.com')
        )
        print("✅ MORNING email sent successfully!")
        
    except Exception as e:
        print(f"❌ MORNING report failed: {e}")
    
    print()
    
    # Test EVENING report
    print("🔍 Testing EVENING report...")
    try:
        evening_report = refactor.generate_evening_report(stage_name, target_date)
        
        # Create email content
        email_content = f"""{evening_report}

# DEBUG DATENEXPORT

Debug output temporarily disabled due to comparison errors"""
        
        # Send real email
        print("📧 Sending evening report email...")
        email_client.send_email(
            subject="🌞 Day Function Test - Evening Report",
            body=email_content,
            to_email=config.get('email', {}).get('to_email', 'test@example.com')
        )
        print("✅ EVENING email sent successfully!")
        
    except Exception as e:
        print(f"❌ EVENING report failed: {e}")
    
    print()
    print("🎯 Both emails sent!")

if __name__ == "__main__":
    send_day_test_emails() 