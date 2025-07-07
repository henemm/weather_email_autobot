"""
Fire risk zone support module (zone-based only).

This module provides integration with the French fire risk prevention system
and fetches/processes forest fire warnings for Corsica using ZONE-LEVEL (zm) data only.

Massif-based logic is deprecated and not used. All fire risk logic is based on zones (zm_key).
"""

import requests
from datetime import date
from typing import Optional, Dict, Any
import logging
from .zone_polygon_mapper import ZonePolygonMapper

logger = logging.getLogger(__name__)

class FireRiskZone:
    """
    Fetch and process fire risk data from French prevention site (zone-based only).
    All fire risk logic is based on zones (zm_key). Massif logic is deprecated and not used.
    """
    def __init__(self, zone_geojson_path: str = "data/digital_massifs.geojson"):
        self.base_url = "https://www.risque-prevention-incendie.fr/static/20/import_data"
        self.zone_mapper = ZonePolygonMapper(zone_geojson_path)

    def fetch_fire_risk_data(self, target_date: Optional[date] = None) -> dict:
        if target_date is None:
            target_date = date.today()
        date_str = target_date.strftime("%Y%m%d")
        url = f"{self.base_url}/{date_str}.json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch fire risk data: {e}")
            return {}

    def get_zone_fire_alert_for_location(self, lat: float, lon: float, target_date: Optional[date] = None) -> dict:
        zone_info = self.zone_mapper.get_zone_for_point(lat, lon)
        if not zone_info or not zone_info.get('name'):
            return {}
        zone_name = zone_info['name']
        zm_key = zone_info.get('zm_key') or zone_info.get('id') or zone_info.get('zm')
        data = self.fetch_fire_risk_data(target_date)
        zm = data.get('zm', {})
        level = None
        if zm_key and str(zm_key) in zm:
            level = zm[str(zm_key)]
        # Debug print for manual verification
        print(f"[DEBUG] Zone: {zone_name}, zm_key: {zm_key}, Level: {level}")
        if level is not None:
            return {
                'zone_name': zone_name,
                'level': level,
                'zm_key': zm_key
            }
        return {}

    def _level_to_warning(self, level: int) -> str:
        if level >= 5:
            return "MAX"
        elif level >= 4:
            return "HIGH"
        elif level >= 3:
            return "WARN"
        else:
            return ""

    def format_fire_warnings(self, lat: float, lon: float, target_date: Optional[date] = None) -> str:
        zone_alert = self.get_zone_fire_alert_for_location(lat, lon, target_date)
        # Debug-Ausgabe für jede Abfrage
        print(f"[FIRE-RISK-DEBUG] Koordinate: {lat:.5f}, {lon:.5f} | Zone: {zone_alert.get('zone_name', '-') if zone_alert else '-'} | zm_key: {zone_alert.get('zm_key', '-') if zone_alert else '-'} | Level: {zone_alert.get('level', '-') if zone_alert else '-'}")
        # Schwelle: ab Level 3
        if not zone_alert or zone_alert.get('level', 0) < 3:
            return ""
        warning_level = self._level_to_warning(zone_alert['level'])
        if not warning_level:
            return ""
        return f"{warning_level} Waldbrand" 