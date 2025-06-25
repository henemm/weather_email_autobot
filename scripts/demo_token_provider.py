#!/usr/bin/env python3
"""
Demo script for MeteoTokenProvider.

This script demonstrates how to use the centralized OAuth2 token provider
for Météo-France APIs.
"""

import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.auth.meteo_token_provider import MeteoTokenProvider


def demo_token_provider():
    """
    Demonstrate the MeteoTokenProvider functionality.
    
    Shows token acquisition, caching, and automatic renewal.
    """
    print("=== MeteoTokenProvider Demo ===\n")
    
    # Check if environment variable is set
    if not os.getenv('METEOFRANCE_BASIC_AUTH'):
        print("❌ METEOFRANCE_BASIC_AUTH environment variable is not set.")
        print("Please set it with your Base64-encoded client credentials.")
        print("Example: export METEOFRANCE_BASIC_AUTH='your_base64_credentials'")
        return
    
    try:
        # Create token provider
        print("🔧 Creating MeteoTokenProvider instance...")
        provider = MeteoTokenProvider()
        
        # Get first token
        print("\n🔑 Requesting first access token...")
        token1 = provider.get_token()
        print(f"✅ Token obtained: {token1[:20]}...")
        
        # Get second token (should be cached)
        print("\n🔄 Requesting second token (should be cached)...")
        token2 = provider.get_token()
        print(f"✅ Cached token returned: {token2[:20]}...")
        
        # Verify tokens are the same
        if token1 == token2:
            print("✅ Token caching is working correctly!")
        else:
            print("❌ Token caching failed - tokens are different!")
        
        # Clear cache and get new token
        print("\n🗑️  Clearing token cache...")
        provider.clear_cache()
        
        print("🔑 Requesting new token after cache clear...")
        token3 = provider.get_token()
        print(f"✅ New token obtained: {token3[:20]}...")
        
        # Verify new token is different
        if token3 != token1:
            print("✅ Cache clearing is working correctly!")
        else:
            print("❌ Cache clearing failed - same token returned!")
        
        print("\n🎉 Demo completed successfully!")
        print("\nUsage in your code:")
        print("from src.auth.meteo_token_provider import MeteoTokenProvider")
        print("provider = MeteoTokenProvider()")
        print("token = provider.get_token()")
        print("headers = {'Authorization': f'Bearer {token}'}")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    demo_token_provider() 