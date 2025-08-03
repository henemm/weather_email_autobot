#!/usr/bin/env python3
"""
TEST REAL EMAIL EVENING REPORT
==============================
Send a real email for evening report to test debug output.
"""

import yaml
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient

def test_real_email_evening_report():
    """Send a real email for evening report to test debug output."""
    print("📧 TEST REAL EMAIL EVENING REPORT")
    print("=" * 50)
    
    try:
        # Load config
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test parameters
        stage_name = "Test"
        target_date = date(2025, 8, 3)
        report_type = "evening"
        
        print(f"📅 Target Date: {target_date}")
        print(f"📍 Stage: {stage_name}")
        print(f"📋 Report Type: {report_type}")
        print()
        
        # Generate report
        print("1️⃣ GENERATING EVENING REPORT:")
        print("-" * 30)
        
        result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date.strftime('%Y-%m-%d'))
        
        print("✅ Evening report generated successfully")
        print(f"Result Output Length: {len(result_output)}")
        print(f"Debug Output Length: {len(debug_output)}")
        print()
        
        print("2️⃣ RESULT OUTPUT:")
        print("-" * 30)
        print(result_output)
        print()
        
        print("3️⃣ DEBUG OUTPUT PREVIEW:")
        print("-" * 30)
        print(debug_output[:200] + "...")
        print()
        
        # Create email content
        email_subject = f"TEST: Evening Report Debug Output Validation"
        email_body = f"""
EVENING REPORT DEBUG OUTPUT VALIDATION TEST
===========================================

This is a test to validate the evening report debug output in emails.

RESULT OUTPUT:
{result_output}

DEBUG OUTPUT:
{debug_output}

END OF EVENING REPORT TEST
"""
        
        print("4️⃣ SENDING EVENING REPORT EMAIL:")
        print("-" * 30)
        
        # Send email
        email_client = EmailClient(config)
        success = email_client.send_email(email_body, email_subject)
        
        if success:
            print("✅ EVENING REPORT EMAIL SENT SUCCESSFULLY!")
            print("📧 Please check your email to see the evening report debug output.")
            print("🔍 Look for:")
            print("   - Double # DEBUG DATENEXPORT markers")
            print("   - Error messages")
            print("   - Complete debug sections")
            print("   - Evening-specific sections (übermorgen)")
            print("   - T2G/T3G references (not T1G)")
        else:
            print("❌ EVENING REPORT EMAIL SENDING FAILED!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_real_email_evening_report() 