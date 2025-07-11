#!/usr/bin/env python3
"""
Extract Massif Data from HTML Table

This script extracts the massif data from the HTML table found on the website.
"""

import requests
from bs4 import BeautifulSoup
import re

def extract_massif_data():
    """Extract massif data from the HTML table."""
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    print(f"Extracting massif data from: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the massif table
        massif_table = soup.find('table', id='tabm')
        
        if not massif_table:
            print("Massif table not found!")
            return []
        
        print("Found massif table!")
        
        # Extract rows from the table body
        tbody = massif_table.find('tbody')
        if not tbody:
            print("Table body not found!")
            return []
        
        rows = tbody.find_all('tr')
        print(f"Found {len(rows)} rows in table")
        
        massif_data = []
        
        for row in rows:
            # Get the row ID
            row_id = row.get('id', '')
            
            # Get all cells in the row
            cells = row.find_all('td')
            
            if len(cells) >= 2:
                # First cell might contain (*) or number
                first_cell = cells[0].get_text(strip=True)
                # Second cell contains the massif name
                second_cell = cells[1].get_text(strip=True)
                
                # Check if this is a massif row (has a numeric ID)
                if row_id.isdigit():
                    massif_id = int(row_id)
                    massif_name = second_cell
                    
                    # Check if it's marked with (*)
                    is_restricted = '(*)' in massif_name
                    
                    massif_data.append({
                        'id': massif_id,
                        'name': massif_name,
                        'restricted': is_restricted
                    })
                    
                    print(f"  Massif {massif_id}: {massif_name} {'(RESTRICTED)' if is_restricted else ''}")
        
        return massif_data
        
    except Exception as e:
        print(f"Error extracting massif data: {e}")
        return []

def extract_zone_data():
    """Try to extract zone data from the page."""
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    print(f"\nTrying to extract zone data from: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for any zone-related content in the page
        page_text = soup.get_text()
        
        # Look for zone names mentioned in the text
        zone_names = ["BALAGNE", "MONTI", "MONTAGNE", "COTE DES NACRES", 
                     "MOYENNE MONTAGNE SUD", "REGION DE CONCA"]
        
        found_zones = []
        
        for zone_name in zone_names:
            if zone_name.lower() in page_text.lower():
                # Find context around the zone name
                matches = re.finditer(rf'.{{0,100}}{zone_name}.{{0,100}}', page_text, re.IGNORECASE)
                print(f"\nFound '{zone_name}' in context:")
                for match in matches[:2]:  # Show first 2 matches
                    print(f"  ...{match.group()}...")
                found_zones.append(zone_name)
        
        if not found_zones:
            print("No GR20 zone names found in the page text.")
        
        return found_zones
        
    except Exception as e:
        print(f"Error extracting zone data: {e}")
        return []

def main():
    """Main function."""
    print("EXTRACTING DATA FROM WEBSITE")
    print("="*60)
    
    # Extract massif data
    massif_data = extract_massif_data()
    
    # Extract zone data
    zone_data = extract_zone_data()
    
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    
    print(f"Massifs found: {len(massif_data)}")
    for massif in massif_data:
        status = "RESTRICTED" if massif['restricted'] else "OPEN"
        print(f"  {massif['id']} → {massif['name']} ({status})")
    
    print(f"\nGR20 zones mentioned: {len(zone_data)}")
    for zone in zone_data:
        print(f"  {zone}")
    
    # Check which massifs are GR20-relevant
    gr20_massif_ids = [1, 29, 3, 4, 5, 6, 9, 10, 16, 24, 25, 26, 27, 28]
    
    gr20_massifs = [m for m in massif_data if m['id'] in gr20_massif_ids]
    restricted_gr20_massifs = [m for m in gr20_massifs if m['restricted']]
    
    print(f"\nGR20-relevant massifs found: {len(gr20_massifs)}")
    for massif in gr20_massifs:
        status = "RESTRICTED" if massif['restricted'] else "OPEN"
        print(f"  {massif['id']} → {massif['name']} ({status})")
    
    print(f"\nGR20 restricted massifs: {len(restricted_gr20_massifs)}")
    restricted_ids = [m['id'] for m in restricted_gr20_massifs]
    print(f"  IDs: {', '.join(map(str, restricted_ids))}")

if __name__ == "__main__":
    main() 