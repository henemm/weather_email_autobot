"""
GR20 Weather Report Scheduler.

This module handles the scheduling and logic for GR20 weather reports,
including scheduled morning/evening reports and dynamic reports based on
weather risk changes.
"""

import json
import os
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

try:
    from utils.logging_setup import get_logger
except ImportError:
    try:
        from src.utils.logging_setup import get_logger
    except ImportError:
        from ..utils.logging_setup import get_logger

logger = get_logger(__name__)


@dataclass
class ReportState:
    """Represents the current report state for tracking."""
    last_scheduled_report: Optional[datetime] = None
    last_dynamic_report: Optional[datetime] = None
    daily_dynamic_report_count: int = 0
    last_risk_value: float = 0.0
    last_report_date: Optional[str] = None


class ReportScheduler:
    """
    Manages GR20 weather report scheduling and state tracking.
    
    This class handles both scheduled reports (morning/evening) and dynamic
    reports based on weather risk changes.
    """
    
    def __init__(self, state_file: str, config: Dict[str, Any]):
        """
        Initialize the report scheduler.
        
        Args:
            state_file: Path to JSON file for state persistence
            config: Configuration dictionary with scheduling parameters
        """
        self.state_file = state_file
        self.config = config
        self.current_state = self._load_state()
        logger.info(f"Report scheduler initialized with state file: {state_file}")
    
    def _load_state(self) -> ReportState:
        """
        Load report state from JSON file.
        
        Returns:
            ReportState object with default values if file doesn't exist
        """
        if not os.path.exists(self.state_file):
            logger.info(f"State file {self.state_file} does not exist, creating new state")
            return ReportState()
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            logger.debug(f"Loaded state from {self.state_file}: {data}")
            
            return ReportState(
                last_scheduled_report=datetime.fromisoformat(data["last_scheduled_report"]) if data.get("last_scheduled_report") else None,
                last_dynamic_report=datetime.fromisoformat(data["last_dynamic_report"]) if data.get("last_dynamic_report") else None,
                daily_dynamic_report_count=data.get("daily_dynamic_report_count", 0),
                last_risk_value=data.get("last_risk_value", 0.0),
                last_report_date=data.get("last_report_date")
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If file is corrupted, start fresh
            logger.warning(f"Failed to load state from {self.state_file}: {e}, creating new state")
            return ReportState()
    
    def _save_state(self) -> None:
        """Save current report state to JSON file."""
        data = {
            "last_scheduled_report": self.current_state.last_scheduled_report.isoformat() if self.current_state.last_scheduled_report else None,
            "last_dynamic_report": self.current_state.last_dynamic_report.isoformat() if self.current_state.last_dynamic_report else None,
            "daily_dynamic_report_count": self.current_state.daily_dynamic_report_count,
            "last_risk_value": self.current_state.last_risk_value,
            "last_report_date": self.current_state.last_report_date
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"State saved to {self.state_file}: {data}")
        except Exception as e:
            logger.error(f"Failed to save state to {self.state_file}: {e}")
    
    def should_send_report(self, current_time: datetime, current_risk: float) -> bool:
        """
        Determine if a report should be sent based on current time and risk.
        
        Args:
            current_time: Current datetime
            current_risk: Current weather risk value (0.0 to 1.0)
            
        Returns:
            True if report should be sent, False otherwise
        """
        logger.debug(f"Checking if report should be sent at {current_time}, risk: {current_risk:.2f}")
        
        # Check for scheduled report
        if should_send_scheduled_report(current_time, self.config):
            logger.info(f"Scheduled report should be sent at {current_time}")
            return True
        
        # Check for dynamic report
        if should_send_dynamic_report(
            current_risk,
            self.current_state.last_risk_value,
            self.current_state.last_dynamic_report,
            self.current_state.daily_dynamic_report_count,
            self.config
        ):
            logger.info(f"Dynamic report should be sent at {current_time}, risk change: {current_risk - self.current_state.last_risk_value:.2f}")
            return True
        
        logger.debug(f"No report needed at {current_time}")
        return False
    
    def update_state_after_report(self, report_time: datetime, risk_value: float, is_dynamic: bool = False) -> None:
        """
        Update state after sending a report.
        
        Args:
            report_time: Time when report was sent
            risk_value: Risk value at time of report
            is_dynamic: Whether this was a dynamic report
        """
        current_date = report_time.strftime("%Y-%m-%d")
        
        # Reset daily counter if it's a new day
        if self.current_state.last_report_date != current_date:
            logger.info(f"New day detected: {current_date}, resetting daily dynamic report count")
            self.current_state.daily_dynamic_report_count = 0
            self.current_state.last_report_date = current_date
        
        if is_dynamic:
            self.current_state.last_dynamic_report = report_time
            self.current_state.daily_dynamic_report_count += 1
            logger.info(f"Updated state after dynamic report: count={self.current_state.daily_dynamic_report_count}")
        else:
            self.current_state.last_scheduled_report = report_time
            logger.info(f"Updated state after scheduled report at {report_time}")
        
        self.current_state.last_risk_value = risk_value
        self._save_state()
    
    def get_report_type(self, current_time: datetime, current_risk: float) -> str:
        """
        Determine the type of report to send.
        
        Args:
            current_time: Current datetime
            current_risk: Current weather risk value
            
        Returns:
            "scheduled" or "dynamic"
        """
        if should_send_scheduled_report(current_time, self.config):
            logger.debug(f"Report type: scheduled at {current_time}")
            return "scheduled"
        else:
            logger.debug(f"Report type: dynamic at {current_time}")
            return "dynamic"


def should_send_scheduled_report(current_time: datetime, config: Dict[str, Any]) -> bool:
    """
    Check if a scheduled report should be sent at the current time.
    
    Args:
        current_time: Current datetime
        config: Configuration dictionary with send_schedule
        
    Returns:
        True if scheduled report should be sent, False otherwise
    """
    schedule_config = config.get("send_schedule", {})
    morning_time = schedule_config.get("morning_time", "04:30")
    evening_time = schedule_config.get("evening_time", "19:00")
    
    # Parse times
    morning_hour, morning_minute = map(int, morning_time.split(":"))
    evening_hour, evening_minute = map(int, evening_time.split(":"))
    
    # Check if current time matches scheduled times
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    is_scheduled_time = (
        (current_hour == morning_hour and current_minute == morning_minute) or
        (current_hour == evening_hour and current_minute == evening_minute)
    )
    
    if is_scheduled_time:
        logger.info(f"Scheduled report time matched: {current_time.strftime('%H:%M')}")
    
    return is_scheduled_time


def should_send_dynamic_report(
    current_risk: float,
    previous_risk: float,
    last_report_time: Optional[datetime],
    daily_report_count: int,
    config: Dict[str, Any]
) -> bool:
    """
    Check if a dynamic report should be sent based on risk changes.
    
    Args:
        current_risk: Current weather risk value
        previous_risk: Previous weather risk value
        last_report_time: Time of last dynamic report
        daily_report_count: Number of dynamic reports sent today
        config: Configuration dictionary with dynamic report settings
        
    Returns:
        True if dynamic report should be sent, False otherwise
    """
    # Use delta_thresholds for dynamic report triggering
    delta_thresholds = config.get("delta_thresholds", {})
    min_interval = config.get("min_interval_min", 60)
    max_daily = config.get("max_daily_reports", 3)
    
    # Calculate risk change
    risk_change = abs(current_risk - previous_risk)
    
    # Use a simple threshold for risk change (0.3 = 30% change)
    risk_threshold = 0.3
    
    # Check if risk change exceeds threshold
    if risk_change < risk_threshold:
        logger.debug(f"Risk change {risk_change:.2f} below threshold {risk_threshold}")
        return False
    
    # Check if enough time has passed since last report
    if last_report_time:
        time_since_last = (datetime.now() - last_report_time).total_seconds() / 60
        if time_since_last < min_interval:
            logger.debug(f"Time since last report {time_since_last:.1f}min below minimum {min_interval}min")
            return False
    
    # Check daily limit
    if daily_report_count >= max_daily:
        logger.debug(f"Daily report count {daily_report_count} at maximum {max_daily}")
        return False
    
    logger.info(f"Dynamic report conditions met: risk change {risk_change:.2f}, daily count {daily_report_count}")
    return True


def get_nearest_stage_location(latitude: float, longitude: float, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Find the nearest GR20 stage location to given coordinates.
    
    Args:
        latitude: Current latitude
        longitude: Current longitude
        config: Configuration dictionary with gr20_stages
        
    Returns:
        Dictionary with stage information or None if no stages configured
    """
    stages = config.get("gr20_stages", [])
    if not stages:
        return None
    
    nearest_stage = None
    min_distance = float('inf')
    
    for stage in stages:
        stage_lat, stage_lon = stage["coordinates"]
        distance = _calculate_distance(latitude, longitude, stage_lat, stage_lon)
        
        if distance < min_distance:
            min_distance = distance
            nearest_stage = stage
    
    return nearest_stage


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1: First latitude
        lon1: First longitude
        lat2: Second latitude
        lon2: Second longitude
        
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in kilometers
    earth_radius = 6371
    
    return earth_radius * c


def get_weather_model_for_report(current_time: datetime, config: Dict[str, Any]) -> str:
    """
    Determine the appropriate weather model based on report type and time.
    
    Args:
        current_time: Current datetime
        config: Configuration dictionary
        
    Returns:
        str: Recommended weather model name
    """
    # Determine report type
    if should_send_scheduled_report(current_time, config):
        # Check if it's morning or evening
        schedule_config = config.get("send_schedule", {})
        morning_time = schedule_config.get("morning_time", "04:30")
        evening_time = schedule_config.get("evening_time", "19:00")
        
        morning_hour, morning_minute = map(int, morning_time.split(":"))
        evening_hour, evening_minute = map(int, evening_time.split(":"))
        
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        if current_hour == morning_hour and current_minute == morning_minute:
            report_type = "morning"
        elif current_hour == evening_hour and current_minute == evening_minute:
            report_type = "evening"
        else:
            # Fallback to morning for scheduled reports
            report_type = "morning"
    else:
        # Dynamic report
        report_type = "dynamic"
    
    # With the new meteofrance-api architecture, we always use meteofrance-api
    # as the primary source with open-meteo as fallback
    logger.info(f"Using meteofrance-api for {report_type} report")
    return "meteofrance-api" 