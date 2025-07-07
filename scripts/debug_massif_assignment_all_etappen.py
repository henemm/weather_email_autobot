import geopandas as gpd
from shapely.geometry import Point

# Beispielhafte GR20-Etappenpunkte (Name, lat, lon)
etappen = [
    ("Calenzana", 42.5106, 8.8581),
    ("Ortu di u Piobbu", 42.4672, 8.9247),
    ("Carrozzu", 42.4131, 8.9722),
    ("Asco Stagnu", 42.3992, 9.0147),
    ("Tighjettu", 42.3742, 9.0481),
    ("Ciottulu di i Mori", 42.3531, 9.0706),
    ("Manganu", 42.3297, 9.0456),
    ("Petra Piana", 42.2642, 9.0456),
    ("Onda", 42.1931, 9.0456),
    ("Vizzavona", 42.1511, 9.0906),
    ("Capannelle", 42.0706, 9.1611),
    ("Prati", 41.9956, 9.2022),
    ("Usciolu", 41.9331, 9.1797),
    ("Matalza", 41.9000, 9.1575),
    ("Asinau", 41.8572, 9.1831),
    ("Paliri", 41.8000, 9.2667),
    ("Conca", 41.7521, 9.2545),
    ("Porto-Vecchio", 41.5912, 9.2796),
]

gdf = gpd.read_file('data/digital_massifs.geojson')

for name, lat, lon in etappen:
    point = Point(lon, lat)
    found = False
    for idx, row in gdf.iterrows():
        massif_name = row['properties']['name'] if 'properties' in row and 'name' in row['properties'] else row.get('name', 'unknown')
        contains = row['geometry'].contains(point)
        if contains:
            # Platzhalter: Warnfarbe nach Zone (muss später automatisiert werden)
            if massif_name in ["Porto-Vecchio-Suedost", "REGION DE CONCA"]:
                color = "orange"
            elif massif_name in ["BONIFATO"]:
                color = "red"
            else:
                color = "green"
            print(f"{name:18s} | {lat:.4f}, {lon:.4f} | Massif: {massif_name:22s} | Farbe: {color}")
            found = True
            break
    if not found:
        print(f"{name:18s} | {lat:.4f}, {lon:.4f} | Kein Massif zugeordnet!") 