#!/usr/bin/env python3
"""
Test the ACTUAL email generation with real data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from src.notification.email_client import EmailClient


def test_actual_email():
    """Test the actual email generation with real data."""
    print("📧 Testing ACTUAL Email Generation")
    print("=" * 50)
    
    # Real configuration
    config = {
        "smtp": {
            "host": "smtp.gmail.com",
            "port": 587,
            "subject": "GR20",
            "to": "test@example.com",
            "user": "test@gmail.com"
        },
        "alternative_risk_analysis": {
            "enabled": True,
            "thunderstorm_timing": True,
            "geo_aggregation": True
        },
        "debug": {
            "enabled": True
        }
    }
    
    # Real report data (simulating what the real system would send)
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
        print("📊 Creating email client...")
        email_client = EmailClient(config)
        print("✅ Email client created")
        
        print("📊 Generating email report...")
        # This calls the REAL send_gr20_report method
        email_text = email_client.send_gr20_report(report_data)
        
        print("\n📋 ACTUAL EMAIL CONTENT:")
        print("=" * 50)
        print(email_text)
        
        # Check what was actually generated
        print("\n🔍 ACTUAL CONTENT ANALYSIS:")
        print("-" * 30)
        
        if "Alternative Risk Analysis" in str(email_text):
            print("✅ Alternative Risk Analysis: FOUND")
        else:
            print("❌ Alternative Risk Analysis: NOT FOUND")
        
        if "Debug" in str(email_text):
            print("✅ Debug Output: FOUND")
        else:
            print("❌ Debug Output: NOT FOUND")
        
        if "Thunderstorm" in str(email_text):
            print("✅ Thunderstorm: FOUND")
        else:
            print("❌ Thunderstorm: NOT FOUND")
        
        print(f"\n📏 Content type: {type(email_text)}")
        if isinstance(email_text, str):
            print(f"📏 Length: {len(email_text)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_actual_email()
    sys.exit(0 if success else 1) 