#!/usr/bin/env python3
"""
Live weather data diagnosis script for Conca, Corsica.

This script fetches weather data from three different APIs:
- Open-Meteo (free, no token required)
- Météo-France WCS (requires OAuth2 token)
- Météo-France Vigilance (requires OAuth2 token)

Outputs structured results to JSON file for analysis and debugging.
"""

import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any

import requests

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.env_loader import get_env_var
from src.wetter.fetch_arome_wcs import fetch_arome_wcs_data
from src.wetter.warning import fetch_vigilance_text_warnings


def fetch_openmeteo_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch current weather data from Open-Meteo API.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
            "timezone": "auto"
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return {
            "status": "success",
            "data": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": "openmeteo_error", "message": str(e), "timestamp": datetime.now().isoformat()}


def get_available_wcs_layers() -> Dict[str, Any]:
    """Fetch available WCS layers using GetCapabilities."""
    try:
        from src.auth.meteo_token_provider import MeteoTokenProvider
        token_provider = MeteoTokenProvider()
        token = token_provider.get_token()
        
        base_url = "https://api.meteofrance.fr/pro/piaf/1.0/wcs/MF-NWP-HIGHRES-PIAF-001-FRANCE-WCS"
        url = f"{base_url}/GetCapabilities?service=WCS&version=2.0.1&language=eng"
        
        headers = {"Authorization": f"Bearer {token}", "accept": "*/*"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        import re
        patterns = [r'<wcs:CoverageId[^>]*>([^<]+)</wcs:CoverageId>', r'<CoverageId[^>]*>([^<]+)</CoverageId>']
        coverage_ids = []
        for pattern in patterns:
            coverage_ids.extend(re.findall(pattern, response.text, re.DOTALL))
        
        unique_layers = list(set(coverage_ids))
        rain_layers = [layer for layer in unique_layers if 'rain' in layer.lower() or 'precipitation' in layer.lower()]

        return {
            "status": "success",
            "total_layers": len(unique_layers),
            "rain_layers": rain_layers,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": "capabilities_error", "message": str(e)}


def fetch_wcs_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch WCS weather data from Météo-France.
    NOTE: This is currently failing with 404 from the API.
    """
    try:
        # This is a best-effort attempt. The API consistently returns 404 for GetCoverage.
        layer_name = "TEMPERATURE__GROUND_OR_WATER_SURFACE"
        grid_data = fetch_arome_wcs_data(lat, lon, layer_name)
        return {
            "status": "success",
            "layer": layer_name,
            "data": {
                "unit": grid_data.unit,
                "times": [t.isoformat() for t in grid_data.times],
                "values": grid_data.values
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": "wcs_error", "message": str(e), "timestamp": datetime.now().isoformat()}


def fetch_vigilance_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch vigilance warnings from Météo-France.
    """
    try:
        result = fetch_vigilance_text_warnings()
        if result["status"] != "success":
            return result
            
        data = result["data"]
        product = data.get("product", {})
        text_blocks = product.get("text_bloc_items", [])
        
        corsica_warnings = [b for b in text_blocks if b.get("domain_id") in ["2A", "2B", "CORSE"]]
        
        return {
            "status": "success",
            "warnings_count": len(text_blocks),
            "corsica_warnings_count": len(corsica_warnings),
            "corsica_warnings": corsica_warnings,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": "vigilance_error", "message": str(e), "timestamp": datetime.now().isoformat()}


def print_colored_status(source: str, status: str, message: str = ""):
    """Prints a colored status message."""
    symbol = "✅" if status == "success" else "❌"
    print(f"{symbol} {source}: {status.capitalize()}" + (f" - {message}" if message else ""))


def main():
    """Main function."""
    lat, lon = 41.7524, 9.2746
    print("🌤️  Live Weather Data Diagnosis for Conca, Corsica")
    print("=" * 50)
    print(f"Coordinates: {lat}, {lon} | Timestamp: {datetime.now().isoformat()}")
    print()

    results = {}
    
    # Open-Meteo
    results["openmeteo"] = fetch_openmeteo_data(lat, lon)
    print_colored_status("Open-Meteo", results["openmeteo"]["status"])

    # WCS
    print("📡 Fetching Météo-France WCS data...")
    results["wcs"] = fetch_wcs_data(lat, lon)
    print_colored_status("WCS", results["wcs"]["status"], results["wcs"].get("message"))

    # Vigilance
    results["vigilance"] = fetch_vigilance_data(lat, lon)
    vigilance_msg = ""
    if results["vigilance"]["status"] == "success":
        vigilance_msg = f"Total: {results['vigilance']['warnings_count']}, Corsica: {results['vigilance']['corsica_warnings_count']}"
    else:
        vigilance_msg = results["vigilance"].get("message")
    print_colored_status("Vigilance", results["vigilance"]["status"], vigilance_msg)

    # Save output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output/live_weather_conca_{timestamp}.json"
    os.makedirs("output", exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_filename}")
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    print(f"📊 Summary: {success_count}/{len(results)} APIs successful.")


if __name__ == "__main__":
    main() 