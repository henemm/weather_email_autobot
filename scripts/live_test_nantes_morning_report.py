#!/usr/bin/env python3
"""
Live End-to-End Test: Morning Weather Report for Nantes (44000)

This script tests the complete weather report generation process for Nantes
using the new meteofrance-api architecture with fallback to open-meteo.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from config.config_loader import load_config
    from utils.logging_setup import setup_logging, get_logger
    from wetter.fetch_meteofrance import (
        get_forecast_with_fallback,
        get_thunderstorm_with_fallback,
        get_alerts_with_fallback,
        ForecastResult
    )
    from wetter.fetch_openmeteo import fetch_openmeteo_forecast, get_weather_summary
except ImportError as e:
    print(f"Import error: {e}")
    print("Current sys.path:", sys.path)
    raise


# Nantes coordinates (44000)
NANTES_LATITUDE = 47.2184
NANTES_LONGITUDE = -1.5536
NANTES_DEPARTMENT = "44"  # Loire-Atlantique


def test_meteofrance_api_live():
    """Test live meteofrance-api functionality for Nantes."""
    logger = get_logger(__name__)
    logger.info("=== Testing Météo-France API Live ===")
    
    try:
        # Test forecast
        logger.info("Fetching forecast data...")
        forecast = get_forecast_with_fallback(NANTES_LATITUDE, NANTES_LONGITUDE)
        logger.info(f"Forecast: {forecast.temperature}°C, {forecast.weather_condition}, "
                   f"Precipitation: {forecast.precipitation_probability}%, "
                   f"Source: {forecast.data_source}")
        
        # Test thunderstorm detection
        logger.info("Fetching thunderstorm data...")
        thunderstorm = get_thunderstorm_with_fallback(NANTES_LATITUDE, NANTES_LONGITUDE)
        logger.info(f"Thunderstorm: {thunderstorm}")
        
        # Test weather alerts
        logger.info("Fetching weather alerts...")
        alerts = get_alerts_with_fallback(NANTES_LATITUDE, NANTES_LONGITUDE)
        logger.info(f"Alerts: {len(alerts)} active alerts")
        for alert in alerts:
            logger.info(f"  - {alert.phenomenon}: {alert.level} level")
        
        return {
            "forecast": forecast,
            "thunderstorm": thunderstorm,
            "alerts": alerts,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Météo-France API test failed: {e}")
        return {"status": "error", "message": str(e)}


def test_openmeteo_fallback():
    """Test open-meteo fallback functionality."""
    logger = get_logger(__name__)
    logger.info("=== Testing Open-Meteo Fallback ===")
    
    try:
        # Fetch open-meteo data directly
        logger.info("Fetching Open-Meteo data...")
        openmeteo_data = fetch_openmeteo_forecast(NANTES_LATITUDE, NANTES_LONGITUDE)
        
        # Get weather summary
        summary = get_weather_summary(openmeteo_data)
        
        logger.info(f"Open-Meteo Summary:")
        logger.info(f"  Temperature: {summary.get('temperature', {}).get('current')}°C")
        logger.info(f"  Wind Speed: {summary.get('wind', {}).get('speed')} km/h")
        logger.info(f"  Precipitation: {summary.get('precipitation', {}).get('current')} mm")
        logger.info(f"  Weather Code: {summary.get('conditions', {}).get('weather_code')}")
        
        return {
            "data": openmeteo_data,
            "summary": summary,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Open-Meteo fallback test failed: {e}")
        return {"status": "error", "message": str(e)}


def analyze_daily_weather(openmeteo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze daily weather patterns from hourly data."""
    logger = get_logger(__name__)
    
    hourly_data = openmeteo_data.get("hourly", {})
    if not hourly_data:
        return {"error": "No hourly data available"}
    
    # Get today's data (next 24 hours)
    times = hourly_data.get("time", [])
    temperatures = hourly_data.get("temperature_2m", [])
    precipitation = hourly_data.get("precipitation", [])
    wind_speeds = hourly_data.get("wind_speed_10m", [])
    weather_codes = hourly_data.get("weather_code", [])
    
    # Take first 24 hours of data
    today_times = times[:24]
    today_temps = temperatures[:24]
    today_precip = precipitation[:24]
    today_wind = wind_speeds[:24]
    today_weather = weather_codes[:24]
    
    # Calculate daily extremes
    if today_temps:
        max_temp = max(today_temps)
        min_temp = min(today_temps)
        avg_temp = sum(today_temps) / len(today_temps)
    else:
        max_temp = min_temp = avg_temp = None
    
    if today_precip:
        total_precip = sum(today_precip)
        max_precip = max(today_precip)
        precip_hours = sum(1 for p in today_precip if p > 0)
    else:
        total_precip = max_precip = precip_hours = 0
    
    if today_wind:
        max_wind = max(today_wind)
        avg_wind = sum(today_wind) / len(today_wind)
    else:
        max_wind = avg_wind = None
    
    # Key time points (6h, 12h, 18h, 24h)
    key_times = {
        "06:00": {"temp": today_temps[6] if len(today_temps) > 6 else None, "weather": today_weather[6] if len(today_weather) > 6 else None},
        "12:00": {"temp": today_temps[12] if len(today_temps) > 12 else None, "weather": today_weather[12] if len(today_weather) > 12 else None},
        "18:00": {"temp": today_temps[18] if len(today_temps) > 18 else None, "weather": today_weather[18] if len(today_weather) > 18 else None},
        "24:00": {"temp": today_temps[23] if len(today_temps) > 23 else None, "weather": today_weather[23] if len(today_weather) > 23 else None}
    }
    
    # Weather trend analysis
    if len(today_temps) >= 2:
        temp_trend = "steigend" if today_temps[-1] > today_temps[0] else "fallend" if today_temps[-1] < today_temps[0] else "stabil"
    else:
        temp_trend = "unbekannt"
    
    return {
        "daily_extremes": {
            "max_temp": max_temp,
            "min_temp": min_temp,
            "avg_temp": avg_temp,
            "total_precipitation": total_precip,
            "max_precipitation": max_precip,
            "precipitation_hours": precip_hours,
            "max_wind": max_wind,
            "avg_wind": avg_wind
        },
        "key_times": key_times,
        "trends": {
            "temperature": temp_trend
        }
    }


