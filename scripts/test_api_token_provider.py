#!/usr/bin/env python3
"""
Test script for the new API token provider.
"""

import sys
sys.path.append('src')

from auth.api_token_provider import APITokenProvider, get_api_token

def test_token_provider():
    """Test the API token provider functionality."""
    
    print("🔍 Testing API Token Provider...\n")
    
    # Test singleton pattern
    provider1 = APITokenProvider()
    provider2 = APITokenProvider()
    print(f"✅ Singleton pattern: {provider1 is provider2}")
    
    # Test available services
    print(f"\n📋 Available services:")
    services = provider1.get_available_services()
    for service, status in services.items():
        print(f"  - {service}: {status}")
    
    # Test token retrieval for each service
    print(f"\n🔑 Testing token retrieval:")
    for service in services.keys():
        try:
            token = get_api_token(service)
            print(f"  ✅ {service}: Token retrieved successfully")
            print(f"     Token preview: {token[:20]}...")
        except Exception as e:
            print(f"  ❌ {service}: {e}")
    
    # Test invalid service
    print(f"\n🚫 Testing invalid service:")
    try:
        token = get_api_token("invalid_service")
        print(f"  ❌ Should have failed but got token")
    except RuntimeError as e:
        print(f"  ✅ Correctly rejected invalid service: {e}")
    
    print(f"\n✅ API Token Provider test completed!")

if __name__ == "__main__":
    test_token_provider() 