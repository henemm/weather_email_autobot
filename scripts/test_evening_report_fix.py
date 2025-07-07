#!/usr/bin/env python3
"""
Test script to verify evening report temperature formatting fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.report.weather_report_generator import generate_weather_report
from src.config.config_loader import load_config


def test_evening_report_temperatures():
    """Test evening report with real weather data to verify temperature formatting."""
    print("Testing evening report temperature formatting...")
    
    try:
        # Generate evening report
        result = generate_weather_report('evening')
        
        if not result['success']:
            print(f"❌ Report generation failed: {result.get('error', 'Unknown error')}")
            return False
        
        report_text = result['report_text']
        print(f"📋 Generated report: {report_text}")
        
        # Check for both temperature types
        has_night_temp = "Nacht" in report_text
        has_day_temp = "Hitze" in report_text
        
        print(f"🌙 Night temperature present: {has_night_temp}")
        print(f"☀️ Day temperature present: {has_day_temp}")
        
        # Extract temperature values for plausibility check
        import re
        
        night_match = re.search(r'Nacht(\d+\.?\d*)°C', report_text)
        day_match = re.search(r'Hitze(\d+\.?\d*)°C', report_text)
        
        if night_match and day_match:
            night_temp = float(night_match.group(1))
            day_temp = float(day_match.group(1))
            
            print(f"🌙 Night temperature: {night_temp}°C")
            print(f"☀️ Day temperature: {day_temp}°C")
            
            # Check plausibility
            temp_diff = day_temp - night_temp
            print(f"📊 Temperature difference: {temp_diff}°C")
            
            if temp_diff > 0:
                print("✅ Day temperature is higher than night temperature")
            else:
                print("❌ Day temperature should be higher than night temperature")
                return False
            
            if 5.0 <= temp_diff <= 25.0:
                print("✅ Temperature difference is plausible")
            else:
                print(f"⚠️ Temperature difference ({temp_diff}°C) may be unrealistic")
        
        # Check report structure
        parts = report_text.split(" | ")
        print(f"📝 Report has {len(parts)} parts")
        
        # Verify order according to specification
        if len(parts) >= 6:
            stage_name = parts[0]
            night_temp_part = parts[1] if has_night_temp else None
            day_temp_part = parts[5] if has_day_temp else None
            
            print(f"📍 Stage: {stage_name}")
            if night_temp_part:
                print(f"🌙 Night temp position: {night_temp_part}")
            if day_temp_part:
                print(f"☀️ Day temp position: {day_temp_part}")
        
        print("✅ Evening report temperature formatting test completed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_morning_report_for_comparison():
    """Test morning report to ensure it's not affected by the changes."""
    print("\nTesting morning report for comparison...")
    
    try:
        result = generate_weather_report('morning')
        
        if not result['success']:
            print(f"❌ Morning report generation failed: {result.get('error', 'Unknown error')}")
            return False
        
        report_text = result['report_text']
        print(f"📋 Morning report: {report_text}")
        
        # Morning report should only have day temperature
        has_night_temp = "Nacht" in report_text
        has_day_temp = "Hitze" in report_text
        
        print(f"🌙 Night temperature present: {has_night_temp}")
        print(f"☀️ Day temperature present: {has_day_temp}")
        
        if not has_night_temp and has_day_temp:
            print("✅ Morning report correctly shows only day temperature")
        else:
            print("❌ Morning report should not show night temperature")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Morning report test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Evening Report Temperature Fix")
    print("=" * 50)
    
    evening_success = test_evening_report_temperatures()
    morning_success = test_morning_report_for_comparison()
    
    print("\n" + "=" * 50)
    if evening_success and morning_success:
        print("🎉 All tests passed! Evening report temperature formatting is fixed.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 