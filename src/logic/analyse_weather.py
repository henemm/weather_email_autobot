from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

from model.datatypes import WeatherData, WeatherPoint

logger = logging.getLogger(__name__)


class RiskType(Enum):
    """Enum für verschiedene Wetterrisiko-Typen"""
    REGEN = "regen"
    GEWITTER = "gewitter"
    WIND = "wind"
    BEWOELKUNG = "bewoelkung"
    HITZE = "hitze"
    CAPE_SHEAR = "cape_shear"
    
    # English values (new)
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    HIGH_WIND = "high_wind"
    OVERCAST = "overcast"
    HEAT_WAVE = "heat_wave"


class RiskLevel(Enum):
    """Enum für Risikostufen"""
    NIEDRIG = "niedrig"
    MITTEL = "mittel"
    HOCH = "hoch"
    SEHR_HOCH = "sehr_hoch"
    
    # English values (new)
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class WeatherRisk:
    """Einzelnes Wetterrisiko"""
    risk_type: RiskType
    level: RiskLevel
    value: float
    threshold: float
    time: datetime
    description: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class WeatherAnalysis:
    """Ergebnis der Wetteranalyse"""
    risks: List[WeatherRisk] = field(default_factory=list)
    max_thunderstorm_probability: Optional[float] = None
    max_rain_probability: Optional[float] = None
    max_precipitation: float = 0.0
    max_wind_speed: float = 0.0
    max_wind_gusts: Optional[float] = None  # Add maximum wind gusts
    max_cloud_cover: float = 0.0
    max_temperature: float = 0.0
    max_cape_shear: Optional[float] = None
    summary: str = ""
    risk: float = 0.0  # Computed risk score from risk model


def get_default_thresholds() -> Dict[str, float]:
    """
    Returns default threshold values for weather analysis.
    
    Returns:
        Dict[str, float]: Default threshold values
    """
    return {
        "rain_probability": 25.0,      # Regenwahrscheinlichkeit in %
        "rain_amount": 2.0,           # Regenmenge in mm
        "thunderstorm_probability": 20.0,  # Gewitterwahrscheinlichkeit in %
        "wind_speed": 20.0,            # Windgeschwindigkeit in km/h
        "temperature": 32.0,           # Temperatur in °C
        "cloud_cover": 90.0,           # Bewölkung in %
    }


def merge_weather_data_sources(weather_data_list: List[WeatherData]) -> WeatherData:
    """
    Führt mehrere Wetterdatenquellen zusammen (Worst-Case-Prinzip).
    
    Args:
        weather_data_list: Liste von WeatherData-Objekten aus verschiedenen Quellen
        
    Returns:
        WeatherData: Zusammengeführte Daten mit höchsten Risikowerten
    """
    if not weather_data_list:
        return WeatherData(points=[])
    
    if len(weather_data_list) == 1:
        return weather_data_list[0]
    
    # Sammle alle Zeitpunkte
    all_times = set()
    for weather_data in weather_data_list:
        for point in weather_data.points:
            all_times.add(point.time)
    
    # Erstelle Worst-Case-Punkte für jeden Zeitpunkt
    merged_points = []
    for time in sorted(all_times):
        worst_case_point = None
        
        for weather_data in weather_data_list:
            for point in weather_data.points:
                if point.time == time:
                    if worst_case_point is None:
                        worst_case_point = point
                    else:
                        # Wähle den "gefährlichsten" Punkt
                        worst_case_point = _select_worst_case_point(worst_case_point, point)
        
        if worst_case_point:
            merged_points.append(worst_case_point)
    
    return WeatherData(points=merged_points)


def _select_worst_case_point(point1: WeatherPoint, point2: WeatherPoint) -> WeatherPoint:
    """
    Wählt den "gefährlichsten" Punkt aus zwei Punkten.
    
    Args:
        point1: Erster Wetterpunkt
        point2: Zweiter Wetterpunkt
        
    Returns:
        WeatherPoint: Punkt mit höheren Risikowerten
    """
    # Verwende den Punkt mit höheren Risikowerten
    if (point2.precipitation > point1.precipitation or
        (point2.thunderstorm_probability or 0) > (point1.thunderstorm_probability or 0) or
        point2.wind_speed > point1.wind_speed or
        point2.cloud_cover > point1.cloud_cover or
        point2.temperature > point1.temperature):
        return point2
    else:
        return point1


