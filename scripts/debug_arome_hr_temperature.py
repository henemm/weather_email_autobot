#!/usr/bin/env python3
"""
Debug script for AROME_HR temperature issue.

This script analyzes why AROME_HR temperature requests fail.
"""

import sys
import os
import logging

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from wetter.fetch_arome_wcs import (
    fetch_arome_wcs,
    get_available_arome_layers,
    _find_layer_for_field
)
from utils.env_loader import get_env_var

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def debug_arome_hr_temperature():
    """Debug AROME_HR temperature issue."""
    print("🔍 Debugging AROME_HR Temperature Issue")
    print("=" * 50)
    
    if not get_env_var("METEOFRANCE_CLIENT_ID"):
        print("⚠️ METEOFRANCE_CLIENT_ID not set")
        return
    
    # Test coordinates for Conca, Corsica
    latitude = 41.75
    longitude = 9.35
    
    print(f"📍 Testing coordinates: lat={latitude}, lon={longitude}")
    
    # Get available layers
    print("\n📋 Getting available AROME_HR layers...")
    available_layers = get_available_arome_layers("AROME_HR")
    
    if not available_layers:
        print("❌ No available layers found")
        return
    
    print(f"📊 Found {len(available_layers)} available layers")
    
    # Find temperature layers
    temp_layers = [layer for layer in available_layers if 'TEMPERATURE' in layer]
    print(f"🌡️ Found {len(temp_layers)} temperature layers")
    
    # Show first 10 temperature layers
    for i, layer in enumerate(temp_layers[:10]):
        print(f"   {i+1}. {layer}")
    
    # Test different temperature layer types
    print("\n🧪 Testing different temperature layer types:")
    
    # Test 1: Ground temperature (no height required)
    print("\n🌡️ Test 1: Ground temperature (GROUND_OR_WATER_SURFACE)")
    ground_temp_layers = [layer for layer in temp_layers if 'GROUND_OR_WATER_SURFACE' in layer]
    if ground_temp_layers:
        test_layer = ground_temp_layers[0]
        print(f"   Using layer: {test_layer}")
        try:
            result = fetch_arome_wcs(latitude, longitude, "AROME_HR", "TEMPERATURE")
            if result:
                print("✅ AROME_HR Temperature: Success")
                print(f"   Layer: {test_layer}")
                print(f"   Value: {result.get('value')}")
                print(f"   Unit: {result.get('unit')}")
                print(f"   Data Size: {result.get('data_size')}")
            else:
                print("   ❌ No data returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print("   ⚠️ No ground temperature layers found")
    
    # Test 2: Specific height temperature with height parameter
    print("\n🌡️ Test 2: Specific height temperature with height=2")
    height_temp_layers = [layer for layer in temp_layers if 'SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND' in layer]
    if height_temp_layers:
        test_layer = height_temp_layers[0]
        print(f"   Using layer: {test_layer}")
        try:
            result = fetch_arome_wcs(latitude, longitude, "AROME_HR", "TEMPERATURE", height_level="2")
            if result:
                print("✅ AROME_HR Temperature: Success")
                print(f"   Layer: {test_layer}")
                print(f"   Value: {result.get('value')}")
                print(f"   Unit: {result.get('unit')}")
                print(f"   Data Size: {result.get('data_size')}")
            else:
                print("   ❌ No data returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print("   ⚠️ No height temperature layers found")
    
    # Test 3: Try with different height values
    print("\n🌡️ Test 3: Testing different height values")
    if height_temp_layers:
        test_layer = height_temp_layers[0]
        for height in ["surface", "2", "10", "50"]:
            print(f"   Testing height={height}")
            try:
                result = fetch_arome_wcs(latitude, longitude, "AROME_HR", "TEMPERATURE", height_level=height)
                if result:
                    print("✅ AROME_HR Temperature: Success")
                    print(f"   Layer: {test_layer}")
                    print(f"   Value: {result.get('value')}")
                    print(f"   Unit: {result.get('unit')}")
                    print(f"   Data Size: {result.get('data_size')}")
                    break
                else:
                    print(f"   ❌ No data with height={height}")
            except Exception as e:
                print(f"   ❌ Error with height={height}: {e}")
    
    # Test 4: Try different coordinates
    print("\n🌡️ Test 4: Testing different coordinates")
    test_coordinates = [
        (42.0, 9.0),  # Different location in Corsica
        (48.8566, 2.3522),  # Paris
        (43.2965, 5.3698),  # Marseille
    ]
    
    for lat, lon in test_coordinates:
        print(f"   Testing coordinates: lat={lat}, lon={lon}")
        try:
            result = fetch_arome_wcs(lat, lon, "AROME_HR", "TEMPERATURE")
            if result:
                print("✅ AROME_HR Temperature: Success")
                print(f"   Layer: {test_layer}")
                print(f"   Value: {result.get('value')}")
                print(f"   Unit: {result.get('unit')}")
                print(f"   Data Size: {result.get('data_size')}")
                break
            else:
                print("   ❌ No data returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    debug_arome_hr_temperature() 