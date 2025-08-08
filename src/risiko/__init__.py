"""
Alternative risk analysis module.

This module provides an alternative approach to weather risk analysis
that uses direct API data without traditional thresholds (except for rain).
"""

from .alternative_risk_analysis import (
    AlternativeRiskAnalyzer,
    RiskAnalysisResult,
    WeatherRiskType
)

__all__ = [
    'AlternativeRiskAnalyzer',
    'RiskAnalysisResult', 
    'WeatherRiskType'
] 