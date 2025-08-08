#!/usr/bin/env python3
"""
Analyze thunderstorm data over extended time periods.
"""

import json
from datetime import datetime, timedelta
from meteofrance_api.client import MeteoFranceClient

def analyze_extended_thunderstorm():
    """Analyze thunderstorm data over extended periods."""
    
    # Test coordinates
    lat = 42.471359
    lon = 2.029742
    
    print("⚡ Erweiterte Gewitter-Analyse")
    print("=" * 50)
    print(f"Koordinaten: {lat}, {lon}")
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        print(f"📊 Gesamtanzahl Forecast-Einträge: {len(forecast.forecast)}")
        print()
        
        # Group entries by date
        entries_by_date = {}
        
        for entry in forecast.forecast:
            dt_timestamp = entry.get('dt')
            if dt_timestamp:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                date_key = entry_datetime.date()
                
                if date_key not in entries_by_date:
                    entries_by_date[date_key] = []
                
                entries_by_date[date_key].append({
                    'datetime': entry_datetime,
                    'entry': entry
                })
        
        # Sort dates
        sorted_dates = sorted(entries_by_date.keys())
        
        print("📅 GEWITTER NACH DATUM:")
        print("-" * 40)
        
        thunderstorm_dates = []
        
        for date in sorted_dates:
            date_entries = entries_by_date[date]
            thunderstorm_entries = []
            
            for entry_data in date_entries:
                weather = entry_data['entry'].get('weather', {})
                if isinstance(weather, dict):
                    desc = weather.get('desc', '').lower()
                    if any(keyword in desc for keyword in ['orage', 'thunderstorm', 'risque']):
                        thunderstorm_entries.append(entry_data)
            
            if thunderstorm_entries:
                thunderstorm_dates.append(date)
                print(f"\n📅 {date.strftime('%Y-%m-%d')} ({date.strftime('%A')}):")
                
                for entry_data in thunderstorm_entries:
                    dt = entry_data['datetime']
                    entry = entry_data['entry']
                    weather = entry.get('weather', {})
                    rain = entry.get('rain', {})
                    
                    print(f"  {dt.strftime('%H:%M')} - {weather.get('desc')}")
                    print(f"    Temperatur: {entry.get('T', {}).get('value')}°C")
                    print(f"    Niederschlag: {rain}")
                    print(f"    Windböen: {entry.get('wind', {}).get('gust')} km/h")
                    print()
        
        # Calculate time spans
        if thunderstorm_dates:
            first_date = min(thunderstorm_dates)
            last_date = max(thunderstorm_dates)
            span_days = (last_date - first_date).days
            
            print("📊 ZEITSPANNE-ANALYSE:")
            print("-" * 30)
            print(f"Erstes Gewitter: {first_date.strftime('%Y-%m-%d')}")
            print(f"Letztes Gewitter: {last_date.strftime('%Y-%m-%d')}")
            print(f"Zeitspanne: {span_days} Tage")
            print(f"Anzahl Tage mit Gewitter: {len(thunderstorm_dates)}")
            
            # Check if beyond 48h
            today = datetime.now().date()
            days_ahead = [(date - today).days for date in thunderstorm_dates]
            max_days_ahead = max(days_ahead)
            
            print(f"Max. Tage in die Zukunft: {max_days_ahead}")
            
            if max_days_ahead > 2:
                print("⚠️  GEWITTER-VORHERSAGE ÜBER 48H HINAUS!")
            else:
                print("✅ Gewitter-Vorhersage innerhalb 48h")
        
        # Show all thunderstorm entries with full details
        print("\n🔍 ALLE GEWITTER-EINTRÄGE (VOLLSTÄNDIG):")
        print("-" * 50)
        
        thunderstorm_count = 0
        for entry in forecast.forecast:
            weather = entry.get('weather', {})
            if isinstance(weather, dict):
                desc = weather.get('desc', '').lower()
                if any(keyword in desc for keyword in ['orage', 'thunderstorm', 'risque']):
                    dt_timestamp = entry.get('dt')
                    if dt_timestamp:
                        entry_datetime = datetime.fromtimestamp(dt_timestamp)
                        thunderstorm_count += 1
                        
                        print(f"\n⚡ Gewitter {thunderstorm_count} - {entry_datetime.strftime('%Y-%m-%d %H:%M')}:")
                        print(json.dumps(entry, indent=2, default=str))
        
        print(f"\n📊 Gesamtanzahl Gewitter-Einträge: {thunderstorm_count}")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_extended_thunderstorm() 