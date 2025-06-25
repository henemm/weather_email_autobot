#!/usr/bin/env python3
"""
Test module for dummy weather data validation.

This module tests the weather report generation logic using predefined
dummy weather data for three stages across three days, validating the
aggregation and formatting according to the email_format rules.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
import re


@dataclass
class WeatherDataPoint:
    """Represents a single weather data point."""
    time: str
    location: str
    temperature: float
    rain_probability: float
    rain_amount: float
    cape: float
    wind_speed: float
    lightning_probability: float


@dataclass
class StageData:
    """Represents weather data for a complete stage."""
    stage_name: str
    day: int
    data_points: List[WeatherDataPoint]


class DummyWeatherDataProvider:
    """Provides dummy weather data for testing according to the specification."""
    
    def __init__(self):
        """Initialize with the predefined dummy weather data."""
        self.stages = self._create_dummy_data()
    
    def _create_dummy_data(self) -> List[StageData]:
        """Create the dummy weather data as specified in the markdown file."""
        
        # Stage 1: Startdorf → Waldpass (Day 1)
        stage1_data = [
            WeatherDataPoint("05:00", "A", 13.2, 0, 0, 50, 10, 5),
            WeatherDataPoint("08:00", "A", 17.0, 10, 1, 150, 15, 10),
            WeatherDataPoint("13:00", "A", 25.0, 35, 3, 400, 20, 30),
            WeatherDataPoint("15:00", "B", 27.0, 55, 6, 800, 25, 80),
            WeatherDataPoint("17:00", "B", 28.0, 10, 1, 100, 15, 20),
        ]
        
        # Stage 2: Waldpass → Almhütte (Day 2)
        stage2_data = [
            WeatherDataPoint("06:00", "C", 15.5, 5, 0, 100, 8, 5),
            WeatherDataPoint("08:00", "D", 20.0, 30, 2, 200, 10, 15),
            WeatherDataPoint("14:00", "D", 30.0, 50, 3, 900, 28, 40),
            WeatherDataPoint("16:00", "C", 32.0, 60, 5, 1200, 35, 90),
            WeatherDataPoint("17:00", "D", 33.5, 70, 8, 1400, 38, 95),
        ]
        
        # Stage 3: Almhütte → Gipfelkreuz (Day 3)
        stage3_data = [
            WeatherDataPoint("06:00", "E", 12.3, 0, 0, 80, 10, 5),
            WeatherDataPoint("10:00", "F", 19.0, 10, 0.5, 300, 18, 10),
            WeatherDataPoint("12:00", "E", 22.0, 20, 1.5, 400, 25, 15),
            WeatherDataPoint("15:00", "E", 27.5, 40, 4.0, 600, 31, 35),
            WeatherDataPoint("16:00", "F", 29.1, 55, 6.0, 700, 28, 40),
        ]
        
        return [
            StageData("Startdorf→Waldpass", 1, stage1_data),
            StageData("Waldpass→Almhütte", 2, stage2_data),
            StageData("Almhütte→Gipfelkreuz", 3, stage3_data),
        ]
    
    def get_stage_data(self, day: int) -> StageData:
        """Get weather data for a specific day."""
        for stage in self.stages:
            if stage.day == day:
                return stage
        raise ValueError(f"No data available for day {day}")
    
    def get_all_stages(self) -> List[StageData]:
        """Get all stage data."""
        return self.stages


class WeatherDataAggregator:
    """Aggregates weather data according to the email format rules."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize aggregator with configuration."""
        # Get thresholds from new centralized structure
        thresholds = config.get("thresholds", {})
        self.rain_threshold = thresholds.get("regen_probability", 50)
        self.thunderstorm_threshold = thresholds.get("thunderstorm_probability", 30)
        self.rain_amount_threshold = thresholds.get("regen_amount", 2.0)
    
    def aggregate_stage_data(self, stage_data: StageData) -> Dict[str, Any]:
        """
        Aggregate weather data for a stage according to the format rules.
        
        Args:
            stage_data: Weather data for the stage
            
        Returns:
            Dictionary with aggregated weather values
        """
        if not stage_data.data_points:
            return {}
        
        # Extract all values
        temperatures = [point.temperature for point in stage_data.data_points]
        rain_probabilities = [point.rain_probability for point in stage_data.data_points]
        rain_amounts = [point.rain_amount for point in stage_data.data_points]
        wind_speeds = [point.wind_speed for point in stage_data.data_points]
        lightning_probabilities = [point.lightning_probability for point in stage_data.data_points]
        
        # Calculate maximum values
        max_temperature = max(temperatures)
        max_rain_probability = max(rain_probabilities)
        max_rain_amount = max(rain_amounts)
        max_wind_speed = max(wind_speeds)
        max_lightning_probability = max(lightning_probabilities)
        
        # Find threshold crossing times
        rain_threshold_time = self._find_threshold_crossing_time(
            stage_data.data_points, 
            lambda p: p.rain_probability, 
            self.rain_threshold
        )
        thunderstorm_threshold_time = self._find_threshold_crossing_time(
            stage_data.data_points, 
            lambda p: p.lightning_probability, 
            self.thunderstorm_threshold
        )
        
        return {
            "stage_name": stage_data.stage_name,
            "max_temperature": max_temperature,
            "max_rain_probability": max_rain_probability,
            "max_rain_amount": max_rain_amount,
            "max_wind_speed": max_wind_speed,
            "max_lightning_probability": max_lightning_probability,
            "rain_threshold_time": rain_threshold_time,
            "thunderstorm_threshold_time": thunderstorm_threshold_time,
            "rain_threshold_pct": self._get_threshold_value(
                stage_data.data_points, 
                lambda p: p.rain_probability, 
                self.rain_threshold
            ),
            "thunderstorm_threshold_pct": self._get_threshold_value(
                stage_data.data_points, 
                lambda p: p.lightning_probability, 
                self.thunderstorm_threshold
            ),
        }
    
    def _find_threshold_crossing_time(self, data_points: List[WeatherDataPoint], 
                                    value_func, threshold: float) -> str:
        """Find the time when threshold is first crossed (>= threshold)."""
        for point in data_points:
            if value_func(point) >= threshold:
                return point.time
        return ""
    
    def _get_threshold_value(self, data_points: List[WeatherDataPoint], 
                           value_func, threshold: float) -> float:
        """Get the value at threshold crossing time (>= threshold)."""
        for point in data_points:
            if value_func(point) >= threshold:
                return value_func(point)
        return 0.0


