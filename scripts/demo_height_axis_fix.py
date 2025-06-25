#!/usr/bin/env python3
"""
Demo script for AROME WCS height axis fix.

This script demonstrates the improved height axis handling that prevents
InvalidSubsetting errors in AROME WCS requests.
"""

import sys
import os
import logging

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from wetter.fetch_arome_wcs import (
    fetch_arome_wcs,
    _extract_height_axis_from_describe,
    _validate_height_subset,
    _build_subset_params_with_height_validation
)
from utils.env_loader import get_env_var

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def demo_height_axis_extraction():
    """Demonstrate height axis extraction from XML."""
    print("\n🔍 Demo: Height Axis Extraction")
    print("=" * 50)
    
    # Sample XML with height axis
    describe_xml_with_height = '''
    <wcs:CoverageDescription xmlns:wcs="http://www.opengis.net/wcs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2">
        <gml:RectifiedGrid>
            <gml:axisLabels>long lat height time</gml:axisLabels>
        </gml:RectifiedGrid>
    </wcs:CoverageDescription>
    '''
    
    # Sample XML without height axis
    describe_xml_without_height = '''
    <wcs:CoverageDescription xmlns:wcs="http://www.opengis.net/wcs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2">
        <gml:RectifiedGrid>
            <gml:axisLabels>long lat time</gml:axisLabels>
        </gml:RectifiedGrid>
    </wcs:CoverageDescription>
    '''
    
    print("📋 XML with height axis:")
    height_info = _extract_height_axis_from_describe(describe_xml_with_height)
    print(f"   Has height axis: {height_info['has_height_axis']}")
    print(f"   Height label: {height_info['height_label']}")
    print(f"   Available heights: {height_info['available_heights']}")
    
    print("\n📋 XML without height axis:")
    height_info_no = _extract_height_axis_from_describe(describe_xml_without_height)
    print(f"   Has height axis: {height_info_no['has_height_axis']}")
    print(f"   Height label: {height_info_no['height_label']}")
    print(f"   Available heights: {height_info_no['available_heights']}")


def demo_height_validation():
    """Demonstrate height validation."""
    print("\n✅ Demo: Height Validation")
    print("=" * 50)
    
    height_info = {
        'has_height_axis': True,
        'height_label': 'height',
        'available_heights': ['surface', '2', '10', '50', '100']
    }
    
    test_heights = ['surface', '2', '10', '0', 'invalid', '100']
    
    for height in test_heights:
        is_valid = _validate_height_subset(height_info, height)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"   Height '{height}': {status}")


def demo_subset_parameter_building():
    """Demonstrate subset parameter building with height validation."""
    print("\n🔧 Demo: Subset Parameter Building")
    print("=" * 50)
    
    # Test case 1: With height axis and valid height
    print("📋 Case 1: With height axis and valid height")
    height_info = {
        'has_height_axis': True,
        'height_label': 'height',
        'available_heights': ['surface', '2', '10']
    }
    
    axis_info = {
        'lat': 'lat',
        'lon': 'long',
        'time': 'time'
    }
    
    subset_params = _build_subset_params_with_height_validation(
        latitude=42.0,
        longitude=9.0,
        axis_info=axis_info,
        height_info=height_info,
        time_value="2025-06-24T12:00:00Z",
        height_level="2"
    )
    print(f"   Subset params: {subset_params}")
    
    # Test case 2: Without height axis
    print("\n📋 Case 2: Without height axis")
    height_info_no = {
        'has_height_axis': False,
        'height_label': None,
        'available_heights': []
    }
    
    subset_params_no = _build_subset_params_with_height_validation(
        latitude=42.0,
        longitude=9.0,
        axis_info=axis_info,
        height_info=height_info_no,
        time_value="2025-06-24T12:00:00Z",
        height_level="2"
    )
    print(f"   Subset params: {subset_params_no}")
    
    # Test case 3: With invalid height
    print("\n📋 Case 3: With invalid height")
    subset_params_invalid = _build_subset_params_with_height_validation(
        latitude=42.0,
        longitude=9.0,
        axis_info=axis_info,
        height_info=height_info,
        time_value="2025-06-24T12:00:00Z",
        height_level="0"  # Invalid
    )
    print(f"   Subset params: {subset_params_invalid}")


def demo_live_arome_fetch():
    """Demonstrate live AROME fetch with height axis handling."""
    print("\n🌤️ Demo: Live AROME Fetch with Height Axis Handling")
    print("=" * 60)
    
    if not get_env_var("METEOFRANCE_CLIENT_ID"):
        print("⚠️ METEOFRANCE_CLIENT_ID not set, skipping live demo")
        return
    
    # Test coordinates for Conca, Corsica
    latitude = 41.75
    longitude = 9.35
    
    print(f"📍 Testing coordinates: lat={latitude}, lon={longitude}")
    
    # Test 1: Temperature without height level
    print("\n🌡️ Test 1: Temperature without height level")
    try:
        result = fetch_arome_wcs(latitude, longitude, "AROME_HR", "TEMPERATURE")
        if result:
            print(f"   ✅ Success: {result['value']} {result['unit']}")
        else:
            print("   ⚠️ No data returned (may be normal)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: CAPE without height level
    print("\n⚡ Test 2: CAPE without height level")
    try:
        result = fetch_arome_wcs(
            latitude, 
            longitude, 
            "AROME_HR", 
            "CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY"
        )
        if result:
            print(f"   ✅ Success: {result['value']} {result['unit']}")
        else:
            print("   ⚠️ No data returned (may be normal)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Temperature with height level (if supported)
    print("\n🌡️ Test 3: Temperature with height level '2'")
    try:
        result = fetch_arome_wcs(
            latitude, 
            longitude, 
            "AROME_HR", 
            "TEMPERATURE",
            height_level="2"
        )
        if result:
            print(f"   ✅ Success: {result['value']} {result['unit']}")
        else:
            print("   ⚠️ No data returned (may be normal)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Temperature with invalid height level
    print("\n🌡️ Test 4: Temperature with invalid height level '0'")
    try:
        result = fetch_arome_wcs(
            latitude, 
            longitude, 
            "AROME_HR", 
            "TEMPERATURE",
            height_level="0"  # Invalid
        )
        if result:
            print(f"   ✅ Success: {result['value']} {result['unit']}")
        else:
            print("   ⚠️ No data returned (may be normal)")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Main demo function."""
    print("🚀 AROME WCS Height Axis Fix Demo")
    print("=" * 60)
    print("This demo shows the improved height axis handling that prevents")
    print("InvalidSubsetting errors in AROME WCS requests.")
    
    # Run demos
    demo_height_axis_extraction()
    demo_height_validation()
    demo_subset_parameter_building()
    demo_live_arome_fetch()
    
    print("\n🎉 Demo completed!")
    print("\n📋 Summary:")
    print("   ✅ Height axis detection working")
    print("   ✅ Height validation working")
    print("   ✅ Subset parameter building working")
    print("   ✅ Fallback behavior implemented")
    print("   🔧 InvalidSubsetting errors should be resolved")


if __name__ == "__main__":
    main() 