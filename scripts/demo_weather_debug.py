#!/usr/bin/env python3
"""
Demo script for the new weather debug output implementation.

This script demonstrates the comprehensive debug output generation
following the specification in example_weather_debug_2025-07-30.md
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from debug.weather_debug import WeatherDebugOutput, generate_weather_debug_output
from config.config_loader import load_config


def demo_weather_debug():
    """Demonstrate the new weather debug output functionality."""
    print("🌤️ Weather Debug Output Demo")
    print("=" * 50)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()
        
        # Check if debug is enabled
        debug_enabled = config.get("debug", {}).get("enabled", False)
        print(f"🔧 Debug enabled: {debug_enabled}")
        
        if not debug_enabled:
            print("⚠️  Debug is disabled in config.yaml. Enable it to see debug output.")
            print("   Set debug.enabled: true in config.yaml")
            return
        
        # Create sample report data
        report_data = {
            "report_type": "morning",
            "location": "Demo Location",
            "stage_names": ["Demo Stage 1", "Demo Stage 2"]
        }
        
        print(f"📊 Report type: {report_data['report_type']}")
        print(f"📍 Location: {report_data['location']}")
        print(f"🏔️  Stage names: {report_data['stage_names']}")
        
        # Generate debug output
        print("\n🔄 Generating debug output...")
        debug_output = generate_weather_debug_output(report_data, config)
        
        if debug_output:
            print("\n📄 DEBUG OUTPUT:")
            print("-" * 50)
            print(debug_output)
            print("-" * 50)
            
            # Check for specific content
            if "DEBUG DATENEXPORT – Rohdatenübersicht MeteoFrance" in debug_output:
                print("✅ Debug header found")
            
            if "Datenquelle: meteo_france / Substruktur: forecast" in debug_output:
                print("✅ Forecast table found")
            
            if "Datenquelle: meteo_france / Substruktur: daily_forecast" in debug_output:
                print("✅ Daily forecast table found")
            
            if "Datenquelle: meteo_france / Substruktur: probability_forecast" in debug_output:
                print("✅ Probability forecast table found")
            
            if "Datenquelle: meteo_france / Substruktur: rain" in debug_output:
                print("✅ Rain data table found")
            
            if "Datenquelle: meteo_france / Substruktur: alerts" in debug_output:
                print("✅ Alerts table found")
            
            # Check for position data
            if "Position:" in debug_output:
                print("✅ Position data found")
            
            # Check for date
            if "Datum:" in debug_output:
                print("✅ Date information found")
            
            print(f"\n📏 Debug output length: {len(debug_output)} characters")
            
        else:
            print("❌ No debug output generated")
            
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


def demo_weather_debug_class():
    """Demonstrate the WeatherDebugOutput class directly."""
    print("\n🔧 WeatherDebugOutput Class Demo")
    print("=" * 50)
    
    try:
        # Load configuration
        config = load_config()
        
        # Create debug output instance
        debug_output = WeatherDebugOutput(config)
        
        print(f"🔧 Debug enabled: {debug_output.should_generate_debug()}")
        print(f"📁 Output directory: {debug_output.output_directory}")
        print(f"📅 Start date: {debug_output.startdatum}")
        
        # Test target date calculation
        morning_date = debug_output.get_target_date("morning")
        evening_date = debug_output.get_target_date("evening")
        
        print(f"🌅 Morning target date: {morning_date}")
        print(f"🌆 Evening target date: {evening_date}")
        
        # Test stage positions
        morning_positions = debug_output.get_stage_positions("morning")
        evening_positions = debug_output.get_stage_positions("evening")
        
        print(f"📍 Morning positions: {len(morning_positions)}")
        for i, (name, lat, lon) in enumerate(morning_positions[:2]):  # Show first 2
            print(f"   {i+1}. {name}: ({lat}, {lon})")
        
        print(f"📍 Evening positions: {len(evening_positions)}")
        for i, (name, lat, lon) in enumerate(evening_positions[:2]):  # Show first 2
            print(f"   {i+1}. {name}: ({lat}, {lon})")
        
        # Test data fetching for first position
        if morning_positions:
            first_name, first_lat, first_lon = morning_positions[0]
            print(f"\n🌤️ Fetching data for {first_name} ({first_lat}, {first_lon})...")
            
            weather_data = debug_output.fetch_meteofrance_data(first_lat, first_lon)
            
            if weather_data:
                print("✅ Weather data fetched successfully")
                print(f"   Forecast entries: {len(weather_data.get('forecast', []))}")
                print(f"   Daily forecast entries: {len(weather_data.get('daily_forecast', []))}")
                print(f"   Probability forecast entries: {len(weather_data.get('probability_forecast', []))}")
                print(f"   Rain data entries: {len(weather_data.get('rain_data', []))}")
                print(f"   Alerts: {len(weather_data.get('alerts', []))}")
            else:
                print("❌ No weather data fetched")
        
    except Exception as e:
        print(f"❌ Error in class demo: {e}")
        import traceback
        traceback.print_exc()


def demo_different_report_types():
    """Demonstrate debug output for different report types."""
    print("\n📊 Different Report Types Demo")
    print("=" * 50)
    
    try:
        config = load_config()
        
        report_types = ["morning", "evening", "dynamic"]
        
        for report_type in report_types:
            print(f"\n🔍 Testing {report_type} report...")
            
            report_data = {
                "report_type": report_type,
                "location": f"Demo {report_type.title()}",
                "stage_names": [f"Stage {report_type} 1", f"Stage {report_type} 2"]
            }
            
            debug_output = generate_weather_debug_output(report_data, config)
            
            if debug_output:
                print(f"✅ {report_type} debug output generated ({len(debug_output)} chars)")
                
                # Check for specific content based on report type
                if report_type == "morning":
                    if "morning" in debug_output.lower():
                        print("   ✅ Morning-specific content found")
                
                elif report_type == "evening":
                    if "evening" in debug_output.lower():
                        print("   ✅ Evening-specific content found")
                
                elif report_type == "dynamic":
                    if "dynamic" in debug_output.lower():
                        print("   ✅ Dynamic-specific content found")
            else:
                print(f"❌ No {report_type} debug output generated")
                
    except Exception as e:
        print(f"❌ Error in report types demo: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo function."""
    print("🚀 Starting Weather Debug Output Demo")
    print("=" * 60)
    
    # Run all demos
    demo_weather_debug()
    demo_weather_debug_class()
    demo_different_report_types()
    
    print("\n✅ Demo completed!")
    print("\n📝 Notes:")
    print("   - Debug output is saved to output/debug/ directory")
    print("   - Enable debug.enabled: true in config.yaml to see output")
    print("   - Check the generated files for detailed weather data")


if __name__ == "__main__":
    main() 