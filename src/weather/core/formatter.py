"""
Central formatting logic for weather reports.

This module provides unified formatting functions for all weather report types
according to the email_format.mdc specification.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .models import AggregatedWeatherData, ReportType, VigilanceData, VigilanceLevel, ReportConfig

logger = logging.getLogger(__name__)


class WeatherFormatter:
    """Central formatter for weather reports according to email_format.mdc specification."""
    
    def __init__(self, config: ReportConfig):
        self.config = config
    
    def format_report_text(self, weather_data: AggregatedWeatherData, report_type: ReportType, 
                          stage_names: Dict[str, str], vigilance_data: Optional[VigilanceData] = None) -> str:
        """
        Format weather data into report text according to email_format.mdc specification.
        
        Args:
            weather_data: Aggregated weather data
            report_type: Type of report (morning, evening, update)
            stage_names: Dictionary with stage names (e.g., {'today': 'SanPetru', 'tomorrow': 'Vizzavona'})
            vigilance_data: Optional vigilance warning data
            
        Returns:
            Formatted report text (max 160 characters)
        """
        try:
            if report_type == ReportType.MORNING:
                return self._format_morning_report(weather_data, stage_names)
            elif report_type == ReportType.EVENING:
                return self._format_evening_report(weather_data, stage_names)
            elif report_type == ReportType.UPDATE:
                return self._format_update_report(weather_data, stage_names)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
        except Exception as e:
            logger.error(f"Error formatting report text: {e}")
            return f"Error: {str(e)}"
    
    def _format_morning_report(self, weather_data: AggregatedWeatherData, stage_names: Dict[str, str]) -> str:
        """Format morning report according to specification."""
        etappe_heute = self._shorten_stage_name(stage_names.get('today', 'Unknown'))
        
        # Format each component
        thunderstorm = self._format_thunderstorm_field(
            weather_data.thunderstorm_threshold_pct,
            weather_data.thunderstorm_threshold_time,
            weather_data.max_thunderstorm_probability,
            weather_data.thunderstorm_max_time
        )
        
        rain = self._format_rain_field(
            weather_data.rain_threshold_pct,
            weather_data.rain_threshold_time,
            weather_data.max_rain_probability,
            weather_data.rain_max_time
        )
        
        precipitation = self._format_precipitation_field(
            weather_data.max_precipitation,
            weather_data.precipitation_max_time
        )
        
        temperature = self._format_temperature_field(weather_data.max_temperature)
        wind = self._format_wind_field(weather_data.max_wind_speed)
        wind_gusts = self._format_wind_gust_field(weather_data.max_wind_gusts)
        
        thunderstorm_next = self._format_thunderstorm_next_field(
            weather_data.tomorrow_max_thunderstorm_probability,
            weather_data.tomorrow_thunderstorm_threshold_time
        )
        
        # Fire risk warning
        fire_risk = self._format_fire_risk_warning(weather_data.fire_risk_warning)
        
        # Assemble report
        report_parts = [
            etappe_heute,
            thunderstorm,
            rain,
            precipitation,
            temperature,
            wind,
            wind_gusts,
            thunderstorm_next,
            fire_risk
        ]
        
        report_text = " - ".join(filter(None, report_parts))
        
        # Validate character limit
        if len(report_text) > self.config.max_report_length:
            logger.warning(f"Morning report exceeds character limit: {len(report_text)} > {self.config.max_report_length}")
            # Truncate if necessary (should not happen with proper formatting)
            report_text = report_text[:self.config.max_report_length]
        
        return report_text
    
    def _format_evening_report(self, weather_data: AggregatedWeatherData, stage_names: Dict[str, str]) -> str:
        """Format evening report according to specification."""
        etappe_morgen = self._shorten_stage_name(stage_names.get('tomorrow', 'Unknown'))
        
        # Night temperature (from min_temperature)
        night_temp = self._format_night_temperature_field(weather_data.min_temperature)
        
        # Format each component (same as morning but for tomorrow's data)
        thunderstorm = self._format_thunderstorm_field(
            weather_data.thunderstorm_threshold_pct,
            weather_data.thunderstorm_threshold_time,
            weather_data.max_thunderstorm_probability,
            weather_data.thunderstorm_max_time
        )
        
        rain = self._format_rain_field(
            weather_data.rain_threshold_pct,
            weather_data.rain_threshold_time,
            weather_data.max_rain_probability,
            weather_data.rain_max_time
        )
        
        precipitation = self._format_precipitation_field(
            weather_data.max_precipitation,
            weather_data.precipitation_max_time
        )
        
        temperature = self._format_temperature_field(weather_data.max_temperature)
        wind = self._format_wind_field(weather_data.max_wind_speed)
        wind_gusts = self._format_wind_gust_field(weather_data.max_wind_gusts)
        
        # Thunderstorm +1 refers to day after tomorrow for evening reports
        thunderstorm_next = self._format_thunderstorm_next_field(
            weather_data.day_after_tomorrow_max_thunderstorm_probability,
            weather_data.day_after_tomorrow_thunderstorm_threshold_time
        )
        
        # Fire risk warning
        fire_risk = self._format_fire_risk_warning(weather_data.fire_risk_warning)
        
        # Assemble report
        report_parts = [
            etappe_morgen,
            night_temp,
            thunderstorm,
            rain,
            precipitation,
            temperature,
            wind,
            wind_gusts,
            thunderstorm_next,
            fire_risk
        ]
        
        report_text = " - ".join(filter(None, report_parts))
        
        # Validate character limit
        if len(report_text) > self.config.max_report_length:
            logger.warning(f"Evening report exceeds character limit: {len(report_text)} > {self.config.max_report_length}")
            report_text = report_text[:self.config.max_report_length]
        
        return report_text
    
    def _format_update_report(self, weather_data: AggregatedWeatherData, stage_names: Dict[str, str]) -> str:
        """Format update report according to specification."""
        etappe_heute = self._shorten_stage_name(stage_names.get('today', 'Unknown'))
        
        # Format each component (same as morning but with "Update:" prefix)
        thunderstorm = self._format_thunderstorm_field(
            weather_data.thunderstorm_threshold_pct,
            weather_data.thunderstorm_threshold_time,
            weather_data.max_thunderstorm_probability,
            weather_data.thunderstorm_max_time
        )
        
        rain = self._format_rain_field(
            weather_data.rain_threshold_pct,
            weather_data.rain_threshold_time,
            weather_data.max_rain_probability,
            weather_data.rain_max_time
        )
        
        precipitation = self._format_precipitation_field(
            weather_data.max_precipitation,
            weather_data.precipitation_max_time
        )
        
        temperature = self._format_temperature_field(weather_data.max_temperature)
        wind = self._format_wind_field(weather_data.max_wind_speed)
        wind_gusts = self._format_wind_gust_field(weather_data.max_wind_gusts)
        
        thunderstorm_next = self._format_thunderstorm_next_field(
            weather_data.tomorrow_max_thunderstorm_probability,
            weather_data.tomorrow_thunderstorm_threshold_time
        )
        
        # Fire risk warning
        fire_risk = self._format_fire_risk_warning(weather_data.fire_risk_warning)
        
        # Assemble report with "Update:" prefix
        report_parts = [
            etappe_heute,
            "Update:",
            thunderstorm,
            rain,
            precipitation,
            temperature,
            wind,
            wind_gusts,
            thunderstorm_next,
            fire_risk
        ]
        
        report_text = " - ".join(filter(None, report_parts))
        
        # Validate character limit
        if len(report_text) > self.config.max_report_length:
            logger.warning(f"Update report exceeds character limit: {len(report_text)} > {self.config.max_report_length}")
            report_text = report_text[:self.config.max_report_length]
        
        return report_text
    
    def _format_thunderstorm_field(self, threshold_pct: Optional[float], threshold_time: Optional[str],
                                  max_pct: Optional[float], max_time: Optional[str]) -> str:
        """Format thunderstorm field according to specification."""
        # Check if we have any thunderstorm data
        has_threshold = threshold_pct and threshold_pct > 0 and threshold_time
        has_max = max_pct and max_pct > 0 and max_time
        t_time = self._format_time_hour(threshold_time)
        m_time = self._format_time_hour(max_time)
        if has_threshold and has_max:
            return f"Gew.{threshold_pct:.0f}%@{t_time}({max_pct:.0f}%@{m_time})"
        elif has_threshold:
            return f"Gew.{threshold_pct:.0f}%@{t_time}"
        elif has_max:
            return f"Gew.{max_pct:.0f}%@{m_time}"
        else:
            return "Gew. -"
    
    def _format_rain_field(self, threshold_pct: Optional[float], threshold_time: Optional[str], 
                          max_pct: Optional[float], max_time: Optional[str]) -> str:
        """
        Format rain probability field according to specification.
        
        Args:
            threshold_pct: Rain probability threshold percentage
            threshold_time: Time when threshold is reached
            max_pct: Maximum rain probability percentage
            max_time: Time when maximum is reached
            
        Returns:
            Formatted rain field string
        """
        # Get rain probability threshold from config
        rain_threshold = self.config.rain_probability_threshold
        
        # Handle None values
        threshold_pct = threshold_pct or 0.0
        max_pct = max_pct or 0.0
        
        # Only show rain probability if it exceeds the threshold
        if threshold_pct < rain_threshold and max_pct < rain_threshold:
            return "Regen -"
        
        # Format threshold crossing
        if threshold_pct >= rain_threshold and threshold_time:
            threshold_part = f"Regen{threshold_pct:.0f}%@{threshold_time}"
        else:
            threshold_part = "Regen -"
        
        # Format maximum
        if max_pct >= rain_threshold and max_time:
            max_part = f"({max_pct:.0f}%@{max_time})"
        else:
            max_part = ""
        
        # Combine parts
        if max_part:
            return f"{threshold_part}{max_part}"
        else:
            return threshold_part
    
    def _format_precipitation_field(self, precipitation_mm: Optional[float], max_time: Optional[str]) -> str:
        """Format precipitation field according to specification."""
        m_time = self._format_time_hour(max_time)
        if precipitation_mm and precipitation_mm > 0 and max_time:
            return f"Regen{precipitation_mm:.1f}mm@{m_time}"
        else:
            return "Regen -mm"
    
    def _format_temperature_field(self, temperature: Optional[float]) -> str:
        """Format temperature field according to specification."""
        if temperature is not None and temperature > 0:
            return f"Hitze{temperature:.0f}"
        else:
            return "Hitze -"
    
    def _format_wind_field(self, wind_speed: Optional[float]) -> str:
        """Format wind field according to specification."""
        if wind_speed is not None and wind_speed > 0:
            return f"Wind{wind_speed:.0f}"
        else:
            return "Wind -"
    
    def _format_wind_gust_field(self, wind_gusts: Optional[float]) -> str:
        """Format wind gust field according to specification."""
        if wind_gusts is not None and wind_gusts > 0:
            return f"Boen{wind_gusts:.0f}"
        else:
            return "Boen -"
    
    def _format_night_temperature_field(self, min_temperature: Optional[float]) -> str:
        """Format night temperature field for evening reports."""
        if min_temperature is not None:
            return f"Nacht{min_temperature:.0f}"
        else:
            return "Nacht -"
    
    def _format_thunderstorm_next_field(self, probability: Optional[float], threshold_time: Optional[str]) -> str:
        """Format thunderstorm next day field according to specification."""
        t_time = self._format_time_hour(threshold_time)
        if probability and probability > 0:
            thunder_next_part = f"Gew+1 {probability:.0f}%"
            if threshold_time:
                thunder_next_part += f"@{t_time}"
            return thunder_next_part
        else:
            return "Gew+1 -"
    
    def _format_fire_risk_warning(self, warning: Optional[str]) -> str:
        """Format fire risk warning field."""
        if warning and warning.strip():
            # The warning is already formatted as "WARN Waldbrand", "HIGH Waldbrand", etc.
            # Just return it as is
            return warning.strip()
        else:
            return ""
    
    def _shorten_stage_name(self, stage_name: str) -> str:
        """Shorten stage name to maximum 10 characters."""
        if len(stage_name) <= 10:
            return stage_name
        else:
            # Try to create a meaningful abbreviation
            words = stage_name.split()
            if len(words) == 1:
                return stage_name[:10]
            elif len(words) >= 2:
                # Take first letter of each word
                abbreviation = "".join(word[0] for word in words)
                if len(abbreviation) <= 10:
                    return abbreviation
                else:
                    return abbreviation[:10]
            else:
                return stage_name[:10]
    
    def _format_time_hour(self, time_str: Optional[str]) -> str:
        """Format a time string to hours only (HH)."""
        if not time_str:
            return "-"
        # Accepts '14:00', '14', '14:30', etc.
        if ":" in time_str:
            return time_str.split(":")[0]
        return time_str

    def format_email_subject(self, report_type: ReportType, stage_name: str, 
                           vigilance_data: Optional[VigilanceData] = None) -> str:
        """
        Format email subject according to specification.
        
        Format: {subject} {etappe}: {risk_level} - {highest_risk} ({report_type})
        """
        subject_parts = [self.config.subject_base, f"{stage_name}:"]
        
        # Add vigilance warning if present
        if vigilance_data and vigilance_data.level != VigilanceLevel.NONE:
            level_text = self._format_vigilance_level(vigilance_data.level)
            phenomenon_text = self._translate_phenomenon(vigilance_data.phenomenon)
            subject_parts.append(f"{level_text} - {phenomenon_text}")
        else:
            subject_parts.append("")
        
        # Add report type
        subject_parts.append(f"({report_type.value})")
        
        # Remove empty fields and join with space, but no space before colon
        subject = " ".join([p for p in subject_parts if p.strip()])
        return subject
    
    def _format_vigilance_level(self, level: VigilanceLevel) -> str:
        """Format vigilance level for email subject."""
        level_mapping = {
            VigilanceLevel.YELLOW: "WARN",
            VigilanceLevel.ORANGE: "HIGH",
            VigilanceLevel.RED: "MAX"
        }
        return level_mapping.get(level, "WARN")
    
    def _translate_phenomenon(self, phenomenon: str) -> str:
        """Translate phenomenon to German for email subject."""
        translation_table = {
            'thunderstorm': 'Gewitter',
            'rain': 'Regen',
            'wind': 'Wind',
            'snow': 'Schnee',
            'flood': 'Hochwasser',
            'forest_fire': 'Waldbrand',
            'heat': 'Hitze',
            'cold': 'Kälte',
            'avalanche': 'Lawine',
            'unknown': 'Warnung'
        }
        return translation_table.get(phenomenon, phenomenon) 

    def format_report_from_raw_data(self, raw_weather_data: Dict[str, Any], report_type: ReportType, 
                                   stage_names: Dict[str, str]) -> str:
        """
        Format report directly from raw weather data, performing aggregation internally.
        
        This method bypasses the problematic aggregation logic in weather_report_generator
        and performs aggregation and formatting in one step.
        
        Args:
            raw_weather_data: Raw weather data dictionary with all time windows
            report_type: Type of report to generate
            stage_names: Dictionary with stage names for today, tomorrow, day_after_tomorrow
            
        Returns:
            Formatted report text
        """
        # Extract the aggregated data that was already calculated correctly
        weather_data = raw_weather_data.get('weather_data', {})
        
        # Create AggregatedWeatherData object with the correct values
        agg_data = AggregatedWeatherData(
            location_name=stage_names.get('today', 'Unknown'),
            latitude=0.0,  # Not used for formatting
            longitude=0.0,  # Not used for formatting
            max_temperature=weather_data.get('max_temperature'),
            min_temperature=weather_data.get('min_temperature'),
            max_temperature_time=weather_data.get('max_temperature_time'),
            min_temperature_time=weather_data.get('min_temperature_time'),
            max_rain_probability=weather_data.get('max_rain_probability'),
            max_precipitation=weather_data.get('max_precipitation'),
            rain_threshold_pct=weather_data.get('rain_threshold_pct'),
            rain_threshold_time=weather_data.get('rain_threshold_time'),
            rain_max_time=weather_data.get('rain_max_time'),
            precipitation_max_time=weather_data.get('rain_total_time'),
            max_wind_speed=weather_data.get('max_wind_speed'),
            max_wind_gusts=weather_data.get('max_wind_gusts'),
            wind_threshold_kmh=weather_data.get('wind_threshold_kmh'),
            wind_threshold_time=weather_data.get('wind_threshold_time'),
            wind_max_time=weather_data.get('wind_max_time'),
            wind_gusts_max_time=weather_data.get('wind_gusts_max_time'),
            max_thunderstorm_probability=weather_data.get('max_thunderstorm_probability'),
            thunderstorm_threshold_pct=weather_data.get('thunderstorm_threshold_pct'),
            thunderstorm_threshold_time=weather_data.get('thunderstorm_threshold_time'),
            thunderstorm_max_time=weather_data.get('thunderstorm_max_time'),
            tomorrow_max_thunderstorm_probability=weather_data.get('thunderstorm_next_day'),
            tomorrow_thunderstorm_threshold_time=weather_data.get('thunderstorm_next_day_threshold_time'),
            tomorrow_thunderstorm_max_time=weather_data.get('thunderstorm_next_day_max_time'),
            day_after_tomorrow_max_thunderstorm_probability=weather_data.get('thunderstorm_next_day'),
            day_after_tomorrow_thunderstorm_threshold_time=weather_data.get('thunderstorm_next_day_threshold_time'),
            day_after_tomorrow_thunderstorm_max_time=weather_data.get('thunderstorm_next_day_max_time'),
            fire_risk_warning=weather_data.get('fire_risk_warning')
        )
        
        # Use the existing formatting logic
        return self.format_report_text(agg_data, report_type, stage_names) 

    def format_report_from_debug_data(self, debug_output: str, report_type: ReportType, 
                                     stage_names: Dict[str, str]) -> str:
        """
        Format a weather report from debug output data.
        
        Args:
            debug_output: Raw debug output string containing global maxima
            stage_names: Dictionary mapping 'today', 'tomorrow', 'day_after_tomorrow' to stage names
            
        Returns:
            Formatted weather report string
        """
        print(f"\n=== DEBUG: format_report_from_debug_data called ===")
        print(f"debug_output length: {len(debug_output)}")
        print(f"stage_names: {stage_names}")
        
        # Extract global maxima from debug output
        global_maxima = self._extract_global_maxima_from_debug(debug_output)
        
        print(f"\n=== DEBUG: After _extract_global_maxima_from_debug ===")
        print(f"global_maxima: {global_maxima}")
        print(f"global_maxima type: {type(global_maxima)}")
        print(f"global_maxima keys: {list(global_maxima.keys()) if global_maxima else 'None'}")
        
        # Determine location name
        location_name = stage_names.get('tomorrow', 'Unknown')
        if not location_name or location_name == 'Unknown':
            location_name = stage_names.get('today', 'Unknown')

        # Debug: Print what we're getting from global_maxima
        print(f"\n=== DEBUG: global_maxima values ===")
        print(f"global_maxima.get('rain_max_time', ''): '{global_maxima.get('rain_max_time', '')}'")
        print(f"global_maxima.get('precipitation_time', ''): '{global_maxima.get('precipitation_time', '')}'")
        print(f"global_maxima.get('rain_probability', 0.0): {global_maxima.get('rain_probability', 0.0)}")
        print(f"global_maxima.get('precipitation', 0.0): {global_maxima.get('precipitation', 0.0)}")
        print(f"==========================================\n")

        # Create a minimal AggregatedWeatherData object with the extracted values
        weather_data = AggregatedWeatherData(
            location_name=location_name,
            latitude=0.0,
            longitude=0.0,
            max_temperature=global_maxima.get('temperature', 0.0),
            max_temperature_time=global_maxima.get('temperature_time', ''),
            min_temperature=global_maxima.get('min_temperature', 0.0),
            min_temperature_time=global_maxima.get('min_temperature_time', ''),
            max_rain_probability=global_maxima.get('rain_probability', 0.0),
            rain_max_time=global_maxima.get('rain_max_time', ''),
            rain_threshold_pct=global_maxima.get('rain_probability', 0.0),
            rain_threshold_time=global_maxima.get('rain_max_time', ''),
            max_precipitation=global_maxima.get('precipitation', 0.0),
            precipitation_max_time=global_maxima.get('precipitation_time', ''),
            max_wind_speed=global_maxima.get('wind_speed', 0.0),
            wind_max_time=global_maxima.get('wind_speed_time', ''),
            max_wind_gusts=global_maxima.get('wind_gusts', 0.0),
            wind_gusts_max_time=global_maxima.get('wind_gusts_time', ''),
            max_thunderstorm_probability=global_maxima.get('thunderstorm', 0.0),
            thunderstorm_threshold_pct=global_maxima.get('thunderstorm', 0.0),
            thunderstorm_threshold_time=global_maxima.get('thunderstorm_threshold_time', ''),
            thunderstorm_max_time=global_maxima.get('thunderstorm_max_time', ''),
            tomorrow_max_thunderstorm_probability=global_maxima.get('thunderstorm_next_day', 0.0),
            tomorrow_thunderstorm_threshold_time=global_maxima.get('thunderstorm_next_day_threshold_time', ''),
            tomorrow_thunderstorm_max_time=global_maxima.get('thunderstorm_next_day_max_time', ''),
            day_after_tomorrow_max_thunderstorm_probability=global_maxima.get('thunderstorm_next_day', 0.0),
            day_after_tomorrow_thunderstorm_threshold_time=global_maxima.get('thunderstorm_next_day_threshold_time', ''),
            day_after_tomorrow_thunderstorm_max_time=global_maxima.get('thunderstorm_next_day_max_time', '')
        )
        
        # Debug: Print the actual values being passed to the formatter
        print(f"\n=== DEBUG: AggregatedWeatherData values ===")
        print(f"max_rain_probability: {weather_data.max_rain_probability}")
        print(f"rain_max_time: '{weather_data.rain_max_time}' (type: {type(weather_data.rain_max_time)})")
        print(f"rain_threshold_pct: {weather_data.rain_threshold_pct}")
        print(f"rain_threshold_time: '{weather_data.rain_threshold_time}' (type: {type(weather_data.rain_threshold_time)})")
        print(f"max_precipitation: {weather_data.max_precipitation}")
        print(f"precipitation_max_time: '{weather_data.precipitation_max_time}' (type: {type(weather_data.precipitation_max_time)})")
        print(f"==========================================\n")
        
        return self.format_report_text(weather_data, report_type, stage_names)
    
    def _extract_global_maxima_from_debug(self, debug_output: str) -> Dict[str, Any]:
        """
        Extract global maxima from debug output string.
        
        Args:
            debug_output: Raw debug output string
            
        Returns:
            Dictionary with extracted global maxima
        """
        import re
        
        result = {}
        
        # Extract temperature (Global max temp: 22.2°C@15 (SanPetru Point 3 (42.02803, 9.19436)))
        temp_match = re.search(r'Global max temp: ([\\d.]+)°C@(\\d+)', debug_output)
        if temp_match:
            result['temperature'] = float(temp_match.group(1))
            result['temperature_time'] = temp_match.group(2)
        
        # Extract min temperature (Global min temp: 10.6°C@05 (SanPetru Point 2 (42.03632, 9.16949)))
        min_temp_match = re.search(r'Global min temp: ([\\d.]+)°C@(\\d+)', debug_output)
        if min_temp_match:
            result['min_temperature'] = float(min_temp_match.group(1))
            result['min_temperature_time'] = min_temp_match.group(2)
        
        # Extract rain probability (Global max rain prob: 30.0%@05 (SanPetru Point 1 (42.07731, 9.15013)))
        rain_prob_match = re.search(r'Global max rain prob: ([\\d.]+)%@(\\d+)', debug_output)
        if rain_prob_match:
            result['rain_probability'] = float(rain_prob_match.group(1))
            result['rain_max_time'] = rain_prob_match.group(2)
        
        # Extract precipitation (Global max precip: 0.1mm@05 (SanPetru Point 1 (42.07731, 9.15013)))
        precip_match = re.search(r'Global max precip: ([\\d.]+)mm@(\\d+)', debug_output)
        if precip_match:
            result['precipitation'] = float(precip_match.group(1))
            result['precipitation_time'] = precip_match.group(2)
        
        # Extract wind speed (Global max wind: 13km/h@05 (SanPetru Point 2 (42.03632, 9.16949)))
        wind_match = re.search(r'Global max wind: ([\\d.]+)km/h@(\\d+)', debug_output)
        if wind_match:
            result['wind_speed'] = float(wind_match.group(1))
            result['wind_speed_time'] = wind_match.group(2)
        
        # Extract wind gusts (Global max gusts: 34km/h@05 (SanPetru Point 2 (42.03632, 9.16949)))
        gusts_match = re.search(r'Global max gusts: ([\\d.]+)km/h@(\\d+)', debug_output)
        if gusts_match:
            result['wind_gusts'] = float(gusts_match.group(1))
            result['wind_gusts_time'] = gusts_match.group(2)
        
        print(f"[DEBUG] Extracted global maxima: {result}")
        return result
    
    def _format_empty_report(self, report_type: ReportType, stage_names: Dict[str, str]) -> str:
        """
        Format an empty report when no data is available.
        
        Args:
            report_type: Type of report
            stage_names: Dictionary of stage names
            
        Returns:
            Formatted empty report text
        """
        stage_name = stage_names.get('today', 'Unknown')
        stage_name_short = self._shorten_stage_name(stage_name)
        
        if report_type == ReportType.EVENING:
            tomorrow_stage = stage_names.get('tomorrow', '')
            day_after_tomorrow_stage = stage_names.get('day_after_tomorrow', '')
            tomorrow_short = self._shorten_stage_name(tomorrow_stage)
            day_after_short = self._shorten_stage_name(day_after_tomorrow_stage)
            return f"{tomorrow_short}→{day_after_short} - Nacht - - Gew. - - Regen - - Regen -mm - Hitze - - Wind - - Boen - - Gew+1 -"
        elif report_type == ReportType.UPDATE:
            return f"{stage_name_short} - Update: - Gew. - - Regen - - Regen -mm - Hitze - - Wind - - Boen - - Gew+1 -"
        else:  # MORNING
            return f"{stage_name_short} - Gew. - - Regen - - Regen -mm - Hitze - - Wind - - Boen - - Gew+1 -" 