def analyze_weather_data(
    weather_data: Union[WeatherData, List[WeatherData]],
    config: Dict
) -> WeatherAnalysis:
    """
    Analysiert Wetterdaten auf Risiken und generiert eine Zusammenfassung.
    
    Args:
        weather_data: Wetterdaten oder Liste von Wetterdaten
        config: Konfigurationsdictionary mit Schwellenwerten
        
    Returns:
        WeatherAnalysis: Analyseergebnis mit Risiken und Zusammenfassung
    """
    logger.info("Starting weather data analysis")
    
    # Handle multiple data sources
    if isinstance(weather_data, list):
        if len(weather_data) == 0:
            logger.warning("No weather data provided")
            return WeatherAnalysis()
        elif len(weather_data) == 1:
            weather_data = weather_data[0]
        else:
            logger.info(f"Merging {len(weather_data)} weather data sources")
            weather_data = merge_weather_data_sources(weather_data)
    
    if not weather_data or not weather_data.points:
        logger.warning("No weather data points available")
        return WeatherAnalysis()
    
    # Get thresholds from config or use defaults
    thresholds = get_default_thresholds()
    if "thresholds" in config:
        thresholds.update(config["thresholds"])
    elif "schwellen" in config:  # Legacy support
        logger.warning("Using legacy 'schwellen' config - consider updating to 'thresholds'")
        legacy_mapping = {
            "regen": "rain_probability",
            "regenmenge": "rain_amount", 
            "gewitter": "thunderstorm_probability",
            "wind": "wind_speed",
            "hitze": "temperature",
            "bewoelkung": "cloud_cover"
        }
        for old_key, new_key in legacy_mapping.items():
            if old_key in config["schwellen"]:
                thresholds[new_key] = config["schwellen"][old_key]
    
    logger.info(f"Using thresholds: {thresholds}")
    
    # Analyze each weather point
    all_risks = []
    max_values = {
        "precipitation": 0.0,
        "rain_probability": 0.0,  # Add rain probability tracking
        "wind_speed": 0.0,
        "wind_gusts": 0.0,  # Add wind gusts tracking
        "cloud_cover": 0.0,
        "temperature": 0.0,
        "thunderstorm_probability": 0.0,
        "cape_shear": 0.0  # Add cape_shear to fix KeyError
    }
    
    for point in weather_data.points:
        # Update max values
        max_values["precipitation"] = max(max_values["precipitation"], point.precipitation or 0.0)
        max_values["rain_probability"] = max(max_values["rain_probability"], point.rain_probability or 0.0)  # Track rain probability
        max_values["wind_speed"] = max(max_values["wind_speed"], point.wind_speed or 0.0)
        if point.wind_gusts:  # Track wind gusts if available
            max_values["wind_gusts"] = max(max_values["wind_gusts"], point.wind_gusts)
        max_values["cloud_cover"] = max(max_values["cloud_cover"], point.cloud_cover or 0.0)
        max_values["temperature"] = max(max_values["temperature"], point.temperature or 0.0)
        if point.thunderstorm_probability:
            max_values["thunderstorm_probability"] = max(max_values["thunderstorm_probability"], point.thunderstorm_probability)
        
        # Analyze risks for this point
        point_risks = _analyze_weather_point(point, thresholds)
        all_risks.extend(point_risks)
    
    # Generate summary
    summary = _generate_summary(all_risks, max_values, thresholds)
    
    # Compute risk score using risk model
    risk_score = 0.0
    if "risk_model" in config:
        risk_score = compute_risk(max_values, config)
    
    logger.info(f"Weather analysis completed: {len(all_risks)} risks detected, risk score: {risk_score:.2f}")
    
    return WeatherAnalysis(
        risks=all_risks,
        max_thunderstorm_probability=max_values["thunderstorm_probability"] if max_values["thunderstorm_probability"] > 0 else None,
        max_rain_probability=max_values["rain_probability"] if max_values["rain_probability"] > 0 else None,  # Add rain probability
        max_precipitation=max_values["precipitation"],
        max_wind_speed=max_values["wind_speed"],
        max_wind_gusts=max_values["wind_gusts"],
        max_cloud_cover=max_values["cloud_cover"],
        max_temperature=max_values["temperature"],
        max_cape_shear=max_values["cape_shear"] if max_values["cape_shear"] > 0 else None,
        summary=summary,
        risk=risk_score
    )


