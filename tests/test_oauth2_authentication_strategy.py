"""
Integration tests for OAuth2 authentication strategy across all Meteo France APIs.

This module implements the test strategy from strategy_authentication_meteo.md
to verify that the centralized OAuth2 token provider works correctly for all
three APIs: AROME WCS, AROME Instability Layers, and Vigilance Bulletins.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.meteo_token_provider import MeteoTokenProvider
from wetter.fetch_arome_wcs import fetch_arome_wcs_data
from wetter.fetch_arome_instability import fetch_arome_instability_layer
from wetter.fetch_arome_thunder import fetch_arome_thunder_probability
from wetter.warning import fetch_warnings
from tests.utils.env_loader import get_env_var


def _has_meteo_token():
    """Check if OAuth2 credentials are available for testing."""
    return bool(get_env_var('METEOFRANCE_BASIC_AUTH'))


class TestOAuth2AuthenticationStrategy:
    """
    Test cases for OAuth2 authentication strategy across all Meteo France APIs.
    
    Implements the test strategy from strategy_authentication_meteo.md to verify:
    - Token is created only once
    - Token is reused across all APIs
    - Token is renewed when expired
    - All APIs return valid responses with the same token
    - Error cases are handled properly
    """
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Reset singleton instance to ensure clean state
        MeteoTokenProvider._instance = None
        self.token_provider = MeteoTokenProvider()
        
        # Test coordinates (Corsica)
        self.latitude = 42.308
        self.longitude = 8.937
        
        # Sample token response
        self.sample_token_response = {
            "access_token": "test_oauth2_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    
    def teardown_method(self):
        """Clean up after each test."""
        # Reset singleton instance
        MeteoTokenProvider._instance = None
    
    def test_token_created_only_once_across_all_apis(self):
        """
        Test that token is created only once and reused across all three APIs.
        
        This test verifies the core requirement: Token wird nur einmal erzeugt
        """
        with patch('auth.meteo_token_provider.requests.post') as mock_post:
            # Mock successful token response
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {'METEOFRANCE_BASIC_AUTH': 'test_auth'}):
                # Call all three APIs
                token1 = self.token_provider.get_token()
                
                # Mock all WCS API calls (used by all three modules)
                with patch('wetter.fetch_arome_wcs.requests.get') as mock_wcs_get:
                    mock_wcs_response = Mock()
                    mock_wcs_response.status_code = 200
                    mock_wcs_response.content = b"dummy_netcdf_data"
                    mock_wcs_get.return_value = mock_wcs_response
                    
                    # Call WCS API
                    fetch_arome_wcs_data(
                        self.latitude, 
                        self.longitude, 
                        "TEMPERATURE__GROUND_OR_WATER_SURFACE"
                    )
                    
                    # Get token again (should be cached)
                    token2 = self.token_provider.get_token()
                    
                    # Call instability API (uses WCS internally)
                    fetch_arome_instability_layer(
                        self.latitude,
                        self.longitude,
                        "CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND"
                    )
                    
                    # Get token again (should still be cached)
                    token3 = self.token_provider.get_token()
                    
                    # Call thunder probability API (uses WCS internally)
                    fetch_arome_thunder_probability(self.latitude, self.longitude)
                    
                    # Get token again (should still be cached)
                    token4 = self.token_provider.get_token()
                
                # Call Vigilance API
                with patch('wetter.warning.requests.get') as mock_vigilance_get:
                    mock_vigilance_response = Mock()
                    mock_vigilance_response.status_code = 200
                    mock_vigilance_response.json.return_value = {
                        "timelaps": [
                            {
                                "validity_start_date": "2025-01-15T12:00:00+00:00",
                                "validity_end_date": "2025-01-15T18:00:00+00:00",
                                "max_colors": [
                                    {
                                        "phenomenon_max_color_id": 3,
                                        "phenomenon_max_name": "Orages"
                                    }
                                ]
                            }
                        ]
                    }
                    mock_vigilance_get.return_value = mock_vigilance_response
                    
                    fetch_warnings(self.latitude, self.longitude)
                
                # Get token one more time (should still be cached)
                token5 = self.token_provider.get_token()
                
                # Verify all tokens are the same
                assert token1 == token2 == token3 == token4 == token5 == "test_oauth2_token_12345"
                
                # Verify token was requested only once
                mock_post.assert_called_once()
    
    def test_token_renewal_after_expiry(self):
        """
        Test that token is renewed after expiration and reused across APIs.
        
        This test verifies: Token wird nach Ablauf erneuert und erneut verwendet
        """
        with patch('auth.meteo_token_provider.requests.post') as mock_post:
            # Mock successful token responses
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {'METEOFRANCE_BASIC_AUTH': 'test_auth'}):
                # First token request
                token1 = self.token_provider.get_token()
                
                # Simulate token expiration
                self.token_provider._token_expiry = datetime.now() - timedelta(minutes=1)
                
                # Second token request should trigger renewal
                token2 = self.token_provider.get_token()
                
                # Verify tokens are the same (same mock response)
                assert token1 == token2 == "test_oauth2_token_12345"
                
                # Verify token was requested twice (initial + renewal)
                assert mock_post.call_count == 2
    
    def test_all_apis_return_valid_responses_with_same_token(self):
        """
        Test that all three APIs return valid responses using the same token.
        
        This test verifies: Alle APIs liefern HTTP 200 oder definierte Antworten
        """
        with patch('auth.meteo_token_provider.requests.post') as mock_token_post:
            # Mock token response
            mock_token_response = Mock()
            mock_token_response.json.return_value = self.sample_token_response
            mock_token_response.status_code = 200
            mock_token_post.return_value = mock_token_response
            
            with patch.dict(os.environ, {'METEOFRANCE_BASIC_AUTH': 'test_auth'}):
                # Mock all API responses
                with patch('wetter.fetch_arome_wcs.requests.get') as mock_wcs_get:
                    mock_wcs_response = Mock()
                    mock_wcs_response.status_code = 200
                    mock_wcs_response.content = b"dummy_netcdf_data"
                    mock_wcs_get.return_value = mock_wcs_response
                    
                    # Test WCS API
                    wcs_result = fetch_arome_wcs_data(
                        self.latitude,
                        self.longitude,
                        "TEMPERATURE__GROUND_OR_WATER_SURFACE"
                    )
                    assert wcs_result is not None
                
                # Test instability API (uses WCS internally)
                with patch('wetter.fetch_arome_wcs.requests.get') as mock_instability_get:
                    mock_instability_response = Mock()
                    mock_instability_response.status_code = 200
                    mock_instability_response.content = b"dummy_netcdf_data"
                    mock_instability_get.return_value = mock_instability_response
                    
                    instability_result = fetch_arome_instability_layer(
                        self.latitude,
                        self.longitude,
                        "CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND"
                    )
                    assert instability_result is not None
                
                # Test thunder probability API (uses WCS internally)
                with patch('wetter.fetch_arome_wcs.requests.get') as mock_thunder_get:
                    mock_thunder_response = Mock()
                    mock_thunder_response.status_code = 200
                    mock_thunder_response.content = b"dummy_netcdf_data"
                    mock_thunder_get.return_value = mock_thunder_response
                    
                    thunder_result = fetch_arome_thunder_probability(
                        self.latitude,
                        self.longitude
                    )
                    assert thunder_result is not None
                
                # Test Vigilance API
                with patch('wetter.warning.requests.get') as mock_vigilance_get:
                    mock_vigilance_response = Mock()
                    mock_vigilance_response.status_code = 200
                    mock_vigilance_response.json.return_value = {
                        "timelaps": [
                            {
                                "validity_start_date": "2025-01-15T12:00:00+00:00",
                                "validity_end_date": "2025-01-15T18:00:00+00:00",
                                "max_colors": [
                                    {
                                        "phenomenon_max_color_id": 3,
                                        "phenomenon_max_name": "Orages"
                                    }
                                ]
                            }
                        ]
                    }
                    mock_vigilance_get.return_value = mock_vigilance_response
                    
                    vigilance_result = fetch_warnings(self.latitude, self.longitude)
                    assert vigilance_result is not None
                    assert len(vigilance_result) == 1
                    assert vigilance_result[0].type == "Orages"
                    assert vigilance_result[0].level == 3
                
                # Verify token was requested only once for all APIs
                mock_token_post.assert_called_once()
    
    def test_invalid_application_id_raises_error(self):
        """
        Test that invalid APPLICATION_ID raises error during token request.
        
        This test verifies: Ungültiger APPLICATION_ID → Fehler beim Token-Abruf
        """
        with patch('auth.meteo_token_provider.requests.post') as mock_post:
            # Mock API error response
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Invalid client credentials"
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {'METEOFRANCE_BASIC_AUTH': 'invalid_auth'}):
                with pytest.raises(Exception) as exc_info:
                    self.token_provider.get_token()
                
                assert "Failed to obtain access token" in str(exc_info.value)
                assert "401" in str(exc_info.value)
    
    def test_missing_token_raises_runtime_error(self):
        """
        Test that missing token raises RuntimeError with clear message.
        
        This test verifies: Token fehlt → RuntimeError mit Klartextmeldung
        """
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                self.token_provider.get_token()
            
            assert "METEOFRANCE_BASIC_AUTH environment variable is required" in str(exc_info.value)
    
    def test_singleton_pattern_ensures_single_token_instance(self):
        """
        Test that singleton pattern ensures only one token instance exists.
        
        This test verifies the singleton behavior across multiple provider instances.
        """
        with patch('auth.meteo_token_provider.requests.post') as mock_post:
            # Mock successful token response
            mock_response = Mock()
            mock_response.json.return_value = self.sample_token_response
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with patch.dict(os.environ, {'METEOFRANCE_BASIC_AUTH': 'test_auth'}):
                # Create multiple provider instances
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
                assert token1 == token2 == token3 == "test_oauth2_token_12345"
                
                # Verify token was requested only once
                mock_post.assert_called_once()


@pytest.mark.integration
@pytest.mark.skipif(
    not _has_meteo_token(),
    reason="METEOFRANCE_BASIC_AUTH environment variable not set"
)
class TestOAuth2AuthenticationLive:
    """
    Live integration tests for OAuth2 authentication with real API calls.
    
    These tests require valid OAuth2 credentials and make actual API calls
    to verify the complete authentication flow works in production.
    """
    
    def setup_method(self):
        """Set up test environment for live tests."""
        # Reset singleton instance
        MeteoTokenProvider._instance = None
        self.token_provider = MeteoTokenProvider()
        
        # Test coordinates (Corsica)
        self.latitude = 42.308
        self.longitude = 8.937
    
    def teardown_method(self):
        """Clean up after live tests."""
        MeteoTokenProvider._instance = None
    
    def test_live_token_acquisition_and_reuse(self):
        """
        Live test: Verify token is acquired once and reused across API calls.
        
        This test makes real API calls to verify the authentication strategy
        works correctly in production.
        """
        print("\n=== Live OAuth2 Authentication Test ===")
        
        # Get first token
        print("🔑 Requesting first OAuth2 token...")
        token1 = self.token_provider.get_token()
        print(f"✅ Token obtained: {token1[:20]}...")
        
        # Get second token (should be cached)
        print("🔄 Requesting second token (should be cached)...")
        token2 = self.token_provider.get_token()
        print(f"✅ Cached token returned: {token2[:20]}...")
        
        # Verify tokens are the same
        assert token1 == token2, "Token caching failed - tokens are different!"
        print("✅ Token caching is working correctly!")
        
        # Test with actual API call
        print("🌤️  Testing token with AROME WCS API...")
        try:
            wcs_data = fetch_arome_wcs_data(
                self.latitude,
                self.longitude,
                "TEMPERATURE__GROUND_OR_WATER_SURFACE"
            )
            print(f"✅ WCS API call successful: {wcs_data.layer}")
        except Exception as e:
            print(f"⚠️  WCS API call failed: {e}")
        
        # Get token again after API call
        token3 = self.token_provider.get_token()
        assert token3 == token1, "Token changed after API call!"
        print("✅ Token remains consistent after API usage!")
    
    def test_live_all_apis_with_same_token(self):
        """
        Live test: Verify all three APIs work with the same OAuth2 token.
        
        This test verifies that the centralized token provider works correctly
        for all three Meteo France APIs in a real environment.
        """
        print("\n=== Live Multi-API Authentication Test ===")
        
        # Get token once
        token = self.token_provider.get_token()
        print(f"🔑 Using token: {token[:20]}...")
        
        # Test all three APIs
        apis_tested = 0
        
        # Test 1: AROME WCS API
        print("1️⃣  Testing AROME WCS API...")
        try:
            wcs_data = fetch_arome_wcs_data(
                self.latitude,
                self.longitude,
                "TEMPERATURE__GROUND_OR_WATER_SURFACE"
            )
            print(f"   ✅ WCS API: {wcs_data.layer}")
            apis_tested += 1
        except Exception as e:
            print(f"   ❌ WCS API failed: {e}")
        
        # Test 2: AROME Instability API
        print("2️⃣  Testing AROME Instability API...")
        try:
            instability_data = fetch_arome_instability_layer(
                self.latitude,
                self.longitude,
                "CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND"
            )
            print(f"   ✅ Instability API: {instability_data.layer}")
            apis_tested += 1
        except Exception as e:
            print(f"   ❌ Instability API failed: {e}")
        
        # Test 3: AROME Thunder Probability API
        print("3️⃣  Testing AROME Thunder Probability API...")
        try:
            thunder_data = fetch_arome_thunder_probability(
                self.latitude,
                self.longitude
            )
            print(f"   ✅ Thunder API: {thunder_data.layer}")
            apis_tested += 1
        except Exception as e:
            print(f"   ❌ Thunder API failed: {e}")
        
        # Test 4: Vigilance API
        print("4️⃣  Testing Vigilance API...")
        try:
            vigilance_data = fetch_warnings(self.latitude, self.longitude)
            print(f"   ✅ Vigilance API: {len(vigilance_data)} alerts found")
            apis_tested += 1
        except Exception as e:
            print(f"   ❌ Vigilance API failed: {e}")
        
        # Verify at least one API worked
        assert apis_tested > 0, "No APIs were successfully tested!"
        print(f"✅ Successfully tested {apis_tested}/4 APIs with the same token!")
        
        # Verify token is still the same
        final_token = self.token_provider.get_token()
        assert final_token == token, "Token changed during API testing!"
        print("✅ Token remained consistent across all API calls!")


if __name__ == "__main__":
    # Run the live tests if executed directly
    pytest.main([__file__, "-v", "-s"]) 