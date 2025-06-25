"""
Position module for GR20 weather reports.

This module handles position-related functionality including stage logic
and ShareMap integration.
"""

from .etappenlogik import (
    get_current_stage,
    get_stage_coordinates,
    get_stage_info,
    get_next_stage,
    get_day_after_tomorrow_stage,
    load_etappen_data
)

__all__ = [
    'get_current_stage',
    'get_stage_coordinates', 
    'get_stage_info',
    'get_next_stage',
    'get_day_after_tomorrow_stage',
    'load_etappen_data'
] 