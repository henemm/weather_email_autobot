#!/usr/bin/env python3
"""
Analyze all possible hazard types in the vigilance API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from wetter.warning import fetch_vigilance_text_warnings
import re

def main():
    result = fetch_vigilance_text_warnings()
    print("ALLE MÖGLICHEN WARNWERTE IN DER VIGILANCE-API:")
    print("=" * 60)
    
    if result['status'] == 'success':
        data = result['data']
        product = data.get('product', {})
        
        # Collect all text content
        all_texts = []
        hazard_keywords = set()
        
        for item in product.get('text_bloc_items', []):
            for bloc_item in item.get('bloc_items', []):
                for text_item in bloc_item.get('text_items', []):
                    for term in text_item.get('term_items', []):
                        # Get all text content
                        subdivision_text = term.get('subdivision_text', [])
                        for subdiv in subdivision_text:
                            text_content = subdiv.get('text', [])
                            for text_line in text_content:
                                all_texts.append(text_line.lower())
        
        # Find French weather hazard terms
        french_hazards = {
            'canicule': 'Hitzewelle',
            'orages': 'Gewitter',
            'orage': 'Gewitter',
            'pluie': 'Regen',
            'pluies': 'Regen',
            'inondation': 'Überschwemmung',
            'inondations': 'Überschwemmung',
            'vent': 'Wind',
            'vents': 'Wind',
            'neige': 'Schnee',
            'neiges': 'Schnee',
            'avalanche': 'Lawine',
            'avalanches': 'Lawine',
            'vague': 'Welle',
            'vagues': 'Wellen',
            'submersion': 'Überflutung',
            'submersions': 'Überflutung',
            'tempête': 'Sturm',
            'tempêtes': 'Stürme',
            'cyclone': 'Zyklon',
            'cyclones': 'Zyklone',
            'sécheresse': 'Dürre',
            'sécheresses': 'Dürren',
            'gel': 'Frost',
            'gèle': 'Frost',
            'verglas': 'Glatteis',
            'brouillard': 'Nebel',
            'brouillards': 'Nebel',
            'chaleur': 'Hitze',
            'froid': 'Kälte',
            'crues': 'Hochwasser',
            'crue': 'Hochwasser'
        }
        
        # Find all occurrences
        found_hazards = {}
        for french, german in french_hazards.items():
            count = 0
            for text in all_texts:
                if french in text:
                    count += 1
            if count > 0:
                found_hazards[french] = {'german': german, 'count': count}
        
        print("Gefundene Warnwerte:")
        for french, info in sorted(found_hazards.items()):
            print(f"  {french} → {info['german']} ({info['count']} Vorkommen)")
        
        print(f"\nInsgesamt {len(found_hazards)} verschiedene Warnwerte gefunden")
        
        # Show some examples
        print("\nBeispiele aus den Texten:")
        for french in list(found_hazards.keys())[:5]:
            for text in all_texts:
                if french in text:
                    print(f"  '{french}' in: {text[:100]}...")
                    break

if __name__ == "__main__":
    main() 