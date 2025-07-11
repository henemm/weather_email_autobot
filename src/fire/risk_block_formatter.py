"""
Risk block formatter for GR20 weather reports.

This module provides functions to generate compact risk blocks containing
zone and massif IDs for fire risk warnings and access restrictions.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import re
import json

logger = logging.getLogger(__name__)


@dataclass
class ZoneInfo:
    """Information about a fire risk zone."""
    id: int
    name: str
    risk_level: int  # 1=low, 2=medium, 3=high, 4=very high


@dataclass
class MassifInfo:
    """Information about a massif with access restrictions."""
    id: int
    name: str
    is_restricted: bool


# GR20-relevant zones (from spatial analysis)
GR20_ZONES = {
    217: ZoneInfo(217, "BALAGNE", 0),
    208: ZoneInfo(208, "REGION DE CONCA", 0),
    209: ZoneInfo(209, "COTE DES NACRES", 0),
    216: ZoneInfo(216, "MONTI", 0),
    206: ZoneInfo(206, "MONTAGNE", 0),
    205: ZoneInfo(205, "MOYENNE MONTAGNE SUD", 0)
}

# GR20-relevant massifs (from website table)
GR20_MASSIFS = {
    1: MassifInfo(1, "AGRIATES OUEST", False),
    29: MassifInfo(29, "AGRIATES EST", False),
    3: MassifInfo(3, "BONIFATO", False),
    4: MassifInfo(4, "TARTAGINE-MELAJA", False),
    5: MassifInfo(5, "FANGO", False),
    6: MassifInfo(6, "ASCO", False),
    9: MassifInfo(9, "VALDU-NIELLU ALBERTACCE", False),
    10: MassifInfo(10, "RESTONICA-TAVIGNANO", False),
    16: MassifInfo(16, "VIZZAVONA", False),
    24: MassifInfo(24, "BAVELLA", False),
    25: MassifInfo(25, "ZONZA", False),
    26: MassifInfo(26, "CAVU LIVIU", False),
    27: MassifInfo(27, "OSPEDALE", False),
    28: MassifInfo(28, "CAGNA", False)
}


def get_zone_risk_levels(latitude: float, longitude: float) -> Dict[int, int]:
    """
    Get current risk levels for GR20-relevant zones by parsing the daily JSON data.
    
    Args:
        latitude: Latitude coordinate (not used in current implementation)
        longitude: Longitude coordinate (not used in current implementation)
        
    Returns:
        Dictionary mapping zone IDs to risk levels (1=low, 2=medium, 3=high, 4=very high)
    """
    import datetime
    
    # Get today's date in YYYYMMDD format
    today = datetime.datetime.now().strftime("%Y%m%d")
    url = f"https://www.risque-prevention-incendie.fr/static/20/import_data/{today}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        zone_risks = {}
        
        # Extract zone risk levels from the "zm" section
        if "zm" in data:
            for zone_id_str, risk_level in data["zm"].items():
                zone_id = int(zone_id_str)
                if zone_id in GR20_ZONES and risk_level >= 2:  # Only zones with risk level >= 2
                    zone_risks[zone_id] = risk_level
                    logger.info(f"Found GR20 zone {zone_id} with level {risk_level}")
        
        return zone_risks
        
    except Exception as e:
        logger.error(f"Error fetching zone risk levels: {e}")
        return {}


def _parse_geojson_zones(geojson_data: List[Dict]) -> Dict[int, int]:
    """Parse zone risk levels from GeoJSON data."""
    zone_risks = {}
    for feature in geojson_data:
        if feature.get("type") == "Feature":
            properties = feature.get("properties", {})
            zone_id = properties.get("id") or properties.get("zone_id")
            risk_level = properties.get("level") or properties.get("risk_level")
            if zone_id and risk_level and zone_id in GR20_ZONES:
                zone_risks[zone_id] = int(risk_level)
    return zone_risks


def _parse_zone_objects(zone_data: List[Dict]) -> Dict[int, int]:
    """Parse zone risk levels from JavaScript zone objects."""
    zone_risks = {}
    for zone in zone_data:
        zone_id = zone.get("id") or zone.get("zone_id")
        risk_level = zone.get("level") or zone.get("risk_level")
        if zone_id and risk_level and zone_id in GR20_ZONES:
            zone_risks[zone_id] = int(risk_level)
    return zone_risks


def _parse_zone_css_classes(content: str) -> Dict[int, int]:
    """Parse zone risk levels from CSS classes or data attributes."""
    zone_risks = {}
    
    # Look for zone elements with risk level classes
    for zone_id in GR20_ZONES.keys():
        # Pattern for elements with zone ID and risk level
        patterns = [
            rf'data-zone["\']?\s*=\s*["\']?{zone_id}["\']?.*?class["\']?\s*=\s*["\']?[^"\']*?(?:high|medium|low|very-high)[^"\']*?["\']?',
            rf'id["\']?\s*=\s*["\']?zone-{zone_id}["\']?.*?class["\']?\s*=\s*["\']?[^"\']*?(?:high|medium|low|very-high)[^"\']*?["\']?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                # Determine risk level from CSS class
                class_text = match.group(0).lower()
                if "very-high" in class_text or "veryhigh" in class_text:
                    zone_risks[zone_id] = 4
                elif "high" in class_text:
                    zone_risks[zone_id] = 3
                elif "medium" in class_text:
                    zone_risks[zone_id] = 2
                elif "low" in class_text:
                    zone_risks[zone_id] = 1
                break
    
    return zone_risks


def get_massif_restrictions() -> List[int]:
    """
    Get list of massif IDs that are currently restricted by parsing the daily JSON data.
    Returns:
        List of massif IDs with access restrictions (level >= 2)
    """
    import datetime
    
    # Get today's date in YYYYMMDD format
    today = datetime.datetime.now().strftime("%Y%m%d")
    url = f"https://www.risque-prevention-incendie.fr/static/20/import_data/{today}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        restricted_ids = []
        
        # Extract massif restrictions from the "massifs" section
        if "massifs" in data:
            for massif_id_str, massif_data in data["massifs"].items():
                massif_id = int(massif_id_str)
                if massif_id in GR20_MASSIFS:
                    # massif_data is [level, procedure] where procedure = 1 means actually restricted
                    if len(massif_data) >= 2 and massif_data[1] == 1:
                        restricted_ids.append(massif_id)
                        logger.info(f"Found GR20 massif {massif_id} with procedure {massif_data[1]} (restricted)")
        
        return restricted_ids
        
    except Exception as e:
        logger.error(f"Error fetching massif restrictions: {e}")
        return []


def format_risk_block(latitude: float, longitude: float) -> Optional[str]:
    """
    Generate a compact risk block string for weather reports.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Compact risk block string (e.g., "Z:HIGH204,208 MAX209 M:3,5,9")
        or None if no relevant risks
    """
    try:
        # Get current risk levels for zones
        zone_risks = get_zone_risk_levels(latitude, longitude)
        
        # Get current massif restrictions
        restricted_massifs = get_massif_restrictions()
        
        # Build zone part (only zones with risk level >= 2)
        zone_parts = []
        high_risk_zones = []
        max_risk_zones = []
        
        for zone_id, risk_level in zone_risks.items():
            if zone_id in GR20_ZONES and risk_level >= 2:
                if risk_level == 4:  # Very high risk
                    max_risk_zones.append(str(zone_id))
                else:  # High risk (level 2-3)
                    high_risk_zones.append(str(zone_id))
        
        # Build zone string
        if high_risk_zones:
            zone_parts.append(f"HIGH{','.join(high_risk_zones)}")
        if max_risk_zones:
            zone_parts.append(f"MAX{','.join(max_risk_zones)}")
        
        # Build massif part (only restricted massifs)
        massif_parts = []
        if restricted_massifs:
            massif_ids = [str(mid) for mid in restricted_massifs if mid in GR20_MASSIFS]
            if massif_ids:
                massif_parts.append(f"M:{','.join(massif_ids)}")
        
        # Combine parts
        if not zone_parts and not massif_parts:
            return None  # No relevant risks
        
        result_parts = []
        if zone_parts:
            result_parts.append(f"Z:{' '.join(zone_parts)}")
        if massif_parts:
            result_parts.extend(massif_parts)
        
        return " ".join(result_parts)
        
    except Exception as e:
        logger.error(f"Error generating risk block: {e}")
        return None


def get_zone_name(zone_id: int) -> Optional[str]:
    """Get zone name by ID."""
    zone = GR20_ZONES.get(zone_id)
    return zone.name if zone else None


def get_massif_name(massif_id: int) -> Optional[str]:
    """Get massif name by ID."""
    massif = GR20_MASSIFS.get(massif_id)
    return massif.name if massif else None


def get_all_gr20_zone_ids() -> List[int]:
    """Get all GR20-relevant zone IDs."""
    return list(GR20_ZONES.keys())


def get_all_gr20_massif_ids() -> List[int]:
    """Get all GR20-relevant massif IDs."""
    return list(GR20_MASSIFS.keys()) 