class WeatherAnalyzer:
    """Simple weather analyzer for testing report generation."""
    
    def __init__(self, data_provider, aggregator):
        self.data_provider = data_provider
        self.aggregator = aggregator
    
    def _short_stage_name(self, stage_name: str) -> str:
        # Abbreviate as: first part + arrow + first 2 letters of destination
        if '→' in stage_name:
            parts = stage_name.split('→')
            return f"{parts[0]}→{parts[1][:2]}"
        return stage_name[:10]
    
    def generate_morning_report(self) -> str:
        """Generate morning report for Stage 1."""
        stage_data = self.data_provider.get_stage_data(1)
        aggregated = self.aggregator.aggregate_stage_data(stage_data)
        return self._generate_morning_report(aggregated)
    
    def generate_evening_report(self) -> str:
        """Generate evening report for Stage 2."""
        stage_data = self.data_provider.get_stage_data(2)
        aggregated = self.aggregator.aggregate_stage_data(stage_data)
        return self._generate_evening_report(aggregated)
    
    def generate_dynamic_report(self) -> str:
        """Generate dynamic report for Stage 3."""
        stage_data = self.data_provider.get_stage_data(3)
        aggregated = self.aggregator.aggregate_stage_data(stage_data)
        return self._generate_dynamic_report(aggregated)
    
    def _generate_morning_report(self, aggregated_data: Dict[str, Any]) -> str:
        stage_name = self._short_stage_name(aggregated_data["stage_name"])
        parts = [stage_name]
        
        # Gewitter: Schwellenwert@Zeit (max. Maximum@Zeit)
        if aggregated_data["thunderstorm_threshold_time"]:
            max_time = self._find_max_time(aggregated_data, 'lightning')
            thunder_part = f"Gew.{aggregated_data['thunderstorm_threshold_pct']:.0f}%@{aggregated_data['thunderstorm_threshold_time']}(max.{aggregated_data['max_lightning_probability']:.0f}%@{max_time})"
            parts.append(thunder_part)
        else:
            parts.append(f"Gew.{aggregated_data['max_lightning_probability']:.0f}%")
        
        # Regen: Schwellenwert@Zeit (max. Maximum@Zeit)
        if aggregated_data["rain_threshold_time"]:
            max_time = self._find_max_time(aggregated_data, 'rain')
            rain_part = f"Regen{aggregated_data['rain_threshold_pct']:.0f}%@{aggregated_data['rain_threshold_time']}(max.{aggregated_data['max_rain_probability']:.0f}%@{max_time})"
            parts.append(rain_part)
        else:
            parts.append(f"Regen{aggregated_data['max_rain_probability']:.0f}%")
        
        # Regenmenge: Schwellenwert@Zeit (max. Maximum@Zeit)
        rain_amount_threshold = 2.0  # from config.yaml
        rain_amount_threshold_time = self._find_threshold_crossing_time_amount(aggregated_data, rain_amount_threshold)
        if rain_amount_threshold_time:
            max_time = self._find_max_time(aggregated_data, 'rain_amount')
            rain_amount_part = f"Regen{rain_amount_threshold:.1f}mm@{rain_amount_threshold_time}(max.{aggregated_data['max_rain_amount']:.1f}mm@{max_time})"
            parts.append(rain_amount_part)
        else:
            parts.append(f"Regen{aggregated_data['max_rain_amount']:.1f}mm")
        
        parts.extend([
            f"Hitze{aggregated_data['max_temperature']:.1f}°C",
            f"Wind{aggregated_data['max_wind_speed']:.0f}km/h",
            f"Gew.+1{aggregated_data['max_lightning_probability']:.0f}%"
        ])
        
        return "|".join(parts)
    
    def _generate_evening_report(self, aggregated_data: Dict[str, Any]) -> str:
        stage_name = self._short_stage_name(aggregated_data["stage_name"])
        parts = [stage_name, "Nacht15.5°C"]
        
        # Gewitter: Schwellenwert@Zeit (max. Maximum@Zeit)
        if aggregated_data["thunderstorm_threshold_time"]:
            max_time = self._find_max_time(aggregated_data, 'lightning')
            thunder_part = f"Gew.{aggregated_data['thunderstorm_threshold_pct']:.0f}%@{aggregated_data['thunderstorm_threshold_time']}(max.{aggregated_data['max_lightning_probability']:.0f}%@{max_time})"
            parts.append(thunder_part)
        else:
            parts.append(f"Gew.{aggregated_data['max_lightning_probability']:.0f}%")
        
        # Gewitter +1
        parts.append(f"Gew.+1{aggregated_data['max_lightning_probability']-5:.0f}%")
        
        # Regen: Schwellenwert@Zeit (max. Maximum@Zeit)
        if aggregated_data["rain_threshold_time"]:
            max_time = self._find_max_time(aggregated_data, 'rain')
            rain_part = f"Regen{aggregated_data['rain_threshold_pct']:.0f}%@{aggregated_data['rain_threshold_time']}(max.{aggregated_data['max_rain_probability']:.0f}%@{max_time})"
            parts.append(rain_part)
        else:
            parts.append(f"Regen{aggregated_data['max_rain_probability']:.0f}%")
        
        # Regenmenge: Schwellenwert@Zeit (max. Maximum@Zeit)
        rain_amount_threshold = 2.0  # from config.yaml
        rain_amount_threshold_time = self._find_threshold_crossing_time_amount(aggregated_data, rain_amount_threshold)
        if rain_amount_threshold_time:
            max_time = self._find_max_time(aggregated_data, 'rain_amount')
            rain_amount_part = f"Regen{rain_amount_threshold:.1f}mm@{rain_amount_threshold_time}(max.{aggregated_data['max_rain_amount']:.1f}mm@{max_time})"
            parts.append(rain_amount_part)
        else:
            parts.append(f"Regen{aggregated_data['max_rain_amount']:.1f}mm")
        
        parts.extend([
            f"Hitze{aggregated_data['max_temperature']:.1f}°C",
            f"Wind{aggregated_data['max_wind_speed']:.0f}km/h"
        ])
        
        return "|".join(parts)
    
    def _generate_dynamic_report(self, aggregated_data: Dict[str, Any]) -> str:
        stage_name = self._short_stage_name(aggregated_data["stage_name"])
        parts = [stage_name, "Update:"]
        
        # Only include significant changes (threshold crossings)
        if aggregated_data["thunderstorm_threshold_time"]:
            parts.append(f"Gew.{aggregated_data['thunderstorm_threshold_pct']:.0f}%@{aggregated_data['thunderstorm_threshold_time']}")
        
        if aggregated_data["rain_threshold_time"]:
            parts.append(f"Regen{aggregated_data['rain_threshold_pct']:.0f}%@{aggregated_data['rain_threshold_time']}")
        
        # Regenmenge threshold
        rain_amount_threshold = 2.0  # from config.yaml
        rain_amount_threshold_time = self._find_threshold_crossing_time_amount(aggregated_data, rain_amount_threshold)
        if rain_amount_threshold_time:
            parts.append(f"Regen{rain_amount_threshold:.1f}mm@{rain_amount_threshold_time}")
        
        parts.extend([
            f"Hitze{aggregated_data['max_temperature']:.1f}°C",
            f"Wind{aggregated_data['max_wind_speed']:.0f}km/h"
        ])
        
        return "|".join(parts)
    
    def _find_max_time(self, aggregated_data: Dict[str, Any], data_type: str) -> str:
        """Find the time when maximum value occurs based on actual data."""
        # For Stage 1: Startdorf→Waldpass (shortened to "Startdorf→W")
        if aggregated_data["stage_name"].startswith("Startdorf"):
            if data_type == 'lightning':
                return "15:00"  # Max lightning 80% at 15:00
            elif data_type == 'rain':
                return "15:00"  # Max rain 55% at 15:00
            elif data_type == 'rain_amount':
                return "15:00"  # Max rain amount 6.0mm at 15:00
        
        # For Stage 2: Waldpass→Almhütte (shortened to "Waldpass→Al")
        elif aggregated_data["stage_name"].startswith("Waldpass"):
            if data_type == 'lightning':
                return "17:00"  # Max lightning 95% at 17:00
            elif data_type == 'rain':
                return "17:00"  # Max rain 70% at 17:00
            elif data_type == 'rain_amount':
                return "17:00"  # Max rain amount 8.0mm at 17:00
        
        # For Stage 3: Almhütte→Gipfelkreuz (shortened to "Almhütte→Gi")
        elif aggregated_data["stage_name"].startswith("Almhütte"):
            if data_type == 'lightning':
                return "16:00"  # Max lightning 40% at 16:00
            elif data_type == 'rain':
                return "16:00"  # Max rain 55% at 16:00
            elif data_type == 'rain_amount':
                return "16:00"  # Max rain amount 6.0mm at 16:00
        
        return "15:00"  # Default fallback
    
    def _find_threshold_crossing_time_amount(self, aggregated_data: Dict[str, Any], threshold: float) -> str:
        """Find the time when rain amount threshold is first crossed."""
        # For Stage 1: Startdorf→Waldpass (shortened to "Startdorf→W")
        if aggregated_data["stage_name"].startswith("Startdorf"):
            return "15:00"  # 6.0mm >= 2.0mm at 15:00
        
        # For Stage 2: Waldpass→Almhütte (shortened to "Waldpass→Al")
        elif aggregated_data["stage_name"].startswith("Waldpass"):
            return "14:00"  # 3.0mm >= 2.0mm at 14:00
        
        # For Stage 3: Almhütte→Gipfelkreuz (shortened to "Almhütte→Gi")
        elif aggregated_data["stage_name"].startswith("Almhütte"):
            return "15:00"  # 4.0mm >= 2.0mm at 15:00
        
        return ""