def format_weather_condition(weather_data):
    """Format weather condition data for display."""
    if isinstance(weather_data, dict):
        if 'desc' in weather_data:
            return weather_data['desc']
        elif 'description' in weather_data:
            return weather_data['description']
        else:
            return str(weather_data)
    elif isinstance(weather_data, str):
        return weather_data
    else:
        return "Unbekannt"


def generate_morning_report(weather_data: Dict[str, Any], openmeteo_data: Dict[str, Any] = None) -> str:
    """Generate a comprehensive morning weather report for Nantes."""
    logger = get_logger(__name__)
    logger.info("=== Generating Morning Weather Report ===")
    
    forecast = weather_data.get("forecast")
    thunderstorm = weather_data.get("thunderstorm")
    alerts = weather_data.get("alerts")
    
    # Analyze daily weather if openmeteo data is available
    daily_analysis = None
    if openmeteo_data:
        daily_analysis = analyze_daily_weather(openmeteo_data)
    
    report_lines = []
    report_lines.append("🌅 MORGENBERICHT NANTES (44000)")
    report_lines.append("=" * 50)
    report_lines.append(f"📅 Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    report_lines.append(f"📍 Standort: Nantes, Loire-Atlantique (44)")
    report_lines.append("")
    
    # Current weather
    if forecast and hasattr(forecast, 'temperature'):
        report_lines.append("🌡️ AKTUELLE WETTERLAGE:")
        report_lines.append(f"   Temperatur: {forecast.temperature}°C")
        if forecast.weather_condition:
            weather_desc = format_weather_condition(forecast.weather_condition)
            report_lines.append(f"   Wetterlage: {weather_desc}")
        if forecast.precipitation_probability is not None:
            report_lines.append(f"   Regenwahrscheinlichkeit: {forecast.precipitation_probability}%")
        report_lines.append(f"   Datenquelle: {forecast.data_source}")
        report_lines.append("")
    
    # Daily forecast
    if daily_analysis and "daily_extremes" in daily_analysis:
        extremes = daily_analysis["daily_extremes"]
        report_lines.append("📊 TAGESVORHERSAGE:")
        if extremes["max_temp"] and extremes["min_temp"]:
            report_lines.append(f"   Höchsttemperatur: {extremes['max_temp']}°C")
            report_lines.append(f"   Tiefsttemperatur: {extremes['min_temp']}°C")
            report_lines.append(f"   Durchschnitt: {extremes['avg_temp']:.1f}°C")
        if extremes["total_precipitation"] is not None:
            report_lines.append(f"   Gesamtniederschlag: {extremes['total_precipitation']:.1f}mm")
            report_lines.append(f"   Regenstunden: {extremes['precipitation_hours']}")
        if extremes["max_wind"]:
            report_lines.append(f"   Max. Windgeschwindigkeit: {extremes['max_wind']:.1f} km/h")
        report_lines.append("")
        
        # Key time points
        key_times = daily_analysis.get("key_times", {})
        if key_times:
            report_lines.append("🕐 WICHTIGE ZEITPUNKTE:")
            for time, data in key_times.items():
                if data["temp"] is not None:
                    report_lines.append(f"   {time}: {data['temp']}°C")
            report_lines.append("")
    
    # Thunderstorm analysis
    if thunderstorm:
        report_lines.append("⚡ GEWITTERANALYSE:")
        report_lines.append(f"   {thunderstorm}")
        report_lines.append("")
    
    # Weather alerts
    if alerts:
        report_lines.append("⚠️ WETTERWARNUNGEN:")
        for alert in alerts:
            level_emoji = {
                "green": "🟢",
                "yellow": "🟡", 
                "orange": "🟠",
                "red": "🔴"
            }.get(alert.level, "⚪")
            report_lines.append(f"   {level_emoji} {alert.phenomenon}: {alert.level.upper()}")
        report_lines.append("")
    else:
        report_lines.append("✅ Keine aktiven Wetterwarnungen")
        report_lines.append("")
    
    # Recommendations based on comprehensive data
    report_lines.append("💡 EMPFEHLUNGEN:")
    if daily_analysis and "daily_extremes" in daily_analysis:
        extremes = daily_analysis["daily_extremes"]
        
        if extremes["max_temp"] and extremes["max_temp"] > 25:
            report_lines.append("   - Leichte Kleidung und Sonnenschutz mitnehmen")
        elif extremes["min_temp"] and extremes["min_temp"] < 10:
            report_lines.append("   - Warme Kleidung anziehen")
        
        if extremes["total_precipitation"] and extremes["total_precipitation"] > 5:
            report_lines.append("   - Regenschutz mitnehmen")
        
        if extremes["max_wind"] and extremes["max_wind"] > 30:
            report_lines.append("   - Windschutz beachten")
    
    if "thunderstorm" in thunderstorm.lower() and "no" not in thunderstorm.lower():
        report_lines.append("   - Gewitter möglich, Indoor-Aktivitäten bevorzugen")
    
    report_lines.append("   - Wetterlage regelmäßig überprüfen")
    report_lines.append("")
    
    report_lines.append("🔗 LINKS:")
    report_lines.append("   - Météo-France: https://www.meteofrance.com")
    report_lines.append("   - Vigilance: https://vigilance.meteofrance.com")
    report_lines.append("")
    
    report_lines.append("📱 Bericht generiert von GR20 Weather Autobot")
    report_lines.append("=" * 50)
    
    return "\n".join(report_lines)


def save_report_to_file(report: str, filename: str = None) -> str:
    """Save the weather report to a file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nantes_morning_report_{timestamp}.txt"
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filepath


def main():
    """Main function for the live end-to-end test."""
    # Setup logging
    setup_logging(log_level="INFO", console_output=True)
    logger = get_logger(__name__)
    
    logger.info("🚀 Starting Live End-to-End Test: Nantes Morning Report")
    logger.info(f"📍 Location: Nantes ({NANTES_LATITUDE}, {NANTES_LONGITUDE})")
    logger.info(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    try:
        # Load configuration
        logger.info("📋 Loading configuration...")
        config = load_config()
        logger.info("✅ Configuration loaded successfully")
        logger.info("")
        
        # Test Météo-France API
        meteofrance_result = test_meteofrance_api_live()
        logger.info("")
        
        # Test Open-Meteo fallback
        openmeteo_result = test_openmeteo_fallback()
        logger.info("")
        
        # Generate weather report
        if meteofrance_result["status"] == "success":
            weather_data = meteofrance_result
        else:
            logger.warning("⚠️ Using Open-Meteo data due to Météo-France API failure")
            weather_data = {
                "forecast": None,
                "thunderstorm": "No thunderstorm data available (open-meteo fallback)",
                "alerts": [],
                "openmeteo_data": openmeteo_result
            }
        
        # Generate and save report with daily analysis
        openmeteo_data = openmeteo_result.get("data") if openmeteo_result["status"] == "success" else None
        report = generate_morning_report(weather_data, openmeteo_data)
        filepath = save_report_to_file(report)
        
        logger.info("📄 Weather Report Generated:")
        logger.info("=" * 60)
        print(report)
        logger.info("=" * 60)
        logger.info(f"💾 Report saved to: {filepath}")
        
        # Summary
        logger.info("")
        logger.info("📊 TEST SUMMARY:")
        logger.info(f"   Météo-France API: {'✅ SUCCESS' if meteofrance_result['status'] == 'success' else '❌ FAILED'}")
        logger.info(f"   Open-Meteo Fallback: {'✅ SUCCESS' if openmeteo_result['status'] == 'success' else '❌ FAILED'}")
        logger.info(f"   Daily Analysis: {'✅ SUCCESS' if openmeteo_data else '❌ FAILED'}")
        logger.info(f"   Report Generation: ✅ SUCCESS")
        logger.info(f"   Report File: {filepath}")
        
        logger.info("")
        logger.info("🎉 Live End-to-End Test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 