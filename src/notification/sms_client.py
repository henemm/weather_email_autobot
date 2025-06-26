"""
SMS client for sending GR20 weather reports via seven.io.

This module provides functionality to send weather reports via SMS
using the seven.io HTTP REST API with proper formatting and character limits.
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SMSClient:
    """
    SMS client for sending GR20 weather reports via seven.io.
    
    This class handles SMS configuration and sending with proper
    formatting for mobile devices using the seven.io API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SMS client.
        
        Args:
            config: Configuration dictionary with SMS settings
            
        Raises:
            ValueError: If SMS configuration is missing or invalid
        """
        if not config or "sms" not in config:
            raise ValueError("SMS configuration is required")
        
        sms_config = config["sms"]
        required_fields = ["api_key", "test_number", "production_number", "mode", "sender"]
        
        for field in required_fields:
            if field not in sms_config:
                raise ValueError(f"SMS configuration missing required field: {field}")
        
        # Validate mode
        mode = sms_config["mode"]
        if mode not in ["test", "production"]:
            raise ValueError("SMS mode must be 'test' or 'production'")
        
        self.enabled = sms_config.get("enabled", True)
        self.provider = sms_config.get("provider", "seven")
        self.api_key = sms_config["api_key"]
        self.mode = mode
        self.sender_name = sms_config["sender"]
        self.config = config  # Store full config for report generation
        
        # Set recipient number based on mode
        if mode == "test":
            self.recipient_number = sms_config["test_number"]
        else:
            self.recipient_number = sms_config["production_number"]
    
    def send_sms(self, message_text: str) -> bool:
        """
        Send an SMS with the given message.
        
        Args:
            message_text: The message text to send (max 160 characters)
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("SMS sending disabled")
            return False
        
        if not message_text or not message_text.strip():
            logger.warning("Empty message text provided")
            return False
        
        # Ensure message doesn't exceed 160 characters
        message_text = message_text.strip()
        if len(message_text) > 160:
            message_text = message_text[:160]
        
        logger.info(f"Sending SMS to {self.recipient_number}: {message_text[:50]}...")
        
        try:
            # Prepare the API request
            url = "https://gateway.seven.io/api/sms"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "to": self.recipient_number,
                "from": self.sender_name,
                "text": message_text
            }
            
            logger.debug(f"SMS API request: URL={url}, to={self.recipient_number}, from={self.sender_name}")
            
            # Send the SMS
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            logger.info(f"SMS API response: {response.status_code}")
            
            # Check if the request was successful
            if response.status_code == 200:
                logger.info("SMS sent successfully")
                return True
            else:
                logger.error(f"Failed to send SMS: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    def send_gr20_report(self, report_data: Dict[str, Any]) -> bool:
        """
        Send a GR20 weather report SMS.
        
        Args:
            report_data: Dictionary containing report information:
                - location: Current location name
                - report_type: "morning", "evening", or "dynamic"
                - weather_data: Detailed weather data for formatting
                - report_time: Datetime of the report
                
        Returns:
            True if SMS sent successfully, False otherwise
        """
        logger.info("SMS send_gr20_report called")
        
        if not self.enabled:
            logger.info("SMS sending disabled")
            return False
        
        # Generate report text using the same format as email
        message_text = self._generate_gr20_report_text(report_data)
        logger.info(f"Generated SMS text: {message_text}")
        
        # Send SMS
        return self.send_sms(message_text)
    
    def _generate_gr20_report_text(self, report_data: Dict[str, Any]) -> str:
        """
        Generate GR20 weather report text for SMS.
        
        Args:
            report_data: Dictionary containing report information:
                - location: Current location name
                - report_type: "morning", "evening", or "dynamic"
                - weather_data: Detailed weather data for formatting
                - report_time: Datetime of the report
                
        Returns:
            Formatted report text (max 160 characters, no links)
        """
        report_type = report_data.get("report_type", "morning")
        
        if report_type == "morning":
            return self._generate_morning_report(report_data)
        elif report_type == "evening":
            return self._generate_evening_report(report_data)
        elif report_type == "dynamic":
            return self._generate_dynamic_report(report_data)
        else:
            # Fallback to simple format
            return self._generate_simple_report(report_data)
    
    def _generate_morning_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate morning report format for SMS.
        
        Format: {EtappeHeute} | Gewitter {g1}%@{t1} {g2}%@{t2} | Regen {r1}%@{t3} {r2}%@{t4} {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h | Gewitter +1 {g1_next}% | {vigilance_warning}
        """
        location = report_data.get("location", "Unknown")
        weather_data = report_data.get("weather_data", {})
        
        # Extract weather values with defaults
        thunderstorm_max = weather_data.get("max_thunderstorm_probability", 0)
        thunderstorm_threshold_time = weather_data.get("thunderstorm_threshold_time", "")
        thunderstorm_threshold_pct = weather_data.get("thunderstorm_threshold_pct", 0)
        thunderstorm_next_day = weather_data.get("thunderstorm_next_day", 0)
        
        rain_total = weather_data.get("max_precipitation", 0)
        rain_max = weather_data.get("rain_probability", 0)  # Use rain_probability if available
        rain_threshold_time = weather_data.get("rain_threshold_time", "")
        rain_threshold_pct = weather_data.get("rain_threshold_pct", 0)
        
        temp_max = weather_data.get("max_temperature", 0)
        wind_max = weather_data.get("max_wind_speed", 0)
        
        # Extract vigilance warning
        vigilance_warning = self._format_vigilance_warning(weather_data.get("vigilance_alerts", []))
        
        # Format components
        stage_part = location.replace(" ", "")
        
        thunder_part = f"Gewitter {thunderstorm_max:.0f}%"
        if thunderstorm_threshold_time and thunderstorm_threshold_pct > 0:
            thunder_part += f"({thunderstorm_threshold_pct:.0f}%@{thunderstorm_threshold_time})"
        
        thunder_next_part = f"Gewitter +1 {thunderstorm_next_day:.0f}%"
        
        rain_part = f"Regen {rain_max:.0f}%"
        if rain_threshold_time and rain_threshold_pct > 0:
            rain_part += f"@{rain_threshold_time} {rain_threshold_pct:.0f}%"
        rain_part += f" {rain_total:.1f}mm"
        
        temp_part = f"Hitze {temp_max:.1f}°C"
        
        # Use real wind gusts data if available
        wind_gusts = weather_data.get("max_wind_gusts")
        if wind_gusts and wind_gusts > wind_max:
            wind_part = f"Wind {wind_max:.0f} (max {wind_gusts:.0f})"
        else:
            wind_part = f"Wind {wind_max:.0f}km/h"
        
        # Combine all parts
        parts = [stage_part, thunder_part, rain_part, temp_part, wind_part, thunder_next_part]
        if vigilance_warning:
            parts.append(vigilance_warning)
        
        report_text = " | ".join(parts)
        
        # Ensure character limit
        if len(report_text) > 160:
            # Truncate while keeping essential information
            essential_parts = [stage_part, thunder_part, rain_part, temp_part, wind_part]
            report_text = " | ".join(essential_parts)
            if len(report_text) > 160:
                # Further truncate if still too long
                report_text = report_text[:160]
        
        return report_text
    
    def _generate_evening_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate evening report format for SMS.
        
        Format: {EtappeMorgen} | Nacht {min_temp}°C | Gewitter {g1}%@{t1} ({g2}%@{t2}) | Gewitter +1 {g1_next}% | Regen {r1}%@{t3} ({r2}%@{t4}) {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h | {vigilance_warning}
        """
        # Use tomorrow's location for evening reports, fallback to current location
        location = report_data.get("tomorrow_location", report_data.get("location", "Unknown"))
        weather_data = report_data.get("weather_data", {})
        
        # Extract weather values with defaults
        min_temp = weather_data.get("min_temperature", 0)
        
        # Use tomorrow's weather data for the main forecast
        thunderstorm_max = weather_data.get("tomorrow_thunderstorm_probability", weather_data.get("max_thunderstorm_probability", 0))
        thunderstorm_threshold_time = weather_data.get("tomorrow_thunderstorm_threshold_time", weather_data.get("thunderstorm_threshold_time", ""))
        thunderstorm_max_time = weather_data.get("tomorrow_thunderstorm_max_time", weather_data.get("thunderstorm_max_time", ""))
        
        # Use day after tomorrow's thunderstorm data for "Gewitter +1"
        thunderstorm_next_day = weather_data.get("day_after_tomorrow_thunderstorm_probability", 0)
        
        # Use tomorrow's weather data for other values
        rain_total = weather_data.get("tomorrow_precipitation", weather_data.get("max_precipitation", 0))
        rain_threshold_time = weather_data.get("tomorrow_rain_threshold_time", weather_data.get("rain_threshold_time", ""))
        rain_max_time = weather_data.get("tomorrow_rain_max_time", weather_data.get("rain_max_time", ""))
        
        temp_max = weather_data.get("tomorrow_temperature", weather_data.get("max_temperature", 0))
        wind_max = weather_data.get("tomorrow_wind_speed", weather_data.get("max_wind_speed", 0))
        
        # Debug logging
        logger.info(f"Evening report weather data: min_temp={min_temp}, temp_max={temp_max}, thunderstorm_max={thunderstorm_max}, rain_total={rain_total}, thunderstorm_next_day={thunderstorm_next_day}")
        
        # Extract vigilance warning
        vigilance_warning = self._format_vigilance_warning(weather_data.get("vigilance_alerts", []))
        
        # Format components
        stage_part = location.replace(" ", "")
        
        night_part = f"Nacht {min_temp:.1f}°C"
        
        thunder_part = f"Gew. {thunderstorm_max:.0f}%"
        if thunderstorm_threshold_time:
            if thunderstorm_max_time and thunderstorm_threshold_time != thunderstorm_max_time:
                # Different times: show threshold time and maximum time
                thunder_part = f"Gew. {thunderstorm_max:.0f}%@{thunderstorm_threshold_time} (max {thunderstorm_max:.0f}%@{thunderstorm_max_time})"
            else:
                # Same time: show only one time
                thunder_part = f"Gew. {thunderstorm_max:.0f}%@{thunderstorm_threshold_time}"
        
        thunder_next_part = f"Gew. +1 {thunderstorm_next_day:.0f}%"
        
        rain_part = f"Regen {rain_total:.1f}mm"
        if rain_threshold_time:
            if rain_max_time and rain_threshold_time != rain_max_time:
                # Different times: show threshold time and maximum time
                rain_part = f"Regen {rain_total:.1f}mm@{rain_threshold_time} (max {rain_total:.1f}mm@{rain_max_time})"
            else:
                # Same time: show only one time
                rain_part = f"Regen {rain_total:.1f}mm@{rain_threshold_time}"
        
        temp_part = f"Hitze {temp_max:.1f}°C"
        
        # Use real wind gusts data if available (tomorrow's data for evening reports)
        wind_gusts = weather_data.get("tomorrow_wind_gusts", weather_data.get("max_wind_gusts"))
        if wind_gusts and wind_gusts > wind_max:
            wind_part = f"Wind {wind_max:.0f} (max {wind_gusts:.0f})"
        else:
            wind_part = f"Wind {wind_max:.0f}km/h"
        
        # Combine all parts
        parts = [stage_part, night_part, thunder_part, rain_part, temp_part, wind_part]
        if vigilance_warning:
            parts.append(vigilance_warning)
        parts.append(thunder_next_part)  # Add "Gewitter +1" at the end since it's for a different day
        
        report_text = " | ".join(parts)
        
        # Ensure character limit
        if len(report_text) > 160:
            # Truncate while keeping essential information
            essential_parts = [stage_part, night_part, thunder_part, rain_part, temp_part, wind_part]
            report_text = " | ".join(essential_parts)
            if len(report_text) > 160:
                # Further truncate if still too long
                report_text = report_text[:160]
        
        return report_text
    
    def _generate_dynamic_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate dynamic report format for SMS.
        
        Format: {EtappeHeute} | Update: Gewitter {g2}%@{t2} | Regen {r2}%@{t4} | Hitze {temp_max}°C | Wind {wind_max}km/h | {vigilance_warning}
        """
        location = report_data.get("location", "Unknown")
        weather_data = report_data.get("weather_data", {})
        
        # Extract weather values with defaults
        thunderstorm_threshold_time = weather_data.get("thunderstorm_threshold_time", "")
        thunderstorm_threshold_pct = weather_data.get("thunderstorm_threshold_pct", 0)
        
        rain_threshold_time = weather_data.get("rain_threshold_time", "")
        rain_threshold_pct = weather_data.get("rain_threshold_pct", 0)
        
        temp_max = weather_data.get("max_temperature", 0)
        wind_max = weather_data.get("max_wind_speed", 0)
        
        # Extract vigilance warning
        vigilance_warning = self._format_vigilance_warning(weather_data.get("vigilance_alerts", []))
        
        # Format components
        stage_part = location.replace(" ", "")
        
        thunder_part = "Update: Gewitter"
        if thunderstorm_threshold_time and thunderstorm_threshold_pct > 0:
            thunder_part += f" {thunderstorm_threshold_pct:.0f}%@{thunderstorm_threshold_time}"
        
        rain_part = "Regen"
        if rain_threshold_time and rain_threshold_pct > 0:
            rain_part += f" {rain_threshold_pct:.0f}%@{rain_threshold_time}"
        
        temp_part = f"Hitze {temp_max:.1f}°C"
        
        # Use real wind gusts data if available
        wind_gusts = weather_data.get("max_wind_gusts")
        if wind_gusts and wind_gusts > wind_max:
            wind_part = f"Wind {wind_max:.0f} (max {wind_gusts:.0f})"
        else:
            wind_part = f"Wind {wind_max:.0f}km/h"
        
        # Combine all parts
        parts = [stage_part, thunder_part, rain_part, temp_part, wind_part]
        if vigilance_warning:
            parts.append(vigilance_warning)
        
        report_text = " | ".join(parts)
        
        # Ensure character limit
        if len(report_text) > 160:
            # Truncate while keeping essential information
            essential_parts = [stage_part, thunder_part, rain_part, temp_part, wind_part]
            report_text = " | ".join(essential_parts)
            if len(report_text) > 160:
                # Further truncate if still too long
                report_text = report_text[:160]
        
        return report_text
    
    def _generate_simple_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate simple report format as fallback.
        """
        location = report_data.get("location", "Unknown")
        weather_data = report_data.get("weather_data", {})
        
        temp_max = weather_data.get("max_temperature", 0)
        wind_max = weather_data.get("max_wind_speed", 0)
        
        report_text = f"{location} | Temp {temp_max:.1f}°C | Wind {wind_max:.0f}km/h"
        
        # Ensure character limit
        if len(report_text) > 160:
            report_text = report_text[:160]
        
        return report_text
    
    def _format_vigilance_warning(self, alerts: list) -> str:
        """
        Format vigilance warnings for SMS.
        
        Args:
            alerts: List of vigilance alert dictionaries
            
        Returns:
            Formatted vigilance warning string or empty string
        """
        if not alerts:
            return ""
        
        # Find the highest level alert
        highest_level = 0
        highest_alert = None
        
        for alert in alerts:
            level = alert.get("level", 0)
            if level > highest_level:
                highest_level = level
                highest_alert = alert
        
        if not highest_alert:
            return ""
        
        # Map level to color
        level_colors = {
            1: "GELB",
            2: "ORANGE", 
            3: "ROT"
        }
        
        color = level_colors.get(highest_level, "")
        alert_type = highest_alert.get("type", "Warnung")
        
        if color:
            return f"{color} {alert_type}"
        else:
            return alert_type 