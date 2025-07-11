"""
Email client for sending GR20 weather reports.

This module provides functionality to send weather reports via email
with proper formatting and character limits for mobile devices.
"""

import smtplib
import os
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

from weather.core.formatter import WeatherFormatter
from weather.core.models import AggregatedWeatherData, ReportType, ReportConfig, convert_dict_to_aggregated_weather_data, create_report_config_from_yaml
from fire.risk_block_formatter import format_risk_block

logger = logging.getLogger(__name__)

# Remove all the old formatting functions (_format_thunderstorm_field, etc.)
# as they are now handled by the central WeatherFormatter

class EmailClient:
    """
    Email client for sending GR20 weather reports.
    
    This class handles SMTP configuration and email sending with proper
    formatting for mobile devices.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the email client.
        
        Args:
            config: Configuration dictionary with SMTP settings
            
        Raises:
            ValueError: If SMTP configuration is missing or invalid
        """
        if not config or "smtp" not in config:
            raise ValueError("SMTP configuration is required")
        
        smtp_config = config["smtp"]
        required_fields = ["host", "port", "user", "to"]
        
        for field in required_fields:
            if field not in smtp_config:
                raise ValueError(f"SMTP configuration missing required field: {field}")
        
        self.smtp_host = smtp_config["host"]
        self.smtp_port = smtp_config["port"]
        self.smtp_user = smtp_config["user"]
        self.recipient_email = smtp_config["to"]
        self.subject_template = smtp_config.get("subject", "GR20 Weather Report")
        self.config = config  # Store full config for report generation
        
        # Get password from config (set by config_loader from GMAIL_APP_PW)
        self.smtp_password = smtp_config.get("password")
        
        # Fallback to environment variable for backward compatibility
        if not self.smtp_password:
            self.smtp_password = os.getenv("GMAIL_APP_PW") or os.getenv("SMTP_PASSWORD")
    
    def send_email(self, message_text: str, subject: Optional[str] = None) -> bool:
        """
        Send an email with the given message.
        
        Args:
            message_text: The message text to send
            subject: Optional subject line (uses template if not provided)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.recipient_email
            msg['Subject'] = subject or self.subject_template
            
            # Add message body
            msg.attach(MIMEText(message_text, 'plain', 'utf-8'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            
            # Login with password from config or environment
            if self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            else:
                # Try without password (for testing or if not required)
                server.login(self.smtp_user, "")
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.smtp_user, self.recipient_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def _generate_dynamic_subject(self, report_data: Dict[str, Any]) -> str:
        """
        Generate email subject according to email_format specification.
        
        Format: {subject} {etappe}: {risk_level} - {highest_risk} ({report_type})
        
        Args:
            report_data: Dictionary containing report information
            
        Returns:
            Formatted subject string
        """
        # Get base subject from config
        base_subject = self.config.get("smtp", {}).get("subject", "GR20 Wetter")
        
        # Get report type
        report_type = report_data.get("report_type", "morning")
        
        # Get stage name
        if report_type == "evening":
            # Use tomorrow's stage for evening reports
            stage = report_data.get("weather_data", {}).get("tomorrow_stage") or report_data.get("location", "Unknown")
        else:
            stage = report_data.get("location", "Unknown")
        
        # Get vigilance warnings (zone-based fire risk warnings are included in fire_risk_warning)
        weather_data = report_data.get("weather_data", {})
        fire_risk_warning = weather_data.get("fire_risk_warning", "")
        vigilance_alerts = weather_data.get("vigilance_alerts", [])
        
        # If fire_risk_warning is present, use it for subject
        if fire_risk_warning:
            # fire_risk_warning is like 'HIGH Waldbrand' or ''
            parts = fire_risk_warning.split()
            if len(parts) == 2:
                risk_level, highest_risk = parts
            else:
                risk_level, highest_risk = fire_risk_warning, "Waldbrand"
        elif not vigilance_alerts:
            # No vigilance warnings
            risk_level = ""
            highest_risk = ""
        else:
            # Find the highest level alert
            level_priority = {"green": 1, "risk": 2, "high": 3, "max": 4}
            highest_alert = max(vigilance_alerts, key=lambda a: level_priority.get(a.get("level", "green"), 1))
            
            level = highest_alert.get("level", "green")
            phenomenon = highest_alert.get("phenomenon", "unknown")
            
            # Only include if level is risk or higher (equivalent to yellow or higher)
            if level_priority.get(level, 1) < 2:
                risk_level = ""
                highest_risk = ""
            else:
                # Translate phenomenon to German (excluding heat, wind, and rain as requested)
                phenomenon_translation = {
                    "thunderstorm": "Gewitter",
                    # "rain": "Regen",  # Excluded as requested
                    # "wind": "Wind",  # Excluded as requested
                    "snow": "Schnee",
                    "flood": "Hochwasser",
                    "forest_fire": "Waldbrand",
                    # "heat": "Hitze",  # Excluded as requested
                    "cold": "Kälte",
                    "avalanche": "Lawine",
                    "unknown": "Warnung"
                }
                german_phenomenon = phenomenon_translation.get(phenomenon.lower(), phenomenon)
                risk_level = level.upper()
                highest_risk = german_phenomenon
        # Format: {subject} {etappe}: {risk_level} - {highest_risk} ({report_type})
        if risk_level and highest_risk:
            subject = f"{base_subject} {stage}: {risk_level} - {highest_risk} ({report_type})"
        else:
            subject = f"{base_subject} {stage}:  ({report_type})"
        return subject

    def send_gr20_report(self, report_data: Dict[str, Any]) -> bool:
        """
        Send a GR20 weather report email.
        
        Args:
            report_data: Dictionary containing report information:
                - location: Current location name
                - risk_percentage: Risk percentage (0-100)
                - risk_description: Description of the risk
                - report_time: Datetime of the report
                - report_type: "scheduled" or "dynamic"
                - weather_analysis: WeatherAnalysis object for risk assessment
                
        Returns:
            True if email sent successfully, False otherwise
        """
        # Generate report text
        message_text = generate_gr20_report_text(report_data, self.config)
        
        # Generate dynamic subject
        subject = self._generate_dynamic_subject(report_data)
        
        # Debug output: show the actual email content
        print(f"\n=== EMAIL CONTENT ===")
        print(f"Subject: {subject}")
        print(f"Message: {message_text}")
        print(f"Length: {len(message_text)} characters")
        print(f"=====================\n")
        
        # Log the email content for debugging
        logger.info(f"EMAIL GENERATED - Subject: {subject}")
        logger.info(f"EMAIL GENERATED - Message: {message_text}")
        logger.info(f"EMAIL GENERATED - Length: {len(message_text)} characters")
        
        # Send email
        send_result = self.send_email(message_text, subject)
        
        if send_result:
            logger.info(f"EMAIL SENT SUCCESSFULLY to {self.recipient_email}")
        else:
            logger.error(f"EMAIL SEND FAILED to {self.recipient_email}")
        
        return send_result


def generate_gr20_report_text(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate GR20 weather report text according to email_format rule.
    
    Args:
        report_data: Dictionary containing report information:
            - location: Current location name
            - report_type: "morning", "evening", or "dynamic"
            - weather_data: Detailed weather data for formatting
            - report_time: Datetime of the report
        config: Configuration dictionary
        
    Returns:
        Formatted report text (max 160 characters, no links)
    """
    report_type = report_data.get("report_type", "morning")
    
    # Generate base report text
    if report_type == "morning":
        base_text = _generate_morning_report(report_data, config)
    elif report_type == "evening":
        base_text = _generate_evening_report(report_data, config)
    elif report_type == "dynamic":
        base_text = _generate_dynamic_report(report_data, config)
    else:
        # Fallback to old format for backward compatibility
        base_text = _generate_legacy_report(report_data, config)
    
    # Add risk block if relevant
    try:
        weather_data = report_data.get("weather_data", {})
        latitude = weather_data.get("latitude", 0.0)
        longitude = weather_data.get("longitude", 0.0)
        
        if latitude and longitude:
            risk_block = format_risk_block(latitude, longitude)
            if risk_block:
                # Append risk block to base text
                combined_text = f"{base_text} {risk_block}"
                
                # Ensure total length doesn't exceed 160 characters
                if len(combined_text) <= 160:
                    return combined_text
                else:
                    # If too long, truncate the base text to make room for risk block
                    available_space = 160 - len(risk_block) - 1  # -1 for space
                    if available_space > 0:
                        truncated_base = base_text[:available_space]
                        return f"{truncated_base} {risk_block}"
                    else:
                        # If risk block is too long, return base text only
                        logger.warning(f"Risk block too long ({len(risk_block)} chars), using base text only")
                        return base_text
    except Exception as e:
        logger.error(f"Error adding risk block to report: {e}")
        # Return base text if risk block fails
    
    return base_text