def _analyze_weather_point(point: WeatherPoint, thresholds: Dict[str, float]) -> List[WeatherRisk]:
    """
    Analysiert einen einzelnen Wetterpunkt auf Risiken.
    
    Args:
        point: WeatherPoint zu analysieren
        thresholds: Schwellenwerte
        
    Returns:
        List[WeatherRisk]: Liste der erkannten Risiken
    """
    risks = []
    
    # Get threshold values (support both German and English keys)
    rain_threshold = thresholds.get("rain_amount", thresholds.get("rain_probability", thresholds.get("precipitation", 2.0)))
    rain_probability_threshold = thresholds.get("rain_probability", 25.0)  # Add rain probability threshold
    wind_threshold = thresholds.get("wind", thresholds.get("wind_speed", 40.0))
    cloud_threshold = thresholds.get("cloud_cover", thresholds.get("bewoelkung", 90.0))
    heat_threshold = thresholds.get("temperature", thresholds.get("hitze", 30.0))
    storm_threshold = thresholds.get("thunderstorm_probability", thresholds.get("gewitter", thresholds.get("gewitter_wahrscheinlichkeit", 20.0)))
    
    # Regenwahrscheinlichkeit-Risiko / Rain Probability Risk
    if point.rain_probability and point.rain_probability > rain_probability_threshold:
        level = _determine_risk_level(point.rain_probability, rain_probability_threshold, [25, 50, 75])
        risks.append(WeatherRisk(
            risk_type=RiskType.REGEN,  # German for backward compatibility
            level=level,  # Keep German level for backward compatibility
            value=point.rain_probability,
            threshold=rain_probability_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Regenwahrscheinlichkeit {point.rain_probability:.0f}% über Schwellwert {rain_probability_threshold}%"
        ))
    
    # Regen-Risiko / Heavy Rain Risk
    if point.precipitation > rain_threshold:
        level = _determine_risk_level(point.precipitation, rain_threshold, [2, 5, 10])
        # Create both German and English risk types for backward compatibility
        risks.append(WeatherRisk(
            risk_type=RiskType.REGEN,  # German for backward compatibility
            level=level,  # Keep German level for backward compatibility
            value=point.precipitation,
            threshold=rain_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Niederschlag {point.precipitation:.1f}mm über Schwellwert {rain_threshold}mm"
        ))
    
    # Gewitter-Risiko / Thunderstorm Risk
    if point.thunderstorm_probability and point.thunderstorm_probability > storm_threshold:
        level = _determine_risk_level(point.thunderstorm_probability, storm_threshold, [20, 40, 60])
        risks.append(WeatherRisk(
            risk_type=RiskType.GEWITTER,  # German for backward compatibility
            level=level,  # Keep German level for backward compatibility
            value=point.thunderstorm_probability,
            threshold=storm_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Gewitterwahrscheinlichkeit {point.thunderstorm_probability:.0f}% über Schwellwert {storm_threshold}%"
        ))
    
    # Wind-Risiko / High Wind Risk
    if point.wind_speed > wind_threshold:
        level = _determine_risk_level(point.wind_speed, wind_threshold, [40, 60, 80])
        risks.append(WeatherRisk(
            risk_type=RiskType.WIND,  # German for backward compatibility
            level=level,  # Keep German level for backward compatibility
            value=point.wind_speed,
            threshold=wind_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Windgeschwindigkeit {point.wind_speed:.0f} km/h über Schwellwert {wind_threshold} km/h"
        ))
    
    # Bewölkungs-Risiko / Overcast Risk
    if point.cloud_cover > cloud_threshold:
        level = _determine_risk_level(point.cloud_cover, cloud_threshold, [90, 95, 98])
        risks.append(WeatherRisk(
            risk_type=RiskType.BEWOELKUNG,  # German for backward compatibility
            level=level,  # Keep German level for backward compatibility
            value=point.cloud_cover,
            threshold=cloud_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Bewölkung {point.cloud_cover:.0f}% über Schwellwert {cloud_threshold}%"
        ))
    
    # Hitze-Risiko / Heat Wave Risk
    if point.temperature > heat_threshold:
        level = _determine_risk_level(point.temperature, heat_threshold, [30, 35, 40])
        risks.append(WeatherRisk(
            risk_type=RiskType.HITZE,  # German for backward compatibility
            level=level,  # Keep German level for backward compatibility
            value=point.temperature,
            threshold=heat_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Temperatur {point.temperature:.1f}°C über Schwellwert {heat_threshold}°C"
        ))
    
    return risks


