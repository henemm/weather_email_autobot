#!/usr/bin/env python3
"""
Demonstration script for risk model integration in English weather analysis.

This script shows how the compute_risk function is integrated into
the English weather analysis process.
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from logic.analyse_weather import analyze_weather_data_english, compute_risk
from model.datatypes import WeatherData, WeatherPoint


def create_sample_weather_data():
    """Create sample weather data with various risk conditions."""
    base_time = datetime.now()
    
    # Create weather points with different risk levels
    points = [
        # High risk conditions
        WeatherPoint(
            latitude=42.5,
            longitude=9.0,
            elevation=100.0,
            time=base_time,
            temperature=35.0,  # Heat wave
            feels_like=38.0,
            precipitation=8.0,  # Heavy rain
            thunderstorm_probability=75.0,  # High thunderstorm probability
            wind_speed=65.0,  # High wind
            wind_direction=180.0,
            cloud_cover=95.0,  # Overcast
            cape=2000.0,  # High CAPE
            shear=25.0  # High shear
        )
    ]
    
    return WeatherData(points=points)


def create_risk_model_config():
    """Create a comprehensive risk model configuration."""
    return {
        "schwellen": {
            "regen": 2.0,
            "wind": 40.0,
            "bewoelkung": 90.0,
            "hitze": 30.0,
            "gewitter_wahrscheinlichkeit": 20.0
        },
        "risk_model": {
            "thunderstorm_probability": {
                "threshold": 25.0,
                "weight": 0.3
            },
            "wind_speed": {
                "threshold": 40.0,
                "weight": 0.2
            },
            "precipitation": {
                "threshold": 2.0,
                "weight": 0.2
            },
            "temperature": {
                "threshold": 25.0,
                "weight": 0.1
            },
            "cape": {
                "threshold": 1000.0,
                "weight": 0.2
            }
        }
    }


def demonstrate_english_risk_model_integration():
    """Demonstrate the risk model integration in English analysis."""
    print("🌤️  English Weather Analysis with Risk Model Integration Demo")
    print("=" * 65)
    
    # Create sample data and config
    weather_data = create_sample_weather_data()
    config = create_risk_model_config()
    
    print(f"📊 Analyzing {len(weather_data.points)} weather points...")
    print()
    
    # Perform analysis using English version
    result = analyze_weather_data_english(weather_data, config)
    
    # Display results
    print("📈 Analysis Results:")
    print(f"   Risk Score: {result.risk:.3f} (0.0 = no risk, 1.0 = maximum risk)")
    print(f"   Summary: {result.summary}")
    print()
    
    print("🌡️  Maximum Values:")
    print(f"   Temperature: {result.max_temperature:.1f}°C")
    print(f"   Precipitation: {result.max_precipitation:.1f}mm")
    print(f"   Wind Speed: {result.max_wind_speed:.0f} km/h")
    print(f"   Cloud Cover: {result.max_cloud_cover:.0f}%")
    if result.max_thunderstorm_probability:
        print(f"   Thunderstorm Probability: {result.max_thunderstorm_probability:.0f}%")
    print()
    
    print("⚠️  Detected Risks (English):")
    if result.risks:
        for i, risk in enumerate(result.risks, 1):
            print(f"   {i}. {risk.risk_type.value.upper()}: {risk.level.value.upper()}")
            print(f"      Value: {risk.value:.1f} (threshold: {risk.threshold:.1f})")
            print(f"      Time: {risk.time.strftime('%H:%M')}")
            print(f"      Description: {risk.description}")
            print()
    else:
        print("   No specific risks detected")
    print()
    
    print("🎯 English Integration Complete!")
    print("   The risk model is integrated into both German and English analysis.")
    print("   Risk scores are computed consistently across both interfaces.")


if __name__ == "__main__":
    demonstrate_english_risk_model_integration() 