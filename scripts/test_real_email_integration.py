#!/usr/bin/env python3
"""
Test script for real email integration.

This script tests the actual email generation process to verify
if the alternative risk analysis is integrated.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from src.notification.email_client import generate_gr20_report_text


def main():
    """Test real email integration with alternative risk analysis."""
    print("📧 Real Email Integration Test")
    print("🎯 Testing Actual Email Generation with Alternative Risk Analysis")
    print("=" * 70)
    
    # Load configuration with alternative risk analysis enabled
    config = {
        "alternative_risk_analysis": {
            "enabled": True,
            "thunderstorm_timing": True,
            "geo_aggregation": True
        },
        "debug": {
            "enabled": False
        },
        "thresholds": {
            "thunderstorm_probability": 20.0,
            "rain_probability": 25.0,
            "rain_amount": 2.0,
            "wind_speed": 30.0,
            "temperature": 32.0
        }
    }
    
    # Sample report data that matches the REAL system structure
    base_time = datetime(2025, 7, 28, 14, 0, 0)
    report_data = {
        "report_type": "morning",
        "stage_names": ["Vizzavona"],
        "weather_data": {
            "location_name": "Vizzavona",
            "latitude": 42.0,
            "longitude": 9.0,
            "forecast": [
                {
                    'dt': int(base_time.timestamp()),  # 14:00
                    'T': {'value': 25.0},
                    'rain': {'1h': 1.0},
                    'weather': {'desc': 'Ciel clair'},
                    'wind': {'speed': 10, 'gust': 15}
                },
                {
                    'dt': int((base_time.replace(hour=15)).timestamp()),  # 15:00
                    'T': {'value': 28.0},
                    'rain': {'1h': 2.0},
                    'weather': {'desc': 'Risque d\'orages'},
                    'wind': {'speed': 20, 'gust': 25}
                },
                {
                    'dt': int((base_time.replace(hour=16)).timestamp()),  # 16:00
                    'T': {'value': 30.0},
                    'rain': {'1h': 2.5},
                    'weather': {'desc': 'Orages'},
                    'wind': {'speed': 25, 'gust': 35}
                },
                {
                    'dt': int((base_time.replace(hour=17)).timestamp()),  # 17:00
                    'T': {'value': 32.5},
                    'rain': {'1h': 3.0},
                    'weather': {'desc': 'Orages lourds'},
                    'wind': {'speed': 30, 'gust': 45}
                }
            ],
            # Standard weather data fields
            "max_thunderstorm_probability": 45.0,
            "thunderstorm_threshold_time": "15:00",
            "thunderstorm_threshold_pct": 30.0,
            "max_precipitation_probability": 60.0,
            "rain_threshold_time": "16:00",
            "rain_threshold_pct": 50.0,
            "max_precipitation": 3.0,
            "max_temperature": 32.5,
            "max_wind_speed": 45.0
        }
    }
    
    try:
        print("📊 Generating real email report...")
        
        # Generate email report text using the REAL function
        email_text = generate_gr20_report_text(report_data, config)
        
        print("\n📋 REAL EMAIL CONTENT:")
        print("=" * 70)
        print(email_text)
        
        # Check if alternative risk analysis is included
        print("\n🔍 INTEGRATION VERIFICATION:")
        print("-" * 40)
        
        if "Alternative Risikoanalyse" in email_text:
            print("✅ Alternative Risk Analysis: INTEGRATED")
        else:
            print("❌ Alternative Risk Analysis: NOT FOUND")
        
        if "Thunderstorm" in email_text:
            print("✅ Thunderstorm Timing: INTEGRATED")
        else:
            print("❌ Thunderstorm Timing: NOT FOUND")
        
        if "Risk @" in email_text or "Moderate @" in email_text or "Heavy @" in email_text:
            print("✅ Thunderstorm Time Ranges: INTEGRATED")
        else:
            print("❌ Thunderstorm Time Ranges: NOT FOUND")
        
        if "Heat" in email_text and "Cold" in email_text:
            print("✅ Temperature Analysis: INTEGRATED")
        else:
            print("❌ Temperature Analysis: NOT FOUND")
        
        if "Rain" in email_text:
            print("✅ Rain Analysis: INTEGRATED")
        else:
            print("❌ Rain Analysis: NOT FOUND")
        
        if "Wind" in email_text:
            print("✅ Wind Analysis: INTEGRATED")
        else:
            print("❌ Wind Analysis: NOT FOUND")
        
        # Show character count
        print(f"\n📏 CHARACTER COUNT: {len(email_text)}")
        
        if len(email_text) > 160:
            print("⚠️ WARNING: Email content exceeds 160 character limit!")
        else:
            print("✅ Email content within character limit")
        
        # Show thunderstorm timing details
        print("\n⛈️ THUNDERSTORM TIMING DETAILS:")
        print("-" * 40)
        lines = email_text.split('\n')
        for line in lines:
            if "Thunderstorm" in line:
                print(f"🚨 {line.strip()}")
                break
        
        # Check if this is the REAL integration
        print("\n🎯 REAL INTEGRATION STATUS:")
        print("-" * 40)
        if "Alternative Risikoanalyse" in email_text:
            print("✅ SUCCESS: Alternative Risk Analysis is integrated in REAL email generation!")
            print("✅ The email will contain the alternative risk analysis when sent.")
        else:
            print("❌ FAILURE: Alternative Risk Analysis is NOT integrated in REAL email generation!")
            print("❌ The email will NOT contain the alternative risk analysis when sent.")
            print("❌ The integration is only in the demo/test scripts, not in the real system.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during real email integration test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main()) 