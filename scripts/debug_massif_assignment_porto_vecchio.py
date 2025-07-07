import geopandas as gpd
from shapely.geometry import Point

lat, lon = 41.5912, 9.2796
point = Point(lon, lat)
gdf = gpd.read_file('data/digital_massifs.geojson')

found = False
for idx, row in gdf.iterrows():
    massif_name = row['name'] if 'name' in row else row['properties']['name'] if 'properties' in row and 'name' in row['properties'] else 'unknown'
    contains = row['geometry'].contains(point)
    distance = point.distance(row['geometry'])
    print(f"Massif | {massif_name:20s} | contains: {contains} | dist: {distance:.5f}")
    if contains:
        found = True
if not found:
    print('Porto-Vecchio liegt in keinem Polygon laut Geometrie!') 