"""
Email client for sending GR20 weather reports.

This module provides functionality to send weather reports via email
with proper formatting and character limits for mobile devices.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional, List


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
                
        Returns:
            True if email sent successfully, False otherwise
        """
        # Generate report text
        message_text = generate_gr20_report_text(report_data, self.config)
        
        # Send email
        return self.send_email(message_text)


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
    
    if report_type == "morning":
        return _generate_morning_report(report_data, config)
    elif report_type == "evening":
        return _generate_evening_report(report_data, config)
    elif report_type == "dynamic":
        return _generate_dynamic_report(report_data, config)
    else:
        # Fallback to old format for backward compatibility
        return _generate_legacy_report(report_data, config)


def _generate_morning_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate morning report format: {EtappeHeute} | Gewitter {g1}%@{t1} {g2}%@{t2} | Regen {r1}%@{t3} {r2}%@{t4} {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h | Gewitter +1 {g1_next}% | {vigilance_warning}
    """
    location = report_data.get("location", "Unknown")
    weather_data = report_data.get("weather_data", {})
    
    # Extract weather values with defaults
    thunderstorm_max = weather_data.get("max_thunderstorm_probability", 0)
    thunderstorm_threshold_time = weather_data.get("thunderstorm_threshold_time", "")
    thunderstorm_threshold_pct = weather_data.get("thunderstorm_threshold_pct", 0)
    thunderstorm_next_day = weather_data.get("thunderstorm_next_day", 0)
    
    rain_max = weather_data.get("max_precipitation_probability", 0)
    rain_threshold_time = weather_data.get("rain_threshold_time", "")
    rain_threshold_pct = weather_data.get("rain_threshold_pct", 0)
    rain_total = weather_data.get("max_precipitation", 0)
    
    temp_max = weather_data.get("max_temperature", 0)
    wind_max = weather_data.get("max_wind_speed", 0)
    
    # Extract vigilance warning
    vigilance_warning = _format_vigilance_warning(weather_data.get("vigilance_alerts", []))
    
    # Format components
    stage_part = location.replace(" ", "")
    
    thunder_part = f"Gewitter {thunderstorm_max:.0f}%"
    if thunderstorm_threshold_time and thunderstorm_threshold_pct > 0:
        thunder_part += f"@{thunderstorm_threshold_time} {thunderstorm_threshold_pct:.0f}%"
    
    thunder_next_part = f"Gewitter +1 {thunderstorm_next_day:.0f}%"
    
    rain_part = f"Regen {rain_max:.0f}%"
    if rain_threshold_time and rain_threshold_pct > 0:
        rain_part += f"@{rain_threshold_time} {rain_threshold_pct:.0f}%"
    rain_part += f" {rain_total:.1f}mm"
    
    temp_part = f"Hitze {temp_max:.1f}°C"
    wind_part = f"Wind {wind_max:.0f}km/h"
    
    # Combine all parts
    parts = [stage_part, thunder_part, rain_part, temp_part, wind_part, thunder_next_part]
    if vigilance_warning:
        parts.append(vigilance_warning)
    
    report_text = " | ".join(parts)
    
    # Ensure character limit
    if len(report_text) > 160:
        report_text = report_text[:157] + "..."
    
    return report_text


def _generate_evening_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate evening report format: {EtappeMorgen}→{EtappeÜbermorgen} | Nacht {min_temp}°C | Gewitter {g1}%@{t1} ({g2}%@{t2}) | Regen {r1}%@{t3} ({r2}%@{t4}) {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h | Gewitter +1 {g1_next}% | {vigilance_warning}
    """
    location = report_data.get("location", "Unknown")
    weather_data = report_data.get("weather_data", {})
    
    # Extract stage information
    tomorrow_stage = weather_data.get("tomorrow_stage", location)
    day_after_stage = weather_data.get("day_after_stage", "")
    
    # Extract weather values
    night_temp = weather_data.get("night_temperature", 0)
    thunderstorm_max = weather_data.get("max_thunderstorm_probability", 0)
    thunderstorm_threshold_time = weather_data.get("thunderstorm_threshold_time", "")
    thunderstorm_threshold_pct = weather_data.get("thunderstorm_threshold_pct", 0)
    thunderstorm_day_after = weather_data.get("thunderstorm_day_after", 0)
    
    rain_max = weather_data.get("max_precipitation_probability", 0)
    rain_threshold_time = weather_data.get("rain_threshold_time", "")
    rain_threshold_pct = weather_data.get("rain_threshold_pct", 0)
    rain_total = weather_data.get("max_precipitation", 0)
    
    temp_max = weather_data.get("max_temperature", 0)
    wind_max = weather_data.get("max_wind_speed", 0)
    
    # Extract vigilance warning
    vigilance_warning = _format_vigilance_warning(weather_data.get("vigilance_alerts", []))
    
    # Format components
    stage_part = tomorrow_stage.replace(" ", "")
    if day_after_stage:
        stage_part += f"→{day_after_stage.replace(' ', '')}"
    
    night_part = f"Nacht {night_temp:.1f}°C"
    
    thunder_part = f"Gewitter {thunderstorm_max:.0f}%"
    if thunderstorm_threshold_time and thunderstorm_threshold_pct > 0:
        thunder_part += f" ({thunderstorm_threshold_pct:.0f}%@{thunderstorm_threshold_time})"
    
    thunder_next_part = f"Gewitter +1 {thunderstorm_day_after:.0f}%"
    
    rain_part = f"Regen {rain_max:.0f}%"
    if rain_threshold_time and rain_threshold_pct > 0:
        rain_part += f" ({rain_threshold_pct:.0f}%@{rain_threshold_time})"
    rain_part += f" {rain_total:.1f}mm"
    
    temp_part = f"Hitze {temp_max:.1f}°C"
    wind_part = f"Wind {wind_max:.0f}km/h"
    
    # Combine all parts
    parts = [stage_part, night_part, thunder_part, rain_part, temp_part, wind_part, thunder_next_part]
    if vigilance_warning:
        parts.append(vigilance_warning)
    
    report_text = " | ".join(parts)
    
    # Ensure character limit
    if len(report_text) > 160:
        report_text = report_text[:157] + "..."
    
    return report_text


def _generate_dynamic_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate dynamic update report format: {EtappeHeute} | Update: Gewitter {g2}%@{t2} | Regen {r2}%@{t4} | Hitze {temp_max}°C | Wind {wind_max}km/h | {vigilance_warning}
    """
    location = report_data.get("location", "Unknown")
    weather_data = report_data.get("weather_data", {})
    
    # Extract weather values (only significant changes)
    thunderstorm_threshold_time = weather_data.get("thunderstorm_threshold_time", "")
    thunderstorm_threshold_pct = weather_data.get("thunderstorm_threshold_pct", 0)
    
    rain_threshold_time = weather_data.get("rain_threshold_time", "")
    rain_threshold_pct = weather_data.get("rain_threshold_pct", 0)
    
    temp_max = weather_data.get("max_temperature", 0)
    wind_max = weather_data.get("max_wind_speed", 0)
    
    # Extract vigilance warning
    vigilance_warning = _format_vigilance_warning(weather_data.get("vigilance_alerts", []))
    
    # Format components
    stage_part = location.replace(" ", "")
    
    thunder_part = ""
    if thunderstorm_threshold_time and thunderstorm_threshold_pct > 0:
        thunder_part = f"Gewitter {thunderstorm_threshold_pct:.0f}%@{thunderstorm_threshold_time}"
    
    rain_part = ""
    if rain_threshold_time and rain_threshold_pct > 0:
        rain_part = f"Regen {rain_threshold_pct:.0f}%@{rain_threshold_time}"
    
    temp_part = f"Hitze {temp_max:.1f}°C"
    wind_part = f"Wind {wind_max:.0f}km/h"
    
    # Combine parts (only include non-empty parts)
    parts = [stage_part, "Update:"]
    if thunder_part:
        parts.append(thunder_part)
    if rain_part:
        parts.append(rain_part)
    parts.extend([temp_part, wind_part])
    if vigilance_warning:
        parts.append(vigilance_warning)
    
    report_text = " | ".join(parts)
    
    # Ensure character limit
    if len(report_text) > 160:
        report_text = report_text[:157] + "..."
    
    return report_text


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
    
    # Find the highest level alert
    level_priority = {"green": 1, "yellow": 2, "orange": 3, "red": 4}
    highest_alert = max(alerts, key=lambda a: level_priority.get(a.get("level", "green"), 1))
    
    level = highest_alert.get("level", "green")
    phenomenon = highest_alert.get("phenomenon", "unknown")
    
    # Only include if level is yellow or higher
    if level_priority.get(level, 1) < 2:
        return ""
    
    # Translate phenomenon to German
    phenomenon_translation = {
        "thunderstorm": "Gewitter",
        "rain": "Regen",
        "wind": "Wind",
        "snow": "Schnee",
        "flood": "Hochwasser",
        "forest_fire": "Waldbrand",
        "heat": "Hitze",
        "cold": "Kälte",
        "avalanche": "Lawine",
        "unknown": "Warnung"
    }
    
    german_phenomenon = phenomenon_translation.get(phenomenon.lower(), phenomenon)
    
    # Format: LEVEL PHENOMENON (e.g., "ORANGE Gewitter", "ROT Waldbrand")
    level_upper = level.upper()
    return f"{level_upper} {german_phenomenon}" 