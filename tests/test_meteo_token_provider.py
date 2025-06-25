import pytest
import requests
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import os
import base64
from src.auth.meteo_token_provider import MeteoTokenProvider


class TestMeteoTokenProvider:
    """Test cases for MeteoTokenProvider class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Reset singleton instance before each test
        MeteoTokenProvider._instance = None
        self.provider = MeteoTokenProvider()
        self.sample_token_response = {
            "access_token": "test_access_token_123",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    
    def teardown_method(self):
        """Clean up after each test."""
        # Reset singleton instance after each test
        MeteoTokenProvider._instance = None
    
    def test_get_token_on_first_call_requests_new_token(self):
        """Test that first call to get_token requests a new token."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                token = self.provider.get_token()
                
                assert token == "test_access_token_123"
                mock_post.assert_called_once()
    
    def test_get_token_caches_token_for_subsequent_calls(self):
        """Test that subsequent calls return cached token without API request."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                # First call
                token1 = self.provider.get_token()
                # Second call
                token2 = self.provider.get_token()
                
                assert token1 == token2 == "test_access_token_123"
                # Should only be called once due to caching
                mock_post.assert_called_once()
    
    def test_get_token_refreshes_expired_token(self):
        """Test that expired token triggers new API request."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                # First call
                token1 = self.provider.get_token()
                
                # Simulate token expiration by setting expiry time in the past
                self.provider._token_expiry = datetime.now() - timedelta(minutes=1)
                
                # Second call should request new token
                token2 = self.provider.get_token()
                
                assert token1 == token2 == "test_access_token_123"
                # Should be called twice due to expiration
                assert mock_post.call_count == 2
    
    def test_get_token_uses_correct_api_endpoint(self):
        """Test that token request uses correct Météo-France API endpoint."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                self.provider.get_token()
                
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                assert call_args[0][0] == "https://portail-api.meteofrance.fr/token"
    
    def test_get_token_computes_basic_auth_header_correctly(self):
        """Test that Basic Auth header is computed correctly from client credentials."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            client_id = "test_client_id"
            client_secret = "test_client_secret"
            expected_basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': client_id,
                'METEOFRANCE_CLIENT_SECRET': client_secret
            }):
                self.provider.get_token()
                
                call_args = mock_post.call_args
                headers = call_args[1]['headers']
                assert headers['Authorization'] == f'Basic {expected_basic_auth}'
                assert headers['Content-Type'] == 'application/x-www-form-urlencoded'
    
    def test_get_token_uses_correct_body(self):
        """Test that token request includes correct request body."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                self.provider.get_token()
                
                call_args = mock_post.call_args
                data = call_args[1]['data']
                assert data == 'grant_type=client_credentials'
    
    def test_get_token_raises_exception_on_api_error(self):
        """Test that API errors are properly handled."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                with pytest.raises(Exception) as exc_info:
                    self.provider.get_token()
                
                assert "Failed to obtain access token" in str(exc_info.value)
    
    def test_get_token_raises_exception_on_missing_client_id(self):
        """Test that missing METEOFRANCE_CLIENT_ID raises exception."""
        with patch.dict(os.environ, {'METEOFRANCE_CLIENT_SECRET': 'test_secret'}, clear=True):
            with pytest.raises(RuntimeError) as exc_info:
                self.provider.get_token()
            
            assert "Environment variable METEOFRANCE_CLIENT_ID is not set" in str(exc_info.value)
    
    def test_get_token_raises_exception_on_missing_client_secret(self):
        """Test that missing METEOFRANCE_CLIENT_SECRET raises exception."""
        with patch.dict(os.environ, {'METEOFRANCE_CLIENT_ID': 'test_id'}, clear=True):
            with pytest.raises(RuntimeError) as exc_info:
                self.provider.get_token()
            
            assert "Environment variable METEOFRANCE_CLIENT_SECRET is not set" in str(exc_info.value)
    
    def test_token_expiry_calculation(self):
        """Test that token expiry is calculated correctly from expires_in."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "test_token",
                "token_type": "Bearer",
                "expires_in": 3600  # 1 hour
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                with patch('src.auth.meteo_token_provider.datetime') as mock_datetime:
                    # Mock current time
                    mock_now = datetime(2023, 1, 1, 12, 0, 0)
                    mock_datetime.now.return_value = mock_now
                    
                    self.provider.get_token()
                    
                    # Token should expire 1 hour from now
                    expected_expiry = mock_now + timedelta(seconds=3600)
                    assert self.provider._token_expiry == expected_expiry
    
    def test_get_token_handles_network_timeout_with_retry(self):
        """Test that network timeouts are handled with retry logic."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            # First two calls fail with timeout, third succeeds
            mock_post.side_effect = [
                requests.Timeout("Request timeout"),
                requests.Timeout("Request timeout"),
                Mock(json=lambda: self.sample_token_response, status_code=200)
            ]
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                token = self.provider.get_token()
                
                assert token == "test_access_token_123"
                assert mock_post.call_count == 3
    
    def test_get_token_fails_after_max_retries(self):
        """Test that token request fails after maximum retry attempts."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            # All calls fail with timeout
            mock_post.side_effect = requests.Timeout("Request timeout")
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                with pytest.raises(Exception) as exc_info:
                    self.provider.get_token()
                
                assert "Failed to obtain access token" in str(exc_info.value)
                assert mock_post.call_count == 3
    
    def test_clear_cache_resets_token_state(self):
        """Test that clear_cache properly resets token state."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                # Get initial token
                self.provider.get_token()
                assert self.provider._access_token is not None
                assert self.provider._token_expiry is not None
                
                # Clear cache
                self.provider.clear_cache()
                assert self.provider._access_token is None
                assert self.provider._token_expiry is None
                
                # Next call should request new token
                self.provider.get_token()
                assert mock_post.call_count == 2
    
    def test_integration_multiple_api_calls_share_same_token(self):
        """Integration test: multiple API calls should share the same token."""
        with patch('src.auth.meteo_token_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {
                'METEOFRANCE_CLIENT_ID': 'test_client_id',
                'METEOFRANCE_CLIENT_SECRET': 'test_client_secret'
            }):
                # Simulate multiple modules using the same token provider
                provider1 = MeteoTokenProvider()
                provider2 = MeteoTokenProvider()
                
                # Both should be the same singleton instance
                assert provider1 is provider2
                
                # First module gets token
                token1 = provider1.get_token()
                
                # Second module gets token (should be cached)
                token2 = provider2.get_token()
                
                # Tokens should be identical
                assert token1 == token2 == "test_access_token_123"
                
                # Only one API call should have been made
                mock_post.assert_called_once()
                
                # Verify the token is properly cached
                assert provider1._access_token == "test_access_token_123"
                assert provider2._access_token == "test_access_token_123"
                assert provider1._token_expiry == provider2._token_expiry 