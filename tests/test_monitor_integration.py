"""
Integration tests for the complete GR20 weather monitor.

This module tests the full workflow from stage selection to weather report generation
and email sending for all modes (morning, evening, dynamic).
"""

import pytest
import tempfile
import json
import os
import sys
from datetime import datetime, date
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wetter.fetch_meteofrance import ForecastResult
from model.datatypes import WeatherData, WeatherPoint


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "startdatum": "2025-06-25",
        "smtp": {
            "host": "smtp.gmail.com",
            "port": 587,
            "user": "test@example.com",
            "to": "test@example.com",
            "subject": "Test Weather Report"
        },
        "thresholds": {
            "rain_probability": 25.0,
            "rain_amount": 2.0,
            "thunderstorm_probability": 20.0,
            "wind_speed": 20.0,
            "temperature": 32.0,
            "cloud_cover": 90.0
        },
        "delta_thresholds": {
            "thunderstorm_probability": 20.0,
            "rain_probability": 30.0,
            "wind_speed": 10.0,
            "temperature": 2.0
        },
        "min_interval_min": 30,
        "max_daily_reports": 3
    }


@pytest.fixture
def temp_etappen_file():
    """Create a temporary etappen.json file for testing."""
    etappen_data = [
        {
            "name": "E1 Ortu",
            "punkte": [
                {"lat": 42.510501, "lon": 8.851262},
                {"lat": 42.471362, "lon": 8.897105}
            ]
        },
        {
            "name": "E2 Carozzu",
            "punkte": [
                {"lat": 42.465338, "lon": 8.906787},
                {"lat": 42.463894, "lon": 8.894516}
            ]
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(etappen_data, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)


@pytest.fixture
def mock_weather_data():
    """Create mock weather data for testing."""
    point = WeatherPoint(
        latitude=42.510501,
        longitude=8.851262,
        elevation=0.0,
        time=datetime.now(),
        temperature=25.5,
        feels_like=25.5,
        precipitation=0.0,
        thunderstorm_probability=15,
        wind_speed=10.0,
        wind_direction=180.0,
        cloud_cover=30.0
    )
    return WeatherData(points=[point])


class TestMonitorIntegration:
    """Integration tests for the complete monitor workflow."""
    
    @patch('src.position.etappenlogik.date')
    @patch('src.wetter.fetch_meteofrance.get_forecast')
    @patch('src.wetter.fetch_openmeteo.fetch_openmeteo_forecast')
    @patch('src.notification.email_client.EmailClient')
    def test_morning_report_success(self, mock_email_client, mock_openmeteo, 
                                   mock_meteofrance, mock_date, sample_config, temp_etappen_file):
        """Test successful morning report generation."""
        # Setup mocks
        mock_date.today.return_value = date(2025, 6, 25)
        
        forecast_result = ForecastResult(
            temperature=25.5,
            weather_condition="sunny",
            precipitation_probability=15,
            timestamp="2025-06-25T19:00:00",
            data_source="meteofrance-api"
        )
        mock_meteofrance.return_value = forecast_result
        
        openmeteo_data = {
            "current": {
                "temperature_2m": 25.0,
                "precipitation": 0.0,
                "wind_speed_10m": 10.0,
                "time": "2025-06-25T19:00:00"
            }
        }
        mock_openmeteo.return_value = openmeteo_data
        
        mock_email_instance = Mock()
        mock_email_instance.send_gr20_report.return_value = True
        mock_email_client.return_value = mock_email_instance
        
        # Import and run the monitor
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        
        # Mock the config loading to use our test config
        with patch('scripts.run_gr20_weather_monitor.load_config') as mock_load_config:
            mock_load_config.return_value = sample_config
            
            # Mock etappen.json path
            with patch('src.position.etappenlogik.load_etappen_data') as mock_load_etappen:
                with open(temp_etappen_file, 'r') as f:
                    mock_load_etappen.return_value = json.load(f)
                
                # Run the monitor
                from scripts.run_gr20_weather_monitor import main
                
                # Mock command line arguments
                with patch('sys.argv', ['run_gr20_weather_monitor.py', '--modus', 'morning']):
                    main()
        
        # Verify email was sent
        mock_email_instance.send_gr20_report.assert_called_once()
        call_args = mock_email_instance.send_gr20_report.call_args[0][0]
        assert call_args["location"] == "E1 Ortu"
        assert call_args["report_type"] == "morning"
    
    @patch('src.position.etappenlogik.date')
    @patch('src.wetter.fetch_meteofrance.get_forecast')
    @patch('src.notification.email_client.EmailClient')
    def test_evening_report_success(self, mock_email_client, mock_meteofrance, 
                                   mock_date, sample_config, temp_etappen_file):
        """Test successful evening report generation."""
        # Setup mocks
        mock_date.today.return_value = date(2025, 6, 25)
        
        forecast_result = ForecastResult(
            temperature=28.0,
            weather_condition="partly_cloudy",
            precipitation_probability=25,
            timestamp="2025-06-25T19:00:00",
            data_source="meteofrance-api"
        )
        mock_meteofrance.return_value = forecast_result
        
        mock_email_instance = Mock()
        mock_email_instance.send_gr20_report.return_value = True
        mock_email_client.return_value = mock_email_instance
        
        # Import and run the monitor
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        
        with patch('scripts.run_gr20_weather_monitor.load_config') as mock_load_config:
            mock_load_config.return_value = sample_config
            
            with patch('src.position.etappenlogik.load_etappen_data') as mock_load_etappen:
                with open(temp_etappen_file, 'r') as f:
                    mock_load_etappen.return_value = json.load(f)
                
                from scripts.run_gr20_weather_monitor import main
                
                with patch('sys.argv', ['run_gr20_weather_monitor.py', '--modus', 'evening']):
                    main()
        
        # Verify email was sent
        mock_email_instance.send_gr20_report.assert_called_once()
        call_args = mock_email_instance.send_gr20_report.call_args[0][0]
        assert call_args["location"] == "E1 Ortu"
        assert call_args["report_type"] == "evening"
    
    @patch('src.position.etappenlogik.date')
    @patch('src.wetter.fetch_meteofrance.get_forecast')
    @patch('src.notification.email_client.EmailClient')
    def test_dynamic_report_constraints(self, mock_email_client, mock_meteofrance, 
                                       mock_date, sample_config, temp_etappen_file):
        """Test dynamic report with constraints (time interval, daily limit)."""
        # Setup mocks
        mock_date.today.return_value = date(2025, 6, 25)
        
        forecast_result = ForecastResult(
            temperature=30.0,
            weather_condition="thunderstorm",
            precipitation_probability=80,
            timestamp="2025-06-25T19:00:00",
            data_source="meteofrance-api"
        )
        mock_meteofrance.return_value = forecast_result
        
        mock_email_instance = Mock()
        mock_email_instance.send_gr20_report.return_value = True
        mock_email_client.return_value = mock_email_instance
        
        # Import and run the monitor
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        
        with patch('scripts.run_gr20_weather_monitor.load_config') as mock_load_config:
            mock_load_config.return_value = sample_config
            
            with patch('src.position.etappenlogik.load_etappen_data') as mock_load_etappen:
                with open(temp_etappen_file, 'r') as f:
                    mock_load_etappen.return_value = json.load(f)
                
                from scripts.run_gr20_weather_monitor import main
                
                with patch('sys.argv', ['run_gr20_weather_monitor.py', '--modus', 'dynamic']):
                    main()
        
        # Verify email was sent (if constraints are met)
        mock_email_instance.send_gr20_report.assert_called_once()
        call_args = mock_email_instance.send_gr20_report.call_args[0][0]
        assert call_args["location"] == "E1 Ortu"
        assert call_args["report_type"] == "dynamic"
    
    @patch('src.position.etappenlogik.date')
    @patch('src.notification.email_client.EmailClient')
    def test_no_stages_available(self, mock_email_client, mock_date, sample_config):
        """Test behavior when no stages are available."""
        # Setup mocks
        mock_date.today.return_value = date(2025, 6, 30)  # Day 5, no stage available
        
        mock_email_instance = Mock()
        mock_email_instance.send_gr20_report.return_value = True
        mock_email_client.return_value = mock_email_instance
        
        # Import and run the monitor
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        
        with patch('scripts.run_gr20_weather_monitor.load_config') as mock_load_config:
            mock_load_config.return_value = sample_config
            
            with patch('src.position.etappenlogik.load_etappen_data') as mock_load_etappen:
                mock_load_etappen.return_value = []  # No stages available
                
                from scripts.run_gr20_weather_monitor import main
                
                with patch('sys.argv', ['run_gr20_weather_monitor.py', '--modus', 'morning']):
                    main()
        
        # Verify notification email was sent
        mock_email_instance.send_gr20_report.assert_called_once()
        call_args = mock_email_instance.send_gr20_report.call_args[0][0]
        assert call_args["location"] == "Keine Etappe"
        assert call_args["risk_description"] == "Keine Etappen mehr konfiguriert"
        assert call_args["report_type"] == "no_stages"
    
    @patch('src.position.etappenlogik.date')
    @patch('src.wetter.fetch_meteofrance.get_forecast')
    @patch('src.wetter.fetch_openmeteo.fetch_openmeteo_forecast')
    @patch('src.notification.email_client.EmailClient')
    def test_fallback_to_openmeteo(self, mock_email_client, mock_openmeteo, 
                                  mock_meteofrance, mock_date, sample_config, temp_etappen_file):
        """Test fallback to OpenMeteo when MeteoFrance fails."""
        # Setup mocks
        mock_date.today.return_value = date(2025, 6, 25)
        
        # MeteoFrance fails
        mock_meteofrance.side_effect = Exception("MeteoFrance API Error")
        
        # OpenMeteo succeeds
        openmeteo_data = {
            "current": {
                "temperature_2m": 22.5,
                "precipitation": 0.0,
                "wind_speed_10m": 15.0,
                "time": "2025-06-25T19:00:00"
            }
        }
        mock_openmeteo.return_value = openmeteo_data
        
        mock_email_instance = Mock()
        mock_email_instance.send_gr20_report.return_value = True
        mock_email_client.return_value = mock_email_instance
        
        # Import and run the monitor
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        
        with patch('scripts.run_gr20_weather_monitor.load_config') as mock_load_config:
            mock_load_config.return_value = sample_config
            
            with patch('src.position.etappenlogik.load_etappen_data') as mock_load_etappen:
                with open(temp_etappen_file, 'r') as f:
                    mock_load_etappen.return_value = json.load(f)
                
                from scripts.run_gr20_weather_monitor import main
                
                with patch('sys.argv', ['run_gr20_weather_monitor.py', '--modus', 'morning']):
                    main()
        
        # Verify email was sent with OpenMeteo data
        mock_email_instance.send_gr20_report.assert_called_once()
        call_args = mock_email_instance.send_gr20_report.call_args[0][0]
        assert call_args["location"] == "E1 Ortu"
        assert call_args["report_type"] == "morning" 