"""
Warning state tracking module.

This module provides functionality to track and persist weather warning states
to detect significant changes that require new warnings.
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class WarningState:
    """Represents the current warning state for comparison."""
    last_check: datetime
    max_thunderstorm_probability: float
    max_precipitation: float
    max_wind_speed: float
    max_temperature: float
    max_cloud_cover: float
    last_warning_time: Optional[datetime] = None


class WarningStateTracker:
    """
    Tracks warning state changes and persists state to JSON file.
    
    This class manages the comparison between current weather analysis
    and previously stored warning state to detect significant changes.
    """
    
    def __init__(self, state_file: str):
        """
        Initialize the state tracker.
        
        Args:
            state_file: Path to JSON file for state persistence
        """
        self.state_file = state_file
        self.current_state = self._load_state()
    
    def _load_state(self) -> Optional[WarningState]:
        """
        Load warning state from JSON file.
        
        Returns:
            WarningState object or None if file doesn't exist
        """
        if not os.path.exists(self.state_file):
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            return WarningState(
                last_check=datetime.fromisoformat(data["last_check"]),
                max_thunderstorm_probability=data["max_thunderstorm_probability"],
                max_precipitation=data["max_precipitation"],
                max_wind_speed=data["max_wind_speed"],
                max_temperature=data["max_temperature"],
                max_cloud_cover=data["max_cloud_cover"],
                last_warning_time=datetime.fromisoformat(data["last_warning_time"]) if data.get("last_warning_time") else None
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If file is corrupted, start fresh
            return None
    
    def save_state(self, state: WarningState) -> None:
        """
        Save warning state to JSON file.
        
        Args:
            state: WarningState object to save
        """
        data = {
            "last_check": state.last_check.isoformat(),
            "max_thunderstorm_probability": state.max_thunderstorm_probability,
            "max_precipitation": state.max_precipitation,
            "max_wind_speed": state.max_wind_speed,
            "max_temperature": state.max_temperature,
            "max_cloud_cover": state.max_cloud_cover,
            "last_warning_time": state.last_warning_time.isoformat() if state.last_warning_time else None
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.current_state = state
    
    def has_significant_change(self, analysis: Any, config: Dict[str, Any]) -> bool:
        """
        Check if weather analysis shows significant change from previous state.
        
        Args:
            analysis: WeatherAnalysis object with current weather data
            config: Configuration dictionary with threshold values
            
        Returns:
            True if significant change detected, False otherwise
        """
        # If no previous state, any analysis is significant
        if self.current_state is None:
            return True
        
        # Get thresholds from config with defaults
        thresholds = config.get("thresholds", {})
        delta_thresholds = thresholds.get("delta_thresholds", {})
        delta_thunderstorm = delta_thresholds.get("thunderstorm_probability", 20.0)
        delta_precipitation = delta_thresholds.get("rain_probability", 30.0)
        delta_wind = delta_thresholds.get("wind_speed", 10.0)
        delta_temperature = delta_thresholds.get("temperature", 2.0)
        
        # Check for significant changes
        thunderstorm_change = (
            analysis.max_thunderstorm_probability - self.current_state.max_thunderstorm_probability
        ) >= delta_thunderstorm
        
        precipitation_change = (
            analysis.max_precipitation - self.current_state.max_precipitation
        ) >= delta_precipitation
        
        wind_change = (
            analysis.max_wind_speed - self.current_state.max_wind_speed
        ) >= delta_wind
        
        temperature_change = (
            analysis.max_temperature - self.current_state.max_temperature
        ) >= delta_temperature
        
        return any([
            thunderstorm_change,
            precipitation_change,
            wind_change,
            temperature_change
        ])
    
    def update_state(self, analysis: Any) -> None:
        """
        Update current state with new analysis data.
        
        Args:
            analysis: WeatherAnalysis object with current weather data
        """
        new_state = WarningState(
            last_check=datetime.now(),
            max_thunderstorm_probability=analysis.max_thunderstorm_probability or 0.0,
            max_precipitation=analysis.max_precipitation,
            max_wind_speed=analysis.max_wind_speed,
            max_temperature=analysis.max_temperature,
            max_cloud_cover=analysis.max_cloud_cover,
            last_warning_time=self.current_state.last_warning_time if self.current_state else None
        )
        
        self.save_state(new_state)
    
    def set_warning_time(self, warning_time: datetime) -> None:
        """
        Update the last warning time.
        
        Args:
            warning_time: Timestamp of the last warning
        """
        if self.current_state:
            updated_state = WarningState(
                last_check=self.current_state.last_check,
                max_thunderstorm_probability=self.current_state.max_thunderstorm_probability,
                max_precipitation=self.current_state.max_precipitation,
                max_wind_speed=self.current_state.max_wind_speed,
                max_temperature=self.current_state.max_temperature,
                max_cloud_cover=self.current_state.max_cloud_cover,
                last_warning_time=warning_time
            )
            self.save_state(updated_state) 