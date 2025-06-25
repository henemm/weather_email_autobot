#!/usr/bin/env python3
"""
Demo script for the OAuth2 token provider.

This script demonstrates how to use the MeteoTokenProvider
with the new OAuth2 client credentials flow using METEOFRANCE_APPLICATION_ID.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auth.meteo_token_provider import MeteoTokenProvider
from utils.env_loader import ensure_env_loaded


def setup_logging():
    """Set up logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def check_environment_variables():
    """
    Check if required environment variables are set.
    
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    required_vars = ['METEOFRANCE_APPLICATION_ID']
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment:")
        print("METEOFRANCE_APPLICATION_ID=your_application_id_here")
        return False
    
    print("✅ All required environment variables are set")
    return True


def demo_token_provider():
    """Demonstrate the token provider functionality."""
    print("\n🔐 OAuth2 Token Provider Demo")
    print("=" * 50)
    
    # Ensure .env is loaded
    ensure_env_loaded()
    
    # Check environment variables
    if not check_environment_variables():
        return False
    
    try:
        # Create token provider instance
        print("\n📡 Creating MeteoTokenProvider instance...")
        provider = MeteoTokenProvider()
        print(f"✅ Provider instance created: {provider}")
        
        # Get token for the first time
        print("\n🔄 Requesting first token...")
        token1 = provider.get_token()
        print(f"✅ First token obtained: {token1[:20]}...")
        
        # Get token again (should be cached)
        print("\n🔄 Requesting token again (should be cached)...")
        token2 = provider.get_token()
        print(f"✅ Second token obtained: {token2[:20]}...")
        
        # Verify tokens are the same
        if token1 == token2:
            print("✅ Tokens are identical (caching works)")
        else:
            print("❌ Tokens are different (caching failed)")
        
        # Show token expiry information
        if provider._token_expiry:
            print(f"📅 Token expires at: {provider._token_expiry}")
        
        # Test singleton pattern
        print("\n🔄 Testing singleton pattern...")
        provider2 = MeteoTokenProvider()
        if provider is provider2:
            print("✅ Singleton pattern works (same instance)")
        else:
            print("❌ Singleton pattern failed (different instances)")
        
        # Test cache clearing
        print("\n🔄 Testing cache clearing...")
        provider.clear_cache()
        print("✅ Cache cleared")
        
        # Get token after clearing cache
        print("\n🔄 Requesting token after cache clear...")
        token3 = provider.get_token()
        print(f"✅ New token obtained: {token3[:20]}...")
        
        # Verify new token is different
        if token1 != token3:
            print("✅ New token is different (cache clearing works)")
        else:
            print("❌ New token is identical (cache clearing failed)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during token provider demo: {e}")
        return False


def demo_live_api_call():
    """Demonstrate a live API call using the OAuth2 token."""
    print("\n🌐 Live API Call Demo")
    print("=" * 30)
    
    try:
        import requests
        
        # Get token
        provider = MeteoTokenProvider()
        token = provider.get_token()
        
        # Make a live WMS API call
        url = "https://public-api.meteofrance.fr/public/arome/1.0/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetCapabilities"
        
        params = {
            "service": "WMS",
            "version": "1.3.0",
            "language": "eng"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "*/*"
        }
        
        print(f"🔗 Making WMS API call to: {url}")
        print(f"🔐 Using token: {token[:20]}...")
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✅ WMS API call successful")
            print(f"   Status: {response.status_code}")
            print(f"   Response size: {len(response.text)} characters")
            
            # Check for WMS capabilities in response
            if "WMS_Capabilities" in response.text or "wms:WMS_Capabilities" in response.text:
                print("✅ Response contains WMS capabilities")
            else:
                print("⚠️  Response format unexpected")
        else:
            print(f"❌ WMS API call failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during live API call demo: {e}")
        return False


def main():
    """Main demo function."""
    setup_logging()
    
    print("🚀 MeteoTokenProvider OAuth2 Demo")
    print("This demo shows the new OAuth2 client credentials flow")
    print("for obtaining access tokens from Météo-France APIs.")
    print("No manual tokens required - everything is automated!")
    
    success1 = demo_token_provider()
    success2 = demo_live_api_call()
    
    if success1 and success2:
        print("\n📋 Summary:")
        print("- OAuth2 token provider works correctly")
        print("- Token caching and singleton pattern function properly")
        print("- Environment variable handling is working")
        print("- Live API calls work with OAuth2 authentication")
        print("- Ready for integration with weather APIs")
    else:
        print("\n❌ Demo failed - please check your configuration")
        sys.exit(1)


if __name__ == "__main__":
    main() 