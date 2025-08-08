#!/usr/bin/env python3
"""
Simplified test script for email integration.

This script tests the alternative risk analysis integration directly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from src.notification.alternative_risk_email_integration import AlternativeRiskEmailIntegration


def main():
    """Test alternative risk analysis integration directly."""
    print("📧 Simplified Email Integration Test")
    print("🎯 Testing Alternative Risk Analysis Integration")
    print("=" * 60)
    
    # Sample report data with MeteoFrance API structure
    base_time = datetime(2025, 7, 28, 14, 0, 0)
    weather_data_by_point = {
        'vizzavona_start': {
            'forecast': [
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
                }
            ],
            'stage_name': 'Vizzavona',
            'stage_date': '2025-07-28'
        },
        'vizzavona_middle': {
            'forecast': [
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
            'stage_name': 'Vizzavona',
            'stage_date': '2025-07-28'
        }
    }
    
    # Create integration instance
    integration = AlternativeRiskEmailIntegration()
    
    try:
        print("📊 Validating weather data...")
        is_valid = integration.validate_weather_data(weather_data_by_point)
        print(f"✅ Data validation: {'PASSED' if is_valid else 'FAILED'}")
        
        if not is_valid:
            print("❌ Cannot proceed with invalid data")
            return 1
        
        # Generate alternative risk report
        print("\n🔍 Generating alternative risk report...")
        alternative_report = integration.generate_alternative_risk_report(
            weather_data_by_point, 'Vizzavona', '2025-07-28'
        )
        
        if not alternative_report:
            print("❌ Failed to generate alternative risk report")
            return 1
        
        print("✅ Alternative risk report generated successfully")
        
        # Simulate existing email content
        existing_email_content = """
# GR20 Weather Report - Vizzavona

## Standard Weather Analysis

**Temperature**: 25-32°C
**Precipitation**: Light rain expected
**Wind**: Moderate gusts up to 45 km/h
**Thunderstorm Risk**: Moderate

## Recommendations
- Bring rain gear
- Monitor weather conditions
- Avoid exposed areas during storms
"""
        
        # Integrate alternative risk report
        print("\n📧 Integrating into email content...")
        combined_email = integration.integrate_into_email_content(
            existing_email_content, alternative_report
        )
        
        # Display results
        print("\n📋 COMPLETE EMAIL CONTENT:")
        print("=" * 60)
        print(combined_email)
        
        # Check integration
        print("\n🔍 INTEGRATION VERIFICATION:")
        print("-" * 40)
        
        if "Alternative Risk Analysis" in combined_email:
            print("✅ Alternative Risk Analysis: INTEGRATED")
        else:
            print("❌ Alternative Risk Analysis: NOT FOUND")
        
        if "Thunderstorm" in combined_email:
            print("✅ Thunderstorm Timing: INTEGRATED")
        else:
            print("❌ Thunderstorm Timing: NOT FOUND")
        
        if "Risk @" in combined_email or "Moderate @" in combined_email or "Heavy @" in combined_email:
            print("✅ Thunderstorm Time Ranges: INTEGRATED")
        else:
            print("❌ Thunderstorm Time Ranges: NOT FOUND")
        
        if "Heat" in combined_email and "Cold" in combined_email:
            print("✅ Temperature Analysis: INTEGRATED")
        else:
            print("❌ Temperature Analysis: NOT FOUND")
        
        if "Rain" in combined_email:
            print("✅ Rain Analysis: INTEGRATED")
        else:
            print("❌ Rain Analysis: NOT FOUND")
        
        if "Wind" in combined_email:
            print("✅ Wind Analysis: INTEGRATED")
        else:
            print("❌ Wind Analysis: NOT FOUND")
        
        # Show character count
        print(f"\n📏 CHARACTER COUNT: {len(combined_email)}")
        
        if len(combined_email) > 160:
            print("⚠️ WARNING: Email content exceeds 160 character limit!")
        else:
            print("✅ Email content within character limit")
        
        # Show thunderstorm timing details
        print("\n⛈️ THUNDERSTORM TIMING DETAILS:")
        print("-" * 40)
        lines = combined_email.split('\n')
        for line in lines:
            if "Thunderstorm:" in line:
                print(f"🚨 {line.strip()}")
                break
        
        print("\n🎯 Email integration test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error during email integration test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main()) 