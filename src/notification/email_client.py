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
        
        # Get vigilance warnings
        vigilance_alerts = report_data.get("weather_data", {}).get("vigilance_alerts", [])
        
        if not vigilance_alerts:
            # No vigilance warnings
            risk_level = ""
            highest_risk = ""
        else:
            # Find the highest level alert
            level_priority = {"green": 1, "yellow": 2, "orange": 3, "red": 4}
            highest_alert = max(vigilance_alerts, key=lambda a: level_priority.get(a.get("level", "green"), 1))
            
            level = highest_alert.get("level", "green")
            phenomenon = highest_alert.get("phenomenon", "unknown")
            
            # Only include if level is yellow or higher
            if level_priority.get(level, 1) < 2:
                risk_level = ""
                highest_risk = ""
            else:
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
        
        # Send email
        return self.send_email(message_text, subject)


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


def _format_value_or_dash(value, *args):
    """Return '-' if value is 0 or None, else format with args."""
    if value is None or value == 0:
        return "-"
    return args[0].format(value) if args else str(value)


def _generate_morning_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate morning report format according to email_format specification.
    
    Format: {etappe_heute} | Gew.{g_threshold}%@{t_g_threshold}({g_pmax}%@{t_g_pmax}) | Regen{r_threshold}%@{t_r_threshold}({r_pmax}%@{t_r_pmax}) | Regen{regen_mm}mm@{t_regen_max} | Hitze{temp_max}°C | Wind{wind}km/h | Windböen{wind_max}km/h | Gew.+1{g1_next}%@{t_g1_next_threshold}
    """
    location = report_data.get("location", "Unknown")
    weather_data = report_data.get("weather_data", {})
    
    # Extract weather values with defaults
    g_threshold = weather_data.get("thunderstorm_threshold_pct", 0)
    t_g_threshold = weather_data.get("thunderstorm_threshold_time", "")
    g_pmax = weather_data.get("max_thunderstorm_probability", 0)
    t_g_pmax = weather_data.get("thunderstorm_max_time", "")
    
    r_threshold = weather_data.get("rain_threshold_pct", 0)
    t_r_threshold = weather_data.get("rain_threshold_time", "")
    r_pmax = weather_data.get("max_rain_probability", 0)
    t_r_pmax = weather_data.get("rain_max_time", "")
    
    regen_mm = weather_data.get("max_precipitation", 0)
    t_regen_max = weather_data.get("rain_total_time", "")
    
    temp_max = weather_data.get("max_temperature", 0)
    wind = weather_data.get("wind_speed", 0)  # Average wind speed
    wind_max = weather_data.get("max_wind_speed", 0)  # Wind gusts
    
    g1_next = weather_data.get("thunderstorm_next_day", 0)
    t_g1_next_threshold = weather_data.get("thunderstorm_next_day_threshold_time", "")
    
    # Extract vigilance warning
    vigilance_warning = _format_vigilance_warning(weather_data.get("vigilance_alerts", []))
    
    # Format components
    stage_part = location.replace(" ", "")
    
    # Thunderstorm part
    if g_threshold == 0 or g_threshold is None:
        thunder_part = "Gew. -"
    else:
        thunder_part = f"Gew.{g_threshold:.0f}%@{t_g_threshold}"
        if g_pmax > g_threshold:
            thunder_part += f"({g_pmax:.0f}%@{t_g_pmax})"
    
    # Rain part
    if r_threshold == 0 or r_threshold is None:
        rain_part = "Regen -"
    else:
        rain_part = f"Regen{r_threshold:.0f}%@{t_r_threshold}"
        if r_pmax > r_threshold:
            rain_part += f"({r_pmax:.0f}%@{t_r_pmax})"
    
    # Rain amount part
    if regen_mm == 0 or regen_mm is None:
        rain_amount_part = "Regen -mm"
    else:
        rain_amount_part = f"Regen{regen_mm:.1f}mm@{t_regen_max}"
    
    # Temperature part
    temp_part = f"Hitze{temp_max:.1f}°C" if temp_max > 0 else "Hitze -"
    
    # Wind parts
    wind_part = f"Wind{wind:.0f}km/h" if wind > 0 else "Wind -"
    wind_gust_part = f"Windböen{wind_max:.0f}km/h" if wind_max > 0 else "Windböen -"
    
    # Thunderstorm next day part
    if g1_next == 0 or g1_next is None:
        thunder_next_part = "Gew.+1 -"
    else:
        thunder_next_part = f"Gew.+1{g1_next:.0f}%"
        if t_g1_next_threshold:
            thunder_next_part += f"@{t_g1_next_threshold}"
    
    # Combine all parts
    parts = [stage_part, thunder_part, rain_part, rain_amount_part, temp_part, wind_part, wind_gust_part, thunder_next_part]
    if vigilance_warning:
        parts.append(vigilance_warning)
    
    report_text = " | ".join(parts)
    
    # Ensure character limit
    if len(report_text) > 160:
        report_text = report_text[:157] + "..."
    
    return report_text


def _generate_evening_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate evening report format according to email_format specification.
    
    Format: {etappe_morgen}→{etappe_uebermorgen} | Nacht{min_temp}°C | Gew.{g_threshold}%@{t_g_threshold}({g_pmax}%@{t_g_pmax}) | Regen{r_threshold}%@{t_r_threshold}({r_pmax}%@{t_r_pmax}) | Regen{regen_mm}mm@{t_regen_max} | Hitze{temp_max}°C | Wind{wind}km/h | Windböen{wind_max}km/h | Gew.+1{g1_next}%@{t_g1_next_threshold}
    """
    location = report_data.get("location", "Unknown")
    weather_data = report_data.get("weather_data", {})
    
    # Extract stage information
    tomorrow_stage = weather_data.get("tomorrow_stage", location)
    day_after_stage = weather_data.get("day_after_stage", "")
    
    # Extract weather values
    min_temp = weather_data.get("min_temperature", 0)
    
    g_threshold = weather_data.get("tomorrow_thunderstorm_threshold_pct", weather_data.get("thunderstorm_threshold_pct", 0))
    t_g_threshold = weather_data.get("tomorrow_thunderstorm_threshold_time", weather_data.get("thunderstorm_threshold_time", ""))
    g_pmax = weather_data.get("tomorrow_thunderstorm_probability", weather_data.get("max_thunderstorm_probability", 0))
    t_g_pmax = weather_data.get("tomorrow_thunderstorm_max_time", weather_data.get("thunderstorm_max_time", ""))
    
    r_threshold = weather_data.get("tomorrow_rain_threshold_pct", weather_data.get("rain_threshold_pct", 0))
    t_r_threshold = weather_data.get("tomorrow_rain_threshold_time", weather_data.get("rain_threshold_time", ""))
    r_pmax = weather_data.get("tomorrow_rain_probability", weather_data.get("max_rain_probability", 0))
    t_r_pmax = weather_data.get("tomorrow_rain_max_time", weather_data.get("rain_max_time", ""))
    
    regen_mm = weather_data.get("tomorrow_precipitation", weather_data.get("max_precipitation", 0))
    t_regen_max = weather_data.get("tomorrow_rain_total_time", weather_data.get("rain_total_time", ""))
    
    temp_max = weather_data.get("tomorrow_temperature", weather_data.get("max_temperature", 0))
    wind = weather_data.get("tomorrow_wind_speed", weather_data.get("wind_speed", 0))
    wind_max = weather_data.get("tomorrow_wind_gusts", weather_data.get("max_wind_speed", 0))
    
    g1_next = weather_data.get("thunderstorm_day_after", 0)
    t_g1_next_threshold = weather_data.get("thunderstorm_day_after_threshold_time", "")
    
    # Extract vigilance warning
    vigilance_warning = _format_vigilance_warning(weather_data.get("vigilance_alerts", []))
    
    # Format components
    stage_part = tomorrow_stage.replace(" ", "")
    if day_after_stage:
        stage_part += f"→{day_after_stage.replace(' ', '')}"
    
    night_part = f"Nacht{min_temp:.1f}°C"
    
    # Thunderstorm part
    if g_threshold == 0 or g_threshold is None:
        thunder_part = "Gew. -"
    else:
        thunder_part = f"Gew.{g_threshold:.0f}%@{t_g_threshold}"
        if g_pmax > g_threshold:
            thunder_part += f"({g_pmax:.0f}%@{t_g_pmax})"
    
    # Rain part
    if r_threshold == 0 or r_threshold is None:
        rain_part = "Regen -"
    else:
        rain_part = f"Regen{r_threshold:.0f}%@{t_r_threshold}"
        if r_pmax > r_threshold:
            rain_part += f"({r_pmax:.0f}%@{t_r_pmax})"
    
    # Rain amount part
    if regen_mm == 0 or regen_mm is None:
        rain_amount_part = "Regen -mm"
    else:
        rain_amount_part = f"Regen{regen_mm:.1f}mm@{t_regen_max}"
    
    # Temperature part
    temp_part = f"Hitze{temp_max:.1f}°C" if temp_max > 0 else "Hitze -"
    
    # Wind parts
    wind_part = f"Wind{wind:.0f}km/h" if wind > 0 else "Wind -"
    wind_gust_part = f"Windböen{wind_max:.0f}km/h" if wind_max > 0 else "Windböen -"
    
    # Thunderstorm next day part
    if g1_next == 0 or g1_next is None:
        thunder_next_part = "Gew.+1 -"
    else:
        thunder_next_part = f"Gew.+1{g1_next:.0f}%"
        if t_g1_next_threshold:
            thunder_next_part += f"@{t_g1_next_threshold}"
    
    # Combine all parts
    parts = [stage_part, night_part, thunder_part, rain_part, rain_amount_part, temp_part, wind_part, wind_gust_part, thunder_next_part]
    if vigilance_warning:
        parts.append(vigilance_warning)
    
    report_text = " | ".join(parts)
    
    # Ensure character limit
    if len(report_text) > 160:
        report_text = report_text[:157] + "..."
    
    return report_text


