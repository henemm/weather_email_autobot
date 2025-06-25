#!/usr/bin/env python3
"""
Demo script for the OAuth2 token provider.

This script demonstrates how to use the MeteoTokenProvider
with the new OAuth2 client credentials flow.
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
    """Check if required environment variables are set."""
    required_vars = ['METEOFRANCE_CLIENT_ID', 'METEOFRANCE_CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("Example .env file:")
        print("METEOFRANCE_CLIENT_ID=your_client_id_here")
        print("METEOFRANCE_CLIENT_SECRET=your_client_secret_here")
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
        return
    
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
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("\nThis could be due to:")
        print("- Invalid client credentials")
        print("- Network connectivity issues")
        print("- Météo-France API being unavailable")
        return False
    
    return True


def main():
    """Main demo function."""
    setup_logging()
    
    print("🚀 MeteoTokenProvider OAuth2 Demo")
    print("This demo shows the new OAuth2 client credentials flow")
    print("for obtaining access tokens from Météo-France APIs.")
    
    success = demo_token_provider()
    
    if success:
        print("\n📋 Summary:")
        print("- OAuth2 token provider works correctly")
        print("- Token caching and singleton pattern function properly")
        print("- Environment variable handling is working")
        print("- Ready for integration with weather APIs")
    else:
        print("\n❌ Demo failed - please check your configuration")
        sys.exit(1)


if __name__ == "__main__":
    main() 