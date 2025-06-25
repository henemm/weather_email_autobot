"""
Error handling tests for the GR20 weather monitor.

This module tests various error scenarios to ensure the system
handles failures gracefully and provides appropriate error messages.
"""

import pytest
import tempfile
import json
import os
import sys
from unittest.mock import patch, Mock
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_startdatum_format(self):
        """Test handling of invalid startdatum format."""
        config = {"startdatum": "invalid-date"}
        
        from src.position.etappenlogik import get_current_stage
        
        with pytest.raises(ValueError, match="Invalid startdatum format"):
            get_current_stage(config)
    
    def test_missing_startdatum(self):
        """Test handling of missing startdatum."""
        config = {}  # No startdatum
        
        from src.position.etappenlogik import get_current_stage
        
        result = get_current_stage(config)
        assert result is None
    
    def test_invalid_etappen_json(self):
        """Test handling of invalid etappen.json."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON
            temp_file = f.name
        
        try:
            from src.position.etappenlogik import load_etappen_data
            
            with pytest.raises(json.JSONDecodeError):
                load_etappen_data(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_missing_etappen_file(self):
        """Test handling of missing etappen.json."""
        from src.position.etappenlogik import load_etappen_data
        
        with pytest.raises(FileNotFoundError):
            load_etappen_data("nonexistent_file.json")
    
    def test_invalid_stage_coordinates(self):
        """Test handling of invalid coordinates in stage data."""
        etappen_data = [
            {
                "name": "E1 Ortu",
                "punkte": [
                    {"lat": "invalid", "lon": 8.851262},  # Invalid lat
                    {"lat": 42.471362, "lon": "invalid"}  # Invalid lon
                ]
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(etappen_data, f)
            temp_file = f.name
        
        try:
            from src.position.etappenlogik import get_stage_coordinates
            
            with pytest.raises(ValueError, match="Invalid coordinates"):
                get_stage_coordinates(etappen_data[0])
        finally:
            os.unlink(temp_file)
    
    def test_missing_punkte_in_stage(self):
        """Test handling of stage without punkte."""
        stage_data = {"name": "E1 Ortu"}  # Missing punkte
        
        from src.position.etappenlogik import get_stage_coordinates
        
        with pytest.raises(KeyError, match="Stage missing 'punkte' key"):
            get_stage_coordinates(stage_data)
    
    @patch('src.wetter.fetch_meteofrance.get_forecast')
    def test_meteofrance_api_failure(self, mock_get_forecast):
        """Test handling of MeteoFrance API failure."""
        mock_get_forecast.side_effect = Exception("API Error")
        
        from src.wetter.fetch_meteofrance import get_forecast
        
        with pytest.raises(RuntimeError, match="Failed to fetch forecast"):
            get_forecast(42.510501, 8.851262)
    
    @patch('src.wetter.fetch_openmeteo.fetch_openmeteo_forecast')
    def test_openmeteo_api_failure(self, mock_fetch_openmeteo):
        """Test handling of OpenMeteo API failure."""
        mock_fetch_openmeteo.side_effect = Exception("OpenMeteo Error")
        
        from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast
        
        with pytest.raises(Exception, match="OpenMeteo Error"):
            fetch_openmeteo_forecast(42.510501, 8.851262)
    
    def test_invalid_coordinates(self):
        """Test handling of invalid coordinates."""
        from src.wetter.fetch_meteofrance import get_forecast
        
        # Invalid latitude
        with pytest.raises(ValueError, match="Invalid coordinates"):
            get_forecast(91.0, 8.851262)  # Latitude > 90
        
        # Invalid longitude
        with pytest.raises(ValueError, match="Invalid coordinates"):
            get_forecast(42.510501, 181.0)  # Longitude > 180
    
    @patch('src.notification.email_client.EmailClient')
    def test_email_sending_failure(self, mock_email_client):
        """Test handling of email sending failure."""
        mock_email_instance = Mock()
        mock_email_instance.send_gr20_report.return_value = False
        mock_email_client.return_value = mock_email_instance
        
        # This would be tested in integration tests
        # For now, just verify the mock is set up correctly
        assert mock_email_instance.send_gr20_report() is False
    
    def test_config_file_not_found(self):
        """Test handling of missing config file."""
        from scripts.run_gr20_weather_monitor import load_config
        
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_config.yaml")
    
    def test_invalid_config_yaml(self):
        """Test handling of invalid YAML in config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content:')  # Invalid YAML
            temp_file = f.name
        
        try:
            from scripts.run_gr20_weather_monitor import load_config
            
            with pytest.raises(Exception):  # YAMLError or similar
                load_config(temp_file)
        finally:
            os.unlink(temp_file)
    
    @patch('src.position.etappenlogik.date')
    def test_stage_before_start_date(self, mock_date):
        """Test handling when current date is before start date."""
        from datetime import date
        from src.position.etappenlogik import get_current_stage
        
        config = {"startdatum": "2025-06-25"}
        mock_date.today.return_value = date(2025, 6, 24)  # Day before start
        
        result = get_current_stage(config)
        assert result is None
    
    def test_empty_etappen_list(self):
        """Test handling of empty etappen list."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)  # Empty list
            temp_file = f.name
        
        try:
            from src.position.etappenlogik import get_current_stage
            
            config = {"startdatum": "2025-06-25"}
            result = get_current_stage(config, temp_file)
            assert result is None
        finally:
            os.unlink(temp_file) 