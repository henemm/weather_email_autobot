#!/usr/bin/env python3
"""
Script to print a table of all GR20 stage end points with their assigned fire risk zone and current fire risk level.
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.wetter.fire_risk_massif import FireRiskZone
from datetime import date

ETAPPEN_PATH = os.path.join(os.path.dirname(__file__), '../etappen.json')

def load_stage_endpoints(etappen_path=ETAPPEN_PATH):
    with open(etappen_path, 'r', encoding='utf-8') as f:
        etappen = json.load(f)
    endpoints = []
    for stage in etappen:
        if 'punkte' in stage and stage['punkte']:
            last_point = stage['punkte'][-1]
            endpoints.append({
                'name': stage.get('name', 'Unknown'),
                'lat': float(last_point['lat']),
                'lon': float(last_point['lon'])
            })
    return endpoints

fire_risk = FireRiskZone()

print(f"{'Stage':<18} | {'Lat':>8} | {'Lon':>9} | {'Zone':<30} | {'Level':>5} | {'Warn'}")
print("-" * 85)

for stage in load_stage_endpoints():
    name = stage['name']
    lat = stage['lat']
    lon = stage['lon']
    zone_alert = fire_risk.get_zone_fire_alert_for_location(lat, lon, date.today())
    zone_name = zone_alert.get('zone_name', '-')
    level = zone_alert.get('level', '-')
    warn = fire_risk._level_to_warning(level) if isinstance(level, int) else '-'
    print(f"{name:<18} | {lat:8.4f} | {lon:9.4f} | {zone_name:<30} | {str(level):>5} | {warn}") 