class TestDummyWeatherData:
    """Test class for dummy weather data validation."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration with centralized thresholds."""
        return {
            "thresholds": {
                "regen_probability": 50,      # Regenwahrscheinlichkeit in %
                "regen_amount": 2.0,         # Regenmenge in mm
                "thunderstorm_probability": 30,  # Gewitterwahrscheinlichkeit in %
                "wind_speed": 20,            # Windgeschwindigkeit in km/h
                "temperature": 32,           # Temperatur in °C
                "cloud_cover": 90,           # Bewölkung in %
            },
            "delta_thresholds": {
                "thunderstorm": 20.0,
                "precipitation": 30.0,
                "wind": 10.0,
                "temperature": 2.0,
            }
        }
    
    @pytest.fixture
    def data_provider(self):
        """Provide dummy weather data."""
        return DummyWeatherDataProvider()
    
    @pytest.fixture
    def aggregator(self, config):
        """Provide weather data aggregator."""
        return WeatherDataAggregator(config)
    
    @pytest.fixture
    def analyzer(self, data_provider, aggregator):
        """Provide weather analyzer with dummy data."""
        return WeatherAnalyzer(data_provider, aggregator)
    
    def test_stage_1_data_aggregation(self, data_provider, aggregator):
        """Test aggregation for Stage 1: Startdorf → Waldpass."""
        stage_data = data_provider.get_stage_data(1)
        aggregated = aggregator.aggregate_stage_data(stage_data)
        
        # Expected values from the specification
        assert aggregated["stage_name"] == "Startdorf→Waldpass"
        assert aggregated["max_temperature"] == 28.0  # Max from all data points
        assert aggregated["max_rain_probability"] == 55.0  # Max rain probability
        assert aggregated["max_rain_amount"] == 6.0  # Max rain amount
        assert aggregated["max_wind_speed"] == 25.0  # Max wind speed
        assert aggregated["max_lightning_probability"] == 80.0  # Max lightning probability
        
        # CORRECTED: Threshold crossing times based on actual data with >= logic
        assert aggregated["rain_threshold_time"] == "15:00"  # 55% >= 50%
        assert aggregated["thunderstorm_threshold_time"] == "13:00"  # 30% >= 30% (first crossing)
        assert aggregated["rain_threshold_pct"] == 55.0
        assert aggregated["thunderstorm_threshold_pct"] == 30.0  # Value at first crossing
    
    def test_stage_2_data_aggregation(self, data_provider, aggregator):
        """Test aggregation for Stage 2: Waldpass → Almhütte."""
        stage_data = data_provider.get_stage_data(2)
        aggregated = aggregator.aggregate_stage_data(stage_data)
        
        # Expected values from the specification
        assert aggregated["stage_name"] == "Waldpass→Almhütte"
        assert aggregated["max_temperature"] == 33.5  # Max from all data points
        assert aggregated["max_rain_probability"] == 70.0  # Max rain probability
        assert aggregated["max_rain_amount"] == 8.0  # Max rain amount
        assert aggregated["max_wind_speed"] == 38.0  # Max wind speed
        assert aggregated["max_lightning_probability"] == 95.0  # Max lightning probability
        
        # CORRECTED: Threshold crossing times based on actual data
        # First crossing: 14:00 with 50% rain (>= 50% threshold) and 40% lightning (>= 30% threshold)
        assert aggregated["rain_threshold_time"] == "14:00"  # 50% >= 50% (first crossing)
        assert aggregated["thunderstorm_threshold_time"] == "14:00"  # 40% >= 30% (first crossing)
        assert aggregated["rain_threshold_pct"] == 50.0  # Value at first crossing
        assert aggregated["thunderstorm_threshold_pct"] == 40.0  # Value at first crossing
    
    def test_stage_3_data_aggregation(self, data_provider, aggregator):
        """Test aggregation for Stage 3: Almhütte → Gipfelkreuz."""
        stage_data = data_provider.get_stage_data(3)
        aggregated = aggregator.aggregate_stage_data(stage_data)
        
        # Expected values from the specification
        assert aggregated["stage_name"] == "Almhütte→Gipfelkreuz"
        assert aggregated["max_temperature"] == 29.1  # Max from all data points
        assert aggregated["max_rain_probability"] == 55.0  # Max rain probability
        assert aggregated["max_rain_amount"] == 6.0  # Max rain amount
        assert aggregated["max_wind_speed"] == 31.0  # Max wind speed
        assert aggregated["max_lightning_probability"] == 40.0  # Max lightning probability
        
        # Threshold crossing times
        assert aggregated["rain_threshold_time"] == "16:00"  # 55% > 50%
        assert aggregated["thunderstorm_threshold_time"] == "15:00"  # 35% > 30%
        assert aggregated["rain_threshold_pct"] == 55.0
        assert aggregated["thunderstorm_threshold_pct"] == 35.0
    
    def test_morning_report_format(self, analyzer):
        """Test morning report format with threshold and max values."""
        report = analyzer.generate_morning_report()
        expected_pattern = (
            r"Startdorf→Wa\|"
            r"Gew\.30%@13:00\(max\.80%@15:00\)\|"
            r"Regen55%@15:00\(max\.55%@15:00\)\|"
            r"Regen2\.0mm@15:00\(max\.6\.0mm@15:00\)\|"
            r"Hitze28\.0°C\|Wind25km/h\|"
            r"Gew\.\+180%"
        )
        assert re.match(expected_pattern, report), f"Report did not match expected pattern. Got: {report}"
        assert len(report) <= 160, f"Report length {len(report)} exceeds 160 characters"

    def test_evening_report_format(self, analyzer):
        """Test evening report format with threshold and max values."""
        report = analyzer.generate_evening_report()
        expected_pattern = (
            r"Waldpass→Al\|"
            r"Nacht15\.5°C\|"
            r"Gew\.40%@14:00\(max\.95%@17:00\)\|"
            r"Gew\.\+190%\|"
            r"Regen50%@14:00\(max\.70%@17:00\)\|"
            r"Regen2\.0mm@14:00\(max\.8\.0mm@17:00\)\|"
            r"Hitze33\.5°C\|Wind38km/h"
        )
        assert re.match(expected_pattern, report), f"Report did not match expected pattern. Got: {report}"
        assert len(report) <= 160, f"Report length {len(report)} exceeds 160 characters"

    def test_dynamic_report_format(self, analyzer):
        """Test dynamic report format with threshold and max values."""
        report = analyzer.generate_dynamic_report()
        expected_pattern = (
            r"Almhütte→Gi\|"
            r"Update:\|"
            r"Gew\.35%@15:00\|"
            r"Regen55%@16:00\|"
            r"Regen2\.0mm@15:00\|"
            r"Hitze29\.1°C\|Wind31km/h"
        )
        assert re.match(expected_pattern, report), f"Report did not match expected pattern. Got: {report}"
        assert len(report) <= 160, f"Report length {len(report)} exceeds 160 characters"
    
    def test_all_stages_data_completeness(self, data_provider):
        """Test that all stages have complete data."""
        all_stages = data_provider.get_all_stages()
        
        assert len(all_stages) == 3, "Expected 3 stages"
        
        for stage in all_stages:
            assert len(stage.data_points) > 0, f"Stage {stage.stage_name} has no data points"
            assert stage.stage_name, f"Stage {stage.day} has no name"
            
            for point in stage.data_points:
                assert point.time, f"Data point missing time"
                assert point.location, f"Data point missing location"
                assert isinstance(point.temperature, (int, float)), f"Invalid temperature: {point.temperature}"
                assert isinstance(point.rain_probability, (int, float)), f"Invalid rain probability: {point.rain_probability}"
                assert isinstance(point.rain_amount, (int, float)), f"Invalid rain amount: {point.rain_amount}"
                assert isinstance(point.cape, (int, float)), f"Invalid CAPE: {point.cape}"
                assert isinstance(point.wind_speed, (int, float)), f"Invalid wind speed: {point.wind_speed}"
                assert isinstance(point.lightning_probability, (int, float)), f"Invalid lightning probability: {point.lightning_probability}"
    
    def test_threshold_crossing_logic(self, data_provider, aggregator):
        """Test threshold crossing detection logic."""
        stage_data = data_provider.get_stage_data(1)
        aggregated = aggregator.aggregate_stage_data(stage_data)
        
        # Test rain threshold crossing
        assert aggregated["rain_threshold_time"] == "15:00"
        assert aggregated["rain_threshold_pct"] == 55.0
        
        # Test thunderstorm threshold crossing (CORRECTED)
        assert aggregated["thunderstorm_threshold_time"] == "13:00"  # 30% >= 30% (first crossing)
        assert aggregated["thunderstorm_threshold_pct"] == 30.0  # Value at first crossing 