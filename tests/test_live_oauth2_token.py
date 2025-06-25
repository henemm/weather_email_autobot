"""
Live test for OAuth2 token integration with Météo-France API.

This test validates that the stored OAuth2 token can successfully authenticate
against the Météo-France WMS API endpoint.
"""

import os
import sys
import pytest
import requests
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.meteo_token_provider import MeteoTokenProvider


def test_oauth2_token_provider_structure():
    """
    Test the OAuth2 token provider structure and basic functionality.
    
    This test validates the token provider can be instantiated and has
    the expected methods, without requiring real OAuth2 credentials.
    """
    # Test that we can create an instance
    token_provider = MeteoTokenProvider()
    assert token_provider is not None, "Token provider should be instantiable"
    
    # Test that it has the expected methods
    assert hasattr(token_provider, 'get_token'), "Token provider should have get_token method"
    assert hasattr(token_provider, 'clear_cache'), "Token provider should have clear_cache method"
    assert hasattr(token_provider, '_request_new_token'), "Token provider should have _request_new_token method"
    assert hasattr(token_provider, '_is_token_valid'), "Token provider should have _is_token_valid method"
    
    # Test singleton pattern
    token_provider2 = MeteoTokenProvider()
    assert token_provider is token_provider2, "Token provider should implement singleton pattern"
    
    # Test cache clearing
    token_provider.clear_cache()
    assert token_provider._access_token is None, "Cache should be cleared"
    assert token_provider._token_expiry is None, "Token expiry should be cleared"
    
    print("✅ OAuth2 token provider structure validation passed")


def test_oauth2_missing_credentials_handling():
    """
    Test that the token provider properly handles missing OAuth2 credentials.
    
    This test validates the error handling when required environment variables
    are not set, without requiring real credentials.
    """
    # Store original credentials and .env file
    original_client_id = os.getenv('METEOFRANCE_CLIENT_ID')
    original_client_secret = os.getenv('METEOFRANCE_CLIENT_SECRET')
    env_file = Path(__file__).parent.parent / ".env"
    env_backup = None
    
    try:
        # Temporarily move .env file to prevent it from being loaded
        if env_file.exists():
            env_backup = tempfile.NamedTemporaryFile(delete=False, suffix='.env.backup')
            shutil.move(str(env_file), env_backup.name)
        
        # Reset singleton instance to ensure clean state
        MeteoTokenProvider._instance = None
        
        # Remove credentials from environment
        if 'METEOFRANCE_CLIENT_ID' in os.environ:
            del os.environ['METEOFRANCE_CLIENT_ID']
        if 'METEOFRANCE_CLIENT_SECRET' in os.environ:
            del os.environ['METEOFRANCE_CLIENT_SECRET']
        
        # Create a new token provider instance
        token_provider = MeteoTokenProvider()
        token_provider.clear_cache()  # Ensure no cached token
        
        # Attempt to get token should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            token_provider.get_token()
        
        # Validate error message
        error_message = str(exc_info.value)
        assert "METEOFRANCE_CLIENT_ID" in error_message or "METEOFRANCE_CLIENT_SECRET" in error_message, (
            f"Expected credential-related error, got: {error_message}"
        )
        
        print(f"✅ Missing credentials properly handled: {error_message[:100]}...")
        
    finally:
        # Restore original credentials
        if original_client_id is not None:
            os.environ['METEOFRANCE_CLIENT_ID'] = original_client_id
        if original_client_secret is not None:
            os.environ['METEOFRANCE_CLIENT_SECRET'] = original_client_secret
        
        # Restore .env file
        if env_backup:
            shutil.move(env_backup.name, str(env_file))
        
        # Reset singleton instance
        MeteoTokenProvider._instance = None


def test_oauth2_token_provider_configuration():
    """
    Test that the token provider has the correct configuration.
    
    This test validates the internal configuration of the token provider
    without requiring real API calls.
    """
    token_provider = MeteoTokenProvider()
    
    # Test configuration values
    assert token_provider._token_endpoint == "https://portail-api.meteofrance.fr/token", (
        "Token endpoint should be correctly configured"
    )
    assert token_provider._max_retries == 3, "Max retries should be set to 3"
    assert hasattr(token_provider, '_logger'), "Logger should be configured"
    
    # Test initial state
    token_provider.clear_cache()
    assert not token_provider._is_token_valid(), "Token should be invalid after cache clear"
    
    print("✅ OAuth2 token provider configuration validation passed")


