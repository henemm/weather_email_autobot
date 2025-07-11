#!/usr/bin/env python3
"""
Identify GR20 Zones

This script identifies which zones contain GR20 coordinates by checking
each GR20 coordinate against the zone polygons from zones.js.
"""

import requests
import re
import json
from shapely.geometry import Point, Polygon
import sys
import os

def extract_zone_polygons():
    """Extract zone polygons from zones.js."""
    url = "https://www.risque-prevention-incendie.fr/static/20/js/zones.js"
    
    print(f"Extracting zone polygons from: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content = response.text
        
        # Extract the zones array
        zones_match = re.search(r'zones\s*=\s*(\[.*?\]);', content, re.DOTALL)
        
        if not zones_match:
            print("Zones array not found!")
            return []
        
        zones_text = zones_match.group(1)
        
        # Fix the JSON format by adding quotes to property names
        fixed_json = re.sub(r'(\w+):', r'"\1":', zones_text)
        
        # Parse the fixed JSON
        zones_data = json.loads(fixed_json)
        print(f"Successfully parsed {len(zones_data)} zones")
        
        zone_polygons = []
        
        for zone in zones_data:
            if isinstance(zone, dict) and 'properties' in zone and 'geometry' in zone:
                props = zone['properties']
                geom = zone['geometry']
                
                if 'numero_zon' in props and 'Zonage_Feu' in props and geom['type'] == 'Polygon':
                    zone_id = props['numero_zon']
                    zone_name = props['Zonage_Feu']
                    coordinates = geom['coordinates'][0]  # First ring of polygon
                    
                    # Create Shapely polygon
                    polygon = Polygon(coordinates)
                    
                    zone_polygons.append({
                        'zone_id': zone_id,
                        'zone_name': zone_name,
                        'polygon': polygon
                    })
                    
                    print(f"  Zone {zone_id}: {zone_name} (polygon with {len(coordinates)} points)")
        
        return zone_polygons
        
    except Exception as e:
        print(f"Error extracting zone polygons: {e}")
        return []

def load_gr20_coordinates():
    """Load GR20 coordinates from etappen.json."""
    etappen_path = "etappen.json"
    
    print(f"\nLoading GR20 coordinates from: {etappen_path}")
    print("="*60)
    
    try:
        with open(etappen_path, 'r', encoding='utf-8') as f:
            etappen = json.load(f)
        
        all_coordinates = []
        
        for stage in etappen:
            stage_name = stage.get('name', 'Unknown')
            points = stage.get('punkte', [])
            
            print(f"Stage {stage_name}: {len(points)} points")
            
            for point in points:
                lat = float(point['lat'])
                lon = float(point['lon'])
                all_coordinates.append({
                    'lat': lat,
                    'lon': lon,
                    'stage': stage_name
                })
        
        print(f"Total GR20 coordinates: {len(all_coordinates)}")
        return all_coordinates
        
    except Exception as e:
        print(f"Error loading GR20 coordinates: {e}")
        return []

def identify_gr20_zones(zone_polygons, gr20_coordinates):
    """Identify which zones contain GR20 coordinates."""
    print(f"\nIdentifying GR20 zones...")
    print("="*60)
    
    gr20_zones = {}
    
    for coord in gr20_coordinates:
        point = Point(coord['lon'], coord['lat'])  # Note: Shapely uses (lon, lat)
        
        for zone in zone_polygons:
            if zone['polygon'].contains(point):
                zone_id = zone['zone_id']
                zone_name = zone['zone_name']
                
                if zone_id not in gr20_zones:
                    gr20_zones[zone_id] = {
                        'zone_name': zone_name,
                        'coordinates': []
                    }
                
                gr20_zones[zone_id]['coordinates'].append({
                    'lat': coord['lat'],
                    'lon': coord['lon'],
                    'stage': coord['stage']
                })
                
                print(f"  Coordinate ({coord['lat']:.4f}, {coord['lon']:.4f}) from stage '{coord['stage']}' is in zone {zone_id}: {zone_name}")
                break
        else:
            print(f"  Coordinate ({coord['lat']:.4f}, {coord['lon']:.4f}) from stage '{coord['stage']}' is not in any zone")
    
    return gr20_zones

def main():
    """Main function."""
    print("IDENTIFYING GR20 ZONES")
    print("="*60)
    
    # Extract zone polygons
    zone_polygons = extract_zone_polygons()
    
    if not zone_polygons:
        print("No zone polygons found!")
        return
    
    # Load GR20 coordinates
    gr20_coordinates = load_gr20_coordinates()
    
    if not gr20_coordinates:
        print("No GR20 coordinates found!")
        return
    
    # Identify GR20 zones
    gr20_zones = identify_gr20_zones(zone_polygons, gr20_coordinates)
    
    print("\n" + "="*60)
    print("GR20 ZONES SUMMARY")
    print("="*60)
    
    if gr20_zones:
        print(f"Found {len(gr20_zones)} zones that contain GR20 coordinates:")
        
        for zone_id, zone_info in gr20_zones.items():
            zone_name = zone_info['zone_name']
            coord_count = len(zone_info['coordinates'])
            stages = set(coord['stage'] for coord in zone_info['coordinates'])
            
            print(f"\nZone {zone_id}: {zone_name}")
            print(f"  Contains {coord_count} GR20 coordinates")
            print(f"  Stages: {', '.join(sorted(stages))}")
            
            # Show sample coordinates
            sample_coords = zone_info['coordinates'][:3]
            for coord in sample_coords:
                print(f"    ({coord['lat']:.4f}, {coord['lon']:.4f}) - {coord['stage']}")
            if len(zone_info['coordinates']) > 3:
                print(f"    ... and {len(zone_info['coordinates']) - 3} more")
        
        # Create final output
        zone_ids = list(gr20_zones.keys())
        zone_ids_str = ', '.join(zone_ids)
        
        print(f"\n" + "="*60)
        print("FINAL RESULT")
        print("="*60)
        print(f"GR20 Zone IDs: {zone_ids_str}")
        
        # Save detailed results
        with open('data/gr20_zone_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(gr20_zones, f, indent=2, ensure_ascii=False)
        print(f"Detailed analysis saved to data/gr20_zone_analysis.json")
        
    else:
        print("No zones found that contain GR20 coordinates.")
        print("This could mean:")
        print("1. The zone polygons don't cover the GR20 route")
        print("2. There's an issue with the coordinate system")
        print("3. The GR20 coordinates are outside the zone boundaries")

if __name__ == "__main__":
    main() 