def _format_value_or_dash(value, *args):
    """Return '-' if value is 0 or None, else format with args."""
    if value is None or value == 0:
        return "-"
    return args[0].format(value) if args else str(value)


def _generate_morning_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate morning report format using central formatter.
    """
    try:
        # Convert report_data to AggregatedWeatherData format
        weather_data = report_data.get("weather_data", {})
        location_name = weather_data.get("location_name") or weather_data.get("location") or "Unknown"
        latitude = weather_data.get("latitude", 0.0)
        longitude = weather_data.get("longitude", 0.0)
        agg_data = convert_dict_to_aggregated_weather_data(weather_data, location_name, latitude, longitude)
        
        # Get stage names from report_data
        stage_names_list = report_data.get("stage_names", ["Unknown"])
        stage_name = stage_names_list[0] if stage_names_list else "Unknown"
        stage_names_dict = {"today": stage_name}
        
        # Use central formatter
        formatter = WeatherFormatter(create_report_config_from_yaml(config))
        return formatter.format_report_text(
            agg_data,
            ReportType("morning"),
            stage_names_dict
        )
    except Exception as e:
        logger.error(f"Error generating morning report: {e}")
        return "Error generating report"


def _generate_evening_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate evening report format using central formatter.
    """
    try:
        # Convert report_data to AggregatedWeatherData format
        weather_data = report_data.get("weather_data", {})
        location_name = weather_data.get("location_name") or weather_data.get("location") or "Unknown"
        latitude = weather_data.get("latitude", 0.0)
        longitude = weather_data.get("longitude", 0.0)
        agg_data = convert_dict_to_aggregated_weather_data(weather_data, location_name, latitude, longitude)
        
        # Get stage names from report_data
        stage_names_list = report_data.get("stage_names", [])
        stage_names_dict = {
            'tomorrow': stage_names_list[0] if len(stage_names_list) > 0 else 'Unknown',
            'day_after_tomorrow': stage_names_list[1] if len(stage_names_list) > 1 else 'Unknown'
        }
        
        # Use central formatter with config from yaml
        formatter = WeatherFormatter(create_report_config_from_yaml(config))
        from weather.core.models import AggregatedWeatherData
        from weather.core.models import ReportType
        
        # Debug: Print the actual values from weather_data
        print(f"\n=== DEBUG: weather_data values ===")
        print(f"max_temperature: {weather_data.get('max_temperature', 0)}")
        print(f"max_temperature_time: {weather_data.get('max_temperature_time', '')}")
        print(f"min_temperature: {weather_data.get('min_temperature', 0)}")
        print(f"min_temperature_time: {weather_data.get('min_temperature_time', '')}")
        print(f"max_rain_probability: {weather_data.get('max_rain_probability', 0)}")
        print(f"rain_max_time: {weather_data.get('rain_max_time', '')}")
        print(f"max_precipitation: {weather_data.get('max_precipitation', 0)}")
        print(f"precipitation_time: {weather_data.get('precipitation_time', '')}")
        print(f"max_wind_speed: {weather_data.get('max_wind_speed', 0)}")
        print(f"wind_speed_time: {weather_data.get('wind_speed_time', '')}")
        print(f"max_wind_gusts: {weather_data.get('max_wind_gusts', 0)}")
        print(f"wind_gusts_time: {weather_data.get('wind_gusts_time', '')}")
        print(f"==========================================\n")
        
        # Create AggregatedWeatherData with the global maxima
        weather_data_obj = AggregatedWeatherData(
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            max_temperature=weather_data.get('max_temperature', 0.0),
            max_temperature_time=weather_data.get('max_temperature_time', ''),
            min_temperature=weather_data.get('min_temperature', 0.0),
            min_temperature_time=weather_data.get('min_temperature_time', ''),
            max_rain_probability=weather_data.get('max_rain_probability', 0.0),
            rain_max_time=weather_data.get('rain_max_time', ''),
            rain_threshold_pct=weather_data.get('rain_threshold_pct', 0.0),
            rain_threshold_time=weather_data.get('rain_threshold_time', ''),
            max_precipitation=weather_data.get('max_precipitation', 0.0),
            precipitation_max_time=weather_data.get('precipitation_time', ''),
            max_wind_speed=weather_data.get('max_wind_speed', 0.0),
            wind_max_time=weather_data.get('wind_speed_time', ''),
            max_wind_gusts=weather_data.get('max_wind_gusts', 0.0),
            wind_gusts_max_time=weather_data.get('wind_gusts_time', ''),
            max_thunderstorm_probability=weather_data.get('max_thunderstorm_probability', 0.0),
            thunderstorm_max_time=weather_data.get('thunderstorm_max_time', ''),
            thunderstorm_threshold_pct=weather_data.get('thunderstorm_threshold_pct', 0.0),
            thunderstorm_threshold_time=weather_data.get('thunderstorm_threshold_time', ''),
            tomorrow_max_thunderstorm_probability=weather_data.get('thunderstorm_next_day', 0.0),
            tomorrow_thunderstorm_max_time=weather_data.get('thunderstorm_next_day_max_time', ''),
            tomorrow_thunderstorm_threshold_time=weather_data.get('thunderstorm_next_day_threshold_time', ''),
            fire_risk_warning=weather_data.get('fire_risk_warning', '')
        )
        
        # Debug: Print the AggregatedWeatherData values
        print(f"\n=== DEBUG: AggregatedWeatherData values ===")
        print(f"max_rain_probability: {weather_data_obj.max_rain_probability}")
        print(f"rain_max_time: '{weather_data_obj.rain_max_time}' (type: {type(weather_data_obj.rain_max_time)})")
        print(f"rain_threshold_pct: {weather_data_obj.rain_threshold_pct}")
        print(f"rain_threshold_time: '{weather_data_obj.rain_threshold_time}' (type: {type(weather_data_obj.rain_threshold_time)})")
        print(f"max_precipitation: {weather_data_obj.max_precipitation}")
        print(f"precipitation_max_time: '{weather_data_obj.precipitation_max_time}' (type: {type(weather_data_obj.precipitation_max_time)})")
        print(f"==========================================\n")
        
        return formatter.format_report_text(weather_data_obj, ReportType("evening"), stage_names_dict)
        
    except Exception as e:
        logger.error(f"Failed to generate evening report: {e}")
        return f"Error generating evening report: {e}"


