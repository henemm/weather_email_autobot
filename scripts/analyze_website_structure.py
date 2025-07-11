#!/usr/bin/env python3
"""
Analyze Website Structure for Zone Data

This script analyzes the fire risk website to understand its structure
and find where zone data is stored.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path

def analyze_website():
    """Analyze the website structure to find zone data."""
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    print(f"Analyzing website: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all script tags
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags")
        
        # Look for specific patterns
        zone_patterns = [
            r'"(\d+)":\s*"([^"]+)"',  # "201": "BALAGNE"
            r'zone_(\d+):\s*"([^"]+)"',  # zone_201: "BALAGNE"
            r'id:\s*(\d+).*?name:\s*"([^"]+)"',  # id: 201, name: "BALAGNE"
            r'numero_zon["\']?\s*:\s*["\']?(\d+)["\']?',  # numero_zon: "201"
            r'Zonage_Feu["\']?\s*:\s*["\']?([^"\']+)["\']?',  # Zonage_Feu: "BALAGNE"
        ]
        
        gr20_zone_names = [
            "BALAGNE", "MONTI", "MONTAGNE", "COTE DES NACRES", 
            "MOYENNE MONTAGNE SUD", "REGION DE CONCA"
        ]
        
        found_data = []
        
        for i, script in enumerate(scripts):
            if script.string:
                content = script.string
                print(f"\nScript {i+1} (length: {len(content)} chars)")
                
                # Look for zone-related content
                if any(zone_name.lower() in content.lower() for zone_name in gr20_zone_names):
                    print(f"  Contains GR20 zone names!")
                    
                    # Try to find zone data
                    for pattern in zone_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            print(f"  Pattern '{pattern}' found {len(matches)} matches:")
                            for match in matches[:5]:  # Show first 5 matches
                                print(f"    {match}")
                            found_data.extend(matches)
                
                # Look for JSON-like structures
                if '{"' in content or '{"' in content:
                    print(f"  Contains JSON-like data")
                    
                    # Try to extract JSON objects
                    json_patterns = [
                        r'\{[^{}]*"numero_zon"[^{}]*\}',
                        r'\{[^{}]*"Zonage_Feu"[^{}]*\}',
                    ]
                    
                    for pattern in json_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            print(f"  JSON pattern found {len(matches)} matches:")
                            for match in matches[:3]:  # Show first 3 matches
                                print(f"    {match}")
        
        # Also check for external data sources
        print("\nLooking for external data sources...")
        
        # Check for API endpoints
        api_patterns = [
            r'https?://[^"\']*\.json',
            r'https?://[^"\']*api[^"\']*',
            r'https?://[^"\']*data[^"\']*',
        ]
        
        for script in scripts:
            if script.string:
                content = script.string
                for pattern in api_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f"  Found API/data URLs: {matches}")
        
        # Check if there's a specific API endpoint for zones
        zone_api_url = "https://www.risque-prevention-incendie.fr/static/20/data/zm.json"
        print(f"\nTrying zone API: {zone_api_url}")
        
        try:
            zone_response = requests.get(zone_api_url, timeout=10)
            if zone_response.status_code == 200:
                zone_data = zone_response.json()
                print(f"  Zone API returned data with {len(zone_data)} keys")
                print(f"  Keys: {list(zone_data.keys())}")
                
                if 'zm' in zone_data:
                    print(f"  'zm' contains {len(zone_data['zm'])} entries")
                    print(f"  Sample entries: {list(zone_data['zm'].items())[:5]}")
            else:
                print(f"  Zone API returned status {zone_response.status_code}")
        except Exception as e:
            print(f"  Zone API error: {e}")
        
        return found_data
        
    except Exception as e:
        print(f"Error analyzing website: {e}")
        return []

if __name__ == "__main__":
    found_data = analyze_website()
    
    if found_data:
        print(f"\nFound {len(found_data)} potential zone data entries")
        print("Sample data:")
        for item in found_data[:10]:
            print(f"  {item}")
    else:
        print("\nNo zone data found in scripts") 