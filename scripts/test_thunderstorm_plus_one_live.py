#!/usr/bin/env python3
"""
Live test for Thunderstorm+1 functionality.
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from weather.core.morning_evening_refactor import MorningEveningRefactor
import json

def test_thunderstorm_plus_one():
    """Test Thunderstorm+1 functionality."""
    
    print("⚡ Live Test: Thunderstorm+1 für morgen")
    print("=" * 50)
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load config
    with open("config.yaml", "r") as f:
        import yaml
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test coordinates from first stage (T2G1)
    test_coords = (42.471359, 2.029742)
    
    print(f"📍 Test-Koordinaten: {test_coords}")
    print(f"📅 Heute: {date.today()}")
    print(f"📅 Morgen: {date.today() + timedelta(days=1)}")
    print()
    
    try:
        # Test Morning Report Thunderstorm+1
        print("🌅 MORNING REPORT - Thunderstorm+1:")
        print("-" * 40)
        
        # Get weather data for today
        weather_data = refactor.fetch_weather_data("FONT-ROMEU-ODEILLO-VIA", date.today())
        
        # Process Thunderstorm+1 for Morning Report
        thunderstorm_plus_one = refactor.process_thunderstorm_plus_one_data(
            weather_data, "FONT-ROMEU-ODEILLO-VIA", date.today(), "morning"
        )
        
        print(f"Threshold: {thunderstorm_plus_one.threshold_value}")
        print(f"Threshold Time: {thunderstorm_plus_one.threshold_time}")
        print(f"Max Value: {thunderstorm_plus_one.max_value}")
        print(f"Max Time: {thunderstorm_plus_one.max_time}")
        print(f"Geo Points: {len(thunderstorm_plus_one.geo_points)}")
        
        for i, point in enumerate(thunderstorm_plus_one.geo_points):
            print(f"  G{i+1}: {point}")
        print()
        
        # Test Evening Report Thunderstorm+1
        print("🌙 EVENING REPORT - Thunderstorm+1:")
        print("-" * 40)
        
        # Process Thunderstorm+1 for Evening Report
        thunderstorm_plus_one_evening = refactor.process_thunderstorm_plus_one_data(
            weather_data, "FONT-ROMEU-ODEILLO-VIA", date.today(), "evening"
        )
        
        print(f"Threshold: {thunderstorm_plus_one_evening.threshold_value}")
        print(f"Threshold Time: {thunderstorm_plus_one_evening.threshold_time}")
        print(f"Max Value: {thunderstorm_plus_one_evening.max_value}")
        print(f"Max Time: {thunderstorm_plus_one_evening.max_time}")
        print(f"Geo Points: {len(thunderstorm_plus_one_evening.geo_points)}")
        
        for i, point in enumerate(thunderstorm_plus_one_evening.geo_points):
            print(f"  G{i+1}: {point}")
        print()
        
        # Check if we have thunderstorm data
        has_morning_thunderstorm = (thunderstorm_plus_one.max_value is not None or 
                                   thunderstorm_plus_one.threshold_value is not None)
        has_evening_thunderstorm = (thunderstorm_plus_one_evening.max_value is not None or 
                                   thunderstorm_plus_one_evening.threshold_value is not None)
        
        print("📊 ERGEBNIS:")
        print("-" * 20)
        print(f"Morning Thunderstorm+1: {'✅ Gefunden' if has_morning_thunderstorm else '❌ Keine Daten'}")
        print(f"Evening Thunderstorm+1: {'✅ Gefunden' if has_evening_thunderstorm else '❌ Keine Daten'}")
        
        if has_morning_thunderstorm:
            print("✅ Morning Thunderstorm+1 funktioniert korrekt")
        else:
            print("❌ Morning Thunderstorm+1 zeigt keine Gewitterdaten")
            
        if has_evening_thunderstorm:
            print("✅ Evening Thunderstorm+1 funktioniert korrekt")
        else:
            print("❌ Evening Thunderstorm+1 zeigt keine Gewitterdaten")
        
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_thunderstorm_plus_one() 