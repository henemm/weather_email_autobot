"""
Tests for email integration with alternative risk analysis.

This module tests the complete email generation pipeline including
the alternative risk analysis integration.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date
from typing import Dict, Any

from src.report.weather_report_generator import generate_weather_report
from src.notification.email_client import EmailClient


class TestEmailIntegration:
    """Test cases for email integration with alternative risk analysis."""

    def test_email_generation_with_alternative_risk_analysis(self):
        """Test that email generation includes alternative risk analysis."""
        # Mock configuration with alternative risk analysis enabled
        config = {
            "alternative_risk_analysis": {
                "enabled": True
            },
            "email": {
                "subject": "GR20 Wetter"
            },
            "startdatum": "2025-07-29",
            "etappen": {
                "2025-07-29": {
                    "name": "Croci",
                    "coordinates": [
                        [42.123, 9.456],
                        [42.124, 9.457],
                        [42.125, 9.458],
                        [42.126, 9.459]
                    ]
                }
            }
        }
        
        # Generate the weather report
        report_result = generate_weather_report(
            report_type='morning',
            config=config
        )
        
        # Extract the report text
        report_text = report_result.get('report_text', '')
        
        # Verify that alternative risk analysis is included
        assert "## 🔍 Alternative Risk Analysis" in report_text
        
        # Verify the structure: standard report, separator, alternative report
        parts = report_text.split("---")
        assert len(parts) >= 2, "Report should contain separator '---'"
        
        # Check that alternative analysis comes after standard report
        alternative_section = parts[-1]  # Last part after separator
        assert "## 🔍 Alternative Risk Analysis" in alternative_section
        
        # Verify alternative analysis content
        assert "🔥 **Heat**" in alternative_section
        assert "❄️ **Cold**" in alternative_section
        assert "🌧️ **Rain**" in alternative_section
        assert "⛈️ **Thunderstorm**" in alternative_section
        assert "🌬️ **Wind**" in alternative_section

    def test_email_generation_without_alternative_risk_analysis(self):
        """Test that email generation works without alternative risk analysis."""
        # Mock configuration with alternative risk analysis disabled
        config = {
            "alternative_risk_analysis": {
                "enabled": False
            },
            "email": {
                "subject": "GR20 Wetter"
            },
            "startdatum": "2025-07-29",
            "etappen": {
                "2025-07-29": {
                    "name": "Croci",
                    "coordinates": [
                        [42.123, 9.456],
                        [42.124, 9.457],
                        [42.125, 9.458],
                        [42.126, 9.459]
                    ]
                }
            }
        }
        
        # Generate the weather report
        report_result = generate_weather_report(
            report_type='morning',
            config=config
        )
        
        # Extract the report text
        report_text = report_result.get('report_text', '')
        
        # Verify that alternative risk analysis is NOT included
        assert "## 🔍 Alternative Risk Analysis" not in report_text
        
        # Verify that separator is NOT present
        assert "---" not in report_text

    def test_email_format_structure(self):
        """Test that email has correct format structure."""
        config = {
            "alternative_risk_analysis": {
                "enabled": True
            },
            "email": {
                "subject": "GR20 Wetter"
            },
            "startdatum": "2025-07-29",
            "etappen": {
                "2025-07-29": {
                    "name": "Croci",
                    "coordinates": [
                        [42.123, 9.456],
                        [42.124, 9.457],
                        [42.125, 9.458],
                        [42.126, 9.459]
                    ]
                }
            }
        }
        
        report_result = generate_weather_report(
            report_type='morning',
            config=config
        )
        
        report_text = report_result.get('report_text', '')
        
        # Verify correct structure: standard report -> separator -> alternative report
        lines = report_text.split('\n')
        
        # Find the separator line
        separator_index = None
        for i, line in enumerate(lines):
            if line.strip() == "---":
                separator_index = i
                break
        
        assert separator_index is not None, "Separator '---' should be present"
        
        # Verify that alternative analysis comes after separator
        after_separator = '\n'.join(lines[separator_index + 1:])
        assert "## 🔍 Alternative Risk Analysis" in after_separator
        
        # Verify that debug info comes after alternative analysis (if present)
        if "--- DEBUG INFO ---" in report_text:
            debug_index = report_text.find("--- DEBUG INFO ---")
            alternative_index = report_text.find("## 🔍 Alternative Risk Analysis")
            assert alternative_index < debug_index, "Alternative analysis should come before debug info"

    def test_alternative_risk_analysis_error_handling(self):
        """Test that alternative risk analysis errors are handled gracefully."""
        config = {
            "alternative_risk_analysis": {
                "enabled": True
            },
            "email": {
                "subject": "GR20 Wetter"
            },
            "startdatum": "2025-07-29",
            "etappen": {
                "2025-07-29": {
                    "name": "Croci",
                    "coordinates": [
                        [42.123, 9.456],
                        [42.124, 9.457],
                        [42.125, 9.458],
                        [42.126, 9.459]
                    ]
                }
            }
        }
        
        # This should not raise an exception even with invalid data
        report_result = generate_weather_report(
            report_type='morning',
            config=config
        )
        
        report_text = report_result.get('report_text', '')
        
        # Verify that alternative analysis is still included with error messages
        assert "## 🔍 Alternative Risk Analysis" in report_text
        assert "❌ MeteoFrance API failure" in report_text 