def _generate_dynamic_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate dynamic update report format using central formatter.
    """
    try:
        # Convert report_data to AggregatedWeatherData format
        weather_data = report_data.get("weather_data", {})
        location_name = weather_data.get("location_name") or weather_data.get("location") or "Unknown"
        latitude = weather_data.get("latitude", 0.0)
        longitude = weather_data.get("longitude", 0.0)
        agg_data = convert_dict_to_aggregated_weather_data(weather_data, location_name, latitude, longitude)
        
        # Get stage names from report_data
        stage_names_list = report_data.get("stage_names", ["Unknown"])
        stage_name = stage_names_list[0] if stage_names_list else "Unknown"
        stage_names_dict = {"today": stage_name}
        
        # Use central formatter
        formatter = WeatherFormatter(create_report_config_from_yaml(config))
        return formatter.format_report_text(
            agg_data,
            ReportType("update"),
            stage_names_dict
        )
    except Exception as e:
        logger.error(f"Error generating dynamic report: {e}")
        return "Error generating report"


def _generate_legacy_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Legacy report format for backward compatibility.
    """
    # Extract data
    location = report_data.get("location", "Unknown")
    risk_percentage = report_data.get("risk_percentage", 0)
    risk_description = report_data.get("risk_description", "Wetterrisiko")
    report_time = report_data.get("report_time", datetime.now())
    
    # Format time
    time_str = report_time.strftime("%d-%b %H:%M")
    
    # Build message components (no links for security)
    header = f"GR20 Wetter {time_str}"
    location_part = f"| {location}"
    
    # Use text-based risk indicator instead of emoji
    if risk_percentage >= 80:
        risk_indicator = "ALARM"
    elif risk_percentage >= 60:
        risk_indicator = "WARNUNG"
    elif risk_percentage >= 40:
        risk_indicator = "ACHTUNG"
    else:
        risk_indicator = "INFO"
    
    risk_part = f"| {risk_indicator} {risk_description} {risk_percentage}%"
    
    # Combine all parts (no links)
    full_message = f"{header} {location_part} {risk_part}".strip()
    
    # Ensure character limit (160 characters for SMS compatibility)
    if len(full_message) > 160:
        # Truncate location name if too long
        max_location_length = 160 - len(header) - len(risk_part) - 3  # 3 for separators
        if max_location_length > 3:
            location_part = f"| {location[:max_location_length-3]}..."
        else:
            location_part = "| ..."
        
        full_message = f"{header} {location_part} {risk_part}".strip()
        
        # Final check - truncate if still too long
        if len(full_message) > 160:
            full_message = full_message[:157] + "..."
    
    return full_message


