#!/usr/bin/env python3
"""
Demo script for the new email formats according to email_format rule.

This script demonstrates the three different report formats:
1. Morning report (04:30)
2. Evening report (19:00) 
3. Dynamic update report
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from notification.email_client import generate_gr20_report_text
from datetime import datetime


def demo_morning_report():
    """Demonstrate morning report format."""
    print("🌅 MORGENBERICHT FORMAT (04:30 Uhr)")
    print("=" * 50)
    print("Format: {EtappeHeute} | Gewitter {g1}%@{t1} {g2}%@{t2} | Gewitter +1 {g1_next}% | Regen {r1}%@{t3} {r2}%@{t4} {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h")
    print()
    
    config = {}
    
    # Example 1: Normal conditions
    report_data = {
        "location": "Vizzavona",
        "report_type": "morning",
        "weather_data": {
            "max_thunderstorm_probability": 25.0,
            "thunderstorm_threshold_time": "14:00",
            "thunderstorm_threshold_pct": 20.0,
            "thunderstorm_next_day": 30.0,
            "max_precipitation_probability": 40.0,
            "rain_threshold_time": "12:00",
            "rain_threshold_pct": 30.0,
            "max_precipitation": 3.5,
            "max_temperature": 26.0,
            "max_wind_speed": 20.0
        },
        "report_time": datetime(2025, 6, 19, 4, 30)
    }
    
    text = generate_gr20_report_text(report_data, config)
    print(f"Beispiel 1 (normale Bedingungen):")
    print(f"'{text}'")
    print(f"Länge: {len(text)} Zeichen")
    print()
    
    # Example 2: High risk conditions
    report_data["weather_data"] = {
        "max_thunderstorm_probability": 75.0,
        "thunderstorm_threshold_time": "13:00",
        "thunderstorm_threshold_pct": 60.0,
        "thunderstorm_next_day": 65.0,
        "max_precipitation_probability": 85.0,
        "rain_threshold_time": "11:00",
        "rain_threshold_pct": 70.0,
        "max_precipitation": 12.5,
        "max_temperature": 32.0,
        "max_wind_speed": 45.0
    }
    
    text = generate_gr20_report_text(report_data, config)
    print(f"Beispiel 2 (hohe Risiken):")
    print(f"'{text}'")
    print(f"Länge: {len(text)} Zeichen")
    print()


def demo_evening_report():
    """Demonstrate evening report format."""
    print("🌙 ABENDBERICHT FORMAT (19:00 Uhr)")
    print("=" * 50)
    print("Format: {EtappeMorgen}→{EtappeÜbermorgen} | Nacht {min_temp}°C | Gewitter {g1}%@{t1} ({g2}%@{t2}) | Gewitter +1 {g1_next}% | Regen {r1}%@{t3} ({r2}%@{t4}) {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h")
    print()
    
    config = {}
    
    # Example 1: Two-stage transition
    report_data = {
        "location": "Haut Asco",
        "report_type": "evening",
        "weather_data": {
            "tomorrow_stage": "Haut Asco",
            "day_after_stage": "Vizzavona",
            "night_temperature": 15.0,
            "max_thunderstorm_probability": 35.0,
            "thunderstorm_threshold_time": "15:00",
            "thunderstorm_threshold_pct": 25.0,
            "thunderstorm_day_after": 45.0,
            "max_precipitation_probability": 50.0,
            "rain_threshold_time": "13:00",
            "rain_threshold_pct": 40.0,
            "max_precipitation": 6.8,
            "max_temperature": 28.0,
            "max_wind_speed": 25.0
        },
        "report_time": datetime(2025, 6, 19, 19, 0)
    }
    
    text = generate_gr20_report_text(report_data, config)
    print(f"Beispiel 1 (Etappenwechsel):")
    print(f"'{text}'")
    print(f"Länge: {len(text)} Zeichen")
    print()
    
    # Example 2: Single stage
    report_data["weather_data"]["day_after_stage"] = ""
    text = generate_gr20_report_text(report_data, config)
    print(f"Beispiel 2 (eine Etappe):")
    print(f"'{text}'")
    print(f"Länge: {len(text)} Zeichen")
    print()


def demo_dynamic_report():
    """Demonstrate dynamic update report format."""
    print("🚨 DYNAMISCHER ZWISCHENBERICHT")
    print("=" * 50)
    print("Format: {EtappeHeute} | Update: Gewitter {g2}%@{t2} | Regen {r2}%@{t4} | Hitze {temp_max}°C | Wind {wind_max}km/h")
    print()
    
    config = {}
    
    # Example 1: Thunderstorm warning
    report_data = {
        "location": "Conca",
        "report_type": "dynamic",
        "weather_data": {
            "thunderstorm_threshold_time": "16:00",
            "thunderstorm_threshold_pct": 45.0,
            "rain_threshold_time": "14:00",
            "rain_threshold_pct": 60.0,
            "max_temperature": 29.0,
            "max_wind_speed": 35.0
        },
        "report_time": datetime(2025, 6, 19, 14, 15)
    }
    
    text = generate_gr20_report_text(report_data, config)
    print(f"Beispiel 1 (Gewitterwarnung):")
    print(f"'{text}'")
    print(f"Länge: {len(text)} Zeichen")
    print()
    
    # Example 2: Only temperature/wind change
    report_data["weather_data"] = {
        "max_temperature": 31.0,
        "max_wind_speed": 40.0
    }
    
    text = generate_gr20_report_text(report_data, config)
    print(f"Beispiel 2 (nur Temperatur/Wind):")
    print(f"'{text}'")
    print(f"Länge: {len(text)} Zeichen")
    print()


def demo_character_limit():
    """Demonstrate character limit handling."""
    print("📏 ZEICHENBEGRENZUNG (160 Zeichen)")
    print("=" * 50)
    
    config = {}
    
    # Test with very long location name
    report_data = {
        "location": "ExtremelyLongLocationNameThatExceedsAllReasonableLimitsForTestingPurposes",
        "report_type": "morning",
        "weather_data": {
            "max_thunderstorm_probability": 99.0,
            "thunderstorm_threshold_time": "14:00",
            "thunderstorm_threshold_pct": 80.0,
            "max_precipitation_probability": 95.0,
            "rain_threshold_time": "12:00",
            "rain_threshold_pct": 90.0,
            "max_precipitation": 99.9,
            "max_temperature": 99.9,
            "max_wind_speed": 99.0
        },
        "report_time": datetime(2025, 6, 19, 4, 30)
    }
    
    text = generate_gr20_report_text(report_data, config)
    print(f"Langer Ortsname (wird gekürzt):")
    print(f"'{text}'")
    print(f"Länge: {len(text)} Zeichen")
    print(f"Gekürzt: {'Ja' if len(text) <= 160 else 'Nein'}")
    print()


def demo_gr20_email_formats():
    """Demonstrate GR20 email formats with vigilance warnings."""
    print("=" * 80)
    print("GR20 EMAIL FORMATS DEMO (with Vigilance Warnings)")
    print("=" * 80)
    
    # Sample weather data with vigilance warnings
    weather_data = {
        "max_thunderstorm_probability": 45.0,
        "thunderstorm_threshold_time": "14:00",
        "thunderstorm_threshold_pct": 30.0,
        "thunderstorm_next_day": 25.0,
        "thunderstorm_day_after": 40.0,
        "max_precipitation_probability": 60.0,
        "rain_threshold_time": "15:30",
        "rain_threshold_pct": 50.0,
        "max_precipitation": 12.5,
        "max_temperature": 28.5,
        "max_wind_speed": 35.0,
        "night_temperature": 15.2,
        "tomorrow_stage": "Vizzavona",
        "day_after_stage": "Corte",
        "vigilance_alerts": [
            {"phenomenon": "thunderstorm", "level": "orange"},
            {"phenomenon": "rain", "level": "yellow"}
        ]
    }
    
    config = {"max_characters": 160}
    
    # Test different report types
    report_types = [
        ("morning", "Conca"),
        ("evening", "Conca"),
        ("dynamic", "Conca")
    ]
    
    for report_type, location in report_types:
        print(f"\n📧 {report_type.upper()} REPORT:")
        print("-" * 40)
        
        report_data = {
            "location": location,
            "report_type": report_type,
            "weather_data": weather_data
        }
        
        try:
            result = generate_gr20_report_text(report_data, config)
            print(f"Result: {result}")
            print(f"Length: {len(result)} characters")
            print(f"Contains vigilance: {'ORANGE' in result or 'YELLOW' in result or 'RED' in result}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test with different vigilance scenarios
    print(f"\n🔔 VIGILANCE WARNING SCENARIOS:")
    print("-" * 40)
    
    scenarios = [
        ("No warnings", []),
        ("Yellow rain", [{"phenomenon": "rain", "level": "yellow"}]),
        ("Orange thunderstorm", [{"phenomenon": "thunderstorm", "level": "orange"}]),
        ("Red forest fire", [{"phenomenon": "forest_fire", "level": "red"}]),
        ("Multiple warnings", [
            {"phenomenon": "rain", "level": "yellow"},
            {"phenomenon": "thunderstorm", "level": "orange"},
            {"phenomenon": "heat", "level": "red"}
        ])
    ]
    
    for scenario_name, alerts in scenarios:
        print(f"\n{scenario_name}:")
        weather_data["vigilance_alerts"] = alerts
        report_data = {
            "location": "Conca",
            "report_type": "morning",
            "weather_data": weather_data
        }
        
        try:
            result = generate_gr20_report_text(report_data, config)
            print(f"  {result}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\n✅ Demo completed successfully!")


def main():
    """Main demo function."""
    print("📧 GR20 E-MAIL FORMAT DEMO")
    print("=" * 60)
    print("Demonstration der neuen E-Mail-Formate gemäß email_format Regel")
    print()
    
    demo_morning_report()
    demo_evening_report()
    demo_dynamic_report()
    demo_character_limit()
    demo_gr20_email_formats()
    
    print("✅ Demo abgeschlossen!")
    print()
    print("Hinweise:")
    print("- Alle Formate respektieren das 160-Zeichen-Limit")
    print("- Keine Links oder Emojis (für InReach-Kompatibilität)")
    print("- Fallback auf Legacy-Format für rückwärtskompatible Tests")
    print("- Automatische Kürzung bei zu langen Texten")


if __name__ == "__main__":
    main() 