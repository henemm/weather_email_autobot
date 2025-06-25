#!/usr/bin/env python3
"""
Demo script for AROME instability layers functionality.

This script demonstrates how to fetch meteorological instability indicators
(CAPE, CIN, Lifted Index) from the Météo-France AROME WCS service.
"""

import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_arome_instability import fetch_arome_instability_layer


def demo_instability_layers():
    """Demonstrate fetching instability layer data."""
    
    # Test coordinates (Corsica, France)
    latitude = 42.5
    longitude = 9.0
    
    # Supported layer names
    layers = {
        "CAPE": "CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
        "CIN": "CONVECTIVE_INHIBITION__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
        "LI": "LIFTED_INDEX__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND"
    }
    
    print("🌩️  AROME Instability Layers Demo")
    print("=" * 50)
    print(f"📍 Location: lat={latitude}, lon={longitude}")
    print()
    
    for layer_name, layer_id in layers.items():
        print(f"🔍 Fetching {layer_name} data...")
        try:
            result = fetch_arome_instability_layer(latitude, longitude, layer_id)
            
            print(f"✅ {layer_name} data retrieved successfully")
            print(f"   Layer: {result.layer}")
            print(f"   Unit: {result.unit}")
            print(f"   Data points: {len(result.times)}")
            
            if result.times and result.values:
                print(f"   Latest value: {result.values[0]} {result.unit}")
                print(f"   Latest time: {result.times[0]}")
                
                # Show threshold analysis
                if layer_name == "CAPE":
                    if result.values[0] > 800:
                        print("   ⚠️  High instability detected (CAPE > 800 J/kg)")
                    elif result.values[0] > 500:
                        print("   ⚡ Moderate instability detected (CAPE > 500 J/kg)")
                    else:
                        print("   ✅ Low instability (CAPE ≤ 500 J/kg)")
                        
                elif layer_name == "CIN":
                    if result.values[0] < -50:
                        print("   ⚡ Low inhibition (CIN < -50 J/kg)")
                    else:
                        print("   ✅ Significant inhibition (CIN ≥ -50 J/kg)")
                        
                elif layer_name == "LI":
                    if result.values[0] < -4:
                        print("   ⚠️  High severe weather potential (LI < -4°C)")
                    elif result.values[0] < -2:
                        print("   ⚡ Moderate instability (LI < -2°C)")
                    else:
                        print("   ✅ Stable conditions (LI ≥ -2°C)")
            
            print()
            
        except Exception as e:
            print(f"❌ Error fetching {layer_name}: {str(e)}")
            print()
    
    print("🎯 Demo completed!")


if __name__ == "__main__":
    demo_instability_layers() 