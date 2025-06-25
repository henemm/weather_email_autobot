"""
Garmin ShareMap position fetching module.

This module provides functionality to fetch current GPS position
from a public Garmin ShareMap URL.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional
from src.model.datatypes import CurrentPosition


def fetch_sharemap_position(sharemap_url: str) -> Optional[CurrentPosition]:
    """
    Fetch current GPS position from a Garmin ShareMap URL.
    
    Args:
        sharemap_url: The Garmin ShareMap URL (e.g., https://share.garmin.com/PDFCF)
        
    Returns:
        CurrentPosition object with latitude, longitude, timestamp, and source_url,
        or None if no position data is found
        
    Raises:
        Exception: When HTTP request fails
        ValueError: When KML format is invalid
    """
    try:
        # Fetch KML data from ShareMap
        response = requests.get(sharemap_url, timeout=10)
        response.raise_for_status()
        
        # Parse KML XML
        root = ET.fromstring(response.text)
        
        # Extract coordinates and timestamp
        position_data = _extract_position_from_kml(root)
        
        if position_data is None:
            return None
            
        latitude, longitude, timestamp = position_data
        
        return CurrentPosition(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            source_url=sharemap_url
        )
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch ShareMap data: {e}")
    except ET.ParseError as e:
        raise ValueError(f"Invalid KML format: {e}")


def _extract_position_from_kml(root: ET.Element) -> Optional[tuple[float, float, datetime]]:
    """
    Extract position data from KML XML root element.
    
    Args:
        root: XML root element of KML document
        
    Returns:
        Tuple of (latitude, longitude, timestamp) or None if not found
    """
    # Define KML namespace
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    # Find Placemark with coordinates
    placemark = root.find('.//kml:Placemark', namespace)
    if placemark is None:
        return None
    
    # Extract coordinates
    coordinates_elem = placemark.find('.//kml:coordinates', namespace)
    if coordinates_elem is None or coordinates_elem.text is None:
        return None
    
    # Parse coordinates (format: "longitude,latitude,altitude")
    coords_text = coordinates_elem.text.strip()
    coords_parts = coords_text.split(',')
    
    if len(coords_parts) < 2:
        return None
    
    try:
        longitude = float(coords_parts[0])
        latitude = float(coords_parts[1])
    except ValueError:
        return None
    
    # Extract timestamp
    timestamp_elem = placemark.find('.//kml:when', namespace)
    if timestamp_elem is None or timestamp_elem.text is None:
        # Use current time if no timestamp found
        timestamp = datetime.utcnow()
    else:
        try:
            timestamp = datetime.fromisoformat(timestamp_elem.text.replace('Z', '+00:00'))
        except ValueError:
            timestamp = datetime.utcnow()
    
    return latitude, longitude, timestamp 