"""
Test for centralized context module.
"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from weather.centralized_context import (
    create_report_context, 
    get_debug_summary,
    ReportContext,
    StageData,
    CoordinatePoint
)


class TestCentralizedContext:
    """Test centralized context functionality."""
    
    def test_create_report_context_with_mock_data(self):
        """Test creating report context with mock stage data."""
        # Mock stage data
        mock_today_stage = {
            "name": "TestStage",
            "punkte": [
                {"lat": 42.1, "lon": 9.1},
                {"lat": 42.2, "lon": 9.2}
            ]
        }
        
        mock_tomorrow_stage = {
            "name": "TestStage2", 
            "punkte": [
                {"lat": 42.3, "lon": 9.3},
                {"lat": 42.4, "lon": 9.4},
                {"lat": 42.5, "lon": 9.5}
            ]
        }
        
        mock_day_after_tomorrow_stage = {
            "name": "TestStage3",
            "punkte": [
                {"lat": 42.6, "lon": 9.6}
            ]
        }
        
        with patch('weather.centralized_context.get_current_stage', return_value=mock_today_stage), \
             patch('weather.centralized_context.get_next_stage', return_value=mock_tomorrow_stage), \
             patch('weather.centralized_context.get_day_after_tomorrow_stage', return_value=mock_day_after_tomorrow_stage):
            
            context = create_report_context('evening', date(2025, 8, 7))
            
            # Verify context structure
            assert context.report_type == 'evening'
            assert context.report_date == date(2025, 8, 7)
            
            # Verify today's data
            assert context.today.stage_name == 'TestStage'
            assert len(context.today.points) == 2
            assert context.today.points[0].lat == 42.1
            assert context.today.points[0].lon == 9.1
            assert context.today.points[1].lat == 42.2
            assert context.today.points[1].lon == 9.2
            
            # Verify tomorrow's data
            assert context.tomorrow.stage_name == 'TestStage2'
            assert len(context.tomorrow.points) == 3
            assert context.tomorrow.points[0].lat == 42.3
            assert context.tomorrow.points[0].lon == 9.3
            
            # Verify day after tomorrow's data
            assert context.day_after_tomorrow.stage_name == 'TestStage3'
            assert len(context.day_after_tomorrow.points) == 1
            assert context.day_after_tomorrow.points[0].lat == 42.6
            assert context.day_after_tomorrow.points[0].lon == 9.6
    
    def test_coordinate_mapping(self):
        """Test coordinate mapping functionality."""
        # Create context with test data
        today_data = StageData(
            date=date(2025, 8, 7),
            stage_name="TestStage",
            points=[
                CoordinatePoint(42.1, 9.1, "point1"),
                CoordinatePoint(42.2, 9.2, "point2")
            ]
        )
        
        tomorrow_data = StageData(
            date=date(2025, 8, 8),
            stage_name="TestStage2", 
            points=[
                CoordinatePoint(42.3, 9.3, "point3")
            ]
        )
        
        day_after_tomorrow_data = StageData(
            date=date(2025, 8, 9),
            stage_name="TestStage3",
            points=[
                CoordinatePoint(42.4, 9.4, "point4")
            ]
        )
        
        context = ReportContext(
            report_date=date(2025, 8, 7),
            report_type='evening',
            today=today_data,
            tomorrow=tomorrow_data,
            day_after_tomorrow=day_after_tomorrow_data
        )
        
        # Test coordinate mapping
        assert context.get_coordinate('T1G1').lat == 42.1
        assert context.get_coordinate('T1G1').lon == 9.1
        assert context.get_coordinate('T1G2').lat == 42.2
        assert context.get_coordinate('T1G2').lon == 9.2
        assert context.get_coordinate('T2G1').lat == 42.3
        assert context.get_coordinate('T2G1').lon == 9.3
        assert context.get_coordinate('T3G1').lat == 42.4
        assert context.get_coordinate('T3G1').lon == 9.4
        
        # Test non-existent coordinate
        assert context.get_coordinate('T1G3') is None
    
    def test_get_debug_summary(self):
        """Test debug summary generation."""
        # Create context with test data
        today_data = StageData(
            date=date(2025, 8, 7),
            stage_name="TestStage",
            points=[
                CoordinatePoint(42.1, 9.1, "point1"),
                CoordinatePoint(42.2, 9.2, "point2")
            ]
        )
        
        tomorrow_data = StageData(
            date=date(2025, 8, 8),
            stage_name="TestStage2",
            points=[
                CoordinatePoint(42.3, 9.3, "point3")
            ]
        )
        
        day_after_tomorrow_data = StageData(
            date=date(2025, 8, 9),
            stage_name="TestStage3",
            points=[
                CoordinatePoint(42.4, 9.4, "point4")
            ]
        )
        
        context = ReportContext(
            report_date=date(2025, 8, 7),
            report_type='evening',
            today=today_data,
            tomorrow=tomorrow_data,
            day_after_tomorrow=day_after_tomorrow_data
        )
        
        summary = get_debug_summary(context)
        
        # Verify summary contains expected information
        assert "Berichts-Typ: evening" in summary
        assert "heute: 2025-08-07, TestStage, 2 Punkte" in summary
        assert "  T1G1 \"lat\": 42.1, \"lon\": 9.1" in summary
        assert "  T1G2 \"lat\": 42.2, \"lon\": 9.2" in summary
        assert "morgen: 2025-08-08, TestStage2, 1 Punkte" in summary
        assert "  T2G1 \"lat\": 42.3, \"lon\": 9.3" in summary
        assert "übermorgen: 2025-08-09, TestStage3, 1 Punkte" in summary
        assert "  T3G1 \"lat\": 42.4, \"lon\": 9.4" in summary 