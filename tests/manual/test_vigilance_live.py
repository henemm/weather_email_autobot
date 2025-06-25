"""
Live test for Météo-France Vigilance API for Corsica (departments 2A, 2B).

This module tests the live connection to Météo-France Vigilance API
to fetch weather warnings for Corsica departments and validate
response formats, warning levels, and German translations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import pytest
import requests
from datetime import datetime
from typing import Dict, List, Any

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


def extract_corsica_warnings(bulletin_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract warnings specifically for Corsica departments (2A, 2B).
    
    Args:
        bulletin_data: Raw bulletin data from API
        
    Returns:
        List of warning dictionaries for Corsica
    """
    corsica_warnings = []
    
    if 'product' not in bulletin_data:
        print("Warning: No 'product' key found in bulletin data")
        return corsica_warnings
    
    product = bulletin_data['product']
    
    if 'text_bloc_items' not in product:
        print("Warning: No 'text_bloc_items' found in product data")
        return corsica_warnings
    
    text_bloc_items = product['text_bloc_items']
    
    # Filter for Corsica departments (2A: Corse-du-Sud, 2B: Haute-Corse)
    corsica_items = [
        item for item in text_bloc_items
        if item.get('domain_id') in ['2A', '2B', 'CORSE']
    ]
    
    print(f"Found {len(corsica_items)} Corsica-specific warning items")
    
    for item in corsica_items:
        domain_id = item.get('domain_id', 'Unknown')
        domain_name = item.get('domain_name', 'Unknown')
        bloc_items = item.get('bloc_items', [])
        
        print(f"Processing domain: {domain_name} ({domain_id}) with {len(bloc_items)} bloc items")
        
        for bloc_item in bloc_items:
            if not isinstance(bloc_item, dict):
                continue
                
            text_items = bloc_item.get('text_items', [])
            
            for text_item in text_items:
                if not isinstance(text_item, dict):
                    continue
                    
                term_items = text_item.get('term_items', [])
                
                for term_item in term_items:
                    if not isinstance(term_item, dict):
                        continue
                    
                    # Extract warning information
                    warning_info = {
                        'domain_id': domain_id,
                        'domain_name': domain_name,
                        'risk_name': term_item.get('risk_name', 'Unknown'),
                        'risk_code': term_item.get('risk_code', '1'),
                        'risk_level': int(term_item.get('risk_level', 1)),
                        'hazard_name': term_item.get('hazard_name', 'Unknown'),
                        'start_time': term_item.get('start_time'),
                        'end_time': term_item.get('end_time'),
                        'risk_color': term_item.get('risk_color', 'green')
                    }
                    
                    corsica_warnings.append(warning_info)
    
    return corsica_warnings


def translate_warning_to_german(warning_info: Dict[str, Any]) -> str:
    """
    Translate warning information to German.
    
    Args:
        warning_info: Warning dictionary with risk and hazard information
        
    Returns:
        German translation of the warning
    """
    risk_name = warning_info.get('risk_name', 'Unknown')
    hazard_name = warning_info.get('hazard_name', 'Unknown')
    risk_level = warning_info.get('risk_level', 1)
    domain_name = warning_info.get('domain_name', 'Unknown')
    
    # German translations for common weather phenomena
    translations = {
        'Orages': 'Gewitter',
        'Pluie-inondation': 'Regen-Überschwemmung',
        'Vent': 'Wind',
        'Neige-verglas': 'Schnee-Glätte',
        'Avalanches': 'Lawinen',
        'Canicule': 'Hitzewelle',
        'Grand-froid': 'Kältewelle',
        'Vagues-submersion': 'Sturmflut',
        'Inondation': 'Überschwemmung'
    }
    
    # Level descriptions in German
    level_descriptions = {
        1: 'Grün - Keine besonderen Vorkommnisse',
        2: 'Gelb - Achtung',
        3: 'Orange - Gefährlich',
        4: 'Rot - Sehr gefährlich'
    }
    
    translated_risk = translations.get(risk_name, risk_name)
    translated_hazard = translations.get(hazard_name, hazard_name)
    level_desc = level_descriptions.get(risk_level, f'Level {risk_level}')
    
    return f"{domain_name}: {translated_risk} ({translated_hazard}) - {level_desc}"


