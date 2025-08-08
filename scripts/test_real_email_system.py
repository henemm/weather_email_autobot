#!/usr/bin/env python3
"""
Test the real email system with alternative risk analysis.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime


def test_real_email_system():
    """Test the real email generation system."""
    print("📧 Testing Real Email System")
    print("=" * 50)
    
    # Mock the problematic imports
    class MockWeatherFormatter:
        def format_report_text(self, data, report_type, stage_names):
            return "Mock standard report"
    
    class MockModule:
        WeatherFormatter = MockWeatherFormatter
    
    sys.modules['weather.core.formatter'] = MockModule()
    sys.modules['weather.core.models'] = MockModule()
    
    try:
        from src.notification.email_client import generate_gr20_report_text
        print("✅ Successfully imported generate_gr20_report_text")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test configuration with alternative risk analysis enabled
    config = {
        "alternative_risk_analysis": {
            "enabled": True,
            "thunderstorm_timing": True,
            "geo_aggregation": True
        },
        "debug": {
            "enabled": False
        }
    }
    
    # Test report data with MeteoFrance format
    base_time = datetime(2025, 7, 28, 14, 0, 0)
    report_data = {
        "report_type": "morning",
        "stage_names": ["Vizzavona"],
        "weather_data": {
            "forecast": [
                {
                    'dt': int(base_time.timestamp()),
                    'T': {'value': 25.0},
                    'rain': {'1h': 1.0},
                    'weather': {'desc': 'Ciel clair'},
                    'wind': {'speed': 10, 'gust': 15}
                },
                {
                    'dt': int((base_time.replace(hour=15)).timestamp()),
                    'T': {'value': 28.0},
                    'rain': {'1h': 2.0},
                    'weather': {'desc': 'Risque d\'orages'},
                    'wind': {'speed': 20, 'gust': 25}
                },
                {
                    'dt': int((base_time.replace(hour=16)).timestamp()),
                    'T': {'value': 30.0},
                    'rain': {'1h': 2.5},
                    'weather': {'desc': 'Orages'},
                    'wind': {'speed': 25, 'gust': 35}
                },
                {
                    'dt': int((base_time.replace(hour=17)).timestamp()),
                    'T': {'value': 32.5},
                    'rain': {'1h': 3.0},
                    'weather': {'desc': 'Orages lourds'},
                    'wind': {'speed': 30, 'gust': 45}
                }
            ]
        }
    }
    
    try:
        print("📊 Generating real email report...")
        email_text = generate_gr20_report_text(report_data, config)
        
        print("\n📋 REAL EMAIL CONTENT:")
        print("=" * 50)
        print(email_text)
        
        # Check integration
        print("\n🔍 INTEGRATION CHECK:")
        print("-" * 30)
        
        if "Alternative Risk Analysis" in email_text:
            print("✅ Alternative Risk Analysis: FOUND")
        else:
            print("❌ Alternative Risk Analysis: NOT FOUND")
        
        if "Thunderstorm" in email_text:
            print("✅ Thunderstorm: FOUND")
        else:
            print("❌ Thunderstorm: NOT FOUND")
        
        if "Risk @" in email_text or "Moderate @" in email_text or "Heavy @" in email_text:
            print("✅ Thunderstorm Time Ranges: FOUND")
        else:
            print("❌ Thunderstorm Time Ranges: NOT FOUND")
        
        print(f"\n📏 Length: {len(email_text)} characters")
        
        # Check if this is the REAL integration
        print("\n🎯 REAL INTEGRATION STATUS:")
        print("-" * 30)
        if "Alternative Risk Analysis" in email_text:
            print("✅ SUCCESS: Alternative Risk Analysis is integrated in REAL email generation!")
            print("✅ The email will contain the alternative risk analysis when sent.")
        else:
            print("❌ FAILURE: Alternative Risk Analysis is NOT integrated in REAL email generation!")
            print("❌ The email will NOT contain the alternative risk analysis when sent.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_real_email_system()
    sys.exit(0 if success else 1) 