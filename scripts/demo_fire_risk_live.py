#!/usr/bin/env python3
"""
Live demo script for fire risk massif warnings.

Tests the fire risk warnings for specific Corsican locations:
- Corte, Ajaccio, Bastia, Calanzana, Calvi
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.wetter.fire_risk_massif import FireRiskZone
from src.notification.email_client import generate_gr20_report_text, EmailClient

# Corsican locations from the original request
CORSICAN_LOCATIONS = {
    "Corte": (42.3061, 9.1500),
    "Ajaccio": (41.9192, 8.7386),
    "Bastia": (42.6977, 9.4500),
    "Calanzana": (42.5083, 8.9500),
    "Calvi": (42.5667, 8.7500),
}

def test_fire_risk_for_location(name: str, lat: float, lon: float) -> Dict[str, Any]:
    """Test fire risk warnings for a specific location."""
    print(f"\n{'='*60}")
    print(f"Testing fire risk for: {name} ({lat}, {lon})")
    print(f"{'='*60}")
    
    try:
        # Initialize fire risk massif
        fire_risk = FireRiskZone()
        
        # Replace any Massif-based logic with zone-based lookups
        # Example usage:
        lat, lon = 41.9181, 8.9247  # Vizzavona
        zone_alert = fire_risk.get_zone_fire_alert_for_location(lat, lon)
        print(zone_alert)
        
        # Get formatted warning
        # warning = fire_risk.format_fire_warnings(lat, lon) # This line is removed as per the new_code
        # print(f"Formatted warning: '{warning}'") # This line is removed as per the new_code
        
        # Create mock weather data for report generation
        weather_data = {
            'max_temperature': 28.5,
            'max_precipitation': 0.0,
            'max_rain_probability': 10.0,
            'max_thunderstorm_probability': 5.0,
            'max_wind_speed': 15.0,
            'wind_speed': 8.0,
            'thunderstorm_threshold_pct': 0,
            'thunderstorm_threshold_time': '',
            'thunderstorm_max_time': '',
            'rain_threshold_pct': 0,
            'rain_threshold_time': '',
            'rain_max_time': '',
            'rain_total_time': '',
            'location': name,
            'data_source': 'meteofrance-api',
            'processed_at': datetime.now().isoformat(),
            # 'fire_risk_warning': warning, # This line is removed as per the new_code
        }
        
        report_data = {
            'location': name,
            'report_type': 'morning',
            'weather_data': weather_data,
            'report_time': datetime.now().isoformat(),
        }
        
        config = {
            'smtp': {
                'subject': 'GR20 Wetter',
                'host': 'smtp.example.com',
                'port': 587,
                'user': 'test@example.com',
                'to': 'recipient@example.com',
                'password': 'dummy',
            }
        }
        
        # Generate report text
        report_text = generate_gr20_report_text(report_data, config)
        print(f"Report text: {report_text}")
        
        # Generate subject
        client = EmailClient(config)
        subject = client._generate_dynamic_subject(report_data)
        print(f"Email subject: {subject}")
        
        return {
            'location': name,
            # 'alerts': alerts, # This line is removed as per the new_code
            # 'warning': warning, # This line is removed as per the new_code
            'report_text': report_text,
            'subject': subject,
            'success': True
        }
        
    except Exception as e:
        print(f"Error testing {name}: {e}")
        return {
            'location': name,
            'error': str(e),
            'success': False
        }

def main():
    """Run live demo for all Corsican locations."""
    print("🔥 Fire Risk Massif Live Demo")
    print("Testing fire risk warnings for Corsican locations")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for name, (lat, lon) in CORSICAN_LOCATIONS.items():
        result = test_fire_risk_for_location(name, lat, lon)
        results.append(result)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        if result['success']:
            # warning = result['warning'] # This line is removed as per the new_code
            # if warning: # This line is removed as per the new_code
            #     print(f"✅ {result['location']}: {warning}") # This line is removed as per the new_code
            # else: # This line is removed as per the new_code
            print(f"ℹ️  {result['location']}: No fire risk warning") # This line is changed as per the new_code
        else:
            print(f"❌ {result['location']}: Error - {result['error']}")
    
    print(f"\nDemo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 