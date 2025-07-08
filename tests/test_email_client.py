"""
Tests for the email client functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.notification.email_client import EmailClient, generate_gr20_report_text
import os


class TestEmailClient:
    """Test cases for EmailClient class."""
    
    def test_email_client_initialization(self):
        """Test EmailClient initialization with config."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report"
            }
        }
        
        client = EmailClient(config)
        
        assert client.smtp_host == "smtp.gmail.com"
        assert client.smtp_port == 587
        assert client.smtp_user == "test@example.com"
        assert client.recipient_email == "recipient@example.com"
        assert client.subject_template == "GR20 Weather Report"
    
    def test_email_client_with_gmail_app_pw_in_config(self):
        """Test EmailClient initialization with GMAIL_APP_PW in config."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report",
                "password": "test_gmail_app_password"
            }
        }
        
        client = EmailClient(config)
        
        assert client.smtp_password == "test_gmail_app_password"
    
    def test_email_client_fallback_to_environment_variables(self):
        """Test EmailClient falls back to environment variables when password not in config."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report"
            }
        }
        
        with patch.dict('os.environ', {'GMAIL_APP_PW': 'env_gmail_password'}):
            client = EmailClient(config)
            assert client.smtp_password == "env_gmail_password"
    
    def test_email_client_fallback_to_smtp_password_env_var(self):
        """Test EmailClient falls back to SMTP_PASSWORD when GMAIL_APP_PW not available."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report"
            }
        }
        
        # Clear both environment variables and set only SMTP_PASSWORD
        with patch.dict('os.environ', {'SMTP_PASSWORD': 'env_smtp_password'}, clear=True):
            client = EmailClient(config)
            assert client.smtp_password == "env_smtp_password"
    
    def test_email_client_prefers_config_password_over_env(self):
        """Test EmailClient prefers password from config over environment variables."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report",
                "password": "config_password"
            }
        }
        
        # Set environment variables but config should take precedence
        with patch.dict('os.environ', {'GMAIL_APP_PW': 'env_password'}):
            client = EmailClient(config)
            assert client.smtp_password == "config_password"
    
    def test_email_client_missing_config(self):
        """Test EmailClient initialization with missing config."""
        config = {}
        
        with pytest.raises(ValueError, match="SMTP configuration is required"):
            EmailClient(config)
    
    def test_email_client_missing_smtp_section(self):
        """Test EmailClient initialization with missing SMTP section."""
        config = {"other_section": {}}
        
        with pytest.raises(ValueError, match="SMTP configuration is required"):
            EmailClient(config)
    
    @patch('src.notification.email_client.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report",
                "password": "test_password"
            }
        }
        
        # Mock SMTP connection
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        client = EmailClient(config)
        result = client.send_email("Test message")
        
        assert result is True
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("test@example.com", "test_password")
        mock_smtp_instance.sendmail.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()
    
    @patch('src.notification.email_client.smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp):
        """Test email sending with SMTP error."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report"
            }
        }
        
        # Mock SMTP error
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        client = EmailClient(config)
        result = client.send_email("Test message")
        
        assert result is False
    
    def test_send_gr20_report(self):
        """Test sending GR20 weather report."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report"
            },
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF",
                "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
            }
        }
        
        with patch.object(EmailClient, 'send_email', return_value=True) as mock_send:
            client = EmailClient(config)
            
            report_data = {
                "location": "Vizzavona",
                "risk_percentage": 45,
                "risk_description": "Gewitterwahrscheinlichkeit",
                "report_time": datetime.now(),
                "report_type": "scheduled"
            }
            
            result = client.send_gr20_report(report_data)
            
            assert result is True
            mock_send.assert_called_once()
            
            # Check that the sent message contains expected content
            sent_message = mock_send.call_args[0][0]
            assert "GR20 Wetter" in sent_message
            assert "Vizzavona" in sent_message
            assert "45%" in sent_message
            assert "Gewitterwahrscheinlichkeit" in sent_message