def _convert_risk_level(german_level: RiskLevel) -> RiskLevel:
    """Convert German risk level to English risk level"""
    conversion_map = {
        RiskLevel.NIEDRIG: RiskLevel.LOW,
        RiskLevel.MITTEL: RiskLevel.MODERATE,
        RiskLevel.HOCH: RiskLevel.HIGH,
        RiskLevel.SEHR_HOCH: RiskLevel.VERY_HIGH,
        RiskLevel.LOW: RiskLevel.LOW,
        RiskLevel.MODERATE: RiskLevel.MODERATE,
        RiskLevel.HIGH: RiskLevel.HIGH,
        RiskLevel.VERY_HIGH: RiskLevel.VERY_HIGH,
    }
    return conversion_map.get(german_level, RiskLevel.MODERATE)


def _determine_risk_level(value: float, threshold: float, level_thresholds: List[float]) -> RiskLevel:
    """
    Bestimmt die Risikostufe basierend auf Wert und Schwellenwerten.
    
    Args:
        value: Aktueller Wert
        threshold: Basis-Schwellwert
        level_thresholds: Schwellenwerte für verschiedene Stufen
        
    Returns:
        RiskLevel: Bestimmte Risikostufe
    """
    if value >= level_thresholds[2]:
        return RiskLevel.SEHR_HOCH
    elif value >= level_thresholds[1]:
        return RiskLevel.HOCH
    elif value >= level_thresholds[0]:
        return RiskLevel.MITTEL
    else:
        return RiskLevel.NIEDRIG


def _generate_summary(risks: List[WeatherRisk], max_values: Dict[str, float], thresholds: Dict[str, float]) -> str:
    """
    Generiert eine kompakte Zusammenfassung der Analyse.
    
    Args:
        risks: Liste der erkannten Risiken
        max_values: Maximalwerte
        thresholds: Schwellenwerte
        
    Returns:
        str: Zusammenfassung
    """
    if not risks:
        return "Keine kritischen Wetterbedingungen erkannt."
    
    # Gruppiere Risiken nach Typ
    risk_groups = {}
    for risk in risks:
        if risk.risk_type not in risk_groups:
            risk_groups[risk.risk_type] = []
        risk_groups[risk.risk_type].append(risk)
    
    summary_parts = []
    
    # Höchste Risiken zuerst
    for risk_type in [RiskType.GEWITTER, RiskType.REGEN, RiskType.WIND, RiskType.HITZE, RiskType.BEWOELKUNG]:
        if risk_type in risk_groups:
            risks_of_type = risk_groups[risk_type]
            highest_risk = max(risks_of_type, key=lambda r: r.level.value)
            
            risk_name = {
                RiskType.GEWITTER: "Gewitter",
                RiskType.REGEN: "Regen",
                RiskType.WIND: "Wind",
                RiskType.HITZE: "Hitze",
                RiskType.BEWOELKUNG: "Bewölkung"
            }[risk_type]
            
            summary_parts.append(f"{risk_name}: {highest_risk.level.value.upper()} ({highest_risk.value:.1f})")
    
    # Maximalwerte hinzufügen
    if max_values["precipitation"] > 0:
        summary_parts.append(f"Max. Niederschlag: {max_values['precipitation']:.1f}mm")
    if max_values["wind_speed"] > 0:
        summary_parts.append(f"Max. Wind: {max_values['wind_speed']:.0f} km/h")
    if max_values["temperature"] > 0:
        summary_parts.append(f"Max. Temperatur: {max_values['temperature']:.1f}°C")
    
    return " | ".join(summary_parts)


