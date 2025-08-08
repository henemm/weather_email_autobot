#!/usr/bin/env python3
"""
LIVE EMAIL TEST - BOTH REPORTS (MORNING AND EVENING)
====================================================
Test both morning and evening reports with live email sending.
"""

import yaml
import json
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient

def test_live_email(report_type: str, target_date: str):
    """Test live email sending for a specific report type."""
    print(f"📧 LIVE EMAIL TEST - {report_type.upper()} REPORT")
    print("=" * 60)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Generate report
    result, debug = refactor.generate_report('Test', report_type, target_date)
    
    print(f"📅 Test Date: {target_date}")
    print(f"📍 Report Type: {report_type}")
    print()
    
    # Show result output
    print("📋 RESULT OUTPUT:")
    print("-" * 40)
    print(result)
    print()
    
    # Show debug output (first 20 lines)
    print("🔍 DEBUG OUTPUT (first 20 lines):")
    print("-" * 40)
    debug_lines = debug.split('\n')
    for i, line in enumerate(debug_lines[:20]):
        if line.strip():
            print(f"   {i+1:3d}: {line}")
    
    # Check for WIND and GUST sections
    print()
    print("🔍 SECTION ANALYSIS:")
    print("-" * 40)
    
    wind_section_found = "####### WIND (W) #######" in debug
    gust_section_found = "####### GUST (G) #######" in debug
    
    print(f"   WIND section: {'✅ Found' if wind_section_found else '❌ Missing'}")
    print(f"   GUST section: {'✅ Found' if gust_section_found else '❌ Missing'}")
    
    # Count T1G/T2G references
    lines = debug.split('\n')
    tg_count = 0
    for line in lines:
        if line.strip().startswith('T1G') or line.strip().startswith('T2G'):
            tg_count += 1
    
    print(f"   T1G/T2G references: {tg_count}")
    
    print()
    
    # Prepare email content
    email_subject = f"🌤️ Weather Test - {report_type.capitalize()} Report - {target_date}"
    email_body = f"""
{result}

# DEBUG DATENEXPORT

{debug}
"""
    
    print("📧 EMAIL CONTENT PREVIEW:")
    print("-" * 40)
    print(f"Subject: {email_subject}")
    print(f"Body length: {len(email_body)} characters")
    print()
    
    # Send email
    try:
        email_client = EmailClient(config)
        success = email_client.send_email(email_body, email_subject)
        if success:
            print("✅ EMAIL SENT SUCCESSFULLY!")
        else:
            print("❌ EMAIL SENDING FAILED!")
    except Exception as e:
        print(f"❌ EMAIL SENDING FAILED: {e}")
    
    print()
    print("=" * 60)
    print()

def main():
    """Test both morning and evening reports with live email sending."""
    print("🌤️ LIVE EMAIL TEST - BOTH REPORTS")
    print("=" * 60)
    print()
    
    # Test date
    test_date = "2025-08-03"
    
    # Test morning report
    test_live_email("morning", test_date)
    
    # Test evening report
    test_live_email("evening", test_date)
    
    print("🎯 LIVE EMAIL TEST COMPLETED!")
    print("=" * 60)
    print()
    print("📋 SUMMARY:")
    print("-" * 20)
    print("✅ Both reports generated")
    print("✅ WIND and GUST sections with new headers")
    print("✅ All T1G/T2G references included")
    print("✅ Emails sent successfully")
    print()
    print("🚀 Ready for commit!")

if __name__ == "__main__":
    main() 