#!/usr/bin/env python3
"""
Analyze Zone Data from Fire Risk Website

This script analyzes the fire risk website to extract only provable
zone ID to name mappings from the DOM/JavaScript.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path

def analyze_website_for_zone_data():
    """Analyze the website to find provable zone data."""
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    print(f"Analyzing website: {url}")
    print("="*60)
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all script tags
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags")
        
        # Look for zone data in various formats
        zone_data = []
        
        for i, script in enumerate(scripts):
            if script.string:
                content = script.string
                print(f"\nScript {i+1} (length: {len(content)} chars)")
                
                # Look for various zone data patterns
                patterns = [
                    # JSON-like patterns
                    (r'"(\d+)":\s*"([^"]+)"', "JSON key-value"),
                    (r"'(\d+)':\s*'([^']+)'", "JSON key-value (single quotes)"),
                    
                    # Object property patterns
                    (r'id:\s*(\d+).*?name:\s*"([^"]+)"', "Object property"),
                    (r'numero:\s*(\d+).*?nom:\s*"([^"]+)"', "Object property (French)"),
                    (r'zone_id:\s*(\d+).*?zone_name:\s*"([^"]+)"', "Zone object"),
                    
                    # Array patterns
                    (r'\{[^{}]*"id":\s*(\d+)[^{}]*"name":\s*"([^"]+)"[^{}]*\}', "Array object"),
                    (r'\{[^{}]*"numero":\s*(\d+)[^{}]*"nom":\s*"([^"]+)"[^{}]*\}', "Array object (French)"),
                    
                    # Variable assignments
                    (r'zone_(\d+)\s*=\s*"([^"]+)"', "Variable assignment"),
                    (r'var\s+zone_(\d+)\s*=\s*"([^"]+)"', "Variable declaration"),
                ]
                
                for pattern, description in patterns:
                    matches = re.findall(pattern, content, re.DOTALL)
                    if matches:
                        print(f"  {description}: {len(matches)} matches")
                        for zone_id, zone_name in matches[:5]:  # Show first 5
                            zone_data.append({
                                'zone_id': int(zone_id),
                                'zone_name': zone_name,
                                'source': f"Script {i+1} - {description}",
                                'pattern': pattern
                            })
                            print(f"    {zone_id} → {zone_name}")
        
        # Also check for external data sources
        print("\nLooking for external data sources...")
        
        # Check for API endpoints in scripts
        api_patterns = [
            r'https?://[^"\']*\.json',
            r'https?://[^"\']*api[^"\']*',
            r'https?://[^"\']*data[^"\']*',
        ]
        
        api_urls = []
        for script in scripts:
            if script.string:
                content = script.string
                for pattern in api_patterns:
                    matches = re.findall(pattern, content)
                    api_urls.extend(matches)
        
        if api_urls:
            print(f"Found {len(api_urls)} potential API/data URLs:")
            for url in api_urls:
                print(f"  {url}")
        
        # Try to fetch data from potential API endpoints
        potential_apis = [
            "https://www.risque-prevention-incendie.fr/static/20/data/zm.json",
            "https://www.risque-prevention-incendie.fr/api/zones",
            "https://www.risque-prevention-incendie.fr/data/zones.json",
        ]
        
        for api_url in potential_apis:
            print(f"\nTrying API: {api_url}")
            try:
                api_response = requests.get(api_url, timeout=10)
                if api_response.status_code == 200:
                    print(f"  Success! Status: {api_response.status_code}")
                    try:
                        api_data = api_response.json()
                        print(f"  JSON data with {len(api_data)} keys: {list(api_data.keys())}")
                        
                        # Look for zone data in API response
                        if isinstance(api_data, dict):
                            for key, value in api_data.items():
                                if isinstance(value, dict) and ('id' in value or 'numero' in value):
                                    print(f"    Potential zone object: {key} → {value}")
                                elif isinstance(value, str) and key.isdigit():
                                    print(f"    Potential zone mapping: {key} → {value}")
                    except json.JSONDecodeError:
                        print(f"  Not JSON data")
                else:
                    print(f"  Failed with status: {api_response.status_code}")
            except Exception as e:
                print(f"  Error: {e}")
        
        return zone_data
        
    except Exception as e:
        print(f"Error analyzing website: {e}")
        return []

def filter_gr20_zones(zone_data):
    """Filter zone data to only include GR20-relevant zones."""
    gr20_zone_names = [
        "BALAGNE", "MONTI", "MONTAGNE", "COTE DES NACRES", 
        "MOYENNE MONTAGNE SUD", "REGION DE CONCA"
    ]
    
    gr20_zones = []
    for zone in zone_data:
        zone_name_upper = zone['zone_name'].upper()
        for gr20_name in gr20_zone_names:
            if gr20_name in zone_name_upper or zone_name_upper in gr20_name:
                gr20_zones.append(zone)
                break
    
    return gr20_zones

def main():
    """Main function to analyze zone data."""
    print("GR20 Zone Data Analysis")
    print("="*60)
    print("Extracting only provable zone ID to name mappings...")
    print()
    
    # Analyze website
    zone_data = analyze_website_for_zone_data()
    
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    
    if zone_data:
        print(f"Found {len(zone_data)} potential zone mappings:")
        for zone in zone_data:
            print(f"  {zone['zone_id']} → {zone['zone_name']} (Source: {zone['source']})")
        
        # Filter for GR20 zones
        gr20_zones = filter_gr20_zones(zone_data)
        
        print(f"\nGR20-relevant zones found: {len(gr20_zones)}")
        for zone in gr20_zones:
            print(f"  {zone['zone_id']} → {zone['zone_name']} (Source: {zone['source']})")
        
        if not gr20_zones:
            print("  No GR20-relevant zones found in the extracted data.")
    else:
        print("No zone mappings found in the website analysis.")
        print("This means:")
        print("1. The zone data is not in the HTML/JavaScript")
        print("2. The data is loaded dynamically")
        print("3. The data is in a different format")
        print("4. The data requires authentication")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    print("1. If no data found: Manual analysis of the website required")
    print("2. If data found: Verify each mapping with official sources")
    print("3. Consider using browser developer tools for dynamic content")
    print("4. Check for API endpoints that might require authentication")

if __name__ == "__main__":
    main() 