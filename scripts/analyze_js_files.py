#!/usr/bin/env python3
"""
Analyze JavaScript Files for Zone Data

This script analyzes the JavaScript files loaded by the website
to find zone data that might be embedded in the JS code.
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def get_js_files():
    """Get all JavaScript files loaded by the website."""
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    print(f"Getting JavaScript files from: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all script tags with src attributes
        script_tags = soup.find_all('script', src=True)
        print(f"Found {len(script_tags)} external script files")
        
        js_files = []
        
        for script in script_tags:
            src = script.get('src')
            if src:
                # Make absolute URL if relative
                if src.startswith('/'):
                    js_url = f"https://www.risque-prevention-incendie.fr{src}"
                elif src.startswith('http'):
                    js_url = src
                else:
                    js_url = f"https://www.risque-prevention-incendie.fr/{src}"
                
                js_files.append(js_url)
                print(f"  {js_url}")
        
        return js_files
        
    except Exception as e:
        print(f"Error getting JS files: {e}")
        return []

def analyze_js_file(url):
    """Analyze a single JavaScript file for zone data."""
    print(f"\nAnalyzing: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"  Failed with status: {response.status_code}")
            return []
        
        content = response.text
        print(f"  Content length: {len(content)} chars")
        
        zone_data = []
        
        # Look for zone data patterns
        zone_patterns = [
            # Array of zone objects
            (r'zones\s*=\s*\[(.*?)\]', "Zones Array"),
            (r'regions\s*=\s*\[(.*?)\]', "Regions Array"),
            (r'zoneData\s*=\s*\[(.*?)\]', "Zone Data Array"),
            
            # Object with zone mappings
            (r'zoneMap\s*=\s*\{([^}]+)\}', "Zone Map Object"),
            (r'regionMap\s*=\s*\{([^}]+)\}', "Region Map Object"),
            
            # GeoJSON features
            (r'"features":\s*\[(.*?)\]', "GeoJSON Features"),
            
            # Zone definitions
            (r'addZone\s*\(\s*(\d+)\s*,\s*"([^"]+)"', "Add Zone Function"),
            (r'createZone\s*\(\s*(\d+)\s*,\s*"([^"]+)"', "Create Zone Function"),
        ]
        
        for pattern, description in zone_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                print(f"  {description}: {len(matches)} matches")
                
                for match in matches[:3]:  # Show first 3
                    if isinstance(match, tuple):
                        zone_id, zone_name = match
                        zone_data.append({
                            'zone_id': zone_id,
                            'zone_name': zone_name,
                            'source': f"{url} - {description}"
                        })
                        print(f"    {zone_id} → {zone_name}")
                    else:
                        print(f"    {match[:100]}...")
        
        # Look for any text that mentions GR20 zones
        gr20_zone_names = ["BALAGNE", "MONTI", "MONTAGNE", "COTE DES NACRES", 
                          "MOYENNE MONTAGNE SUD", "REGION DE CONCA"]
        
        for zone_name in gr20_zone_names:
            if zone_name.lower() in content.lower():
                # Find context around the zone name
                matches = re.finditer(rf'.{{0,100}}{zone_name}.{{0,100}}', content, re.IGNORECASE)
                print(f"\n  Found '{zone_name}' in context:")
                for match in matches[:2]:  # Show first 2 matches
                    print(f"    ...{match.group()}...")
        
        return zone_data
        
    except Exception as e:
        print(f"  Error analyzing file: {e}")
        return []

def try_specific_js_files():
    """Try to analyze specific JavaScript files that might contain zone data."""
    print("\n" + "="*60)
    print("ANALYZING SPECIFIC JS FILES")
    print("="*60)
    
    # Common JS files that might contain zone data
    specific_files = [
        "https://www.risque-prevention-incendie.fr/static/js/main_prev.js",
        "https://www.risque-prevention-incendie.fr/static/20/js/prev.js",
        "https://www.risque-prevention-incendie.fr/static/js/map.js",
        "https://www.risque-prevention-incendie.fr/static/20/js/map.js",
        "https://www.risque-prevention-incendie.fr/static/js/zones.js",
        "https://www.risque-prevention-incendie.fr/static/20/js/zones.js",
        "https://www.risque-prevention-incendie.fr/static/js/data.js",
        "https://www.risque-prevention-incendie.fr/static/20/js/data.js",
    ]
    
    all_zone_data = []
    
    for js_file in specific_files:
        zone_data = analyze_js_file(js_file)
        all_zone_data.extend(zone_data)
    
    return all_zone_data

def main():
    """Main function."""
    print("ANALYZING JAVASCRIPT FILES FOR ZONE DATA")
    print("="*60)
    
    # Get JS files from the main page
    js_files = get_js_files()
    
    # Analyze each JS file
    all_zone_data = []
    
    for js_file in js_files:
        zone_data = analyze_js_file(js_file)
        all_zone_data.extend(zone_data)
    
    # Try specific JS files
    specific_zone_data = try_specific_js_files()
    all_zone_data.extend(specific_zone_data)
    
    print("\n" + "="*60)
    print("JAVASCRIPT ANALYSIS SUMMARY")
    print("="*60)
    
    if all_zone_data:
        print(f"Found {len(all_zone_data)} zone mappings in JavaScript files:")
        for data in all_zone_data:
            print(f"  {data['zone_id']} → {data['zone_name']} (Source: {data['source']})")
        
        # Filter for GR20 zones
        gr20_zone_names = ["BALAGNE", "MONTI", "MONTAGNE", "COTE DES NACRES", 
                          "MOYENNE MONTAGNE SUD", "REGION DE CONCA"]
        
        gr20_zones = []
        for data in all_zone_data:
            zone_name_upper = data['zone_name'].upper()
            for gr20_name in gr20_zone_names:
                if gr20_name in zone_name_upper or zone_name_upper in gr20_name:
                    gr20_zones.append(data)
                    break
        
        print(f"\nGR20-relevant zones: {len(gr20_zones)}")
        for zone in gr20_zones:
            print(f"  {zone['zone_id']} → {zone['zone_name']}")
    
    else:
        print("No zone data found in JavaScript files.")
        print("\nThis suggests:")
        print("1. Zone data is loaded via AJAX after page load")
        print("2. Zone data is embedded in map tiles")
        print("3. Zone data requires authentication")
        print("4. Zone data is in a different format")

if __name__ == "__main__":
    main() 