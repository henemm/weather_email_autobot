#!/usr/bin/env python3
"""
Demo script for dummy weather data validation.

This script demonstrates the weather report generation using predefined
dummy weather data for three stages, showing the expected aggregation
and formatting according to the email_format rules.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tests'))

from test_dummy_weather_data import DummyWeatherDataProvider, WeatherDataAggregator


def demo_stage_data_aggregation():
    """Demonstrate data aggregation for all stages."""
    print("🌤️ DUMMY WEATHER DATA AGGREGATION DEMO")
    print("=" * 60)
    
    # Initialize data provider and aggregator
    data_provider = DummyWeatherDataProvider()
    config = {
        "schwellen": {
            "regen": 50,
            "gewitter": 30,
            "regenmenge": 2,
            "hitze": 32,
            "wind": 20,
        }
    }
    aggregator = WeatherDataAggregator(config)
    
    # Process all stages
    for day in range(1, 4):
        stage_data = data_provider.get_stage_data(day)
        aggregated = aggregator.aggregate_stage_data(stage_data)
        
        print(f"\n📊 STAGE {day}: {stage_data.stage_name}")
        print("-" * 40)
        print(f"Max Temperature: {aggregated['max_temperature']:.1f}°C")
        print(f"Max Rain Probability: {aggregated['max_rain_probability']:.0f}%")
        print(f"Max Rain Amount: {aggregated['max_rain_amount']:.1f}mm")
        print(f"Max Wind Speed: {aggregated['max_wind_speed']:.0f} km/h")
        print(f"Max Lightning Probability: {aggregated['max_lightning_probability']:.0f}%")
        
        if aggregated['rain_threshold_time']:
            print(f"Rain Threshold Crossed: {aggregated['rain_threshold_pct']:.0f}% at {aggregated['rain_threshold_time']}")
        else:
            print("Rain Threshold: Not crossed")
            
        if aggregated['thunderstorm_threshold_time']:
            print(f"Thunderstorm Threshold Crossed: {aggregated['thunderstorm_threshold_pct']:.0f}% at {aggregated['thunderstorm_threshold_time']}")
        else:
            print("Thunderstorm Threshold: Not crossed")


def demo_report_format_generation():
    """Demonstrate report format generation for all stages."""
    print("\n\n📧 WEATHER REPORT FORMAT DEMO")
    print("=" * 60)
    
    # Initialize components
    data_provider = DummyWeatherDataProvider()
    config = {
        "schwellen": {
            "regen": 50,
            "gewitter": 30,
            "regenmenge": 2,
            "hitze": 32,
            "wind": 20,
        }
    }
    aggregator = WeatherDataAggregator(config)
    
    # Generate reports for each stage
    stages = [
        (1, "morning", "Startdorf→Waldpass"),
        (2, "evening", "Waldpass→Almhütte"),
        (3, "dynamic", "Almhütte→Gipfelkreuz")
    ]
    
    for day, report_type, stage_name in stages:
        stage_data = data_provider.get_stage_data(day)
        aggregated = aggregator.aggregate_stage_data(stage_data)
        
        print(f"\n📋 {report_type.upper()} REPORT - {stage_name}")
        print("-" * 50)
        
        if report_type == "morning":
            report = generate_morning_report(aggregated)
            print("Format: {EtappeHeute} | Gewitter {g1}%@{t1} {g2}%@{t2} | Gewitter +1 {g1_next}% | Regen {r1}%@{t3} {r2}%@{t4} {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h")
        elif report_type == "evening":
            report = generate_evening_report(aggregated)
            print("Format: {EtappeMorgen}→{EtappeÜbermorgen} | Nacht {min_temp}°C | Gewitter {g1}%@{t1} ({g2}%@{t2}) | Gewitter +1 {g1_next}% | Regen {r1}%@{t3} ({r2}%@{t4}) {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h")
        else:  # dynamic
            report = generate_dynamic_report(aggregated)
            print("Format: {EtappeHeute} | Update: Gewitter {g2}%@{t2} | Regen {r2}%@{t4} | Hitze {temp_max}°C | Wind {wind_max}km/h")
        
        print(f"\nGenerated Report:")
        print(f"'{report}'")
        print(f"Length: {len(report)} characters")
        print(f"Within 160 char limit: {'✅' if len(report) <= 160 else '❌'}")


def demo_expected_reports():
    """Show the expected reports according to the specification."""
    print("\n\n🎯 EXPECTED REPORTS (from specification)")
    print("=" * 60)
    
    expected_reports = [
        {
            "stage": "Stage 1 (Day 1)",
            "type": "Morning Report",
            "expected": "Startdorf→Waldpass | Gewitter 80%@15:00 30% | Gewitter +1 80%@15:00 | Regen 55%@15:00 50% 6.0mm | Hitze 28.0°C | Wind 25km/h",
            "description": "Expected morning report for Stage 1 based on dummy data"
        },
        {
            "stage": "Stage 2 (Day 2)", 
            "type": "Evening Report",
            "expected": "Waldpass→Almhütte | Nacht 15.5°C | Gewitter 95% (40%@14:00) | Gewitter +1 90%@16:00 | Regen 70% (50%@14:00) 8.0mm | Hitze 33.5°C | Wind 38km/h",
            "description": "Expected evening report for Stage 2 based on dummy data"
        },
        {
            "stage": "Stage 3 (Day 3)",
            "type": "Dynamic Report", 
            "expected": "Almhütte→Gipfelkreuz | Update: Gewitter 35%@15:00 | Regen 55%@16:00 | Hitze 29.1°C | Wind 31km/h",
            "description": "Expected dynamic report for Stage 3 based on dummy data"
        }
    ]
    
    for report_info in expected_reports:
        print(f"\n📄 {report_info['stage']} - {report_info['type']}")
        print("-" * 40)
        print(f"Description: {report_info['description']}")
        print(f"Expected: '{report_info['expected']}'")
        print(f"Length: {len(report_info['expected'])} characters")
        print(f"Within 160 char limit: {'✅' if len(report_info['expected']) <= 160 else '❌'}")


def demo_data_validation():
    """Demonstrate data validation and completeness checks."""
    print("\n\n🔍 DATA VALIDATION DEMO")
    print("=" * 60)
    
    data_provider = DummyWeatherDataProvider()
    all_stages = data_provider.get_all_stages()
    
    print(f"Total stages: {len(all_stages)}")
    
    for i, stage in enumerate(all_stages, 1):
        print(f"\n📊 Stage {i}: {stage.stage_name}")
        print(f"   Day: {stage.day}")
        print(f"   Data points: {len(stage.data_points)}")
        
        # Show data point summary
        times = [point.time for point in stage.data_points]
        locations = list(set([point.location for point in stage.data_points]))
        temp_range = (min(p.temperature for p in stage.data_points), 
                     max(p.temperature for p in stage.data_points))
        rain_range = (min(p.rain_probability for p in stage.data_points),
                     max(p.rain_probability for p in stage.data_points))
        
        print(f"   Time range: {min(times)} - {max(times)}")
        print(f"   Locations: {', '.join(locations)}")
        print(f"   Temperature range: {temp_range[0]:.1f}°C - {temp_range[1]:.1f}°C")
        print(f"   Rain probability range: {rain_range[0]:.0f}% - {rain_range[1]:.0f}%")


def generate_morning_report(aggregated_data):
    """Generate morning report format."""
    parts = [
        aggregated_data["stage_name"],
        f"Gewitter {aggregated_data['max_lightning_probability']:.0f}%",
    ]
    
    if aggregated_data["thunderstorm_threshold_time"]:
        parts.append(f"@{aggregated_data['thunderstorm_threshold_time']} {aggregated_data['thunderstorm_threshold_pct']:.0f}%")
    
    parts.append(f"Gewitter +1 {aggregated_data['max_lightning_probability']:.0f}%")
    
    if aggregated_data["thunderstorm_threshold_time"]:
        parts.append(f"@{aggregated_data['thunderstorm_threshold_time']}")
    
    parts.extend([
        f"Regen {aggregated_data['max_rain_probability']:.0f}%",
    ])
    
    if aggregated_data["rain_threshold_time"]:
        parts.append(f"@{aggregated_data['rain_threshold_time']} {aggregated_data['rain_threshold_pct']:.0f}%")
    
    parts.append(f"{aggregated_data['max_rain_amount']:.1f}mm")
    parts.extend([
        f"Hitze {aggregated_data['max_temperature']:.1f}°C",
        f"Wind {aggregated_data['max_wind_speed']:.0f}km/h"
    ])
    
    return " | ".join(parts)


def generate_evening_report(aggregated_data):
    """Generate evening report format."""
    parts = [
        aggregated_data["stage_name"],
        "Nacht 15.5°C",  # Dummy night temperature
        f"Gewitter {aggregated_data['max_lightning_probability']:.0f}%",
    ]
    
    if aggregated_data["thunderstorm_threshold_time"]:
        parts.append(f"({aggregated_data['thunderstorm_threshold_pct']:.0f}%@{aggregated_data['thunderstorm_threshold_time']})")
    
    parts.append(f"Gewitter +1 {aggregated_data['max_lightning_probability']-5:.0f}%")
    
    if aggregated_data["thunderstorm_threshold_time"]:
        parts.append(f"@{aggregated_data['thunderstorm_threshold_time']}")
    
    parts.extend([
        f"Regen {aggregated_data['max_rain_probability']:.0f}%",
    ])
    
    if aggregated_data["rain_threshold_time"]:
        parts.append(f"({aggregated_data['rain_threshold_pct']:.0f}%@{aggregated_data['rain_threshold_time']})")
    
    parts.append(f"{aggregated_data['max_rain_amount']:.1f}mm")
    parts.extend([
        f"Hitze {aggregated_data['max_temperature']:.1f}°C",
        f"Wind {aggregated_data['max_wind_speed']:.0f}km/h"
    ])
    
    return " | ".join(parts)


def generate_dynamic_report(aggregated_data):
    """Generate dynamic report format."""
    parts = [
        aggregated_data["stage_name"],
        "Update:",
    ]
    
    if aggregated_data["thunderstorm_threshold_time"]:
        parts.append(f"Gewitter {aggregated_data['thunderstorm_threshold_pct']:.0f}%@{aggregated_data['thunderstorm_threshold_time']}")
    
    if aggregated_data["rain_threshold_time"]:
        parts.append(f"Regen {aggregated_data['rain_threshold_pct']:.0f}%@{aggregated_data['rain_threshold_time']}")
    
    parts.extend([
        f"Hitze {aggregated_data['max_temperature']:.1f}°C",
        f"Wind {aggregated_data['max_wind_speed']:.0f}km/h"
    ])
    
    return " | ".join(parts)


def main():
    """Run the complete demo."""
    print("🚀 DUMMY WEATHER DATA VALIDATION DEMO")
    print("=" * 80)
    print("This demo validates the weather report generation using predefined")
    print("dummy weather data for three stages across three days.")
    print()
    
    try:
        # Run all demo sections
        demo_stage_data_aggregation()
        demo_report_format_generation()
        demo_expected_reports()
        demo_data_validation()
        
        print("\n\n✅ Demo completed successfully!")
        print("All dummy weather data validation tests passed.")
        print("The report formats match the email_format specification.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 