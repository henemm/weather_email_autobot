#!/usr/bin/env python3
"""
Live End-to-End Test für GR20 Abendbericht (Etappe 2: Carozzu)

Simuliert einen vollständigen Durchlauf des GR20-Warnsystems im Abendmodus.
"""

import sys
import os
import json
import logging
from datetime import datetime, time
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_openmeteo import fetch_openmeteo_forecast
from wetter.fetch_meteofrance import get_forecast_with_fallback
from wetter.analyse import analysiere_regen_risiko, WetterDaten
from model.datatypes import WeatherData, WeatherPoint
from notification.email_client import EmailClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_etappen_data() -> Dict:
    """Load stage data from etappen.json"""
    try:
        with open('etappen.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("etappen.json not found")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing etappen.json: {e}")
        return {}

def get_current_stage() -> Dict:
    """Get current stage based on date (for testing, use stage 2)"""
    etappen = load_etappen_data()
    if not etappen or len(etappen) < 2:
        return {}
    stage_2 = etappen[1]  # Index 1 for stage 2
    logger.info(f"Using stage 2 (Carozzu)")
    return stage_2

def fetch_weather_for_points(points: List[Dict]) -> List[WeatherData]:
    """Fetch weather data for all points of the stage"""
    weather_data_list = []
    
    for i, point in enumerate(points):
        lat = point['lat']
        lon = point['lon']
        
        logger.info(f"Fetching weather for point {i+1}/{len(points)}: {lat}, {lon}")
        
        # Fetch MeteoFrance data with fallback to OpenMeteo
        try:
            meteofrance_data = get_forecast_with_fallback(lat, lon)
            if meteofrance_data:
                # Convert MeteoFrance data to WeatherData object
                weather_point = WeatherPoint(
                    latitude=lat,
                    longitude=lon,
                    elevation=0.0,  # No elevation from MeteoFrance
                    time=datetime.now(),
                    temperature=meteofrance_data.temperature,
                    feels_like=meteofrance_data.temperature,  # Use same as temperature if not available
                    precipitation=0.0,  # Not directly available in ForecastResult
                    thunderstorm_probability=meteofrance_data.precipitation_probability,
                    wind_speed=0.0,  # Not available in ForecastResult
                    wind_direction=0.0,  # Not available in ForecastResult
                    cloud_cover=0.0  # Not available in ForecastResult
                )
                
                weather_data = WeatherData(points=[weather_point])
                weather_data_list.append(weather_data)
                logger.info(f"Successfully fetched MeteoFrance data for point {i+1}: temp={meteofrance_data.temperature}°C, source={meteofrance_data.data_source}")
            else:
                logger.warning(f"Failed to fetch MeteoFrance data for point {i+1}")
                
        except Exception as e:
            logger.error(f"Error fetching MeteoFrance data for point {i+1}: {e}")
        
        # Fetch OpenMeteo data as additional source
        try:
            openmeteo_data = fetch_openmeteo_forecast(lat, lon)
            if openmeteo_data and openmeteo_data.get('current'):
                current = openmeteo_data['current']
                logger.info(f"OpenMeteo data for point {i+1}: temp={current.get('temperature_2m')}°C, precip={current.get('precipitation')}mm")
            else:
                logger.warning(f"No OpenMeteo data available for point {i+1}")
                
        except Exception as e:
            logger.error(f"Error fetching OpenMeteo data for point {i+1}: {e}")
    
    return weather_data_list

def aggregate_weather_data(weather_data_list: List[WeatherData]) -> List[WetterDaten]:
    """Convert WeatherData list to WetterDaten list for analysis"""
    wetter_daten_list = []
    for wd in weather_data_list:
        for point in wd.points:
            wetter_daten_list.append(WetterDaten(
                datum=point.time,
                temperatur=point.temperature,
                niederschlag_prozent=0.0,  # Not available
                niederschlag_mm=point.precipitation,
                wind_geschwindigkeit=point.wind_speed,
                luftfeuchtigkeit=0.0  # Not available
            ))
    return wetter_daten_list

def generate_evening_report(stage_data: Dict, wetter_daten_list: List[WetterDaten]) -> str:
    """Generate evening weather report text using analysiere_regen_risiko"""
    # Minimal config for thresholds
    config = {"schwellen": {"regen": 25, "regenmenge": 2}}
    analyse = analysiere_regen_risiko(wetter_daten_list, config)
    stage_name = stage_data.get('name', 'Unknown Stage')
    # Short, link- and emoji-free summary
    return f"{stage_name}: {analyse.risiko_stufe.value.upper()} | {analyse.bewertung[:120]}"[:160]

def send_evening_report(report_text: str, stage_data: Dict) -> bool:
    """Send evening report via email"""
    try:
        email_client = EmailClient()
        
        stage_name = stage_data.get('name', 'Unknown Stage')
        subject = f"GR20 Wetterbericht Abend - {stage_name}"
        
        # Send email
        success = email_client.send_email(
            subject=subject,
            body=report_text,
            recipient="test@example.com"  # Replace with actual recipient
        )
        
        if success:
            logger.info(f"Evening report sent successfully: {subject}")
            return True
        else:
            logger.error("Failed to send evening report")
            return False
            
    except Exception as e:
        logger.error(f"Error sending evening report: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting GR20 Evening Mode End-to-End Test")
    
    # Get current stage data
    stage_data = get_current_stage()
    if not stage_data:
        logger.error("Failed to get stage data")
        return False
    
    stage_name = stage_data.get('name', 'Unknown')
    points = stage_data.get('punkte', [])
    
    logger.info(f"Testing evening mode for stage: {stage_name}")
    logger.info(f"Number of route points: {len(points)}")
    
    # Fetch weather data for all points
    weather_data_list = fetch_weather_for_points(points)
    
    if not weather_data_list:
        logger.error("No weather data fetched")
        return False
    
    logger.info(f"Successfully fetched weather data for {len(weather_data_list)} points")
    
    # Aggregate weather data according to evening mode rules
    wetter_daten_list = aggregate_weather_data(weather_data_list)
    
    if not wetter_daten_list:
        logger.error("Failed to aggregate weather data")
        return False
    
    # Generate evening report
    report_text = generate_evening_report(stage_data, wetter_daten_list)
    
    if not report_text:
        logger.error("Failed to generate evening report")
        return False
    
    # Check report constraints
    if len(report_text) > 160:
        logger.warning(f"Report too long ({len(report_text)} chars), should be <= 160")
    
    if 'http' in report_text.lower():
        logger.warning("Report contains links, which are not allowed")
    
    # Send report (optional for testing)
    logger.info("Evening report generated successfully")
    logger.info(f"Report text: {report_text}")
    
    # Uncomment to actually send the report
    # send_success = send_evening_report(report_text, stage_data)
    # return send_success
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("GR20 Evening Mode Test completed successfully")
        sys.exit(0)
    else:
        logger.error("GR20 Evening Mode Test failed")
        sys.exit(1) 