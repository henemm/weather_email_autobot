#!/usr/bin/env python3
"""
Check detailed vigilance warnings for Corsica
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from wetter.warning import fetch_vigilance_text_warnings

def main():
    result = fetch_vigilance_text_warnings()
    print("VIGILANCE_API Details:")
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        data = result['data']
        product = data.get('product', {})
        corsica_warnings = [
            bloc for bloc in product.get('text_bloc_items', [])
            if bloc.get('domain_id') in ['2A', '2B', 'CORSE']
        ]
        
        print(f"Korsika-Warnungen: {len(corsica_warnings)}")
        print()
        
        for warning in corsica_warnings:
            print(f"Domain: {warning.get('domain_id')} - {warning.get('domain_name')}")
            print(f"  Phenomenon: {warning.get('phenomenon_max_name', 'N/A')}")
            print(f"  Level: {warning.get('phenomenon_max_color_id', 'N/A')}")
            print(f"  Content: {warning.get('text_bloc_content', 'N/A')[:500]}")
            print()

if __name__ == "__main__":
    main() 