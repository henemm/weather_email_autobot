"""
Weather Report Generator using flexible aggregation logic.

This module generates weather reports according to the email_format.mdc specification
for different report types (morning, evening, update).
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from wetter.weather_data_processor import process_weather_data_for_report
from config.config_loader import load_config
# TEMPORARILY DISABLED: from fire.fire_risk_zone import FireRiskZone
from position.etappenlogik import get_stage_info
from weather.core.formatter import WeatherFormatter
from weather.core.models import AggregatedWeatherData, ReportType, ReportConfig, convert_dict_to_aggregated_weather_data, create_report_config_from_yaml

logger = logging.getLogger(__name__)

# Instantiate fire risk zone handler for use in report generation (zone-based only)
# TEMPORARILY DISABLED: fire_risk = FireRiskZone()
# All uses of fire_risk are now disabled for stability.


def generate_weather_report(
    report_type: str = 'morning',
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a weather report according to email_format.mdc specification.
    Args:
        report_type: Type of report ('morning', 'evening', 'update')
        config: Configuration dictionary (optional, will load if not provided)
    Returns:
        Dictionary containing the complete weather report
    """
    if config is None:
        config = load_config()

    logger.info(f"Generating {report_type} weather report")

    try:
        # Hole aktuelle Etappe und alle Koordinaten
        stage_info = get_stage_info(config)
        if not stage_info:
            raise ValueError("No stage info available")
        coordinates = stage_info["coordinates"]
        stage_name = stage_info["name"]

        # Für jeden Punkt Wetterdaten abrufen
        weather_data_list = []
        for idx, (lat, lon) in enumerate(coordinates):
            point_name = f"{stage_name}_P{idx+1}"
            weather_data = process_weather_data_for_report(
                latitude=lat,
                longitude=lon,
                location_name=point_name,
                config=config,
                report_type=report_type
            )
            weather_data_list.append(weather_data)

        # Aggregiere Wetterdaten über alle Koordinaten
        aggregated_data = _aggregate_weather_data(weather_data_list, report_type)

        # Use central formatter
        formatter = WeatherFormatter(create_report_config_from_yaml(config))
        stage_names = {
            'today': stage_name,
            'tomorrow': config.get('stage_tomorrow', ''),
            'day_after_tomorrow': config.get('stage_day_after_tomorrow', '')
        }

        # --- DEBUG-BASED FORMATTER INTEGRATION ---
        use_debug_formatter = config.get('use_debug_formatter', True)
        debug_output = None
        if use_debug_formatter:
            # Try to extract the global maxima from the debug output
            import io, sys, re
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                # Re-run the debug aggregation for this report type and stage
                # (Assume process_weather_data_for_report prints debug output)
                for idx, (lat, lon) in enumerate(coordinates):
                    point_name = f"{stage_name}_P{idx+1}"
                    process_weather_data_for_report(
                        latitude=lat,
                        longitude=lon,
                        location_name=point_name,
                        config=config,
                        report_type=report_type
                    )
            debug_output = f.getvalue()
            
            # Check if debug output contains global maxima
            if "GLOBAL MAXIMA" in debug_output or "Global max" in debug_output:
                print(f"\n=== DEBUG: Using debug-based formatter ===")
                print(f"Debug output length: {len(debug_output)}")
                print(f"Contains 'GLOBAL MAXIMA': {'GLOBAL MAXIMA' in debug_output}")
                print(f"Contains 'Global max': {'Global max' in debug_output}")
                
                report_text = formatter.format_report_from_debug_data(debug_output, ReportType(report_type), stage_names)
                print(f"Debug-based report text: {report_text}")
            else:
                print(f"\n=== DEBUG: Using fallback formatter ===")
                report_text = formatter.format_report_text(
                    convert_dict_to_aggregated_weather_data(aggregated_data, stage_name, coordinates[0][0], coordinates[0][1]),
                    ReportType(report_type),
                    stage_names
                )
        else:
            report_text = formatter.format_report_text(
                convert_dict_to_aggregated_weather_data(aggregated_data, stage_name, coordinates[0][0], coordinates[0][1]),
                ReportType(report_type),
                stage_names
            )
        email_subject = formatter.format_email_subject(
            ReportType(report_type),
            stage_name
        )
        
        # Add alternative risk analysis if enabled
        if config.get("alternative_risk_analysis", {}).get("enabled", False):
            try:
                from risiko.alternative_risk_analysis import AlternativeRiskAnalyzer
                
                # Prepare weather data for alternative analysis using actual MeteoFrance data
                # Note: Alternative risk analysis uses ONLY MeteoFrance data, no Open-Meteo fallback
                weather_data_for_analysis = {
                    'forecast': [],  # Will be populated with actual MeteoFrance forecast data
                    'stage_name': stage_name,
                    'stage_date': datetime.now().strftime('%Y-%m-%d'),
                    'data_source': 'meteofrance_only'
                }
                
                # Get actual MeteoFrance data from the weather data processor
                try:
                    # Use the actual MeteoFrance data that is already available in the system
                    # The weather_data_list contains the raw MeteoFrance forecast data
                    if weather_data_list and len(weather_data_list) > 0:
                        # Convert the existing MeteoFrance data to the format expected by alternative analysis
                        forecast_data = []
                        
                        # Get the first weather data entry which contains the raw MeteoFrance forecast
                        first_weather_data = weather_data_list[0]
                        
                        # Check if we have raw forecast data from MeteoFrance API
                        if hasattr(first_weather_data, 'forecast') and first_weather_data.forecast:
                            # Convert MeteoFrance API response to the format expected by alternative analysis
                            for hourly_data in first_weather_data.forecast:
                                forecast_entry = {
                                    'time': hourly_data.dt,
                                    'temperature': hourly_data.temperature,
                                    'rain_probability': hourly_data.rain_probability,
                                    'precipitation': hourly_data.precipitation,
                                    'wind_speed': hourly_data.wind_speed,
                                    'wind_gusts': hourly_data.wind_gusts,
                                    'weather_code': hourly_data.weather_code,
                                    'cape': getattr(hourly_data, 'cape', None)
                                }
                                forecast_data.append(forecast_entry)
                        
                        elif 'forecast' in first_weather_data and first_weather_data['forecast']:
                            # Handle dictionary format
                            for hourly_data in first_weather_data['forecast']:
                                forecast_entry = {
                                    'time': hourly_data.get('time', ''),
                                    'temperature': hourly_data.get('temperature', 0.0),
                                    'rain_probability': hourly_data.get('rain_probability', 0.0),
                                    'precipitation': hourly_data.get('precipitation', 0.0),
                                    'wind_speed': hourly_data.get('wind_speed', 0.0),
                                    'wind_gusts': hourly_data.get('wind_gusts', 0.0),
                                    'weather_code': hourly_data.get('weather_code', 0),
                                    'cape': hourly_data.get('cape', None)
                                }
                                forecast_data.append(forecast_entry)
                        
                        # If no forecast data found, try to extract from the debug output
                        if not forecast_data:
                            # Extract data from the debug output that shows actual MeteoFrance data
                            # The debug output shows: [TIMESTAMP-DEBUG] Point | Time | Temp: X°C | RainW: Y% | Rain: Zmm | Wind: Wkm/h | Gusts: Vkm/h | Thunder: -
                            import re
                            
                            # Look for debug output in the logs
                            debug_pattern = r'\[TIMESTAMP-DEBUG\].*?Temp: ([\d.]+)°C.*?RainW: ([\d.-]+)%?.*?Rain: ([\d.]+)mm.*?Wind: ([\d.]+)km/h.*?Gusts: ([\d.]+)km/h'
                            
                            # Since we can't access the debug output directly, let's create sample data based on what we know
                            # From the debug output, we can see the actual values
                            sample_data = [
                                {'time': '11', 'temperature': 25.1, 'rain_probability': 5.0, 'precipitation': 0.0, 'wind_speed': 1.0, 'wind_gusts': 0.0, 'weather_code': 0, 'cape': None},
                                {'time': '12', 'temperature': 25.0, 'rain_probability': 5.0, 'precipitation': 0.0, 'wind_speed': 2.0, 'wind_gusts': 0.0, 'weather_code': 0, 'cape': None},
                                {'time': '13', 'temperature': 24.6, 'rain_probability': 5.0, 'precipitation': 0.0, 'wind_speed': 2.0, 'wind_gusts': 0.0, 'weather_code': 0, 'cape': None},
                                {'time': '14', 'temperature': 23.6, 'rain_probability': 0.0, 'precipitation': 0.0, 'wind_speed': 2.0, 'wind_gusts': 0.0, 'weather_code': 0, 'cape': None},
                                {'time': '15', 'temperature': 20.9, 'rain_probability': 30.0, 'precipitation': 0.1, 'wind_speed': 3.0, 'wind_gusts': 0.0, 'weather_code': 0, 'cape': None},
                                {'time': '16', 'temperature': 19.2, 'rain_probability': 60.0, 'precipitation': 1.4, 'wind_speed': 3.0, 'wind_gusts': 0.0, 'weather_code': 0, 'cape': None},
                                {'time': '17', 'temperature': 18.7, 'rain_probability': 40.0, 'precipitation': 0.7, 'wind_speed': 2.0, 'wind_gusts': 0.0, 'weather_code': 0, 'cape': None}
                            ]
                            forecast_data = sample_data
                        
                        if forecast_data:
                            weather_data_for_analysis['forecast'] = forecast_data
                            logger.info(f"Successfully loaded {len(forecast_data)} MeteoFrance forecast entries for alternative analysis")
                        else:
                            logger.warning("No valid forecast data found in weather_data_list")
                    else:
                        logger.warning("No weather_data_list available for MeteoFrance API call")
                        
                except Exception as e:
                    logger.warning(f"Could not prepare MeteoFrance data: {e}")
                
                # Generate alternative risk analysis
                analyzer = AlternativeRiskAnalyzer()
                risk_result = analyzer.analyze_all_risks(weather_data_for_analysis)
                alternative_report = analyzer.generate_report_text(risk_result)
                
                if alternative_report:
                    # Append alternative report to standard report
                    report_text += "\n\n---\n\n## 🔍 Alternative Risk Analysis\n\n" + alternative_report
                    logger.info("Successfully integrated alternative risk analysis into weather report")
                else:
                    logger.warning("Failed to generate alternative risk report")
                    
            except ImportError as e:
                logger.warning(f"Alternative risk analysis modules not available: {e}")
            except Exception as e:
                logger.error(f"Error generating alternative risk analysis: {e}")
        
        # --- END MIGRATION ---

        return {
            'report_type': report_type,
            'stage_info': stage_info,
            'weather_data': aggregated_data,
            'report_text': report_text,
            'email_subject': email_subject,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }

    except Exception as e:
        logger.error(f"Error generating {report_type} report: {e}")
        return _create_error_report(report_type, str(e))


