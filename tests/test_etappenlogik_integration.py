"""
Integration tests for stage logic.

This module tests the stage selection logic based on start date
and current date using real etappen.json data.
"""

import pytest
import tempfile
import json
import os
from datetime import datetime, date
from unittest.mock import patch

from position.etappenlogik import (
    get_current_stage,
    get_stage_info,
    get_next_stage,
    get_day_after_tomorrow_stage
)


@pytest.fixture
def sample_etappen():
    """Sample etappen data for testing."""
    return [
        {
            "name": "E1 Ortu",
            "punkte": [
                {"lat": 42.510501, "lon": 8.851262},
                {"lat": 42.471362, "lon": 8.897105}
            ]
        },
        {
            "name": "E2 Carozzu", 
            "punkte": [
                {"lat": 42.465338, "lon": 8.906787},
                {"lat": 42.463894, "lon": 8.894516}
            ]
        },
        {
            "name": "E3 Ascu",
            "punkte": [
                {"lat": 42.426238, "lon": 8.900291},
                {"lat": 42.410526, "lon": 8.908343}
            ]
        }
    ]


@pytest.fixture
def temp_etappen_file(sample_etappen):
    """Create a temporary etappen.json file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_etappen, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)


def test_get_current_stage_day_1(temp_etappen_file):
    """Test stage selection for day 1."""
    config = {"startdatum": "2025-06-25"}
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 25)  # Same as start date
        
        stage = get_current_stage(config, temp_etappen_file)
        
        assert stage is not None
        assert stage["name"] == "E1 Ortu"


def test_get_current_stage_day_2(temp_etappen_file):
    """Test stage selection for day 2."""
    config = {"startdatum": "2025-06-25"}
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 26)  # Day after start
        
        stage = get_current_stage(config, temp_etappen_file)
        
        assert stage is not None
        assert stage["name"] == "E2 Carozzu"


def test_get_current_stage_day_3(temp_etappen_file):
    """Test stage selection for day 3."""
    config = {"startdatum": "2025-06-25"}
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 27)  # Two days after start
        
        stage = get_current_stage(config, temp_etappen_file)
        
        assert stage is not None
        assert stage["name"] == "E3 Ascu"


def test_get_current_stage_no_stage_available(temp_etappen_file):
    """Test when no stage is available (day 4)."""
    config = {"startdatum": "2025-06-25"}
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 28)  # Three days after start
        
        stage = get_current_stage(config, temp_etappen_file)
        
        assert stage is None


def test_get_current_stage_before_start_date(temp_etappen_file):
    """Test when current date is before start date."""
    config = {"startdatum": "2025-06-25"}
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 24)  # Day before start
        
        stage = get_current_stage(config, temp_etappen_file)
        
        assert stage is None


def test_get_stage_info_with_coordinates(temp_etappen_file):
    """Test getting stage info with coordinates."""
    config = {"startdatum": "2025-06-25"}
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 25)
        
        stage_info = get_stage_info(config, temp_etappen_file)
        
        assert stage_info is not None
        assert stage_info["name"] == "E1 Ortu"
        assert len(stage_info["coordinates"]) == 2
        assert stage_info["coordinates"][0] == (42.510501, 8.851262)


def test_get_next_stage(temp_etappen_file):
    """Test getting next stage."""
    config = {"startdatum": "2025-06-25"}
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 25)
        
        next_stage = get_next_stage(config, temp_etappen_file)
        
        assert next_stage is not None
        assert next_stage["name"] == "E2 Carozzu"


def test_get_day_after_tomorrow_stage(temp_etappen_file):
    """Test getting day after tomorrow stage."""
    config = {"startdatum": "2025-06-25"}
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 25)
        
        day_after_stage = get_day_after_tomorrow_stage(config, temp_etappen_file)
        
        assert day_after_stage is not None
        assert day_after_stage["name"] == "E3 Ascu"


def test_invalid_startdatum_format(temp_etappen_file):
    """Test with invalid startdatum format."""
    config = {"startdatum": "invalid-date"}
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 25)
        
        with pytest.raises(ValueError, match="Invalid startdatum format"):
            get_current_stage(config, temp_etappen_file)


def test_missing_startdatum(temp_etappen_file):
    """Test with missing startdatum in config."""
    config = {}  # No startdatum
    
    with patch('position.etappenlogik.date') as mock_date:
        mock_date.today.return_value = date(2025, 6, 25)
        
        stage = get_current_stage(config, temp_etappen_file)
        
        assert stage is None 