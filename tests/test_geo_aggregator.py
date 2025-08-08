"""
Tests for GEO aggregator module.

This module tests the aggregation of weather data from multiple geographical points.
"""

import pytest
from datetime import datetime, date
from typing import Dict, Any

from src.risiko.geo_aggregator import GeoAggregator, AggregatedWeatherData, GeoPoint


class TestGeoAggregator:
    """Test cases for GeoAggregator."""

    def test_aggregate_stage_weather_with_multiple_points(self):
        """Test aggregation of weather data from multiple GEO-points."""
        # Arrange
        base_time = datetime(2025, 7, 28, 14, 0, 0)
        weather_data_by_point = {
            'point1': {
                'forecast': [
                    {
                        'dt': int(base_time.timestamp()),
                        'T': {'value': 25.0},
                        'rain': {'1h': 1.0},
                        'weather': {'desc': 'Ciel clair'},
                        'wind': {'speed': 10, 'gust': 15}
                    }
                ],
                'stage_name': 'Vizzavona',
                'stage_date': '2025-07-28'
            },
            'point2': {
                'forecast': [
                    {
                        'dt': int((base_time.replace(hour=15)).timestamp()),
                        'T': {'value': 28.0},
                        'rain': {'1h': 2.0},
                        'weather': {'desc': 'Orages'},
                        'wind': {'speed': 20, 'gust': 25}
                    }
                ],
                'stage_name': 'Vizzavona',
                'stage_date': '2025-07-28'
            }
        }
        aggregator = GeoAggregator()

        # Act
        result = aggregator.aggregate_stage_weather(weather_data_by_point)

        # Assert
        assert isinstance(result, AggregatedWeatherData)
        assert result.stage_name == 'Vizzavona'
        assert result.stage_date == date(2025, 7, 28)
        assert result.point_count == 2
        assert len(result.forecast_entries) == 2
        assert result.forecast_entries[0]['T']['value'] == 25.0
        assert result.forecast_entries[1]['T']['value'] == 28.0

    def test_aggregate_night_temperature(self):
        """Test aggregation of night temperature from multiple points."""
        # Arrange
        base_time = datetime(2025, 7, 28, 22, 0, 0)  # 22:00
        weather_data_by_point = {
            'point1': {
                'forecast': [
                    {
                        'dt': int(base_time.timestamp()),  # 22:00
                        'T': {'value': 15.0}
                    },
                    {
                        'dt': int((base_time.replace(hour=23)).timestamp()),  # 23:00
                        'T': {'value': 12.0}
                    },
                    {
                        'dt': int((base_time.replace(hour=6)).timestamp()),  # 06:00
                        'T': {'value': 8.0}
                    }
                ]
            },
            'point2': {
                'forecast': [
                    {
                        'dt': int((base_time.replace(hour=0)).timestamp()),  # 00:00
                        'T': {'value': 10.0}
                    },
                    {
                        'dt': int((base_time.replace(hour=3)).timestamp()),  # 03:00
                        'T': {'value': 6.0}
                    }
                ]
            }
        }
        aggregator = GeoAggregator()

        # Act
        result = aggregator.aggregate_night_temperature(weather_data_by_point, night_hours=(22, 6))

        # Assert
        assert result == 6.0  # Minimum night temperature

    def test_aggregate_stage_weather_with_empty_data(self):
        """Test aggregation with empty weather data."""
        # Arrange
        weather_data_by_point = {}
        aggregator = GeoAggregator()

        # Act & Assert
        with pytest.raises(ValueError, match="No valid weather data found"):
            aggregator.aggregate_stage_weather(weather_data_by_point)

    def test_aggregate_stage_weather_with_invalid_data(self):
        """Test aggregation with invalid weather data."""
        # Arrange
        weather_data_by_point = {
            'point1': {'invalid': 'data'},
            'point2': None
        }
        aggregator = GeoAggregator()

        # Act & Assert
        with pytest.raises(ValueError, match="No valid weather data found"):
            aggregator.aggregate_stage_weather(weather_data_by_point)

    def test_get_stage_geopoints(self):
        """Test getting GEO-points for a stage."""
        # Arrange
        aggregator = GeoAggregator()
        stage_name = "Vizzavona"
        stage_date = date(2025, 7, 28)

        # Act
        result = aggregator.get_stage_geopoints(stage_name, stage_date)

        # Assert
        assert len(result) == 3
        assert all(isinstance(point, GeoPoint) for point in result)
        assert result[0].stage_name == stage_name
        assert result[0].stage_date == stage_date
        assert result[0].point_type == "start"
        assert result[1].point_type == "middle"
        assert result[2].point_type == "end" 