#!/usr/bin/env python3
"""
Comprehensive debug script to show all raw weather data for all stage points
and all hours (5-17) in a human-readable format.
This helps verify the data that goes into the weather report.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from position.etappenlogik import get_current_stage
from wetter.debug_raw_data import get_raw_data_for_multiple_locations
from wetter.fetch_meteofrance import get_forecast
from config.config_loader import load_config


def debug_complete_etappe_data():
    """Debug all weather data for all stage points and hours."""
    
    print("🌤️ COMPLETE ETAPPE WEATHER DATA DEBUG")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    start_date = config['startdatum']
    
    print(f"Start Date: {start_date}")
    print(f"Current Date: {datetime.now().strftime('%Y-%m-%d')}")
    print()
    
    # Get stage points for today
    try:
        stage_points = get_current_stage(config)
        if not stage_points:
            print("❌ No stage found for today")
            return
        print(f"Stage: {stage_points['name']}")
        print(f"Points: {len(stage_points['punkte'])}")
        print()
    except Exception as e:
        print(f"❌ Error getting stage points: {e}")
        return
    
    # Get raw weather data for all points
    locations = [(p['lat'], p['lon'], f"Geo {i+1}") for i, p in enumerate(stage_points['punkte'])]
    
    print("📊 FETCHING RAW WEATHER DATA")
    print("-" * 40)
    
    try:
        debug_data_list = get_raw_data_for_multiple_locations(locations, hours_ahead=24)
        print(f"✅ Fetched data for {len(debug_data_list)} locations")
        print()
    except Exception as e:
        print(f"❌ Error fetching weather data: {e}")
        return
    
    # Create comprehensive data overview
    print("📋 COMPLETE DATA OVERVIEW (5-17 Uhr)")
    print("=" * 60)
    
    # Collect all data points for analysis
    all_data_points = []
    
    for debug_data in debug_data_list:
        location_name = debug_data.etappe
        print(f"\n📍 LOCATION: {location_name}")
        print("-" * 40)
        
        # Filter data for hours 5-17
        filtered_points = [
            p for p in debug_data.time_points 
            if 5 <= p.timestamp.hour <= 17
        ]
        
        if not filtered_points:
            print("❌ No data for hours 5-17")
            continue
        
        # Group by hour for better readability
        for hour in range(5, 18):
            hour_points = [p for p in filtered_points if p.timestamp.hour == hour]
            
            if not hour_points:
                continue
                
            print(f"\n🕐 {hour:02d}:00")
            
            for point in hour_points:
                # Format data
                thunderstorm = f"{point.thunderstorm_probability}%" if point.thunderstorm_probability is not None else "N/A"
                precip_prob = f"{point.precipitation_probability}%" if point.precipitation_probability is not None else "N/A"
                precip_amount = f"{point.precipitation_amount}mm" if point.precipitation_amount is not None else "N/A"
                temp = f"{point.temperature}°C" if point.temperature is not None else "N/A"
                wind = f"{point.wind_speed}km/h" if point.wind_speed is not None else "N/A"
                wind_gusts = f"{point.wind_gusts}km/h" if point.wind_gusts is not None else "N/A"
                weather = point.weather_condition or "N/A"
                
                print(f"   {location_name}: "
                      f"Blitz {thunderstorm}, "
                      f"RegenW {precip_prob}, "
                      f"RegenM {precip_amount}, "
                      f"Temp {temp}, "
                      f"Wind {wind}, "
                      f"Böen {wind_gusts}, "
                      f"Wetter {weather}")
                
                # Store for analysis
                all_data_points.append({
                    'location': location_name,
                    'hour': hour,
                    'timestamp': point.timestamp,
                    'thunderstorm_probability': point.thunderstorm_probability,
                    'precipitation_probability': point.precipitation_probability,
                    'precipitation_amount': point.precipitation_amount,
                    'temperature': point.temperature,
                    'wind_speed': point.wind_speed,
                    'wind_gusts': point.wind_gusts,
                    'weather_condition': point.weather_condition
                })
    
    # Analysis section
    print("\n" + "=" * 60)
    print("🔍 DATA ANALYSIS")
    print("=" * 60)
    
    if not all_data_points:
        print("❌ No data points found for analysis")
        return
    
    # Find maximum values (like the report does)
    max_values = {
        'thunderstorm_probability': None,
        'precipitation_probability': None,
        'precipitation_amount': None,
        'temperature': None,
        'wind_speed': None,
        'wind_gusts': None
    }
    
    max_value_details = {}
    
    for data_point in all_data_points:
        for field in max_values.keys():
            value = data_point[field]
            if value is not None:
                if max_values[field] is None or value > max_values[field]:
                    max_values[field] = value
                    max_value_details[field] = {
                        'location': data_point['location'],
                        'hour': data_point['hour'],
                        'value': value
                    }
    
    print("\n📈 MAXIMUM VALUES FOUND (Report Logic):")
    print("-" * 40)
    
    for field, max_value in max_values.items():
        if max_value is not None:
            details = max_value_details[field]
            if field == 'thunderstorm_probability':
                print(f"⚡ Gewitter: {max_value}% @ {details['hour']:02d}:00 ({details['location']})")
            elif field == 'precipitation_probability':
                print(f"🌧️ Regenwahrscheinlichkeit: {max_value}% @ {details['hour']:02d}:00 ({details['location']})")
            elif field == 'precipitation_amount':
                print(f"💧 Regenmenge: {max_value}mm @ {details['hour']:02d}:00 ({details['location']})")
            elif field == 'temperature':
                print(f"🌡️ Temperatur: {max_value}°C @ {details['hour']:02d}:00 ({details['location']})")
            elif field == 'wind_speed':
                print(f"💨 Wind: {max_value}km/h @ {details['hour']:02d}:00 ({details['location']})")
            elif field == 'wind_gusts':
                print(f"💨 Windböen: {max_value}km/h @ {details['hour']:02d}:00 ({details['location']})")
        else:
            print(f"❌ {field}: Keine Daten verfügbar")
    
    # Check for specific values mentioned in the report
    print("\n🔍 SEARCHING FOR REPORT VALUES:")
    print("-" * 40)
    
    # Look for values that might match the report
    report_values_to_find = [
        ('precipitation_probability', 5),  # Regen 5%
        ('precipitation_amount', 0.2),     # Regen 0.2mm
    ]
    
    for field, target_value in report_values_to_find:
        found_matches = []
        for data_point in all_data_points:
            if data_point[field] == target_value:
                found_matches.append({
                    'location': data_point['location'],
                    'hour': data_point['hour'],
                    'value': data_point[field]
                })
        
        if found_matches:
            print(f"✅ {field} = {target_value} gefunden:")
            for match in found_matches:
                print(f"   - {match['location']} @ {match['hour']:02d}:00")
        else:
            print(f"❌ {field} = {target_value} NICHT gefunden in Rohdaten")
    
    # Save detailed data to file
    output_file = f"output/debug/complete_etappe_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'stage': stage_points['name'],
            'start_date': start_date,
            'all_data_points': all_data_points,
            'max_values': max_values,
            'max_value_details': max_value_details
        }, f, indent=2, default=str)
    
    print(f"\n💾 Detailed data saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"Total data points analyzed: {len(all_data_points)}")
    print(f"Locations: {len(debug_data_list)}")
    print(f"Time range: 5:00 - 17:00")
    print(f"Data source: meteofrance-api")
    
    # Check if we found the report values
    found_precip_prob = any(p['precipitation_probability'] == 5 for p in all_data_points)
    found_precip_amount = any(p['precipitation_amount'] == 0.2 for p in all_data_points)
    
    print(f"\nReport value check:")
    print(f"  Regenwahrscheinlichkeit 5%: {'✅ Gefunden' if found_precip_prob else '❌ Nicht gefunden'}")
    print(f"  Regenmenge 0.2mm: {'✅ Gefunden' if found_precip_amount else '❌ Nicht gefunden'}")


if __name__ == "__main__":
    debug_complete_etappe_data() 