"""
Integration tests for the complete GR20 weather report system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.logic.report_scheduler import ReportScheduler
from src.notification.email_client import EmailClient, generate_gr20_report_text
from src.logic.analyse_weather import WeatherAnalysis
from src.model.datatypes import WeatherData, WeatherPoint


class TestGR20ReportIntegration:
    """Integration tests for the complete GR20 report system."""
    
    def test_complete_report_flow_scheduled(self):
        """Test complete flow for scheduled report."""
        # Setup configuration
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report"
            },
            "send_schedule": {
                "morning_time": "04:30",
                "evening_time": "19:00"
            },
            "dynamic_send": {
                "threshold": 0.4,
                "delta_pct": 15.0,
                "min_interval_min": 30,
                "max_daily_reports": 3
            },
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF",
                "weather_map": "https://www.meteofrance.com/previsions-meteo-france/corse/2A"
            },
            "gr20_stages": [
                {"name": "Vizzavona", "coordinates": [42.1167, 9.1333]},
                {"name": "Haut Asco", "coordinates": [42.4500, 9.0333]}
            ]
        }
        
        # Create scheduler
        scheduler = ReportScheduler("test_state.json", config)
        
        # Test scheduled report time
        scheduled_time = datetime.now().replace(hour=4, minute=30, second=0, microsecond=0)
        current_risk = 0.3
        
        # Check if report should be sent
        should_send = scheduler.should_send_report(scheduled_time, current_risk)
        assert should_send is True
        
        # Check report type
        report_type = scheduler.get_report_type(scheduled_time, current_risk)
        assert report_type == "scheduled"
        
        # Generate report data
        report_data = {
            "location": "Vizzavona",
            "risk_percentage": int(current_risk * 100),
            "risk_description": "Gewitterwahrscheinlichkeit",
            "report_time": scheduled_time,
            "report_type": report_type
        }
        
        # Generate report text
        report_text = generate_gr20_report_text(report_data, config)
        
        # Verify report text format
        assert "GR20 Wetter" in report_text
        assert "Vizzavona" in report_text
        assert "30%" in report_text
        assert "Gewitterwahrscheinlichkeit" in report_text
        assert len(report_text) <= 160
        
        # Update scheduler state
        scheduler.update_state_after_report(scheduled_time, current_risk, is_dynamic=False)
        
        # Verify state was updated
        assert scheduler.current_state.last_scheduled_report == scheduled_time
        assert scheduler.current_state.last_risk_value == current_risk
    
    def test_complete_report_flow_dynamic(self):
        """Test complete flow for dynamic report."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report"
            },
            "send_schedule": {
                "morning_time": "04:30",
                "evening_time": "19:00"
            },
            "dynamic_send": {
                "threshold": 0.4,
                "delta_pct": 15.0,
                "min_interval_min": 30,
                "max_daily_reports": 3
            },
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF"
            },
            "gr20_stages": [
                {"name": "Haut Asco", "coordinates": [42.4500, 9.0333]}
            ]
        }
        
        # Create scheduler with previous state
        scheduler = ReportScheduler("test_state.json", config)
        scheduler.current_state.last_risk_value = 0.2
        scheduler.current_state.last_dynamic_report = datetime.now() - timedelta(minutes=45)
        scheduler.current_state.daily_dynamic_report_count = 1
        
        # Test dynamic report conditions
        current_time = datetime.now()
        current_risk = 0.6  # Above threshold and significant change
        
        should_send = scheduler.should_send_report(current_time, current_risk)
        assert should_send is True
        
        report_type = scheduler.get_report_type(current_time, current_risk)
        assert report_type == "dynamic"
        
        # Generate report data
        report_data = {
            "location": "Haut Asco",
            "risk_percentage": int(current_risk * 100),
            "risk_description": "Starkregen",
            "report_time": current_time,
            "report_type": report_type
        }
        
        # Generate report text
        report_text = generate_gr20_report_text(report_data, config)
        
        # Verify report text
        assert "GR20 Wetter" in report_text
        assert "Haut Asco" in report_text
        assert "60%" in report_text
        assert "Starkregen" in report_text
        assert len(report_text) <= 160
        
        # Update state
        scheduler.update_state_after_report(current_time, current_risk, is_dynamic=True)
        
        # Verify state was updated
        assert scheduler.current_state.last_dynamic_report == current_time
        assert scheduler.current_state.daily_dynamic_report_count == 2
        assert scheduler.current_state.last_risk_value == current_risk
    
    @patch('src.notification.email_client.smtplib.SMTP')
    def test_email_client_integration(self, mock_smtp):
        """Test email client integration with scheduler."""
        config = {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test@example.com",
                "to": "recipient@example.com",
                "subject": "GR20 Weather Report"
            },
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF"
            }
        }
        
        # Mock SMTP
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        # Create email client
        email_client = EmailClient(config)
        
        # Test report data
        report_data = {
            "location": "Vizzavona",
            "risk_percentage": 45,
            "risk_description": "Gewitterwahrscheinlichkeit",
            "report_time": datetime.now(),
            "report_type": "scheduled"
        }
        
        # Send report
        result = email_client.send_gr20_report(report_data)
        
        assert result is True
        mock_smtp.assert_called_once()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.send_message.assert_called_once()
    
    def test_nearest_stage_location_integration(self):
        """Test integration of nearest stage location finding."""
        from src.logic.report_scheduler import get_nearest_stage_location
        
        config = {
            "gr20_stages": [
                {"name": "Calenzana", "coordinates": [42.5083, 8.8556]},
                {"name": "Haut Asco", "coordinates": [42.4500, 9.0333]},
                {"name": "Vizzavona", "coordinates": [42.1167, 9.1333]},
                {"name": "Conca", "coordinates": [41.7333, 9.3500]}
            ]
        }
        
        # Test position near Vizzavona
        test_lat, test_lon = 42.12, 9.14
        nearest = get_nearest_stage_location(test_lat, test_lon, config)
        
        assert nearest is not None
        assert nearest["name"] == "Vizzavona"
        assert nearest["coordinates"] == [42.1167, 9.1333]
        
        # Test position near Conca
        test_lat, test_lon = 41.75, 9.35
        nearest = get_nearest_stage_location(test_lat, test_lon, config)
        
        assert nearest is not None
        assert nearest["name"] == "Conca"
        assert nearest["coordinates"] == [41.7333, 9.3500]
    
    def test_character_limit_enforcement(self):
        """Test that character limit is properly enforced."""
        config = {
            "link_template": {
                "sharemap": "https://share.garmin.com/PDFCF"
            }
        }
        
        # Test with very long location name
        report_data = {
            "location": "VeryLongLocationNameThatExceedsNormalLengthAndShouldBeTruncated",
            "risk_percentage": 99,
            "risk_description": "SehrLangerRisikoBeschreibungstextDerAuchGekuerztWerdenMuss",
            "report_time": datetime(2025, 6, 19, 4, 30),
            "report_type": "scheduled"
        }
        
        report_text = generate_gr20_report_text(report_data, config)
        
        # Verify character limit
        assert len(report_text) <= 160
        assert "GR20 Wetter" in report_text
        assert "99%" in report_text
        
        # Verify truncation indicators
        if len(report_data["location"]) > 20:
            assert "..." in report_text
    
    def test_daily_report_limit_enforcement(self):
        """Test that daily report limits are properly enforced."""
        config = {
            "send_schedule": {
                "morning_time": "04:30",
                "evening_time": "19:00"
            },
            "dynamic_send": {
                "threshold": 0.4,
                "delta_pct": 15.0,
                "min_interval_min": 30,
                "max_daily_reports": 3
            }
        }
        
        scheduler = ReportScheduler("test_state.json", config)
        
        # Set up state with maximum daily reports
        scheduler.current_state.daily_dynamic_report_count = 3
        scheduler.current_state.last_risk_value = 0.2
        scheduler.current_state.last_dynamic_report = datetime.now() - timedelta(minutes=45)
        
        # Test that no more dynamic reports are allowed
        current_time = datetime.now()
        current_risk = 0.8  # High risk
        
        should_send = scheduler.should_send_report(current_time, current_risk)
        assert should_send is False
        
        # But scheduled reports should still work
        scheduled_time = datetime.now().replace(hour=4, minute=30, second=0, microsecond=0)
        should_send = scheduler.should_send_report(scheduled_time, current_risk)
        assert should_send is True 