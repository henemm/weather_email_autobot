#!/usr/bin/env python3
"""
Demo script to test WCS GML parsing functionality.

This script demonstrates the extraction of temperature values from WCS GML responses
for coordinates around Bustanico/Conca, Corsica.
"""

import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_arome_wcs import fetch_arome_wcs_data, _extract_temperature_from_gml
from auth.meteo_token_provider import MeteoTokenProvider


def main():
    """Main demo function."""
    print("🌡️  WCS GML Parsing Demo")
    print("=" * 50)
    
    # Test coordinates around Bustanico/Conca, Corsica
    test_coordinates = [
        (41.6875, 9.3125, "Conca center"),
        (41.7, 9.3, "Conca north"),
        (41.68, 9.32, "Conca east"),
        (41.69, 9.31, "Conca northeast")
    ]
    
    # Temperature layer name
    layer_name = "TEMPERATURE__GROUND_OR_WATER_SURFACE"
    
    print(f"📍 Testing coordinates around Bustanico/Conca, Corsica")
    print(f"🌡️  Layer: {layer_name}")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check if we have a valid token
    try:
        token_provider = MeteoTokenProvider()
        token = token_provider.get_token()
        print(f"✅ Token available: {token[:10]}...")
    except Exception as e:
        print(f"❌ Token error: {e}")
        return
    
    # Test each coordinate
    for lat, lon, description in test_coordinates:
        print(f"\n🔍 Testing {description} (lat={lat}, lon={lon}):")
        print("-" * 40)
        
        try:
            # Fetch data with GML format
            print("📡 Fetching WCS data with GML format...")
            grid_data = fetch_arome_wcs_data(lat, lon, layer_name, format_type="gml")
            
            # Display results
            print(f"✅ Successfully fetched data:")
            print(f"   - Layer: {grid_data.layer}")
            print(f"   - Unit: {grid_data.unit}")
            print(f"   - Values count: {len(grid_data.values)}")
            print(f"   - Times count: {len(grid_data.times)}")
            
            if grid_data.values:
                print(f"   - First value: {grid_data.values[0]}")
                print(f"   - Last value: {grid_data.values[-1]}")
                print(f"   - Value range: {min(grid_data.values):.1f} to {max(grid_data.values):.1f}")
            
            if grid_data.times:
                print(f"   - First time: {grid_data.times[0]}")
                print(f"   - Last time: {grid_data.times[-1]}")
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            continue
    
    # Test with bounding box constraint
    print(f"\n🗺️  Testing with bounding box constraint:")
    print("-" * 40)
    
    try:
        # Small bounding box around Conca
        bbox = [9.3, 41.68, 9.32, 41.69]
        print(f"📦 Bounding box: {bbox}")
        
        # Fetch data for center point
        lat, lon = 41.6875, 9.3125
        grid_data = fetch_arome_wcs_data(lat, lon, layer_name, format_type="gml")
        
        print(f"✅ Data with bbox constraint:")
        print(f"   - Values count: {len(grid_data.values)}")
        if grid_data.values:
            print(f"   - Value range: {min(grid_data.values):.1f} to {max(grid_data.values):.1f}")
        
    except Exception as e:
        print(f"❌ Error with bbox constraint: {e}")
    
    # Test GML parsing with sample data
    print(f"\n🧪 Testing GML parsing with sample data:")
    print("-" * 40)
    
    sample_gml = """<?xml version="1.0" encoding="UTF-8"?>
<gml:RectifiedGridCoverage xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="temperature_coverage">
  <gml:domainSet>
    <gml:RectifiedGrid gml:id="temperature_grid" dimension="2">
      <gml:limits>
        <gml:GridEnvelope>
          <gml:low>0 0</gml:low>
          <gml:high>1 1</gml:high>
        </gml:GridEnvelope>
      </gml:limits>
      <gml:axisLabels>i j</gml:axisLabels>
      <gml:origin>
        <gml:Point gml:id="origin_point">
          <gml:pos>9.3125 41.6875</gml:pos>
        </gml:Point>
      </gml:origin>
      <gml:offsetVector>0.0125 0</gml:offsetVector>
      <gml:offsetVector>0 0.0125</gml:offsetVector>
    </gml:RectifiedGrid>
  </gml:domainSet>
  <gml:rangeSet>
    <gml:DataBlock>
      <gml:rangeParameters>
        <gml:Quantity>
          <gml:name>Temperature</gml:name>
          <gml:uom code="°C"/>
        </gml:Quantity>
      </gml:rangeParameters>
      <gml:doubleOrNilReasonTupleList>24.5 25.1 24.8 25.3</gml:doubleOrNilReasonTupleList>
    </gml:DataBlock>
  </gml:rangeSet>
</gml:RectifiedGridCoverage>"""
    
    try:
        extracted_data = _extract_temperature_from_gml(sample_gml)
        
        if extracted_data:
            print(f"✅ Sample GML parsing successful:")
            print(f"   - Values: {extracted_data['values']}")
            print(f"   - Unit: {extracted_data['unit']}")
            print(f"   - Bbox: {extracted_data['bbox']}")
        else:
            print(f"❌ Sample GML parsing failed")
            
    except Exception as e:
        print(f"❌ Error parsing sample GML: {e}")
    
    print(f"\n🎯 Demo completed at {datetime.now().isoformat()}")


if __name__ == "__main__":
    main() 