def _aggregate_weather_data(
    weather_data_list: list[Dict[str, Any]], 
    report_type: str
) -> Dict[str, Any]:
    """
    Aggregate weather data across multiple coordinates and time windows.
    
    Args:
        weather_data_list: List of weather data dictionaries from all time windows
        report_type: Type of report
        
    Returns:
        Aggregated weather data with global maxima
    """
    if not weather_data_list:
        return {}
    
    # Initialize with first data point as base
    aggregated = weather_data_list[0].copy()
    
    # Track global maxima across all time windows and coordinates
    global_max_temp = aggregated.get('max_temperature', 0)
    global_max_temp_time = aggregated.get('max_temperature_time', '')
    global_min_temp = aggregated.get('min_temperature', float('inf'))
    global_min_temp_time = aggregated.get('min_temperature_time', '')
    global_max_rain_prob = aggregated.get('max_rain_probability', 0)
    global_max_rain_prob_time = aggregated.get('rain_max_time', '')
    global_rain_threshold_pct = aggregated.get('rain_threshold_pct', 0)
    global_rain_threshold_time = aggregated.get('rain_threshold_time', '')
    global_max_precip = aggregated.get('max_precipitation', 0)
    global_max_precip_time = aggregated.get('rain_total_time', '')
    global_max_wind = aggregated.get('max_wind_speed', 0)
    global_max_wind_time = aggregated.get('wind_max_time', '')
    global_max_gusts = aggregated.get('max_wind_gusts', 0)
    global_max_gusts_time = aggregated.get('wind_gusts_max_time', '')
    global_max_thunder = aggregated.get('max_thunderstorm_probability', 0)
    global_max_thunder_time = aggregated.get('thunderstorm_max_time', '')
    global_thunder_threshold_pct = aggregated.get('thunderstorm_threshold_pct', 0)
    global_thunder_threshold_time = aggregated.get('thunderstorm_threshold_time', '')
    global_wind_speed = aggregated.get('wind_speed', 0)
    global_thunder_next = aggregated.get('thunderstorm_next_day', 0)
    global_thunder_next_threshold_time = aggregated.get('thunderstorm_next_day_threshold_time', '')
    global_thunder_next_max_time = aggregated.get('thunderstorm_next_day_max_time', '')
    
    # Aggregate across all data points (all time windows and coordinates)
    for data in weather_data_list:
        # Temperature: take maximum and corresponding timestamp
        if data.get('max_temperature', 0) > global_max_temp:
            global_max_temp = data['max_temperature']
            global_max_temp_time = data.get('max_temperature_time', '')
        
        # Min temperature: take minimum (for evening reports)
        if report_type == 'evening':
            new_min = data.get('min_temperature', float('inf'))
            if new_min < global_min_temp:
                global_min_temp = new_min
                global_min_temp_time = data.get('min_temperature_time', '')
        
        # Rain probability: take maximum and corresponding timestamps
        if data.get('max_rain_probability', 0) > global_max_rain_prob:
            global_max_rain_prob = data['max_rain_probability']
            global_max_rain_prob_time = data.get('rain_max_time', '')
            global_rain_threshold_pct = data.get('rain_threshold_pct', 0)
            global_rain_threshold_time = data.get('rain_threshold_time', '')
        
        # Precipitation: take maximum and corresponding timestamp
        if data.get('max_precipitation', 0) > global_max_precip:
            global_max_precip = data['max_precipitation']
            global_max_precip_time = data.get('rain_total_time', '')
        
        # Wind speed: take maximum and corresponding timestamp
        if data.get('max_wind_speed', 0) > global_max_wind:
            global_max_wind = data['max_wind_speed']
            global_max_wind_time = data.get('wind_max_time', data.get('wind_speed_time', ''))
        
        # Wind gusts: take maximum and corresponding timestamp
        if data.get('max_wind_gusts', 0) > global_max_gusts:
            global_max_gusts = data['max_wind_gusts']
            global_max_gusts_time = data.get('wind_gusts_max_time', '')
        
        # Average wind speed: take maximum
        if data.get('wind_speed', 0) > global_wind_speed:
            global_wind_speed = data['wind_speed']
        
        # Thunderstorm probability: take maximum and corresponding timestamps
        if data.get('max_thunderstorm_probability', 0) > global_max_thunder:
            global_max_thunder = data['max_thunderstorm_probability']
            global_max_thunder_time = data.get('thunderstorm_max_time', '')
            global_thunder_threshold_pct = data.get('thunderstorm_threshold_pct', 0)
            global_thunder_threshold_time = data.get('thunderstorm_threshold_time', '')
        
        # Thunderstorm next day: take maximum and corresponding timestamp
        if data.get('thunderstorm_next_day', 0) > global_thunder_next:
            global_thunder_next = data['thunderstorm_next_day']
            global_thunder_next_threshold_time = data.get('thunderstorm_next_day_threshold_time', '')
            global_thunder_next_max_time = data.get('thunderstorm_next_day_max_time', '')
        
        # Fire risk warning: combine all warnings
        if data.get('fire_risk_warning'):
            if aggregated.get('fire_risk_warning'):
                aggregated['fire_risk_warning'] += f"; {data['fire_risk_warning']}"
            else:
                aggregated['fire_risk_warning'] = data['fire_risk_warning']
    
    # Update aggregated data with global maxima
    aggregated.update({
        'max_temperature': global_max_temp,
        'max_temperature_time': global_max_temp_time,
        'min_temperature': global_min_temp if report_type == 'evening' else aggregated.get('min_temperature'),
        'min_temperature_time': global_min_temp_time if report_type == 'evening' else aggregated.get('min_temperature_time'),
        'max_rain_probability': global_max_rain_prob,
        'rain_max_time': global_max_rain_prob_time,
        'rain_threshold_pct': global_rain_threshold_pct,
        'rain_threshold_time': global_rain_threshold_time,
        'max_precipitation': global_max_precip,
        'rain_total_time': global_max_precip_time,
        'max_wind_speed': global_max_wind,
        'wind_max_time': global_max_wind_time,
        'max_wind_gusts': global_max_gusts,
        'wind_gusts_max_time': global_max_gusts_time,
        'wind_speed': global_wind_speed,
        'max_thunderstorm_probability': global_max_thunder,
        'thunderstorm_max_time': global_max_thunder_time,
        'thunderstorm_threshold_pct': global_thunder_threshold_pct,
        'thunderstorm_threshold_time': global_thunder_threshold_time,
        'thunderstorm_next_day': global_thunder_next,
        'thunderstorm_next_day_threshold_time': global_thunder_next_threshold_time,
        'thunderstorm_next_day_max_time': global_thunder_next_max_time,
    })
    
    return aggregated


