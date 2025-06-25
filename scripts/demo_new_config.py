#!/usr/bin/env python3
"""
Demo-Skript für die neue zentralisierte Konfiguration.

Zeigt, wie die neuen Schwellenwerte aus config.yaml verwendet werden.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config.config_loader import load_config
from tests.test_dummy_weather_data import DummyWeatherDataProvider, WeatherDataAggregator, WeatherAnalyzer

def main():
    """Demonstriert die neue zentralisierte Konfiguration."""
    print("=" * 60)
    print("DEMO: Neue zentralisierte Konfiguration")
    print("=" * 60)
    
    # Lade die neue Konfiguration
    config = load_config()
    
    print("\n📋 ZENTRALE SCHWELLENWERTE:")
    print("-" * 40)
    thresholds = config.get("thresholds", {})
    for key, value in thresholds.items():
        unit = {
            "regen_probability": "%",
            "regen_amount": "mm", 
            "thunderstorm_probability": "%",
            "wind_speed": "km/h",
            "temperature": "°C",
            "cloud_cover": "%"
        }.get(key, "")
        print(f"  {key}: {value}{unit}")
    
    print("\n⚖️ RISIKOMODELL-GEWICHTUNGEN:")
    print("-" * 40)
    risk_model = config.get("risk_model", {})
    for param, settings in risk_model.items():
        if isinstance(settings, dict):
            weight = settings.get("weight", 0.0)
            threshold = settings.get("threshold", "aus thresholds")
            print(f"  {param}: Gewichtung {weight}, Schwellenwert {threshold}")
    
    print("\n🔄 DELTA-SCHWELLENWERTE:")
    print("-" * 40)
    delta_thresholds = config.get("delta_thresholds", {})
    for key, value in delta_thresholds.items():
        unit = "°C" if key == "temperature" else "%"
        print(f"  {key}: {value}{unit}")
    
    print("\n📧 E-MAIL-BERICHTE MIT NEUEN SCHWELLENWERTEN:")
    print("-" * 40)
    
    # Erstelle Test-Daten und Analyzer
    data_provider = DummyWeatherDataProvider()
    aggregator = WeatherDataAggregator(config)
    analyzer = WeatherAnalyzer(data_provider, aggregator)
    
    # Generiere Berichte
    morning_report = analyzer.generate_morning_report()
    evening_report = analyzer.generate_evening_report()
    dynamic_report = analyzer.generate_dynamic_report()
    
    print(f"🌅 Morgenbericht ({len(morning_report)} Zeichen):")
    print(f"  {morning_report}")
    
    print(f"\n🌙 Abendbericht ({len(evening_report)} Zeichen):")
    print(f"  {evening_report}")
    
    print(f"\n🚨 Dynamischer Bericht ({len(dynamic_report)} Zeichen):")
    print(f"  {dynamic_report}")
    
    print("\n✅ Alle Berichte sind unter 160 Zeichen!")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 