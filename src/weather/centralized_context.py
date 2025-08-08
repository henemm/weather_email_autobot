"""
Centralized context for weather report data.

This module determines all data (dates and coordinates) once and stores them
as constants for all methods to use consistently.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

from position.etappenlogik import get_current_stage, get_next_stage, get_day_after_tomorrow_stage

logger = logging.getLogger(__name__)


@dataclass
class CoordinatePoint:
    """Represents a coordinate point with lat/lon."""
    lat: float
    lon: float
    name: str


@dataclass
class StageData:
    """Represents stage data for a specific day."""
    date: date
    stage_name: str
    points: List[CoordinatePoint]


@dataclass
class ReportContext:
    """Centralized context for weather report data."""
    report_date: date
    report_type: str  # 'morning' or 'evening'
    
    # Stage data for today, tomorrow, and day after tomorrow
    today: StageData
    tomorrow: StageData
    day_after_tomorrow: StageData
    
    # Cached coordinate mappings for easy access
    coordinate_mapping: Dict[str, CoordinatePoint] = None
    
    def __post_init__(self):
        """Initialize coordinate mapping after object creation."""
        if self.coordinate_mapping is None:
            self.coordinate_mapping = {}
            self._build_coordinate_mapping()
    
    def _build_coordinate_mapping(self):
        """Build coordinate mapping for all points."""
        # Today's points (T1G1, T1G2, T1G3, etc.)
        for i, point in enumerate(self.today.points, 1):
            self.coordinate_mapping[f"T1G{i}"] = point
        
        # Tomorrow's points (T2G1, T2G2, T2G3, etc.)
        for i, point in enumerate(self.tomorrow.points, 1):
            self.coordinate_mapping[f"T2G{i}"] = point
        
        # Day after tomorrow's points (T3G1, T3G2, T3G3, etc.)
        for i, point in enumerate(self.day_after_tomorrow.points, 1):
            self.coordinate_mapping[f"T3G{i}"] = point
    
    def get_coordinate(self, point_id: str) -> Optional[CoordinatePoint]:
        """Get coordinate for a specific point ID (e.g., 'T1G1', 'T2G3')."""
        return self.coordinate_mapping.get(point_id)
    
    def get_all_coordinates(self) -> Dict[str, CoordinatePoint]:
        """Get all coordinates as a dictionary."""
        return self.coordinate_mapping.copy()
    
    def get_today_coordinates(self) -> List[CoordinatePoint]:
        """Get all today's coordinates."""
        return self.today.points
    
    def get_tomorrow_coordinates(self) -> List[CoordinatePoint]:
        """Get all tomorrow's coordinates."""
        return self.tomorrow.points
    
    def get_day_after_tomorrow_coordinates(self) -> List[CoordinatePoint]:
        """Get all day after tomorrow's coordinates."""
        return self.day_after_tomorrow.points


def create_report_context(report_type: str, report_date: Optional[date] = None, config: Optional[Dict] = None) -> ReportContext:
    """
    Create centralized report context with all data determined once.
    
    Args:
        report_type: 'morning' or 'evening'
        report_date: Optional report date, defaults to today
        config: Configuration dictionary (required for stage determination)
        
    Returns:
        ReportContext with all data determined and stored as constants
    """
    if report_date is None:
        report_date = date.today()
    
    if config is None:
        # Load config from file
        import yaml
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise ValueError("Config is required for stage determination")
    
    logger.info(f"Creating centralized context for {report_type} report on {report_date}")
    
    # Get stage data for all three days
    today_stage = get_current_stage(config)
    tomorrow_stage = get_next_stage(config)
    day_after_tomorrow_stage = get_day_after_tomorrow_stage(config)
    
    # Create stage data objects
    today_data = StageData(
        date=report_date,
        stage_name=today_stage["name"],
        points=[CoordinatePoint(p["lat"], p["lon"], f"{today_stage['name']}_point_{i+1}") 
                for i, p in enumerate(today_stage["punkte"])]
    )
    
    tomorrow_data = StageData(
        date=report_date.replace(day=report_date.day + 1),
        stage_name=tomorrow_stage["name"],
        points=[CoordinatePoint(p["lat"], p["lon"], f"{tomorrow_stage['name']}_point_{i+1}") 
                for i, p in enumerate(tomorrow_stage["punkte"])]
    )
    
    day_after_tomorrow_data = StageData(
        date=report_date.replace(day=report_date.day + 2),
        stage_name=day_after_tomorrow_stage["name"],
        points=[CoordinatePoint(p["lat"], p["lon"], f"{day_after_tomorrow_stage['name']}_point_{i+1}") 
                for i, p in enumerate(day_after_tomorrow_stage["punkte"])]
    )
    
    # Create and return context
    context = ReportContext(
        report_date=report_date,
        report_type=report_type,
        today=today_data,
        tomorrow=tomorrow_data,
        day_after_tomorrow=day_after_tomorrow_data
    )
    
    logger.info(f"Created context: today={today_data.stage_name} ({len(today_data.points)} points), "
                f"tomorrow={tomorrow_data.stage_name} ({len(tomorrow_data.points)} points), "
                f"day_after_tomorrow={day_after_tomorrow_data.stage_name} ({len(day_after_tomorrow_data.points)} points)")
    
    return context


def get_debug_summary(context: ReportContext) -> str:
    """
    Generate debug summary showing all determined data.
    
    Args:
        context: ReportContext with all data
        
    Returns:
        Formatted debug summary string
    """
    summary = []
    summary.append(f"Berichts-Typ: {context.report_type}")
    summary.append("")
    
    # Today
    summary.append(f"heute: {context.today.date}, {context.today.stage_name}, {len(context.today.points)} Punkte")
    for i, point in enumerate(context.today.points, 1):
        summary.append(f"  T1G{i} \"lat\": {point.lat}, \"lon\": {point.lon}")
    
    # Tomorrow
    summary.append(f"morgen: {context.tomorrow.date}, {context.tomorrow.stage_name}, {len(context.tomorrow.points)} Punkte")
    for i, point in enumerate(context.tomorrow.points, 1):
        summary.append(f"  T2G{i} \"lat\": {point.lat}, \"lon\": {point.lon}")
    
    # Day after tomorrow
    summary.append(f"übermorgen: {context.day_after_tomorrow.date}, {context.day_after_tomorrow.stage_name}, {len(context.day_after_tomorrow.points)} Punkte")
    for i, point in enumerate(context.day_after_tomorrow.points, 1):
        summary.append(f"  T3G{i} \"lat\": {point.lat}, \"lon\": {point.lon}")
    
    return "\n".join(summary) 