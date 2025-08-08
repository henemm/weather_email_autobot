#!/usr/bin/env python3
"""
Functional test for real email generation with alternative risk analysis.

This script tests the ACTUAL email generation pipeline and verifies that
the alternative risk analysis is properly integrated into the final email.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report.weather_report_generator import generate_weather_report
from config.config_loader import load_config


def test_real_email_generation():
    """Test the actual email generation with alternative risk analysis."""
    print("🎯 FUNCTIONAL TEST: Real Email Generation with Alternative Risk Analysis")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    
    # Enable alternative risk analysis
    config["alternative_risk_analysis"] = {
        "enabled": True
    }
    
    print(f"✅ Configuration loaded with alternative risk analysis enabled")
    
    # Generate morning report
    print(f"📧 Generating morning weather report...")
    result = generate_weather_report(
        report_type='morning',
        config=config
    )
    
    if not result.get('success', False):
        print(f"❌ FAILED: Report generation failed")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return False
    
    # Extract the actual email text
    email_text = result.get('report_text', '')
    
    print(f"📏 Email length: {len(email_text)} characters")
    print(f"📧 Email subject: {result.get('email_subject', 'No subject')}")
    
    # Check for alternative risk analysis
    print(f"\n🔍 CHECKING ALTERNATIVE RISK ANALYSIS INTEGRATION:")
    
    if "## 🔍 Alternative Risk Analysis" in email_text:
        print(f"✅ Alternative Risk Analysis: FOUND")
        
        # Check for specific content
        if "🔥 **Heat**" in email_text:
            print(f"✅ Heat analysis: FOUND")
        else:
            print(f"❌ Heat analysis: NOT FOUND")
            
        if "❄️ **Cold**" in email_text:
            print(f"✅ Cold analysis: FOUND")
        else:
            print(f"❌ Cold analysis: NOT FOUND")
            
        if "🌧️ **Rain**" in email_text:
            print(f"✅ Rain analysis: FOUND")
        else:
            print(f"❌ Rain analysis: NOT FOUND")
            
        if "⛈️ **Thunderstorm**" in email_text:
            print(f"✅ Thunderstorm analysis: FOUND")
        else:
            print(f"❌ Thunderstorm analysis: NOT FOUND")
            
        if "🌬️ **Wind**" in email_text:
            print(f"✅ Wind analysis: FOUND")
        else:
            print(f"❌ Wind analysis: NOT FOUND")
        
        # Check structure
        parts = email_text.split("---")
        if len(parts) >= 2:
            print(f"✅ Separator structure: CORRECT ({len(parts)} parts)")
            
            # Check that alternative analysis comes after separator
            after_separator = parts[-1]
            if "## 🔍 Alternative Risk Analysis" in after_separator:
                print(f"✅ Alternative analysis position: CORRECT (after separator)")
            else:
                print(f"❌ Alternative analysis position: INCORRECT")
        else:
            print(f"❌ Separator structure: INCORRECT")
            
    else:
        print(f"❌ Alternative Risk Analysis: NOT FOUND")
        print(f"❌ FAILED: Alternative risk analysis is not integrated!")
        return False
    
    # Check for debug info (should be present but not interfere)
    if "--- DEBUG INFO ---" in email_text:
        print(f"⚠️  Debug info: PRESENT (this is expected)")
    else:
        print(f"⚠️  Debug info: NOT PRESENT")
    
    # Show the actual email content
    print(f"\n📧 ACTUAL EMAIL CONTENT:")
    print("-" * 80)
    print(email_text)
    print("-" * 80)
    
    # Final verification
    print(f"\n🎯 FINAL VERIFICATION:")
    
    # Check that we have both standard report and alternative analysis
    if "Croci -" in email_text and "## 🔍 Alternative Risk Analysis" in email_text:
        print(f"✅ SUCCESS: Email contains both standard report AND alternative risk analysis!")
        print(f"✅ The alternative risk analysis is properly integrated into the email.")
        return True
    else:
        print(f"❌ FAILURE: Email is missing required components!")
        if "Croci -" not in email_text:
            print(f"   - Standard report missing")
        if "## 🔍 Alternative Risk Analysis" not in email_text:
            print(f"   - Alternative risk analysis missing")
        return False


def test_email_without_alternative_analysis():
    """Test email generation without alternative risk analysis."""
    print(f"\n🎯 TEST: Email Generation WITHOUT Alternative Risk Analysis")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    
    # Disable alternative risk analysis
    config["alternative_risk_analysis"] = {
        "enabled": False
    }
    
    print(f"✅ Configuration loaded with alternative risk analysis DISABLED")
    
    # Generate morning report
    print(f"📧 Generating morning weather report...")
    result = generate_weather_report(
        report_type='morning',
        config=config
    )
    
    if not result.get('success', False):
        print(f"❌ FAILED: Report generation failed")
        return False
    
    # Extract the actual email text
    email_text = result.get('report_text', '')
    
    # Check that alternative risk analysis is NOT present
    if "## 🔍 Alternative Risk Analysis" not in email_text:
        print(f"✅ SUCCESS: Alternative risk analysis correctly NOT included when disabled")
        return True
    else:
        print(f"❌ FAILURE: Alternative risk analysis incorrectly included when disabled")
        return False


if __name__ == "__main__":
    print("🚀 Starting Functional Email Tests")
    print("=" * 80)
    
    # Test 1: With alternative risk analysis
    success1 = test_real_email_generation()
    
    # Test 2: Without alternative risk analysis
    success2 = test_email_without_alternative_analysis()
    
    print(f"\n🎯 FINAL RESULTS:")
    print("=" * 80)
    
    if success1 and success2:
        print(f"✅ ALL TESTS PASSED!")
        print(f"✅ Alternative risk analysis integration is working correctly!")
        sys.exit(0)
    else:
        print(f"❌ SOME TESTS FAILED!")
        if not success1:
            print(f"   - Test with alternative risk analysis: FAILED")
        if not success2:
            print(f"   - Test without alternative risk analysis: FAILED")
        sys.exit(1) 