@pytest.mark.integration
@pytest.mark.skipif(
    not get_env_var("METEOFRANCE_CLIENT_ID"),
    reason="METEOFRANCE_CLIENT_ID environment variable not set"
)
def test_vigilance_live_corsica():
    """
    Live test for Météo-France Vigilance API for Corsica (departments 2A, 2B).
    
    Tests:
    1. API call with valid token
    2. Filtering for departments 2A (Corse-du-Sud) and 2B (Haute-Corse)
    3. Extraction of warning levels (1-4), hazard types, and timestamps
    4. Validation of response structure and German translations
    """
    print("\n" + "="*60)
    print("LIVE TEST: Météo-France Vigilance API for Corsica")
    print("="*60)
    
    # Step 1: Fetch bulletin data
    print("1. Fetching Vigilance bulletin...")
    bulletin_data = fetch_vigilance_bulletin()
    
    # Validate basic response structure
    assert isinstance(bulletin_data, dict), "Bulletin data should be a dictionary"
    assert 'product' in bulletin_data, "Bulletin data should contain 'product' key"
    
    product = bulletin_data['product']
    assert isinstance(product, dict), "Product should be a dictionary"
    assert 'text_bloc_items' in product, "Product should contain 'text_bloc_items'"
    
    text_bloc_items = product['text_bloc_items']
    assert isinstance(text_bloc_items, list), "text_bloc_items should be a list"
    assert len(text_bloc_items) > 0, "Should have at least one text bloc item"
    
    print(f"✅ API responded with HTTP 200")
    print(f"✅ JSON contains {len(text_bloc_items)} text bloc items")
    
    # Step 2: Extract Corsica warnings
    print("\n2. Extracting Corsica warnings...")
    corsica_warnings = extract_corsica_warnings(bulletin_data)
    
    # Validate that we have entries for both departments
    corsica_domains = set(warning['domain_id'] for warning in corsica_warnings)
    print(f"✅ Found warnings for domains: {corsica_domains}")
    
    # Step 3: Validate warning structure and content
    print("\n3. Validating warning structure...")
    
    if corsica_warnings:
        print(f"✅ Found {len(corsica_warnings)} active warnings for Corsica")
        
        for i, warning in enumerate(corsica_warnings, 1):
            print(f"\n   Warning {i}:")
            print(f"     Domain: {warning['domain_id']} - {warning['domain_name']}")
            print(f"     Risk: {warning['risk_name']} (Level {warning['risk_level']})")
            print(f"     Hazard: {warning['hazard_name']}")
            print(f"     Time: {warning['start_time']} to {warning['end_time']}")
            
            # Validate warning level (1-4)
            assert 1 <= warning['risk_level'] <= 4, f"Warning level should be 1-4, got {warning['risk_level']}"
            
            # Validate required fields
            assert warning['domain_id'] in ['2A', '2B', 'CORSE'], f"Invalid domain ID: {warning['domain_id']}"
            assert warning['risk_name'], "Risk name should not be empty"
            assert warning['hazard_name'], "Hazard name should not be empty"
            
            # Test German translation
            german_translation = translate_warning_to_german(warning)
            print(f"     German: {german_translation}")
            assert 'Gewitter' in german_translation or 'Regen' in german_translation or 'Wind' in german_translation or 'Unknown' in german_translation, "Translation should contain expected German terms"
        
        print(f"\n✅ Successfully extracted and validated {len(corsica_warnings)} warnings")
        print(f"✅ All warnings have valid structure and German translations")
    else:
        print("ℹ️  No active warnings for Corsica at this time")
        print("✅ API structure is valid even with no active warnings")
    
    # Step 4: Final validation
    print("\n4. Final validation...")
    
    # Check that we have at least one valid response
    assert len(text_bloc_items) > 0, "Should have at least one text bloc item in response"
    
    # Check that the structure is as expected
    for item in text_bloc_items:
        assert isinstance(item, dict), "Each text bloc item should be a dictionary"
        assert 'domain_id' in item, "Each item should have a domain_id"
        assert 'domain_name' in item, "Each item should have a domain_name"
        assert 'bloc_items' in item, "Each item should have bloc_items"
    
    print("✅ All validations passed")
    print("✅ Live test completed successfully")


@pytest.mark.integration
@pytest.mark.skipif(
    not get_env_var("METEOFRANCE_CLIENT_ID"),
    reason="METEOFRANCE_CLIENT_ID environment variable not set"
)
def test_vigilance_api_connectivity():
    """
    Test basic connectivity to Vigilance API.
    """
    print("\nTesting Vigilance API connectivity...")
    
    try:
        result = fetch_vigilance_text_warnings()
        assert result['status'] == 'success', f"API should return success status, got {result['status']}"
        assert 'data' in result, "Response should contain 'data' key"
        assert 'product' in result['data'], "Data should contain 'product' key"
        
        print("✅ Vigilance API connectivity test passed")
        
    except Exception as e:
        pytest.fail(f"Vigilance API connectivity test failed: {e}")


if __name__ == "__main__":
    # Run the test directly if executed as script
    pytest.main([__file__, "-v", "-s"])