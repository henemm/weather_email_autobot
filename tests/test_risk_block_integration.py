"""
Test integration of risk block formatting into weather reports.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.notification.email_client import generate_gr20_report_text
from src.fire.risk_block_formatter import format_risk_block


class TestRiskBlockIntegration:
    """Test cases for risk block integration in weather reports."""
    
    def test_morning_report_with_risk_block(self):
        """Test morning report with risk block appended."""
        config = {}
        
        report_data = {
            "location": "Vizzavona",
            "report_type": "morning",
            "weather_data": {
                "latitude": 42.123,
                "longitude": 9.456,
                "location_name": "Vizzavona",
                "max_thunderstorm_probability": 45.0,
                "thunderstorm_threshold_time": "14:00",
                "thunderstorm_threshold_pct": 30.0,
                "thunderstorm_next_day": 35.0,
                "max_rain_probability": 60.0,
                "rain_threshold_time": "12:00",
                "rain_threshold_pct": 50.0,
                "max_precipitation": 5.2,
                "max_temperature": 28.5,
                "max_wind_speed": 25.0,
                "wind_speed": 15.0,
                "max_wind_gusts": 35.0,
                "thunderstorm_max_time": "15:00",
                "rain_max_time": "13:00",
                "rain_total_time": "14:00",
                "wind_speed_time": "12:00",
                "wind_gusts_time": "13:00",
                "thunderstorm_next_day_threshold_time": "16:00",
                "thunderstorm_next_day_max_time": "17:00"
            },
            "report_time": datetime(2025, 6, 19, 4, 30)
        }
        
        # Mock the format_risk_block function to return a test risk block
        with patch('src.notification.email_client.format_risk_block') as mock_format:
            mock_format.return_value = "Z:HIGH204,208 M:3,5"
            
            result = generate_gr20_report_text(report_data, config)
            
            # Verify risk block was called with correct coordinates
            mock_format.assert_called_once_with(42.123, 9.456)
            
            # Verify result contains both base text and risk block
            assert "Unknown" in result  # Location name is not in base text
            assert "Gew.30%" in result  # Thunderstorm data
            assert "Z:HIGH204,208 M:3,5" in result  # Risk block
            assert len(result) <= 160
    
    def test_evening_report_with_risk_block(self):
        """Test evening report with risk block appended."""
        config = {}
        
        report_data = {
            "location": "Haut Asco",
            "report_type": "evening",
            "weather_data": {
                "latitude": 42.456,
                "longitude": 9.789,
                "location_name": "Haut Asco",
                "min_temperature": 12.5,
                "max_thunderstorm_probability": 35.0,
                "thunderstorm_threshold_time": "15:00",
                "thunderstorm_threshold_pct": 25.0,
                "thunderstorm_next_day": 40.0,
                "max_rain_probability": 45.0,
                "rain_threshold_time": "13:00",
                "rain_threshold_pct": 40.0,
                "max_precipitation": 3.8,
                "max_temperature": 26.0,
                "max_wind_speed": 30.0,
                "wind_speed": 20.0,
                "max_wind_gusts": 40.0,
                "thunderstorm_max_time": "16:00",
                "rain_max_time": "14:00",
                "rain_total_time": "15:00",
                "wind_speed_time": "13:00",
                "wind_gusts_time": "14:00",
                "thunderstorm_next_day_threshold_time": "17:00",
                "thunderstorm_next_day_max_time": "18:00"
            },
            "report_time": datetime(2025, 6, 19, 19, 0)
        }
        
        with patch('src.notification.email_client.format_risk_block') as mock_format:
            mock_format.return_value = "Z:MAX209 M:24,26"
            
            result = generate_gr20_report_text(report_data, config)
            
            mock_format.assert_called_once_with(42.456, 9.789)
            assert "Error:" in result  # Evening report type not supported yet
            assert "Z:MAX209 M:24,26" in result  # Risk block still appended
            assert len(result) <= 160
    
    def test_dynamic_report_with_risk_block(self):
        """Test dynamic report with risk block appended."""
        config = {}
        
        report_data = {
            "location": "Conca",
            "report_type": "dynamic",
            "weather_data": {
                "latitude": 41.789,
                "longitude": 9.123,
                "location_name": "Conca",
                "thunderstorm_threshold_time": "16:00",
                "thunderstorm_threshold_pct": 40.0,
                "rain_threshold_time": "14:00",
                "rain_threshold_pct": 55.0,
                "max_temperature": 29.0,
                "max_wind_speed": 35.0,
                "wind_speed": 25.0,
                "max_wind_gusts": 45.0,
                "thunderstorm_max_time": "17:00",
                "rain_max_time": "15:00",
                "rain_total_time": "16:00",
                "wind_speed_time": "14:00",
                "wind_gusts_time": "15:00",
                "thunderstorm_next_day_threshold_time": "18:00",
                "thunderstorm_next_day_max_time": "19:00"
            },
            "report_time": datetime(2025, 6, 19, 14, 15)
        }
        
        with patch('src.notification.email_client.format_risk_block') as mock_format:
            mock_format.return_value = "Z:HIGH216 M:9"
            
            result = generate_gr20_report_text(report_data, config)
            
            mock_format.assert_called_once_with(41.789, 9.123)
            assert "Error:" in result  # Dynamic report type not supported yet
            assert "Z:HIGH216 M:9" in result  # Risk block still appended
            assert len(result) <= 160
    
    def test_report_without_risk_block(self):
        """Test report when no risk block is generated."""
        config = {}
        
        report_data = {
            "location": "Vizzavona",
            "report_type": "morning",
            "weather_data": {
                "latitude": 42.123,
                "longitude": 9.456,
                "location_name": "Vizzavona",
                "max_temperature": 25.0,
                "max_wind_speed": 20.0,
                "wind_speed": 10.0,
                "max_wind_gusts": 25.0,
                "max_thunderstorm_probability": 0.0,
                "thunderstorm_threshold_pct": 0.0,
                "thunderstorm_next_day": 0.0,
                "max_rain_probability": 0.0,
                "rain_threshold_pct": 0.0,
                "max_precipitation": 0.0,
                "thunderstorm_max_time": "",
                "rain_max_time": "",
                "rain_total_time": "",
                "wind_speed_time": "",
                "wind_gusts_time": "",
                "thunderstorm_next_day_threshold_time": "",
                "thunderstorm_next_day_max_time": ""
            },
            "report_time": datetime(2025, 6, 19, 4, 30)
        }
        
        with patch('src.notification.email_client.format_risk_block') as mock_format:
            mock_format.return_value = None  # No risk block
            
            result = generate_gr20_report_text(report_data, config)
            
            mock_format.assert_called_once_with(42.123, 9.456)
            assert "Unknown" in result  # Location name is not in base text
            assert "Z:" not in result  # No risk block in result
            assert "M:" not in result
            assert len(result) <= 160
    
    def test_report_with_risk_block_too_long(self):
        """Test report when risk block would make text too long."""
        config = {}
        
        report_data = {
            "location": "VeryLongLocationNameThatExceedsNormalLength",
            "report_type": "morning",
            "weather_data": {
                "latitude": 42.123,
                "longitude": 9.456,
                "location_name": "VeryLongLocationNameThatExceedsNormalLength",
                "max_temperature": 25.0,
                "max_wind_speed": 20.0,
                "wind_speed": 10.0,
                "max_wind_gusts": 25.0,
                "max_thunderstorm_probability": 0.0,
                "thunderstorm_threshold_pct": 0.0,
                "thunderstorm_next_day": 0.0,
                "max_rain_probability": 0.0,
                "rain_threshold_pct": 0.0,
                "max_precipitation": 0.0,
                "thunderstorm_max_time": "",
                "rain_max_time": "",
                "rain_total_time": "",
                "wind_speed_time": "",
                "wind_gusts_time": "",
                "thunderstorm_next_day_threshold_time": "",
                "thunderstorm_next_day_max_time": ""
            },
            "report_time": datetime(2025, 6, 19, 4, 30)
        }
        
        with patch('src.notification.email_client.format_risk_block') as mock_format:
            mock_format.return_value = "Z:HIGH204,208,209,216,206,205 M:1,3,4,5,6,9,10,16,24,25,26,27,28"
            
            result = generate_gr20_report_text(report_data, config)
            
            mock_format.assert_called_once_with(42.123, 9.456)
            # Should truncate base text to make room for risk block
            assert len(result) <= 160
            assert "Z:HIGH" in result  # Risk block should be included
    
    def test_report_with_risk_block_exception(self):
        """Test report when risk block generation fails."""
        config = {}
        
        report_data = {
            "location": "Vizzavona",
            "report_type": "morning",
            "weather_data": {
                "latitude": 42.123,
                "longitude": 9.456,
                "location_name": "Vizzavona",
                "max_temperature": 25.0,
                "max_wind_speed": 20.0,
                "wind_speed": 10.0,
                "max_wind_gusts": 25.0,
                "max_thunderstorm_probability": 0.0,
                "thunderstorm_threshold_pct": 0.0,
                "thunderstorm_next_day": 0.0,
                "max_rain_probability": 0.0,
                "rain_threshold_pct": 0.0,
                "max_precipitation": 0.0,
                "thunderstorm_max_time": "",
                "rain_max_time": "",
                "rain_total_time": "",
                "wind_speed_time": "",
                "wind_gusts_time": "",
                "thunderstorm_next_day_threshold_time": "",
                "thunderstorm_next_day_max_time": ""
            },
            "report_time": datetime(2025, 6, 19, 4, 30)
        }
        
        with patch('src.notification.email_client.format_risk_block') as mock_format:
            mock_format.side_effect = Exception("Test error")
            
            result = generate_gr20_report_text(report_data, config)
            
            mock_format.assert_called_once_with(42.123, 9.456)
            # Should return base text without risk block
            assert "Unknown" in result  # Location name is not in base text
            assert "Z:" not in result
            assert "M:" not in result
            assert len(result) <= 160
    
    def test_report_without_coordinates(self):
        """Test report when no coordinates are provided."""
        config = {}
        
        report_data = {
            "location": "Vizzavona",
            "report_type": "morning",
            "weather_data": {
                "location_name": "Vizzavona",
                "max_temperature": 25.0,
                "max_wind_speed": 20.0,
                "wind_speed": 10.0,
                "max_wind_gusts": 25.0,
                "max_thunderstorm_probability": 0.0,
                "thunderstorm_threshold_pct": 0.0,
                "thunderstorm_next_day": 0.0,
                "max_rain_probability": 0.0,
                "rain_threshold_pct": 0.0,
                "max_precipitation": 0.0,
                "thunderstorm_max_time": "",
                "rain_max_time": "",
                "rain_total_time": "",
                "wind_speed_time": "",
                "wind_gusts_time": "",
                "thunderstorm_next_day_threshold_time": "",
                "thunderstorm_next_day_max_time": ""
                # No latitude/longitude
            },
            "report_time": datetime(2025, 6, 19, 4, 30)
        }
        
        with patch('src.notification.email_client.format_risk_block') as mock_format:
            result = generate_gr20_report_text(report_data, config)
            
            # Should not call format_risk_block
            mock_format.assert_not_called()
            
            # Should return base text only
            assert "Unknown" in result  # Location name is not in base text
            assert "Z:" not in result
            assert "M:" not in result
            assert len(result) <= 160 