def analyze_multiple_sources(
    weather_data_list: List[WeatherData],
    config: Dict
) -> WeatherAnalysis:
    """
    Analysiert mehrere Wetterdatenquellen mit Worst-Case-Prinzip.
    
    Args:
        weather_data_list: Liste von WeatherData-Objekten aus verschiedenen Quellen
        config: Konfigurationsdictionary mit Schwellenwerten
        
    Returns:
        WeatherAnalysis: Analyseergebnis basierend auf höchsten Risikowerten
    """
    # Führe Datenquellen zusammen (Worst-Case-Prinzip)
    merged_data = merge_weather_data_sources(weather_data_list)
    
    # Analysiere zusammengeführte Daten
    return analyze_weather_data(merged_data, config)


def analyze_weather_data_english(
    weather_data: Union[WeatherData, List[WeatherData]],
    config: Dict
) -> WeatherAnalysis:
    """
    Analyzes weather data and detects potentially dangerous conditions (English interface).
    
    Args:
        weather_data: WeatherData object or list of WeatherData objects
        config: Configuration dictionary with threshold values
        
    Returns:
        WeatherAnalysis: Analysis result with detected risks using English enum values
    """
    # Handle multiple sources
    if isinstance(weather_data, list):
        if not weather_data:
            return WeatherAnalysis(summary="No weather data available")
        if len(weather_data) == 1:
            weather_data = weather_data[0]
        else:
            # Merge multiple sources using worst-case principle
            weather_data = merge_weather_data_sources(weather_data)
    
    if not weather_data.points:
        return WeatherAnalysis(summary="No weather data available")
    
    # Schwellenwerte aus Konfiguration extrahieren
    thresholds = get_default_thresholds()
    if "schwellen" in config:
        thresholds.update(config["schwellen"])
    
    risks = []
    max_values = {
        "thunderstorm_probability": 0.0,
        "precipitation": 0.0,
        "wind_speed": 0.0,
        "wind_gusts": 0.0,  # Add wind gusts tracking
        "cloud_cover": 0.0,
        "temperature": 0.0,
        "cape_shear": 0.0
    }
    
    # Analysiere jeden Wetterpunkt
    for point in weather_data.points:
        # Aktualisiere Maximalwerte
        max_values["precipitation"] = max(max_values["precipitation"], point.precipitation)
        max_values["wind_speed"] = max(max_values["wind_speed"], point.wind_speed)
        if point.wind_gusts:  # Track wind gusts if available
            max_values["wind_gusts"] = max(max_values["wind_gusts"], point.wind_gusts)
        max_values["cloud_cover"] = max(max_values["cloud_cover"], point.cloud_cover)
        max_values["temperature"] = max(max_values["temperature"], point.temperature)
        
        if point.thunderstorm_probability:
            max_values["thunderstorm_probability"] = max(
                max_values["thunderstorm_probability"], 
                point.thunderstorm_probability
            )
        
        # Prüfe Risiken mit englischen Enum-Werten
        point_risks = _analyze_weather_point_english(point, thresholds)
        risks.extend(point_risks)
    
    # Erstelle Zusammenfassung
    summary = _generate_summary_english(risks, max_values, thresholds)
    
    # Compute risk score using risk model
    risk_score = 0.0
    if "risk_model" in config:
        # Extract metrics from weather data for risk computation
        metrics = {
            "thunderstorm_probability": max_values["thunderstorm_probability"] if max_values["thunderstorm_probability"] > 0 else 0.0,
            "precipitation": max_values["precipitation"],
            "wind_speed": max_values["wind_speed"],
            "temperature": max_values["temperature"],
            "cloud_cover": max_values["cloud_cover"]
        }
        
        # Add CAPE and shear if available
        cape_values = [point.cape for point in weather_data.points if point.cape is not None]
        shear_values = [point.shear for point in weather_data.points if point.shear is not None]
        
        if cape_values:
            metrics["cape"] = max(cape_values)
        if shear_values:
            metrics["shear"] = max(shear_values)
        
        # Compute risk score
        risk_score = compute_risk(metrics, config)
    
    return WeatherAnalysis(
        risks=risks,
        max_thunderstorm_probability=max_values["thunderstorm_probability"] if max_values["thunderstorm_probability"] > 0 else None,
        max_precipitation=max_values["precipitation"],
        max_wind_speed=max_values["wind_speed"],
        max_wind_gusts=max_values["wind_gusts"],
        max_cloud_cover=max_values["cloud_cover"],
        max_temperature=max_values["temperature"],
        max_cape_shear=max_values["cape_shear"] if max_values["cape_shear"] > 0 else None,
        summary=summary,
        risk=risk_score
    )


