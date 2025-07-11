#!/usr/bin/env python3
"""
Fire Zone Mapper - Map coordinates to official fire risk zones

This module provides functionality to determine which fire risk zone
a given coordinate belongs to, using the official zone polygons.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any
import geopandas as gpd
from shapely.geometry import Point


class FireZoneMapper:
    """Map coordinates to official fire risk zones."""
    
    def __init__(self, geojson_path: str = "data/fire_zones.geojson"):
        """
        Initialize the zone mapper.
        
        Args:
            geojson_path: Path to the official fire zones GeoJSON file
        """
        self.geojson_path = Path(geojson_path)
        self.gdf = None
        self._load_zones()
        
        # Official zone number to name mapping based on screenshots and official map
        # This mapping is created manually by comparing zone numbers with the official map
        self.ZONE_NUMBER_TO_NAME = {
            "201": "BALAGNE",
            "202": "REGION DE CALVI", 
            "203": "REGION DE CALVI",
            "204": "REGION DE CALVI",
            "205": "REGION DE CALVI",
            "206": "REGION DE CALVI",
            "207": "REGION DE CALVI",
            "208": "REGION DE CALVI", 
            "209": "REGION DE CALVI",
            "211": "REGION DE CALVI",
            "212": "REGION DE CALVI",
            "213": "BALAGNE",
            "214": "REGION DE CONCA",
            "215": "EXTREME SUD",
            "216": "EXTREME SUD",
            "217": "EXTREME SUD",
            "218": "EXTREME SUD"
        }
        
    def _load_zones(self) -> None:
        """Load zone polygons from GeoJSON file."""
        if not self.geojson_path.exists():
            raise FileNotFoundError(f"Fire zones GeoJSON not found: {self.geojson_path}")
            
        self.gdf = gpd.read_file(self.geojson_path)
        
    def get_zone_for_coordinates(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """
        Get zone information for given coordinates.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            
        Returns:
            Dictionary with zone information or None if not found
        """
        if self.gdf is None:
            return None
            
        point = Point(lon, lat)
        
        for idx, row in self.gdf.iterrows():
            # Access columns directly, not as 'properties'
            zone_number = row['numero_zon']
            zone_name = self.ZONE_NUMBER_TO_NAME.get(zone_number, f"Zone {zone_number}")
            if row.geometry.contains(point):
                return {
                    'zone_number': zone_number,
                    'zone_name': zone_name,
                    'description': row['Zonage_Feu'],
                    'level': row['level']
                }
                
        return None
    
    def get_all_zones(self) -> Dict[str, str]:
        """
        Get all available zones with their names.
        
        Returns:
            Dictionary mapping zone numbers to zone names
        """
        return self.ZONE_NUMBER_TO_NAME.copy()
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate that coordinates are within any fire risk zone.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            
        Returns:
            True if coordinates are within a zone, False otherwise
        """
        return self.get_zone_for_coordinates(lat, lon) is not None 