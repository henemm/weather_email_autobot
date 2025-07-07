"""
Snapshot tests for all weather report types (direct format check).

These tests capture the current functionality of morning, evening, and dynamic reports
as a baseline for architecture refactoring. Sie prüfen direkt die zentrale Formatierungsfunktion.
"""

import pytest
from src.notification.email_client import generate_gr20_report_text

class TestSnapshotReports:
    def setup_method(self):
        self.mock_config = {
            "subject": "GR20 Wetter",
            "smtp": {
                "host": "localhost",
                "port": 25,
                "user": "test",
                "to": "test@example.com"
            },
            "thresholds": {
                "regen_probability": 25,
                "thunderstorm_probability": 20,
                "regen_amount": 2.0,
                "wind_speed": 20,
                "temperature": 32
            }
        }
        self.mock_weather_data = {
            "max_temperature": 25.5,
            "min_temperature": 12.3,
            "max_rain_probability": 45.0,
            "max_precipitation": 2.1,
            "max_wind_speed": 18.0,
            "max_wind_gusts": 32.0,
            "max_thunderstorm_probability": 65.0,
            "thunderstorm_threshold_pct": 35.0,
            "thunderstorm_threshold_time": "14:00",
            "rain_threshold_pct": 25.0,
            "rain_threshold_time": "15:00",
            "precipitation_threshold_mm": 2.0,
            "precipitation_threshold_time": "16:00",
            "wind_threshold_kmh": 20.0,
            "wind_threshold_time": "13:00",
            "temperature_threshold_c": 30.0,
            "temperature_threshold_time": "15:00",
            "tomorrow_max_thunderstorm_probability": 75.0,
            "tomorrow_thunderstorm_threshold_time": "14:00",
            "night_min_temperature": 15.7,
            "tomorrow_max_temperature": 28.2,
            "tomorrow_max_rain_probability": 55.0,
            "tomorrow_max_precipitation": 3.5,
            "tomorrow_max_wind_speed": 22.0,
            "tomorrow_wind_gusts": 38.0,
            "day_after_tomorrow_max_thunderstorm_probability": 80.0,
            "day_after_tomorrow_thunderstorm_threshold_time": "15:00"
        }
        self.mock_vigilance = {
            "vigilance_level": 3,
            "vigilance_phenomenon": "thunderstorm"
        }

    def test_snapshot_morning_report_text(self):
        data = self.mock_weather_data.copy()
        data.update({"report_type": "morning", "etappe_heute": "SanPetru"})
        data.update(self.mock_vigilance)
        text = generate_gr20_report_text(data, self.mock_config)
        # Snapshot: Der Text muss die wichtigsten Felder enthalten
        assert "SanPetru" in text
        assert "Gew." in text
        assert "Regen" in text
        assert "Wind" in text
        assert "Hitze" in text
        assert len(text) <= 160

    def test_snapshot_evening_report_text(self):
        data = self.mock_weather_data.copy()
        data.update({"report_type": "evening", "etappe_morgen": "Vizzavona", "etappe_uebermorgen": "Corte", "night_min_temperature": 15.7})
        data.update(self.mock_vigilance)
        text = generate_gr20_report_text(data, self.mock_config)
        assert "Vizzavona" in text
        assert "Corte" in text
        assert "Nacht" in text
        assert "Gew." in text
        assert "Regen" in text
        assert "Wind" in text
        assert "Hitze" in text
        assert len(text) <= 160

    def test_snapshot_dynamic_report_text(self):
        data = self.mock_weather_data.copy()
        data.update({"report_type": "update", "etappe_heute": "Almhütte"})
        data.update(self.mock_vigilance)
        text = generate_gr20_report_text(data, self.mock_config)
        assert "Almhütte" in text
        assert "Update" in text
        assert "Gew." in text
        assert "Regen" in text
        assert "Wind" in text
        assert "Hitze" in text
        assert len(text) <= 160

    def test_snapshot_null_value_handling(self):
        data = {"report_type": "morning", "etappe_heute": "SanPetru", "max_temperature": None, "max_rain_probability": None, "max_precipitation": None, "max_wind_speed": None, "max_wind_gusts": None, "max_thunderstorm_probability": None}
        data.update(self.mock_vigilance)
        text = generate_gr20_report_text(data, self.mock_config)
        # Nullwerte werden als "-" oder "-mm" etc. ausgegeben
        assert "-" in text
        assert len(text) <= 160

    def test_snapshot_character_limit_compliance(self):
        data = self.mock_weather_data.copy()
        data.update({"report_type": "evening", "etappe_morgen": "VeryLongStageName", "etappe_uebermorgen": "AnotherVeryLongStageName", "max_temperature": 35.5, "max_rain_probability": 95.0, "max_precipitation": 15.5, "max_wind_speed": 45.0, "max_wind_gusts": 75.0, "max_thunderstorm_probability": 98.0, "thunderstorm_threshold_pct": 85.0, "thunderstorm_threshold_time": "14:00", "rain_threshold_pct": 90.0, "rain_threshold_time": "15:00", "precipitation_threshold_mm": 12.0, "precipitation_threshold_time": "16:00", "wind_threshold_kmh": 40.0, "wind_threshold_time": "13:00", "temperature_threshold_c": 35.0, "temperature_threshold_time": "15:00", "tomorrow_max_thunderstorm_probability": 99.0, "tomorrow_thunderstorm_threshold_time": "14:00", "day_after_tomorrow_max_thunderstorm_probability": 95.0, "day_after_tomorrow_thunderstorm_threshold_time": "15:00", "night_min_temperature": 25.5, "tomorrow_max_temperature": 38.2, "tomorrow_max_rain_probability": 98.0, "tomorrow_max_precipitation": 18.5, "tomorrow_max_wind_speed": 55.0, "tomorrow_wind_gusts": 85.0})
        data.update(self.mock_vigilance)
        text = generate_gr20_report_text(data, self.mock_config)
        assert len(text) <= 160 