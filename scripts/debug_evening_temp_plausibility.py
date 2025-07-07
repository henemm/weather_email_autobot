#!/usr/bin/env python3
"""
Debug-Skript: Plausibilität von Nacht- und Tagestemperatur im Evening-Report

- Gibt alle Temperaturwerte für Nacht (22–05 Uhr) und Tag (05–17 Uhr) aus
- Zeigt Minimum (Nacht) und Maximum (Tag)
- Prüft, ob die Differenz plausibel ist
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.wetter.weather_data_processor import WeatherDataProcessor
import yaml


def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def debug_evening_temp_plausibility(latitude, longitude, location_name):
    config = load_config()
    processor = WeatherDataProcessor(config)
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    print(f"\n=== DEBUG: Evening-Report Temperatur-Plausibilität für {location_name} ===")
    print(f"Datum heute: {today}, morgen: {tomorrow}")

    # 1. Alle Forecast-Einträge holen
    client = None
    try:
        from src.wetter.fetch_meteofrance import MeteoFranceClient
        client = MeteoFranceClient()
    except Exception as e:
        print(f"Fehler beim Import von MeteoFranceClient: {e}")
        return

    forecast = client.get_forecast(latitude, longitude)
    if not forecast or not forecast.forecast:
        print("Keine Forecast-Daten verfügbar!")
        return

    # 2. Nacht: 22–05 Uhr (letzter Punkt der heutigen Etappe)
    night_temps = []
    for entry in forecast.forecast:
        dt = entry.get('dt')
        if not dt:
            continue
        dt_obj = datetime.fromtimestamp(dt)
        date_obj = dt_obj.date()
        hour = dt_obj.hour
        # Nacht: heute 22–23 Uhr, morgen 0–5 Uhr
        if (date_obj == today and hour >= 22) or (date_obj == tomorrow and hour <= 5):
            temp = entry.get('T', {}).get('value')
            night_temps.append((dt_obj.strftime('%Y-%m-%d %H:%M'), temp))

    # 3. Tag: 05–17 Uhr (alle Punkte der morgigen Etappe)
    day_temps = []
    for entry in forecast.forecast:
        dt = entry.get('dt')
        if not dt:
            continue
        dt_obj = datetime.fromtimestamp(dt)
        date_obj = dt_obj.date()
        hour = dt_obj.hour
        if date_obj == tomorrow and 5 <= hour <= 17:
            temp = entry.get('T', {}).get('value')
            day_temps.append((dt_obj.strftime('%Y-%m-%d %H:%M'), temp))

    print("\nNacht-Temperaturen (22–05 Uhr):")
    for t in night_temps:
        print(f"  {t[0]}: {t[1]}°C")
    if night_temps:
        min_night = min([t[1] for t in night_temps if t[1] is not None])
        print(f"--> Minimum Nacht: {min_night}°C")
    else:
        print("Keine Nachtwerte gefunden!")
        min_night = None

    print("\nTagestemperaturen (05–17 Uhr):")
    for t in day_temps:
        print(f"  {t[0]}: {t[1]}°C")
    if day_temps:
        max_day = max([t[1] for t in day_temps if t[1] is not None])
        print(f"--> Maximum Tag: {max_day}°C")
    else:
        print("Keine Tageswerte gefunden!")
        max_day = None

    # Plausibilitäts-Check
    if min_night is not None and max_day is not None:
        diff = max_day - min_night
        print(f"\nDifferenz Tag/Nacht: {max_day} - {min_night} = {diff}°C")
        if diff < 2:
            print("⚠️  WARNUNG: Tag- und Nachttemperatur liegen ungewöhnlich nah beieinander!")
        elif diff < 0:
            print("❌ FEHLER: Nachttemperatur ist höher als Tagestemperatur!")
        else:
            print("✅ Differenz ist plausibel.")
    else:
        print("(Nicht genug Daten für Plausibilitätsprüfung)")


if __name__ == "__main__":
    # Beispiel: Corte
    debug_evening_temp_plausibility(42.3069, 9.1497, "Corte") 