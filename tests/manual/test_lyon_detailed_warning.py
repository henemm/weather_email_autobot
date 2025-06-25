#!/usr/bin/env python3
"""
Test detailed Lyon warning with German translation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from wetter.warning import get_vigilance_summary

def main():
    print("LYON VIGILANCE - MIT DEUTSCHER ÜBERSETZUNG:")
    print("=" * 50)
    
    result = get_vigilance_summary()
    lyon = [w for w in result['warnings'] if w['domain_id'] == '69' and w['is_active']]
    
    print(f"Aktive Lyon-Warnungen: {len(lyon)}")
    print()
    
    for i, warning in enumerate(lyon[:2], 1):
        print(f"Warnung {i}:")
        print(f"  {warning['german_summary']}")
        print(f"  Risiko-Level: {warning['risk_level']} ({warning['risk_name']})")
        print(f"  Gültig bis: {warning['end_time']}")
        
        details = warning['details']
        if details['qualification']:
            print(f"  Qualifikation: {details['qualification'][:150]}...")
        if details['situation']:
            print(f"  Situation: {details['situation'][:150]}...")
        if details['evolution']:
            print(f"  Entwicklung: {details['evolution'][:150]}...")
        print()

if __name__ == "__main__":
    main() 