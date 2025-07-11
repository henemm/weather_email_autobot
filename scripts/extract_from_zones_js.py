#!/usr/bin/env python3
"""
Extract Zone Data from zones.js

This script extracts zone data from the zones.js file that contains
the actual zone definitions.
"""

import requests
import re
import json

def extract_zones_from_js():
    """Extract zone data from the zones.js file."""
    url = "https://www.risque-prevention-incendie.fr/static/20/js/zones.js"
    
    print(f"Extracting zone data from: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content = response.text
        print(f"Content length: {len(content)} chars")
        
        # Look for the zones array
        zones_match = re.search(r'zones\s*=\s*\[(.*?)\];', content, re.DOTALL)
        
        if not zones_match:
            print("Zones array not found!")
            return []
        
        zones_text = zones_match.group(1)
        print(f"Found zones array with {len(zones_text)} chars")
        
        # Extract individual zone objects
        zone_objects = []
        
        # Look for individual zone objects
        zone_pattern = r'\{[^{}]*"type":\s*"Feature"[^{}]*"properties":\s*\{[^{}]*"numero_zon":\s*"(\d+)"[^{}]*"Zonage_Feu":\s*"([^"]+)"[^{}]*\}'
        
        matches = re.findall(zone_pattern, zones_text, re.DOTALL)
        
        if matches:
            print(f"Found {len(matches)} zone objects")
            
            for zone_id, zone_name in matches:
                zone_objects.append({
                    'zone_id': zone_id,
                    'zone_name': zone_name
                })
                print(f"  {zone_id} → {zone_name}")
        
        # If the above pattern didn't work, try a different approach
        if not zone_objects:
            print("Trying alternative extraction method...")
            
            # Look for any object with numero_zon and Zonage_Feu
            alt_pattern = r'"numero_zon":\s*"(\d+)"[^{}]*"Zonage_Feu":\s*"([^"]+)"'
            matches = re.findall(alt_pattern, zones_text)
            
            if matches:
                print(f"Found {len(matches)} zone mappings (alternative method)")
                
                for zone_id, zone_name in matches:
                    zone_objects.append({
                        'zone_id': zone_id,
                        'zone_name': zone_name
                    })
                    print(f"  {zone_id} → {zone_name}")
        
        return zone_objects
        
    except Exception as e:
        print(f"Error extracting zones: {e}")
        return []

def extract_full_zone_data():
    """Extract the complete zone data structure."""
    url = "https://www.risque-prevention-incendie.fr/static/20/js/zones.js"
    
    print(f"\nExtracting full zone data structure from: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content = response.text
        
        # Try to extract the complete zones array as JSON
        zones_match = re.search(r'zones\s*=\s*(\[.*?\]);', content, re.DOTALL)
        
        if zones_match:
            zones_json_text = zones_match.group(1)
            print(f"Found zones JSON with {len(zones_json_text)} chars")
            
            # Try to parse as JSON
            try:
                zones_data = json.loads(zones_json_text)
                print(f"Successfully parsed JSON with {len(zones_data)} zones")
                
                zone_objects = []
                for zone in zones_data:
                    if isinstance(zone, dict) and 'properties' in zone:
                        props = zone['properties']
                        if 'numero_zon' in props and 'Zonage_Feu' in props:
                            zone_objects.append({
                                'zone_id': props['numero_zon'],
                                'zone_name': props['Zonage_Feu'],
                                'level': props.get('level', 'unknown')
                            })
                            print(f"  {props['numero_zon']} → {props['Zonage_Feu']} (level: {props.get('level', 'unknown')})")
                
                return zone_objects
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
                print("JSON text preview:")
                print(zones_json_text[:500] + "...")
        
        return []
        
    except Exception as e:
        print(f"Error extracting full zone data: {e}")
        return []

def main():
    """Main function."""
    print("EXTRACTING ZONE DATA FROM ZONES.JS")
    print("="*60)
    
    # Extract zones using regex
    zones = extract_zones_from_js()
    
    # Extract full zone data structure
    full_zones = extract_full_zone_data()
    
    # Combine results
    all_zones = zones + full_zones
    
    # Remove duplicates
    unique_zones = []
    seen_ids = set()
    for zone in all_zones:
        if zone['zone_id'] not in seen_ids:
            unique_zones.append(zone)
            seen_ids.add(zone['zone_id'])
    
    print("\n" + "="*60)
    print("ZONE EXTRACTION SUMMARY")
    print("="*60)
    
    if unique_zones:
        print(f"Found {len(unique_zones)} unique zones:")
        for zone in unique_zones:
            level_info = f" (level: {zone.get('level', 'unknown')})" if 'level' in zone else ""
            print(f"  {zone['zone_id']} → {zone['zone_name']}{level_info}")
        
        # Filter for GR20 zones
        gr20_zone_names = ["BALAGNE", "MONTI", "MONTAGNE", "COTE DES NACRES", 
                          "MOYENNE MONTAGNE SUD", "REGION DE CONCA"]
        
        gr20_zones = []
        for zone in unique_zones:
            zone_name_upper = zone['zone_name'].upper()
            for gr20_name in gr20_zone_names:
                if gr20_name in zone_name_upper or zone_name_upper in gr20_name:
                    gr20_zones.append(zone)
                    break
        
        print(f"\nGR20-relevant zones: {len(gr20_zones)}")
        for zone in gr20_zones:
            level_info = f" (level: {zone.get('level', 'unknown')})" if 'level' in zone else ""
            print(f"  {zone['zone_id']} → {zone['zone_name']}{level_info}")
        
        # Save to file
        with open('data/extracted_zones.json', 'w', encoding='utf-8') as f:
            json.dump(unique_zones, f, indent=2, ensure_ascii=False)
        print(f"\nZone data saved to data/extracted_zones.json")
        
    else:
        print("No zones found in zones.js")

if __name__ == "__main__":
    main() 