#!/usr/bin/env python3
"""
FIX WIND AND GUST COMPLETE
==========================
Completely fix the WIND and GUST debug output by placing them in the correct scope.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Read the current file
with open('src/weather/core/morning_evening_refactor.py', 'r') as f:
    content = f.read()

# Find the WIND section and replace it completely
wind_old_section = '''            # Wind data debug (analog to Rain) - show ALL n GEO points
            debug_lines.append("WIND")
            
            # Get the correct stage and all n GEO points
            start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            days_since_start = (report_data.report_date - start_date).days
            
            if report_data.report_type == 'evening':
                stage_idx = days_since_start + 1  # Tomorrow's stage
            else:  # morning
                stage_idx = days_since_start  # Today's stage
            
            import json
            with open("etappen.json", "r") as f:
                etappen_data = json.load(f)
            
            if stage_idx < len(etappen_data):
                stage = etappen_data[stage_idx]
                stage_points = stage.get('punkte', [])
                
                # Show ALL n GEO points, not just those with data
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Wind Speed")
                    
                    # Get hourly data for this geo point - show all hours 4:00-19:00
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
                
                # Add Threshold and Maximum summary tables (like RAIN)
                debug_lines.append("Threshold")
                debug_lines.append("GEO | Time | Speed")
                
                # Calculate threshold for each point
                # Get stage points from the stage data
                if stage_idx < len(etappen_data):
                    stage = etappen_data[stage_idx]
                    stage_points = stage.get('punkte', [])
                    
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
                # Get stage points from the stage data (reuse from above)
                if stage_idx < len(etappen_data):
                    stage = etappen_data[stage_idx]
                    stage_points = stage.get('punkte', [])
                    
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

wind_new_section = '''            # Wind data debug (analog to Rain) - show ALL n GEO points
            debug_lines.append("WIND")
            
            # Get the correct stage and all n GEO points
            start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            days_since_start = (report_data.report_date - start_date).days
            
            if report_data.report_type == 'evening':
                stage_idx = days_since_start + 1  # Tomorrow's stage
            else:  # morning
                stage_idx = days_since_start  # Today's stage
            
            import json
            with open("etappen.json", "r") as f:
                etappen_data = json.load(f)
            
            if stage_idx < len(etappen_data):
                stage = etappen_data[stage_idx]
                stage_points = stage.get('punkte', [])
                
                # Show ALL n GEO points, not just those with data
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Wind Speed")
                    
                    # Get hourly data for this geo point - show all hours 4:00-19:00
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

# Replace WIND section
content = content.replace(wind_old_section, wind_new_section)

# Find the GUST section and replace it completely
gust_old_section = '''            # Gust data debug (analog to Rain) - show ALL n GEO points
            debug_lines.append("GUST")
            
            # Get the correct stage and all n GEO points (same logic as WIND)
            if stage_idx < len(etappen_data):
                stage = etappen_data[stage_idx]
                stage_points = stage.get('punkte', [])
                
                # Show ALL n GEO points, not just those with data
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Gust Speed")
                    
                    # Get hourly data for this geo point - show all hours 4:00-19:00
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
                
                # Add Threshold and Maximum summary tables (like RAIN)
                debug_lines.append("Threshold")
                debug_lines.append("GEO | Time | Speed")
                
                # Calculate threshold for each point
                # Get stage points from the stage data
                if stage_idx < len(etappen_data):
                    stage = etappen_data[stage_idx]
                    stage_points = stage.get('punkte', [])
                    
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
                # Get stage points from the stage data (reuse from above)
                if stage_idx < len(etappen_data):
                    stage = etappen_data[stage_idx]
                    stage_points = stage.get('punkte', [])
                    
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

gust_new_section = '''            # Gust data debug (analog to Rain) - show ALL n GEO points
            debug_lines.append("GUST")
            
            # Get the correct stage and all n GEO points (same logic as WIND)
            if stage_idx < len(etappen_data):
                stage = etappen_data[stage_idx]
                stage_points = stage.get('punkte', [])
                
                # Show ALL n GEO points, not just those with data
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Gust Speed")
                    
                    # Get hourly data for this geo point - show all hours 4:00-19:00
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

# Replace GUST section
content = content.replace(gust_old_section, gust_new_section)

# Write back to file
with open('src/weather/core/morning_evening_refactor.py', 'w') as f:
    f.write(content)

print("✅ WIND and GUST debug output completely fixed!")
print("   - All variables properly defined in scope")
print("   - Shows ALL n GEO points")
print("   - Includes Threshold and Maximum summary tables")
print("   - Analog to RAIN (mm) implementation") 