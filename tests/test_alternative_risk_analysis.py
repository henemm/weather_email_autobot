"""
Tests for alternative risk analysis module.

This module tests the alternative risk analysis that uses direct MeteoFrance API data
without traditional thresholds (except for rain).
"""

import pytest
from datetime import datetime, date
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch

from src.risiko.alternative_risk_analysis import (
    AlternativeRiskAnalyzer,
    RiskAnalysisResult,
    WeatherRiskType,
    ThunderstormTime
)


class TestAlternativeRiskAnalyzer:
    """Test cases for AlternativeRiskAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use default config values for testing
        config = {
            'wind_gust_threshold': 10.0,
            'wind_gust_percentage': 50.0
        }
        self.analyzer = AlternativeRiskAnalyzer(config)
    
    def test_analyze_heat_risk_with_meteofrance_data(self):
        """Test heat risk analysis with valid MeteoFrance data."""
        weather_data = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 12, 0).timestamp()),
                    'T': {'value': 28.5}
                },
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'T': {'value': 32.1}
                },
                {
                    'dt': int(datetime(2024, 6, 21, 16, 0).timestamp()),
                    'T': {'value': 30.8}
                }
            ]
        }
        
        result = self.analyzer.analyze_heat_risk(weather_data)
        
        assert result.max_temperature == 32.1
        assert "32.1°C" in result.description
    
    def test_analyze_cold_risk_with_meteofrance_data(self):
        """Test cold risk analysis with valid MeteoFrance data."""
        weather_data = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 22, 0).timestamp()),
                    'T': {'value': 18.2}
                },
                {
                    'dt': int(datetime(2024, 6, 22, 2, 0).timestamp()),
                    'T': {'value': 12.5}
                },
                {
                    'dt': int(datetime(2024, 6, 22, 6, 0).timestamp()),
                    'T': {'value': 15.8}
                }
            ]
        }
        
        result = self.analyzer.analyze_cold_risk(weather_data)
        
        assert result.min_temperature == 12.5
        assert "12.5°C" in result.description
    
    def test_analyze_rain_risk_with_timing_information(self):
        """Test rain risk analysis with MeteoFrance data including timing."""
        weather_data = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'rain': {'1h': 0.5},
                    'weather': {'desc': 'Ciel dégagé'}
                },
                {
                    'dt': int(datetime(2024, 6, 21, 15, 0).timestamp()),
                    'rain': {'1h': 2.5},
                    'weather': {'desc': 'Averses de pluie'}
                },
                {
                    'dt': int(datetime(2024, 6, 21, 16, 0).timestamp()),
                    'rain': {'1h': 1.8},
                    'weather': {'desc': 'Pluie modérée'}
                }
            ]
        }
        
        result = self.analyzer.analyze_rain_risk(weather_data)
        
        assert result.max_precipitation == 2.5
        assert "2.5mm/h" in result.description
        assert result.probability_max_time == "15"  # Hour of max precipitation
    
    def test_analyze_thunderstorm_risk_with_cape(self):
        """Test thunderstorm risk analysis with MeteoFrance data including CAPE."""
        weather_data = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'weather': {'desc': 'Risque d\'orages'},
                    'cape': 850.0
                },
                {
                    'dt': int(datetime(2024, 6, 21, 15, 0).timestamp()),
                    'weather': {'desc': 'Orages lourds'},
                    'cape': 1200.0
                },
                {
                    'dt': int(datetime(2024, 6, 21, 16, 0).timestamp()),
                    'weather': {'desc': 'Ciel dégagé'},
                    'cape': 200.0
                }
            ]
        }
        
        result = self.analyzer.analyze_thunderstorm_risk(weather_data)
        
        assert result.has_risk
        assert len(result.thunderstorm_times) == 2
        assert result.max_cape == 1200.0
        assert "Orages lourds@15h" in result.description
        assert "Risque d'orages@14h" in result.description
    
    def test_analyze_wind_risk_with_timing(self):
        """Test wind risk analysis with MeteoFrance data including timing."""
        weather_data = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 12, 0).timestamp()),
                    'wind': {'speed': 15.0, 'gust': 25.0}
                },
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'wind': {'speed': 20.0, 'gust': 35.0}
                },
                {
                    'dt': int(datetime(2024, 6, 21, 16, 0).timestamp()),
                    'wind': {'speed': 18.0, 'gust': 28.0}
                }
            ]
        }
        
        result = self.analyzer.analyze_wind_risk(weather_data)
        
        assert result.max_wind_speed == 20.0
        assert result.max_wind_gusts == 35.0
        assert result.has_risk  # 35 km/h > 30 km/h threshold
        assert "35.0 km/h gusts" in result.description
        assert result.wind_speed_time == "14"
        assert result.wind_gusts_time == "14"
    
    def test_analyze_all_risks_complete_analysis(self):
        """Test complete risk analysis with all MeteoFrance data."""
        weather_data = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 12, 0).timestamp()),
                    'T': {'value': 28.0},
                    'rain': {'1h': 0.0},
                    'wind': {'speed': 15.0, 'gust': 25.0},
                    'weather': {'desc': 'Ciel dégagé'}
                },
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'T': {'value': 32.0},
                    'rain': {'1h': 2.5},
                    'wind': {'speed': 20.0, 'gust': 35.0},
                    'weather': {'desc': 'Averses orageuses'},
                    'cape': 900.0
                }
            ]
        }
        
        result = self.analyzer.analyze_all_risks(weather_data)
        
        assert result.heat_risk.max_temperature == 32.0
        assert result.rain_risk.max_precipitation == 2.5
        assert result.thunderstorm_risk.has_risk
        assert result.wind_risk.has_risk
    
    def test_analyze_all_risks_with_missing_data(self):
        """Test risk analysis with missing MeteoFrance data."""
        weather_data = {
            'forecast': []
        }
        
        result = self.analyzer.analyze_all_risks(weather_data)
        
        assert "MeteoFrance API failure" in result.heat_risk.description
        assert "MeteoFrance API failure" in result.cold_risk.description
        # Rain risk doesn't show API failure when no data, it shows default values
        assert result.rain_risk.max_probability == 0.0
        assert result.rain_risk.max_precipitation == 0.0
        # Thunderstorm risk shows default message when no data
        assert result.thunderstorm_risk.has_risk == False
        assert "No thunderstorm conditions detected" in result.thunderstorm_risk.description
        # Wind risk shows default values when no data
        assert result.wind_risk.max_wind_speed == 0.0
        assert result.wind_risk.max_wind_gusts == 0.0
    
    def test_generate_report_text_with_timing(self):
        """Test report text generation with timing information."""
        weather_data = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'T': {'value': 32.0},
                    'rain': {'1h': 2.5},
                    'wind': {'speed': 20.0, 'gust': 35.0},
                    'weather': {'desc': 'Orages lourds'},
                    'cape': 900.0
                }
            ]
        }
        
        result = self.analyzer.analyze_all_risks(weather_data)
        report_text = self.analyzer.generate_report_text(result)
        
        assert "Heat" in report_text
        assert "Heat32" in report_text  # New format without °C
        # Rain risk is not detected because probability is only 10% (estimated from weather desc)
        assert "Rain10%" in report_text  # New format
        assert "Rain2mm" in report_text  # New format
        assert "Gew:High14" in report_text  # New format
        assert "Wind20@14(35@14)" in report_text  # New format with gusts
    
    def test_analyze_heat_risk_with_zero_temperature(self):
        """Test heat risk analysis with 0°C temperature (should be flagged as error)."""
        weather_data = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 12, 0).timestamp()),
                    'T': {'value': 0.0}
                }
            ]
        }
        
        result = self.analyzer.analyze_heat_risk(weather_data)
        
        # Should detect temperature failure and return API failure message
        assert "MeteoFrance API failure" in result.description 
    
    def test_rain_threshold_timing_issue(self):
        """Test rain threshold timing to verify the reported issue with Rain20%@20 vs Rain20%@17."""
        # Create debug data structure similar to what the user reported
        debug_data = {
            'probability_data': {
                'Petra_P2': [
                    {'time': '11:00', 'rain_3h': None},
                    {'time': '14:00', 'rain_3h': 0},
                    {'time': '17:00', 'rain_3h': 20},  # First threshold crossing (15%)
                    {'time': '20:00', 'rain_3h': 10},
                    {'time': '23:00', 'rain_3h': 0}
                ]
            },
            'report_type': 'morning',
            'stage_date': '2024-06-21'
        }
        
        # Analyze the data
        result = self.analyzer.analyze_from_debug_data(debug_data)
        
        # Verify that the threshold time is correctly identified as 17:00
        assert result.rain_risk.probability_threshold_time == "17:00"
        assert result.rain_risk.max_probability == 20.0
        assert result.rain_risk.probability_max_time == "17:00"
        
        # Generate report text and verify format
        report_text = self.analyzer.generate_report_text(result, debug_data)
        assert "Rain20%@17" in report_text  # Should show threshold time, not max time 
    
    def test_wind_formatting_scenarios(self):
        """Test wind formatting for different scenarios."""
        # Test case 1: Wind speed and gusts are similar (no separate gust display)
        weather_data_1 = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'T': {'value': 25.0},
                    'wind': {'speed': 15.0, 'gust': 18.0},  # Gusts only 20% higher (below 50% threshold)
                }
            ]
        }
        
        result_1 = self.analyzer.analyze_all_risks(weather_data_1)
        report_text_1 = self.analyzer.generate_report_text(result_1)
        
        # Should show only wind speed, no separate gusts
        assert "Wind15@14" in report_text_1
        assert "(18@14)" not in report_text_1
        
        # Test case 2: Wind gusts significantly higher than speed
        weather_data_2 = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'T': {'value': 25.0},
                    'wind': {'speed': 10.0, 'gust': 25.0},  # Gusts 150% higher
                }
            ]
        }
        
        result_2 = self.analyzer.analyze_all_risks(weather_data_2)
        report_text_2 = self.analyzer.generate_report_text(result_2)
        
        # Should show both wind speed and gusts
        assert "Wind10@14(25@14)" in report_text_2
        
        # Test case 3: Wind gusts with 10+ km/h difference
        weather_data_3 = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'T': {'value': 25.0},
                    'wind': {'speed': 5.0, 'gust': 16.0},  # 11 km/h difference
                }
            ]
        }
        
        result_3 = self.analyzer.analyze_all_risks(weather_data_3)
        report_text_3 = self.analyzer.generate_report_text(result_3)
        
        # Should show both wind speed and gusts due to 10+ km/h difference
        assert "Wind5@14(16@14)" in report_text_3 
    
    def test_wind_gust_configuration(self):
        """Test wind gust formatting with different configuration values."""
        # Test with custom configuration
        custom_config = {
            'wind_gust_threshold': 5.0,  # Lower threshold
            'wind_gust_percentage': 25.0  # Lower percentage
        }
        custom_analyzer = AlternativeRiskAnalyzer(custom_config)
        
        # Test case 1: Wind gusts with 6 km/h difference (above 5 km/h threshold, below 50% threshold)
        weather_data_1 = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'T': {'value': 25.0},
                    'wind': {'speed': 20.0, 'gust': 26.0},  # 6 km/h difference, 30% higher
                }
            ]
        }
        
        result_1 = custom_analyzer.analyze_all_risks(weather_data_1)
        report_text_1 = custom_analyzer.generate_report_text(result_1)
        
        # Should show gusts because 6 km/h > 5 km/h threshold
        assert "Wind20@14(26@14)" in report_text_1
        
        # Test with default configuration (should not show gusts for same data)
        default_config = {
            'wind_gust_threshold': 10.0,
            'wind_gust_percentage': 50.0
        }
        default_analyzer = AlternativeRiskAnalyzer(default_config)
        result_default = default_analyzer.analyze_all_risks(weather_data_1)
        report_text_default = default_analyzer.generate_report_text(result_default)
        
        # Should not show gusts because 6 km/h < 10 km/h threshold
        assert "Wind20@14" in report_text_default
        assert "(26@14)" not in report_text_default
        
        # Test case 2: Wind gusts with percentage threshold
        weather_data_2 = {
            'forecast': [
                {
                    'dt': int(datetime(2024, 6, 21, 14, 0).timestamp()),
                    'T': {'value': 25.0},
                    'wind': {'speed': 10.0, 'gust': 16.0},  # 6 km/h difference, 60% higher
                }
            ]
        }
        
        result_2 = default_analyzer.analyze_all_risks(weather_data_2)
        report_text_2 = default_analyzer.generate_report_text(result_2)
        
        # Should show gusts because 60% > 50% threshold
        assert "Wind10@14(16@14)" in report_text_2 