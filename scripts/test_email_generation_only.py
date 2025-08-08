#!/usr/bin/env python3
"""
Test ONLY the email generation function without EmailClient.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime


def test_email_generation_only():
    """Test only the email generation function."""
    print("📧 Testing Email Generation Function ONLY")
    print("=" * 50)
    
    # Mock the missing imports
    class MockLogger:
        def info(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass
    
    import logging
    logging.getLogger = lambda: MockLogger()
    
    try:
        from src.notification.email_client import generate_gr20_report_text
        print("✅ Successfully imported generate_gr20_report_text")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Real configuration
    config = {
        "alternative_risk_analysis": {
            "enabled": True,
            "thunderstorm_timing": True,
            "geo_aggregation": True
        },
        "debug": {
            "enabled": True
        }
    }
    
    # Real report data
    report_data = {
        "location": "Vizzavona",
        "report_type": "morning",
        "stage_names": ["Vizzavona"],
        "weather_data": {
            "location_name": "Vizzavona",
            "latitude": 42.0,
            "longitude": 9.0,
            "forecast": [
                {
                    'dt': int(datetime(2025, 7, 28, 14, 0, 0).timestamp()),
                    'T': {'value': 25.0},
                    'rain': {'1h': 1.0},
                    'weather': {'desc': 'Ciel clair'},
                    'wind': {'speed': 10, 'gust': 15}
                },
                {
                    'dt': int(datetime(2025, 7, 28, 15, 0, 0).timestamp()),
                    'T': {'value': 28.0},
                    'rain': {'1h': 2.0},
                    'weather': {'desc': 'Risque d\'orages'},
                    'wind': {'speed': 20, 'gust': 25}
                },
                {
                    'dt': int(datetime(2025, 7, 28, 16, 0, 0).timestamp()),
                    'T': {'value': 30.0},
                    'rain': {'1h': 2.5},
                    'weather': {'desc': 'Orages'},
                    'wind': {'speed': 25, 'gust': 35}
                }
            ]
        },
        "report_time": datetime.now()
    }
    
    try:
        print("📊 Generating email report...")
        email_text = generate_gr20_report_text(report_data, config)
        
        print("\n📋 GENERATED EMAIL CONTENT:")
        print("=" * 50)
        print(email_text)
        
        # Check what was actually generated
        print("\n🔍 CONTENT ANALYSIS:")
        print("-" * 30)
        
        if "Alternative Risk Analysis" in email_text:
            print("✅ Alternative Risk Analysis: FOUND")
        else:
            print("❌ Alternative Risk Analysis: NOT FOUND")
        
        if "Debug" in email_text:
            print("✅ Debug Output: FOUND")
        else:
            print("❌ Debug Output: NOT FOUND")
        
        if "Thunderstorm" in email_text:
            print("✅ Thunderstorm: FOUND")
        else:
            print("❌ Thunderstorm: NOT FOUND")
        
        print(f"\n📏 Length: {len(email_text)} characters")
        
        # Show the actual structure
        print("\n📋 EMAIL STRUCTURE:")
        print("-" * 30)
        lines = email_text.split('\n')
        for i, line in enumerate(lines):
            if line.strip():
                print(f"{i+1:2d}: {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_email_generation_only()
    sys.exit(0 if success else 1) 