class TestGenerateGR20ReportText:
    """Test cases for generate_gr20_report_text function."""
    
    def test_generate_gr20_report_text_scheduled(self):
        """Test generating GR20 report text for scheduled report."""
        config = {
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF",
                "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
            }
        }
        
        report_data = {
            "location": "Vizzavona",
            "risk_percentage": 45,
            "risk_description": "Gewitterwahrscheinlichkeit",
            "report_time": datetime(2025, 6, 19, 4, 30),
            "report_type": "scheduled"
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        assert "GR20 Wetter 19-Jun 04:30" in text
        assert "Vizzavona" in text
        assert "45%" in text
        assert "Gewitterwahrscheinlichkeit" in text
        # No links should be present for security reasons
        assert "https://share.garmin.com/PDFCF" not in text
        assert "http" not in text
        assert "www." not in text
        assert len(text) <= 160  # Character limit
    
    def test_generate_gr20_report_text_dynamic(self):
        """Test generating GR20 report text for dynamic report."""
        config = {
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF",
                "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
            }
        }
        
        report_data = {
            "location": "Haut Asco",
            "report_type": "dynamic",
            "weather_data": {
                "max_temperature": 25.0,
                "max_wind_speed": 30.0
            },
            "report_time": datetime(2025, 6, 19, 14, 15)
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        # Should use new dynamic format
        assert "HautAsco" in text
        assert "Update:" in text
        assert "Hitze 25.0" in text
        assert "Wind 30" in text
        assert len(text) <= 160
        assert "https://share.garmin.com/PDFCF" not in text  # No links
    
    def test_generate_gr20_report_text_character_limit(self):
        """Test that generated text respects character limit."""
        config = {
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF",
                "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
            }
        }
        
        # Test with very long location name
        report_data = {
            "location": "VeryLongLocationNameThatExceedsNormalLength",
            "risk_percentage": 99,
            "risk_description": "SehrLangerRisikoBeschreibungstext",
            "report_time": datetime(2025, 6, 19, 4, 30),
            "report_type": "scheduled"
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        assert len(text) <= 160
        assert "GR20 Wetter" in text
        assert "99%" in text
    
    def test_generate_gr20_report_text_missing_config(self):
        """Test generate_gr20_report_text with missing config."""
        report_data = {
            "location": "Vizzavona",
            "risk_percentage": 45,
            "risk_description": "Gewitterwahrscheinlichkeit",
            "report_time": datetime.now(),
            "report_type": "scheduled"
        }
        
        result = generate_gr20_report_text(report_data, {})
        
        assert "GR20 Wetter" in result
        assert "Vizzavona" in result
        assert "Gewitterwahrscheinlichkeit" in result
        assert "45%" in result
    
    def test_generate_gr20_report_text_emoji_free(self):
        """Test that generated GR20 report text is emoji-free."""
        config = {
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF"
            }
        }
        
        report_data = {
            "location": "Vizzavona",
            "risk_percentage": 75,
            "risk_description": "Gewitterwahrscheinlichkeit",
            "report_time": datetime.now(),
            "report_type": "scheduled"
        }
        
        result = generate_gr20_report_text(report_data, config)
        
        # Check that no emojis are present
        emoji_chars = ["⚠️", "⚡", "🌤️", "🚨", "🌧️", "🌩️", "🌪️", "🌊", "❄️", "☀️", "⛈️", "🌨️", "💨", "🌫️", "🌡️", "💧", "🏔️", "🌋"]
        for emoji in emoji_chars:
            assert emoji not in result, f"Emoji '{emoji}' found in report text"
        
        # Verify the text still contains the essential information
        assert "GR20 Wetter" in result
        assert "Vizzavona" in result
        assert "Gewitterwahrscheinlichkeit" in result
        assert "75%" in result
        assert "WARNUNG" in result  # Should use text instead of emoji
    
    def test_generate_morning_report_format(self):
        """Test generating morning report according to email_format rule."""
        config = {
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF",
                "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
            }
        }
        
        report_data = {
            "location": "Vizzavona",
            "report_type": "morning",
            "weather_data": {
                "max_thunderstorm_probability": 45.0,
                "thunderstorm_threshold_time": "14:00",
                "thunderstorm_threshold_pct": 30.0,
                "thunderstorm_next_day": 35.0,
                "max_precipitation_probability": 60.0,
                "rain_threshold_time": "12:00",
                "rain_threshold_pct": 50.0,
                "max_precipitation": 5.2,
                "max_temperature": 28.5,
                "max_wind_speed": 25.0
            },
            "report_time": datetime(2025, 6, 19, 4, 30)
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        # Check format: {EtappeHeute} - Gewitter {g1}%@{t1} {g2}%@{t2} - Gewitter +1 {g1_next}% - Regen {r1}%@{t3} {r2}%@{t4} {regen_mm}mm - Hitze {temp_max} - Wind {wind_max}
        assert "Vizzavona" in text
        assert "Gewitter 45%" in text
        assert "@14:00 30%" in text
        assert "Gewitter +1 35%" in text
        assert "Regen 60%" in text
        assert "@12:00 50%" in text
        assert "5.2mm" in text
        assert "Hitze 28.5" in text
        assert "Wind 25" in text
        assert len(text) <= 160
        assert "http" not in text  # No links
    
    def test_generate_evening_report_format(self):
        """Test generating evening report according to email_format rule."""
        config = {
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF",
                "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
            }
        }
        
        report_data = {
            "location": "Haut Asco",
            "report_type": "evening",
            "weather_data": {
                "tomorrow_stage": "Haut Asco",
                "day_after_stage": "Vizzavona",
                "night_temperature": 12.5,
                "max_thunderstorm_probability": 35.0,
                "thunderstorm_threshold_time": "15:00",
                "thunderstorm_threshold_pct": 25.0,
                "thunderstorm_day_after": 40.0,
                "max_precipitation_probability": 45.0,
                "rain_threshold_time": "13:00",
                "rain_threshold_pct": 40.0,
                "max_precipitation": 3.8,
                "max_temperature": 26.0,
                "max_wind_speed": 30.0
            },
            "report_time": datetime(2025, 6, 19, 19, 0)
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        # Check format: {EtappeMorgen}→{EtappeÜbermorgen} - Nacht {min_temp} - Gewitter {g1}%@{t1} ({g2}%@{t2}) - Gewitter +1 {g1_next}% - Regen {r1}%@{t3} ({r2}%@{t4}) {regen_mm}mm - Hitze {temp_max} - Wind {wind_max}
        assert "HautAsco→Vizzavona" in text
        assert "Nacht 12.5" in text
        assert "Gewitter 35%" in text
        assert "(25%@15:00)" in text
        assert "Gewitter +1 40%" in text
        assert "Regen 45%" in text
        assert "(40%@13:00)" in text
        assert "3.8mm" in text
        assert "Hitze 26.0" in text
        assert "Wind 30" in text
        assert len(text) <= 160
        assert "http" not in text  # No links
    
    def test_generate_dynamic_report_format(self):
        """Test generating dynamic update report according to email_format rule."""
        config = {
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF",
                "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
            }
        }
        
        report_data = {
            "location": "Conca",
            "report_type": "dynamic",
            "weather_data": {
                "thunderstorm_threshold_time": "16:00",
                "thunderstorm_threshold_pct": 40.0,
                "rain_threshold_time": "14:00",
                "rain_threshold_pct": 55.0,
                "max_temperature": 29.0,
                "max_wind_speed": 35.0
            },
            "report_time": datetime(2025, 6, 19, 14, 15)
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        # Check format: {EtappeHeute} - Update: Gewitter {g2}%@{t2} - Regen {r2}%@{t4} - Hitze {temp_max} - Wind {wind_max}
        assert "Conca" in text
        assert "Update:" in text
        assert "Gewitter 40%@16:00" in text
        assert "Regen 55%@14:00" in text
        assert "Hitze 29.0" in text
        assert "Wind 35" in text
        assert len(text) <= 160
        assert "http" not in text  # No links
    
    def test_generate_dynamic_report_without_thresholds(self):
        """Test dynamic report when no threshold times are available."""
        config = {}
        
        report_data = {
            "location": "Calenzana",
            "report_type": "dynamic",
            "weather_data": {
                "max_temperature": 25.0,
                "max_wind_speed": 20.0
            },
            "report_time": datetime(2025, 6, 19, 14, 15)
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        # Should only include temperature and wind, no thunder/rain parts
        assert "Calenzana" in text
        assert "Update:" in text
        assert "Hitze 25.0" in text
        assert "Wind 20" in text
        assert "Gewitter" not in text  # No thunderstorm data
        assert "Regen" not in text  # No rain data
        assert len(text) <= 160
    
    def test_generate_morning_report_character_limit(self):
        """Test that morning report respects 160 character limit."""
        config = {}
        
        # Test with very long location name
        report_data = {
            "location": "VeryLongLocationNameThatExceedsNormalLength",
            "report_type": "morning",
            "weather_data": {
                "max_thunderstorm_probability": 99.0,
                "thunderstorm_threshold_time": "14:00",
                "thunderstorm_threshold_pct": 80.0,
                "max_precipitation_probability": 95.0,
                "rain_threshold_time": "12:00",
                "rain_threshold_pct": 90.0,
                "max_precipitation": 99.9,
                "max_temperature": 99.9,
                "max_wind_speed": 99.0
            },
            "report_time": datetime(2025, 6, 19, 4, 30)
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        assert len(text) <= 160
        assert "VeryLongLocationNameThatExceedsNormalLength" in text or "..." in text
    
    def test_generate_evening_report_character_limit(self):
        """Test that evening report respects 160 character limit."""
        config = {}
        
        # Test with extremely long stage names to force truncation
        report_data = {
            "location": "Haut Asco",
            "report_type": "evening",
            "weather_data": {
                "tomorrow_stage": "ExtremelyLongTomorrowStageNameThatExceedsAllReasonableLimits",
                "day_after_stage": "ExtremelyLongDayAfterStageNameThatExceedsAllReasonableLimits",
                "night_temperature": 12.5,
                "max_thunderstorm_probability": 99.0,
                "thunderstorm_threshold_time": "15:00",
                "thunderstorm_threshold_pct": 80.0,
                "max_precipitation_probability": 95.0,
                "rain_threshold_time": "13:00",
                "rain_threshold_pct": 90.0,
                "max_precipitation": 99.9,
                "max_temperature": 99.9,
                "max_wind_speed": 99.0
            },
            "report_time": datetime(2025, 6, 19, 19, 0)
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        assert len(text) <= 160
        assert "..." in text  # Should be truncated
    
    def test_generate_legacy_report_backward_compatibility(self):
        """Test legacy report format for backward compatibility."""
        config = {
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF",
                "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
            }
        }
        
        report_data = {
            "location": "Vizzavona",
            "risk_percentage": 45,
            "risk_description": "Gewitterwahrscheinlichkeit",
            "report_time": datetime(2025, 6, 19, 4, 30),
            "report_type": "scheduled"  # Old format
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        # Should use legacy format
        assert "GR20 Wetter 19-Jun 04:30" in text
        assert "Vizzavona" in text
        assert "45%" in text
        assert "Gewitterwahrscheinlichkeit" in text
        assert len(text) <= 160
        assert "https://share.garmin.com/PDFCF" not in text  # No links
    
    def test_generate_morning_report_with_missing_data(self):
        """Test morning report with missing weather data."""
        config = {}
        
        report_data = {
            "location": "Test Location",
            "report_type": "morning",
            "weather_data": {},  # Empty data
            "report_time": datetime(2025, 6, 19, 4, 30)
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        # Should handle missing data gracefully
        assert "TestLocation" in text
        assert "Gewitter 0%" in text
        assert "Gewitter +1 0%" in text
        assert "Regen 0%" in text
        assert "Hitze 0.0" in text
        assert "Wind 0" in text
        assert len(text) <= 160
    
    def test_generate_evening_report_with_missing_data(self):
        """Test evening report with missing weather data."""
        config = {}
        
        report_data = {
            "location": "Test Location",
            "report_type": "evening",
            "weather_data": {},  # Empty data
            "report_time": datetime(2025, 6, 19, 19, 0)
        }
        
        text = generate_gr20_report_text(report_data, config)
        
        # Should handle missing data gracefully
        assert "TestLocation" in text
        assert "Nacht 0.0" in text
        assert "Gewitter 0%" in text
        assert "Gewitter +1 0%" in text
        assert "Regen 0%" in text
        assert "Hitze 0.0" in text
        assert "Wind 0" in text
        assert len(text) <= 160 

    def test_generate_morning_report_with_vigilance_warning(self):
        """Test morning report generation with vigilance warning."""
        report_data = {
            "location": "Conca",
            "weather_data": {
                "max_thunderstorm_probability": 45.0,
                "thunderstorm_threshold_time": "14:00",
                "thunderstorm_threshold_pct": 30.0,
                "thunderstorm_next_day": 25.0,
                "max_precipitation_probability": 60.0,
                "rain_threshold_time": "15:30",
                "rain_threshold_pct": 50.0,
                "max_precipitation": 12.5,
                "max_temperature": 28.5,
                "max_wind_speed": 35.0,
                "vigilance_alerts": [
                    {"phenomenon": "thunderstorm", "level": "orange"},
                    {"phenomenon": "rain", "level": "yellow"}
                ]
            }
        }
        config = {"max_characters": 160}
        
        result = generate_gr20_report_text(report_data, config)
        
        # Should include vigilance warning at the end
        assert "ORANGE Gewitter" in result
        assert len(result) <= 160
        assert result.count("|") >= 5  # Multiple sections

    def test_generate_evening_report_with_vigilance_warning(self):
        """Test evening report generation with vigilance warning."""
        report_data = {
            "location": "Conca",
            "report_type": "evening",
            "weather_data": {
                "tomorrow_stage": "Vizzavona",
                "day_after_stage": "Corte",
                "night_temperature": 15.2,
                "max_thunderstorm_probability": 35.0,
                "thunderstorm_threshold_time": "16:00",
                "thunderstorm_threshold_pct": 25.0,
                "thunderstorm_day_after": 40.0,
                "max_precipitation_probability": 45.0,
                "rain_threshold_time": "17:30",
                "rain_threshold_pct": 40.0,
                "max_precipitation": 8.5,
                "max_temperature": 26.0,
                "max_wind_speed": 25.0,
                "vigilance_alerts": [
                    {"phenomenon": "forest_fire", "level": "red"}
                ]
            }
        }
        config = {"max_characters": 160}
        
        result = generate_gr20_report_text(report_data, config)
        
        # Should include vigilance warning at the end
        assert "RED Waldbrand" in result
        assert len(result) <= 160
        assert "Gewitter +1" in result

    def test_generate_dynamic_report_with_vigilance_warning(self):
        """Test dynamic report generation with vigilance warning."""
        report_data = {
            "location": "Conca",
            "report_type": "dynamic",
            "weather_data": {
                "thunderstorm_threshold_time": "13:00",
                "thunderstorm_threshold_pct": 35.0,
                "rain_threshold_time": "14:30",
                "rain_threshold_pct": 55.0,
                "max_temperature": 30.0,
                "max_wind_speed": 40.0,
                "vigilance_alerts": [
                    {"phenomenon": "wind", "level": "yellow"},
                    {"phenomenon": "heat", "level": "orange"}
                ]
            }
        }
        config = {"max_characters": 160}
        
        result = generate_gr20_report_text(report_data, config)
        
        # Should include highest level vigilance warning
        assert "ORANGE Hitze" in result
        assert len(result) <= 160
        assert "Update:" in result

    def test_vigilance_warning_formatting(self):
        """Test vigilance warning formatting with various scenarios."""
        from src.notification.email_client import _format_vigilance_warning
        
        # Test empty alerts
        assert _format_vigilance_warning([]) == ""
        
        # Test green level (should be ignored)
        alerts = [{"phenomenon": "rain", "level": "green"}]
        assert _format_vigilance_warning(alerts) == ""
        
        # Test yellow level
        alerts = [{"phenomenon": "thunderstorm", "level": "yellow"}]
        assert _format_vigilance_warning(alerts) == "YELLOW Gewitter"
        
        # Test orange level
        alerts = [{"phenomenon": "forest_fire", "level": "orange"}]
        assert _format_vigilance_warning(alerts) == "ORANGE Waldbrand"
        
        # Test red level
        alerts = [{"phenomenon": "wind", "level": "red"}]
        assert _format_vigilance_warning(alerts) == "RED Wind"
        
        # Test multiple alerts - should return highest level
        alerts = [
            {"phenomenon": "rain", "level": "yellow"},
            {"phenomenon": "thunderstorm", "level": "orange"},
            {"phenomenon": "heat", "level": "red"}
        ]
        assert _format_vigilance_warning(alerts) == "RED Hitze"
        
        # Test unknown phenomenon
        alerts = [{"phenomenon": "unknown_phenomenon", "level": "orange"}]
        assert _format_vigilance_warning(alerts) == "ORANGE unknown_phenomenon"

    def test_vigilance_warning_german_translations(self):
        """Test German translations for vigilance warning phenomena."""
        from src.notification.email_client import _format_vigilance_warning
        
        test_cases = [
            ("thunderstorm", "Gewitter"),
            ("rain", "Regen"),
            ("wind", "Wind"),
            ("snow", "Schnee"),
            ("flood", "Hochwasser"),
            ("forest_fire", "Waldbrand"),
            ("heat", "Hitze"),
            ("cold", "Kälte"),
            ("avalanche", "Lawine"),
            ("unknown", "Warnung")
        ]
        
        for english, german in test_cases:
            alerts = [{"phenomenon": english, "level": "orange"}]
            result = _format_vigilance_warning(alerts)
            assert german in result, f"Expected '{german}' in result for '{english}'"

    def test_report_without_vigilance_warning(self):
        """Test reports without vigilance warnings."""
        report_data = {
            "location": "Conca",
            "weather_data": {
                "max_thunderstorm_probability": 25.0,
                "thunderstorm_next_day": 20.0,
                "max_precipitation_probability": 30.0,
                "max_precipitation": 5.0,
                "max_temperature": 25.0,
                "max_wind_speed": 20.0,
                "vigilance_alerts": []  # No alerts
            }
        }
        config = {"max_characters": 160}
        
        # Test morning report
        morning_result = generate_gr20_report_text(report_data, config)
        assert "ORANGE" not in morning_result
        assert "YELLOW" not in morning_result
        assert "RED" not in morning_result
        assert "Gewitter +1" in morning_result
        
        # Test evening report
        evening_result = generate_gr20_report_text(report_data, config)
        assert "ORANGE" not in evening_result
        assert "YELLOW" not in evening_result
        assert "RED" not in evening_result
        assert "Gewitter +1" in evening_result

    def test_vigilance_warning_character_limit(self):
        """Test that vigilance warnings respect character limits."""
        report_data = {
            "location": "VeryLongLocationNameThatExceedsNormalLength",
            "weather_data": {
                "max_thunderstorm_probability": 45.0,
                "thunderstorm_next_day": 30.0,
                "max_precipitation_probability": 60.0,
                "max_precipitation": 15.0,
                "max_temperature": 30.0,
                "max_wind_speed": 40.0,
                "vigilance_alerts": [
                    {"phenomenon": "forest_fire", "level": "red"}
                ]
            }
        }
        config = {"max_characters": 160}
        
        result = generate_gr20_report_text(report_data, config)
        
        # Should be truncated to 160 characters
        assert len(result) <= 160
        # Should end with "..." if truncated
        if len(result) == 160:
            assert result.endswith("...")

    def test_vigilance_warning_edge_cases(self):
        """Test vigilance warning edge cases."""
        from src.notification.email_client import _format_vigilance_warning
        
        # Test missing level
        alerts = [{"phenomenon": "thunderstorm"}]
        assert _format_vigilance_warning(alerts) == ""
        
        # Test missing phenomenon
        alerts = [{"level": "orange"}]
        result = _format_vigilance_warning(alerts)
        assert "ORANGE" in result
        
        # Test invalid level
        alerts = [{"phenomenon": "rain", "level": "invalid"}]
        assert _format_vigilance_warning(alerts) == ""
        
        # Test case insensitive phenomenon
        alerts = [{"phenomenon": "THUNDERSTORM", "level": "orange"}]
        assert _format_vigilance_warning(alerts) == "ORANGE Gewitter" 