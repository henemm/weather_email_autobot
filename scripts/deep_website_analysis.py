#!/usr/bin/env python3
"""
Deep Website Analysis for Zone Data

This script performs a thorough analysis of the fire risk website
to find zone ID to name mappings using multiple approaches.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path

def analyze_main_page():
    """Analyze the main page thoroughly."""
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    print(f"Analyzing main page: {url}")
    print("="*60)
    
    try:
        # Try with different headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        print(f"Content type: {response.headers.get('content-type', 'unknown')}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for any data attributes or hidden fields
        print("\nLooking for data attributes...")
        data_elements = soup.find_all(attrs={"data-zone": True})
        print(f"Elements with data-zone: {len(data_elements)}")
        for elem in data_elements:
            print(f"  {elem.get('data-zone')} → {elem.text.strip()}")
        
        # Look for any elements with zone-related attributes
        zone_attrs = ['data-zone', 'data-zone-id', 'data-zone-name', 'zone-id', 'zone-name']
        for attr in zone_attrs:
            elements = soup.find_all(attrs={attr: True})
            if elements:
                print(f"Elements with {attr}: {len(elements)}")
                for elem in elements[:3]:
                    print(f"  {elem.get(attr)} → {elem.text.strip()[:50]}")
        
        # Check for any JSON-LD structured data
        print("\nLooking for JSON-LD structured data...")
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        print(f"JSON-LD scripts found: {len(json_ld_scripts)}")
        
        for i, script in enumerate(json_ld_scripts):
            try:
                data = json.loads(script.string)
                print(f"  JSON-LD {i+1}: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"  JSON-LD {i+1}: Invalid JSON")
        
        # Look for any map-related elements
        print("\nLooking for map elements...")
        map_elements = soup.find_all(['div', 'canvas'], class_=re.compile(r'map|leaflet|zone'))
        print(f"Map-related elements: {len(map_elements)}")
        
        for elem in map_elements[:5]:
            print(f"  {elem.name}.{elem.get('class', [])} - {elem.get('id', 'no-id')}")
        
        # Check all script contents more thoroughly
        print("\nAnalyzing all script contents...")
        scripts = soup.find_all('script')
        print(f"Total scripts: {len(scripts)}")
        
        for i, script in enumerate(scripts):
            if script.string:
                content = script.string
                print(f"\nScript {i+1} (length: {len(content)} chars)")
                
                # Look for any zone-related content
                zone_keywords = ['zone', 'balagne', 'monti', 'montagne', 'conca', 'calvi']
                found_keywords = []
                for keyword in zone_keywords:
                    if keyword.lower() in content.lower():
                        found_keywords.append(keyword)
                
                if found_keywords:
                    print(f"  Contains keywords: {found_keywords}")
                    
                    # Show context around keywords
                    for keyword in found_keywords:
                        matches = re.finditer(rf'.{{0,50}}{keyword}.{{0,50}}', content, re.IGNORECASE)
                        for match in matches[:2]:  # Show first 2 matches
                            print(f"    Context for '{keyword}': ...{match.group()}...")
        
        return soup
        
    except Exception as e:
        print(f"Error analyzing main page: {e}")
        return None

def try_different_urls():
    """Try different URL patterns that might contain zone data."""
    base_urls = [
        "https://www.risque-prevention-incendie.fr/corse",
        "https://www.risque-prevention-incendie.fr/",
        "https://www.risque-prevention-incendie.fr/api/",
        "https://www.risque-prevention-incendie.fr/data/",
    ]
    
    api_patterns = [
        "/api/zones",
        "/api/regions", 
        "/data/zones.json",
        "/data/regions.json",
        "/static/data/zones.json",
        "/static/20/data/zm.json",
        "/api/corse/zones",
        "/api/corse/regions",
    ]
    
    print("\n" + "="*60)
    print("TRYING DIFFERENT URL PATTERNS")
    print("="*60)
    
    found_data = []
    
    for base_url in base_urls:
        for pattern in api_patterns:
            url = base_url.rstrip('/') + pattern
            print(f"\nTrying: {url}")
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json, text/plain, */*',
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  Success! Content length: {len(response.content)}")
                    
                    # Try to parse as JSON
                    try:
                        data = response.json()
                        print(f"  JSON data: {json.dumps(data, indent=2)[:300]}...")
                        found_data.append({'url': url, 'data': data})
                    except json.JSONDecodeError:
                        print(f"  Not JSON: {response.text[:200]}...")
                        
            except Exception as e:
                print(f"  Error: {e}")
    
    return found_data

def check_for_dynamic_content():
    """Check if there are any hints about dynamic content loading."""
    print("\n" + "="*60)
    print("CHECKING FOR DYNAMIC CONTENT")
    print("="*60)
    
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for AJAX calls or fetch requests
        scripts = soup.find_all('script')
        
        ajax_patterns = [
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'ajax\s*\(\s*["\']([^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+)["\']',
            r'\.post\s*\(\s*["\']([^"\']+)["\']',
            r'XMLHttpRequest.*?open.*?["\']([^"\']+)["\']',
        ]
        
        for script in scripts:
            if script.string:
                content = script.string
                for pattern in ajax_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        print(f"Found AJAX/fetch calls: {matches}")
        
        # Look for any configuration or initialization data
        config_patterns = [
            r'config\s*=\s*\{[^}]*\}',
            r'init\s*\(\s*\{[^}]*\}',
            r'data\s*:\s*\{[^}]*\}',
        ]
        
        for script in scripts:
            if script.string:
                content = script.string
                for pattern in config_patterns:
                    matches = re.findall(pattern, content, re.DOTALL)
                    if matches:
                        print(f"Found config/init data: {matches}")
        
    except Exception as e:
        print(f"Error checking dynamic content: {e}")

def main():
    """Main analysis function."""
    print("DEEP WEBSITE ANALYSIS FOR ZONE DATA")
    print("="*60)
    
    # Analyze main page
    soup = analyze_main_page()
    
    # Try different URLs
    found_data = try_different_urls()
    
    # Check for dynamic content
    check_for_dynamic_content()
    
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    
    if found_data:
        print(f"Found {len(found_data)} data sources:")
        for item in found_data:
            print(f"  {item['url']}")
    else:
        print("No direct data sources found.")
        print("\nNext steps:")
        print("1. Use browser developer tools to inspect network requests")
        print("2. Check for JavaScript that loads data dynamically")
        print("3. Look for map initialization code")
        print("4. Examine any configuration files or settings")

if __name__ == "__main__":
    main() 