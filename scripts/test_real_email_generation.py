#!/usr/bin/env python3
"""
Simple test for real email generation with alternative risk analysis.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime


def test_email_generation():
    """Test the actual email generation function."""
    print("📧 Testing Real Email Generation")
    print("=" * 50)
    
    # Import the function directly
    try:
        from src.notification.email_client import generate_gr20_report_text
        print("✅ Successfully imported generate_gr20_report_text")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test configuration
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
    
    # Test report data
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
                }
            ]
        }
    }
    
    try:
        print("📊 Generating email report...")
        email_text = generate_gr20_report_text(report_data, config)
        
        print("\n📋 GENERATED EMAIL:")
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
        
        print(f"\n📏 Length: {len(email_text)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_email_generation()
    sys.exit(0 if success else 1) 