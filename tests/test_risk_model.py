import pytest
from typing import Dict

# Import the functions to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from logic.analyse_weather import compute_risk


class TestRiskModel:
    """Test cases for the configurable risk model functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.base_config = {
            "risk_model": {
                "thunderstorm_probability": {
                    "threshold": 50,
                    "weight": 0.4
                },
                "cape": {
                    "threshold": 800,
                    "weight": 0.3
                },
                "lifted_index": {
                    "threshold": -4,
                    "weight": 0.3
                },
                "wind_speed": {
                    "threshold": 60,
                    "weight": 0.2
                },
                "precipitation": {
                    "threshold": 10,
                    "weight": 0.1
                },
                "temperature": {
                    "threshold": 35,
                    "weight": 0.1
                }
            }
        }
    
    def test_compute_risk_no_risk_all_values_below_thresholds(self):
        """Test risk computation when all values are below thresholds"""
        metrics = {
            "thunderstorm_probability": 30,
            "cape": 400,
            "lifted_index": -2,
            "wind_speed": 40,
            "precipitation": 5,
            "temperature": 25
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        assert risk == 0.0
    
    def test_compute_risk_single_threshold_exceeded(self):
        """Test risk computation when one threshold is exceeded"""
        metrics = {
            "thunderstorm_probability": 70,  # Above 50 threshold
            "cape": 400,
            "lifted_index": -2,
            "wind_speed": 40,
            "precipitation": 5,
            "temperature": 25
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        assert risk == 0.4  # Only thunderstorm probability weight
    
    def test_compute_risk_multiple_thresholds_exceeded(self):
        """Test risk computation when multiple thresholds are exceeded"""
        metrics = {
            "thunderstorm_probability": 70,  # Above 50 threshold
            "cape": 1200,  # Above 800 threshold
            "lifted_index": -5,  # Above -4 threshold
            "wind_speed": 40,
            "precipitation": 5,
            "temperature": 25
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        expected_risk = 0.4 + 0.3 + 0.3  # thunderstorm + cape + lifted_index
        assert risk == expected_risk
    
    def test_compute_risk_all_thresholds_exceeded(self):
        """Test risk computation when all thresholds are exceeded"""
        metrics = {
            "thunderstorm_probability": 80,
            "cape": 1500,
            "lifted_index": -6,
            "wind_speed": 80,
            "precipitation": 20,
            "temperature": 40
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        # Should be capped at 1.0
        assert risk == 1.0
    
    def test_compute_risk_unknown_parameters_ignored(self):
        """Test that unknown parameters in metrics are ignored"""
        metrics = {
            "thunderstorm_probability": 70,
            "cape": 1200,
            "unknown_parameter": 1000,  # Should be ignored
            "wind_speed": 40
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        expected_risk = 0.4 + 0.3  # thunderstorm + cape
        assert risk == expected_risk
    
    def test_compute_risk_missing_parameters_ignored(self):
        """Test that missing parameters in metrics are ignored"""
        metrics = {
            "thunderstorm_probability": 70,
            "cape": 1200
            # Missing lifted_index, wind_speed, etc.
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        expected_risk = 0.4 + 0.3  # thunderstorm + cape
        assert risk == expected_risk
    
    def test_compute_risk_empty_metrics(self):
        """Test risk computation with empty metrics"""
        metrics = {}
        
        risk = compute_risk(metrics, self.base_config)
        
        assert risk == 0.0
    
    def test_compute_risk_empty_config(self):
        """Test risk computation with empty config"""
        metrics = {
            "thunderstorm_probability": 70,
            "cape": 1200
        }
        empty_config = {}
        
        risk = compute_risk(metrics, empty_config)
        
        assert risk == 0.0
    
    def test_compute_risk_missing_risk_model_config(self):
        """Test risk computation when risk_model section is missing"""
        metrics = {
            "thunderstorm_probability": 70,
            "cape": 1200
        }
        config_without_risk_model = {"other_config": "value"}
        
        risk = compute_risk(metrics, config_without_risk_model)
        
        assert risk == 0.0
    
    def test_compute_risk_partial_risk_model_config(self):
        """Test risk computation with partial risk model configuration"""
        partial_config = {
            "risk_model": {
                "thunderstorm_probability": {
                    "threshold": 50,
                    "weight": 0.4
                }
                # Missing other parameters
            }
        }
        
        metrics = {
            "thunderstorm_probability": 70,
            "cape": 1200  # Should be ignored since not in config
        }
        
        risk = compute_risk(metrics, partial_config)
        
        assert risk == 0.4  # Only thunderstorm probability weight
    
    def test_compute_risk_none_values_ignored(self):
        """Test that None values in metrics are ignored"""
        metrics = {
            "thunderstorm_probability": 70,
            "cape": None,  # Should be ignored
            "lifted_index": -5
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        expected_risk = 0.4 + 0.3  # thunderstorm + lifted_index
        assert risk == expected_risk
    
    def test_compute_risk_exact_threshold_values(self):
        """Test risk computation with values exactly at thresholds"""
        metrics = {
            "thunderstorm_probability": 50,  # Exactly at threshold
            "cape": 800,  # Exactly at threshold
            "lifted_index": -4,  # Exactly at threshold
            "wind_speed": 40,
            "precipitation": 5,
            "temperature": 25
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        # Values exactly at threshold should not contribute to risk
        assert risk == 0.0
    
    def test_compute_risk_just_below_threshold_values(self):
        """Test risk computation with values just below thresholds"""
        metrics = {
            "thunderstorm_probability": 49,  # Just below threshold
            "cape": 799,  # Just below threshold
            "lifted_index": -3.9,  # Just below threshold
            "wind_speed": 40,
            "precipitation": 5,
            "temperature": 25
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        assert risk == 0.0
    
    def test_compute_risk_just_above_threshold_values(self):
        """Test risk computation with values just above thresholds"""
        metrics = {
            "thunderstorm_probability": 51,  # Just above threshold
            "cape": 801,  # Just above threshold
            "lifted_index": -4.1,  # Just above threshold
            "wind_speed": 40,
            "precipitation": 5,
            "temperature": 25
        }
        
        risk = compute_risk(metrics, self.base_config)
        
        expected_risk = 0.4 + 0.3 + 0.3  # All three weights
        assert risk == expected_risk 