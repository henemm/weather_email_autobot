import pytest
from datetime import datetime, timedelta
from typing import Dict, List

# Import the functions to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from logic.analyse_weather import (
    RiskType, 
    RiskLevel, 
    WeatherRisk, 
    WeatherAnalysis,
    get_default_thresholds,
    merge_weather_data_sources,
    analyze_weather_data,
    analyze_weather_data_english,
    analyze_multiple_sources,
    _select_worst_case_point,
    _analyze_weather_point,
    _determine_risk_level,
    _generate_summary,
    compute_risk
)
from model.datatypes import WeatherData, WeatherPoint, WeatherAlert


class TestWeatherAnalysis:
    """Test cases for weather analysis functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.base_time = datetime(2025, 6, 15, 12, 0)
        self.base_config = {
            "schwellen": {
                "regen": 2.0,
                "wind": 40.0,
                "bewoelkung": 90.0,
                "hitze": 30.0,
                "gewitter_wahrscheinlichkeit": 20.0
            }
        }
        
        # Create sample weather points
        self.normal_point = WeatherPoint(
            latitude=42.5,
            longitude=9.0,
            elevation=100.0,
            time=self.base_time,
            temperature=20.0,
            feels_like=18.0,
            precipitation=1.0,
            thunderstorm_probability=10.0,
            wind_speed=15.0,
            wind_direction=180.0,
            cloud_cover=60.0
        )
        
        self.rainy_point = WeatherPoint(
            latitude=42.5,
            longitude=9.0,
            elevation=100.0,
            time=self.base_time,
            temperature=18.0,
            feels_like=16.0,
            precipitation=5.0,  # Above threshold
            thunderstorm_probability=25.0,  # Above threshold
            wind_speed=20.0,
            wind_direction=180.0,
            cloud_cover=85.0
        )
        
        self.stormy_point = WeatherPoint(
            latitude=42.5,
            longitude=9.0,
            elevation=100.0,
            time=self.base_time,
            temperature=15.0,
            feels_like=12.0,
            precipitation=15.0,  # High precipitation
            thunderstorm_probability=80.0,  # High thunderstorm probability
            wind_speed=60.0,  # High wind speed
            wind_direction=180.0,
            cloud_cover=95.0  # High cloud cover
        )
        
        self.hot_point = WeatherPoint(
            latitude=42.5,
            longitude=9.0,
            elevation=100.0,
            time=self.base_time,
            temperature=35.0,  # Above heat threshold
            feels_like=38.0,
            precipitation=0.0,
            thunderstorm_probability=None,
            wind_speed=10.0,
            wind_direction=180.0,
            cloud_cover=20.0
        )
    
    def test_risk_type_enum_values(self):
        """Test that RiskType enum has correct values"""
        assert RiskType.REGEN.value == "regen"
        assert RiskType.GEWITTER.value == "gewitter"
        assert RiskType.WIND.value == "wind"
        assert RiskType.BEWOELKUNG.value == "bewoelkung"
        assert RiskType.HITZE.value == "hitze"
        assert RiskType.CAPE_SHEAR.value == "cape_shear"
    
    def test_risk_level_enum_values(self):
        """Test that RiskLevel enum has correct values"""
        assert RiskLevel.NIEDRIG.value == "niedrig"
        assert RiskLevel.MITTEL.value == "mittel"
        assert RiskLevel.HOCH.value == "hoch"
        assert RiskLevel.SEHR_HOCH.value == "sehr_hoch"
    
    def test_get_default_thresholds(self):
        """Test default threshold values"""
        thresholds = get_default_thresholds()
        
        assert thresholds["rain_amount"] == 2.0
        assert thresholds["wind_speed"] == 20.0
        assert thresholds["cloud_cover"] == 90.0
        assert thresholds["temperature"] == 32.0
        assert thresholds["thunderstorm_probability"] == 20.0
        assert thresholds["rain_probability"] == 25.0
    
    def test_weather_risk_creation(self):
        """Test WeatherRisk dataclass creation"""
        risk = WeatherRisk(
            risk_type=RiskType.REGEN,
            level=RiskLevel.MITTEL,
            value=5.0,
            threshold=2.0,
            time=self.base_time,
            description="Test risk"
        )
        
        assert risk.risk_type == RiskType.REGEN
        assert risk.level == RiskLevel.MITTEL
        assert risk.value == 5.0
        assert risk.threshold == 2.0
        assert risk.time == self.base_time
        assert risk.description == "Test risk"
    
    def test_weather_analysis_creation(self):
        """Test WeatherAnalysis dataclass creation"""
        analysis = WeatherAnalysis(
            risks=[],
            max_precipitation=10.0,
            max_wind_speed=50.0,
            summary="Test summary"
        )
        
        assert analysis.risks == []
        assert analysis.max_precipitation == 10.0
        assert analysis.max_wind_speed == 50.0
        assert analysis.summary == "Test summary"
    
    def test_analyze_weather_data_empty(self):
        """Test weather analysis with empty data"""
        empty_data = WeatherData(points=[])
        result = analyze_weather_data(empty_data, self.base_config)
        
        assert result.summary == "Keine Wetterdaten verfügbar"
        assert len(result.risks) == 0
        assert result.max_precipitation == 0.0
        assert result.max_wind_speed == 0.0
    
    def test_analyze_weather_data_normal_conditions(self):
        """Test weather analysis with normal conditions"""
        normal_data = WeatherData(points=[self.normal_point])
        result = analyze_weather_data(normal_data, self.base_config)
        
        assert result.summary == "Keine kritischen Wetterbedingungen erkannt."
        assert len(result.risks) == 0
        assert result.max_precipitation == 1.0
        assert result.max_wind_speed == 15.0
        assert result.max_temperature == 20.0
        assert result.max_cloud_cover == 60.0
        assert result.max_thunderstorm_probability == 10.0
    
    def test_analyze_weather_data_rain_risk(self):
        """Test weather analysis with rain risk"""
        rainy_data = WeatherData(points=[self.rainy_point])
        result = analyze_weather_data(rainy_data, self.base_config)
        
        assert len(result.risks) == 2  # Rain and thunderstorm risks
        assert result.max_precipitation == 5.0
        
        # Check rain risk
        rain_risks = [r for r in result.risks if r.risk_type == RiskType.REGEN]
        assert len(rain_risks) == 1
        assert rain_risks[0].value == 5.0
        assert rain_risks[0].level == RiskLevel.HOCH  # 5.0mm > 5.0mm threshold for HOCH
        
        # Check thunderstorm risk
        thunder_risks = [r for r in result.risks if r.risk_type == RiskType.GEWITTER]
        assert len(thunder_risks) == 1
        assert thunder_risks[0].value == 25.0
        assert thunder_risks[0].level == RiskLevel.MITTEL
    
    def test_analyze_weather_data_multiple_risks(self):
        """Test weather analysis with multiple risk types"""
        stormy_data = WeatherData(points=[self.stormy_point])
        result = analyze_weather_data(stormy_data, self.base_config)
        
        assert len(result.risks) >= 3  # Rain, thunderstorm, wind, cloud cover
        assert result.max_precipitation == 15.0
        assert result.max_wind_speed == 60.0
        assert result.max_thunderstorm_probability == 80.0
        assert result.max_cloud_cover == 95.0
        
        # Check risk levels
        rain_risks = [r for r in result.risks if r.risk_type == RiskType.REGEN]
        assert len(rain_risks) == 1
        assert rain_risks[0].level == RiskLevel.SEHR_HOCH  # 15mm > 10mm threshold
        
        wind_risks = [r for r in result.risks if r.risk_type == RiskType.WIND]
        assert len(wind_risks) == 1
        assert wind_risks[0].level == RiskLevel.HOCH  # 60km/h > 40km/h but < 80km/h
    
    def test_analyze_weather_data_heat_risk(self):
        """Test weather analysis with heat risk"""
        hot_data = WeatherData(points=[self.hot_point])
        result = analyze_weather_data(hot_data, self.base_config)
        
        assert len(result.risks) == 1  # Heat risk only
        assert result.max_temperature == 35.0
        
        heat_risks = [r for r in result.risks if r.risk_type == RiskType.HITZE]
        assert len(heat_risks) == 1
        assert heat_risks[0].value == 35.0
        assert heat_risks[0].level == RiskLevel.HOCH  # 35°C > 30°C but < 40°C
    
    def test_analyze_weather_data_custom_thresholds(self):
        """Test weather analysis with custom thresholds"""
        custom_config = {
            "schwellen": {
                "regen": 1.0,  # Lower threshold
                "wind": 10.0,  # Lower threshold
                "hitze": 25.0  # Lower threshold
            }
        }
        
        normal_data = WeatherData(points=[self.normal_point])
        result = analyze_weather_data(normal_data, custom_config)
        
        # Should now detect risks with lower thresholds
        assert len(result.risks) >= 1  # At least rain risk (1.0mm > 1.0mm threshold)
    
    def test_determine_risk_level(self):
        """Test risk level determination"""
        # Test different levels
        assert _determine_risk_level(1.5, 1.0, [2, 5, 10]) == RiskLevel.NIEDRIG
        assert _determine_risk_level(3.0, 1.0, [2, 5, 10]) == RiskLevel.MITTEL
        assert _determine_risk_level(7.0, 1.0, [2, 5, 10]) == RiskLevel.HOCH
        assert _determine_risk_level(12.0, 1.0, [2, 5, 10]) == RiskLevel.SEHR_HOCH
    
    def test_analyze_weather_point(self):
        """Test individual weather point analysis"""
        thresholds = get_default_thresholds()
        
        # Test normal point (no risks)
        normal_risks = _analyze_weather_point(self.normal_point, thresholds)
        assert len(normal_risks) == 0
        
        # Test rainy point (rain and thunderstorm risks)
        rainy_risks = _analyze_weather_point(self.rainy_point, thresholds)
        assert len(rainy_risks) == 2
        
        risk_types = [r.risk_type for r in rainy_risks]
        assert RiskType.REGEN in risk_types
        assert RiskType.GEWITTER in risk_types
    
    def test_generate_summary(self):
        """Test summary generation"""
        # Create test risks
        risks = [
            WeatherRisk(RiskType.REGEN, RiskLevel.MITTEL, 5.0, 2.0, self.base_time, "Rain"),
            WeatherRisk(RiskType.WIND, RiskLevel.HOCH, 60.0, 40.0, self.base_time, "Wind"),
            WeatherRisk(RiskType.GEWITTER, RiskLevel.SEHR_HOCH, 80.0, 20.0, self.base_time, "Thunder")
        ]
        
        max_values = {
            "precipitation": 5.0,
            "wind_speed": 60.0,
            "temperature": 20.0,
            "thunderstorm_probability": 80.0,
            "cloud_cover": 60.0,
            "cape_shear": 0.0
        }
        
        summary = _generate_summary(risks, max_values, {})
        
        assert "Gewitter: SEHR_HOCH (80.0)" in summary
        assert "Regen: MITTEL (5.0)" in summary
        assert "Wind: HOCH (60.0)" in summary
        assert "Max. Niederschlag: 5.0mm" in summary
        assert "Max. Wind: 60 km/h" in summary
    
    def test_generate_summary_no_risks(self):
        """Test summary generation with no risks"""
        summary = _generate_summary([], {}, {})
        assert summary == "Keine kritischen Wetterbedingungen erkannt."
    
    def test_select_worst_case_point(self):
        """Test worst case point selection"""
        # Create two points with different risk levels
        point1 = WeatherPoint(
            latitude=42.5, longitude=9.0, elevation=100.0,
            time=self.base_time, temperature=20.0, feels_like=18.0,
            precipitation=1.0, thunderstorm_probability=10.0,
            wind_speed=15.0, wind_direction=180.0, cloud_cover=60.0
        )
        
        point2 = WeatherPoint(
            latitude=42.5, longitude=9.0, elevation=100.0,
            time=self.base_time, temperature=25.0, feels_like=23.0,
            precipitation=5.0, thunderstorm_probability=30.0,
            wind_speed=25.0, wind_direction=180.0, cloud_cover=80.0
        )
        
        # Point2 should be selected as worst case
        worst_case = _select_worst_case_point(point1, point2)
        assert worst_case == point2
        
        # Point1 should be selected when compared to itself
        same_case = _select_worst_case_point(point1, point1)
        assert same_case == point1
    
    def test_merge_weather_data_sources_empty(self):
        """Test merging empty weather data sources"""
        result = merge_weather_data_sources([])
        assert result.points == []
    
    def test_merge_weather_data_sources_single(self):
        """Test merging single weather data source"""
        data = WeatherData(points=[self.normal_point])
        result = merge_weather_data_sources([data])
        assert result == data
    
    def test_merge_weather_data_sources_multiple(self):
        """Test merging multiple weather data sources"""
        # Create points with different times
        point1 = WeatherPoint(
            latitude=42.5, longitude=9.0, elevation=100.0,
            time=self.base_time,
            temperature=20.0, feels_like=18.0,
            precipitation=1.0, thunderstorm_probability=10.0,
            wind_speed=15.0, wind_direction=180.0, cloud_cover=60.0
        )
        
        point2 = WeatherPoint(
            latitude=42.5, longitude=9.0, elevation=100.0,
            time=self.base_time + timedelta(hours=3),  # Different time
            temperature=18.0, feels_like=16.0,
            precipitation=5.0, thunderstorm_probability=25.0,
            wind_speed=20.0, wind_direction=180.0, cloud_cover=85.0
        )
        
        data1 = WeatherData(points=[point1])
        data2 = WeatherData(points=[point2])
        
        result = merge_weather_data_sources([data1, data2])
        
        # Should have 2 points (different times)
        assert len(result.points) == 2
        
        # Check that worst case values are used for same time
        same_time_data1 = WeatherData(points=[self.normal_point])
        same_time_data2 = WeatherData(points=[self.rainy_point])
        
        # Modify time to be the same
        same_time_data2.points[0].time = self.base_time
        
        merged = merge_weather_data_sources([same_time_data1, same_time_data2])
        assert len(merged.points) == 1
        
        # Should have the higher risk values from rainy_point
        merged_point = merged.points[0]
        assert merged_point.precipitation == 5.0  # Higher value
        assert merged_point.thunderstorm_probability == 25.0  # Higher value
    
    def test_analyze_multiple_sources(self):
        """Test analysis of multiple weather data sources"""
        data1 = WeatherData(points=[self.normal_point])
        data2 = WeatherData(points=[self.rainy_point])
        
        result = analyze_multiple_sources([data1, data2], self.base_config)
        
        # Should detect risks from the worst case data
        assert len(result.risks) >= 2  # Rain and thunderstorm risks from rainy_point
        assert result.max_precipitation == 5.0  # From rainy_point
        assert result.max_thunderstorm_probability == 25.0  # From rainy_point
    
    def test_integration_full_workflow(self):
        """Test complete integration workflow"""
        # Create weather data with multiple risks
        weather_data = WeatherData(points=[self.stormy_point, self.hot_point])
        
        # Analyze weather data
        result = analyze_weather_data(weather_data, self.base_config)
        
        # Verify results
        assert len(result.risks) >= 4  # Rain, thunderstorm, wind, heat, cloud cover
        assert result.max_precipitation == 15.0
        assert result.max_wind_speed == 60.0
        assert result.max_temperature == 35.0
        assert result.max_thunderstorm_probability == 80.0
        assert result.max_cloud_cover == 95.0
        
        # Check that summary contains risk information
        assert "Gewitter" in result.summary
        assert "Regen" in result.summary
        assert "Wind" in result.summary
        assert "Hitze" in result.summary
        
        # Check risk levels
        risk_types = [r.risk_type for r in result.risks]
        assert RiskType.REGEN in risk_types
        assert RiskType.GEWITTER in risk_types
        assert RiskType.WIND in risk_types
        assert RiskType.HITZE in risk_types
        assert RiskType.BEWOELKUNG in risk_types

    def test_analyse_weather_data_with_no_risks_returns_empty_analysis(self):
        """Test that normal weather conditions return empty risk list"""
        # Arrange
        weather_point = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=20.0,
            feels_like=18.0,
            precipitation=0.0,
            thunderstorm_probability=None,
            wind_speed=10.0,
            wind_direction=180.0,
            cloud_cover=30.0
        )
        weather_data = WeatherData(points=[weather_point])
        config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 2,
                "gewitter": 20,
                "delta_prozent": 20,
                "hitze": 32,
                "wind": 20
            }
        }

        # Act
        result = analyze_weather_data_english(weather_data, config)

        # Assert
        assert isinstance(result, WeatherAnalysis)
        assert len(result.risks) == 0
        assert result.max_precipitation == 0.0
        assert result.max_wind_speed == 10.0
        assert result.max_temperature == 20.0
        assert result.max_cloud_cover == 30.0
        assert "No significant weather risks detected" in result.summary

    def test_analyse_weather_data_with_heavy_rain_detects_risk(self):
        """Test that heavy precipitation triggers rain risk detection"""
        # Arrange
        weather_point = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=15.0,
            feels_like=12.0,
            precipitation=5.0,  # Above threshold of 2mm
            thunderstorm_probability=None,
            wind_speed=8.0,
            wind_direction=180.0,
            cloud_cover=80.0
        )
        weather_data = WeatherData(points=[weather_point])
        config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 2,
                "gewitter": 20,
                "delta_prozent": 20,
                "hitze": 32,
                "wind": 20
            }
        }

        # Act
        result = analyze_weather_data_english(weather_data, config)

        # Assert
        assert len(result.risks) == 1
        risk = result.risks[0]
        assert risk.risk_type == RiskType.HEAVY_RAIN
        assert risk.level == RiskLevel.HIGH  # 5.0mm >= 5.0mm threshold for HIGH
        assert risk.value == 5.0
        assert result.max_precipitation == 5.0
        assert "Heavy rain" in result.summary

    def test_analyse_weather_data_with_high_wind_detects_risk(self):
        """Test that high wind speed triggers wind risk detection"""
        # Arrange
        weather_point = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=18.0,
            feels_like=15.0,
            precipitation=0.0,
            thunderstorm_probability=None,
            wind_speed=45.0,  # Above threshold of 20 km/h
            wind_direction=180.0,
            cloud_cover=60.0
        )
        weather_data = WeatherData(points=[weather_point])
        config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 2,
                "gewitter": 20,
                "delta_prozent": 20,
                "hitze": 32,
                "wind": 20
            }
        }

        # Act
        result = analyze_weather_data_english(weather_data, config)

        # Assert
        assert len(result.risks) == 1
        risk = result.risks[0]
        assert risk.risk_type == RiskType.HIGH_WIND
        assert risk.level == RiskLevel.MODERATE  # 45.0 km/h >= 40.0 km/h but < 60.0 km/h for MODERATE
        assert risk.value == 45.0
        assert result.max_wind_speed == 45.0
        assert "High wind" in result.summary

    def test_analyse_weather_data_with_heat_wave_detects_risk(self):
        """Test that high temperature triggers heat risk detection"""
        # Arrange
        weather_point = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=35.0,  # Above threshold of 32°C
            feels_like=38.0,
            precipitation=0.0,
            thunderstorm_probability=None,
            wind_speed=5.0,
            wind_direction=180.0,
            cloud_cover=20.0
        )
        weather_data = WeatherData(points=[weather_point])
        config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 2,
                "gewitter": 20,
                "delta_prozent": 20,
                "hitze": 32,
                "wind": 20
            }
        }

        # Act
        result = analyze_weather_data_english(weather_data, config)

        # Assert
        assert len(result.risks) == 1
        risk = result.risks[0]
        assert risk.risk_type == RiskType.HEAT_WAVE
        assert risk.level == RiskLevel.HIGH  # 35.0°C >= 35.0°C absolute threshold for HIGH
        assert risk.value == 35.0
        assert result.max_temperature == 35.0
        assert "Heat wave" in result.summary

    def test_analyse_weather_data_with_thunderstorm_detects_risk(self):
        """Test that high thunderstorm probability triggers storm risk detection"""
        # Arrange
        weather_point = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=22.0,
            feels_like=20.0,
            precipitation=1.0,
            thunderstorm_probability=30.0,  # Above threshold of 20%
            wind_speed=12.0,
            wind_direction=180.0,
            cloud_cover=85.0
        )
        weather_data = WeatherData(points=[weather_point])
        config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 2,
                "gewitter": 20,
                "delta_prozent": 20,
                "hitze": 32,
                "wind": 20
            }
        }

        # Act
        result = analyze_weather_data_english(weather_data, config)

        # Assert
        assert len(result.risks) == 1
        risk = result.risks[0]
        assert risk.risk_type == RiskType.THUNDERSTORM
        assert risk.level == RiskLevel.MODERATE  # 30.0% >= 20.0% but < 40.0% for MODERATE
        assert risk.value == 30.0
        assert result.max_thunderstorm_probability == 30.0
        assert "Thunderstorm" in result.summary

    def test_analyse_weather_data_with_high_cloud_cover_detects_risk(self):
        """Test that high cloud cover triggers overcast risk detection"""
        # Arrange
        weather_point = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=16.0,
            feels_like=14.0,
            precipitation=0.5,
            thunderstorm_probability=None,
            wind_speed=8.0,
            wind_direction=180.0,
            cloud_cover=95.0  # Above threshold of 90%
        )
        weather_data = WeatherData(points=[weather_point])
        config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 2,
                "gewitter": 20,
                "delta_prozent": 20,
                "hitze": 32,
                "wind": 20
            }
        }

        # Act
        result = analyze_weather_data_english(weather_data, config)

        # Assert
        assert len(result.risks) == 1
        risk = result.risks[0]
        assert risk.risk_type == RiskType.OVERCAST
        assert risk.level == RiskLevel.HIGH  # 95.0% >= 95.0% absolute threshold for HIGH
        assert risk.value == 95.0
        assert result.max_cloud_cover == 95.0
        assert "Overcast" in result.summary

    def test_analyse_weather_data_with_multiple_risks_detects_all(self):
        """Test that multiple weather risks are all detected"""
        # Arrange
        weather_point = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=35.0,  # Heat wave
            feels_like=38.0,
            precipitation=8.0,  # Heavy rain
            thunderstorm_probability=40.0,  # Thunderstorm
            wind_speed=50.0,  # High wind
            wind_direction=180.0,
            cloud_cover=95.0  # Overcast
        )
        weather_data = WeatherData(points=[weather_point])
        config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 2,
                "gewitter": 20,
                "delta_prozent": 20,
                "hitze": 32,
                "wind": 20
            }
        }

        # Act
        result = analyze_weather_data_english(weather_data, config)

        # Assert
        assert len(result.risks) == 5
        risk_types = [risk.risk_type for risk in result.risks]
        assert RiskType.HEAT_WAVE in risk_types
        assert RiskType.HEAVY_RAIN in risk_types
        assert RiskType.THUNDERSTORM in risk_types
        assert RiskType.HIGH_WIND in risk_types
        assert RiskType.OVERCAST in risk_types

    def test_analyse_weather_data_with_multiple_sources_uses_worst_case(self):
        """Test that multiple weather data sources use worst-case values"""
        # Arrange
        point1 = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=25.0,
            feels_like=23.0,
            precipitation=3.0,
            thunderstorm_probability=15.0,
            wind_speed=25.0,
            wind_direction=180.0,
            cloud_cover=70.0
        )
        point2 = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=38.0,  # Higher temperature
            feels_like=40.0,
            precipitation=10.0,  # Higher precipitation
            thunderstorm_probability=50.0,  # Higher storm probability
            wind_speed=60.0,  # Higher wind speed
            wind_direction=180.0,
            cloud_cover=98.0  # Higher cloud cover
        )
        weather_data_list = [
            WeatherData(points=[point1]),
            WeatherData(points=[point2])
        ]
        config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 2,
                "gewitter": 20,
                "delta_prozent": 20,
                "hitze": 32,
                "wind": 20
            }
        }

        # Act
        result = analyze_weather_data_english(weather_data_list, config)

        # Assert
        assert result.max_temperature == 38.0
        assert result.max_precipitation == 10.0
        assert result.max_thunderstorm_probability == 50.0
        assert result.max_wind_speed == 60.0
        assert result.max_cloud_cover == 98.0

    def test_analyse_weather_data_with_custom_thresholds_uses_config(self):
        """Test that custom threshold values from config are used"""
        # Arrange
        weather_point = WeatherPoint(
            latitude=42.0,
            longitude=9.0,
            elevation=100.0,
            time=datetime.now(),
            temperature=25.0,
            feels_like=23.0,
            precipitation=1.5,  # Below default threshold but above custom
            thunderstorm_probability=15.0,
            wind_speed=15.0,
            wind_direction=180.0,
            cloud_cover=70.0
        )
        weather_data = WeatherData(points=[weather_point])
        config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 1.0,  # Custom lower threshold
                "gewitter": 20,
                "delta_prozent": 20,
                "hitze": 32,
                "wind": 20
            }
        }

        # Act
        result = analyze_weather_data_english(weather_data, config)

        # Assert
        assert len(result.risks) == 1
        risk = result.risks[0]
        assert risk.risk_type == RiskType.HEAVY_RAIN
        assert risk.value == 1.5

    def test_analyse_weather_data_with_time_window_captures_duration(self):
        """Test that weather analysis captures risk duration across time windows"""
        # Create multiple points over time
        points = []
        for i in range(3):
            point = WeatherPoint(
                latitude=42.5,
                longitude=9.0,
                elevation=100.0,
                time=self.base_time + timedelta(hours=i),
                temperature=20.0,
                feels_like=18.0,
                precipitation=5.0,  # Above threshold
                thunderstorm_probability=25.0,  # Above threshold
                wind_speed=20.0,
                wind_direction=180.0,
                cloud_cover=85.0
            )
            points.append(point)
        
        weather_data = WeatherData(points=points)
        result = analyze_weather_data(weather_data, self.base_config)
        
        assert len(result.risks) > 0
        # Check that risks have start and end times
        for risk in result.risks:
            assert risk.start_time is not None
            assert risk.end_time is not None

    def test_analyse_weather_data_integrates_risk_model(self):
        """Test that weather analysis integrates risk model computation"""
        # Create weather data with values that will trigger risk model
        point = WeatherPoint(
            latitude=42.5,
            longitude=9.0,
            elevation=100.0,
            time=self.base_time,
            temperature=25.0,
            feels_like=23.0,
            precipitation=3.0,
            thunderstorm_probability=30.0,
            wind_speed=45.0,
            wind_direction=180.0,
            cloud_cover=85.0,
            cape=1500.0,  # High CAPE value
            shear=20.0    # Wind shear value
        )
        
        weather_data = WeatherData(points=[point])
        
        # Configuration with risk model settings
        config_with_risk_model = {
            "schwellen": {
                "regen": 2.0,
                "wind": 40.0,
                "bewoelkung": 90.0,
                "hitze": 30.0,
                "gewitter_wahrscheinlichkeit": 20.0
            },
            "risk_model": {
                "thunderstorm_probability": {
                    "threshold": 25.0,
                    "weight": 0.3
                },
                "wind_speed": {
                    "threshold": 40.0,
                    "weight": 0.2
                },
                "precipitation": {
                    "threshold": 2.0,
                    "weight": 0.2
                },
                "temperature": {
                    "threshold": 25.0,
                    "weight": 0.1
                },
                "cape": {
                    "threshold": 1000.0,
                    "weight": 0.2
                }
            }
        }
        
        result = analyze_weather_data(weather_data, config_with_risk_model)
        
        # Verify that risk score is computed and included in result
        assert hasattr(result, 'risk')
        assert isinstance(result.risk, float)
        assert 0.0 <= result.risk <= 1.0
        
        # Verify that risk score is greater than 0 due to multiple threshold exceedances
        assert result.risk > 0.0
        
        # Verify that individual risks are still detected
        assert len(result.risks) > 0

    def test_analyse_weather_data_without_risk_model_returns_zero_risk(self):
        """Test that weather analysis returns zero risk when no risk model config is provided"""
        point = WeatherPoint(
            latitude=42.5,
            longitude=9.0,
            elevation=100.0,
            time=self.base_time,
            temperature=25.0,
            feels_like=23.0,
            precipitation=3.0,
            thunderstorm_probability=30.0,
            wind_speed=45.0,
            wind_direction=180.0,
            cloud_cover=85.0
        )
        
        weather_data = WeatherData(points=[point])
        
        # Configuration without risk model
        config_without_risk_model = {
            "schwellen": {
                "regen": 2.0,
                "wind": 40.0,
                "bewoelkung": 90.0,
                "hitze": 30.0,
                "gewitter_wahrscheinlichkeit": 20.0
            }
        }
        
        result = analyze_weather_data(weather_data, config_without_risk_model)
        
        # Verify that risk score is 0.0 when no risk model is configured
        assert hasattr(result, 'risk')
        assert result.risk == 0.0

    def test_analyse_weather_data_risk_model_with_lifted_index(self):
        """Test risk model integration with lifted_index parameter (negative threshold logic)"""
        point = WeatherPoint(
            latitude=42.5,
            longitude=9.0,
            elevation=100.0,
            time=self.base_time,
            temperature=25.0,
            feels_like=23.0,
            precipitation=1.0,
            thunderstorm_probability=15.0,
            wind_speed=20.0,
            wind_direction=180.0,
            cloud_cover=60.0
        )
        
        weather_data = WeatherData(points=[point])
        
        # Configuration with lifted_index (more negative = higher instability)
        config_with_lifted_index = {
            "risk_model": {
                "lifted_index": {
                    "threshold": -2.0,  # More negative threshold
                    "weight": 0.5
                }
            }
        }
        
        # Mock the metrics to include lifted_index
        # Since we don't have lifted_index in WeatherPoint, we'll test the compute_risk function directly
        metrics = {
            "lifted_index": -5.0,  # More negative than threshold
            "temperature": 25.0
        }
        
        risk_score = compute_risk(metrics, config_with_lifted_index)
        
        # Should be 0.5 since lifted_index threshold is exceeded
        assert risk_score == 0.5 