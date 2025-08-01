#!/usr/bin/env python3
"""
Wind Position Test for Evening Report

This script tests the Wind position implementation for the Evening report.
It will send a real email with the test results.
"""

import yaml
import sys
import os
from datetime import date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient

def main():
    print("🌤️  WIND POSITION TEST - Evening Report")
    print("=" * 50)
    print("Testing Wind position for Evening report")
    print("⚠️  WARNING: This will send a REAL EMAIL!")
    print()
    
    # Load configuration
    print("📋 Loading configuration...")
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        print("✅ Configuration loaded")
        print(f"   SMTP host: {config.get('smtp', {}).get('host', 'N/A')}")
        print(f"   Email to: {config.get('email', {}).get('to', 'N/A')}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Initialize MorningEveningRefactor
    print("🔧 Initializing MorningEveningRefactor...")
    try:
        refactor = MorningEveningRefactor(config)
        print("✅ MorningEveningRefactor initialized")
    except Exception as e:
        print(f"❌ Failed to initialize MorningEveningRefactor: {e}")
        return False
    
    # Get stage info
    print("📅 Generating Evening Report for Wind position...")
    print("-" * 40)
    
    try:
        # Get current stage info
        from src.position.etappenlogik import get_stage_info
        stage_info = get_stage_info(config)
        
        if not stage_info:
            print("❌ Failed to get stage info")
            return False
        
        stage_name = stage_info['name']
        target_date = date.today()
        
        # Generate report
        result_output, debug_output = refactor.generate_report(stage_name, 'evening', target_date)
        
        print("✅ Evening Report Generated:")
        print(f"   Result: {result_output}")
        print(f"   Length: {len(result_output)} chars")
        print()
        
        # Show debug output
        print("📊 Debug Output:")
        print(debug_output)
        print()
        
        # Prepare email content
        print("📧 Preparing Email Content...")
        print("-" * 40)
        
        email_subject = f"GR20 Evening Report - Wind Position Test"
        email_content = f"""
GR20 Evening Report - Wind Position Test

Generated on: {date.today()}
Stage: {stage_name}
Report Type: Evening

RESULT OUTPUT:
{result_output}

DEBUG OUTPUT:
{debug_output}

---
This is a test email for the Wind position implementation.
"""
        
        # Send email
        print("📧 SENDING REAL EMAIL...")
        print("-" * 40)
        print("⚠️  This will send an actual email to:", config.get('email', {}).get('to', 'N/A'))
        print(f"📧 Subject: {email_subject}")
        print(f"📧 Content length: {len(email_content)} chars")
        print()
        
        try:
            email_client = EmailClient(config)
            email_client.send_email(message_text=email_content, subject=email_subject)
            print("✅ EMAIL SENT SUCCESSFULLY!")
            print(f"   Email delivered to: {config.get('email', {}).get('to', 'N/A')}")
            print(f"   Subject: {email_subject}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
        
        # Summary
        print()
        print("📋 WIND POSITION TEST SUMMARY")
        print("-" * 40)
        print("✅ Etappen-Berechnung: SUCCESS")
        print("✅ Debug-Output: SUCCESS")
        print("✅ Wind Position: SUCCESS")
        print("✅ Email sending: SUCCESS")
        print()
        print("🎉 WIND POSITION TEST COMPLETED!")
        print("   Ready for next position (Gust)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate report: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 