#!/usr/bin/env python3
"""
Live weather data for Porto Vecchio, Corsica
Fetches data from all available weather APIs and displays comprehensive analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_arome_wcs import fetch_arome_wcs, fetch_arome_temperature, fetch_arome_precipitation
from wetter.fetch_openmeteo import fetch_openmeteo_forecast
from wetter.warning import get_vigilance_summary
from logic.analyse_weather import analyse_weather
import json
from datetime import datetime

def main():
    print("🌤️  PORTO VECCHIO LIVE WEATHER DATA")
    print("=" * 50)
    
    # Porto Vecchio coordinates
    lat, lon = 41.5911, 9.2794
    
    print(f"📍 Location: Porto Vecchio, Corsica ({lat}, {lon})")
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # 1. AROME_HR - High Resolution Model
    print("🔵 AROME_HR (High Resolution):")
    try:
        # Temperature
        temp_result = fetch_arome_temperature(lat, lon, "AROME_HR")
        if temp_result:
            print(f"  ✅ Temperature: {temp_result:.1f}°C")
        else:
            print(f"  ❌ Temperature: No data")
        
        # CAPE
        cape_result = fetch_arome_wcs(lat, lon, "AROME_HR", "CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY")
        if cape_result and cape_result.get('value') is not None:
            print(f"  ✅ CAPE: {cape_result['value']:.1f} {cape_result['unit']}")
        else:
            print(f"  ❌ CAPE: No data")
        
        # Precipitation
        precip_result = fetch_arome_precipitation(lat, lon, "AROME_HR")
        if precip_result:
            print(f"  ✅ Precipitation: {precip_result:.1f} mm/h")
        else:
            print(f"  ❌ Precipitation: No data")
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    print()
    
    # 2. AROME_HR_NOWCAST - Nowcast
    print("🟡 AROME_HR_NOWCAST (Nowcast):")
    try:
        precip_result = fetch_arome_precipitation(lat, lon, "AROME_HR_NOWCAST")
        print(f"   Niederschlag: {precip_result} mm/h")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # 3. PIAF_NOWCAST - PIAF
    print("🟠 PIAF_NOWCAST (PIAF):")
    try:
        precip_result = fetch_arome_precipitation(lat, lon, "PIAF_NOWCAST")
        print(f"   Niederschlag: {precip_result} mm/h")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # 4. OPENMETEO_GLOBAL - Global fallback
    print("🟢 OPENMETEO_GLOBAL (Global):")
    try:
        openmeteo_data = fetch_openmeteo_forecast(lat, lon)
        if openmeteo_data and 'current' in openmeteo_data:
            current = openmeteo_data['current']
            print(f"  ✅ Status: Success")
            print(f"  🌡️  Temperature: {current.get('temperature_2m', 'N/A')}°C")
            print(f"  🌧️  Precipitation: {current.get('precipitation', 'N/A')} mm/h")
            print(f"  💨 Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h")
            print(f"  💨 Wind Direction: {current.get('wind_direction_10m', 'N/A')}°")
        else:
            print(f"  ❌ Status: No data available")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    print()
    
    # 5. VIGILANCE_API - Weather Warnings
    print("🔴 VIGILANCE_API (Weather Warnings):")
    try:
        vigilance_summary = get_vigilance_summary()
        if vigilance_summary['status'] == 'success':
            print(f"  ✅ Status: Success")
            print(f"  📊 Summary: {vigilance_summary['summary']}")
            print(f"  🏝️  Corsica Warnings: {vigilance_summary['corsica_warnings']}")
            print(f"  🌍 Total Warnings: {vigilance_summary['total_warnings']}")
            print(f"  ⏰ Active Warnings: {vigilance_summary['active_warnings']}")
            
            # Show Corsica-specific details if any
            if vigilance_summary['corsica_details']:
                print("  🏝️  Corsica Details:")
                for warning in vigilance_summary['corsica_details']:
                    print(f"    - {warning['domain_name']}: {warning['risk_name']} ({warning['hazard']})")
                    print(f"      Time: {warning['start_time']} to {warning['end_time']}")
            else:
                print("  🏝️  No active warnings for Corsica")
                
            # Show nearby active warnings
            active_warnings = [w for w in vigilance_summary['warnings'] if w['is_active']]
            if active_warnings:
                print("  🌍 Nearby Active Warnings:")
                for warning in active_warnings[:5]:  # Show first 5
                    print(f"    - {warning['domain_name']}: {warning['risk_name']} ({warning['hazard']})")
        else:
            print(f"  ❌ Status: {vigilance_summary['status']}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    print()
    
    # 6. Integrated Weather Analysis
    print("🧠 INTEGRATED WEATHER ANALYSIS:")
    try:
        analysis = analyse_weather(lat, lon)
        if analysis['status'] == 'success':
            data = analysis['data']
            print(f"  ✅ Status: Success")
            print(f"  ⚠️  Risk Level: {data.get('risk_level', 'N/A')}")
            print(f"  📊 Risk Score: {data.get('risk_score', 'N/A')}")
            print(f"  🎯 Decision: {data.get('decision', 'N/A')}")
            print(f"  📝 Reasoning: {data.get('reasoning', 'N/A')}")
            
            # Show contributing factors
            factors = data.get('contributing_factors', {})
            if factors:
                print("  🔍 Contributing Factors:")
                for factor, value in factors.items():
                    print(f"    - {factor}: {value}")
        else:
            print(f"  ❌ Status: {analysis['status']}")
            print(f"  📝 Error: {analysis.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    print()
    
    print("=" * 50)
    print("✅ Live weather data analysis complete!")

if __name__ == "__main__":
    main() 