def _format_vigilance_warning(alerts: List[Dict[str, Any]]) -> str:
    """
    Format vigilance warnings to a compact string.
    Args:
        alerts: List of alert dictionaries with 'phenomenon' and 'level' keys
    Returns:
        Formatted warning string or empty string if no alerts
    """
    if not alerts:
        return ""
    # Exclude wind, rain, and heat from vigilance warnings
    EXCLUDED = {"wind", "rain", "heat"}
    level_priority = {"green": 1, "risk": 2, "high": 3, "max": 4}
    # Sort alerts by level descending
    sorted_alerts = sorted(alerts, key=lambda a: level_priority.get(a.get("level", "green"), 1), reverse=True)
    for alert in sorted_alerts:
        phenomenon = alert.get("phenomenon", "unknown").lower()
        if phenomenon in EXCLUDED:
            continue
        level = alert.get("level", "green")
        if level_priority.get(level, 1) < 2:
            continue
        # Translate phenomenon to German (excluding heat, wind, and rain as requested)
        phenomenon_translation = {
            "thunderstorm": "Gewitter",
            # "rain": "Regen",  # Excluded as requested
            # "wind": "Wind",  # Excluded as requested
            "snow": "Schnee",
            "flood": "Hochwasser",
            "forest_fire": "Waldbrand",
            # "heat": "Hitze",  # Excluded as requested
            "cold": "Kälte",
            "avalanche": "Lawine",
            "unknown": "Warnung"
        }
        german_phenomenon = phenomenon_translation.get(phenomenon, phenomenon)
        level_upper = level.upper()
        return f"{level_upper} {german_phenomenon}"
    return "" 