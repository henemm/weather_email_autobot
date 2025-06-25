#!/usr/bin/env python3
"""
Demo script for fetching weather data from all three Météo-France APIs.

This script demonstrates the complete OAuth2-authenticated weather data fetching
for Bustanico, Corsica using:
1. AROME WCS (temperature, precipitation, wind, etc.)
2. AROME Instability (CAPE, CIN, Lifted Index)
3. AROME Thunderstorm Probability
4. Vigilance Warnings

All APIs use the new OAuth2 Client Credentials flow.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from wetter.fetch_arome_wcs import fetch_arome_wcs_data, fetch_weather_for_position
    from wetter.fetch_arome_instability import fetch_arome_instability_layer
    from wetter.fetch_arome_thunder import fetch_arome_thunder_probability
    from wetter.warning import fetch_warnings
    from auth.meteo_token_provider import MeteoTokenProvider
except ImportError:
    # Fallback for different import paths
    from src.wetter.fetch_arome_wcs import fetch_arome_wcs_data, fetch_weather_for_position
    from src.wetter.fetch_arome_instability import fetch_arome_instability_layer
    from src.wetter.fetch_arome_thunder import fetch_arome_thunder_probability
    from src.wetter.warning import fetch_warnings
    from src.auth.meteo_token_provider import MeteoTokenProvider


# Bustanico, Corsica coordinates
BUSTANICO_LATITUDE = 42.308
BUSTANICO_LONGITUDE = 8.937

# Target time: today 18:00
TARGET_TIME = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)


def check_oauth2_credentials():
    """Check if OAuth2 credentials are available."""
    print("🔐 OAuth2 Credentials Check")
    print("=" * 50)
    
    client_id = os.getenv('METEOFRANCE_CLIENT_ID')
    client_secret = os.getenv('METEOFRANCE_CLIENT_SECRET')
    
    if client_id and client_secret:
        print("✅ OAuth2 credentials found")
        print(f"   Client ID: {client_id[:10]}...")
        print(f"   Client Secret: {'*' * len(client_secret)}")
        return True
    else:
        print("❌ OAuth2 credentials missing")
        print("   Required environment variables:")
        print("   - METEOFRANCE_CLIENT_ID")
        print("   - METEOFRANCE_CLIENT_SECRET")
        return False


def test_oauth2_token():
    """Test OAuth2 token acquisition."""
    print("\n🔑 OAuth2 Token Test")
    print("=" * 50)
    
    try:
        token_provider = MeteoTokenProvider()
        token = token_provider.get_token()
        
        print("✅ OAuth2 token acquired successfully")
        print(f"   Token: {token[:20]}...")
        print(f"   Length: {len(token)} characters")
        
        # Check token expiry
        if token_provider._token_expiry:
            print(f"   Expires: {token_provider._token_expiry}")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth2 token acquisition failed: {e}")
        return False


def fetch_arome_weather_data():
    """Fetch comprehensive AROME weather data."""
    print("\n🌤️  AROME Weather Data")
    print("=" * 50)
    
    try:
        # Fetch comprehensive weather data
        weather_data = fetch_weather_for_position(BUSTANICO_LATITUDE, BUSTANICO_LONGITUDE)
        
        print("✅ AROME weather data fetched successfully")
        print(f"   Data points: {len(weather_data.points)}")
        
        # Show data for target time (18:00)
        target_data = None
        for point in weather_data.points:
            if point.time.hour == 18:
                target_data = point
                break
        
        if target_data:
            print(f"\n📅 Weather for {target_data.time.strftime('%Y-%m-%d %H:%M')}:")
            print(f"   Temperature: {target_data.temperature:.1f}°C")
            print(f"   Feels like: {target_data.feels_like:.1f}°C")
            print(f"   Precipitation: {target_data.precipitation:.1f} mm/h")
            print(f"   Wind: {target_data.wind_speed:.1f} km/h at {target_data.wind_direction:.0f}°")
            print(f"   Cloud cover: {target_data.cloud_cover:.0f}%")
            
            if target_data.thunderstorm_probability is not None:
                print(f"   Thunderstorm probability: {target_data.thunderstorm_probability:.1f}%")
        else:
            print("⚠️  No data available for 18:00")
        
        return weather_data
        
    except Exception as e:
        print(f"❌ AROME weather data fetch failed: {e}")
        return None


def fetch_instability_data():
    """Fetch AROME instability indicators."""
    print("\n⚡ Instability Indicators")
    print("=" * 50)
    
    layers = {
        "CAPE": "CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
        "CIN": "CONVECTIVE_INHIBITION__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
        "LI": "LIFTED_INDEX__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND"
    }
    
    results = {}
    
    for layer_name, layer_id in layers.items():
        try:
            data = fetch_arome_instability_layer(BUSTANICO_LATITUDE, BUSTANICO_LONGITUDE, layer_id)
            
            print(f"✅ {layer_name} data fetched")
            print(f"   Layer: {data.layer}")
            print(f"   Unit: {data.unit}")
            print(f"   Data points: {len(data.times)}")
            
            if data.times and data.values:
                latest_value = data.values[0]
                latest_time = data.times[0]
                print(f"   Latest ({latest_time.strftime('%H:%M')}): {latest_value} {data.unit}")
                
                # Risk assessment
                if layer_name == "CAPE":
                    if latest_value > 800:
                        print("   ⚠️  High instability (CAPE > 800 J/kg)")
                    elif latest_value > 500:
                        print("   ⚡ Moderate instability (CAPE > 500 J/kg)")
                    else:
                        print("   ✅ Low instability (CAPE ≤ 500 J/kg)")
                        
                elif layer_name == "CIN":
                    if latest_value < -50:
                        print("   ⚡ Low inhibition (CIN < -50 J/kg)")
                    else:
                        print("   ✅ Significant inhibition (CIN ≥ -50 J/kg)")
                        
                elif layer_name == "LI":
                    if latest_value < -4:
                        print("   ⚠️  High severe weather potential (LI < -4°C)")
                    elif latest_value < -2:
                        print("   ⚡ Moderate instability (LI < -2°C)")
                    else:
                        print("   ✅ Stable conditions (LI ≥ -2°C)")
            
            results[layer_name] = data
            
        except Exception as e:
            print(f"❌ {layer_name} fetch failed: {e}")
            results[layer_name] = None
    
    return results


def fetch_thunderstorm_probability():
    """Fetch AROME thunderstorm probability."""
    print("\n⛈️  Thunderstorm Probability")
    print("=" * 50)
    
    try:
        data = fetch_arome_thunder_probability(BUSTANICO_LATITUDE, BUSTANICO_LONGITUDE)
        
        print("✅ Thunderstorm probability data fetched")
        print(f"   Layer: {data.layer}")
        print(f"   Unit: {data.unit}")
        print(f"   Data points: {len(data.times)}")
        
        if data.times and data.values:
            latest_value = data.values[0]
            latest_time = data.times[0]
            print(f"   Latest ({latest_time.strftime('%H:%M')}): {latest_value}%")
            
            # Risk assessment
            if latest_value > 70:
                print("   🚨 Very high thunderstorm probability (>70%)")
            elif latest_value > 50:
                print("   ⚠️  High thunderstorm probability (>50%)")
            elif latest_value > 30:
                print("   ⚡ Moderate thunderstorm probability (>30%)")
            else:
                print("   ✅ Low thunderstorm probability (≤30%)")
        
        return data
        
    except Exception as e:
        print(f"❌ Thunderstorm probability fetch failed: {e}")
        return None


def fetch_vigilance_warnings():
    """Fetch Vigilance weather warnings."""
    print("\n🚨 Vigilance Warnings")
    print("=" * 50)
    
    try:
        warnings = fetch_warnings(BUSTANICO_LATITUDE, BUSTANICO_LONGITUDE)
        
        print("✅ Vigilance warnings fetched")
        print(f"   Warnings found: {len(warnings)}")
        
        if warnings:
            for i, warning in enumerate(warnings, 1):
                print(f"\n   Warning {i}:")
                print(f"     Type: {warning.type}")
                print(f"     Level: {warning.level}")
                print(f"     Start: {warning.start_time}")
                print(f"     End: {warning.end_time}")
                
                # Level interpretation
                if warning.level == 1:
                    print("     🟡 Yellow - Be aware")
                elif warning.level == 2:
                    print("     🟠 Orange - Be prepared")
                elif warning.level == 3:
                    print("     🔴 Red - Take action")
                elif warning.level == 4:
                    print("     🟣 Purple - Extreme danger")
        else:
            print("   ✅ No active warnings")
        
        return warnings
        
    except Exception as e:
        print(f"❌ Vigilance warnings fetch failed: {e}")
        return None


def generate_summary_report(weather_data, instability_data, thunder_data, warnings):
    """Generate a summary report."""
    print("\n📊 Summary Report for Bustanico, Corsica")
    print("=" * 60)
    print(f"📍 Location: {BUSTANICO_LATITUDE}, {BUSTANICO_LONGITUDE}")
    print(f"🕐 Target time: {TARGET_TIME.strftime('%Y-%m-%d %H:%M')}")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Weather summary
    if weather_data and weather_data.points:
        target_point = None
        for point in weather_data.points:
            if point.time.hour == 18:
                target_point = point
                break
        
        if target_point:
            print(f"\n🌤️  Weather Conditions:")
            print(f"   Temperature: {target_point.temperature:.1f}°C")
            print(f"   Precipitation: {target_point.precipitation:.1f} mm/h")
            print(f"   Wind: {target_point.wind_speed:.1f} km/h")
            print(f"   Cloud cover: {target_point.cloud_cover:.0f}%")
    
    # Instability summary
    if instability_data:
        cape_data = instability_data.get("CAPE")
        if cape_data and cape_data.values:
            cape_value = cape_data.values[0]
            print(f"\n⚡ Instability:")
            print(f"   CAPE: {cape_value:.0f} J/kg")
            if cape_value > 800:
                print("   ⚠️  High instability conditions")
            elif cape_value > 500:
                print("   ⚡ Moderate instability conditions")
            else:
                print("   ✅ Stable conditions")
    
    # Thunderstorm summary
    if thunder_data and thunder_data.values:
        thunder_value = thunder_data.values[0]
        print(f"\n⛈️  Thunderstorm Risk:")
        print(f"   Probability: {thunder_value:.1f}%")
        if thunder_value > 70:
            print("   🚨 Very high risk")
        elif thunder_value > 50:
            print("   ⚠️  High risk")
        elif thunder_value > 30:
            print("   ⚡ Moderate risk")
        else:
            print("   ✅ Low risk")
    
    # Warnings summary
    if warnings:
        print(f"\n🚨 Active Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"   • {warning.type} (Level {warning.level})")
    else:
        print(f"\n✅ No active warnings")
    
    print("\n" + "=" * 60)


def main():
    """Main function to run the complete demo."""
    print("🌍 Bustanico Weather Demo - All Météo-France APIs")
    print("=" * 60)
    print(f"📍 Location: Bustanico, Corsica ({BUSTANICO_LATITUDE}, {BUSTANICO_LONGITUDE})")
    print(f"🕐 Target time: {TARGET_TIME.strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Check credentials
    if not check_oauth2_credentials():
        print("\n❌ Cannot proceed without OAuth2 credentials")
        return
    
    # Test token
    if not test_oauth2_token():
        print("\n❌ Cannot proceed without valid OAuth2 token")
        return
    
    # Fetch all data
    weather_data = fetch_arome_weather_data()
    instability_data = fetch_instability_data()
    thunder_data = fetch_thunderstorm_probability()
    warnings = fetch_vigilance_warnings()
    
    # Generate summary
    generate_summary_report(weather_data, instability_data, thunder_data, warnings)
    
    print("✅ Demo completed successfully!")


if __name__ == "__main__":
    main() 