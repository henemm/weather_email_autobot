#!/usr/bin/env python3
"""
Fire Zone Extractor - Extract official zone polygons from zones.js

This module extracts the official fire risk zone polygons from the French
prevention website's zones.js file and converts them to GeoJSON format.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any


class FireZoneExtractor:
    """Extract and convert official fire risk zones from zones.js to GeoJSON."""
    
    def __init__(self, zones_js_path: str = "data/official_zones.js"):
        """
        Initialize the extractor.
        
        Args:
            zones_js_path: Path to the downloaded zones.js file
        """
        self.zones_js_path = Path(zones_js_path)
        
    def extract_zones_from_js(self) -> List[Dict[str, Any]]:
        """
        Extract zone data from the JavaScript file.
        
        Returns:
            List of zone dictionaries with properties and geometry
        """
        if not self.zones_js_path.exists():
            raise FileNotFoundError(f"Zones.js file not found: {self.zones_js_path}")
            
        with open(self.zones_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find the zones array in the JavaScript
        zones_match = re.search(r'var zones = \[(.*?)\];', content, re.DOTALL)
        if not zones_match:
            raise ValueError("Could not find zones array in zones.js")
            
        zones_text = zones_match.group(1)
        
        # Parse each zone object
        zones = []
        zone_objects = self._split_zone_objects(zones_text)
        
        for zone_obj in zone_objects:
            zone_data = self._parse_zone_object(zone_obj)
            if zone_data:
                zones.append(zone_data)
                
        return zones
    
    def _split_zone_objects(self, zones_text: str) -> List[str]:
        """Split the zones text into individual zone objects."""
        # Simple splitting by }, { pattern
        parts = zones_text.split('}, {')
        zone_objects = []
        
        for i, part in enumerate(parts):
            if i == 0:
                # First part: remove leading {
                part = part.lstrip('{')
            elif i == len(parts) - 1:
                # Last part: remove trailing }
                part = part.rstrip('}')
            else:
                # Middle parts: add back the braces
                part = '{' + part + '}'
                
            zone_objects.append(part)
            
        return zone_objects
    
    def _parse_zone_object(self, zone_text: str) -> Dict[str, Any]:
        """Parse a single zone object from JavaScript to Python dict."""
        try:
            # Extract properties
            properties_match = re.search(r'properties: \{(.*?)\}', zone_text, re.DOTALL)
            if not properties_match:
                return None
                
            properties_text = properties_match.group(1)
            
            # Parse numero_zon
            numero_match = re.search(r'numero_zon: "(\d+)"', properties_text)
            numero_zon = numero_match.group(1) if numero_match else None
            
            # Parse level
            level_match = re.search(r'level: (\d+)', properties_text)
            level = int(level_match.group(1)) if level_match else 0
            
            # Parse Zonage_Feu description
            zonage_match = re.search(r'Zonage_Feu: "(.*?)"', properties_text)
            zonage_feu = zonage_match.group(1) if zonage_match else ""
            
            # Extract geometry coordinates
            coordinates_match = re.search(r'coordinates: \[\[(.*?)\]\]', zone_text, re.DOTALL)
            if not coordinates_match:
                return None
                
            coords_text = coordinates_match.group(1)
            coordinates = self._parse_coordinates(coords_text)
            
            if not coordinates:
                return None
                
            return {
                "type": "Feature",
                "properties": {
                    "numero_zon": numero_zon,
                    "level": level,
                    "Zonage_Feu": zonage_feu
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                }
            }
            
        except Exception as e:
            print(f"Error parsing zone object: {e}")
            return None
    
    def _parse_coordinates(self, coords_text: str) -> List[List[float]]:
        """Parse coordinate pairs from text and ensure polygon is closed."""
        coordinates = []
        
        # Split by coordinate pairs
        coord_pairs = re.findall(r'\[([\d.-]+), ([\d.-]+)\]', coords_text)
        
        for lon_str, lat_str in coord_pairs:
            try:
                lon = float(lon_str)
                lat = float(lat_str)
                coordinates.append([lon, lat])
            except ValueError:
                continue
        
        # Ensure polygon is closed (first and last coordinates should be the same)
        if coordinates and len(coordinates) > 2:
            first_coord = coordinates[0]
            last_coord = coordinates[-1]
            
            # If first and last coordinates are not the same, add the first coordinate at the end
            if first_coord != last_coord:
                coordinates.append(first_coord)
                
        return coordinates
    
    def convert_to_geojson(self, output_path: str = "data/fire_zones.geojson") -> None:
        """
        Convert extracted zones to GeoJSON format and save to file.
        
        Args:
            output_path: Path to save the GeoJSON file
        """
        zones = self.extract_zones_from_js()
        
        geojson = {
            "type": "FeatureCollection",
            "features": zones
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
            
        print(f"Converted {len(zones)} zones to GeoJSON: {output_file}")
    
    def get_zone_mapping(self) -> Dict[str, str]:
        """
        Create a mapping from zone number to zone description.
        
        Returns:
            Dictionary mapping zone numbers to descriptions
        """
        zones = self.extract_zones_from_js()
        mapping = {}
        
        for zone in zones:
            numero_zon = zone['properties']['numero_zon']
            zonage_feu = zone['properties']['Zonage_Feu']
            mapping[numero_zon] = zonage_feu
            
        return mapping


def main():
    """Main function to extract and convert zones."""
    extractor = FireZoneExtractor()
    
    try:
        # Convert to GeoJSON
        extractor.convert_to_geojson()
        
        # Show zone mapping
        mapping = extractor.get_zone_mapping()
        print("\nZone Number to Description Mapping:")
        print("=" * 50)
        for numero, description in sorted(mapping.items()):
            print(f"Zone {numero}: {description}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 