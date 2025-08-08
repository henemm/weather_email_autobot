#!/usr/bin/env python3
"""
Detailed analysis of MeteoFrance API to answer specific questions.
"""

import sys
import json
from datetime import datetime
from meteofrance_api.client import MeteoFranceClient

def detailed_api_analysis():
    """Detailed analysis to answer specific questions about the API."""
    
    print("Detailed MeteoFrance API Analysis - Answering Specific Questions")
    print("=" * 70)
    
    # Test coordinates
    lat = 41.79418
    lon = 9.259567
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        print(f"Analysis for coordinates: {lat}, {lon}")
        print(f"Timestamp: {datetime.now()}")
        print()
        
        # 1. PROBABILITY_FORECAST ANALYSIS
        print("1. PROBABILITY_FORECAST - Was bedeutet dieser Wert?")
        print("-" * 55)
        if hasattr(forecast, 'probability_forecast') and forecast.probability_forecast:
            print(f"Anzahl Einträge: {len(forecast.probability_forecast)}")
            print("Beispiel-Einträge:")
            for i, entry in enumerate(forecast.probability_forecast[:5]):
                dt_time = datetime.fromtimestamp(entry['dt'])
                print(f"  Eintrag {i+1}: {dt_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"    Rain 3h: {entry['rain']['3h']}")
                print(f"    Rain 6h: {entry['rain']['6h']}")
                print(f"    Snow 3h: {entry['snow']['3h']}")
                print(f"    Snow 6h: {entry['snow']['6h']}")
                print(f"    Freezing: {entry['freezing']}")
                print()
        else:
            print("Keine probability_forecast Daten verfügbar")
        print()
        
        # 2. WEATHER BESCHREIBUNGEN - Zeitfenster und Form
        print("2. WEATHER/WETTERBESCHREIBUNGEN - Stündlich? In welcher Form?")
        print("-" * 65)
        if forecast.forecast:
            print("Stündliche Wetterbeschreibungen:")
            for i, entry in enumerate(forecast.forecast[:10]):  # Erste 10 Einträge
                dt_time = datetime.fromtimestamp(entry['dt'])
                weather = entry.get('weather', {})
                desc = weather.get('desc', 'N/A')
                icon = weather.get('icon', 'N/A')
                print(f"  {dt_time.strftime('%Y-%m-%d %H:%M')}: {desc} (Icon: {icon})")
        print()
        
        # 3. WIND DATEN - Wind und Windböen
        print("3. WIND DATEN - Wind und Windböen (gust)")
        print("-" * 40)
        if forecast.forecast:
            print("Wind-Daten (erste 10 Einträge):")
            for i, entry in enumerate(forecast.forecast[:10]):
                dt_time = datetime.fromtimestamp(entry['dt'])
                wind = entry.get('wind', {})
                speed = wind.get('speed', 'N/A')
                gust = wind.get('gust', 'N/A')
                direction = wind.get('direction', 'N/A')
                icon = wind.get('icon', 'N/A')
                print(f"  {dt_time.strftime('%H:%M')}: Speed={speed}km/h, Gust={gust}km/h, Dir={direction}°, Icon={icon}")
        print()
        
        # 4. REGENWAHRSCHEINLICHKEIT - Exemplarische Ausgabe
        print("4. REGENWAHRSCHEINLICHKEIT - Exemplarische API-Ausgabe")
        print("-" * 55)
        if hasattr(forecast, 'probability_forecast') and forecast.probability_forecast:
            print("Probability Forecast Raw Data:")
            for i, entry in enumerate(forecast.probability_forecast[:3]):
                dt_time = datetime.fromtimestamp(entry['dt'])
                print(f"Zeitpunkt {i+1}: {dt_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"  Raw entry: {json.dumps(entry, indent=4, default=str)}")
                print()
        else:
            print("Keine probability_forecast Daten verfügbar")
        print()
        
        # 5. GEWITTER ZEITPUNKT - Gibt es Zeitpunkte für Gewitter?
        print("5. GEWITTER ZEITPUNKT - Gibt es Zeitpunkte für Gewitter?")
        print("-" * 55)
        thunderstorm_entries = []
        for entry in forecast.forecast:
            weather = entry.get('weather', {})
            desc = weather.get('desc', '').lower()
            if any(keyword in desc for keyword in ['orage', 'thunderstorm', 'éclair', 'orages', 'averses orageuses']):
                dt_time = datetime.fromtimestamp(entry['dt'])
                thunderstorm_entries.append({
                    'time': dt_time,
                    'description': weather.get('desc', ''),
                    'icon': weather.get('icon', ''),
                    'rain_amount': entry.get('rain', {}).get('1h', 0),
                    'wind_speed': entry.get('wind', {}).get('speed', 0)
                })
        
        if thunderstorm_entries:
            print(f"Gefundene Gewitter-Einträge: {len(thunderstorm_entries)}")
            for entry in thunderstorm_entries:
                print(f"  {entry['time'].strftime('%Y-%m-%d %H:%M')}: {entry['description']}")
                print(f"    Icon: {entry['icon']}, Regen: {entry['rain_amount']}mm/h, Wind: {entry['wind_speed']}km/h")
        else:
            print("Keine Gewitter in den aktuellen Daten gefunden")
        print()
        
        # 6. ZEITFENSTER ANALYSE - Für welche Zeitfenster sind Daten verfügbar?
        print("6. ZEITFENSTER ANALYSE - Für welche Zeitfenster sind Daten verfügbar?")
        print("-" * 65)
        if forecast.forecast:
            first_time = datetime.fromtimestamp(forecast.forecast[0]['dt'])
            last_time = datetime.fromtimestamp(forecast.forecast[-1]['dt'])
            print(f"Stündliche Daten: {first_time} bis {last_time}")
            print(f"Gesamtstunden: {(last_time - first_time).total_seconds() / 3600:.1f}")
        
        if hasattr(forecast, 'daily_forecast') and forecast.daily_forecast:
            first_daily = datetime.fromtimestamp(forecast.daily_forecast[0]['dt'])
            last_daily = datetime.fromtimestamp(forecast.daily_forecast[-1]['dt'])
            print(f"Tagesdaten: {first_daily.date()} bis {last_daily.date()}")
            print(f"Anzahl Tage: {len(forecast.daily_forecast)}")
        
        if hasattr(forecast, 'probability_forecast') and forecast.probability_forecast:
            first_prob = datetime.fromtimestamp(forecast.probability_forecast[0]['dt'])
            last_prob = datetime.fromtimestamp(forecast.probability_forecast[-1]['dt'])
            print(f"Wahrscheinlichkeitsdaten: {first_prob} bis {last_prob}")
            print(f"Anzahl Einträge: {len(forecast.probability_forecast)}")
        print()
        
        # 7. REGENWAHRSCHEINLICHKEIT UMRECHNUNG - Exemplarisch
        print("7. REGENWAHRSCHEINLICHKEIT UMRECHNUNG - Exemplarisch")
        print("-" * 55)
        if hasattr(forecast, 'probability_forecast') and forecast.probability_forecast:
            print("Beispiel für Regenwahrscheinlichkeit-Umrechnung:")
            for i, entry in enumerate(forecast.probability_forecast[:3]):
                dt_time = datetime.fromtimestamp(entry['dt'])
                rain_3h = entry['rain']['3h']
                rain_6h = entry['rain']['6h']
                
                print(f"Zeitpunkt {i+1}: {dt_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"  Raw 3h: {rain_3h}")
                print(f"  Raw 6h: {rain_6h}")
                
                # Interpretation
                if rain_3h is not None:
                    print(f"  Interpretation 3h: {rain_3h}% Regenwahrscheinlichkeit in den nächsten 3 Stunden")
                if rain_6h is not None:
                    print(f"  Interpretation 6h: {rain_6h}% Regenwahrscheinlichkeit in den nächsten 6 Stunden")
                print()
        else:
            print("Keine probability_forecast Daten für Umrechnung verfügbar")
        
        print("=" * 70)
        print("Detaillierte Analyse abgeschlossen!")
        
    except Exception as e:
        print(f"Fehler bei der detaillierten Analyse: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    detailed_api_analysis() 