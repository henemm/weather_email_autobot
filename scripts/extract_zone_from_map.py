#!/usr/bin/env python3
"""
Extract Zone Data from Interactive Map

This script analyzes the JavaScript code that loads the interactive map
to find zone ID to name mappings.
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def analyze_map_javascript():
    """Analyze the JavaScript that loads the map data."""
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    print(f"Analyzing map JavaScript: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all script tags
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags")
        
        # Look for Leaflet map initialization
        map_data = []
        
        for i, script in enumerate(scripts):
            if script.string:
                content = script.string
                
                # Look for Leaflet map initialization
                if 'leaflet' in content.lower() or 'map' in content.lower():
                    print(f"\nScript {i+1} contains map-related code (length: {len(content)} chars)")
                    
                    # Look for zone data patterns in the map code
                    zone_patterns = [
                        # GeoJSON patterns
                        (r'"type":\s*"Feature".*?"properties":\s*\{[^}]*"numero_zon":\s*"(\d+)"[^}]*"Zonage_Feu":\s*"([^"]+)"[^}]*\}', "GeoJSON Feature"),
                        (r'"properties":\s*\{[^}]*"numero_zon":\s*"(\d+)"[^}]*"nom":\s*"([^"]+)"[^}]*\}', "GeoJSON Properties"),
                        
                        # Array patterns
                        (r'\{[^{}]*"numero_zon":\s*"(\d+)"[^{}]*"Zonage_Feu":\s*"([^"]+)"[^{}]*\}', "Zone Object"),
                        (r'\{[^{}]*"id":\s*(\d+)[^{}]*"name":\s*"([^"]+)"[^{}]*\}', "Zone Object (id/name)"),
                        
                        # Variable assignments
                        (r'zones\s*=\s*\[(.*?)\]', "Zones Array"),
                        (r'regions\s*=\s*\[(.*?)\]', "Regions Array"),
                        
                        # Function calls with zone data
                        (r'addZone\s*\(\s*(\d+)\s*,\s*"([^"]+)"', "Add Zone Function"),
                        (r'setZone\s*\(\s*(\d+)\s*,\s*"([^"]+)"', "Set Zone Function"),
                    ]
                    
                    for pattern, description in zone_patterns:
                        matches = re.findall(pattern, content, re.DOTALL)
                        if matches:
                            print(f"  {description}: {len(matches)} matches")
                            for match in matches[:5]:  # Show first 5
                                if isinstance(match, tuple):
                                    zone_id, zone_name = match
                                    map_data.append({
                                        'zone_id': zone_id,
                                        'zone_name': zone_name,
                                        'source': f"Script {i+1} - {description}"
                                    })
                                    print(f"    {zone_id} → {zone_name}")
                                else:
                                    print(f"    {match}")
        
        return map_data
        
    except Exception as e:
        print(f"Error analyzing map JavaScript: {e}")
        return []

def try_map_data_endpoints():
    """Try to find map data endpoints."""
    print("\n" + "="*60)
    print("TRYING MAP DATA ENDPOINTS")
    print("="*60)
    
    # Common patterns for map data endpoints
    endpoints = [
        "https://www.risque-prevention-incendie.fr/static/20/data/zones.geojson",
        "https://www.risque-prevention-incendie.fr/static/20/data/regions.geojson",
        "https://www.risque-prevention-incendie.fr/static/20/data/corse.geojson",
        "https://www.risque-prevention-incendie.fr/static/20/data/map.geojson",
        "https://www.risque-prevention-incendie.fr/static/20/data/feu.geojson",
        "https://www.risque-prevention-incendie.fr/static/20/data/incendie.geojson",
        "https://www.risque-prevention-incendie.fr/static/20/data/risk.geojson",
        "https://www.risque-prevention-incendie.fr/static/20/data/prev.geojson",
    ]
    
    found_data = []
    
    for endpoint in endpoints:
        print(f"\nTrying: {endpoint}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, application/geo+json, */*',
            }
            
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  Success! Content length: {len(response.content)}")
                
                try:
                    data = response.json()
                    print(f"  JSON data type: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                        
                        # Look for features array
                        if 'features' in data:
                            features = data['features']
                            print(f"  Found {len(features)} features")
                            
                            for feature in features[:3]:  # Show first 3
                                if 'properties' in feature:
                                    props = feature['properties']
                                    print(f"    Properties: {props}")
                                    
                                    # Look for zone data in properties
                                    if 'numero_zon' in props and 'Zonage_Feu' in props:
                                        zone_id = props['numero_zon']
                                        zone_name = props['Zonage_Feu']
                                        found_data.append({
                                            'zone_id': zone_id,
                                            'zone_name': zone_name,
                                            'source': endpoint
                                        })
                                        print(f"    Found zone: {zone_id} → {zone_name}")
                    
                    elif isinstance(data, list):
                        print(f"  Array with {len(data)} items")
                        for item in data[:3]:  # Show first 3
                            print(f"    Item: {item}")
                            
                except json.JSONDecodeError:
                    print(f"  Not JSON data")
                    
            else:
                print(f"  Failed")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    return found_data

def check_for_dynamic_loading():
    """Check for dynamic loading of map data."""
    print("\n" + "="*60)
    print("CHECKING FOR DYNAMIC LOADING")
    print("="*60)
    
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        scripts = soup.find_all('script')
        
        # Look for any AJAX or fetch calls that might load zone data
        loading_patterns = [
            r'fetch\s*\(\s*["\']([^"\']*zone[^"\']*)["\']',
            r'fetch\s*\(\s*["\']([^"\']*region[^"\']*)["\']',
            r'fetch\s*\(\s*["\']([^"\']*data[^"\']*)["\']',
            r'\.ajax\s*\(\s*\{[^}]*url:\s*["\']([^"\']*)["\']',
            r'XMLHttpRequest.*?open.*?["\']([^"\']*)["\']',
        ]
        
        for script in scripts:
            if script.string:
                content = script.string
                for pattern in loading_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        print(f"Found dynamic loading: {matches}")
        
        # Look for any configuration that might point to data sources
        config_patterns = [
            r'dataUrl\s*[:=]\s*["\']([^"\']*)["\']',
            r'zoneUrl\s*[:=]\s*["\']([^"\']*)["\']',
            r'regionUrl\s*[:=]\s*["\']([^"\']*)["\']',
        ]
        
        for script in scripts:
            if script.string:
                content = script.string
                for pattern in config_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f"Found config URL: {matches}")
        
    except Exception as e:
        print(f"Error checking dynamic loading: {e}")

def main():
    """Main function."""
    print("EXTRACTING ZONE DATA FROM MAP")
    print("="*60)
    
    # Analyze map JavaScript
    map_data = analyze_map_javascript()
    
    # Try map data endpoints
    endpoint_data = try_map_data_endpoints()
    
    # Check for dynamic loading
    check_for_dynamic_loading()
    
    # Combine all found data
    all_data = map_data + endpoint_data
    
    print("\n" + "="*60)
    print("ZONE DATA EXTRACTION SUMMARY")
    print("="*60)
    
    if all_data:
        print(f"Found {len(all_data)} zone mappings:")
        for data in all_data:
            print(f"  {data['zone_id']} → {data['zone_name']} (Source: {data['source']})")
        
        # Filter for GR20 zones
        gr20_zone_names = ["BALAGNE", "MONTI", "MONTAGNE", "COTE DES NACRES", 
                          "MOYENNE MONTAGNE SUD", "REGION DE CONCA"]
        
        gr20_zones = []
        for data in all_data:
            zone_name_upper = data['zone_name'].upper()
            for gr20_name in gr20_zone_names:
                if gr20_name in zone_name_upper or zone_name_upper in gr20_name:
                    gr20_zones.append(data)
                    break
        
        print(f"\nGR20-relevant zones: {len(gr20_zones)}")
        for zone in gr20_zones:
            print(f"  {zone['zone_id']} → {zone['zone_name']}")
    
    else:
        print("No zone data found.")
        print("\nThis means:")
        print("1. Zone data is loaded dynamically via JavaScript")
        print("2. Zone data requires authentication")
        print("3. Zone data is in a different format")
        print("4. Zone data is embedded in the map tiles themselves")

if __name__ == "__main__":
    main() 