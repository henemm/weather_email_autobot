import math
from typing import Optional, Dict, Any


def generate_warntext(risk: float, config: Dict[str, Any]) -> Optional[str]:
    """
    Generate warning text based on risk value and configuration thresholds.
    
    Args:
        risk: Risk value between 0.0 and 1.0
        config: Configuration dictionary containing warn_thresholds
        
    Returns:
        Optional[str]: Warning text if risk exceeds thresholds, None otherwise
        
    Raises:
        ValueError: If risk is invalid or configuration is incomplete
    """
    _validate_risk_value(risk)
    _validate_config(config)
    
    thresholds = config["warn_thresholds"]
    
    # Check if risk is below info threshold
    if risk < thresholds["info"]:
        return None
    
    # Determine warning level based on thresholds
    if risk >= thresholds["critical"]:
        return _generate_alarm_text(risk)
    elif risk >= thresholds["warning"]:
        return _generate_warning_text(risk)
    else:
        return _generate_info_text(risk)


def _validate_risk_value(risk: float) -> None:
    """
    Validate that risk value is within valid range.
    
    Args:
        risk: Risk value to validate
        
    Raises:
        ValueError: If risk is invalid
    """
    if not isinstance(risk, (int, float)):
        raise ValueError("Risk must be a numeric value")
    
    if math.isnan(risk):
        raise ValueError("Risk cannot be NaN")
    
    if math.isinf(risk):
        raise ValueError("Risk cannot be infinity")
    
    if risk < 0.0:
        raise ValueError("Risk cannot be negative")
    
    if risk > 1.0:
        raise ValueError("Risk cannot exceed 1.0")


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Validate that configuration contains required warn_thresholds.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If configuration is invalid or incomplete
    """
    if not config:
        raise ValueError("Configuration cannot be empty")
    
    if "warn_thresholds" not in config:
        raise ValueError("Configuration must contain 'warn_thresholds'")
    
    thresholds = config["warn_thresholds"]
    required_keys = ["info", "warning", "critical"]
    
    for key in required_keys:
        if key not in thresholds:
            raise ValueError(f"Configuration missing required threshold: {key}")
        
        if not isinstance(thresholds[key], (int, float)):
            raise ValueError(f"Threshold '{key}' must be a numeric value")
        
        if thresholds[key] < 0.0 or thresholds[key] > 1.0:
            raise ValueError(f"Threshold '{key}' must be between 0.0 and 1.0")
    
    # Validate threshold order
    if not (thresholds["info"] <= thresholds["warning"] <= thresholds["critical"]):
        raise ValueError("Thresholds must be in ascending order: info <= warning <= critical")


def _generate_info_text(risk: float) -> str:
    """
    Generate info-level warning text.
    
    Args:
        risk: Risk value
        
    Returns:
        str: Info warning text
    """
    risk_percentage = int(risk * 100)
    return f"WARNUNG: Leicht erhöhte Wettergefahr - Risiko: {risk_percentage}%"


def _generate_warning_text(risk: float) -> str:
    """
    Generate warning-level text.
    
    Args:
        risk: Risk value
        
    Returns:
        str: Warning text
    """
    risk_percentage = int(risk * 100)
    return f"WARNUNG: Das Wetter-Risiko liegt bei {risk_percentage}%"


def _generate_alarm_text(risk: float) -> str:
    """
    Generate critical alarm text.
    
    Args:
        risk: Risk value
        
    Returns:
        str: Alarm text
    """
    risk_percentage = int(risk * 100)
    return f"ALARM! Sehr hohes Wetterrisiko - {risk_percentage}%" 