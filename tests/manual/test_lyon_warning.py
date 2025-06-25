#!/usr/bin/env python3
"""
Test what our application would output as a warning for Lyon
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from wetter.warning import get_vigilance_summary
from wetter.fetch_openmeteo import fetch_openmeteo_forecast
from datetime import datetime

def main():
    print("🌤️  LYON WETTERWARNUNG - APP-AUSGABE")
    print("=" * 50)
    
    # Lyon coordinates
    lat, lon = 45.7578, 4.8320
    
    print(f"📍 Location: Lyon, France ({lat}, {lon})")
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # 1. Vigilance Warnings
    print("🔴 VIGILANCE WARNINGS:")
    vigilance_summary = get_vigilance_summary()
    
    if vigilance_summary['status'] == 'success':
        lyon_warnings = [w for w in vigilance_summary['warnings'] if w['domain_id'] == '69' and w['is_active']]
        
        if lyon_warnings:
            print(f"  ⚠️  ACTIVE WARNINGS: {len(lyon_warnings)}")
            for warning in lyon_warnings:
                print(f"    - {warning['german_summary']}")
                print(f"      Valid until: {warning['end_time']}")
        else:
            print("  ✅ No active warnings")
        
        print(f"  📊 Summary: {vigilance_summary['summary']}")
    else:
        print("  ❌ Vigilance data unavailable")
    print()
    
    # 2. Current Weather Data
    print("🌡️  CURRENT WEATHER:")
    try:
        weather_data = fetch_openmeteo_forecast(lat, lon)
        if weather_data and 'current' in weather_data:
            current = weather_data['current']
            print(f"  ✅ Temperature: {current.get('temperature_2m', 'N/A')}°C")
            print(f"  ✅ Precipitation: {current.get('precipitation', 'N/A')} mm/h")
            print(f"  ✅ Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h")
            print(f"  ✅ Wind Direction: {current.get('wind_direction_10m', 'N/A')}°")
            print(f"  ✅ Cloud Cover: {current.get('cloud_cover', 'N/A')}%")
        else:
            print("  ❌ Weather data unavailable")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # 3. Application Warning Output
    print("📱 APP WARNING OUTPUT:")
    print("=" * 30)
    
    if vigilance_summary['status'] == 'success' and lyon_warnings:
        # Generate warning message based on active warnings
        warning_levels = [w['risk_level'] for w in lyon_warnings]
        max_level = max(warning_levels) if warning_levels else 0
        
        # Get the most specific warning description
        specific_warnings = [w['german_summary'] for w in lyon_warnings if 'Unbekannt' not in w['german_summary']]
        if specific_warnings:
            warning_desc = specific_warnings[0]
        else:
            warning_desc = f"{len(lyon_warnings)} weather warnings"
        
        if max_level >= 3:  # Orange or Red
            print("🚨 HIGH RISK WARNING")
            print(f"Lyon: {warning_desc}")
            print(f"Risk Level: {max_level} (Orange/Red)")
            print(f"Valid until: {lyon_warnings[0]['end_time']}")
            print("⚠️  Exercise caution - monitor weather conditions")
        elif max_level == 2:  # Yellow
            print("⚠️  MODERATE RISK WARNING")
            print(f"Lyon: {warning_desc}")
            print("Stay informed about weather developments")
        else:
            print("✅ No significant weather risks")
    else:
        print("✅ No active weather warnings for Lyon")
    
    print()
    print("=" * 50)
    print("✅ Lyon weather warning analysis complete!")

if __name__ == "__main__":
    main() 