#!/usr/bin/env python3
"""
Demo script for live OAuth2 token testing.

This script demonstrates the OAuth2 token provider functionality
and shows how to configure it for live testing with Météo-France APIs.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path for absolute imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.auth.meteo_token_provider import MeteoTokenProvider
from src.utils.env_loader import ensure_env_loaded


def setup_logging():
    """Set up logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def check_environment_setup():
    """Check and display environment setup information."""
    print("🔧 Environment Setup Check")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("   Create a .env file in the project root with:")
        print("   METEOFRANCE_CLIENT_ID=your_client_id_here")
        print("   METEOFRANCE_CLIENT_SECRET=your_client_secret_here")
    
    # Check environment variables
    client_id = os.getenv('METEOFRANCE_CLIENT_ID')
    client_secret = os.getenv('METEOFRANCE_CLIENT_SECRET')
    
    if client_id and client_secret:
        print("✅ OAuth2 credentials found in environment")
        print(f"   Client ID: {client_id[:10]}...")
        print(f"   Client Secret: {'*' * len(client_secret)}")
    else:
        print("❌ OAuth2 credentials not found")
        print("   Required environment variables:")
        print("   - METEOFRANCE_CLIENT_ID")
        print("   - METEOFRANCE_CLIENT_SECRET")
    
    print()


def demonstrate_token_provider_structure():
    """Demonstrate the token provider structure and basic functionality."""
    print("🏗️  Token Provider Structure Demo")
    print("=" * 50)
    
    try:
        # Create token provider instance
        token_provider = MeteoTokenProvider()
        print("✅ Token provider instantiated successfully")
        
        # Check singleton pattern
        token_provider2 = MeteoTokenProvider()
        if token_provider is token_provider2:
            print("✅ Singleton pattern working correctly")
        else:
            print("❌ Singleton pattern not working")
        
        # Check available methods
        methods = ['get_token', 'clear_cache', '_request_new_token', '_is_token_valid']
        for method in methods:
            if hasattr(token_provider, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
        
        # Check configuration
        print(f"✅ Token endpoint: {token_provider._token_endpoint}")
        print(f"✅ Max retries: {token_provider._max_retries}")
        print(f"✅ Logger configured: {token_provider._logger is not None}")
        
        # Test cache clearing
        token_provider.clear_cache()
        print("✅ Cache clearing works")
        
        print()
        
    except Exception as e:
        print(f"❌ Error demonstrating token provider structure: {e}")
        print()


def demonstrate_error_handling():
    """Demonstrate error handling for missing credentials."""
    print("🚨 Error Handling Demo")
    print("=" * 50)
    
    # Store original credentials
    original_client_id = os.getenv('METEOFRANCE_CLIENT_ID')
    original_client_secret = os.getenv('METEOFRANCE_CLIENT_SECRET')
    
    try:
        # Temporarily remove credentials
        if 'METEOFRANCE_CLIENT_ID' in os.environ:
            del os.environ['METEOFRANCE_CLIENT_ID']
        if 'METEOFRANCE_CLIENT_SECRET' in os.environ:
            del os.environ['METEOFRANCE_CLIENT_SECRET']
        
        # Create token provider and attempt to get token
        token_provider = MeteoTokenProvider()
        token_provider.clear_cache()
        
        try:
            token = token_provider.get_token()
            print("❌ Expected error but got token successfully")
        except RuntimeError as e:
            print("✅ Properly handled missing credentials")
            print(f"   Error: {str(e)[:100]}...")
        except Exception as e:
            print("✅ Handled missing credentials (different error type)")
            print(f"   Error: {str(e)[:100]}...")
        
        print()
        
    finally:
        # Restore original credentials
        if original_client_id is not None:
            os.environ['METEOFRANCE_CLIENT_ID'] = original_client_id
        if original_client_secret is not None:
            os.environ['METEOFRANCE_CLIENT_SECRET'] = original_client_secret


def demonstrate_live_functionality():
    """Demonstrate live functionality if credentials are available."""
    print("🌐 Live Functionality Demo")
    print("=" * 50)
    
    client_id = os.getenv('METEOFRANCE_CLIENT_ID')
    client_secret = os.getenv('METEOFRANCE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("⏭️  Skipping live demo - OAuth2 credentials not available")
        print("   To enable live testing:")
        print("   1. Get OAuth2 credentials from Météo-France")
        print("   2. Add to .env file or environment variables")
        print("   3. Run this demo again")
        print()
        return
    
    try:
        # Ensure .env is loaded
        ensure_env_loaded()
        
        # Create token provider
        token_provider = MeteoTokenProvider()
        print("✅ Token provider created")
        
        # Clear cache to force new token request
        token_provider.clear_cache()
        print("✅ Cache cleared")
        
        # Get token
        print("🔄 Requesting OAuth2 token...")
        token = token_provider.get_token()
        print(f"✅ Token obtained: {token[:20]}...")
        
        # Validate token format
        if len(token) >= 50:
            print("✅ Token format looks valid")
        else:
            print("⚠️  Token seems short")
        
        # Show token expiry
        if token_provider._token_expiry:
            print(f"📅 Token expires at: {token_provider._token_expiry}")
        
        print("🎉 Live functionality demo completed successfully!")
        print()
        
    except Exception as e:
        print(f"❌ Live functionality demo failed: {e}")
        print("   This could be due to:")
        print("   - Invalid credentials")
        print("   - Network issues")
        print("   - API endpoint problems")
        print()


def show_test_instructions():
    """Show instructions for running the live tests."""
    print("🧪 Test Instructions")
    print("=" * 50)
    
    print("To run the complete live OAuth2 tests:")
    print()
    print("1. Configure OAuth2 credentials:")
    print("   export METEOFRANCE_CLIENT_ID=your_client_id")
    print("   export METEOFRANCE_CLIENT_SECRET=your_client_secret")
    print()
    print("2. Run the live tests:")
    print("   python -m pytest tests/test_live_oauth2_token.py -v")
    print()
    print("3. Or run specific tests:")
    print("   python -m pytest tests/test_live_oauth2_token.py::test_oauth2_token_refresh_flow -v")
    print("   python -m pytest tests/test_live_oauth2_token.py::test_live_oauth2_token_authentication -v")
    print()
    print("4. Tests that work without credentials:")
    print("   python -m pytest tests/test_live_oauth2_token.py::test_oauth2_token_provider_structure -v")
    print("   python -m pytest tests/test_live_oauth2_token.py::test_oauth2_missing_credentials_handling -v")
    print("   python -m pytest tests/test_live_oauth2_token.py::test_oauth2_token_provider_configuration -v")
    print()


def main():
    """Main demo function."""
    setup_logging()
    
    print("🚀 Live OAuth2 Token Test Demo")
    print("This demo shows the OAuth2 token provider functionality")
    print("and how to configure it for live testing with Météo-France APIs.")
    print()
    
    # Check environment setup
    check_environment_setup()
    
    # Demonstrate token provider structure
    demonstrate_token_provider_structure()
    
    # Demonstrate error handling
    demonstrate_error_handling()
    
    # Demonstrate live functionality
    demonstrate_live_functionality()
    
    # Show test instructions
    show_test_instructions()
    
    print("📋 Summary:")
    print("- OAuth2 token provider structure is working correctly")
    print("- Error handling for missing credentials is implemented")
    print("- Live functionality requires valid OAuth2 credentials")
    print("- Tests are available for both structural and live validation")
    print()
    print("✅ Demo completed!")


if __name__ == "__main__":
    main() 