def _analyze_weather_point_english(point: WeatherPoint, thresholds: Dict[str, float]) -> List[WeatherRisk]:
    """
    Analyzes a single weather point for risks using English enum values.
    
    Args:
        point: WeatherPoint to analyze
        thresholds: Threshold values
        
    Returns:
        List[WeatherRisk]: List of detected risks with English enum values
    """
    risks = []
    
    # Get threshold values (support both German and English keys)
    rain_threshold = thresholds.get("rain_amount", thresholds.get("rain_probability", thresholds.get("precipitation", 2.0)))
    wind_threshold = thresholds.get("wind", thresholds.get("wind_speed", 40.0))
    cloud_threshold = thresholds.get("cloud_cover", thresholds.get("bewoelkung", 90.0))
    heat_threshold = thresholds.get("temperature", thresholds.get("hitze", 30.0))
    storm_threshold = thresholds.get("thunderstorm_probability", thresholds.get("gewitter", thresholds.get("gewitter_wahrscheinlichkeit", 20.0)))
    
    # Heavy Rain Risk
    if point.precipitation > rain_threshold:
        level = _determine_risk_level(point.precipitation, rain_threshold, [2, 5, 10])
        risks.append(WeatherRisk(
            risk_type=RiskType.HEAVY_RAIN,
            level=_convert_risk_level(level),
            value=point.precipitation,
            threshold=rain_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Heavy rain {point.precipitation:.1f}mm above threshold {rain_threshold}mm"
        ))
    
    # Thunderstorm Risk
    if point.thunderstorm_probability and point.thunderstorm_probability > storm_threshold:
        level = _determine_risk_level(point.thunderstorm_probability, storm_threshold, [20, 40, 60])
        risks.append(WeatherRisk(
            risk_type=RiskType.THUNDERSTORM,
            level=_convert_risk_level(level),
            value=point.thunderstorm_probability,
            threshold=storm_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Thunderstorm probability {point.thunderstorm_probability:.0f}% above threshold {storm_threshold}%"
        ))
    
    # High Wind Risk
    if point.wind_speed > wind_threshold:
        level = _determine_risk_level(point.wind_speed, wind_threshold, [40, 60, 80])
        risks.append(WeatherRisk(
            risk_type=RiskType.HIGH_WIND,
            level=_convert_risk_level(level),
            value=point.wind_speed,
            threshold=wind_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"High wind speed {point.wind_speed:.0f} km/h above threshold {wind_threshold} km/h"
        ))
    
    # Overcast Risk
    if point.cloud_cover > cloud_threshold:
        level = _determine_risk_level(point.cloud_cover, cloud_threshold, [90, 95, 98])
        risks.append(WeatherRisk(
            risk_type=RiskType.OVERCAST,
            level=_convert_risk_level(level),
            value=point.cloud_cover,
            threshold=cloud_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Overcast conditions {point.cloud_cover:.0f}% above threshold {cloud_threshold}%"
        ))
    
    # Heat Wave Risk
    if point.temperature > heat_threshold:
        level = _determine_risk_level(point.temperature, heat_threshold, [30, 35, 40])
        risks.append(WeatherRisk(
            risk_type=RiskType.HEAT_WAVE,
            level=_convert_risk_level(level),
            value=point.temperature,
            threshold=heat_threshold,
            time=point.time,
            start_time=point.time,
            end_time=point.time,
            description=f"Heat wave temperature {point.temperature:.1f}°C above threshold {heat_threshold}°C"
        ))
    
    return risks


