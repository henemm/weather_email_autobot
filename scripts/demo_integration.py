#!/usr/bin/env python3
"""
Demo script for complete integration.

This script demonstrates the complete integration of:
- GEO-point aggregation
- Alternative risk analysis
- Email integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from src.notification.alternative_risk_email_integration import AlternativeRiskEmailIntegration


def main():
    """Demonstrate complete integration with sample data."""
    print("🌤️ Complete Integration Demo")
    print("🎯 GEO-Points + Alternative Risk Analysis + Email Integration")
    print("=" * 70)
    
    # Sample weather data from multiple GEO-points
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
        },
        'vizzavona_end': {
            'forecast': [
                {
                    'dt': int((base_time.replace(hour=18)).timestamp()),  # 18:00
                    'T': {'value': 29.0},
                    'rain': {'1h': 1.5},
                    'weather': {'desc': 'Pluie'},
                    'wind': {'speed': 15, 'gust': 20}
                }
            ],
            'stage_name': 'Vizzavona',
            'stage_date': '2025-07-28'
        }
    }
    
    # Create integration instance
    integration = AlternativeRiskEmailIntegration()
    
    try:
        # Validate weather data
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
        
        if alternative_report:
            print("✅ Alternative risk report generated successfully")
        else:
            print("❌ Failed to generate alternative risk report")
            return 1
        
        # Get night temperature info
        print("\n🌙 Getting night temperature information...")
        night_temp_info = integration.get_night_temperature_info(weather_data_by_point)
        if night_temp_info:
            print(f"✅ {night_temp_info}")
        else:
            print("⚠️ No night temperature data available")
        
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
        print("=" * 70)
        print(combined_email)
        
        # Show integration summary
        print("\n📊 INTEGRATION SUMMARY:")
        print("-" * 40)
        print(f"✅ GEO-points processed: {len(weather_data_by_point)}")
        print(f"✅ Weather data aggregated: {sum(len(data['forecast']) for data in weather_data_by_point.values())} entries")
        print(f"✅ Alternative risk analysis: COMPLETED")
        print(f"✅ Email integration: COMPLETED")
        print(f"✅ Night temperature: {night_temp_info or 'N/A'}")
        
        # Show thunderstorm timing (most important for hikers)
        print("\n⛈️ THUNDERSTORM TIMING FOR HIKERS:")
        print("-" * 40)
        if "Thunderstorm:" in alternative_report:
            thunderstorm_line = [line for line in alternative_report.split('\n') if "Thunderstorm:" in line][0]
            print(f"🚨 {thunderstorm_line}")
            print("\n🥾 HIKER RECOMMENDATIONS:")
            print("   • Plan your hike to avoid thunderstorm hours")
            print("   • Seek shelter before thunderstorms arrive")
            print("   • Avoid exposed ridges and summits during storms")
            print("   • Monitor weather conditions closely")
        else:
            print("✅ No thunderstorm risk detected")
        
        print("\n🎯 Integration demo completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error during integration demo: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 