def test_live_oauth2_token_authentication():
    """
    Test live OAuth2 token authentication against Météo-France WMS API.
    
    This test performs a real HTTP request to the Météo-France WMS GetCapabilities
    endpoint using the OAuth2 token from MeteoTokenProvider to validate authentication.
    
    Returns:
        None
        
    Raises:
        ValueError: If OAuth2 credentials are not available
        requests.RequestException: If HTTP request fails
        AssertionError: If response validation fails
    """
    # Check if OAuth2 credentials are available
    if not os.getenv('METEOFRANCE_CLIENT_ID') or not os.getenv('METEOFRANCE_CLIENT_SECRET'):
        pytest.skip("OAuth2 credentials not available - skipping live authentication test")
    
    # Get the OAuth2 token using the token provider
    try:
        token_provider = MeteoTokenProvider()
        token = token_provider.get_token()
    except ValueError as e:
        pytest.fail(f"OAuth2 credentials not available: {e}")
    except Exception as e:
        pytest.fail(f"Failed to obtain OAuth2 token: {e}")
    
    # Target URL for Météo-France WMS GetCapabilities
    url = "https://public-api.meteofrance.fr/public/arome/1.0/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetCapabilities"
    
    # Query parameters
    params = {
        "service": "WMS",
        "version": "1.3.0",
        "language": "eng"
    }
    
    # Headers with OAuth2 Bearer token
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "*/*"
    }
    
    try:
        # Perform the HTTP request
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        # Validate response status code
        assert response.status_code == 200, (
            f"Expected status code 200, got {response.status_code}. "
            f"Response: {response.text[:500]}"
        )
        
        # Validate content type (should be XML for WMS GetCapabilities)
        content_type = response.headers.get("content-type", "")
        assert "xml" in content_type.lower() or "application/xml" in content_type.lower(), (
            f"Expected XML content type, got: {content_type}"
        )
        
        # Validate response content is not empty
        assert response.text.strip(), "Response content is empty"
        
        # Validate response contains expected WMS elements
        response_text = response.text.lower()
        assert "wms_capabilities" in response_text or "capabilities" in response_text, (
            "Response does not contain expected WMS capabilities structure"
        )
        
        print(f"✅ OAuth2 token authentication successful")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {content_type}")
        print(f"   Response length: {len(response.text)} characters")
        
    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                pytest.fail(
                    f"OAuth2 token authentication failed (401 Unauthorized). "
                    f"Token may be expired or invalid. Response: {e.response.text[:500]}"
                )
            else:
                pytest.fail(
                    f"HTTP request failed with status {e.response.status_code}: {e.response.text[:500]}"
                )
        else:
            pytest.fail(f"HTTP request failed: {e}")


def test_oauth2_token_refresh_flow():
    """
    Test complete OAuth2 token refresh flow with live API validation.
    
    This test validates the complete OAuth2 flow:
    1. Clear any cached token to force a new token request
    2. Request a new token using client credentials
    3. Use the new token for a live WMS API call
    4. Validate the API response
    
    This ensures the central authentication logic works correctly in live operation.
    
    Returns:
        None
        
    Raises:
        RuntimeError: If required environment variables are missing
        requests.RequestException: If HTTP request fails
        AssertionError: If response validation fails
    """
    # Check if OAuth2 credentials are available
    if not os.getenv('METEOFRANCE_CLIENT_ID') or not os.getenv('METEOFRANCE_CLIENT_SECRET'):
        pytest.skip("OAuth2 credentials not available - skipping token refresh flow test")
    
    # Get token provider instance
    token_provider = MeteoTokenProvider()
    
    # Clear any cached token to force a new token request
    token_provider.clear_cache()
    print("✅ Cleared token cache to force new token request")
    
    # Request a new token (this should trigger the OAuth2 flow)
    try:
        token = token_provider.get_token()
        print(f"✅ Successfully obtained new OAuth2 token: {token[:10]}...")
    except RuntimeError as e:
        pytest.fail(f"Failed to obtain OAuth2 token - missing credentials: {e}")
    except Exception as e:
        pytest.fail(f"Failed to obtain OAuth2 token: {e}")
    
    # Validate token format
    assert token.strip(), "OAuth2 token is empty or whitespace only"
    assert len(token) >= 50, f"OAuth2 token seems too short: {len(token)} characters"
    
    # Use the new token for a live WMS API call
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
    
    try:
        # Perform the HTTP request with the fresh token
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        # Validate response status code
        assert response.status_code == 200, (
            f"Expected status code 200, got {response.status_code}. "
            f"Response: {response.text[:500]}"
        )
        
        # Validate content type
        content_type = response.headers.get("content-type", "")
        assert "xml" in content_type.lower() or "application/xml" in content_type.lower(), (
            f"Expected XML content type, got: {content_type}"
        )
        
        # Validate response content
        assert response.text.strip(), "Response content is empty"
        
        # Validate WMS capabilities structure
        response_text = response.text.lower()
        assert "wms_capabilities" in response_text or "capabilities" in response_text, (
            "Response does not contain expected WMS capabilities structure"
        )
        
        print(f"✅ Fresh OAuth2 token successfully authenticated against WMS API")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {content_type}")
        print(f"   Response length: {len(response.text)} characters")
        
    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                pytest.fail(
                    f"Fresh OAuth2 token authentication failed (401 Unauthorized). "
                    f"Token may be invalid or API endpoint changed. Response: {e.response.text[:500]}"
                )
            else:
                pytest.fail(
                    f"HTTP request failed with status {e.response.status_code}: {e.response.text[:500]}"
                )
        else:
            pytest.fail(f"HTTP request failed: {e}")