def _generate_summary_english(risks: List[WeatherRisk], max_values: Dict[str, float], thresholds: Dict[str, float]) -> str:
    """
    Generates a compact summary of the analysis in English.
    
    Args:
        risks: List of detected risks
        max_values: Maximum values
        thresholds: Threshold values
        
    Returns:
        str: Summary in English
    """
    if not risks:
        return "No significant weather risks detected"
    
    # Group risks by type
    risk_groups = {}
    for risk in risks:
        if risk.risk_type not in risk_groups:
            risk_groups[risk.risk_type] = []
        risk_groups[risk.risk_type].append(risk)
    
    summary_parts = []
    
    # Highest risks first
    for risk_type in [RiskType.THUNDERSTORM, RiskType.HEAVY_RAIN, RiskType.HIGH_WIND, RiskType.HEAT_WAVE, RiskType.OVERCAST]:
        if risk_type in risk_groups:
            risks_of_type = risk_groups[risk_type]
            highest_risk = max(risks_of_type, key=lambda r: r.level.value)
            
            risk_name = {
                RiskType.THUNDERSTORM: "Thunderstorm",
                RiskType.HEAVY_RAIN: "Heavy rain",
                RiskType.HIGH_WIND: "High wind",
                RiskType.HEAT_WAVE: "Heat wave",
                RiskType.OVERCAST: "Overcast"
            }[risk_type]
            
            summary_parts.append(f"{risk_name}: {highest_risk.level.value.upper()} ({highest_risk.value:.1f})")
    
    # Add maximum values
    if max_values["precipitation"] > 0:
        summary_parts.append(f"Max. precipitation: {max_values['precipitation']:.1f}mm")
    if max_values["wind_speed"] > 0:
        summary_parts.append(f"Max. wind: {max_values['wind_speed']:.0f} km/h")
    if max_values["temperature"] > 0:
        summary_parts.append(f"Max. temperature: {max_values['temperature']:.1f}°C")
    
    return " | ".join(summary_parts)


def compute_risk(metrics: Dict[str, float], config: Dict) -> float:
    """
    Computes a weighted risk score based on meteorological indicators.
    
    Args:
        metrics: Dictionary containing current weather values
        config: Configuration dictionary with risk model settings
        
    Returns:
        float: Risk level between 0.0 and 1.0
    """
    if not metrics or not config:
        return 0.0
    
    risk_model_config = config.get("risk_model", {})
    if not risk_model_config:
        return 0.0
    
    total_risk = 0.0
    
    for parameter, settings in risk_model_config.items():
        if not isinstance(settings, dict):
            continue
            
        threshold = settings.get("threshold")
        weight = settings.get("weight", 0.0)
        
        if threshold is None or weight <= 0:
            continue
        
        # Get the current value for this parameter
        current_value = metrics.get(parameter)
        
        # Skip if value is None or not provided
        if current_value is None:
            continue
        
        # Check if threshold is exceeded based on parameter type
        threshold_exceeded = False
        
        if parameter == "lifted_index":
            # For lifted_index, more negative values indicate higher instability
            # So we check if current_value < threshold (more negative)
            threshold_exceeded = current_value < threshold
        else:
            # For other parameters, higher values indicate higher risk
            # So we check if current_value > threshold
            threshold_exceeded = current_value > threshold
        
        if threshold_exceeded:
            total_risk += weight
    
    # Cap the risk at 1.0
    return min(total_risk, 1.0)

