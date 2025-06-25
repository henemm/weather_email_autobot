#!/usr/bin/env python3
"""
Demo script for fetching Bustanico weather data from Météo-France APIs (WMS, WCS, Vigilance) using OAuth2.
- Always uses a valid WMS time from GetCapabilities
- Robust error handling and clear output
- Displays actual weather data values
"""

import os
import sys
import requests
import re
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from auth.meteo_token_provider import MeteoTokenProvider
except ImportError:
    from src.auth.meteo_token_provider import MeteoTokenProvider

# Bustanico coordinates
BUSTANICO_LAT = 42.308
BUSTANICO_LON = 8.937

def get_available_wms_times(token):
    """
    Fetch available WMS times from GetCapabilities.
    Args:
        token (str): OAuth2 access token
    Returns:
        list[str]: List of ISO8601 time strings
    """
    url = "https://public-api.meteofrance.fr/public/arome/1.0/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetCapabilities"
    params = {"service": "WMS", "version": "1.3.0", "language": "eng"}
    headers = {"Authorization": f"Bearer {token}", "Accept": "*/*"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            content = response.text
            time_pattern = r'<Dimension name="time" units="ISO8601">(.*?)</Dimension>'
            time_match = re.search(time_pattern, content)
            if time_match:
                time_values = time_match.group(1).strip().split(',')
                return [t.strip() for t in time_values if t.strip()]
            else:
                print("❌ No <Dimension name=\"time\"> found in WMS GetCapabilities.")
        else:
            print(f"❌ WMS GetCapabilities failed: {response.status_code} {response.text[:100]}")
    except Exception as e:
        print(f"❌ Error getting WMS times: {e}")
    return []

def get_wcs_temperature_data(token):
    """Get actual temperature data from WCS API."""
    url = "https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCoverage"
    params = {
        "service": "WCS",
        "version": "2.0.1",
        "request": "GetCoverage",
        "coverageId": "TEMPERATURE__GROUND_OR_WATER_SURFACE",
        "subset": f"Long({BUSTANICO_LON})",
        "subset": f"Lat({BUSTANICO_LAT})",
        "format": "application/gml+xml"
    }
    headers = {"Authorization": f"Bearer {token}", "Accept": "*/*"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            content = response.text
            # Extract temperature value from GML response
            temp_pattern = r'<gml:doubleOrNilReasonTupleList>(.*?)</gml:doubleOrNilReasonTupleList>'
            temp_match = re.search(temp_pattern, content)
            if temp_match:
                temp_value = temp_match.group(1).strip()
                return float(temp_value) if temp_value != "nil" else None
    except Exception as e:
        print(f"❌ Error getting WCS temperature: {e}")
    return None

def get_vigilance_details(token):
    """Get detailed vigilance warning information."""
    url = "https://public-api.meteofrance.fr/public/DPVigilance/v1/textesvigilance/encours"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "product" in data:
                product = data["product"]
                if "text_bloc_items" in product:
                    corsica_warnings = []
                    for bloc in product["text_bloc_items"]:
                        if bloc.get("domain_id") in ["2A", "2B", "CORSE"]:
                            corsica_warnings.append({
                                "domain": bloc.get("domain_id"),
                                "phenomenon": bloc.get("phenomenon_id"),
                                "level": bloc.get("level_id"),
                                "text": bloc.get("text", "")[:200] + "..." if len(bloc.get("text", "")) > 200 else bloc.get("text", "")
                            })
                    return corsica_warnings
    except Exception as e:
        print(f"❌ Error getting vigilance details: {e}")
    return []

def main():
    print("🌍 Bustanico Weather Demo - Météo-France APIs")
    print("=" * 50)
    print(f"📍 Location: Bustanico, Corsica ({BUSTANICO_LAT}, {BUSTANICO_LON})\n")
    
    # Check credentials
    client_id = os.getenv('METEOFRANCE_CLIENT_ID')
    client_secret = os.getenv('METEOFRANCE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ OAuth2 credentials missing\n   Set METEOFRANCE_CLIENT_ID and METEOFRANCE_CLIENT_SECRET")
        return
    
    print("✅ OAuth2 credentials found")
    
    # Get token
    try:
        token_provider = MeteoTokenProvider()
        token = token_provider.get_token()
        print(f"✅ OAuth2 token: {token[:20]}...")
    except Exception as e:
        print(f"❌ Token acquisition failed: {e}")
        return
    
    # Test WMS API
    print("\n🌤️  Testing WMS API...")
    
    # Get available times first
    available_times = get_available_wms_times(token)
    if available_times:
        print(f"   Found {len(available_times)} available times")
        # Use the most recent time
        latest_time = available_times[-1]
        print(f"   Using latest time: {latest_time}")
        
        url = "https://public-api.meteofrance.fr/public/arome/1.0/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetMap"
        params = {
            "service": "WMS",
            "version": "1.3.0",
            "request": "GetMap",
            "layers": "TEMPERATURE__GROUND_OR_WATER_SURFACE",
            "crs": "EPSG:4326",
            "bbox": f"{BUSTANICO_LON-0.1},{BUSTANICO_LAT-0.1},{BUSTANICO_LON+0.1},{BUSTANICO_LAT+0.1}",
            "width": 256,
            "height": 256,
            "format": "image/png",
            "time": latest_time
        }
        headers = {"Authorization": f"Bearer {token}", "Accept": "*/*"}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            print(f"WMS Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ WMS API works - Weather data available")
                print(f"   Image size: {len(response.content)} bytes")
            else:
                print(f"❌ WMS API failed: {response.text[:100]}")
        except Exception as e:
            print(f"❌ WMS API error: {e}")
    else:
        print("❌ Could not get available WMS times. No WMS request sent.")
    
    # Test WCS API
    print("\n📊 Testing WCS API...")
    url = "https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCapabilities"
    params = {"service": "WCS", "version": "2.0.1", "language": "eng"}
    headers = {"Authorization": f"Bearer {token}", "Accept": "*/*"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(f"WCS Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ WCS API works - Data download available")
            content = response.text.lower()
            if "temperature" in content:
                print("   ✅ Temperature data available")
            if "convective" in content:
                print("   ✅ Convective data available")
            
            # Get actual temperature data
            print("\n🌡️  Fetching actual temperature data...")
            temp_value = get_wcs_temperature_data(token)
            if temp_value is not None:
                print(f"   📍 Temperature at Bustanico: {temp_value:.1f}°C")
            else:
                print("   ❌ Could not retrieve temperature data")
        else:
            print(f"❌ WCS API failed: {response.text[:100]}")
    except Exception as e:
        print(f"❌ WCS API error: {e}")
    
    # Test Vigilance API
    print("\n🚨 Testing Vigilance API...")
    url = "https://public-api.meteofrance.fr/public/DPVigilance/v1/textesvigilance/encours"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Vigilance Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Vigilance API works - Warning data available")
            data = response.json()
            if "product" in data:
                product = data["product"]
                if "text_bloc_items" in product:
                    warnings_count = len(product["text_bloc_items"])
                    print(f"   ✅ Found {warnings_count} warning blocks")
                    
                    # Look for Corsica warnings
                    corsica_warnings = [b for b in product["text_bloc_items"] 
                                      if b.get("domain_id") in ["2A", "2B", "CORSE"]]
                    if corsica_warnings:
                        print(f"   ✅ Found {len(corsica_warnings)} Corsica warnings")
                        
                        # Get detailed warning information
                        print("\n⚠️  Corsica Warning Details:")
                        for warning in corsica_warnings:
                            print(f"   🏷️  Domain: {warning.get('domain_id', 'N/A')}")
                            print(f"   🌪️  Phenomenon: {warning.get('phenomenon_id', 'N/A')}")
                            print(f"   📊 Level: {warning.get('level_id', 'N/A')}")
                            print(f"   📝 Text: {warning.get('text', 'N/A')[:100]}...")
                            print()
                    else:
                        print("   ℹ️  No active warnings for Corsica")
        else:
            print(f"❌ Vigilance API failed: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Vigilance API error: {e}")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    main() 