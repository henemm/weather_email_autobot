#!/usr/bin/env python3
"""
Script to check all Météo-France API tokens and test their validity.
"""

import requests
import os
import sys
from typing import Dict, Any, List

# Add src to path for imports
sys.path.append('src')
from utils.env_loader import get_env_var

def test_api_endpoint(url: str, token: str, service_name: str) -> Dict[str, Any]:
    """
    Test an API endpoint with a given token.
    
    Args:
        url: API endpoint URL
        token: Bearer token
        service_name: Name of the service for logging
        
    Returns:
        Dictionary with test results
    """
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print(f"Testing {service_name}...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print(f"  ✅ {service_name}: SUCCESS (HTTP {response.status_code})")
            return {
                'service': service_name,
                'status': 'success',
                'status_code': response.status_code,
                'content_length': len(response.text)
            }
        else:
            print(f"  ❌ {service_name}: FAILED (HTTP {response.status_code})")
            error_msg = response.text[:200] if response.text else "No error message"
            print(f"     Error: {error_msg}")
            return {
                'service': service_name,
                'status': 'failed',
                'status_code': response.status_code,
                'error': error_msg
            }
            
    except Exception as e:
        print(f"  ❌ {service_name}: ERROR - {e}")
        return {
            'service': service_name,
            'status': 'error',
            'error': str(e)
        }

def main():
    """Main function to test all API tokens."""
    
    # Define all API endpoints to test
    endpoints = [
        {
            'name': 'AROME Model (WMS)',
            'url': 'https://public-api.meteofrance.fr/public/arome/1.0/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetCapabilities?service=WMS&version=1.3.0&language=eng',
            'token_var': 'METEOFRANCE_WCS_TOKEN'
        },
        {
            'name': 'AROME Immediate Forecast (WCS)',
            'url': 'https://public-api.meteofrance.fr/public/aromepi/1.0/wcs/MF-NWP-HIGHRES-AROMEPI-001-FRANCE-WCS/GetCapabilities?service=WCS&version=2.0.1&language=eng',
            'token_var': 'METEOFRANCE_IFC_TOKEN'
        },
        {
            'name': 'AROME Aggregated Rainrate Forecast (WCS)',
            'url': 'https://public-api.meteofrance.fr/public/arome-agg/1.0/wcs/MF-NWP-HIGHRES-AROME-AGG-001-FRANCE-WCS?service=WCS&version=2.0.1&request=GetCapabilities',
            'token_var': 'METEOFRANCE_WCS_TOKEN'
        },
        {
            'name': 'AROME Model Merged Aggregated Immediate Forecast (PIAF)',
            'url': 'https://api.meteofrance.fr/pro/piaf/1.0/wcs/MF-NWP-HIGHRES-PIAF-001-FRANCE-WCS/GetCapabilities?service=WCS&version=2.0.1&language=eng',
            'token_var': 'METEOFRANCE_PIA_TOKEN'
        }
    ]
    
    print("🔍 Testing all Météo-France API tokens...\n")
    
    results = []
    
    for endpoint in endpoints:
        token = get_env_var(endpoint['token_var'])
        
        if not token:
            print(f"❌ {endpoint['name']}: No token found for {endpoint['token_var']}")
            results.append({
                'service': endpoint['name'],
                'status': 'no_token',
                'token_var': endpoint['token_var']
            })
            continue
        
        result = test_api_endpoint(endpoint['url'], token, endpoint['name'])
        result['token_var'] = endpoint['token_var']
        results.append(result)
    
    # Summary
    print(f"\n📊 Token Test Summary:")
    print(f"=" * 50)
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    errors = [r for r in results if r['status'] == 'error']
    no_tokens = [r for r in results if r['status'] == 'no_token']
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⚠️  Errors: {len(errors)}")
    print(f"🔑 No tokens: {len(no_tokens)}")
    
    if successful:
        print(f"\n✅ Working APIs:")
        for result in successful:
            print(f"  - {result['service']} (Token: {result['token_var']})")
    
    if failed:
        print(f"\n❌ Failed APIs (likely expired tokens):")
        for result in failed:
            print(f"  - {result['service']} (Token: {result['token_var']}) - HTTP {result['status_code']}")
    
    if no_tokens:
        print(f"\n🔑 Missing tokens:")
        for result in no_tokens:
            print(f"  - {result['service']} (Variable: {result['token_var']})")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if failed:
        print("  - Some tokens appear to be expired. Consider regenerating them.")
        print("  - Each API requires its own dedicated token.")
    
    if successful:
        print("  - Working APIs can be used for Conca weather data.")
        print("  - All APIs use the same bounding box: [-12, 37.5, 16, 55.4] (covers Conca)")
    
    return results

if __name__ == "__main__":
    main() 