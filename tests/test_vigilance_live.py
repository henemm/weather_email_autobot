"""
Integration test for live Vigilance API weather warnings.

This module tests the live connection to Météo-France Vigilance API
to fetch weather warnings for French postal codes.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import pytest
import requests
from datetime import datetime
from datetime import timezone
from typing import List, Dict, Any

from model.datatypes import WeatherAlert
from wetter.warning import fetch_vigilance_text_warnings

try:
    from tests.utils.env_loader import get_env_var
except ImportError:
    from utils.env_loader import get_env_var


def fetch_vigilance_bulletin() -> Dict[str, Any]:
    """
    Fetch the current Vigilance bulletin from Météo-France API using OAuth2.
    
    Returns:
        Dict containing the bulletin data
        
    Raises:
        RuntimeError: If API token is missing
        requests.RequestException: If API request fails
    """
    # Use the existing token provider system
    from auth.meteo_token_provider import MeteoTokenProvider
    
    token_provider = MeteoTokenProvider()
    access_token = token_provider.get_token()
    
    print(f"Access token obtained: {access_token[:20]}...")
    
    # Use the access token to fetch Vigilance bulletin
    bulletin_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    bulletin_url = "https://public-api.meteofrance.fr/public/DPVigilance/v1/textesvigilance/encours"
    
    print(f"Requesting bulletin from: {bulletin_url}")
    
    bulletin_response = requests.get(bulletin_url, headers=bulletin_headers, timeout=30)
    
    print(f"Bulletin response status: {bulletin_response.status_code}")
    print(f"Bulletin response headers: {dict(bulletin_response.headers)}")
    
    if bulletin_response.status_code != 200:
        print(f"Bulletin response text: {bulletin_response.text[:500]}")
        bulletin_response.raise_for_status()
    
    try:
        bulletin_json = bulletin_response.json()
        print(f"Bulletin response JSON keys: {list(bulletin_json.keys())}")
        return bulletin_json
    except Exception as e:
        print(f"Failed to parse bulletin response: {e}")
        print(f"Response text: {bulletin_response.text[:500]}")
        raise


def hex_to_color_name(hex_color: str) -> str:
    """
    Convert hex color codes to color names.
    
    Args:
        hex_color: Hex color code (e.g., '#f7a401')
        
    Returns:
        Color name (green, yellow, orange, red)
    """
    # Common hex color mappings for Vigilance levels
    color_mapping = {
        '#00ff00': 'green',    # Green
        '#ffff00': 'yellow',   # Yellow  
        '#f7a401': 'orange',   # Orange
        '#ff0000': 'red',      # Red
        '#ff6600': 'orange',   # Alternative orange
        '#ffcc00': 'yellow',   # Alternative yellow
    }
    
    # Normalize hex color (remove # if present, convert to lowercase)
    normalized_hex = hex_color.lower().replace('#', '')
    if not normalized_hex.startswith('#'):
        normalized_hex = '#' + normalized_hex
    
    return color_mapping.get(normalized_hex, 'green')  # Default to green if unknown


def parse_vigilance_alerts(bulletin_data: Dict[str, Any]) -> List[WeatherAlert]:
    """
    Parse Vigilance bulletin data into WeatherAlert objects.
    
    Args:
        bulletin_data: Raw bulletin data from API
        
    Returns:
        List of WeatherAlert objects
    """
    alerts = []
    
    # Check if we have the expected structure
    if 'product' not in bulletin_data:
        print("Warning: No 'product' key found in bulletin data")
        return alerts
    
    product = bulletin_data['product']
    
    # Check for text_bloc_items which contain the actual warnings
    if 'text_bloc_items' not in product:
        print("Warning: No 'text_bloc_items' found in product data")
        return alerts
    
    text_bloc_items = product['text_bloc_items']
    
    print(f"Processing {len(text_bloc_items)} text bloc items...")
    
    for item in text_bloc_items:
        if not isinstance(item, dict):
            continue
            
        # Each item represents a domain/region with bloc_items containing the actual warnings
        domain_id = item.get('domain_id', 'Unknown')
        domain_name = item.get('domain_name', 'Unknown')
        bloc_title = item.get('bloc_title', 'Unknown')
        bloc_items = item.get('bloc_items', [])
        
        print(f"Processing domain: {domain_name} ({domain_id}) with {len(bloc_items)} bloc items")
        
        # Process each bloc_item which contains the actual warning details
        for bloc_item in bloc_items:
            if not isinstance(bloc_item, dict):
                continue
                
            print(f"  Processing bloc_item with keys: {list(bloc_item.keys())}")
            
            # Extract basic information from bloc_item
            bloc_id = bloc_item.get('id', 'Unknown')
            type_name = bloc_item.get('type_name', bloc_title)
            type_group = bloc_item.get('type_group', 'Unknown')
            text_items = bloc_item.get('text_items', [])
            
            print(f"    Type: {type_name} ({type_group}) with {len(text_items)} text items")
            
            # Process each text_item which contains the actual warning details
            for text_item in text_items:
                if not isinstance(text_item, dict):
                    continue
                    
                print(f"      Processing text_item with keys: {list(text_item.keys())}")
                
                # Extract basic information from text_item
                type_code = text_item.get('type_code', 'Unknown')
                hazard_code = text_item.get('hazard_code', 'Unknown')
                hazard_name = text_item.get('hazard_name', type_name)
                term_items = text_item.get('term_items', [])
                
                print(f"        Hazard: {hazard_name} ({hazard_code}) with {len(term_items)} term items")
                
                # Process each term_item which contains the actual warning details
                for term_item in term_items:
                    if not isinstance(term_item, dict):
                        continue
                        
                    print(f"          Processing term_item with keys: {list(term_item.keys())}")
                    
                    # Extract warning information from the term_item
                    try:
                        # Extract the actual warning data from term_item
                        term_names = term_item.get('term_names', [])
                        start_time_str = term_item.get('start_time')
                        end_time_str = term_item.get('end_time')
                        risk_name = term_item.get('risk_name', hazard_name)
                        risk_code = term_item.get('risk_code', hazard_code)
                        risk_color = term_item.get('risk_color', 'green')
                        risk_level = term_item.get('risk_level', 1)
                        subdivision_text = term_item.get('subdivision_text', '')
                        
                        print(f"            Risk: {risk_name} ({risk_code}) - Color: {risk_color} - Level: {risk_level}")
                        print(f"            Time: {start_time_str} to {end_time_str}")
                        
                        # Parse dates
                        valid_from = None
                        valid_to = None
                        
                        if start_time_str:
                            try:
                                valid_from = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                            except (ValueError, AttributeError):
                                pass
                                
                        if end_time_str:
                            try:
                                valid_to = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                            except (ValueError, AttributeError):
                                pass
                        
                        # Only create alert if we have valid dates and a meaningful risk level
                        if valid_from and valid_to and risk_level > 1:
                            # Use the first term name as phenomenon, or risk_name as fallback
                            phenomenon = term_names[0] if term_names else risk_name
                            
                            # Convert hex color to color name
                            color_name = hex_to_color_name(risk_color)
                            
                            alert = WeatherAlert(
                                phenomenon=phenomenon,
                                level=color_name,
                                valid_from=valid_from,
                                valid_to=valid_to,
                                region=domain_id
                            )
                            alerts.append(alert)
                            print(f"            ✅ Created alert: {phenomenon} - {color_name} - {domain_id}")
                        else:
                            print(f"            ⏭️  Skipped: level={risk_level}, valid_from={valid_from}, valid_to={valid_to}")
                            
                    except Exception as e:
                        print(f"          Error processing term_item: {e}")
                        continue
    
    print(f"Created {len(alerts)} weather alerts")
    return alerts


def test_parse_vigilance_alerts_with_mock_data():
    """
    Test parsing logic with mock Vigilance API response data.
    """
    # Mock data simulating the actual Vigilance API response structure
    mock_bulletin_data = {
        "product": {
            "text_bloc_items": [
                {
                    "domain_id": "69",
                    "domain_name": "Rhône",
                    "bloc_title": "Situation météorologique",
                    "bloc_items": [
                        {
                            "id": "situation_69",
                            "type_name": "Situation météorologique",
                            "type_group": "SITUATION",
                            "text_items": [
                                {
                                    "type_code": "SITUATION",
                                    "hazard_code": "6",
                                    "hazard_name": "Canicule",
                                    "term_items": [
                                        {
                                            "term_names": ["J"],
                                            "start_time": "2025-01-15T12:00:00Z",
                                            "end_time": "2025-01-15T18:00:00Z",
                                            "risk_name": "Orange",
                                            "risk_code": "3",
                                            "risk_color": "#f7a401",
                                            "risk_level": 2,
                                            "subdivision_text": "Rhône"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "domain_id": "75",
                    "domain_name": "Paris",
                    "bloc_title": "Situation météorologique",
                    "bloc_items": [
                        {
                            "id": "situation_75",
                            "type_name": "Situation météorologique",
                            "type_group": "SITUATION",
                            "text_items": [
                                {
                                    "type_code": "SITUATION",
                                    "hazard_code": "1",
                                    "hazard_name": "Vent",
                                    "term_items": [
                                        {
                                            "term_names": ["J"],
                                            "start_time": "2025-01-15T10:00:00Z",
                                            "end_time": "2025-01-15T20:00:00Z",
                                            "risk_name": "Yellow",
                                            "risk_code": "2",
                                            "risk_color": "#ffff00",
                                            "risk_level": 2,
                                            "subdivision_text": "Paris"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

    # Parse alerts
    alerts = parse_vigilance_alerts(mock_bulletin_data)

    # Validate results
    assert len(alerts) == 2, f"Expected 2 alerts, got {len(alerts)}"

    # Check first alert (Orange level)
    orange_alert = alerts[0]
    assert orange_alert.phenomenon == "J"
    assert orange_alert.level == "orange"
    assert orange_alert.region == "69"
    assert orange_alert.valid_from == datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc)
    assert orange_alert.valid_to == datetime(2025, 1, 15, 18, 0, tzinfo=timezone.utc)

    # Check second alert (Yellow level)
    yellow_alert = alerts[1]
    assert yellow_alert.phenomenon == "J"
    assert yellow_alert.level == "yellow"
    assert yellow_alert.region == "75"
    assert yellow_alert.valid_from == datetime(2025, 1, 15, 10, 0, tzinfo=timezone.utc)
    assert yellow_alert.valid_to == datetime(2025, 1, 15, 20, 0, tzinfo=timezone.utc)


def test_parse_vigilance_alerts_empty_data():
    """
    Test parsing logic with empty data.
    """
    empty_data = {}
    alerts = parse_vigilance_alerts(empty_data)
    assert len(alerts) == 0


def test_parse_vigilance_alerts_no_warnings():
    """
    Test parsing logic when no active warnings exist.
    """
    no_warnings_data = {
        "product": {
            "text_bloc_items": []
        }
    }
    alerts = parse_vigilance_alerts(no_warnings_data)
    assert len(alerts) == 0


@pytest.mark.integration
@pytest.mark.skipif(
    not get_env_var("METEOFRANCE_BASIC_AUTH"),
    reason="METEOFRANCE_BASIC_AUTH environment variable not set"
)
def test_vigilance_live_fetch():
    """
    Integration test for live Vigilance API weather warnings.
    
    Tests the complete flow from API call to WeatherAlert object creation.
    """
    # Fetch bulletin data
    print("Fetching Vigilance bulletin...")
    bulletin_data = fetch_vigilance_bulletin()
    
    print(f"Bulletin data keys: {list(bulletin_data.keys())}")
    
    # Parse alerts
    alerts = parse_vigilance_alerts(bulletin_data)
    
    print(f"Found {len(alerts)} active weather alerts")
    
    # Basic validation
    assert isinstance(alerts, list), "Alerts should be a list"
    
    # If there are alerts, validate their structure
    if alerts:
        alert = alerts[0]
        
        # Check required fields
        assert hasattr(alert, 'phenomenon'), "Alert should have phenomenon field"
        assert hasattr(alert, 'level'), "Alert should have level field"
        assert hasattr(alert, 'valid_from'), "Alert should have valid_from field"
        assert hasattr(alert, 'valid_to'), "Alert should have valid_to field"
        assert hasattr(alert, 'region'), "Alert should have region field"
        
        # Validate data types
        assert isinstance(alert.phenomenon, str), "Phenomenon should be string"
        assert isinstance(alert.level, str), "Level should be string"
        assert isinstance(alert.valid_from, datetime), "Valid_from should be datetime"
        assert isinstance(alert.valid_to, datetime), "Valid_to should be datetime"
        assert isinstance(alert.region, str), "Region should be string"
        
        # Validate level values
        valid_levels = ["green", "yellow", "orange", "red"]
        assert alert.level in valid_levels, f"Level should be one of {valid_levels}"
        
        # Validate date logic
        assert alert.valid_from < alert.valid_to, "Valid_from should be before valid_to"
        
        print(f"Sample alert: {alert.phenomenon} - {alert.level} - {alert.region}")
        print(f"Valid from: {alert.valid_from}")
        print(f"Valid to: {alert.valid_to}")
    
    print("✅ Vigilance API integration test completed successfully")


@pytest.mark.integration
@pytest.mark.skipif(
    not get_env_var("METEOFRANCE_BASIC_AUTH"),
    reason="METEOFRANCE_BASIC_AUTH environment variable not set"
)
def test_vigilance_api_connectivity():
    """
    Test basic API connectivity and response structure.
    """
    print("Testing Vigilance API connectivity...")
    
    # Test API endpoint
    bulletin_data = fetch_vigilance_bulletin()
    
    # Check response structure
    assert isinstance(bulletin_data, dict), "Response should be a dictionary"
    
    # Check for expected top-level keys
    expected_keys = ["product", "meta"]
    for key in expected_keys:
        if key in bulletin_data:
            print(f"✅ Found expected key: {key}")
    
    print(f"✅ API connectivity test passed. Response keys: {list(bulletin_data.keys())}")


def test_fetch_vigilance_text_warnings_success():
    """
    Test that fetching vigilance text warnings returns a non-empty result and expected fields.
    """
    result = fetch_vigilance_text_warnings()
    assert isinstance(result, dict)
    assert result.get("status") == "success"
    assert "data" in result
    assert isinstance(result["data"], dict)
    # The top-level key should be 'product'
    assert "product" in result["data"]
    # The product should contain text_bloc_items or similar
    product = result["data"]["product"]
    assert isinstance(product, dict)
    assert "text_bloc_items" in product
    assert isinstance(product["text_bloc_items"], list)
    # There should be at least one text block
    assert len(product["text_bloc_items"]) > 0


if __name__ == "__main__":
    # Run the live test if executed directly
    test_vigilance_live_fetch() 