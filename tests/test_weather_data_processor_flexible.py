"""
Tests for flexible weather data aggregation logic.

This module tests the new flexible date-based weather data aggregation
that handles different report types (morning, evening, update) correctly.
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch
from src.wetter.weather_data_processor import WeatherDataProcessor


class TestFlexibleWeatherDataAggregation:
    """Test flexible weather data aggregation for different report types."""
    
    @pytest.fixture
    def config(self):
        """Sample configuration for testing."""
        return {
            "thresholds": {
                "thunderstorm_probability": 20.0,
                "rain_probability": 25.0,
                "regen_amount": 2.0,
                "wind_speed": 20.0,
                "temperature": 32.0
            }
        }
    
    @pytest.fixture
    def processor(self, config):
        """WeatherDataProcessor instance for testing."""
        return WeatherDataProcessor(config)
    
    @pytest.fixture
    def mock_forecast_data(self):
        """Mock forecast data for testing."""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)
        
        # Create mock forecast entries for different days and times
        forecast_entries = []
        
        # Today's data (05:00-17:00)
        for hour in range(5, 18):
            dt = datetime.combine(today, datetime.min.time().replace(hour=hour))
            forecast_entries.append({
                'dt': int(dt.timestamp()),
                'weather': {'desc': 'Ensoleillé' if hour < 12 else 'Averses orageuses'},
                'T': {'value': 20.0 + hour},  # Temperature increases with hour
                'wind': {'speed': 10.0 + hour, 'gust': 15.0 + hour},
                'precipitation_probability': 30 if hour >= 12 else 10,
                'rain': {'1h': 0.5 if hour >= 12 else 0.0}
            })
        
        # Tomorrow's data (05:00-17:00)
        for hour in range(5, 18):
            dt = datetime.combine(tomorrow, datetime.min.time().replace(hour=hour))
            forecast_entries.append({
                'dt': int(dt.timestamp()),
                'weather': {'desc': 'Pluie' if hour < 10 else 'Orage'},
                'T': {'value': 18.0 + hour},
                'wind': {'speed': 15.0 + hour, 'gust': 25.0 + hour},
                'precipitation_probability': 60 if hour < 10 else 80,
                'rain': {'1h': 1.5 if hour < 10 else 2.0}
            })
        
        # Day after tomorrow's data (05:00-17:00)
        for hour in range(5, 18):
            dt = datetime.combine(day_after_tomorrow, datetime.min.time().replace(hour=hour))
            forecast_entries.append({
                'dt': int(dt.timestamp()),
                'weather': {'desc': 'Ensoleillé'},
                'T': {'value': 25.0 + hour},
                'wind': {'speed': 8.0 + hour, 'gust': 12.0 + hour},
                'precipitation_probability': 5,
                'rain': {'1h': 0.0}
            })
        
        # Night data (22:00-05:00) for min_temperature
        for hour in [22, 23, 0, 1, 2, 3, 4, 5]:
            if hour >= 22:
                dt = datetime.combine(today, datetime.min.time().replace(hour=hour))
            else:
                dt = datetime.combine(tomorrow, datetime.min.time().replace(hour=hour))
            forecast_entries.append({
                'dt': int(dt.timestamp()),
                'weather': {'desc': 'Ciel dégagé'},
                'T': {'value': 15.0 - (hour % 6)},  # Temperature decreases at night but stays positive
                'wind': {'speed': 5.0, 'gust': 8.0},
                'precipitation_probability': 0,
                'rain': {'1h': 0.0}
            })
        
        return forecast_entries
    
    def test_calculate_weather_data_for_day_today(self, processor, mock_forecast_data):
        """Test weather data calculation for today (05:00-17:00)."""
        today = datetime.now().date()
        
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor._calculate_weather_data_for_day(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                target_date=today,
                start_hour=5,
                end_hour=17
            )
        
        # Verify the result contains expected data
        assert result['max_temperature'] > 0
        assert result['max_wind_speed'] > 0
        assert result['target_date'] == today.isoformat()
        assert result['time_window'] == "05:00-17:00"
        assert result['data_source'] == 'meteofrance-api'
    
    def test_calculate_weather_data_for_day_tomorrow(self, processor, mock_forecast_data):
        """Test weather data calculation for tomorrow (05:00-17:00)."""
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor._calculate_weather_data_for_day(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                target_date=tomorrow,
                start_hour=5,
                end_hour=17
            )
        
        # Verify the result contains expected data
        assert result['max_temperature'] > 0
        assert result['max_wind_speed'] > 0
        assert result['target_date'] == tomorrow.isoformat()
        assert result['time_window'] == "05:00-17:00"
    
    def test_calculate_thunderstorm_next_day_morning_report(self, processor, mock_forecast_data):
        """Test thunderstorm next day calculation for morning report (should be tomorrow)."""
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor._calculate_thunderstorm_next_day(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                report_type='morning'
            )
        
        # Morning report: Gewitter +1 = morgen
        expected_date = datetime.now().date() + timedelta(days=1)
        assert result['target_date'] == expected_date.isoformat()
        assert result['report_type'] == 'morning'
        assert 'thunderstorm_next_day' in result
    
    def test_calculate_thunderstorm_next_day_evening_report(self, processor, mock_forecast_data):
        """Test thunderstorm next day calculation for evening report (should be day after tomorrow)."""
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor._calculate_thunderstorm_next_day(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                report_type='evening'
            )
        
        # Evening report: Gewitter +1 = übermorgen
        expected_date = datetime.now().date() + timedelta(days=2)
        assert result['target_date'] == expected_date.isoformat()
        assert result['report_type'] == 'evening'
        assert 'thunderstorm_next_day' in result
    
    def test_calculate_thunderstorm_next_day_update_report(self, processor, mock_forecast_data):
        """Test thunderstorm next day calculation for update report (should be tomorrow)."""
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor._calculate_thunderstorm_next_day(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                report_type='update'
            )
        
        # Update report: Gewitter +1 = morgen
        expected_date = datetime.now().date() + timedelta(days=1)
        assert result['target_date'] == expected_date.isoformat()
        assert result['report_type'] == 'update'
        assert 'thunderstorm_next_day' in result
    
    def test_calculate_min_temperature(self, processor, mock_forecast_data):
        """Test minimum temperature calculation for night period (22:00-05:00)."""
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor._calculate_min_temperature(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location"
            )
        
        # Should return minimum temperature from night entries
        assert result > 0
        assert result <= 15.0  # Based on our mock data
    
    def test_process_weather_data_morning_report(self, processor, mock_forecast_data):
        """Test complete weather data processing for morning report."""
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor.process_weather_data(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                report_type='morning'
            )
        
        # Verify morning report structure
        assert result['report_type'] == 'morning'
        assert result['max_temperature'] > 0
        assert result['min_temperature'] == 0.0  # Not calculated for morning reports
        assert result['thunderstorm_next_day'] >= 0
        assert 'target_date' in result
        assert 'thunderstorm_next_day_date' in result
    
    def test_process_weather_data_evening_report(self, processor, mock_forecast_data):
        """Test complete weather data processing for evening report."""
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor.process_weather_data(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                report_type='evening'
            )
        
        # Verify evening report structure
        assert result['report_type'] == 'evening'
        assert result['max_temperature'] > 0
        assert result['min_temperature'] > 0  # Should be calculated for evening reports
        assert result['thunderstorm_next_day'] >= 0
        assert 'target_date' in result
        assert 'thunderstorm_next_day_date' in result
    
    def test_process_weather_data_update_report(self, processor, mock_forecast_data):
        """Test complete weather data processing for update report."""
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor.process_weather_data(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                report_type='update'
            )
        
        # Verify update report structure
        assert result['report_type'] == 'update'
        assert result['max_temperature'] > 0
        assert result['min_temperature'] == 0.0  # Not calculated for update reports
        assert result['thunderstorm_next_day'] >= 0
        assert 'target_date' in result
        assert 'thunderstorm_next_day_date' in result
    
    def test_empty_forecast_data(self, processor):
        """Test handling of empty forecast data."""
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = []
            mock_client.return_value = mock_instance
            
            result = processor.process_weather_data(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                report_type='morning'
            )
        
        # Should return empty result structure
        assert result['max_temperature'] == 0.0
        assert result['max_thunderstorm_probability'] == 0.0
        assert result['location'] == 'Unknown'
        assert result['data_source'] == 'meteofrance-api'
    
    def test_invalid_report_type(self, processor, mock_forecast_data):
        """Test handling of invalid report type."""
        with patch('src.wetter.weather_data_processor.MeteoFranceClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_forecast.return_value.forecast = mock_forecast_data
            mock_client.return_value = mock_instance
            
            result = processor.process_weather_data(
                latitude=42.0,
                longitude=9.0,
                location_name="Test Location",
                report_type='invalid'
            )
        
        # Should fallback to today's data
        assert result['report_type'] == 'invalid'
        assert result['max_temperature'] > 0  # Should still process data
        assert 'target_date' in result 