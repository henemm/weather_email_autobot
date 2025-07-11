#!/usr/bin/env python3
"""
Fix and Extract Zone Data from zones.js

This script fixes the non-standard JSON format in zones.js and extracts
the zone data properly.
"""

import requests
import re
import json

def extract_and_fix_zones():
    """Extract zone data from zones.js and fix the JSON format."""
    url = "https://www.risque-prevention-incendie.fr/static/20/js/zones.js"
    
    print(f"Extracting and fixing zone data from: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content = response.text
        print(f"Content length: {len(content)} chars")
        
        # Extract the zones array
        zones_match = re.search(r'zones\s*=\s*(\[.*?\]);', content, re.DOTALL)
        
        if not zones_match:
            print("Zones array not found!")
            return []
        
        zones_text = zones_match.group(1)
        print(f"Found zones array with {len(zones_text)} chars")
        
        # Fix the JSON format by adding quotes to property names
        fixed_json = re.sub(r'(\w+):', r'"\1":', zones_text)
        
        print("Fixed JSON format")
        
        # Try to parse the fixed JSON
        try:
            zones_data = json.loads(fixed_json)
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
            print(f"Failed to parse fixed JSON: {e}")
            print("Fixed JSON preview:")
            print(fixed_json[:500] + "...")
            
            # Try manual extraction as fallback
            print("\nTrying manual extraction...")
            return manual_extract_zones(zones_text)
        
    except Exception as e:
        print(f"Error extracting zones: {e}")
        return []

def manual_extract_zones(zones_text):
    """Manually extract zone data using regex patterns."""
    print("Using manual extraction method...")
    
    zone_objects = []
    
    # Pattern to match zone objects
    zone_pattern = r'numero_zon:\s*"(\d+)"[^{}]*Zonage_Feu:\s*"([^"]+)"'
    
    matches = re.findall(zone_pattern, zones_text)
    
    if matches:
        print(f"Found {len(matches)} zones using manual extraction")
        
        for zone_id, zone_name in matches:
            zone_objects.append({
                'zone_id': zone_id,
                'zone_name': zone_name,
                'level': 'unknown'
            })
            print(f"  {zone_id} → {zone_name}")
    
    return zone_objects

def filter_gr20_zones(zones):
    """Filter zones to only include GR20-relevant ones."""
    gr20_zone_names = ["BALAGNE", "MONTI", "MONTAGNE", "COTE DES NACRES", 
                      "MOYENNE MONTAGNE SUD", "REGION DE CONCA"]
    
    gr20_zones = []
    
    for zone in zones:
        zone_name_upper = zone['zone_name'].upper()
        
        # Check for exact matches or partial matches
        for gr20_name in gr20_zone_names:
            if gr20_name in zone_name_upper or zone_name_upper in gr20_name:
                gr20_zones.append(zone)
                break
        
        # Also check for common variations
        if any(keyword in zone_name_upper for keyword in ['BALAGNE', 'CONCA', 'CALVI']):
            if zone not in gr20_zones:
                gr20_zones.append(zone)
    
    return gr20_zones

def main():
    """Main function."""
    print("FIXING AND EXTRACTING ZONE DATA")
    print("="*60)
    
    # Extract and fix zones
    zones = extract_and_fix_zones()
    
    print("\n" + "="*60)
    print("ZONE EXTRACTION SUMMARY")
    print("="*60)
    
    if zones:
        print(f"Found {len(zones)} total zones:")
        for zone in zones:
            level_info = f" (level: {zone.get('level', 'unknown')})" if 'level' in zone else ""
            print(f"  {zone['zone_id']} → {zone['zone_name']}{level_info}")
        
        # Filter for GR20 zones
        gr20_zones = filter_gr20_zones(zones)
        
        print(f"\nGR20-relevant zones: {len(gr20_zones)}")
        for zone in gr20_zones:
            level_info = f" (level: {zone.get('level', 'unknown')})" if 'level' in zone else ""
            print(f"  {zone['zone_id']} → {zone['zone_name']}{level_info}")
        
        # Save all zones to file
        with open('data/all_zones.json', 'w', encoding='utf-8') as f:
            json.dump(zones, f, indent=2, ensure_ascii=False)
        print(f"\nAll zone data saved to data/all_zones.json")
        
        # Save GR20 zones to file
        with open('data/gr20_zones.json', 'w', encoding='utf-8') as f:
            json.dump(gr20_zones, f, indent=2, ensure_ascii=False)
        print(f"GR20 zone data saved to data/gr20_zones.json")
        
        # Create the final output format
        gr20_zone_ids = [zone['zone_id'] for zone in gr20_zones]
        gr20_zone_ids_str = ', '.join(gr20_zone_ids) if gr20_zone_ids else ''
        
        print(f"\nFinal GR20 Zone IDs: {gr20_zone_ids_str}")
        
    else:
        print("No zones found in zones.js")

if __name__ == "__main__":
    main() 