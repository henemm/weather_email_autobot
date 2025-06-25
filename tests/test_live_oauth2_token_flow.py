"""
Live test for OAuth2 token flow with Météo-France API.

This test validates the complete OAuth2 client credentials flow using
the new METEOFRANCE_APPLICATION_ID environment variable.
"""

import os
import sys
import pytest
import requests

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.meteo_token_provider import MeteoTokenProvider


def test_oauth2_token_flow_without_application_id():
    """
    Test that the OAuth2 flow is skipped when APPLICATION_ID is not available.
    
    This test validates the graceful handling when OAuth2 credentials are not configured.
    """
    # Store original environment variable
    original_application_id = os.getenv('METEOFRANCE_APPLICATION_ID')
    
    try:
        # Remove the environment variable
        if 'METEOFRANCE_APPLICATION_ID' in os.environ:
            del os.environ['METEOFRANCE_APPLICATION_ID']
        
        # Try to create token provider - should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            token_provider = MeteoTokenProvider()
            token_provider.get_token()
        
        error_message = str(exc_info.value)
        assert "METEOFRANCE_APPLICATION_ID" in error_message, (
            f"Error message should mention METEOFRANCE_APPLICATION_ID, got: {error_message}"
        )
        
        print("✅ OAuth2 flow correctly skipped when APPLICATION_ID is not available")
        
    finally:
        # Restore original environment variable
        if original_application_id:
            os.environ['METEOFRANCE_APPLICATION_ID'] = original_application_id


def test_oauth2_token_flow_with_application_id():
    """
    Test live OAuth2 token flow with valid APPLICATION_ID.
    
    This test performs a real HTTP request to validate that the OAuth2 flow
    works correctly with the Météo-France WMS API.
    """
    # Check if OAuth2 credentials are available
    if not os.getenv('METEOFRANCE_APPLICATION_ID'):
        pytest.skip("METEOFRANCE_APPLICATION_ID not available - skipping live OAuth2 flow test")
    
    try:
        # Get the OAuth2 token using the token provider
        token_provider = MeteoTokenProvider()
        token = token_provider.get_token()
        
        # Validate token format
        assert token.strip(), "OAuth2 token is empty or whitespace only"
        assert len(token) >= 50, f"OAuth2 token seems too short: {len(token)} characters"
        
        # Use the token for a live WMS API call
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
        
        print(f"🔐 Testing OAuth2 token flow with WMS API...")
        print(f"   Token: {token[:20]}...")
        print(f"   URL: {url}")
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        # Validate response
        assert response.status_code == 200, (
            f"WMS API call failed with status {response.status_code}: {response.text}"
        )
        
        # Check that response contains WMS capabilities
        response_text = response.text
        assert "WMS_Capabilities" in response_text or "wms:WMS_Capabilities" in response_text, (
            "Response should contain WMS capabilities XML"
        )
        
        print("✅ OAuth2 token flow works correctly with WMS API")
        print(f"   Response status: {response.status_code}")
        print(f"   Response size: {len(response_text)} characters")
        
    except Exception as e:
        pytest.fail(f"OAuth2 token flow test failed: {e}")


def test_oauth2_token_caching():
    """
    Test that OAuth2 tokens are properly cached and reused.
    
    This test validates the caching behavior of the token provider.
    """
    # Check if OAuth2 credentials are available
    if not os.getenv('METEOFRANCE_APPLICATION_ID'):
        pytest.skip("METEOFRANCE_APPLICATION_ID not available - skipping token caching test")
    
    try:
        # Clear any existing token cache
        token_provider = MeteoTokenProvider()
        token_provider.clear_cache()
        
        # Get first token
        token1 = token_provider.get_token()
        assert token1, "First token should not be empty"
        
        # Get second token (should be cached)
        token2 = token_provider.get_token()
        assert token2, "Second token should not be empty"
        
        # Tokens should be identical (cached)
        assert token1 == token2, "Cached tokens should be identical"
        
        print("✅ OAuth2 token caching works correctly")
        print(f"   Token: {token1[:20]}...")
        
    except Exception as e:
        pytest.fail(f"OAuth2 token caching test failed: {e}")


def test_oauth2_token_refresh():
    """
    Test that OAuth2 tokens are refreshed when expired.
    
    This test validates the token refresh mechanism.
    """
    # Check if OAuth2 credentials are available
    if not os.getenv('METEOFRANCE_APPLICATION_ID'):
        pytest.skip("METEOFRANCE_APPLICATION_ID not available - skipping token refresh test")
    
    try:
        # Clear any existing token cache
        token_provider = MeteoTokenProvider()
        token_provider.clear_cache()
        
        # Get initial token
        initial_token = token_provider.get_token()
        assert initial_token, "Initial token should not be empty"
        
        # Simulate token expiration by setting expiry to past
        from datetime import datetime, timedelta
        token_provider._token_expiry = datetime.now() - timedelta(minutes=1)
        
        # Get token again (should trigger refresh)
        refreshed_token = token_provider.get_token()
        assert refreshed_token, "Refreshed token should not be empty"
        
        # Tokens should be different (new token requested)
        assert initial_token != refreshed_token, "Refreshed token should be different from initial token"
        
        print("✅ OAuth2 token refresh works correctly")
        print(f"   Initial token: {initial_token[:20]}...")
        print(f"   Refreshed token: {refreshed_token[:20]}...")
        
    except Exception as e:
        pytest.fail(f"OAuth2 token refresh test failed: {e}")


if __name__ == "__main__":
    # Run tests manually
    print("🧪 Running OAuth2 token flow tests...")
    
    # Test without APPLICATION_ID
    try:
        test_oauth2_token_flow_without_application_id()
    except Exception as e:
        print(f"❌ Test without APPLICATION_ID failed: {e}")
    
    # Test with APPLICATION_ID (if available)
    if os.getenv('METEOFRANCE_APPLICATION_ID'):
        try:
            test_oauth2_token_flow_with_application_id()
        except Exception as e:
            print(f"❌ Test with APPLICATION_ID failed: {e}")
        
        try:
            test_oauth2_token_caching()
        except Exception as e:
            print(f"❌ Token caching test failed: {e}")
        
        try:
            test_oauth2_token_refresh()
        except Exception as e:
            print(f"❌ Token refresh test failed: {e}")
    else:
        print("⚠️  METEOFRANCE_APPLICATION_ID not set - skipping live tests")
    
    print("✅ OAuth2 token flow tests completed") 