def test_oauth2_invalid_credentials_handling():
    """
    Test handling of invalid OAuth2 credentials.
    
    This test validates that the system properly handles invalid client credentials
    by temporarily modifying environment variables and expecting appropriate error handling.
    
    Note: This test requires careful handling to avoid affecting other tests.
    """
    # Store original credentials and .env file
    original_client_id = os.getenv('METEOFRANCE_CLIENT_ID')
    original_client_secret = os.getenv('METEOFRANCE_CLIENT_SECRET')
    env_file = Path(__file__).parent.parent / ".env"
    env_backup = None
    
    try:
        # Temporarily move .env file to prevent it from being loaded
        if env_file.exists():
            env_backup = tempfile.NamedTemporaryFile(delete=False, suffix='.env.backup')
            shutil.move(str(env_file), env_backup.name)
        
        # Reset singleton instance to ensure clean state
        MeteoTokenProvider._instance = None
        
        # Set invalid credentials
        os.environ['METEOFRANCE_CLIENT_ID'] = 'invalid_client_id'
        os.environ['METEOFRANCE_CLIENT_SECRET'] = 'invalid_client_secret'
        
        # Create a new token provider instance (should pick up invalid credentials)
        token_provider = MeteoTokenProvider()
        token_provider.clear_cache()  # Clear any cached valid token
        
        # Attempt to get token with invalid credentials
        with pytest.raises(Exception) as exc_info:
            token_provider.get_token()
        
        # Validate that we get an appropriate error
        error_message = str(exc_info.value)
        assert "401" in error_message or "unauthorized" in error_message.lower() or "invalid" in error_message.lower(), (
            f"Expected authentication error, got: {error_message}"
        )
        
        print(f"✅ Invalid credentials properly rejected: {error_message[:100]}...")
        
    finally:
        # Restore original credentials
        if original_client_id is not None:
            os.environ['METEOFRANCE_CLIENT_ID'] = original_client_id
        else:
            os.environ.pop('METEOFRANCE_CLIENT_ID', None)
            
        if original_client_secret is not None:
            os.environ['METEOFRANCE_CLIENT_SECRET'] = original_client_secret
        else:
            os.environ.pop('METEOFRANCE_CLIENT_SECRET', None)
        
        # Restore .env file
        if env_backup:
            shutil.move(env_backup.name, str(env_file))
        
        # Reset singleton instance
        MeteoTokenProvider._instance = None


def test_oauth2_token_format():
    """
    Test that the OAuth2 token has the expected format.
    
    Validates that the token is not empty and has a reasonable length
    for a JWT or OAuth2 token.
    """
    # Check if OAuth2 credentials are available
    if not os.getenv('METEOFRANCE_CLIENT_ID') or not os.getenv('METEOFRANCE_CLIENT_SECRET'):
        pytest.skip("OAuth2 credentials not available - skipping token format test")
    
    try:
        token_provider = MeteoTokenProvider()
        token = token_provider.get_token()
    except ValueError as e:
        pytest.fail(f"OAuth2 credentials not available: {e}")
    except Exception as e:
        pytest.fail(f"Failed to obtain OAuth2 token: {e}")
    
    # Validate token is not empty
    assert token.strip(), "OAuth2 token is empty or whitespace only"
    
    # Validate token has reasonable length (JWT tokens are typically 100+ characters)
    assert len(token) >= 50, f"OAuth2 token seems too short: {len(token)} characters"
    
    # Validate token doesn't contain obvious invalid characters
    assert not any(char in token for char in ['\n', '\r', '\t']), "OAuth2 token contains invalid whitespace characters"
    
    print(f"✅ OAuth2 token format validation passed")
    print(f"   Token length: {len(token)} characters")


def test_meteo_token_provider_availability():
    """
    Test that the MeteoTokenProvider can be instantiated and configured.
    
    This test validates that the OAuth2 credentials are properly configured
    and the token provider can be created.
    """
    # Check if OAuth2 credentials are available
    if not os.getenv('METEOFRANCE_CLIENT_ID') or not os.getenv('METEOFRANCE_CLIENT_SECRET'):
        pytest.skip("OAuth2 credentials not available - skipping availability test")
    
    try:
        token_provider = MeteoTokenProvider()
        print(f"✅ MeteoTokenProvider instantiated successfully")
        
        # Test that we can get a token
        token = token_provider.get_token()
        assert token, "Token provider returned empty token"
        print(f"✅ Token provider can retrieve tokens")
        
    except ValueError as e:
        pytest.fail(f"MeteoTokenProvider configuration error: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error with MeteoTokenProvider: {e}") 