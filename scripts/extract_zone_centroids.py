#!/usr/bin/env python3
"""
Extract Zone Centroids

This script extracts the centroids of all zone polygons from zones.js
for visual comparison with the map.
"""

import requests
import re
import json
from shapely.geometry import Polygon

def extract_zone_centroids():
    url = "https://www.risque-prevention-incendie.fr/static/20/js/zones.js"
    print(f"Extracting centroids from: {url}")
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
        centroids = []
        for zone in zones_data:
            if isinstance(zone, dict) and 'properties' in zone and 'geometry' in zone:
                props = zone['properties']
                geom = zone['geometry']
                if 'numero_zon' in props and 'Zonage_Feu' in props and geom['type'] == 'Polygon':
                    zone_id = props['numero_zon']
                    zone_name = props['Zonage_Feu']
                    coordinates = geom['coordinates'][0]  # First ring of polygon
                    polygon = Polygon(coordinates)
                    centroid = polygon.centroid
                    centroids.append({
                        'zone_id': zone_id,
                        'zone_name': zone_name,
                        'centroid_lat': centroid.y,
                        'centroid_lon': centroid.x
                    })
        return centroids
    except Exception as e:
        print(f"Error extracting centroids: {e}")
        return []

def main():
    centroids = extract_zone_centroids()
    print("\nZone Centroids:")
    print("ID      | Latitude   | Longitude   | Name")
    print("-----------------------------------------------")
    for c in centroids:
        print(f"{c['zone_id']:>7} | {c['centroid_lat']:.5f} | {c['centroid_lon']:.5f} | {c['zone_name']}")
    # Save as CSV for further use
    with open('data/zone_centroids.csv', 'w', encoding='utf-8') as f:
        f.write("zone_id,centroid_lat,centroid_lon,zone_name\n")
        for c in centroids:
            f.write(f"{c['zone_id']},{c['centroid_lat']},{c['centroid_lon']},\"{c['zone_name']}\"\n")
    print("\nCentroids saved to data/zone_centroids.csv")

if __name__ == "__main__":
    main() 