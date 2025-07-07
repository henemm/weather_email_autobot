#!/usr/bin/env python3
"""
Stage logic for GR20 weather reports.

This module determines the current stage based on the start date
and current date, using etappen.json for stage data.
"""

import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    from utils.logging_setup import get_logger
    logger = get_logger(__name__)
except Exception:
    class NullLogger:
        def info(self, *a, **k): pass
        def warning(self, *a, **k): pass
        def error(self, *a, **k): pass
    logger = NullLogger()


def load_etappen_data(etappen_path: str = "etappen.json") -> List[Dict]:
    """
    Load stage data from etappen.json file.
    
    Args:
        etappen_path: Path to etappen.json file
        
    Returns:
        List of stage dictionaries
        
    Raises:
        FileNotFoundError: If etappen.json not found
        json.JSONDecodeError: If etappen.json is invalid JSON
    """
    try:
        with open(etappen_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Etappen file not found: {etappen_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in etappen file: {e}")


def get_current_stage(config: Dict, etappen_path: str = "etappen.json") -> Optional[Dict]:
    """
    Determine the current stage based on start date and current date.
    
    Args:
        config: Configuration dictionary containing startdatum
        etappen_path: Path to etappen.json file
        
    Returns:
        Current stage dictionary or None if no stages available
        
    Raises:
        ValueError: If startdatum is invalid
    """
    try:
        # Load etappen data
        etappen = load_etappen_data(etappen_path)
        
        if not etappen:
            logger.warning("No stages found in etappen.json")
            return None
        
        # Get start date from config
        startdatum_str = config.get("startdatum")
        if not startdatum_str:
            logger.error("No startdatum found in config")
            return None
        
        # Parse start date
        try:
            start_date = datetime.strptime(startdatum_str, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid startdatum format in config: {startdatum_str}. Expected YYYY-MM-DD") from e
        
        # Get current date
        current_date = date.today()
        
        # Calculate days since start
        days_since_start = (current_date - start_date).days
        
        if days_since_start < 0:
            logger.warning(f"Current date {current_date} is before start date {start_date}")
            return None
        
        # Determine stage index (0-based)
        stage_index = days_since_start
        
        if stage_index >= len(etappen):
            logger.warning(f"No stage available for day {days_since_start + 1} (stage index {stage_index})")
            return None
        
        current_stage = etappen[stage_index]
        logger.info(f"Current stage: {current_stage['name']} (day {days_since_start + 1})")
        
        return current_stage
        
    except Exception as e:
        logger.error(f"Error determining current stage: {e}")
        return None


def get_stage_coordinates(stage: Dict) -> List[Tuple[float, float]]:
    """
    Extract coordinates from a stage dictionary.
    
    Args:
        stage: Stage dictionary from etappen.json
        
    Returns:
        List of (latitude, longitude) tuples
        
    Raises:
        KeyError: If stage doesn't have 'punkte' key
        ValueError: If coordinates are invalid
    """
    if "punkte" not in stage:
        raise KeyError("Stage missing 'punkte' key")
    
    coordinates = []
    for point in stage["punkte"]:
        if "lat" not in point or "lon" not in point:
            raise ValueError(f"Invalid point in stage: {point}")
        
        try:
            lat = float(point["lat"])
            lon = float(point["lon"])
            coordinates.append((lat, lon))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid coordinates in point {point}: {e}") from e
    
    return coordinates


def get_stage_info(config: Dict, etappen_path: str = "etappen.json") -> Optional[Dict]:
    """
    Get comprehensive stage information including coordinates.
    
    Args:
        config: Configuration dictionary
        etappen_path: Path to etappen.json file
        
    Returns:
        Dictionary with stage info including name and coordinates, or None if no stage available
    """
    stage = get_current_stage(config, etappen_path)
    
    if not stage:
        return None
    
    try:
        coordinates = get_stage_coordinates(stage)
        return {
            "name": stage["name"],
            "coordinates": coordinates,
            "stage_data": stage
        }
    except Exception as e:
        logger.error(f"Error extracting stage coordinates: {e}")
        return None


def get_next_stage(config: Dict, etappen_path: str = "etappen.json") -> Optional[Dict]:
    """
    Get the next stage (for evening reports).
    
    Args:
        config: Configuration dictionary
        etappen_path: Path to etappen.json file
        
    Returns:
        Next stage dictionary or None if no next stage available
    """
    try:
        etappen = load_etappen_data(etappen_path)
        
        if not etappen:
            return None
        
        # Get current stage index
        startdatum_str = config.get("startdatum")
        if not startdatum_str:
            return None
        
        start_date = datetime.strptime(startdatum_str, "%Y-%m-%d").date()
        current_date = date.today()
        days_since_start = (current_date - start_date).days
        
        if days_since_start < 0:
            return None
        
        next_stage_index = days_since_start + 1
        
        if next_stage_index >= len(etappen):
            logger.info("No next stage available")
            return None
        
        next_stage = etappen[next_stage_index]
        logger.info(f"Next stage: {next_stage['name']}")
        
        return next_stage
        
    except Exception as e:
        logger.error(f"Error getting next stage: {e}")
        return None


def get_day_after_tomorrow_stage(config: Dict, etappen_path: str = "etappen.json") -> Optional[Dict]:
    """
    Get the stage for the day after tomorrow (for evening reports).
    
    Args:
        config: Configuration dictionary
        etappen_path: Path to etappen.json file
        
    Returns:
        Day after tomorrow stage dictionary or None if not available
    """
    try:
        etappen = load_etappen_data(etappen_path)
        
        if not etappen:
            return None
        
        # Get current stage index
        startdatum_str = config.get("startdatum")
        if not startdatum_str:
            return None
        
        start_date = datetime.strptime(startdatum_str, "%Y-%m-%d").date()
        current_date = date.today()
        days_since_start = (current_date - start_date).days
        
        if days_since_start < 0:
            return None
        
        day_after_tomorrow_index = days_since_start + 2
        
        if day_after_tomorrow_index >= len(etappen):
            logger.info("No day after tomorrow stage available")
            return None
        
        day_after_tomorrow_stage = etappen[day_after_tomorrow_index]
        logger.info(f"Day after tomorrow stage: {day_after_tomorrow_stage['name']}")
        
        return day_after_tomorrow_stage
        
    except Exception as e:
        logger.error(f"Error getting day after tomorrow stage: {e}")
        return None 