#!/usr/bin/env python3
"""
Debug script for fire risk API response.
"""

import requests
from datetime import date
import json

def debug_api_response():
    """Debug the actual API response format."""
    today = date.today()
    date_str = today.strftime("%Y%m%d")
    url = f"https://www.risque-prevention-incendie.fr/static/20/import_data/{date_str}.json"
    
    print(f"🔍 Debugging API Response")
    print(f"URL: {url}")
    print(f"Date: {today}")
    print("=" * 60)
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Try to parse as JSON
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Length: {len(data) if isinstance(data, list) else 'N/A'}")
                
                if isinstance(data, list) and len(data) > 0:
                    print(f"\nFirst entry:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
                    
                    # Look for massif_id fields
                    for i, entry in enumerate(data):
                        if isinstance(entry, dict) and 'massif_id' in entry:
                            print(f"\nEntry {i} with massif_id:")
                            print(json.dumps(entry, indent=2, ensure_ascii=False))
                            break
                else:
                    print(f"\nRaw response (first 500 chars):")
                    print(repr(response.text[:500]))
                    
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response (first 500 chars):")
                print(repr(response.text[:500]))
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    debug_api_response() 