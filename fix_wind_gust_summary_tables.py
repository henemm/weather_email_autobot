#!/usr/bin/env python3
"""
FIX WIND AND GUST SUMMARY TABLES
================================
Add missing Threshold and Maximum summary tables for WIND and GUST debug output.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Read the current file
with open('src/weather/core/morning_evening_refactor.py', 'r') as f:
    content = f.read()

# Find the end of WIND section and add summary tables
wind_end_marker = '''                    debug_lines.append("")'''

wind_summary_tables = '''                    debug_lines.append("")
                
                # Add Threshold and Maximum summary tables (like RAIN)
                debug_lines.append("Threshold")
                debug_lines.append("GEO | Time | Speed")
                
                # Calculate threshold for each point
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                    point_threshold_time = None
                    point_threshold_value = None
                    
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if report_data.report_type == 'evening':
                                        target_date = report_data.report_date
                                    else:
                                        target_date = report_data.report_date
                                    if hour_date == target_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                        
                                        # Track threshold (earliest time when wind >= threshold)
                                        if wind_speed >= self.thresholds.get('wind_speed', 1.0) and point_threshold_time is None:
                                            point_threshold_time = str(hour_time.hour)
                                            point_threshold_value = wind_speed
                    
                    if point_threshold_time is not None:
                        debug_lines.append(f"{tg_ref} | {point_threshold_time}:00 | {point_threshold_value}")
                    else:
                        debug_lines.append(f"{tg_ref} | - | -")
                
                debug_lines.append("=========")
                if report_data.wind.threshold_time is not None:
                    debug_lines.append(f"Threshold | {report_data.wind.threshold_time}:00 | {report_data.wind.threshold_value}")
                else:
                    debug_lines.append("Threshold | - | -")
                debug_lines.append("")
                
                debug_lines.append("Maximum")
                debug_lines.append("GEO | Time | Max")
                
                # Calculate maximum for each point
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                    point_max_time = None
                    point_max_value = None
                    
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if report_data.report_type == 'evening':
                                        target_date = report_data.report_date
                                    else:
                                        target_date = report_data.report_date
                                    if hour_date == target_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                        
                                        # Track maximum (highest value, if equal take earliest time)
                                        if point_max_value is None or wind_speed > point_max_value:
                                            point_max_value = wind_speed
                                            point_max_time = str(hour_time.hour)
                                        elif wind_speed == point_max_value and point_max_time is not None:
                                            # If equal values, take earliest time
                                            if int(str(hour_time.hour)) < int(point_max_time):
                                                point_max_time = str(hour_time.hour)
                    
                    if point_max_time is not None and point_max_value is not None and point_max_value > 0:
                        debug_lines.append(f"{tg_ref} | {point_max_time}:00 | {point_max_value}")
                    else:
                        debug_lines.append(f"{tg_ref} | - | -")
                
                debug_lines.append("=========")
                if report_data.wind.max_time is not None and report_data.wind.max_value is not None and report_data.wind.max_value > 0:
                    debug_lines.append(f"MAX | {report_data.wind.max_time}:00 | {report_data.wind.max_value}")
                else:
                    debug_lines.append("MAX | - | -")
                debug_lines.append("")'''

# Replace WIND end marker with summary tables
content = content.replace(wind_end_marker, wind_summary_tables)

# Find the end of GUST section and add summary tables
gust_end_marker = '''                    debug_lines.append("")'''

gust_summary_tables = '''                    debug_lines.append("")
                
                # Add Threshold and Maximum summary tables (like RAIN)
                debug_lines.append("Threshold")
                debug_lines.append("GEO | Time | Speed")
                
                # Calculate threshold for each point
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                    point_threshold_time = None
                    point_threshold_value = None
                    
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if report_data.report_type == 'evening':
                                        target_date = report_data.report_date
                                    else:
                                        target_date = report_data.report_date
                                    if hour_date == target_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        gust_speed = hour_data.get('wind', {}).get('gust', 0)
                                        
                                        # Track threshold (earliest time when gust >= threshold)
                                        if gust_speed >= self.thresholds.get('wind_gust_threshold', 5.0) and point_threshold_time is None:
                                            point_threshold_time = str(hour_time.hour)
                                            point_threshold_value = gust_speed
                    
                    if point_threshold_time is not None:
                        debug_lines.append(f"{tg_ref} | {point_threshold_time}:00 | {point_threshold_value}")
                    else:
                        debug_lines.append(f"{tg_ref} | - | -")
                
                debug_lines.append("=========")
                if report_data.gust.threshold_time is not None:
                    debug_lines.append(f"Threshold | {report_data.gust.threshold_time}:00 | {report_data.gust.threshold_value}")
                else:
                    debug_lines.append("Threshold | - | -")
                debug_lines.append("")
                
                debug_lines.append("Maximum")
                debug_lines.append("GEO | Time | Max")
                
                # Calculate maximum for each point
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                    point_max_time = None
                    point_max_value = None
                    
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if report_data.report_type == 'evening':
                                        target_date = report_data.report_date
                                    else:
                                        target_date = report_data.report_date
                                    if hour_date == target_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        gust_speed = hour_data.get('wind', {}).get('gust', 0)
                                        
                                        # Track maximum (highest value, if equal take earliest time)
                                        if point_max_value is None or gust_speed > point_max_value:
                                            point_max_value = gust_speed
                                            point_max_time = str(hour_time.hour)
                                        elif gust_speed == point_max_value and point_max_time is not None:
                                            # If equal values, take earliest time
                                            if int(str(hour_time.hour)) < int(point_max_time):
                                                point_max_time = str(hour_time.hour)
                    
                    if point_max_time is not None and point_max_value is not None and point_max_value > 0:
                        debug_lines.append(f"{tg_ref} | {point_max_time}:00 | {point_max_value}")
                    else:
                        debug_lines.append(f"{tg_ref} | - | -")
                
                debug_lines.append("=========")
                if report_data.gust.max_time is not None and report_data.gust.max_value is not None and report_data.gust.max_value > 0:
                    debug_lines.append(f"MAX | {report_data.gust.max_time}:00 | {report_data.gust.max_value}")
                else:
                    debug_lines.append("MAX | - | -")
                debug_lines.append("")'''

# Replace GUST end marker with summary tables
content = content.replace(gust_end_marker, gust_summary_tables)

# Write back to file
with open('src/weather/core/morning_evening_refactor.py', 'w') as f:
    f.write(content)

print("✅ WIND and GUST summary tables added!")
print("   - Threshold summary table added")
print("   - Maximum summary table added")
print("   - Shows '-' for points without threshold/maximum")
print("   - Analog to RAIN (mm) implementation") 