#!/usr/bin/env python3
"""
Detailed analysis of vigilance warnings for Corsica
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from wetter.warning import fetch_vigilance_text_warnings
import json

def main():
    result = fetch_vigilance_text_warnings()
    print("VIGILANCE_API - Detaillierte Analyse:")
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        data = result['data']
        product = data.get('product', {})
        
        # Find Corsica-specific warnings
        corsica_items = [
            item for item in product.get('text_bloc_items', [])
            if item.get('domain_id') in ['2A', '2B', 'CORSE']
        ]
        
        print(f"\nKorsika-spezifische Warnungen: {len(corsica_items)}")
        print()
        
        for item in corsica_items:
            print(f"Domain: {item['domain_id']} - {item['domain_name']}")
            print(f"Title: {item['bloc_title']}")
            print(f"Items: {len(item.get('bloc_items', []))}")
            
            # Check for actual warning content
            bloc_items = item.get('bloc_items', [])
            for bloc_item in bloc_items:
                print(f"  - {bloc_item.get('type_name', 'N/A')}")
                text_items = bloc_item.get('text_items', [])
                for text_item in text_items:
                    term_items = text_item.get('term_items', [])
                    for term in term_items:
                        print(f"    Risk: {term.get('risk_name', 'N/A')} (Level {term.get('risk_code', 'N/A')})")
                        print(f"    Time: {term.get('start_time', 'N/A')} to {term.get('end_time', 'N/A')}")
                        print(f"    Hazard: {term.get('hazard_name', 'N/A')}")
            print()
        
        # Check for any active warnings
        print("Aktive Warnungen in ganz Frankreich:")
        all_items = product.get('text_bloc_items', [])
        for item in all_items:
            bloc_items = item.get('bloc_items', [])
            for bloc_item in bloc_items:
                text_items = bloc_item.get('text_items', [])
                for text_item in text_items:
                    term_items = text_item.get('term_items', [])
                    for term in term_items:
                        risk_level = term.get('risk_code', '0')
                        if risk_level in ['3', '4']:  # Orange or Red
                            print(f"  {item.get('domain_name', 'N/A')}: {term.get('risk_name', 'N/A')} - {term.get('hazard_name', 'N/A')}")

if __name__ == "__main__":
    main() 