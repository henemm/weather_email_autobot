"""
Department mapping module for Météo-France warning API.

This module provides functionality to convert GEO coordinates to French department codes
required by the Météo-France get_warning_full() API.
"""

import requests
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DepartmentMapper:
    """
    Maps GEO coordinates to French department codes for Météo-France warning API.
    """
    
    # French department codes mapping for all of France
    # This is a comprehensive mapping for French departments
    DEPARTMENT_MAPPING = {
        # Corsica (Corse)
        "2A": "Corse-du-Sud",  # South Corsica
        "2B": "Haute-Corse",   # Upper Corsica
        
        # Southern France (Provence-Alpes-Côte d'Azur)
        "06": "Alpes-Maritimes",  # Nice area
        "83": "Var",              # Toulon area
        "13": "Bouches-du-Rhône", # Marseille area
        "04": "Alpes-de-Haute-Provence",
        "05": "Hautes-Alpes",
        "84": "Vaucluse",
        
        # Occitanie (Southern France)
        "11": "Aude",
        "30": "Gard",
        "34": "Hérault",
        "48": "Lozère",
        "66": "Pyrénées-Orientales",
        "09": "Ariège",
        "12": "Aveyron",
        "31": "Haute-Garonne",
        "32": "Gers",
        "46": "Lot",
        "65": "Hautes-Pyrénées",
        "81": "Tarn",
        "82": "Tarn-et-Garonne",
        
        # Nouvelle-Aquitaine
        "16": "Charente",
        "17": "Charente-Maritime",
        "19": "Corrèze",
        "23": "Creuse",
        "24": "Dordogne",
        "33": "Gironde",
        "40": "Landes",
        "47": "Lot-et-Garonne",
        "64": "Pyrénées-Atlantiques",
        "79": "Deux-Sèvres",
        "86": "Vienne",
        "87": "Haute-Vienne",
        
        # Other regions as needed
        "75": "Paris",
        "92": "Hauts-de-Seine",
        "93": "Seine-Saint-Denis",
        "94": "Val-de-Marne",
    }
    
    def __init__(self):
        """Initialize the department mapper."""
        pass
    
    def get_department_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """
        Get French department code from GEO coordinates.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            
        Returns:
            Optional[str]: Department code (e.g., "2B" for Haute-Corse) or None if not found
        """
        try:
            # Corsica area
            if 41.0 <= lat <= 43.0 and 8.0 <= lon <= 10.0:
                if lat < 42.0:
                    return "2A"  # Corse-du-Sud (South Corsica)
                else:
                    return "2B"  # Haute-Corse (Upper Corsica)
            
            # Southern France (Provence-Alpes-Côte d'Azur)
            elif 43.0 <= lat <= 45.0 and 4.0 <= lon <= 8.0:
                if 6.0 <= lon <= 7.5 and 43.5 <= lat <= 44.5:
                    return "06"  # Alpes-Maritimes (Nice area)
                elif 5.0 <= lon <= 6.5 and 43.0 <= lat <= 44.0:
                    return "83"  # Var (Toulon area)
                elif 4.5 <= lon <= 5.5 and 43.0 <= lat <= 43.8:
                    return "13"  # Bouches-du-Rhône (Marseille area)
                elif 5.5 <= lon <= 6.5 and 44.0 <= lat <= 45.0:
                    return "04"  # Alpes-de-Haute-Provence
                elif 5.5 <= lon <= 7.0 and 44.5 <= lat <= 45.0:
                    return "05"  # Hautes-Alpes
                elif 4.5 <= lon <= 5.5 and 43.8 <= lat <= 44.5:
                    return "84"  # Vaucluse
            
            # Occitanie (Southern France)
            elif 42.5 <= lat <= 44.5 and 0.0 <= lon <= 4.0:
                if 2.0 <= lon <= 3.0 and 42.5 <= lat <= 43.5:
                    return "11"  # Aude
                elif 3.5 <= lon <= 4.5 and 43.5 <= lat <= 44.5:
                    return "30"  # Gard
                elif 2.5 <= lon <= 4.0 and 43.0 <= lat <= 43.8:
                    return "34"  # Hérault
                elif 3.0 <= lon <= 4.0 and 44.0 <= lat <= 44.8:
                    return "48"  # Lozère
                elif 1.5 <= lon <= 2.5 and 42.5 <= lat <= 42.8:
                    return "66"  # Pyrénées-Orientales
                elif 1.0 <= lon <= 2.0 and 42.5 <= lat <= 43.0:
                    return "09"  # Ariège
                elif 2.0 <= lon <= 3.0 and 44.0 <= lat <= 44.5:
                    return "12"  # Aveyron
                elif 0.5 <= lon <= 2.0 and 43.0 <= lat <= 43.8:
                    return "31"  # Haute-Garonne
                elif 0.0 <= lon <= 1.0 and 43.5 <= lat <= 44.0:
                    return "32"  # Gers
                elif 1.0 <= lon <= 2.0 and 44.5 <= lat <= 45.0:
                    return "46"  # Lot
                elif 0.0 <= lon <= 0.5 and 42.5 <= lat <= 43.5:
                    return "65"  # Hautes-Pyrénées
                elif 1.5 <= lon <= 2.5 and 43.5 <= lat <= 44.0:
                    return "81"  # Tarn
                elif 0.5 <= lon <= 1.5 and 43.8 <= lat <= 44.5:
                    return "82"  # Tarn-et-Garonne
            
            # For coordinates that don't match known areas, try to find closest department
            # This is a simplified approach - in production, use proper geocoding
            logger.warning(f"Coordinates {lat}, {lon} not in mapped areas - attempting fallback mapping")
            
            # Fallback: try to find closest department based on rough geographic areas
            if 42.0 <= lat <= 43.0 and 2.0 <= lon <= 3.0:
                return "66"  # Pyrénées-Orientales (likely closest)
            elif 42.0 <= lat <= 43.0 and 3.0 <= lon <= 4.0:
                return "11"  # Aude (likely closest)
            elif 43.0 <= lat <= 44.0 and 2.0 <= lon <= 3.0:
                return "34"  # Hérault (likely closest)
            elif 43.0 <= lat <= 44.0 and 3.0 <= lon <= 4.0:
                return "30"  # Gard (likely closest)
            
            logger.warning(f"No department mapping found for coordinates {lat}, {lon}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting department from coordinates {lat}, {lon}: {e}")
            return None
    
    def get_warning_data_for_coordinates(self, lat: float, lon: float) -> Optional[dict]:
        """
        Get warning data for coordinates by first mapping to department.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            
        Returns:
            Optional[dict]: Warning data from get_warning_full() API or None if error
        """
        try:
            department = self.get_department_from_coordinates(lat, lon)
            if not department:
                logger.warning(f"No department found for coordinates {lat}, {lon}")
                return None
            
            # Import here to avoid circular imports
            from meteofrance_api.client import MeteoFranceClient
            
            client = MeteoFranceClient()
            warnings = client.get_warning_current_phenomenons(department)
            
            logger.info(f"Retrieved warning data for department {department}: {warnings}")
            return warnings
            
        except Exception as e:
            logger.error(f"Error getting warning data for coordinates {lat}, {lon}: {e}")
            return None


def get_department_from_coordinates(lat: float, lon: float) -> Optional[str]:
    """
    Convenience function to get department code from coordinates.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        
    Returns:
        Optional[str]: Department code or None
    """
    mapper = DepartmentMapper()
    return mapper.get_department_from_coordinates(lat, lon)


def get_warning_data_for_coordinates(lat: float, lon: float) -> Optional[dict]:
    """
    Convenience function to get warning data for coordinates.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        
    Returns:
        Optional[dict]: Warning data or None
    """
    mapper = DepartmentMapper()
    return mapper.get_warning_data_for_coordinates(lat, lon)
