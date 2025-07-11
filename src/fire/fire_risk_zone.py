#!/usr/bin/env python3
"""
Fire Risk Zone - Official zone-based fire risk warnings

This module provides fire risk warnings based on official French fire prevention
zones, using the official API and zone polygons.
"""

import requests
from datetime import date
from typing import Dict, Optional, Any
import logging
import json

from .fire_zone_mapper import FireZoneMapper

logger = logging.getLogger(__name__)


class FireRiskZone:
    """Fire risk warnings based on official zones."""
    
    def __init__(self):
        """Initialize the fire risk zone handler."""
        self.zone_mapper = FireZoneMapper()
        self.api_url = "https://www.risque-prevention-incendie.fr/static/20/data/zm.json"
        
    def fetch_fire_risk_data(self, report_date: Optional[date] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch fire risk data from the official API.
        
        Args:
            report_date: Date for the report (defaults to today)
            
        Returns:
            Dictionary with fire risk data or None if fetch fails
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched fire risk data for {len(data.get('zm', {}))} zones")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch fire risk data: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse fire risk data: {e}")
            return None
    
    def get_zone_fire_alert_for_location(self, lat: float, lon: float, report_date: Optional[date] = None) -> Optional[Dict[str, Any]]:
        """
        Get fire risk alert for a specific location.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            report_date: Date for the report (defaults to today)
            
        Returns:
            Dictionary with fire risk alert information or None if not found
        """
        # Get zone information for coordinates
        zone_info = self.zone_mapper.get_zone_for_coordinates(lat, lon)
        if not zone_info:
            logger.warning(f"No fire risk zone found for coordinates ({lat}, {lon})")
            return None
            
        # Fetch current fire risk data
        api_data = self.fetch_fire_risk_data(report_date)
        if not api_data or 'zm' not in api_data:
            logger.warning("No fire risk data available from API")
            return None
            
        # Get fire risk level for the zone
        zone_number = zone_info['zone_number']
        fire_level = api_data['zm'].get(zone_number)
        
        if fire_level is None:
            logger.warning(f"No fire risk level found for zone {zone_number}")
            return None
            
        return {
            'zone_number': zone_number,
            'zone_name': zone_info['zone_name'],
            'level': fire_level,
            'description': zone_info['description']
        }
    
    def format_fire_warnings(self, lat: float, lon: float, report_date: Optional[date] = None) -> str:
        """
        Format fire risk warnings for email/SMS output.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            report_date: Date for the report (defaults to today)
            
        Returns:
            Formatted warning string or empty string if no warning
        """
        alert = self.get_zone_fire_alert_for_location(lat, lon, report_date)
        
        if not alert:
            return ""
            
        level = alert['level']
        
        # Only show warnings for level 2 or higher (as per email_format.mdc)
        if level < 2:
            return ""
            
        # Map level to warning format
        if level == 2:
            return "WARN Waldbrand"
        elif level == 3:
            return "HIGH Waldbrand"
        elif level >= 4:
            return "MAX Waldbrand"
        else:
            return ""
    
    def _get_level_description(self, level: int) -> str:
        """
        Get human-readable description for fire risk level.
        
        Args:
            level: Fire risk level (0-4)
            
        Returns:
            Description string
        """
        descriptions = {
            0: "Faible",
            1: "Modéré", 
            2: "Élevé",
            3: "Très élevé",
            4: "Exceptionnel"
        }
        return descriptions.get(level, "Inconnu")
    
    def _level_to_warning(self, level: int) -> str:
        """
        Convert fire risk level to warning string.
        
        Args:
            level: Fire risk level (0-4)
            
        Returns:
            Warning string
        """
        if level < 2:
            return ""
        elif level == 2:
            return "WARN"
        elif level == 3:
            return "HIGH"
        elif level >= 4:
            return "MAX"
        else:
            return "" 