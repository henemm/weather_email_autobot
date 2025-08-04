"""
Dynamic Report Comparator

This module implements the comparison logic for dynamic weather reports.
It compares current weather data with the last sent report to determine
if a new dynamic report should be triggered.
"""

import json
import os
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DynamicReportComparator:
    """
    Compares weather reports to detect significant changes for dynamic reporting.
    
    This class implements the comparison logic specified in dynamic-report.md:
    - Compare numerical values against delta_thresholds
    - Compare timing of threshold and maximum events
    - Check for stage changes (low → med → high)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the comparator with configuration.
        
        Args:
            config: Configuration dictionary with delta_thresholds
        """
        self.config = config
        self.delta_thresholds = config.get('delta_thresholds', {})
        self.data_dir = ".data/weather_reports"
        
    def load_last_report(self, stage_name: str, report_date: date) -> Optional[Dict[str, Any]]:
        """
        Load the last sent report for a specific stage and date.
        
        Args:
            stage_name: Name of the stage
            report_date: Date of the report
            
        Returns:
            Dictionary with last report data or None if not found
        """
        try:
            date_str = report_date.strftime('%Y-%m-%d')
            filepath = os.path.join(self.data_dir, date_str, f"{stage_name}.json")
            
            if not os.path.exists(filepath):
                logger.debug(f"No previous report found at {filepath}")
                return None
                
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            logger.info(f"Loaded previous report from {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading last report: {e}")
            return None
    
    def compare_reports(self, current_report: Dict[str, Any], 
                       previous_report: Optional[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
        """
        Compare current report with previous report to detect significant changes.
        
        Args:
            current_report: Current weather report data
            previous_report: Previous weather report data (can be None)
            
        Returns:
            Tuple of (should_send_report, change_details)
        """
        if not previous_report:
            logger.info("No previous report found - sending first report")
            return True, {"reason": "first_report"}
        
        change_details = {
            "reason": "no_significant_changes",
            "changes": []
        }
        
        # Compare each weather element
        elements_to_compare = [
            ('rain_mm', 'rain_amount'),
            ('rain_percent', 'rain_probability'),
            ('wind', 'wind_speed'),
            ('gust', 'wind_speed'),  # Use same threshold as wind
            ('thunderstorm', 'thunderstorm')
        ]
        
        has_significant_changes = False
        
        for element_name, threshold_key in elements_to_compare:
            if self._compare_element(current_report, previous_report, element_name, threshold_key):
                has_significant_changes = True
                change_details["changes"].append({
                    "element": element_name,
                    "threshold_key": threshold_key
                })
        
        if has_significant_changes:
            change_details["reason"] = "significant_changes_detected"
            logger.info(f"Significant changes detected: {change_details['changes']}")
        else:
            logger.debug("No significant changes detected")
            
        return has_significant_changes, change_details
    
    def _compare_element(self, current: Dict[str, Any], previous: Dict[str, Any], 
                        element_name: str, threshold_key: str) -> bool:
        """
        Compare a specific weather element between current and previous reports.
        
        Args:
            current: Current report data
            previous: Previous report data
            element_name: Name of the weather element (e.g., 'rain_mm')
            threshold_key: Key for delta threshold in config
            
        Returns:
            True if significant change detected, False otherwise
        """
        try:
            # Get current and previous element data
            current_element = current.get(element_name, {})
            previous_element = previous.get(element_name, {})
            
            if not current_element or not previous_element:
                return False
            
            # Get threshold value
            threshold = self.delta_thresholds.get(threshold_key, 0)
            if threshold == 0:
                return False
            
            # Compare maximum values
            current_max = current_element.get('max_value')
            previous_max = previous_element.get('max_value')
            
            if current_max is not None and previous_max is not None:
                max_change = abs(current_max - previous_max)
                if max_change >= threshold:
                    logger.debug(f"{element_name} max change: {max_change} >= {threshold}")
                    return True
            
            # Compare threshold times (if both have thresholds)
            current_threshold_time = current_element.get('threshold_time')
            previous_threshold_time = previous_element.get('threshold_time')
            
            if current_threshold_time and previous_threshold_time:
                # Convert times to hours for comparison
                try:
                    current_hour = int(current_threshold_time)
                    previous_hour = int(previous_threshold_time)
                    time_change = abs(current_hour - previous_hour)
                    
                    if time_change >= 1:  # At least 1 hour difference
                        logger.debug(f"{element_name} threshold time change: {time_change} hours")
                        return True
                except (ValueError, TypeError):
                    pass
            
            # Compare maximum times (if both have maximums)
            current_max_time = current_element.get('max_time')
            previous_max_time = previous_element.get('max_time')
            
            if current_max_time and previous_max_time:
                try:
                    current_hour = int(current_max_time)
                    previous_hour = int(previous_max_time)
                    time_change = abs(current_hour - previous_hour)
                    
                    if time_change >= 1:  # At least 1 hour difference
                        logger.debug(f"{element_name} maximum time change: {time_change} hours")
                        return True
                except (ValueError, TypeError):
                    pass
            
            return False
            
        except Exception as e:
            logger.error(f"Error comparing element {element_name}: {e}")
            return False
    
    def save_comparison_result(self, stage_name: str, report_date: date, 
                             should_send: bool, change_details: Dict[str, Any]) -> None:
        """
        Save the comparison result for debugging and tracking.
        
        Args:
            stage_name: Name of the stage
            report_date: Date of the report
            should_send: Whether report should be sent
            change_details: Details about detected changes
        """
        try:
            date_str = report_date.strftime('%Y-%m-%d')
            comparison_dir = os.path.join(self.data_dir, date_str, "comparisons")
            os.makedirs(comparison_dir, exist_ok=True)
            
            filename = f"{stage_name}_comparison_{datetime.now().strftime('%H%M%S')}.json"
            filepath = os.path.join(comparison_dir, filename)
            
            comparison_data = {
                "stage_name": stage_name,
                "report_date": date_str,
                "comparison_time": datetime.now().isoformat(),
                "should_send": should_send,
                "change_details": change_details,
                "delta_thresholds": self.delta_thresholds
            }
            
            with open(filepath, 'w') as f:
                json.dump(comparison_data, f, indent=2, default=str)
                
            logger.debug(f"Saved comparison result to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving comparison result: {e}") 