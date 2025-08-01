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
        # Try multiple possible API endpoints
        self.api_urls = [
            "https://www.risque-prevention-incendie.fr/static/20/data/zm.json",
            "https://www.risque-prevention-incendie.fr/static/4/data/zm.json",
            "https://www.risque-prevention-incendie.fr/static/data/zm.json",
            "https://www.risque-prevention-incendie.fr/api/zones",
            "https://www.risque-prevention-incendie.fr/data/zones.json"
        ]
        
    def fetch_fire_risk_data(self, report_date: Optional[date] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch fire risk data from the official API.
        
        Args:
            report_date: Date for the report (defaults to today)
            
        Returns:
            Dictionary with fire risk data or None if fetch fails
        """
        for url in self.api_urls:
            try:
                logger.info(f"Trying fire risk API URL: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Successfully fetched fire risk data from {url} for {len(data.get('zm', {}))} zones")
                return data
                
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch fire risk data from {url}: {e}")
                continue
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse fire risk data from {url}: {e}")
                continue
        
        logger.error("All fire risk API endpoints failed")
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
            Formatted warning string
        """
        alert = self.get_zone_fire_alert_for_location(lat, lon, report_date)
        if not alert:
            return "Keine Waldbrand-Warnung verfügbar"
        
        level = alert['level']
        zone_name = alert['zone_name']
        
        warning_text = self._level_to_warning(level)
        return f"{warning_text} in Zone {alert['zone_number']} ({zone_name})"
    
    def _get_level_description(self, level: int) -> str:
        """Get human-readable description for fire risk level."""
        descriptions = {
            1: "Niedrig",
            2: "Mittel", 
            3: "Hoch",
            4: "Sehr hoch",
            5: "Extrem"
        }
        return descriptions.get(level, "Unbekannt")
    
    def _level_to_warning(self, level: int) -> str:
        """Convert fire risk level to warning text."""
        if level <= 2:
            return f"Waldbrand-Risiko: {self._get_level_description(level)}"
        elif level == 3:
            return f"⚠️ Waldbrand-Risiko: {self._get_level_description(level)}"
        elif level == 4:
            return f"🚨 Waldbrand-Risiko: {self._get_level_description(level)}"
        else:
            return f"🔥 Waldbrand-Risiko: {self._get_level_description(level)}" 