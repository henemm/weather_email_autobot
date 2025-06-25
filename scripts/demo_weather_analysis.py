#!/usr/bin/env python3
"""
Demo script for weather analysis functionality.
Shows both German and English interfaces.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from datetime import datetime, timedelta
from logic.analyse_weather import (
    analyze_weather_data, 
    analyze_weather_data_english,
    analyze_multiple_sources,
    RiskType, 
    RiskLevel
)
from model.datatypes import WeatherData, WeatherPoint


def create_sample_weather_data():
    """Create sample weather data for demonstration"""
    base_time = datetime.now()
    
    # Normale Wetterbedingungen
    normal_point = WeatherPoint(
        latitude=42.5, longitude=9.0, elevation=100.0,
        time=base_time,
        temperature=22.0, feels_like=20.0,
        precipitation=0.5, thunderstorm_probability=5.0,
        wind_speed=15.0, wind_direction=180.0, cloud_cover=40.0
    )
    
    # Regen und Gewitter
    storm_point = WeatherPoint(
        latitude=42.5, longitude=9.0, elevation=100.0,
        time=base_time + timedelta(hours=3),
        temperature=18.0, feels_like=15.0,
        precipitation=8.0, thunderstorm_probability=70.0,
        wind_speed=45.0, wind_direction=180.0, cloud_cover=95.0
    )
    
    # Hitze
    heat_point = WeatherPoint(
        latitude=42.5, longitude=9.0, elevation=100.0,
        time=base_time + timedelta(hours=6),
        temperature=35.0, feels_like=38.0,
        precipitation=0.0, thunderstorm_probability=None,
        wind_speed=10.0, wind_direction=180.0, cloud_cover=20.0
    )
    
    return WeatherData(points=[normal_point, storm_point, heat_point])


def create_multiple_sources():
    """Erstellt mehrere Wetterdatenquellen für Worst-Case-Demonstration"""
    base_time = datetime(2025, 6, 15, 12, 0)
    
    # Quelle 1: Optimistische Vorhersage
    source1 = WeatherData(points=[
        WeatherPoint(
            latitude=42.5, longitude=9.0, elevation=100.0,
            time=base_time,
            temperature=20.0, feels_like=18.0,
            precipitation=2.0, thunderstorm_probability=15.0,
            wind_speed=20.0, wind_direction=180.0, cloud_cover=60.0
        )
    ])
    
    # Quelle 2: Pessimistische Vorhersage (Worst Case)
    source2 = WeatherData(points=[
        WeatherPoint(
            latitude=42.5, longitude=9.0, elevation=100.0,
            time=base_time,
            temperature=25.0, feels_like=23.0,
            precipitation=6.0, thunderstorm_probability=40.0,
            wind_speed=35.0, wind_direction=180.0, cloud_cover=85.0
        )
    ])
    
    return [source1, source2]


def main():
    """Hauptfunktion für die Demonstration"""
    print("🌤️  WETTERANALYSE-DEMONSTRATION")
    print("=" * 50)
    
    # Konfiguration mit Schwellenwerten
    config = {
        "schwellen": {
            "regen": 2.0,
            "wind": 40.0,
            "bewoelkung": 90.0,
            "hitze": 30.0,
            "gewitter_wahrscheinlichkeit": 20.0
        }
    }
    
    print("\n📊 1. Analyse einer Wetterdatenquelle:")
    print("-" * 40)
    
    weather_data = create_sample_weather_data()
    analysis = analyze_weather_data(weather_data, config)
    
    print(f"Zusammenfassung: {analysis.summary}")
    print(f"Max. Niederschlag: {analysis.max_precipitation:.1f}mm")
    print(f"Max. Wind: {analysis.max_wind_speed:.0f} km/h")
    print(f"Max. Temperatur: {analysis.max_temperature:.1f}°C")
    print(f"Max. Gewitterwahrscheinlichkeit: {analysis.max_thunderstorm_probability:.0f}%")
    
    print(f"\nErkannte Risiken ({len(analysis.risks)}):")
    for risk in analysis.risks:
        print(f"  • {risk.risk_type.value.upper()}: {risk.level.value.upper()} "
              f"({risk.value:.1f}) - {risk.description}")
    
    print("\n📊 2. Worst-Case-Analyse mit mehreren Quellen:")
    print("-" * 40)
    
    multiple_sources = create_multiple_sources()
    worst_case_analysis = analyze_multiple_sources(multiple_sources, config)
    
    print(f"Zusammenfassung: {worst_case_analysis.summary}")
    print(f"Max. Niederschlag: {worst_case_analysis.max_precipitation:.1f}mm")
    print(f"Max. Wind: {worst_case_analysis.max_wind_speed:.0f} km/h")
    print(f"Max. Temperatur: {worst_case_analysis.max_temperature:.1f}°C")
    print(f"Max. Gewitterwahrscheinlichkeit: {worst_case_analysis.max_thunderstorm_probability:.0f}%")
    
    print(f"\nErkannte Risiken ({len(worst_case_analysis.risks)}):")
    for risk in worst_case_analysis.risks:
        print(f"  • {risk.risk_type.value.upper()}: {risk.level.value.upper()} "
              f"({risk.value:.1f}) - {risk.description}")
    
    print("\n✅ Demonstration abgeschlossen!")


if __name__ == "__main__":
    main() 