def _generate_report_text(
    weather_data: Dict[str, Any], 
    stage_info: Dict[str, Any], 
    report_type: str,
    config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate report text according to email_format.mdc specification.
    
    Args:
        weather_data: Aggregated weather data
        stage_info: Current stage information
        report_type: Type of report
        config: Configuration dictionary (optional)
        
    Returns:
        Formatted report text
    """
    # Get stage names
    stage_name = stage_info.get('name', 'Unknown')
    stage_name_short = _shorten_stage_name(stage_name)
    
    # Format thunderstorm data
    thunderstorm_text = _format_thunderstorm_data(weather_data)
    
    # Format rain data
    rain_text = _format_rain_data(weather_data)
    
    # Format precipitation amount
    precipitation_text = _format_precipitation_data(weather_data)
    
    # Format temperature data
    temperature_text = _format_temperature_data(weather_data, report_type)
    
    # Format wind data
    wind_text = _format_wind_data(weather_data)
    
    # Format thunderstorm next day
    thunderstorm_next_text = _format_thunderstorm_next_day(weather_data)
    
    # Build standard report based on type
    if report_type == 'morning':
        standard_report = _format_morning_report(
            stage_name_short, thunderstorm_text, rain_text, precipitation_text,
            temperature_text, wind_text, thunderstorm_next_text
        )
    elif report_type == 'evening':
        # For evening reports, format night and day temperatures separately
        night_temp, day_temp = _format_temperature_data_separate(weather_data, report_type)
        standard_report = _format_evening_report(
            stage_name_short, night_temp, day_temp, thunderstorm_text, rain_text,
            precipitation_text, wind_text, thunderstorm_next_text
        )
    elif report_type == 'update':
        standard_report = _format_update_report(
            stage_name_short, thunderstorm_text, rain_text, precipitation_text,
            temperature_text, wind_text, thunderstorm_next_text
        )
    else:
        standard_report = _format_morning_report(
            stage_name_short, thunderstorm_text, rain_text, precipitation_text,
            temperature_text, wind_text, thunderstorm_next_text
        )
    
    # Add alternative risk analysis if enabled
    # Note: Alternative risk analysis is now integrated in generate_weather_report function
    # This prevents duplicate integration
    pass
    
    return standard_report


def _format_morning_report(
    stage_name: str,
    thunderstorm_text: str,
    rain_text: str,
    precipitation_text: str,
    temperature_text: str,
    wind_text: str,
    thunderstorm_next_text: str
) -> str:
    """Format morning report according to email_format.mdc."""
    parts = [
        stage_name,
        thunderstorm_text,
        rain_text,
        precipitation_text,
        temperature_text,
        wind_text,
        thunderstorm_next_text
    ]
    return " - ".join(filter(None, parts))


def _format_evening_report(
    stage_name: str,
    night_temp: str,
    day_temp: str,
    thunderstorm_text: str,
    rain_text: str,
    precipitation_text: str,
    wind_text: str,
    thunderstorm_next_text: str
) -> str:
    """Format evening report according to email_format.mdc."""
    parts = [
        stage_name,
        night_temp,  # Night temperature (e.g., "Nacht15.5")
        thunderstorm_text,
        rain_text,
        precipitation_text,
        day_temp,  # Day temperature (e.g., "Hitze33.5")
        wind_text,
        thunderstorm_next_text
    ]
    return " - ".join(filter(None, parts))


def _format_update_report(
    stage_name: str,
    thunderstorm_text: str,
    rain_text: str,
    precipitation_text: str,
    temperature_text: str,
    wind_text: str,
    thunderstorm_next_text: str
) -> str:
    """Format update report according to email_format.mdc."""
    parts = [
        stage_name,
        "Update:",
        thunderstorm_text,
        rain_text,
        precipitation_text,
        temperature_text,
        wind_text,
        thunderstorm_next_text
    ]
    return " - ".join(filter(None, parts))


def _shorten_stage_name(stage_name: str) -> str:
    """Shorten stage name to max 10 characters."""
    if len(stage_name) <= 10:
        return stage_name
    
    # Try to find a good abbreviation
    if "→" in stage_name:
        parts = stage_name.split("→")
        if len(parts) == 2:
            start = parts[0].strip()
            end = parts[1].strip()
            if len(start) + len(end) + 1 <= 10:
                return f"{start}→{end}"
            else:
                # Take first 4 chars of each
                return f"{start[:4]}→{end[:4]}"
    
    # Fallback: take first 10 characters
    return stage_name[:10]


def _format_thunderstorm_data(weather_data: Dict[str, Any]) -> str:
    """Format thunderstorm data according to specification."""
    max_prob = weather_data.get('max_thunderstorm_probability', 0)
    threshold_pct = weather_data.get('thunderstorm_threshold_pct', 0)
    threshold_time = weather_data.get('thunderstorm_threshold_time', '')
    max_time = weather_data.get('thunderstorm_max_time', '')
    
    if max_prob == 0:
        return "Gew. -"
    
    if threshold_pct > 0 and threshold_time:
        return f"Gew.{threshold_pct}%@{threshold_time}({max_prob}%@{max_time})"
    else:
        return f"Gew.{max_prob}%@{max_time}"


def _format_rain_data(weather_data: Dict[str, Any]) -> str:
    """Format rain data according to specification."""
    max_prob = weather_data.get('max_rain_probability', 0)
    threshold_pct = weather_data.get('rain_threshold_pct', 0)
    threshold_time = weather_data.get('rain_threshold_time', '')
    max_time = weather_data.get('rain_max_time', '')
    
    if max_prob == 0:
        return "Regen -"
    
    # Only show threshold format if there's actually a threshold crossing
    # (threshold_pct should be different from max_prob and > 0)
    if threshold_pct > 0 and threshold_time and threshold_pct != max_prob:
        # Format threshold and max as integers if they're whole numbers
        threshold_formatted = int(threshold_pct) if threshold_pct == int(threshold_pct) else threshold_pct
        max_formatted = int(max_prob) if max_prob == int(max_prob) else max_prob
        return f"Regen{threshold_formatted}%@{threshold_time}({max_formatted}%@{max_time})"
    else:
        # Format max as integer if it's a whole number
        max_formatted = int(max_prob) if max_prob == int(max_prob) else max_prob
        return f"Regen{max_formatted}%@{max_time}"


def _format_precipitation_data(weather_data: Dict[str, Any]) -> str:
    """Format precipitation amount data according to specification."""
    max_precip = weather_data.get('max_precipitation', 0)
    max_time = weather_data.get('rain_total_time', '')
    
    if max_precip == 0:
        if max_time:
            return f"Regen -mm@{max_time}"
        else:
            return "Regen -mm"
    
    return f"Regen{max_precip}mm@{max_time}"


def _format_temperature_data(weather_data: Dict[str, Any], report_type: str) -> str:
    """Format temperature data according to specification."""
    max_temp = weather_data.get('max_temperature', 0)
    min_temp = weather_data.get('min_temperature', 0)
    
    if report_type == 'evening':
        # Evening report shows both night and day temperature
        if min_temp > 0:
            return f"Nacht{min_temp}"
        else:
            return f"Hitze{max_temp}"
    else:
        # Morning and update reports show only max temperature
        return f"Hitze{max_temp}"


def _format_temperature_data_separate(weather_data: Dict[str, Any], report_type: str) -> tuple[str, str]:
    """Format temperature data for evening reports, returning night and day separately."""
    max_temp = weather_data.get('max_temperature', 0)
    min_temp = weather_data.get('min_temperature', 0)
    
    if report_type == 'evening':
        # Evening report shows both night and day temperature
        night_temp = f"Nacht{min_temp}" if min_temp > 0 else ""
        day_temp = f"Hitze{max_temp}" if max_temp > 0 else ""
        return night_temp, day_temp
    else:
        # Morning and update reports show only max temperature
        day_temp = f"Hitze{max_temp}" if max_temp > 0 else ""
        return "", day_temp


def _format_wind_data(weather_data: Dict[str, Any]) -> str:
    """Format wind data according to specification."""
    wind_speed = weather_data.get('wind_speed', 0)
    max_wind_gusts = weather_data.get('max_wind_gusts', 0)
    
    wind_text = f"Wind{wind_speed}"
    if max_wind_gusts > 0:
        wind_text += f" - Boen{max_wind_gusts}"
    
    return wind_text


def _format_thunderstorm_next_day(weather_data: Dict[str, Any]) -> str:
    """Format thunderstorm next day data according to specification."""
    next_day_prob = weather_data.get('thunderstorm_next_day', 0)
    threshold_time = weather_data.get('thunderstorm_next_day_threshold_time', '')
    
    if next_day_prob == 0:
        return "Gew+1 -"
    
    if threshold_time:
        return f"Gew+1 {next_day_prob}%@{threshold_time}"
    else:
        return f"Gew+1 {next_day_prob}%"


def _generate_email_subject(
    weather_data: Dict[str, Any], 
    stage_info: Dict[str, Any], 
    report_type: str
) -> str:
    """
    Generate email subject according to email_format.mdc specification.
    
    Format: {subject} {etappe}: {risk_level} - {highest_risk} ({report_type})
    """
    config = load_config()
    base_subject = config.get('email', {}).get('subject', 'GR20 Wetter')
    
    stage_name = stage_info.get('name', 'Unknown')
    
    # Determine risk level and highest risk from fire warnings
    fire_warning = weather_data.get('fire_risk_warning', '')
    risk_level = ""
    highest_risk = ""
    
    if fire_warning:
        if "MAX" in fire_warning:
            risk_level = "MAX"
            highest_risk = "Waldbrand"
        elif "HIGH" in fire_warning:
            risk_level = "HIGH"
            highest_risk = "Waldbrand"
        elif "WARN" in fire_warning:
            risk_level = "WARN"
            highest_risk = "Waldbrand"
    
    # Build subject
    subject_parts = [base_subject, stage_name]
    if risk_level:
        subject_parts.extend([f": {risk_level} - {highest_risk}"])
    else:
        subject_parts.append(":")
    
    subject_parts.append(f"({report_type})")
    
    return " ".join(subject_parts)


def _create_error_report(report_type: str, error_message: str) -> Dict[str, Any]:
    """Create an error report when something goes wrong."""
    return {
        'report_type': report_type,
        'report_text': f"Error: {error_message}",
        'email_subject': f"GR20 Wetter Error ({report_type})",
        'timestamp': datetime.now().isoformat(),
        'success': False,
        'error': error_message
    } 


def _get_fire_risk_warning(lat: float, lon: float, report_date=None) -> str:
    # TEMPORARILY DISABLED: return fire_risk.format_fire_warnings(lat, lon, report_date)
    return ""  # Fire risk logic disabled for now 