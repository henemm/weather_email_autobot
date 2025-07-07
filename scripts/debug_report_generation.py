#!/usr/bin/env python3
"""
Debug script for weather report generation.

This script tests the new weather report generation that uses
the flexible aggregation logic and follows email_format.mdc specification.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.report.weather_report_generator import generate_weather_report


def test_report_generation():
    """Test weather report generation for different report types."""
    print("🌤️ Testing Weather Report Generation")
    print("=" * 60)
    
    # Test different report types
    report_types = ['morning', 'evening', 'update']
    
    for report_type in report_types:
        print(f"\n📊 Testing {report_type.upper()} Report Generation")
        print("-" * 50)
        
        try:
            # Generate report
            result = generate_weather_report(report_type=report_type)
            
            # Display results
            if result['success']:
                print(f"✅ Report generated successfully")
                print(f"📅 Report Type: {result['report_type']}")
                print(f"📍 Stage: {result['stage_info'].get('name', 'Unknown')}")
                print(f"📧 Email Subject: {result['email_subject']}")
                print(f"📝 Report Text: {result['report_text']}")
                print(f"📊 Character Count: {len(result['report_text'])}")
                
                # Check character limit
                if len(result['report_text']) > 160:
                    print(f"⚠️  WARNING: Report exceeds 160 character limit!")
                else:
                    print(f"✅ Report within character limit")
                
                # Display weather data summary
                weather_data = result['weather_data']
                print(f"\n🌡️ Weather Data Summary:")
                print(f"   Max Temperature: {weather_data.get('max_temperature', 0)}°C")
                print(f"   Min Temperature: {weather_data.get('min_temperature', 0)}°C")
                print(f"   Max Thunderstorm: {weather_data.get('max_thunderstorm_probability', 0)}%")
                print(f"   Max Rain: {weather_data.get('max_rain_probability', 0)}%")
                print(f"   Max Precipitation: {weather_data.get('max_precipitation', 0)}mm")
                print(f"   Max Wind: {weather_data.get('max_wind_speed', 0)} km/h")
                print(f"   Thunderstorm Next Day: {weather_data.get('thunderstorm_next_day', 0)}%")
                
                if weather_data.get('fire_risk_warning'):
                    print(f"   Fire Risk: {weather_data['fire_risk_warning']}")
                
            else:
                print(f"❌ Report generation failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception during {report_type} report generation: {e}")
            import traceback
            traceback.print_exc()


def test_report_formatting():
    """Test specific formatting functions."""
    print(f"\n\n🎨 Testing Report Formatting")
    print("=" * 60)
    
    # Test with sample data
    sample_weather_data = {
        'max_temperature': 28.5,
        'min_temperature': 15.2,
        'max_thunderstorm_probability': 45.0,
        'thunderstorm_threshold_pct': 30.0,
        'thunderstorm_threshold_time': '14',
        'thunderstorm_max_time': '16',
        'max_rain_probability': 60.0,
        'rain_threshold_pct': 40.0,
        'rain_threshold_time': '13',
        'rain_max_time': '15',
        'max_precipitation': 2.5,
        'rain_total_time': '15',
        'wind_speed': 12.0,
        'max_wind_speed': 25.0,
        'thunderstorm_next_day': 35.0,
        'thunderstorm_next_day_threshold_time': '14',
        'fire_risk_warning': 'HIGH Waldbrand'
    }
    
    sample_stage_info = {
        'name': 'Corte→Vizzavona',
        'stage_number': 1
    }
    
    # Test different report types
    report_types = ['morning', 'evening', 'update']
    
    for report_type in report_types:
        print(f"\n📊 {report_type.upper()} Report Format")
        print("-" * 30)
        
        try:
            # Import formatting functions
            from src.report.weather_report_generator import (
                _generate_report_text,
                _generate_email_subject
            )
            
            # Generate report text
            report_text = _generate_report_text(sample_weather_data, sample_stage_info, report_type)
            email_subject = _generate_email_subject(sample_weather_data, sample_stage_info, report_type)
            
            print(f"📧 Subject: {email_subject}")
            print(f"📝 Text: {report_text}")
            print(f"📊 Length: {len(report_text)} characters")
            
            # Validate format
            if report_type == 'morning':
                if "Gew." in report_text and "Regen" in report_text and "Hitze" in report_text:
                    print(f"✅ Morning format looks correct")
                else:
                    print(f"❌ Morning format missing required elements")
                    
            elif report_type == 'evening':
                if "Nacht" in report_text and "Gew." in report_text and "Regen" in report_text:
                    print(f"✅ Evening format looks correct")
                else:
                    print(f"❌ Evening format missing required elements")
                    
            elif report_type == 'update':
                if "Update:" in report_text and "Gew." in report_text and "Regen" in report_text:
                    print(f"✅ Update format looks correct")
                else:
                    print(f"❌ Update format missing required elements")
                    
        except Exception as e:
            print(f"❌ Error testing {report_type} format: {e}")


def test_stage_name_shortening():
    """Test stage name shortening functionality."""
    print(f"\n\n✂️ Testing Stage Name Shortening")
    print("=" * 60)
    
    from src.report.weather_report_generator import _shorten_stage_name
    
    test_names = [
        "Corte",
        "Corte→Vizzavona",
        "Vizzavona→Bocca di Verdi",
        "Very Long Stage Name That Exceeds Limit",
        "Start→End",
        "A→B→C"
    ]
    
    for name in test_names:
        shortened = _shorten_stage_name(name)
        print(f"'{name}' → '{shortened}' ({len(shortened)} chars)")
        
        if len(shortened) <= 10:
            print(f"   ✅ Within limit")
        else:
            print(f"   ❌ Exceeds limit")


if __name__ == "__main__":
    print("🚀 Starting Weather Report Generation Debug")
    print("=" * 60)
    
    # Test report generation
    test_report_generation()
    
    # Test formatting
    test_report_formatting()
    
    # Test stage name shortening
    test_stage_name_shortening()
    
    print(f"\n✅ Debug completed successfully!") 