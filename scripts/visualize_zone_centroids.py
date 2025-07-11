#!/usr/bin/env python3
"""
Visualize Zone Centroids on a Map

This script visualizes the zone centroids on an interactive map using Folium.
"""

import json
import folium

# Load centroids from CSV (created previously)
centroids_path = 'data/zone_centroids.csv'
centroids = []
with open(centroids_path, 'r', encoding='utf-8') as f:
    next(f)  # skip header
    for line in f:
        zone_id, lat, lon, name = line.strip().split(',', 3)
        centroids.append({
            'zone_id': zone_id,
            'lat': float(lat),
            'lon': float(lon),
            'name': name.strip('"')
        })

# Center map on Korsika
m = folium.Map(location=[42.2, 9.0], zoom_start=8, tiles='OpenStreetMap')

# Add markers for each centroid
for c in centroids:
    folium.Marker(
        location=[c['lat'], c['lon']],
        popup=f"ID: {c['zone_id']}<br>{c['name']}",
        tooltip=f"ID: {c['zone_id']}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

# Save map to HTML
m.save('zone_centroids_map.html')
print("Map saved as zone_centroids_map.html") 