def _generate_dynamic_report(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate dynamic update report format according to email_format specification.
    
    Format: {etappe_heute} | Update: | Gew.{g_threshold}%@{t_g_threshold}({g_pmax}%@{t_g_pmax}) | Regen{r_threshold}%@{t_r_threshold}({r_pmax}%@{t_r_pmax}) | Regen{regen_mm}mm@{t_regen_max} | Hitze{temp_max}°C | Wind{wind}km/h | Windböen{wind_max}km/h | Gew.+1{g1_next}%@{t_g1_next_threshold}
    """
    location = report_data.get("location", "Unknown")
    weather_data = report_data.get("weather_data", {})
    
    # Extract weather values (only significant changes)
    g_threshold = weather_data.get("thunderstorm_threshold_pct", 0)
    t_g_threshold = weather_data.get("thunderstorm_threshold_time", "")
    g_pmax = weather_data.get("max_thunderstorm_probability", 0)
    t_g_pmax = weather_data.get("thunderstorm_max_time", "")
    
    r_threshold = weather_data.get("rain_threshold_pct", 0)
    t_r_threshold = weather_data.get("rain_threshold_time", "")
    r_pmax = weather_data.get("max_rain_probability", 0)
    t_r_pmax = weather_data.get("rain_max_time", "")
    
    regen_mm = weather_data.get("max_precipitation", 0)
    t_regen_max = weather_data.get("rain_total_time", "")
    
    temp_max = weather_data.get("max_temperature", 0)
    wind = weather_data.get("wind_speed", 0)
    wind_max = weather_data.get("max_wind_speed", 0)
    
    g1_next = weather_data.get("thunderstorm_next_day", 0)
    t_g1_next_threshold = weather_data.get("thunderstorm_next_day_threshold_time", "")
    
    # Extract vigilance warning
    vigilance_warning = _format_vigilance_warning(weather_data.get("vigilance_alerts", []))
    
    # Format components
    stage_part = location.replace(" ", "")
    
    # Thunderstorm part
    if g_threshold == 0 or g_threshold is None:
        thunder_part = "Gew. -"
    else:
        thunder_part = f"Gew.{g_threshold:.0f}%@{t_g_threshold}"
        if g_pmax > g_threshold:
            thunder_part += f"({g_pmax:.0f}%@{t_g_pmax})"
    
    # Rain part
    if r_threshold == 0 or r_threshold is None:
        rain_part = "Regen -"
    else:
        rain_part = f"Regen{r_threshold:.0f}%@{t_r_threshold}"
        if r_pmax > r_threshold:
            rain_part += f"({r_pmax:.0f}%@{t_r_pmax})"
    
    # Rain amount part
    if regen_mm == 0 or regen_mm is None:
        rain_amount_part = "Regen -mm"
    else:
        rain_amount_part = f"Regen{regen_mm:.1f}mm@{t_regen_max}"
    
    # Temperature part
    temp_part = f"Hitze{temp_max:.1f}°C" if temp_max > 0 else "Hitze -"
    
    # Wind parts
    wind_part = f"Wind{wind:.0f}km/h" if wind > 0 else "Wind -"
    wind_gust_part = f"Windböen{wind_max:.0f}km/h" if wind_max > 0 else "Windböen -"
    
    # Thunderstorm next day part
    if g1_next == 0 or g1_next is None:
        thunder_next_part = "Gew.+1 -"
    else:
        thunder_next_part = f"Gew.+1{g1_next:.0f}%"
        if t_g1_next_threshold:
            thunder_next_part += f"@{t_g1_next_threshold}"
    
    # Combine parts (only include non-empty parts)
    parts = [stage_part, "Update:"]
    if thunder_part != "Gew. -":
        parts.append(thunder_part)
    if rain_part != "Regen -":
        parts.append(rain_part)
    if rain_amount_part != "Regen -mm":
        parts.append(rain_amount_part)
    parts.extend([temp_part, wind_part, wind_gust_part, thunder_next_part])
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