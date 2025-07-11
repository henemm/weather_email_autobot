#!/usr/bin/env python3
"""
Debug script to visualize and analyze zone polygons.
Shows which polygons cover which areas and why coordinates are assigned incorrectly.
"""

import sys
import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import numpy as np
from shapely.geometry import Point

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fire.fire_zone_mapper import FireZoneMapper

def analyze_zone_polygons():
    """Analyze and visualize zone polygons to debug coordinate assignment."""
    print("🔍 DEBUG: Zone Polygon Analysis")
    print("=" * 60)
    
    mapper = FireZoneMapper()
    
    # Test coordinates
    test_coords = [
        (42.4653, 8.9070, "Ortu (should be BALAGNE)"),
        (41.7330, 9.3377, "Conca (should be REGION DE CONCA)"),
    ]
    
    print("\n📍 Testing coordinate assignments:")
    print("-" * 40)
    
    for lat, lon, description in test_coords:
        zone_info = mapper.get_zone_for_coordinates(lat, lon)
        if zone_info:
            print(f"{description}:")
            print(f"  Coordinates: ({lat}, {lon})")
            print(f"  Assigned zone: {zone_info['zone_name']}")
            print(f"  Zone number: {zone_info['zone_number']}")
            print(f"  Description: {zone_info['description']}")
        else:
            print(f"{description}: No zone found!")
        print()
    
    # Analyze all polygons
    print("\n🗺️ Analyzing all zone polygons:")
    print("-" * 40)
    
    for idx, row in mapper.gdf.iterrows():
        zone_number = row['numero_zon']
        zone_name = mapper.ZONE_NUMBER_TO_NAME.get(zone_number, f"Zone {zone_number}")
        
        # Get polygon bounds
        bounds = row.geometry.bounds
        min_lon, min_lat, max_lon, max_lat = bounds
        
        print(f"Zone {zone_number} ({zone_name}):")
        print(f"  Bounds: ({min_lat:.4f}, {min_lon:.4f}) to ({max_lat:.4f}, {max_lon:.4f})")
        print(f"  Center: ({(min_lat + max_lat)/2:.4f}, {(min_lon + max_lon)/2:.4f})")
        
        # Check if test coordinates fall within this polygon
        for lat, lon, description in test_coords:
            point = row.geometry.contains(Point(lon, lat))
            if point:
                print(f"  ✅ Contains {description}")
        print()
    
    # Create visualization
    create_polygon_visualization(mapper)

def create_polygon_visualization(mapper):
    """Create a visualization of all zone polygons."""
    print("\n📊 Creating polygon visualization...")
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Colors for different zones
    colors = plt.cm.Set3(np.linspace(0, 1, len(mapper.gdf)))
    
    # Plot each polygon
    for idx, row in mapper.gdf.iterrows():
        zone_number = row['numero_zon']
        zone_name = mapper.ZONE_NUMBER_TO_NAME.get(zone_number, f"Zone {zone_number}")
        
        # Get polygon coordinates
        if hasattr(row.geometry, 'exterior'):
            coords = list(row.geometry.exterior.coords)
        else:
            # Handle MultiPolygon or other geometry types
            coords = list(row.geometry.geoms[0].exterior.coords)
        
        # Convert to numpy array for plotting
        coords = np.array(coords)
        
        # Plot polygon
        color = colors[idx % len(colors)]
        polygon = patches.Polygon(coords, facecolor=color, alpha=0.6, edgecolor='black', linewidth=1)
        ax.add_patch(polygon)
        
        # Add label at centroid
        centroid = row.geometry.centroid
        ax.text(centroid.x, centroid.y, f"{zone_number}\n{zone_name[:10]}", 
                ha='center', va='center', fontsize=8, weight='bold')
    
    # Plot test coordinates
    test_coords = [
        (42.4653, 8.9070, "Ortu"),
        (41.7330, 9.3377, "Conca"),
    ]
    
    for lat, lon, name in test_coords:
        ax.plot(lon, lat, 'ro', markersize=8, markeredgecolor='black', markeredgewidth=2)
        ax.text(lon + 0.01, lat + 0.01, name, fontsize=10, weight='bold', color='red')
    
    # Set up the plot
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Corsica Fire Risk Zones\n(Red dots = Test coordinates)')
    ax.grid(True, alpha=0.3)
    
    # Set reasonable bounds for Corsica
    ax.set_xlim(8.5, 9.6)
    ax.set_ylim(41.3, 43.1)
    
    # Save the plot
    output_file = "output/zone_polygons_debug.png"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📁 Visualization saved to: {output_file}")
    
    plt.show()

def check_polygon_integrity():
    """Check if polygons are valid and properly closed."""
    print("\n🔧 Checking polygon integrity:")
    print("-" * 40)
    
    mapper = FireZoneMapper()
    
    for idx, row in mapper.gdf.iterrows():
        zone_number = row['numero_zon']
        zone_name = mapper.ZONE_NUMBER_TO_NAME.get(zone_number, f"Zone {zone_number}")
        
        geometry = row.geometry
        
        # Check if geometry is valid
        is_valid = geometry.is_valid
        area = geometry.area
        
        print(f"Zone {zone_number} ({zone_name}):")
        print(f"  Valid: {is_valid}")
        print(f"  Area: {area:.6f}")
        
        if not is_valid:
            print(f"  ⚠️  Invalid geometry!")
        
        # Check if it's a simple polygon
        if hasattr(geometry, 'exterior'):
            coords = list(geometry.exterior.coords)
            print(f"  Points: {len(coords)}")
            
            # Check if first and last points are the same (closed ring)
            if coords[0] != coords[-1]:
                print(f"  ⚠️  Polygon not closed! First: {coords[0]}, Last: {coords[-1]}")
        else:
            print(f"  ⚠️  Not a simple polygon")
        
        print()

if __name__ == "__main__":
    analyze_zone_polygons()
    check_polygon_integrity() 