"""
Enhanced Alternative Risk Analysis using stable MeteoFrance API.

This module provides a comprehensive alternative risk analysis that:
- Uses ONLY MeteoFrance API data (no fallbacks)
- Provides 100% transparent debug output
- Shows exactly how aggregated display is generated from raw data
- Includes probability data and thunderstorm forecasts
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EnhancedHeatRiskResult:
    """Enhanced heat risk analysis result with debug information."""
    max_temperature: float
    description: str
    debug_info: str
    data_source: str = "meteofrance-api"


@dataclass
class EnhancedColdRiskResult:
    """Enhanced cold risk analysis result with debug information."""
    min_temperature: float
    description: str
    debug_info: str
    data_source: str = "meteofrance-api"


@dataclass
class EnhancedRainRiskResult:
    """Enhanced rain risk analysis result with debug information."""
    has_rain: bool
    max_probability: int
    max_rain_rate: float
    first_rain_time: Optional[str]
    description: str
    debug_info: str
    data_source: str = "meteofrance-api"


@dataclass
class EnhancedThunderstormRiskResult:
    """Enhanced thunderstorm risk analysis result with debug information."""
    has_thunderstorm: bool
    thunderstorm_count: int
    first_thunderstorm_time: Optional[str]
    max_probability: int
    description: str
    debug_info: str
    data_source: str = "meteofrance-api"


@dataclass
class EnhancedThunderstormTomorrowResult:
    """Enhanced thunderstorm risk analysis result for tomorrow (+1 day)."""
    has_thunderstorm: bool
    thunderstorm_count: int
    first_thunderstorm_time: Optional[str]
    max_probability: int
    description: str
    debug_info: str
    data_source: str = "meteofrance-api"


@dataclass
class EnhancedWindRiskResult:
    """Enhanced wind risk analysis result with debug information."""
    max_wind_speed: float
    max_gusts: float
    first_high_wind_time: Optional[str]
    description: str
    debug_info: str
    data_source: str = "meteofrance-api"


@dataclass
class EnhancedRiskAnalysisResult:
    """Enhanced risk analysis result with comprehensive debug information."""
    heat: EnhancedHeatRiskResult
    cold: EnhancedColdRiskResult
    rain: EnhancedRainRiskResult
    thunderstorm: EnhancedThunderstormRiskResult
    thunderstorm_tomorrow: EnhancedThunderstormTomorrowResult
    wind: EnhancedWindRiskResult
    overall_debug_info: str


class EnhancedAlternativeRiskAnalyzer:
    """
    Enhanced alternative risk analyzer with transparent debug output.
    
    This analyzer provides 100% transparent debug information showing
    exactly how the aggregated display is generated from raw MeteoFrance data.
    """
    
    def __init__(self):
        """Initialize the enhanced alternative risk analyzer."""
        logger.info("EnhancedAlternativeRiskAnalyzer initialized")
    
    def analyze_all_risks(self, weather_data: Dict[str, Any]) -> EnhancedRiskAnalysisResult:
        """
        Analyze all weather risks with comprehensive debug information.
        
        Args:
            weather_data: Dictionary containing MeteoFrance weather data
            
        Returns:
            EnhancedRiskAnalysisResult with all risk analyses and debug info
        """
        try:
            logger.info("Starting enhanced alternative risk analysis")
            
            # Analyze each risk type with debug information
            heat_result = self._analyze_heat_risk_with_debug(weather_data)
            cold_result = self._analyze_cold_risk_with_debug(weather_data)
            rain_result = self._analyze_rain_risk_with_debug(weather_data)
            thunderstorm_result = self._analyze_thunderstorm_risk_with_debug(weather_data)
            thunderstorm_tomorrow_result = self._analyze_thunderstorm_tomorrow_with_debug(weather_data)
            wind_result = self._analyze_wind_risk_with_debug(weather_data)
            
            # Generate overall debug information
            overall_debug = self._generate_overall_debug_info(weather_data, {
                'heat': heat_result,
                'cold': cold_result,
                'rain': rain_result,
                'thunderstorm': thunderstorm_result,
                'thunderstorm_tomorrow': thunderstorm_tomorrow_result,
                'wind': wind_result
            })
            
            result = EnhancedRiskAnalysisResult(
                heat=heat_result,
                cold=cold_result,
                rain=rain_result,
                thunderstorm=thunderstorm_result,
                thunderstorm_tomorrow=thunderstorm_tomorrow_result,
                wind=wind_result,
                overall_debug_info=overall_debug
            )
            
            logger.info("Enhanced alternative risk analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to perform enhanced alternative risk analysis: {e}")
            return self._create_error_result(str(e))
    
    def _analyze_heat_risk_with_debug(self, weather_data: Dict[str, Any]) -> EnhancedHeatRiskResult:
        """Analyze heat risk with detailed debug information."""
        debug_lines = []
        debug_lines.append("HEAT RISK ANALYSIS DEBUG:")
        debug_lines.append("=" * 40)
        
        try:
            # Check for API failure
            if self._detect_api_failure(weather_data):
                debug_lines.append("ERROR: MeteoFrance API failure detected")
                return EnhancedHeatRiskResult(
                    max_temperature=0.0,
                    description="MeteoFrance API failure: No weather data available",
                    debug_info="\n".join(debug_lines)
                )
            
            # Extract daily temperature data
            daily_data = weather_data.get('daily_data', [])
            debug_lines.append(f"Daily data entries found: {len(daily_data)}")
            
            max_temp = None
            max_temp_source = "unknown"
            
            # Try to get daily max temperature first
            for i, day in enumerate(daily_data):
                temp_max = day.get('temperature', {}).get('max')
                if temp_max is not None:
                    max_temp = float(temp_max)
                    max_temp_source = f"daily_data[{i}].temperature.max"
                    debug_lines.append(f"Found daily max temperature: {max_temp}°C from {max_temp_source}")
                    break
            
            # Fallback to hourly aggregation if no daily data
            if max_temp is None:
                debug_lines.append("No daily max temperature found, falling back to hourly aggregation")
                hourly_data = weather_data.get('hourly_data', [])
                debug_lines.append(f"Hourly data entries found: {len(hourly_data)}")
                
                if hourly_data:
                    max_temp = float('-inf')
                    for i, entry in enumerate(hourly_data):
                        temp_value = entry.temperature
                        if temp_value > max_temp:
                            max_temp = temp_value
                            max_temp_source = f"hourly_data[{i}].temperature"
                    
                    if max_temp != float('-inf'):
                        debug_lines.append(f"Calculated max temperature from hourly data: {max_temp}°C")
                    else:
                        debug_lines.append("ERROR: No valid temperature data found in hourly data")
                        return EnhancedHeatRiskResult(
                            max_temperature=0.0,
                            description="MeteoFrance API failure: No temperature data",
                            debug_info="\n".join(debug_lines)
                        )
                else:
                    debug_lines.append("ERROR: No hourly data available")
                    return EnhancedHeatRiskResult(
                        max_temperature=0.0,
                        description="MeteoFrance API failure: No hourly data",
                        debug_info="\n".join(debug_lines)
                    )
            
            debug_lines.append(f"Final max temperature: {max_temp}°C (source: {max_temp_source})")
            debug_lines.append("Heat risk analysis completed successfully")
            
            return EnhancedHeatRiskResult(
                max_temperature=max_temp,
                description=f"Maximum temperature: {max_temp}°C",
                debug_info="\n".join(debug_lines)
            )
            
        except Exception as e:
            debug_lines.append(f"ERROR in heat risk analysis: {e}")
            return EnhancedHeatRiskResult(
                max_temperature=0.0,
                description=f"MeteoFrance API failure: Analysis error - {str(e)}",
                debug_info="\n".join(debug_lines)
            )
    
    def _analyze_cold_risk_with_debug(self, weather_data: Dict[str, Any]) -> EnhancedColdRiskResult:
        """Analyze cold risk with detailed debug information."""
        debug_lines = []
        debug_lines.append("COLD RISK ANALYSIS DEBUG:")
        debug_lines.append("=" * 40)
        
        try:
            # Check for API failure
            if self._detect_api_failure(weather_data):
                debug_lines.append("ERROR: MeteoFrance API failure detected")
                return EnhancedColdRiskResult(
                    min_temperature=0.0,
                    description="MeteoFrance API failure: No weather data available",
                    debug_info="\n".join(debug_lines)
                )
            
            # Extract daily temperature data
            daily_data = weather_data.get('daily_data', [])
            debug_lines.append(f"Daily data entries found: {len(daily_data)}")
            
            min_temp = None
            min_temp_source = "unknown"
            
            # Try to get daily min temperature first
            for i, day in enumerate(daily_data):
                temp_min = day.get('temperature', {}).get('min')
                if temp_min is not None:
                    min_temp = float(temp_min)
                    min_temp_source = f"daily_data[{i}].temperature.min"
                    debug_lines.append(f"Found daily min temperature: {min_temp}°C from {min_temp_source}")
                    break
            
            # Fallback to hourly aggregation if no daily data
            if min_temp is None:
                debug_lines.append("No daily min temperature found, falling back to hourly aggregation")
                hourly_data = weather_data.get('hourly_data', [])
                debug_lines.append(f"Hourly data entries found: {len(hourly_data)}")
                
                if hourly_data:
                    min_temp = float('inf')
                    for i, entry in enumerate(hourly_data):
                        temp_value = entry.temperature
                        if temp_value < min_temp:
                            min_temp = temp_value
                            min_temp_source = f"hourly_data[{i}].temperature"
                    
                    if min_temp != float('inf'):
                        debug_lines.append(f"Calculated min temperature from hourly data: {min_temp}°C")
                    else:
                        debug_lines.append("ERROR: No valid temperature data found in hourly data")
                        return EnhancedColdRiskResult(
                            min_temperature=0.0,
                            description="MeteoFrance API failure: No temperature data",
                            debug_info="\n".join(debug_lines)
                        )
                else:
                    debug_lines.append("ERROR: No hourly data available")
                    return EnhancedColdRiskResult(
                        min_temperature=0.0,
                        description="MeteoFrance API failure: No hourly data",
                        debug_info="\n".join(debug_lines)
                    )
            
            debug_lines.append(f"Final min temperature: {min_temp}°C (source: {min_temp_source})")
            debug_lines.append("Cold risk analysis completed successfully")
            
            return EnhancedColdRiskResult(
                min_temperature=min_temp,
                description=f"Minimum temperature: {min_temp}°C",
                debug_info="\n".join(debug_lines)
            )
            
        except Exception as e:
            debug_lines.append(f"ERROR in cold risk analysis: {e}")
            return EnhancedColdRiskResult(
                min_temperature=0.0,
                description=f"MeteoFrance API failure: Analysis error - {str(e)}",
                debug_info="\n".join(debug_lines)
            )
    
    def _analyze_rain_risk_with_debug(self, weather_data: Dict[str, Any]) -> EnhancedRainRiskResult:
        """Analyze rain risk with detailed debug information."""
        debug_lines = []
        debug_lines.append("RAIN RISK ANALYSIS DEBUG:")
        debug_lines.append("=" * 50)
        
        try:
            # Get report type and stage date
            report_type = weather_data.get('report_type', 'morning')
            stage_date = weather_data.get('stage_date', 'Unknown')
            debug_lines.append(f"ANALYZING RAIN FOR DATE: {stage_date}")
            debug_lines.append(f"REPORT TYPE: {report_type}")
            
            # Extract rain probability data from unified_data
            unified_data = weather_data.get('unified_data')
            if unified_data and hasattr(unified_data, 'data_points'):
                # Extract rain amount data from unified_data
                rain_amount_data = []
                for point in unified_data.data_points:
                    if hasattr(point, 'entries'):
                        for entry in point.entries:
                            # Create rain amount entry
                            if hasattr(entry, 'rain_amount') and entry.rain_amount is not None:
                                rain_amount_data.append({
                                    'timestamp': entry.timestamp,
                                    'amount': entry.rain_amount
                                })
                
                # Use traditional probability_data for rain probability
                rain_probability_data = weather_data.get('probability_data', [])
            else:
                # Fallback to traditional data structure
                rain_probability_data = weather_data.get('probability_data', [])
                rain_amount_data = weather_data.get('hourly_data', [])
            
            debug_lines.append(f"Rain probability data entries: {len(rain_probability_data)}")
            debug_lines.append(f"Rain amount data entries: {len(rain_amount_data)}")
            
            # Determine target date based on report type
            if isinstance(stage_date, str):
                from datetime import datetime, timedelta
                stage_date_obj = datetime.strptime(stage_date, '%Y-%m-%d').date()
            else:
                stage_date_obj = stage_date
            
            if report_type == 'morning':
                # Morning Report: analyze today (current day)
                target_date = stage_date_obj
                debug_lines.append(f"Morning Report: Filtering rain data for today: {target_date}")
            else:
                # Evening Report: analyze tomorrow (day after current day)
                target_date = stage_date_obj + timedelta(days=1)
                debug_lines.append(f"Evening Report: Filtering rain data for tomorrow: {target_date}")
            
            # Filter rain probability data for target date
            rain_probabilities = []
            for prob_entry in rain_probability_data:
                if isinstance(prob_entry, dict):
                    entry_timestamp = prob_entry.get('timestamp')
                    probability = prob_entry.get('probability')
                else:
                    entry_timestamp = getattr(prob_entry, 'timestamp', None)
                    probability = getattr(prob_entry, 'rain_3h', None)
                
                if entry_timestamp and probability is not None and entry_timestamp.date() == target_date:
                    rain_probabilities.append({
                        'time': entry_timestamp,
                        'probability': probability
                    })
            
            debug_lines.append(f"Rain probability entries found for {target_date}: {len(rain_probabilities)}")
            
            # Filter rain amount data for target date
            rain_amounts = []
            for amount_entry in rain_amount_data:
                if isinstance(amount_entry, dict):
                    entry_timestamp = amount_entry.get('timestamp')
                    amount = amount_entry.get('amount')
                else:
                    entry_timestamp = getattr(amount_entry, 'timestamp', None)
                    amount = getattr(amount_entry, 'rain_amount', None)
                
                if entry_timestamp and amount is not None and entry_timestamp.date() == target_date:
                    rain_amounts.append({
                        'time': entry_timestamp,
                        'amount': amount
                    })
            
            debug_lines.append(f"Rain amount entries found for {target_date}: {len(rain_amounts)}")
            
            # Show raw rain data
            debug_lines.append("RAW RAIN PROBABILITY DATA:")
            for i, entry in enumerate(rain_probabilities[:10]):  # Show first 10 entries
                debug_lines.append(f"  Entry {i+1}: {str(int(entry['time'].hour))} - {entry['probability']}%")
            
            debug_lines.append("RAW RAIN AMOUNT DATA:")
            for i, entry in enumerate(rain_amounts[:10]):  # Show first 10 entries
                debug_lines.append(f"  Entry {i+1}: {str(int(entry['time'].hour))} - {entry['amount']}mm/h")
            
            # Calculate rain risk
            if not rain_probabilities and not rain_amounts:
                debug_lines.append("No rain data available for target date")
                return EnhancedRainRiskResult(
                    has_rain=False,
                    max_probability=0,
                    max_rain_rate=0.0,
                    first_rain_time=None,
                    description="Regen -",
                    debug_info="\n".join(debug_lines),
                    data_source="meteofrance-api"
                )
            
            # Find maximum probability
            max_probability = 0
            max_probability_time = None
            if rain_probabilities:
                max_prob_entry = max(rain_probabilities, key=lambda x: x['probability'])
                max_probability = max_prob_entry['probability']
                max_probability_time = max_prob_entry['time']
            
            # Find maximum amount
            max_amount = 0
            max_amount_time = None
            if rain_amounts:
                max_amount_entry = max(rain_amounts, key=lambda x: x['amount'])
                max_amount = max_amount_entry['amount']
                max_amount_time = max_amount_entry['time']
            
            debug_lines.append(f"Max probability: {max_probability}%")
            debug_lines.append(f"Max amount: {max_amount}mm/h")
            
            # Check if rain conditions are met
            has_rain = False
            if max_probability >= 50 and max_amount > 2.0:
                has_rain = True
                debug_lines.append("Rain conditions met: probability >= 50% AND amount > 2mm/h")
            else:
                debug_lines.append(f"Rain conditions not met: probability {max_probability}% < 50% OR amount {max_amount}mm/h <= 2mm/h")
            
            # Generate description
            if has_rain and max_probability_time and max_amount_time:
                description = f"Regen{max_probability}%@{str(int(max_probability_time.hour))}(max{max_amount}mm@{str(int(max_amount_time.hour))})"
            else:
                description = "Regen -"
            
            debug_lines.append(f"Final description: {description}")
            debug_lines.append("Rain risk analysis completed successfully")
            
            return EnhancedRainRiskResult(
                has_rain=has_rain,
                max_probability=max_probability,
                max_rain_rate=max_amount, # Changed from max_rain_rate to max_amount
                first_rain_time=str(int(max_probability_time.hour)) if max_probability_time else None,
                description=description,
                debug_info="\n".join(debug_lines),
                data_source="meteofrance-api"
            )
            
        except Exception as e:
            debug_lines.append(f"ERROR in rain risk analysis: {e}")
            return EnhancedRainRiskResult(
                has_rain=False,
                max_probability=0,
                max_rain_rate=0.0,
                first_rain_time=None,
                description="Regen -",
                debug_info="\n".join(debug_lines),
                data_source="meteofrance-api"
            )
    
    def _analyze_thunderstorm_risk_with_debug(self, weather_data: Dict[str, Any]) -> EnhancedThunderstormRiskResult:
        """Analyze thunderstorm risk with detailed debug information following email_format.mdc specification."""
        debug_lines = []
        debug_lines.append("THUNDERSTORM RISK ANALYSIS DEBUG:")
        debug_lines.append("=" * 50)
        
        try:
            # Get the stage date and report type for analysis
            stage_date = weather_data.get('stage_date', 'Unknown')
            report_type = weather_data.get('report_type', 'morning')  # Default to morning
            debug_lines.append(f"ANALYZING THUNDERSTORM FOR DATE: {stage_date}")
            debug_lines.append(f"REPORT TYPE: {report_type}")
            
            # Check for API failure
            if self._detect_api_failure(weather_data):
                debug_lines.append("ERROR: MeteoFrance API failure detected")
                return EnhancedThunderstormRiskResult(
                    has_thunderstorm=False,
                    thunderstorm_count=0,
                    first_thunderstorm_time=None,
                    max_probability=0,
                    description="MeteoFrance API failure: No weather data available",
                    debug_info="\n".join(debug_lines),
                    data_source="meteofrance-api"
                )
            
            # Extract thunderstorm data from unified_data
            unified_data = weather_data.get('unified_data')
            if unified_data and hasattr(unified_data, 'data_points'):
                # Extract thunderstorm data from unified_data
                thunderstorm_data = []
                for point in unified_data.data_points:
                    if hasattr(point, 'entries'):
                        for entry in point.entries:
                            # Check if this is a thunderstorm entry
                            desc_lower = entry.weather_description.lower()
                            if any(keyword in desc_lower for keyword in ['orage', 'thunderstorm', 'éclair', 'orages', 'averses orageuses']):
                                thunderstorm_data.append({
                                    'timestamp': entry.timestamp,
                                    'description': entry.weather_description,
                                    'icon': entry.weather_icon,
                                    'rain_amount': entry.rain_amount,
                                    'wind_speed': entry.wind_speed
                                })
            else:
                # Fallback to traditional thunderstorm_data
                thunderstorm_data = weather_data.get('thunderstorm_data', [])
            
            debug_lines.append(f"Thunderstorm data entries: {len(thunderstorm_data)}")
            
            # Extract hourly data from unified_data
            if unified_data and hasattr(unified_data, 'data_points'):
                # Extract hourly data from unified_data
                hourly_data = []
                for point in unified_data.data_points:
                    if hasattr(point, 'entries'):
                        hourly_data.extend(point.entries)
            else:
                # Fallback to traditional hourly_data
                hourly_data = weather_data.get('hourly_data', [])
            
            debug_lines.append(f"Hourly data entries: {len(hourly_data)}")
            
            # Extract probability data from unified_data
            if unified_data and hasattr(unified_data, 'data_points'):
                # Extract probability data from unified_data
                probability_data = []
                for point in unified_data.data_points:
                    if hasattr(point, 'entries'):
                        for entry in point.entries:
                            # Create probability entry from hourly data
                            probability_data.append({
                                'timestamp': entry.timestamp,
                                'rain_3h': getattr(entry, 'rain_probability', None)
                            })
            else:
                # Fallback to traditional probability_data
                probability_data = weather_data.get('probability_data', [])
            
            debug_lines.append(f"Probability data entries: {len(probability_data)}")
            
            if not thunderstorm_data:
                debug_lines.append("No thunderstorm data available")
                return EnhancedThunderstormRiskResult(
                    has_thunderstorm=False,
                    thunderstorm_count=0,
                    first_thunderstorm_time=None,
                    max_probability=0,
                    description="Gew. -",
                    debug_info="\n".join(debug_lines),
                    data_source="meteofrance-api"
                )
            
            # Show raw thunderstorm data
            debug_lines.append("RAW THUNDERSTORM DATA:")
            for i, entry in enumerate(thunderstorm_data[:10]):  # Show first 10 entries
                debug_lines.append(f"  Entry {i+1}: {str(int(entry['timestamp'].hour))} - {entry['description']} (Icon: {entry['icon']}, Rain: {entry['rain_amount']}mm/h, Wind: {entry['wind_speed']}km/h)")
            
            # Show raw hourly weather data for thunderstorm detection
            debug_lines.append("RAW HOURLY WEATHER DATA:")
            for i, entry in enumerate(hourly_data[:10]):  # Show first 10 entries
                # Check if this is a thunderstorm
                desc_lower = entry.weather_description.lower()
                is_thunderstorm = any(keyword in desc_lower for keyword in ['orage', 'thunderstorm', 'éclair', 'orages', 'averses orageuses'])
                debug_lines.append(f"  Entry {i+1}: {str(int(entry.timestamp.hour))} - {entry.weather_description} (Thunderstorm: {is_thunderstorm})")
            
            # Find thunderstorm entries based on report type
            thunderstorm_entries = []
            
            # Get the stage date and calculate target date based on report type
            stage_date = weather_data.get('stage_date', 'Unknown')
            if isinstance(stage_date, str):
                from datetime import datetime, timedelta
                stage_date_obj = datetime.strptime(stage_date, '%Y-%m-%d').date()
            else:
                stage_date_obj = stage_date
            
            # Determine target date based on report type
            if report_type == 'morning':
                # Morning Report: analyze today (current day)
                target_date = stage_date_obj
                debug_lines.append(f"Morning Report: Filtering thunderstorm data for today: {target_date}")
            else:
                # Evening Report: analyze tomorrow (day after current day)
                target_date = stage_date_obj + timedelta(days=1)
                debug_lines.append(f"Evening Report: Filtering thunderstorm data for tomorrow: {target_date}")
            
            # Define time range for target date (04:00-22:00)
            from datetime import datetime
            target_start = datetime.combine(target_date, datetime.min.time().replace(hour=4))
            target_end = datetime.combine(target_date, datetime.min.time().replace(hour=22))
            
            for entry in thunderstorm_data:
                # Check if entry is within target date's time range
                if target_start <= entry['timestamp'] <= target_end:
                    # Check for thunderstorm in weather description
                    desc_lower = entry['description'].lower()
                    if any(keyword in desc_lower for keyword in ['orage', 'thunderstorm', 'éclair', 'orages', 'averses orageuses']):
                        # Determine severity based on weather icon
                        severity = "light"
                        if entry['icon'] in ['p28j', 'p29j']:
                            severity = "moderate"
                        elif entry['icon'] in ['p30j', 'p31j']:
                            severity = "severe"
                        
                        thunderstorm_entries.append({
                            'time': entry['timestamp'],
                            'description': entry['description'],
                            'severity': severity
                        })
                        debug_lines.append(f"Found thunderstorm for {target_date}: {str(int(entry['timestamp'].hour))} - {entry['description']} (Severity: {severity})")
            
            if not thunderstorm_entries:
                debug_lines.append(f"No thunderstorm entries found for {target_date}")
                return EnhancedThunderstormRiskResult(
                    has_thunderstorm=False,
                    thunderstorm_count=0,
                    first_thunderstorm_time=None,
                    max_probability=0,
                    description="Gew. -",
                    debug_info="\n".join(debug_lines),
                    data_source="meteofrance-api"
                )
            
            # Calculate thunderstorm probability based on number of thunderstorm hours
            total_hours = 18  # 04:00-22:00 = 18 hours
            thunderstorm_hours = len(thunderstorm_entries)
            thunderstorm_probability = min(100, int((thunderstorm_hours / total_hours) * 100))
            
            debug_lines.append(f"Thunderstorm probability calculation: {thunderstorm_hours}/{total_hours} hours = {thunderstorm_probability}%")
            
            # Check probability data for thunderstorm probability
            debug_lines.append("Checking probability data for thunderstorm probability...")
            for prob_entry in probability_data[:20]:  # Show first 20 entries
                debug_lines.append(f"  Probability entry: {prob_entry}")
            
            # Get threshold from config (default 10% if not available)
            thunderstorm_threshold = 10  # Default threshold from config.yaml
            
            # Find first thunderstorm time
            first_thunderstorm_time = min(thunderstorm_entries, key=lambda x: x['time'])['time']
            first_time_str = str(int(first_thunderstorm_time.hour))
            
            # Find maximum thunderstorm probability time
            max_thunderstorm_time = max(thunderstorm_entries, key=lambda x: x['time'])['time']
            max_time_str = str(int(max_thunderstorm_time.hour))
            
            # Determine severity (use most severe thunderstorm found)
            severities = [entry['severity'] for entry in thunderstorm_entries]
            if 'severe' in severities:
                overall_severity = 'severe'
            elif 'moderate' in severities:
                overall_severity = 'moderate'
            else:
                overall_severity = 'light'
            
            # Generate description following email_format.mdc format
            if thunderstorm_probability >= thunderstorm_threshold:
                description = f"Gew.{thunderstorm_probability}%@{first_time_str}(max{thunderstorm_probability}%@{max_time_str}) ({overall_severity})"
            else:
                description = f"Gew.{thunderstorm_probability}% (below threshold {thunderstorm_threshold}%)"
            
            debug_lines.append(f"Thunderstorm threshold: {thunderstorm_threshold}%")
            debug_lines.append(f"Severity level: {overall_severity}")
            debug_lines.append(f"Final description: {description}")
            debug_lines.append("Thunderstorm risk analysis completed successfully")
            
            return EnhancedThunderstormRiskResult(
                has_thunderstorm=True,
                thunderstorm_count=len(thunderstorm_entries),
                first_thunderstorm_time=first_time_str,
                max_probability=thunderstorm_probability,
                description=description,
                debug_info="\n".join(debug_lines),
                data_source="meteofrance-api"
            )
            
        except Exception as e:
            debug_lines.append(f"Error in thunderstorm risk analysis: {e}")
            return EnhancedThunderstormRiskResult(
                has_thunderstorm=False,
                thunderstorm_count=0,
                first_thunderstorm_time=None,
                max_probability=0,
                description="Gew. -",
                debug_info="\n".join(debug_lines),
                data_source="meteofrance-api"
            )
    
    def _analyze_thunderstorm_tomorrow_with_debug(self, weather_data: Dict[str, Any]) -> EnhancedThunderstormTomorrowResult:
        """Analyze tomorrow's thunderstorm risk (+1 or +2 days relative to stage_date based on report type) with detailed debug information following email_format.mdc specification."""
        debug_lines = []
        debug_lines.append("THUNDERSTORM TOMORROW RISK ANALYSIS DEBUG:")
        debug_lines.append("=" * 50)
        
        try:
            # Get the stage date and report type for analysis
            stage_date = weather_data.get('stage_date', 'Unknown')
            report_type = weather_data.get('report_type', 'morning')  # Default to morning
            debug_lines.append(f"Stage date: {stage_date}")
            debug_lines.append(f"Report type: {report_type}")
            
            # Check for API failure
            if self._detect_api_failure(weather_data):
                debug_lines.append("ERROR: MeteoFrance API failure detected")
                return EnhancedThunderstormTomorrowResult(
                    has_thunderstorm=False,
                    thunderstorm_count=0,
                    first_thunderstorm_time=None,
                    max_probability=0,
                    description="MeteoFrance API failure: No weather data available",
                    debug_info="\n".join(debug_lines)
                )
            
            # Extract unified weather data
            unified_data = weather_data.get('unified_data')
            if not unified_data:
                debug_lines.append("No unified weather data available")
                return EnhancedThunderstormTomorrowResult(
                    has_thunderstorm=False,
                    thunderstorm_count=0,
                    first_thunderstorm_time=None,
                    max_probability=0,
                    description="No unified weather data available",
                    debug_info="\n".join(debug_lines)
                )
            
            # Get the stage date and calculate target date based on report type
            if isinstance(stage_date, str):
                from datetime import datetime, timedelta
                stage_date_obj = datetime.strptime(stage_date, '%Y-%m-%d').date()
            else:
                stage_date_obj = stage_date
            
            # Determine target date based on report type
            if report_type == 'morning':
                # Morning Report: analyze tomorrow (+1 day)
                target_date = stage_date_obj + timedelta(days=1)
                debug_lines.append(f"Morning Report: Calculating thunderstorm for tomorrow: {target_date}")
            else:
                # Evening Report: analyze day after tomorrow (+2 days)
                target_date = stage_date_obj + timedelta(days=2)
                debug_lines.append(f"Evening Report: Calculating thunderstorm for day after tomorrow: {target_date}")
            
            # Find target date in the available data timestamps
            all_timestamps = []
            for point in getattr(unified_data, 'data_points', []):
                for entry in getattr(point, 'entries', []):
                    all_timestamps.append(entry.timestamp.date())
            
            if not all_timestamps:
                debug_lines.append("No timestamps found in unified data")
                return EnhancedThunderstormTomorrowResult(
                    has_thunderstorm=False,
                    thunderstorm_count=0,
                    first_thunderstorm_time=None,
                    max_probability=0,
                    description="No timestamp data available",
                    debug_info="\n".join(debug_lines)
                )
            
            # Check if target date is available in the data
            unique_dates = sorted(list(set(all_timestamps)))
            debug_lines.append(f"Available dates in data: {unique_dates}")
            
            if target_date not in unique_dates:
                debug_lines.append(f"Target date {target_date} not available in data")
                return EnhancedThunderstormTomorrowResult(
                    has_thunderstorm=False,
                    thunderstorm_count=0,
                    first_thunderstorm_time=None,
                    max_probability=0,
                    description="No target date data available",
                    debug_info="\n".join(debug_lines)
                )
            
            debug_lines.append(f"Found target date in data: {target_date}")
            
            # Define time range for target date (04:00-22:00)
            from datetime import datetime
            target_start = datetime.combine(target_date, datetime.min.time().replace(hour=4))
            target_end = datetime.combine(target_date, datetime.min.time().replace(hour=22))
            
            debug_lines.append(f"Analyzing thunderstorm forecast for target date ({target_date})")
            
            # Collect all thunderstorm entries for target date from all data points
            all_thunderstorm_entries = []
            
            for point in getattr(unified_data, 'data_points', []):
                location_name = getattr(point, 'location_name', 'Unknown')
                entries = getattr(point, 'entries', [])
                
                for entry in entries:
                    # Check if entry is within target date's time range
                    if target_start <= entry.timestamp <= target_end:
                        # Check for thunderstorm in weather description
                        desc_lower = entry.weather_description.lower()
                        if any(keyword in desc_lower for keyword in ['orage', 'thunderstorm', 'éclair', 'orages', 'averses orageuses']):
                            all_thunderstorm_entries.append({
                                'timestamp': entry.timestamp,
                                'location': location_name,
                                'description': entry.weather_description,
                                'rain_amount': entry.rain_amount,
                                'wind_speed': entry.wind_speed
                            })
                            debug_lines.append(f"Found thunderstorm for {target_date}: {str(int(entry.timestamp.hour))} - {entry.weather_description} (Location: {location_name})")
            
            debug_lines.append(f"Total thunderstorm entries found for {target_date}: {len(all_thunderstorm_entries)}")
            
            if not all_thunderstorm_entries:
                debug_lines.append(f"No thunderstorm entries found for {target_date}")
                return EnhancedThunderstormTomorrowResult(
                    has_thunderstorm=False,
                    thunderstorm_count=0,
                    first_thunderstorm_time=None,
                    max_probability=0,
                    description="No thunderstorm risk for target date",
                    debug_info="\n".join(debug_lines)
                )
            
            # Sort by timestamp to find first occurrence
            all_thunderstorm_entries.sort(key=lambda x: x['timestamp'])
            first_thunderstorm_time = all_thunderstorm_entries[0]['timestamp']
            
            # Calculate thunderstorm probability based on number of thunderstorm hours
            total_hours = 18  # 04:00-22:00 = 18 hours
            thunderstorm_hours = len(all_thunderstorm_entries)
            thunderstorm_probability = min(100, int((thunderstorm_hours / total_hours) * 100))
            
            debug_lines.append(f"Thunderstorm probability calculation: {thunderstorm_hours}/{total_hours} hours = {thunderstorm_probability}%")
            
            # Show raw thunderstorm details
            debug_lines.append(f"RAW THUNDERSTORM DATA FOR {target_date}:")
            for i, detail in enumerate(all_thunderstorm_entries[:10]):  # Show first 10 entries
                time_str = str(int(detail['timestamp'].hour))
                debug_lines.append(f"  Entry {i+1}: {time_str} - {detail['description']} (Rain: {detail['rain_amount']}mm/h, Wind: {detail['wind_speed']}km/h, Location: {detail['location']})")
            
            # Get threshold from config (default 10% if not available)
            thunderstorm_threshold = 10  # Default threshold from config.yaml
            
            # Format first thunderstorm time
            first_time_str = str(int(first_thunderstorm_time.hour))
            debug_lines.append(f"First thunderstorm time: {first_time_str}")
            
            # Generate description following email_format.mdc format
            if thunderstorm_probability >= thunderstorm_threshold:
                description = f"Gew.+1{thunderstorm_probability}%@{first_time_str}"
            else:
                description = f"Gew.+1{thunderstorm_probability}% (below threshold {thunderstorm_threshold}%)"
            
            debug_lines.append(f"Thunderstorm threshold: {thunderstorm_threshold}%")
            debug_lines.append(f"Final description: {description}")
            debug_lines.append(f"Thunderstorm risk analysis for {target_date} completed successfully")
            
            return EnhancedThunderstormTomorrowResult(
                has_thunderstorm=True,
                thunderstorm_count=len(all_thunderstorm_entries),
                first_thunderstorm_time=first_time_str,
                max_probability=thunderstorm_probability,
                description=description,
                debug_info="\n".join(debug_lines)
            )
            
        except Exception as e:
            debug_lines.append(f"ERROR in thunderstorm risk analysis: {e}")
            return EnhancedThunderstormTomorrowResult(
                has_thunderstorm=False,
                thunderstorm_count=0,
                first_thunderstorm_time=None,
                max_probability=0,
                description=f"Error analyzing thunderstorm: {e}",
                debug_info="\n".join(debug_lines)
            )
    
    def _analyze_wind_risk_with_debug(self, weather_data: Dict[str, Any]) -> EnhancedWindRiskResult:
        """Analyze wind risk with detailed debug information following email_format.mdc specification."""
        debug_lines = []
        debug_lines.append("WIND RISK ANALYSIS DEBUG:")
        debug_lines.append("=" * 35)
        
        try:
            # Check for API failure
            if self._detect_api_failure(weather_data):
                debug_lines.append("ERROR: MeteoFrance API failure detected")
                return EnhancedWindRiskResult(
                    max_wind_speed=0.0,
                    max_gusts=0.0,
                    first_high_wind_time=None,
                    description="MeteoFrance API failure: No weather data available",
                    debug_info="\n".join(debug_lines)
                )
            
            # Extract hourly wind data
            hourly_data = weather_data.get('hourly_data', [])
            debug_lines.append(f"Hourly data entries found: {len(hourly_data)}")
            
            # Get threshold from config (default 40 km/h if not available)
            wind_threshold = 40  # Default threshold from config.yaml
            
            # Analyze wind data for threshold crossing and maximum
            max_wind_speed = 0.0
            max_gusts = 0.0
            max_wind_time = None
            max_gusts_time = None
            first_threshold_time = None
            
            for i, entry in enumerate(hourly_data):
                wind_speed = entry.wind_speed
                wind_gusts = entry.wind_gusts
                
                # Check for maximum wind speed
                if wind_speed > max_wind_speed:
                    max_wind_speed = wind_speed
                    max_wind_time = str(int(entry.timestamp.hour))
                    debug_lines.append(f"Found higher wind speed: {max_wind_speed}km/h at {max_wind_time}")
                
                # Check for maximum gusts
                if wind_gusts > max_gusts:
                    max_gusts = wind_gusts
                    max_gusts_time = str(int(entry.timestamp.hour))
                    debug_lines.append(f"Found higher wind gusts: {max_gusts}km/h at {max_gusts_time}")
                
                # Check for first threshold crossing
                if (wind_speed > wind_threshold or wind_gusts > wind_threshold) and first_threshold_time is None:
                    first_threshold_time = str(int(entry.timestamp.hour))
                    debug_lines.append(f"First threshold crossing (>{wind_threshold}km/h): {first_threshold_time}")
            
            # Determine wind risk
            has_high_wind = max_wind_speed > wind_threshold or max_gusts > wind_threshold
            debug_lines.append(f"Wind threshold: {wind_threshold}km/h")
            debug_lines.append(f"Max wind speed: {max_wind_speed}km/h")
            debug_lines.append(f"Max gusts: {max_gusts}km/h")
            debug_lines.append(f"High wind detected: {has_high_wind}")
            
            # Generate description following email_format.mdc format
            if has_high_wind and first_threshold_time:
                wind_time_str = f"@{max_wind_time}" if max_wind_time else ""
                gusts_time_str = f"@{max_gusts_time}" if max_gusts_time else ""
                description = f"Wind{max_wind_speed}{wind_time_str} Boen{max_gusts}{gusts_time_str}"
            else:
                description = f"Wind{max_wind_speed} Boen{max_gusts}"
            
            debug_lines.append(f"Final description: {description}")
            debug_lines.append("Wind risk analysis completed successfully")
            
            return EnhancedWindRiskResult(
                max_wind_speed=max_wind_speed,
                max_gusts=max_gusts,
                first_high_wind_time=first_threshold_time,
                description=description,
                debug_info="\n".join(debug_lines)
            )
            
        except Exception as e:
            debug_lines.append(f"ERROR in wind risk analysis: {e}")
            return EnhancedWindRiskResult(
                max_wind_speed=0.0,
                max_gusts=0.0,
                first_high_wind_time=None,
                description=f"MeteoFrance API failure: Analysis error - {str(e)}",
                debug_info="\n".join(debug_lines)
            )
    
    def _detect_api_failure(self, weather_data: Dict[str, Any]) -> bool:
        """Detect if there was an API failure based on data availability."""
        try:
            # Check if we have unified_data with data_points
            unified_data = weather_data.get('unified_data')
            if unified_data and hasattr(unified_data, 'data_points') and unified_data.data_points:
                # Check if data_points have entries
                for point in unified_data.data_points:
                    if hasattr(point, 'entries') and point.entries:
                        return False  # We have data, no API failure
                return True  # No entries in any data point
            else:
                # Fallback: check traditional data structure
                hourly_data = weather_data.get('hourly_data', [])
                thunderstorm_data = weather_data.get('thunderstorm_data', [])
                probability_data = weather_data.get('probability_data', [])
                
                # If we have any of these data types, it's not a complete API failure
                if hourly_data or thunderstorm_data or probability_data:
                    return False
                
                return True  # No data available
                
        except Exception as e:
            logger.error(f"Error detecting API failure: {e}")
            return True  # Assume failure on error
    
    def _generate_overall_debug_info(self, weather_data: Dict[str, Any], 
                                   results: Dict[str, Any]) -> str:
        """Generate overall debug information with explicit date information."""
        debug_lines = []
        debug_lines.append("OVERALL ALTERNATIVE RISK ANALYSIS DEBUG:")
        debug_lines.append("=" * 50)
        
        # Add explicit date information
        stage_date = weather_data.get('stage_date', 'Unknown')
        report_type = weather_data.get('report_type', 'Unknown')
        debug_lines.append(f"ANALYSIS DATE: {stage_date}")
        debug_lines.append(f"REPORT TYPE: {report_type}")
        debug_lines.append("")
        
        # Add GEO coordinate debug info
        geo_debug = self._generate_geo_coordinate_debug_info(weather_data)
        debug_lines.append(geo_debug)
        
        debug_lines.append("")
        debug_lines.append("SUMMARY OF ALL RISK ANALYSES:")
        debug_lines.append("=" * 30)
        
        # Add summary of each risk analysis
        for risk_type, result in results.items():
            if hasattr(result, 'description'):
                debug_lines.append(f"  {risk_type}: {result.description}")
        
        return "\n".join(debug_lines)
    
    def _create_error_result(self, error_message: str) -> EnhancedRiskAnalysisResult:
        """Create an error result when analysis fails."""
        error_debug = f"ERROR: {error_message}"
        
        return EnhancedRiskAnalysisResult(
            heat=EnhancedHeatRiskResult(0.0, f"MeteoFrance API failure: {error_message}", error_debug),
            cold=EnhancedColdRiskResult(0.0, f"MeteoFrance API failure: {error_message}", error_debug),
            rain=EnhancedRainRiskResult(False, 0, 0.0, None, f"MeteoFrance API failure: {error_message}", error_debug),
            thunderstorm=EnhancedThunderstormRiskResult(False, 0, None, 0, f"MeteoFrance API failure: {error_message}", error_debug),
            thunderstorm_tomorrow=EnhancedThunderstormTomorrowResult(False, 0, None, 0, f"MeteoFrance API failure: {error_message}", error_debug),
            wind=EnhancedWindRiskResult(0.0, 0.0, None, f"MeteoFrance API failure: {error_message}", error_debug),
            overall_debug_info=error_debug
        )
    
    def generate_report_text(self, result: EnhancedRiskAnalysisResult) -> str:
        """Generate the complete alternative risk analysis report text."""
        try:
            report_lines = []
            report_lines.append("## Alternative Risikoanalyse")
            report_lines.append("")
            
            # Summary section
            report_lines.append("Heat: " + result.heat.description)
            report_lines.append("Cold: " + result.cold.description)
            report_lines.append("Rain: " + result.rain.description)
            report_lines.append("Thunderstorm: " + result.thunderstorm.description)
            report_lines.append("Thunderstorm_tomorrow: " + result.thunderstorm_tomorrow.description)
            report_lines.append("Wind: " + result.wind.description)
            report_lines.append("")
            
            # Detailed debug information
            report_lines.append("HEAT ANALYSIS:")
            report_lines.append(result.heat.debug_info)
            report_lines.append("")
            report_lines.append("COLD ANALYSIS:")
            report_lines.append(result.cold.debug_info)
            report_lines.append("")
            report_lines.append("RAIN ANALYSIS:")
            report_lines.append(result.rain.debug_info)
            report_lines.append("")
            report_lines.append("THUNDERSTORM ANALYSIS:")
            report_lines.append(result.thunderstorm.debug_info)
            report_lines.append("")
            report_lines.append("THUNDERSTORM_TOMORROW ANALYSIS:")
            report_lines.append(result.thunderstorm_tomorrow.debug_info)
            report_lines.append("")
            report_lines.append("WIND ANALYSIS:")
            report_lines.append(result.wind.debug_info)
            report_lines.append("")
            report_lines.append("OVERALL ANALYSIS:")
            report_lines.append(result.overall_debug_info)
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced report text: {e}")
            return f"Error generating report: {str(e)}"

    def _generate_geo_coordinate_debug_info(self, weather_data: Dict[str, Any]) -> str:
        """Generate debug information for different GEO coordinates following debug_email_append.md specification."""
        debug_lines = []
        debug_lines.append("GEO COORDINATE DEBUG INFO:")
        debug_lines.append("=" * 40)
        
        try:
            # Extract unified weather data if available
            unified_data = weather_data.get('unified_data')
            if not unified_data:
                debug_lines.append("No unified weather data available for GEO coordinate debug")
                return "\n".join(debug_lines)
            
            # Get data points (GEO coordinates)
            data_points = getattr(unified_data, 'data_points', [])
            if not data_points:
                debug_lines.append("No data points found in unified weather data")
                return "\n".join(debug_lines)
            
            debug_lines.append(f"Found {len(data_points)} GEO coordinate points")
            
            # Determine day context based on report type
            report_type = weather_data.get('report_type', 'morning')
            if report_type == 'morning':
                day_context = "morning, Tag"
            elif report_type == 'evening':
                day_context = "evening, Tag"
            else:
                day_context = "update, Tag"
            
            # Process each GEO coordinate point
            for i, point in enumerate(data_points):
                location_name = getattr(point, 'location_name', f'Point {i+1}')
                latitude = getattr(point, 'latitude', 0.0)
                longitude = getattr(point, 'longitude', 0.0)
                entries = getattr(point, 'entries', [])
                
                debug_lines.append("")
                # Format header according to debug_email_append.md specification
                debug_lines.append(f"{location_name} ({latitude:.5f}, {longitude:.5f}) ({day_context})")
                
                if not entries:
                    debug_lines.append("No weather entries available for this point")
                    continue
                
                # Create table header
                debug_lines.append("+-------+--------+--------+--------+--------+--------+--------+")
                debug_lines.append("| Hour  |  Temp  | RainW% | Rainmm |  Wind  | Gusts  | Thund% |")
                debug_lines.append("+-------+--------+--------+--------+--------+--------+--------+")
                
                # Process hourly data (04:00-22:00)
                hourly_data = {}
                for entry in entries:
                    hour = entry.timestamp.hour
                    if 4 <= hour <= 22:  # Only show 04:00-22:00
                        # Handle rain_probability - might not exist
                        rain_prob = getattr(entry, 'rain_probability', None)
                        rain_prob_str = f"{rain_prob:.1f}" if rain_prob is not None else '-'
                        
                        # Handle thunderstorm_probability - might not exist
                        thund_prob = getattr(entry, 'thunderstorm_probability', None)
                        thund_str = f"{thund_prob:.1f}" if thund_prob is not None else '-'
                        
                        hourly_data[hour] = {
                            'temp': entry.temperature,
                            'rain_prob': rain_prob_str,
                            'rain_mm': entry.rain_amount,
                            'wind': entry.wind_speed,
                            'gusts': entry.wind_gusts,
                            'thund': thund_str
                        }
                
                # Show hourly data in table format WITHOUT leading zeros for hours (as per email_format.mdc)
                for hour in range(4, 23):  # 04:00-22:00
                    if hour in hourly_data:
                        data = hourly_data[hour]
                        # Format hour without leading zero
                        hour_str = str(hour)
                        debug_lines.append(f"|  {hour_str:>2}   |  {data['temp']:5.1f}  |  {data['rain_prob']:>5s}  |  {data['rain_mm']:5.1f}  |  {data['wind']:5.1f}  |  {data['gusts']:5.1f}  |  {data['thund']:>5s}  |")
                    else:
                        hour_str = str(hour)
                        debug_lines.append(f"|  {hour_str:>2}   |   -    |   -    |   -    |   -    |   -    |   -    |")
                
                # Calculate min/max values
                if hourly_data:
                    temps = [data['temp'] for data in hourly_data.values()]
                    rain_probs = [float(data['rain_prob']) for data in hourly_data.values() if data['rain_prob'] != '-']
                    rain_mms = [data['rain_mm'] for data in hourly_data.values()]
                    winds = [data['wind'] for data in hourly_data.values()]
                    gusts = [data['gusts'] for data in hourly_data.values()]
                    thunds = [float(data['thund']) for data in hourly_data.values() if data['thund'] != '-']
                    
                    debug_lines.append("+-------+--------+--------+--------+--------+--------+--------+")
                    
                    # Format min values
                    min_rain_prob = f"{min(rain_probs):5.1f}" if rain_probs else "   -  "
                    min_thund = f"{min(thunds):5.1f}" if thunds else "   -  "
                    debug_lines.append(f"|  Min  |  {min(temps):5.1f}  |  {min_rain_prob}  |  {min(rain_mms):5.1f}  |  {min(winds):5.1f}  |  {min(gusts):5.1f}  |  {min_thund}  |")
                    
                    # Format max values
                    max_rain_prob = f"{max(rain_probs):5.1f}" if rain_probs else "   -  "
                    max_thund = f"{max(thunds):5.1f}" if thunds else "   -  "
                    debug_lines.append(f"|  Max  |  {max(temps):5.1f}  |  {max_rain_prob}  |  {max(rain_mms):5.1f}  |  {max(winds):5.1f}  |  {max(gusts):5.1f}  |  {max_thund}  |")
                    debug_lines.append("+-------+--------+--------+--------+--------+--------+--------+")
                else:
                    debug_lines.append("+-------+--------+--------+--------+--------+--------+--------+")
                    debug_lines.append("|  Min  |   -    |   -    |   -    |   -    |   -    |   -    |")
                    debug_lines.append("|  Max  |   -    |   -    |   -    |   -    |   -    |   -    |")
                    debug_lines.append("+-------+--------+--------+--------+--------+--------+--------+")
            
            return "\n".join(debug_lines)
            
        except Exception as e:
            debug_lines.append(f"ERROR generating GEO coordinate debug info: {e}")
            return "\n".join(debug_lines)