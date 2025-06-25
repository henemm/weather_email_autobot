"""
Tests for OAuth2 client credentials flow implementation.

This module tests the refactored OAuth2 implementation that uses
METEOFRANCE_CLIENT_ID and METEOFRANCE_CLIENT_SECRET instead of
METEOFRANCE_APPLICATION_ID.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.meteo_token_provider import MeteoTokenProvider


class TestOAuth2ClientCredentials:
    """Test OAuth2 client credentials flow implementation."""

    def setup_method(self):
        """Set up test environment."""
        # Reset singleton instance
        MeteoTokenProvider._instance = None
        self.provider = MeteoTokenProvider()
        
        # Sample token response
        self.sample_token_response = {
            'access_token': 'test_oauth2_token_12345',
            'token_type': 'Bearer',
            'expires_in': 3600
        }

    def teardown_method(self):
        """Clean up after tests."""
        MeteoTokenProvider._instance = None

    def test_get_token_uses_client_credentials(self):
        """Test that token request uses client_id and client_secret."""
        MeteoTokenProvider._instance = None
        with patch('auth.meteo_token_provider.requests.post') as mock_post, \
             patch('src.utils.env_loader.load_dotenv'):
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }, clear=True):
                provider = MeteoTokenProvider()
                token = provider.get_token()
                
                # Verify token was returned
                assert token == 'test_oauth2_token_12345'
                
                # Verify correct API call
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                
                # Check URL
                assert call_args[0][0] == "https://portail-api.meteofrance.fr/token"
                
                # Check headers
                headers = call_args[1]['headers']
                assert headers['Content-Type'] == 'application/x-www-form-urlencoded'
                
                # Check Authorization header format
                auth_header = headers['Authorization']
                assert auth_header.startswith('Basic ')
                
                # Decode and verify credentials
                import base64
                credentials = base64.b64decode(auth_header[6:]).decode()
                assert credentials == 'test_client_id:test_client_secret'
                
                # Check data
                assert call_args[1]['data'] == 'grant_type=client_credentials'

    def test_get_token_raises_exception_on_missing_client_id(self):
        """Test that missing METEOFRANCE_CLIENT_ID raises exception."""
        MeteoTokenProvider._instance = None
        with patch('src.utils.env_loader.load_dotenv'), \
             patch.dict(os.environ, {'METEOFRANCE_CLIENT_SECRET': 'test_secret'}, clear=True):
            provider = MeteoTokenProvider()
            with pytest.raises(RuntimeError) as exc_info:
                provider.get_token()
            
            assert "Environment variable METEOFRANCE_CLIENT_ID is not set" in str(exc_info.value)

    def test_get_token_raises_exception_on_missing_client_secret(self):
        """Test that missing METEOFRANCE_CLIENT_SECRET raises exception."""
        MeteoTokenProvider._instance = None
        with patch('src.utils.env_loader.load_dotenv'), \
             patch.dict(os.environ, {'METEOFRANCE_CLIENT_ID': 'test_id'}, clear=True):
            provider = MeteoTokenProvider()
            with pytest.raises(RuntimeError) as exc_info:
                provider.get_token()
            
            assert "Environment variable METEOFRANCE_CLIENT_SECRET is not set" in str(exc_info.value)

    def test_get_token_raises_exception_on_api_error(self):
        """Test that API errors are properly handled."""
        MeteoTokenProvider._instance = None
        with patch('auth.meteo_token_provider.requests.post') as mock_post, \
             patch('src.utils.env_loader.load_dotenv'):
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Invalid client credentials"
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }, clear=True):
                provider = MeteoTokenProvider()
                with pytest.raises(Exception) as exc_info:
                    provider.get_token()
                
                assert "Failed to obtain access token" in str(exc_info.value)
                assert "401" in str(exc_info.value)

    def test_token_caching_works_correctly(self):
        """Test that tokens are properly cached and reused."""
        MeteoTokenProvider._instance = None
        with patch('auth.meteo_token_provider.requests.post') as mock_post, \
             patch('src.utils.env_loader.load_dotenv'):
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }, clear=True):
                provider = MeteoTokenProvider()
                # Get first token
                token1 = provider.get_token()
                assert token1 == 'test_oauth2_token_12345'
                
                # Get second token (should be cached)
                token2 = provider.get_token()
                assert token2 == 'test_oauth2_token_12345'
                
                # Verify tokens are identical
                assert token1 == token2
                
                # Verify API was called only once
                mock_post.assert_called_once()

    def test_token_refresh_when_expired(self):
        """Test that tokens are refreshed when expired."""
        MeteoTokenProvider._instance = None
        with patch('auth.meteo_token_provider.requests.post') as mock_post, \
             patch('src.utils.env_loader.load_dotenv'):
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }, clear=True):
                provider = MeteoTokenProvider()
                # Get initial token
                initial_token = provider.get_token()
                assert initial_token == 'test_oauth2_token_12345'
                
                # Simulate token expiration
                provider._token_expiry = datetime.now() - timedelta(minutes=1)
                
                # Get token again (should trigger refresh)
                refreshed_token = provider.get_token()
                assert refreshed_token == 'test_oauth2_token_12345'
                
                # Verify API was called twice (initial + refresh)
                assert mock_post.call_count == 2

    def test_clear_cache_forces_new_token_request(self):
        """Test that clear_cache forces a new token request."""
        MeteoTokenProvider._instance = None
        with patch('auth.meteo_token_provider.requests.post') as mock_post, \
             patch('src.utils.env_loader.load_dotenv'):
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }, clear=True):
                provider = MeteoTokenProvider()
                # Get initial token
                token1 = provider.get_token()
                assert token1 == 'test_oauth2_token_12345'
                
                # Clear cache
                provider.clear_cache()
                
                # Get token again (should request new token)
                token2 = provider.get_token()
                assert token2 == 'test_oauth2_token_12345'
                
                # Verify API was called twice
                assert mock_post.call_count == 2

    def test_singleton_pattern_works(self):
        """Test that singleton pattern ensures single instance."""
        MeteoTokenProvider._instance = None
        with patch('auth.meteo_token_provider.requests.post') as mock_post, \
             patch('src.utils.env_loader.load_dotenv'):
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }, clear=True):
                provider1 = MeteoTokenProvider()
                provider2 = MeteoTokenProvider()
                provider3 = MeteoTokenProvider()
                
                # Verify all instances are the same object
                assert provider1 is provider2
                assert provider2 is provider3
                assert provider1 is provider3
                
                # Get token from first instance
                token1 = provider1.get_token()
                
                # Get token from other instances (should reuse cached token)
                token2 = provider2.get_token()
                token3 = provider3.get_token()
                
                # Verify all tokens are the same
                assert token1 == token2 == token3 == 'test_oauth2_token_12345'
                
                # Verify token was requested only once
                mock_post.assert_called_once()


@pytest.mark.integration
@pytest.mark.skipif(
    not (os.getenv('METEOFRANCE_CLIENT_ID') and os.getenv('METEOFRANCE_CLIENT_SECRET')),
    reason="METEOFRANCE_CLIENT_ID and METEOFRANCE_CLIENT_SECRET environment variables not set"
)
class TestOAuth2ClientCredentialsLive:
    """Live integration tests for OAuth2 client credentials flow."""

    def setup_method(self):
        """Set up test environment for live tests."""
        # Reset singleton instance
        MeteoTokenProvider._instance = None
        self.provider = MeteoTokenProvider()

    def teardown_method(self):
        """Clean up after live tests."""
        MeteoTokenProvider._instance = None

    def test_live_token_acquisition(self):
        """Live test: Verify token can be acquired with real credentials."""
        print("\n=== Live OAuth2 Client Credentials Test ===")
        
        try:
            # Get token
            print("🔑 Requesting OAuth2 token with client credentials...")
            token = self.provider.get_token()
            
            # Validate token format
            assert token.strip(), "OAuth2 token is empty or whitespace only"
            assert len(token) >= 50, f"OAuth2 token seems too short: {len(token)} characters"
            
            print(f"✅ Token obtained successfully: {token[:20]}...")
            
            # Test token with WMS API
            import requests
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
            
            print("🌤️  Testing token with WMS API...")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            assert response.status_code == 200, (
                f"WMS API call failed with status {response.status_code}: {response.text}"
            )
            
            print("✅ WMS API call successful with OAuth2 token")
            
        except Exception as e:
            pytest.fail(f"Live OAuth2 client credentials test failed: {e}")

    def test_live_token_caching(self):
        """Live test: Verify token caching works with real API."""
        print("\n=== Live OAuth2 Token Caching Test ===")
        
        try:
            # Clear any existing cache
            self.provider.clear_cache()
            
            # Get first token
            print("🔑 Requesting first token...")
            token1 = self.provider.get_token()
            assert token1, "First token should not be empty"
            
            # Get second token (should be cached)
            print("🔄 Requesting second token (should be cached)...")
            token2 = self.provider.get_token()
            assert token2, "Second token should not be empty"
            
            # Tokens should be identical (cached)
            assert token1 == token2, "Cached tokens should be identical"
            
            print("✅ Token caching works correctly with live API")
            print(f"   Token: {token1[:20]}...")
            
        except Exception as e:
            pytest.fail(f"Live token caching test failed: {e}")


if __name__ == "__main__":
    # Run tests manually
    print("🧪 Running OAuth2 client credentials tests...")
    
    # Test without credentials
    try:
        test_instance = TestOAuth2ClientCredentials()
        test_instance.setup_method()
        test_instance.test_get_token_raises_exception_on_missing_client_id()
        test_instance.test_get_token_raises_exception_on_missing_client_secret()
        print("✅ Tests without credentials passed")
    except Exception as e:
        print(f"❌ Tests without credentials failed: {e}")
    
    # Test with credentials (if available)
    if os.getenv('METEOFRANCE_CLIENT_ID') and os.getenv('METEOFRANCE_CLIENT_SECRET'):
        try:
            live_test_instance = TestOAuth2ClientCredentialsLive()
            live_test_instance.setup_method()
            live_test_instance.test_live_token_acquisition()
            live_test_instance.test_live_token_caching()
            print("✅ Live tests with credentials passed")
        except Exception as e:
            print(f"❌ Live tests with credentials failed: {e}")
    else:
        print("⚠️  METEOFRANCE_CLIENT_ID and METEOFRANCE_CLIENT_SECRET not set - skipping live tests")
    
    print("✅ OAuth2 client credentials tests completed") 