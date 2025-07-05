#!/usr/bin/env python3
"""
Detailed debug script to examine all possible fields in the meteofrance API response.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meteofrance_api.client import MeteoFranceClient


def debug_api_detailed():
    """Debug the meteofrance API response in detail."""
    
    # Test coordinates (Asco)
    latitude = 42.426238
    longitude = 8.900291
    
    print(f"🔍 DETAILED MÉTÉO-FRANCE API ANALYSIS")
    print("=" * 60)
    print(f"Coordinates: {latitude}, {longitude}")
    print()
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(latitude, longitude)
        
        if not forecast.forecast:
            print("❌ No forecast data received")
            return
        
        print(f"✅ Received {len(forecast.forecast)} forecast entries")
        print()
        
        # Find entries for today 14-17 Uhr
        today_entries = []
        for i, entry in enumerate(forecast.forecast):
            dt_timestamp = entry.get('dt')
            if dt_timestamp:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                today = datetime.now().date()
                
                if entry_datetime.date() == today and 14 <= entry_datetime.hour <= 17:
                    today_entries.append({
                        'index': i,
                        'datetime': entry_datetime,
                        'entry': entry
                    })
        
        print(f"📅 Found {len(today_entries)} entries for today 14-17 Uhr:")
        print()
        
        for entry_info in today_entries:
            i = entry_info['index']
            dt = entry_info['datetime']
            entry = entry_info['entry']
            
            print(f"🕐 ENTRY {i+1} - {dt.strftime('%Y-%m-%d %H:%M')} (Hour {dt.hour}):")
            print("-" * 50)
            
            # Show all fields in detail
            print("📋 ALL FIELDS:")
            for key, value in entry.items():
                print(f"  {key}: {value}")
            
            print()
            
            # Look specifically for probability-related fields
            print("🔍 PROBABILITY ANALYSIS:")
            
            # Check for precipitation_probability
            precip_prob = entry.get('precipitation_probability')
            print(f"  precipitation_probability: {precip_prob}")
            
            # Check for any field containing 'prob'
            prob_fields = {k: v for k, v in entry.items() if 'prob' in k.lower()}
            if prob_fields:
                print(f"  Fields containing 'prob': {prob_fields}")
            else:
                print("  No fields containing 'prob' found")
            
            # Check for any field containing 'rain'
            rain_fields = {k: v for k, v in entry.items() if 'rain' in k.lower()}
            if rain_fields:
                print(f"  Fields containing 'rain': {rain_fields}")
            else:
                print("  No fields containing 'rain' found")
            
            # Check for any field containing 'precip'
            precip_fields = {k: v for k, v in entry.items() if 'precip' in k.lower()}
            if precip_fields:
                print(f"  Fields containing 'precip': {precip_fields}")
            else:
                print("  No fields containing 'precip' found")
            
            # Check weather description
            weather = entry.get('weather', {})
            if isinstance(weather, dict):
                weather_desc = weather.get('desc', 'Unknown')
                print(f"  Weather description: {weather_desc}")
                
                # Check if weather description indicates rain probability
                if 'averse' in weather_desc.lower() or 'pluie' in weather_desc.lower():
                    print(f"    -> Weather description suggests rain!")
            
            print()
            print("=" * 50)
            print()
        
        # Save detailed data to file
        output_file = "output/debug/detailed_api_analysis.json"
        Path("output/debug").mkdir(parents=True, exist_ok=True)
        
        detailed_data = {
            'timestamp': datetime.now().isoformat(),
            'coordinates': {'lat': latitude, 'lon': longitude},
            'total_entries': len(forecast.forecast),
            'today_entries': [
                {
                    'index': entry['index'],
                    'datetime': entry['datetime'].isoformat(),
                    'all_fields': entry['entry'],
                    'weather_description': entry['entry'].get('weather', {}).get('desc') if isinstance(entry['entry'].get('weather'), dict) else str(entry['entry'].get('weather')),
                    'precipitation_probability': entry['entry'].get('precipitation_probability'),
                    'rain_data': entry['entry'].get('rain', {}),
                    'temperature': entry['entry'].get('T', {}),
                    'wind': entry['entry'].get('wind', {})
                }
                for entry in today_entries
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, default=str)
        
        print(f"💾 Detailed analysis saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_api_detailed() 