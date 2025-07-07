#!/usr/bin/env python3
"""
Debug script to check fire risk API data directly.
"""

import sys
import os
import requests
import json
from datetime import date

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.wetter.fire_risk_massif import FireRiskZone

def check_api_data():
    """Check the fire risk API data directly."""
    print("🔥 Fire Risk API Debug")
    print(f"Date: {date.today()}")
    
    # Check today's data
    today = date.today()
    date_str = today.strftime("%Y%m%d")
    url = f"https://www.risque-prevention-incendie.fr/static/20/import_data/{date_str}.json"
    
    print(f"Fetching: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"Response status: {response.status_code}")
        print(f"Data keys: {list(data.keys())}")
        
        if 'massifs' in data:
            massifs_data = data['massifs']
            print(f"Massifs data type: {type(massifs_data)}")
            
            if isinstance(massifs_data, dict):
                print(f"Number of massifs: {len(massifs_data)}")
                print("Massif IDs:", list(massifs_data.keys()))
                
                # Show first few massifs
                for i, (massif_id, massif_data) in enumerate(massifs_data.items()):
                    if i < 5:  # Show first 5
                        print(f"  Massif {massif_id} (type: {type(massif_id)}): {massif_data}")
                        print(f"    Massif data type: {type(massif_data)}")
                        if isinstance(massif_data, list):
                            print(f"    List length: {len(massif_data)}")
                            for j, item in enumerate(massif_data):
                                print(f"      Item {j}: {item} (type: {type(item)})")
            elif isinstance(massifs_data, list):
                print(f"Number of massifs: {len(massifs_data)}")
                for i, massif in enumerate(massifs_data[:3]):  # Show first 3
                    print(f"  Massif {i}: {massif}")
        else:
            print("No 'massifs' key found in data")
            print("Available keys:", list(data.keys()))
            
    except Exception as e:
        print(f"Error fetching API data: {e}")

def test_massif_mapping():
    """Test massif mapping for Corsican locations."""
    print("\n" + "="*60)
    print("Testing Massif Mapping")
    print("="*60)
    
    locations = {
        "Corte": (42.3061, 9.1500),
        "Ajaccio": (41.9192, 8.7386),
        "Bastia": (42.6977, 9.4500),
        "Calanzana": (42.5083, 8.9500),
        "Calvi": (42.5667, 8.7500),
    }
    
    try:
        fire_risk = FireRiskZone()
        
        for name, (lat, lon) in locations.items():
            massif_id = fire_risk._get_massif_for_coordinates(lat, lon)
            massif_name = fire_risk._get_massif_name(massif_id) if massif_id else "Unknown"
            print(f"{name}: Massif ID {massif_id} ({massif_name})")
            
    except Exception as e:
        print(f"Error testing massif mapping: {e}")

def main():
    """Run debug checks."""
    check_api_data()
    test_massif_mapping()

if __name__ == "__main__":
    main() 