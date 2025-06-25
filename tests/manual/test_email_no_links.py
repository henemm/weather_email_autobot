#!/usr/bin/env python3
"""
Test that emails no longer contain links
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from notification.email_client import generate_gr20_report_text
from datetime import datetime

def main():
    print("TEST: E-MAIL OHNE LINKS")
    print("=" * 40)
    
    # Test configuration (with links that should be ignored)
    config = {
        "link_template": {
            "sharemap": "https://share.garmin.com/PDFCF",
            "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
        }
    }
    
    # Test report data
    report_data = {
        "location": "Conca, Korsika",
        "risk_percentage": 75,
        "risk_description": "Gewitter",
        "report_time": datetime.now(),
        "report_type": "scheduled"
    }
    
    # Generate email text
    email_text = generate_gr20_report_text(report_data, config)
    
    print(f"Generierter E-Mail-Text:")
    print(f"'{email_text}'")
    print(f"Länge: {len(email_text)} Zeichen")
    print()
    
    # Check for links
    link_indicators = ['http', 'https', 'www.', '.com', '.fr', 'share.garmin']
    found_links = []
    
    for indicator in link_indicators:
        if indicator in email_text.lower():
            found_links.append(indicator)
    
    if found_links:
        print(f"❌ LINKS GEFUNDEN: {found_links}")
        return False
    else:
        print("✅ KEINE LINKS GEFUNDEN")
        return True

if __name__ == "__main__":
    main() 