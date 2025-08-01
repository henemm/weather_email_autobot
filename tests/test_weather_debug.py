"""
Tests for the weather debug output module.

This module tests the WeatherDebugOutput class and related functions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from typing import Dict, Any

from src.debug.weather_debug import WeatherDebugOutput, generate_weather_debug_output


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "debug": {
            "enabled": True,
            "output_directory": "test_output/debug",
            "save_debug_files": True
        },
        "startdatum": "2025-07-25"
    }


@pytest.fixture
def sample_report_data():
    """Sample report data for testing."""
    return {
        "report_type": "morning",
        "location": "Test Location",
        "stage_names": ["Stage 1", "Stage 2"]
    }


@pytest.fixture
def mock_meteofrance_client():
    """Mock MeteoFrance client."""
    mock_client = Mock()
    
    # Mock forecast data
    mock_forecast = Mock()
    mock_forecast.forecast = [
        {
            'datetime': '2025-07-30T04:00:00Z',
            'T': {'value': 9.7},
            'wind': {'speed': 2.0, 'gust': 0.0},
            'rain': {'1h': 0.0},
            'weather': {'desc': 'Ciel clair', 'icon': 'p01n'}
        },
        {
            'datetime': '2025-07-30T06:00:00Z',
            'T': {'value': 9.6},
            'wind': {'speed': 2.0, 'gust': 0.0},
            'rain': {'1h': 0.0},
            'weather': {'desc': 'Ciel clair', 'icon': 'p01n'}
        },
        {
            'datetime': '2025-07-30T12:00:00Z',
            'T': {'value': 18.1},
            'wind': {'speed': 3.0, 'gust': 12.0},
            'rain': {'1h': 0.0},
            'weather': {'desc': 'Ensoleillé', 'icon': 'p02j'}
        },
        {
            'datetime': '2025-07-30T17:00:00Z',
            'T': {'value': 17.0},
            'wind': {'speed': 4.0, 'gust': 14.0},
            'rain': {'1h': 0.0},
            'weather': {'desc': 'Peu nuageux', 'icon': 'p03j'}
        }
    ]
    
    # Mock daily forecast data
    mock_forecast.daily_forecast = [
        {
            'dt': '2025-07-30',
            'T': {
                'min': {'value': 8.9},
                'max': {'value': 17.6}
            },
            'rain': {'24h': 1.2},
            'wind': {'gust': {'max': 14.0}},
            'uv': {'value': 6}
        }
    ]
    
    # Mock probability forecast data
    mock_forecast.probability_forecast = [
        {
            'dt': '2025-07-30T06:00:00Z',
            'rain': {'3h': '-'},
            'snow': {'3h': '-'},
            'freezing_rain': {'3h': '-'},
            'storm': {'3h': '-'}
        },
        {
            'dt': '2025-07-30T12:00:00Z',
            'rain': {'3h': '-'},
            'snow': {'3h': '-'},
            'freezing_rain': {'3h': '-'},
            'storm': {'3h': '-'}
        },
        {
            'dt': '2025-07-30T15:00:00Z',
            'rain': {'3h': '-'},
            'snow': {'3h': '-'},
            'freezing_rain': {'3h': '-'},
            'storm': {'3h': '-'}
        }
    ]
    
    mock_client.get_forecast.return_value = mock_forecast
    return mock_client


@pytest.fixture
def mock_stage_data():
    """Mock stage data."""
    return {
        "name": "Test Stage",
        "punkte": [
            {"lat": 42.28647, "lon": 8.89356},
            {"lat": 42.25421, "lon": 8.92553},
            {"lat": 42.22935, "lon": 8.97768},
            {"lat": 42.22026, "lon": 8.98073}
        ]
    }


class TestWeatherDebugOutput:
    """Test the WeatherDebugOutput class."""
    
    def test_initialization(self, sample_config):
        """Test WeatherDebugOutput initialization."""
        debug_output = WeatherDebugOutput(sample_config)
        
        assert debug_output.config == sample_config
        assert debug_output.debug_config == sample_config["debug"]
        assert debug_output.startdatum == "2025-07-25"
        assert debug_output.output_directory == "test_output/debug"
    
    def test_should_generate_debug_enabled(self, sample_config):
        """Test debug generation when enabled."""
        debug_output = WeatherDebugOutput(sample_config)
        assert debug_output.should_generate_debug() is True
    
    def test_should_generate_debug_disabled(self):
        """Test debug generation when disabled."""
        config = {"debug": {"enabled": False}}
        debug_output = WeatherDebugOutput(config)
        assert debug_output.should_generate_debug() is False
    
    def test_get_target_date_morning(self, sample_config):
        """Test target date calculation for morning report."""
        with patch('src.debug.weather_debug.date') as mock_date:
            mock_date.today.return_value = date(2025, 7, 30)
            
            debug_output = WeatherDebugOutput(sample_config)
            target_date = debug_output.get_target_date("morning")
            
            # Should be 5 days after start date (2025-07-25)
            expected_date = date(2025, 7, 30)
            assert target_date == expected_date
    
    def test_get_target_date_evening(self, sample_config):
        """Test target date calculation for evening report."""
        with patch('src.debug.weather_debug.date') as mock_date:
            mock_date.today.return_value = date(2025, 7, 30)
            
            debug_output = WeatherDebugOutput(sample_config)
            target_date = debug_output.get_target_date("evening")
            
            # Should be 6 days after start date (2025-07-25)
            expected_date = date(2025, 7, 31)
            assert target_date == expected_date
    
    @patch('src.debug.weather_debug.get_current_stage')
    @patch('src.debug.weather_debug.get_stage_coordinates')
    def test_get_stage_positions_morning(self, mock_get_coordinates, mock_get_stage, sample_config, mock_stage_data):
        """Test getting stage positions for morning report."""
        mock_get_stage.return_value = mock_stage_data
        mock_get_coordinates.return_value = [
            (42.28647, 8.89356),
            (42.25421, 8.92553),
            (42.22935, 8.97768),
            (42.22026, 8.98073)
        ]
        
        debug_output = WeatherDebugOutput(sample_config)
        positions = debug_output.get_stage_positions("morning")
        
        assert len(positions) == 4
        assert positions[0] == ("Test Stage_P1", 42.28647, 8.89356)
        assert positions[1] == ("Test Stage_P2", 42.25421, 8.92553)
        assert positions[2] == ("Test Stage_P3", 42.22935, 8.97768)
        assert positions[3] == ("Test Stage_P4", 42.22026, 8.98073)
    
    @patch('src.debug.weather_debug.get_stage_coordinates')
    def test_get_stage_positions_evening(self, mock_get_coordinates, sample_config, mock_stage_data):
        """Test getting stage positions for evening report."""
        # Mock the import and function call
        with patch('src.debug.weather_debug.get_current_stage') as mock_get_current_stage:
            mock_get_current_stage.return_value = None  # This will trigger the evening path
            
            # Mock the get_next_stage import and call
            with patch('src.position.etappenlogik.get_next_stage') as mock_get_next_stage:
                mock_get_next_stage.return_value = mock_stage_data
                mock_get_coordinates.return_value = [
                    (42.28647, 8.89356),
                    (42.25421, 8.92553)
                ]
                
                debug_output = WeatherDebugOutput(sample_config)
                positions = debug_output.get_stage_positions("evening")
                
                assert len(positions) == 2
                assert positions[0] == ("Test Stage_P1", 42.28647, 8.89356)
                assert positions[1] == ("Test Stage_P2", 42.25421, 8.92553)
    
    @patch('src.debug.weather_debug.MeteoFranceClient')
    def test_fetch_meteofrance_data(self, mock_client_class, sample_config, mock_meteofrance_client):
        """Test fetching MeteoFrance data."""
        mock_client_class.return_value = mock_meteofrance_client
        
        debug_output = WeatherDebugOutput(sample_config)
        weather_data = debug_output.fetch_meteofrance_data(42.28647, 8.89356)
        
        assert 'forecast' in weather_data
        assert 'daily_forecast' in weather_data
        assert 'probability_forecast' in weather_data
        assert 'rain_data' in weather_data
        assert 'alerts' in weather_data
        
        # Check forecast data
        forecast = weather_data['forecast']
        assert len(forecast) == 4
        assert forecast[0]['temperature'] == 9.7
        assert forecast[0]['wind_speed'] == 2.0
        assert forecast[0]['condition'] == 'Ciel clair'
    
    def test_extract_forecast_data(self, sample_config):
        """Test forecast data extraction."""
        debug_output = WeatherDebugOutput(sample_config)
        
        forecast_entries = [
            {
                'datetime': '2025-07-30T04:00:00Z',
                'T': {'value': 9.7},
                'wind': {'speed': 2.0, 'gust': 0.0},
                'rain': {'1h': 0.0},
                'weather': {'desc': 'Ciel clair', 'icon': 'p01n'}
            }
        ]
        
        extracted = debug_output._extract_forecast_data(forecast_entries)
        
        assert len(extracted) == 1
        assert extracted[0]['temperature'] == 9.7
        assert extracted[0]['wind_speed'] == 2.0
        assert extracted[0]['gusts'] == 0.0
        assert extracted[0]['rain'] == 0.0
        assert extracted[0]['condition'] == 'Ciel clair'
        assert extracted[0]['icon'] == 'p01n'
        assert extracted[0]['thunderstorm'] is False
        assert extracted[0]['time'] == '04:00'
    
    def test_extract_daily_forecast_data(self, sample_config):
        """Test daily forecast data extraction."""
        debug_output = WeatherDebugOutput(sample_config)
        
        daily_entries = [
            {
                'dt': '2025-07-30',
                'T': {
                    'min': {'value': 8.9},
                    'max': {'value': 17.6}
                },
                'rain': {'24h': 1.2},
                'wind': {'gust': {'max': 14.0}},
                'uv': {'value': 6}
            }
        ]
        
        extracted = debug_output._extract_daily_forecast_data(daily_entries)
        
        assert len(extracted) == 1
        assert extracted[0]['day'] == '2025-07-30'
        assert extracted[0]['temp_min'] == 8.9
        assert extracted[0]['temp_max'] == 17.6
        assert extracted[0]['rain_sum'] == 1.2
        assert extracted[0]['wind_gust_max'] == 14.0
        assert extracted[0]['uv_index'] == 6
    
    def test_extract_probability_forecast_data(self, sample_config):
        """Test probability forecast data extraction."""
        debug_output = WeatherDebugOutput(sample_config)
        
        prob_entries = [
            {
                'dt': '2025-07-30T06:00:00Z',
                'rain': {'3h': '-'},
                'snow': {'3h': '-'},
                'freezing_rain': {'3h': '-'},
                'storm': {'3h': '-'}
            }
        ]
        
        extracted = debug_output._extract_probability_forecast_data(prob_entries)
        
        assert len(extracted) == 1
        assert extracted[0]['time'] == '06:00'
        assert extracted[0]['rain_3h'] == '-'
        assert extracted[0]['snow_3h'] == '-'
        assert extracted[0]['freezing_rain_3h'] == '-'
        assert extracted[0]['storm_3h'] == '-'
    
    def test_extract_rain_data(self, sample_config):
        """Test rain data extraction."""
        debug_output = WeatherDebugOutput(sample_config)
        
        forecast_entries = [
            {
                'datetime': '2025-07-30T12:00:00Z',
                'rain': {'1h': 0.0}
            },
            {
                'datetime': '2025-07-30T12:01:00Z',
                'rain': {'1h': 0.0}
            },
            {
                'datetime': '2025-07-30T12:02:00Z',
                'rain': {'1h': 0.1}
            }
        ]
        
        extracted = debug_output._extract_rain_data(forecast_entries)
        
        assert len(extracted) == 3
        assert extracted[0]['time'] == '12:00'
        assert extracted[0]['rain_mm'] == 0.0
        assert extracted[0]['rain_intensity'] == '-'
        assert extracted[2]['rain_mm'] == 0.1
        assert extracted[2]['rain_intensity'] == 'leicht'
    
    def test_get_alert_color(self, sample_config):
        """Test alert color mapping."""
        debug_output = WeatherDebugOutput(sample_config)
        
        assert debug_output._get_alert_color(1) == 'grün'
        assert debug_output._get_alert_color(2) == 'gelb'
        assert debug_output._get_alert_color(3) == 'orange'
        assert debug_output._get_alert_color(4) == 'rot'
        assert debug_output._get_alert_color(5) == 'unbekannt'
    
    @patch('src.debug.weather_debug.date')
    @patch('src.debug.weather_debug.get_current_stage')
    @patch('src.debug.weather_debug.get_stage_coordinates')
    @patch('src.debug.weather_debug.MeteoFranceClient')
    def test_generate_debug_output(self, mock_client_class, mock_get_coordinates, mock_get_stage, mock_date, sample_config, mock_stage_data, mock_meteofrance_client):
        """Test complete debug output generation."""
        mock_date.today.return_value = date(2025, 7, 30)
        mock_get_stage.return_value = mock_stage_data
        mock_get_coordinates.return_value = [(42.28647, 8.89356)]
        mock_client_class.return_value = mock_meteofrance_client
        
        debug_output = WeatherDebugOutput(sample_config)
        output = debug_output.generate_debug_output("morning")
        
        assert "DEBUG DATENEXPORT – Rohdatenübersicht MeteoFrance" in output
        assert "Datenquelle: meteo_france / Substruktur: forecast" in output
        assert "Position: 42.28647, 8.89356" in output
        assert "Datum: 2025-07-30" in output
        assert "| Uhrzeit | temperature | wind_speed | gusts | rain | icon | condition     | thunderstorm |" in output
        assert "| 04:00   | 9.7 °C      | 2 km/h     | 0 km/h| 0.0mm| p01n | Ciel clair     | false        |" in output
    
    @patch('src.debug.weather_debug.date')
    @patch('src.debug.weather_debug.get_current_stage')
    @patch('src.debug.weather_debug.get_stage_coordinates')
    def test_generate_debug_output_no_stage(self, mock_get_coordinates, mock_get_stage, mock_date, sample_config):
        """Test debug output generation when no stage is available."""
        mock_date.today.return_value = date(2025, 7, 30)
        mock_get_stage.return_value = None
        
        debug_output = WeatherDebugOutput(sample_config)
        output = debug_output.generate_debug_output("morning")
        
        assert "No stage positions available for debug output" in output
    
    def test_generate_debug_output_disabled(self):
        """Test debug output generation when debug is disabled."""
        config = {"debug": {"enabled": False}}
        debug_output = WeatherDebugOutput(config)
        output = debug_output.generate_debug_output("morning")
        
        assert output == ""


class TestGenerateWeatherDebugOutput:
    """Test the generate_weather_debug_output function."""
    
    @patch('src.debug.weather_debug.WeatherDebugOutput')
    def test_generate_weather_debug_output_success(self, mock_debug_class, sample_config, sample_report_data):
        """Test successful debug output generation."""
        mock_debug_instance = Mock()
        mock_debug_instance.generate_debug_output.return_value = "Test debug output"
        mock_debug_class.return_value = mock_debug_instance
        
        result = generate_weather_debug_output(sample_report_data, sample_config)
        
        assert result == "Test debug output"
        mock_debug_instance.generate_debug_output.assert_called_once_with("morning")
    
    def test_generate_weather_debug_output_error(self, sample_config, sample_report_data):
        """Test debug output generation with error."""
        # Force an error by using invalid config
        invalid_config = {"debug": {"enabled": True}, "startdatum": "invalid-date"}
        
        result = generate_weather_debug_output(sample_report_data, invalid_config)
        
        # The function should return a message about no stage positions available
        assert "No stage positions available for debug output" in result 