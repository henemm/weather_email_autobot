import geopandas as gpd
from shapely.geometry import Point
import os

ZONE_GEOJSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/digital_massifs.geojson')

# Static mapping from zone name to zm_key (API key)
ZONE_NAME_TO_ZM_KEY = {
    "Zone - BALAGNE": "201",
    "Zone - MONTI": "202",
    "Zone - SILLON CENTRAL": "203",
    "Zone - VIZZAVONA": "204",
    "Zone - MOYENNE MONTAGNE NORD": "205",
    "Zone - MOYENNE MONTAGNE SUD": "206",
    "Zone - SARTENAIS": "207",
    "Zone - REGION DE CONCA": "208"
}

class ZonePolygonMapper:
    """
    Utility for mapping coordinates to Zone name and zm_key using polygon data from digital_massifs.geojson.
    """
    def __init__(self, geojson_path: str = ZONE_GEOJSON_PATH):
        self.geojson_path = geojson_path
        self.gdf = gpd.read_file(geojson_path)
        # Force CRS to WGS84 if not set
        if self.gdf.crs is None:
            self.gdf.set_crs(epsg=4326, inplace=True)

    def get_zone_for_point(self, lat: float, lon: float):
        """
        Returns the zone name and zm_key for a given coordinate, or None if not found.
        """
        point = Point(lon, lat)
        for _, row in self.gdf.iterrows():
            if row.geometry.contains(point):
                name = row['properties']['name'] if 'properties' in row and 'name' in row['properties'] else row.get('name', None)
                zm_key = ZONE_NAME_TO_ZM_KEY.get(name)
                return {'name': name, 'zm_key': zm_key}
        # Fallback: nearest zone by centroid
        centroids = self.gdf.copy()
        centroids['centroid'] = centroids.geometry.centroid
        centroids['distance'] = centroids['centroid'].distance(point)
        nearest = centroids.sort_values('distance').iloc[0]
        name = nearest['properties']['name'] if 'properties' in nearest and 'name' in nearest['properties'] else nearest.get('name', None)
        zm_key = ZONE_NAME_TO_ZM_KEY.get(name)
        return {'name': name, 'zm_key': zm_key}

# Example usage (for debugging):
if __name__ == "__main__":
    mapper = ZonePolygonMapper()
    test_points = [
        (41.9192, 8.7386),   # Ajaccio
        (42.3069, 9.1497),   # Corte
        (42.5667, 8.7575),   # Calvi
        (42.7028, 9.4491),   # Bastia
        (41.5911, 9.2794),   # Porto-Vecchio
    ]
    for lat, lon in test_points:
        result = mapper.get_zone_for_point(lat, lon)
        print(f"Point ({lat}, {lon}): {result}") 