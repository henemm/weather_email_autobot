# Alternative Risk Analysis Module

This module provides an alternative approach to weather risk analysis that uses direct MeteoFrance API data without traditional thresholds (except for rain).

## Overview

The alternative risk analysis differs from the standard approach by:

- **No threshold-based risks** for heat and cold (pure informational values)
- **Direct MeteoFrance API data usage** (e.g., `T.value` instead of OpenMeteo-style fields)
- **French weather descriptions** for thunderstorm detection
- **Independent condition checking** for rain (probability AND amount must be met)

## Features

### 🔥 Heat Analysis
- Uses `T.value` directly from MeteoFrance API forecast entries
- No risk threshold - purely informational
- Aggregates maximum temperature across all forecast entries

### ❄️ Cold Analysis  
- Uses `T.value` directly from MeteoFrance API forecast entries
- No risk threshold - purely informational
- Aggregates minimum temperature across all forecast entries

### 🌧️ Rain Analysis
- Requires **both** conditions to be met:
  - Precipitation probability ≥ 50%
  - Precipitation amount > 2.0 mm/h
- Uses `rain.1h` for precipitation amount
- Estimates probability from `weather.desc` if `precipitation_probability` unavailable
- Independent threshold checking

### ⛈️ Thunderstorm Analysis
- Uses French weather descriptions from `weather.desc`
- Detects keywords: `orage`, `orages`, `thunderstorm`, `risque d'orage`, etc.
- Maps to WMO codes based on description intensity:
  - `Orages` → 95 (moderate thunderstorm)
  - `Orages lourds` → 99 (heavy thunderstorm)
  - `Orages avec grêle` → 96 (thunderstorm with hail)

### 🌬️ Wind Analysis
- Checks wind gusts > 30 km/h using `wind.gust`
- Uses `wind.speed` for base wind speed
- Simple threshold-based detection

## MeteoFrance API Data Structure

The module expects MeteoFrance API data in this format:

```python
{
    'forecast': [
        {
            'T': {'value': 25.5},                    # Temperature
            'rain': {'1h': 1.5},                     # Precipitation amount
            'precipitation_probability': 30,          # Optional
            'weather': {'desc': 'Ciel clair'},       # Weather description
            'wind': {'speed': 15, 'gust': 20}        # Wind data
        },
        # ... more forecast entries
    ]
}
```

## Usage

```python
from src.risiko.alternative_risk_analysis import AlternativeRiskAnalyzer

# Create analyzer
analyzer = AlternativeRiskAnalyzer()

# Analyze MeteoFrance weather data
weather_data = {
    'forecast': [
        {
            'T': {'value': 32.5},
            'rain': {'1h': 2.5},
            'precipitation_probability': 60,
            'weather': {'desc': 'Orages'},
            'wind': {'speed': 35, 'gust': 45}
        }
    ]
}

result = analyzer.analyze_all_risks(weather_data)
report_text = analyzer.generate_report_text(result)
```

## Output Format

The module generates a plaintext report that can be appended to email reports:

```
---

## 🔍 Alternative Risk Analysis

🔥 **Heat**: Maximum temperature: 32.5°C
❄️ **Cold**: Minimum temperature: 25.5°C
🌧️ **Rain**: Rain risk detected: 70.0% probability, 3.0mm/h
⛈️ **Thunderstorm**: Thunderstorm detected (WMO codes: 95, 99)
🌬️ **Wind**: Wind gusts detected: 45.0 km/h max
```

## Configuration

Thresholds are defined as class constants:

- `RAIN_PROBABILITY_THRESHOLD = 50.0` (%)
- `RAIN_AMOUNT_THRESHOLD = 2.0` (mm/h)
- `WIND_GUST_THRESHOLD = 30.0` (km/h)

## Error Handling

- Missing data fields raise `ValueError` with descriptive messages
- No fallback to standard logic (as per requirements)
- Comprehensive logging for debugging
- Graceful handling of missing precipitation probability (estimated from weather description)

## Testing

Run the test suite:

```bash
python3 -m pytest tests/test_alternative_risk_analysis.py -v
```

## Demo

Run the demo script:

```bash
python3 scripts/demo_alternative_risk_analysis.py
```

## Integration Notes

This module is designed to work with the existing MeteoFrance API integration and can be easily integrated into the email generation pipeline. It uses the same data structure as the existing `weather_data_processor.py` module. 