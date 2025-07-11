#!/usr/bin/env python3
"""
Examine HTML Structure

This script examines the actual HTML structure of the website
to understand how zone data is presented.
"""

import requests
from bs4 import BeautifulSoup
import re

def examine_html_structure():
    """Examine the HTML structure in detail."""
    url = "https://www.risque-prevention-incendie.fr/corse"
    
    print(f"Examining HTML structure: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Print the full HTML for inspection
        print("FULL HTML CONTENT:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        # Look for any table elements that might contain zone data
        print("\nLooking for tables...")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"\nTable {i+1}:")
            print(table.prettify()[:500] + "..." if len(table.prettify()) > 500 else table.prettify())
        
        # Look for any div elements with zone-related classes or IDs
        print("\nLooking for zone-related divs...")
        zone_divs = soup.find_all('div', class_=re.compile(r'zone|region|area|map', re.IGNORECASE))
        print(f"Found {len(zone_divs)} zone-related divs")
        
        for div in zone_divs:
            print(f"  {div.get('class', [])} - {div.get('id', 'no-id')} - {div.text.strip()[:100]}")
        
        # Look for any list elements that might contain zone data
        print("\nLooking for lists...")
        lists = soup.find_all(['ul', 'ol'])
        print(f"Found {len(lists)} lists")
        
        for i, lst in enumerate(lists):
            print(f"\nList {i+1}:")
            items = lst.find_all('li')
            for item in items[:5]:  # Show first 5 items
                print(f"  - {item.text.strip()}")
        
        # Look for any text content that mentions zones
        print("\nLooking for zone-related text...")
        body_text = soup.get_text()
        
        zone_keywords = ['balagne', 'monti', 'montagne', 'conca', 'calvi', 'zone', 'region']
        for keyword in zone_keywords:
            if keyword.lower() in body_text.lower():
                # Find context around the keyword
                matches = re.finditer(rf'.{{0,100}}{keyword}.{{0,100}}', body_text, re.IGNORECASE)
                print(f"\nFound '{keyword}' in context:")
                for match in matches[:3]:  # Show first 3 matches
                    print(f"  ...{match.group()}...")
        
        # Look for any form elements that might contain zone data
        print("\nLooking for forms...")
        forms = soup.find_all('form')
        print(f"Found {len(forms)} forms")
        
        for form in forms:
            print(f"  Form action: {form.get('action', 'no-action')}")
            inputs = form.find_all('input')
            for inp in inputs:
                print(f"    Input: {inp.get('name', 'no-name')} = {inp.get('value', 'no-value')}")
        
        # Look for any select elements (dropdowns)
        print("\nLooking for select elements...")
        selects = soup.find_all('select')
        print(f"Found {len(selects)} select elements")
        
        for select in selects:
            print(f"  Select name: {select.get('name', 'no-name')}")
            options = select.find_all('option')
            for option in options[:5]:  # Show first 5 options
                print(f"    Option: {option.get('value', 'no-value')} - {option.text.strip()}")
        
    except Exception as e:
        print(f"Error examining HTML: {e}")

if __name__ == "__main__":
    examine_html_structure() 