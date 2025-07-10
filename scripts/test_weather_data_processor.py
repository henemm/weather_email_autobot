#!/usr/bin/env python3
"""
Test script for the new weather data processor.

This script tests the weather data processor to ensure it correctly
converts Météo-France raw data into the format expected by the report generator.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.config_loader import load_config
from wetter.weather_data_processor import process_weather_data_for_report


def test_weather_data_processor():
    """Test the weather data processor with Asco coordinates."""
    
    print("🧪 TESTING WEATHER DATA PROCESSOR")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Asco coordinates (from etappen.json)
    latitude = 42.426238
    longitude = 8.900291
    location_name = "Asco"
    
    print(f"Testing location: {location_name}")
    print(f"Coordinates: {latitude}, {longitude}")
    print()
    
    try:
        # Process weather data
        processed_data = process_weather_data_for_report(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            config=config,
            hours_ahead=24
        )
        
        print("✅ Weather data processed successfully!")
        print()
        
        # Display key results
        print("📊 PROCESSED WEATHER DATA:")
        print("-" * 30)
        
        # Thunderstorm data
        thunderstorm_pct = processed_data.get('thunderstorm_threshold_pct', 0)
        thunderstorm_time = processed_data.get('thunderstorm_threshold_time', '')
        thunderstorm_max = processed_data.get('max_thunderstorm_probability', 0)
        thunderstorm_max_time = processed_data.get('thunderstorm_max_time', '')
        
        print(f"⚡ Thunderstorm threshold: {thunderstorm_pct}% @ {thunderstorm_time}")
        print(f"⚡ Thunderstorm max: {thunderstorm_max}% @ {thunderstorm_max_time}")
        
        # Rain data
        rain_pct = processed_data.get('rain_threshold_pct', 0)
        rain_time = processed_data.get('rain_threshold_time', '')
        rain_max = processed_data.get('max_rain_probability', 0)
        rain_max_time = processed_data.get('rain_max_time', '')
        
        print(f"🌧️ Rain threshold: {rain_pct}% @ {rain_time}")
        print(f"🌧️ Rain max: {rain_max}% @ {rain_max_time}")
        
        # Precipitation amount
        precip_amount = processed_data.get('max_precipitation', 0)
        precip_time = processed_data.get('rain_total_time', '')
        
        print(f"💧 Precipitation amount: {precip_amount}mm @ {precip_time}")
        
        # Temperature
        temp_max = processed_data.get('max_temperature', 0)
        temp_time = processed_data.get('temperature_time', '')
        
        print(f"🌡️ Temperature max: {temp_max}°C @ {temp_time}")
        
        # Wind
        wind_speed = processed_data.get('wind_speed', 0)
        wind_max = processed_data.get('max_wind_speed', 0)
        
        print(f"💨 Wind speed: {wind_speed}km/h")
        print(f"💨 Wind gusts: {wind_max}km/h")
        
        print()
        
        # Check if this matches the expected report format
        print("🔍 REPORT FORMAT CHECK:")
        print("-" * 30)
        
        # Expected report format: Gew.{g_threshold}%@{t_g_threshold}({g_pmax}%@{t_g_pmax})
        if thunderstorm_pct > 0:
            thunderstorm_part = f"Gew.{thunderstorm_pct}%@{thunderstorm_time}"
            if thunderstorm_max > thunderstorm_pct:
                thunderstorm_part += f"({thunderstorm_max}%@{thunderstorm_max_time})"
        else:
            thunderstorm_part = "Gew. -"
        
        print(f"Thunderstorm part: {thunderstorm_part}")
        
        # Expected report format: Regen{r_threshold}%@{t_r_threshold}({r_pmax}%@{t_r_pmax})
        if rain_pct > 0:
            rain_part = f"Regen{rain_pct}%@{rain_time}"
            if rain_max > rain_pct:
                rain_part += f"({rain_max}%@{rain_max_time})"
        else:
            rain_part = "Regen -"
        
        print(f"Rain part: {rain_part}")
        
        # Expected report format: Regen{regen_mm}mm@{t_regen_max}
        if precip_amount > 0:
            precip_part = f"Regen{precip_amount}mm@{precip_time}"
        else:
            precip_part = "Regen -mm"
        
        print(f"Precipitation part: {precip_part}")
        
        print()
        
        # Compare with actual report output
        print("📋 COMPARISON WITH ACTUAL REPORT:")
        print("-" * 30)
        print("Actual report shows: Ascu | Gew. - | Regen5%@ | Regen0.2mm@14 | Hitze25.0°C | Wind - | Windböen9km/h | Gew+1 -")
        print()
        
        # Check discrepancies
        issues = []
        
        if thunderstorm_pct == 0 and "Gew. -" in thunderstorm_part:
            print("✅ Thunderstorm: Correctly shows 'Gew. -' (no thunderstorm)")
        else:
            issues.append(f"Thunderstorm discrepancy: Expected 'Gew. -', got {thunderstorm_part}")
        
        if rain_pct == 0 and "Regen -" in rain_part:
            print("✅ Rain probability: Correctly shows 'Regen -' (no rain)")
        else:
            issues.append(f"Rain probability discrepancy: Expected 'Regen -', got {rain_part}")
        
        if precip_amount == 0 and "Regen -mm" in precip_part:
            print("✅ Precipitation amount: Correctly shows 'Regen -mm' (no precipitation)")
        else:
            issues.append(f"Precipitation amount discrepancy: Expected 'Regen -mm', got {precip_part}")
        
        if issues:
            print("❌ ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ All values match expected report format!")
        
        # Save detailed data for inspection
        output_file = f"output/debug/weather_processor_test_{location_name.lower()}.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed data saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error testing weather data processor: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_weather_data_processor() 