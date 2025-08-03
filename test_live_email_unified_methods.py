#!/usr/bin/env python3
"""
Test script to validate unified methods for Morning and Evening reports.
Sends live emails to verify both reports work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
import yaml
from datetime import date

def test_live_email_unified_methods():
    """Test both Morning and Evening reports with unified methods."""
    
    print("🔍 LIVE E-MAIL TEST: UNIFIED METHODS")
    print("=" * 50)
    
    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    
    # Test date
    test_date = "2025-08-03"
    stage_name = "Test"
    
    print(f"📅 Test Date: {test_date}")
    print(f"📍 Stage: {stage_name}")
    print()
    
    # Test Morning Report
    print("🌅 TESTING MORNING REPORT:")
    print("-" * 30)
    try:
        result_output, debug_output = refactor.generate_report(stage_name, "morning", test_date)
        
        print("✅ Morning Report generated successfully")
        print(f"📧 Result Output Length: {len(result_output)} chars")
        print(f"🔍 Debug Output Length: {len(debug_output)} chars")
        
        # Send Morning email
        subject = f"TEST: Morning Report - {stage_name} - {test_date}"
        email_content = f"{result_output}\n\n# DEBUG DATENEXPORT\n{debug_output}"
        
        success = email_client.send_email(email_content, subject)
        if success:
            print("✅ Morning email sent successfully")
        else:
            print("❌ Failed to send Morning email")
            
    except Exception as e:
        print(f"❌ Morning Report failed: {e}")
    
    print()
    
    # Test Evening Report
    print("🌆 TESTING EVENING REPORT:")
    print("-" * 30)
    try:
        result_output, debug_output = refactor.generate_report(stage_name, "evening", test_date)
        
        print("✅ Evening Report generated successfully")
        print(f"📧 Result Output Length: {len(result_output)} chars")
        print(f"🔍 Debug Output Length: {len(debug_output)} chars")
        
        # Send Evening email
        subject = f"TEST: Evening Report - {stage_name} - {test_date}"
        email_content = f"{result_output}\n\n# DEBUG DATENEXPORT\n{debug_output}"
        
        success = email_client.send_email(email_content, subject)
        if success:
            print("✅ Evening email sent successfully")
        else:
            print("❌ Failed to send Evening email")
            
    except Exception as e:
        print(f"❌ Evening Report failed: {e}")
    
    print()
    print("🎯 TEST COMPLETED!")
    print("Check your email inbox for both test emails.")

if __name__ == "__main__":
    test_live_email_unified_methods() 