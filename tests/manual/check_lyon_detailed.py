#!/usr/bin/env python3
"""
Extract detailed vigilance warning text for Lyon
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from wetter.warning import fetch_vigilance_text_warnings
import json

def main():
    result = fetch_vigilance_text_warnings()
    print("LYON VIGILANCE - DETAILLIERTE TEXTE:")
    print("=" * 50)
    
    if result['status'] == 'success':
        data = result['data']
        product = data.get('product', {})
        
        # Find Lyon-specific warnings
        lyon_items = [
            item for item in product.get('text_bloc_items', [])
            if item.get('domain_id') == '69'
        ]
        
        print(f"Lyon-spezifische Einträge: {len(lyon_items)}")
        print()
        
        for item in lyon_items:
            print(f"Domain: {item['domain_name']}")
            print(f"Title: {item['bloc_title']}")
            
            bloc_items = item.get('bloc_items', [])
            print(f"Items: {len(bloc_items)}")
            
            for bloc_item in bloc_items:
                print(f"  - {bloc_item.get('type_name', 'N/A')}")
                text_items = bloc_item.get('text_items', [])
                
                for text_item in text_items:
                    term_items = text_item.get('term_items', [])
                    
                    for term in term_items:
                        print(f"    Risk: {term.get('risk_name', 'N/A')} (Level {term.get('risk_code', 'N/A')})")
                        print(f"    Hazard: {term.get('hazard_name', 'N/A')}")
                        print(f"    Time: {term.get('start_time', 'N/A')} to {term.get('end_time', 'N/A')}")
                        
                        # Extract detailed text content
                        subdivision_text = term.get('subdivision_text', [])
                        if subdivision_text:
                            print("    Details:")
                            for subdiv in subdivision_text:
                                bold_text = subdiv.get('bold_text', '')
                                text_content = subdiv.get('text', [])
                                if bold_text:
                                    print(f"      {bold_text}")
                                for text_line in text_content:
                                    print(f"        {text_line}")
                        print()
            print()

if __name__ == "__main__":
    main() 