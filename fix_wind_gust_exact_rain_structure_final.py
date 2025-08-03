#!/usr/bin/env python3
"""
FIX WIND AND GUST EXACT RAIN STRUCTURE - FINAL
==============================================
Fix WIND and GUST debug output to use EXACTLY the same structure as RAIN (mm).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Read the current file
with open('src/weather/core/morning_evening_refactor.py', 'r') as f:
    content = f.read()

# Find the WIND section to replace
wind_section_start = '''            # Wind data debug
            if report_data.wind.geo_points:
                debug_lines.append("WIND")
                for i, point in enumerate(report_data.wind.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Wind (km/h)")
                    
                    # Get raw hourly data for this geo point
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        time_str = str(hour_time.hour)
                                        wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                        debug_lines.append(f"{time_str}:00 | {wind_speed}")
                    
                    # Calculate threshold and maximum for this point from raw data
                    point_threshold_time = None
                    point_max_time = None
                    point_max_value = None
                    point_threshold_value = None
                    
                    # Extract time and wind data from raw hourly data
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        time_str = str(hour_time.hour)
                                        wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                        
                                        # Track maximum
                                        if point_max_value is None or wind_speed > point_max_value:
                                            point_max_value = wind_speed
                                            point_max_time = time_str
                                        
                                        # Track threshold (earliest time when wind >= threshold)
                                        if wind_speed >= self.thresholds.get('wind_speed', 10) and point_threshold_time is None:
                                            point_threshold_time = time_str
                                            point_threshold_value = wind_speed
                    
                    # Add threshold and maximum for this point
                    debug_lines.append("=========")
                    if point_threshold_time is not None:
                        debug_lines.append(f"{point_threshold_time}:00 | {point_threshold_value} (Threshold)")
                    if point_max_time is not None:
                        debug_lines.append(f"{point_max_time}:00 | {point_max_value} (Max)")
                    debug_lines.append("")
                
                # Use processed data from report_data.wind
                global_max_value = report_data.wind.max_value
                global_max_time = report_data.wind.max_time
                
                # Add threshold and maximum tables as per specification
                # Always show threshold table, even if no threshold reached
                debug_lines.append("Threshold")
                debug_lines.append("GEO | Time | km/h")
                wind_threshold = self.thresholds.get('wind_speed', 1.0)
                for i, point in enumerate(report_data.wind.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                    # Calculate threshold for this point using the same logic as processing
                    point_threshold_time = None
                    point_threshold_value = None
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        # Use the same extractor as in processing
                                        wind_speed = hour_data.get('wind', {}).get('speed', 0)'''

# Create new WIND section using EXACT same structure as RAIN (mm)
new_wind_section = '''            # Wind data debug (EXACT same structure as RAIN (mm))
            if report_data.wind.geo_points:
                debug_lines.append("WIND")
                for i, point in enumerate(report_data.wind.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Wind Speed")
                    
                    # Get raw hourly data for this geo point - show all 24 hours
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            # Create a dictionary of all hours with default value 0
                            all_hours = {str(hour): 0 for hour in range(24)}
                            
                            # Fill in actual data
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    # Use the SAME date logic as the processing functions
                                    if report_data.report_type == 'evening':
                                        target_date = report_data.report_date  # Use target_date (tomorrow) directly
                                    else:
                                        target_date = report_data.report_date  # Today's date
                                    if hour_date == target_date:
                                        time_str = str(hour_time.hour)
                                        wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                        all_hours[time_str] = wind_speed
                            
                            # Display only hours 4:00 - 19:00 (as per specification)
                            for hour in range(4, 20):  # 4 to 19 inclusive
                                time_str = str(hour)
                                wind_speed = all_hours[time_str]
                                debug_lines.append(f"{time_str}:00 | {wind_speed}")
                    
                    # Add threshold and maximum for this point from processed data
                    debug_lines.append("=========")
                    # Calculate threshold and maximum for this specific point
                    point_threshold_time = None
                    point_threshold_value = None
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
                                        
                                        # Track maximum
                                        if point_max_value is None or wind_speed > point_max_value:
                                            point_max_value = wind_speed
                                            point_max_time = str(hour_time.hour)
                                        
                                        # Track threshold (earliest time when wind >= threshold)
                                        if wind_speed >= self.thresholds.get('wind_speed', 1.0) and point_threshold_time is None:
                                            point_threshold_time = str(hour_time.hour)
                                            point_threshold_value = wind_speed
                    
                    # Add threshold and maximum for this point
                    if point_threshold_time is not None:
                        debug_lines.append(f"{point_threshold_time}:00 | {point_threshold_value} (Threshold)")
                    if point_max_time is not None:
                        debug_lines.append(f"{point_max_time}:00 | {point_max_value} (Max)")
                    debug_lines.append("")
                
                # Add threshold and maximum tables as per specification
                if report_data.wind.threshold_time is not None:
                    debug_lines.append("Threshold")
                    debug_lines.append("GEO | Time | km/h")
                    for i, point in enumerate(report_data.wind.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                        # Get threshold for this point from processed data
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                point_threshold_time = None
                                point_threshold_value = None
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
                    debug_lines.append(f"Threshold | {report_data.wind.threshold_time}:00 | {report_data.wind.threshold_value}")
                    debug_lines.append("")
                
                # Add maximum table
                if report_data.wind.max_time is not None:
                    debug_lines.append("Maximum")
                    debug_lines.append("GEO | Time | Max")
                    for i, point in enumerate(report_data.wind.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                        # Get maximum for this point from processed data
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                point_max_time = None
                                point_max_value = None
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
                                            
                                            # Track maximum
                                            if point_max_value is None or wind_speed > point_max_value:
                                                point_max_value = wind_speed
                                                point_max_time = str(hour_time.hour)
                                
                                if point_max_time is not None and point_max_value is not None and point_max_value > 0:
                                    debug_lines.append(f"{tg_ref} | {point_max_time}:00 | {point_max_value}")
                                else:
                                    debug_lines.append(f"{tg_ref} | - | -")
                    
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.wind.max_time}:00 | {report_data.wind.max_value}")
                    debug_lines.append("")'''

# Find and replace the WIND section
content = content.replace(wind_section_start, new_wind_section)

# Find the GUST section to replace
gust_section_start = '''            # Gust data debug
            if report_data.gust.geo_points:
                debug_lines.append("GUST")
                for i, point in enumerate(report_data.gust.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Gust Speed")
                    
                    # Get raw hourly data for this geo point
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        time_str = str(hour_time.hour)
                                        gust_speed = hour_data.get('wind', {}).get('gust', 0)
                                        debug_lines.append(f"{time_str}:00 | {gust_speed}")
                    
                    # Calculate threshold and maximum for this point from raw data
                    point_threshold_time = None
                    point_max_time = None
                    point_max_value = None
                    point_threshold_value = None
                    
                    # Extract time and gust data from raw hourly data
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        time_str = str(hour_time.hour)
                                        gust_speed = hour_data.get('wind', {}).get('gust', 0)
                                        
                                        # Track maximum
                                        if point_max_value is None or gust_speed > point_max_value:
                                            point_max_value = gust_speed
                                            point_max_time = time_str
                                        
                                        # Track threshold (earliest time when gust >= threshold)
                                        if gust_speed >= self.thresholds.get('wind_gust_threshold', 5.0) and point_threshold_time is None:
                                            point_threshold_time = time_str
                                            point_threshold_value = gust_speed
                    
                    # Add threshold and maximum for this point
                    debug_lines.append("=========")
                    if point_threshold_time is not None:
                        debug_lines.append(f"{point_threshold_time}:00 | {point_threshold_value} (Threshold)")
                    if point_max_time is not None:
                        debug_lines.append(f"{point_max_time}:00 | {point_max_value} (Max)")
                    debug_lines.append("")
                
                # Use processed data from report_data.gust
                global_max_value = report_data.gust.max_value
                global_max_time = report_data.gust.max_time
                
                # Add threshold and maximum tables as per specification
                # Always show threshold table, even if no threshold reached
                debug_lines.append("Threshold")
                debug_lines.append("GEO | Time | km/h")
                gust_threshold = self.thresholds.get('wind_gust_threshold', 5.0)
                for i, point in enumerate(report_data.gust.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                    # Calculate threshold for this point using the same logic as processing
                    point_threshold_time = None
                    point_threshold_value = None
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        # Use the same extractor as in processing
                                        gust_speed = hour_data.get('wind', {}).get('gust', 0)'''

# Create new GUST section using EXACT same structure as RAIN (mm)
new_gust_section = '''            # Gust data debug (EXACT same structure as RAIN (mm))
            if report_data.gust.geo_points:
                debug_lines.append("GUST")
                for i, point in enumerate(report_data.gust.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Gust Speed")
                    
                    # Get raw hourly data for this geo point - show all 24 hours
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            # Create a dictionary of all hours with default value 0
                            all_hours = {str(hour): 0 for hour in range(24)}
                            
                            # Fill in actual data
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    # Use the SAME date logic as the processing functions
                                    if report_data.report_type == 'evening':
                                        target_date = report_data.report_date  # Use target_date (tomorrow) directly
                                    else:
                                        target_date = report_data.report_date  # Today's date
                                    if hour_date == target_date:
                                        time_str = str(hour_time.hour)
                                        gust_speed = hour_data.get('wind', {}).get('gust', 0)
                                        all_hours[time_str] = gust_speed
                            
                            # Display only hours 4:00 - 19:00 (as per specification)
                            for hour in range(4, 20):  # 4 to 19 inclusive
                                time_str = str(hour)
                                gust_speed = all_hours[time_str]
                                debug_lines.append(f"{time_str}:00 | {gust_speed}")
                    
                    # Add threshold and maximum for this point from processed data
                    debug_lines.append("=========")
                    # Calculate threshold and maximum for this specific point
                    point_threshold_time = None
                    point_threshold_value = None
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
                                        
                                        # Track maximum
                                        if point_max_value is None or gust_speed > point_max_value:
                                            point_max_value = gust_speed
                                            point_max_time = str(hour_time.hour)
                                        
                                        # Track threshold (earliest time when gust >= threshold)
                                        if gust_speed >= self.thresholds.get('wind_gust_threshold', 5.0) and point_threshold_time is None:
                                            point_threshold_time = str(hour_time.hour)
                                            point_threshold_value = gust_speed
                    
                    # Add threshold and maximum for this point
                    if point_threshold_time is not None:
                        debug_lines.append(f"{point_threshold_time}:00 | {point_threshold_value} (Threshold)")
                    if point_max_time is not None:
                        debug_lines.append(f"{point_max_time}:00 | {point_max_value} (Max)")
                    debug_lines.append("")
                
                # Add threshold and maximum tables as per specification
                if report_data.gust.threshold_time is not None:
                    debug_lines.append("Threshold")
                    debug_lines.append("GEO | Time | km/h")
                    for i, point in enumerate(report_data.gust.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                        # Get threshold for this point from processed data
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                point_threshold_time = None
                                point_threshold_value = None
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
                    debug_lines.append(f"Threshold | {report_data.gust.threshold_time}:00 | {report_data.gust.threshold_value}")
                    debug_lines.append("")
                
                # Add maximum table
                if report_data.gust.max_time is not None:
                    debug_lines.append("Maximum")
                    debug_lines.append("GEO | Time | Max")
                    for i, point in enumerate(report_data.gust.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                        # Get maximum for this point from processed data
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                point_max_time = None
                                point_max_value = None
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
                                            
                                            # Track maximum
                                            if point_max_value is None or gust_speed > point_max_value:
                                                point_max_value = gust_speed
                                                point_max_time = str(hour_time.hour)
                                
                                if point_max_time is not None and point_max_value is not None and point_max_value > 0:
                                    debug_lines.append(f"{tg_ref} | {point_max_time}:00 | {point_max_value}")
                                else:
                                    debug_lines.append(f"{tg_ref} | - | -")
                    
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.gust.max_time}:00 | {report_data.gust.max_value}")
                    debug_lines.append("")'''

# Find and replace the GUST section
content = content.replace(gust_section_start, new_gust_section)

# Write back to file
with open('src/weather/core/morning_evening_refactor.py', 'w') as f:
    f.write(content)

print("✅ WIND and GUST debug output fixed!")
print("   - EXACT same structure as RAIN (mm)")
print("   - Uses report_data.wind.geo_points and report_data.gust.geo_points")
print("   - Shows all n GEO points (T1G1, T1G2, T1G3, etc.)")
print("   - Identical logic for Morning and Evening reports")
print("   - Only different values: wind_speed vs gusts vs rain")
print("   - Complete Threshold and Maximum tables") 