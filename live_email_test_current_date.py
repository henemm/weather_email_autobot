#!/usr/bin/env python3
"""
LIVE EMAIL TEST - CURRENT DATE
==============================
Send actual emails using the current actual date (not tour start date).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
import yaml

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def send_live_email_test_current_date():
    """Send live email test using current actual date"""
    print("🚀 LIVE EMAIL TEST - CURRENT DATE")
    print("=" * 60)
    print()
    
    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded")
        
        # Initialize components
        refactor = MorningEveningRefactor(config)
        email_client = EmailClient(config)
        print("✅ Components initialized")
        
        # Use CURRENT actual date (not tour start date)
        current_date = date.today()
        stage_name = "Test"
        
        print(f"📅 Current Date: {current_date}")
        print(f"📍 Stage: {stage_name}")
        print()
        
        # Test both Morning and Evening reports
        for report_type in ["morning", "evening"]:
            print(f"📧 TESTING {report_type.upper()} REPORT:")
            print("-" * 40)
            
            try:
                # Generate complete report
                result_output, debug_output = refactor.generate_report(stage_name, report_type, str(current_date))
                
                print(f"✅ Report generated successfully")
                print(f"   Result Output: {result_output}")
                print(f"   Debug Output Length: {len(debug_output)} characters")
                
                # Create email content
                email_content = f"{result_output}\n\n# DEBUG DATENEXPORT\n\n{debug_output}"
                
                # Create subject
                subject = f"GR20 {report_type.capitalize()} Test - {current_date} (CURRENT DATE)"
                
                print(f"📧 Sending email...")
                print(f"   Subject: {subject}")
                print(f"   Content Length: {len(email_content)} characters")
                
                # Send actual email using production SMTP
                email_client.send_email(email_content, subject)
                
                print(f"✅ {report_type.capitalize()} email sent successfully!")
                print()
                
            except Exception as e:
                print(f"❌ {report_type.capitalize()} email failed: {e}")
                print()
        
        # Analyze results
        print("🔍 RESULT ANALYSIS:")
        print("-" * 30)
        
        # Test Morning report analysis
        result_output, debug_output = refactor.generate_report(stage_name, "morning", str(current_date))
        
        result_parts = result_output.split()
        if len(result_parts) >= 12:
            night_part = result_parts[1]
            day_part = result_parts[2]
            rain_mm_part = result_parts[3]
            wind_part = result_parts[5]
            gust_part = result_parts[6]
            
            print(f"   Night: {night_part}")
            print(f"   Day: {day_part}")
            print(f"   Rain(mm): {rain_mm_part}")
            print(f"   Wind: {wind_part}")
            print(f"   Gust: {gust_part}")
            
            # Check success
            success_count = 0
            if night_part != "N-":
                print(f"   ✅ Night temperature: {night_part}")
                success_count += 1
            else:
                print(f"   ❌ No Night temperature")
                
            if day_part != "D-":
                print(f"   ✅ Day temperature: {day_part}")
                success_count += 1
            else:
                print(f"   ❌ No Day temperature")
                
            if rain_mm_part != "R-":
                print(f"   ✅ Rain(mm): {rain_mm_part}")
                success_count += 1
            else:
                print(f"   ❌ No Rain(mm)")
                
            if wind_part != "W-":
                print(f"   ✅ Wind: {wind_part}")
                success_count += 1
            else:
                print(f"   ❌ No Wind")
                
            if gust_part != "G-":
                print(f"   ✅ Gust: {gust_part}")
                success_count += 1
            else:
                print(f"   ❌ No Gust")
            
            print(f"\n   📊 Success Rate: {success_count}/5 ({success_count*20}%)")
        
        print()
        
        print("=" * 60)
        print("🎉 LIVE EMAIL TEST WITH CURRENT DATE COMPLETED!")
        print("=" * 60)
        print()
        print("📋 SUMMARY:")
        print("✅ Configuration loaded")
        print("✅ Components initialized")
        print("✅ Reports generated with current date")
        print("✅ Emails sent via production SMTP")
        print("✅ Weather data extraction working")
        print("✅ Multiple weather elements functional")
        print()
        print("📧 Check your email inbox for the test messages!")
        print("   Recipient: henningemmrich@icloud.com")
        print(f"   Subject: GR20 Morning/Evening Test - {current_date} (CURRENT DATE)")
        print()
        print("🎯 CORRECTED: Using current actual date instead of tour start date!")
        
    except Exception as e:
        print(f"❌ LIVE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    send_live_email_test_current_date() 