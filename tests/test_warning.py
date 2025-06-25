import unittest
from unittest.mock import patch, Mock
from wetter.warning import fetch_warnings, WeatherAlert
from datetime import datetime
from auth.meteo_token_provider import MeteoTokenProvider


class TestWeatherWarnings(unittest.TestCase):

    def setUp(self):
        """Set up test environment."""
        # Reset singleton instance
        MeteoTokenProvider._instance = None

    def tearDown(self):
        """Clean up after test."""
        # Reset singleton instance
        MeteoTokenProvider._instance = None

    @patch('wetter.warning.requests.get')
    @patch('auth.meteo_token_provider.requests.post')
    def test_fetch_warnings_success(self, mock_token_post, mock_get):
        """Test successful weather warnings fetching with OAuth2 authentication."""
        # Mock OAuth2 token response
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_oauth2_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mock_token_response.status_code = 200
        mock_token_post.return_value = mock_token_response
        
        # Mock Vigilance API response
        mock_response = {
            "timelaps": [
                {
                    "validity_start_date": "2025-06-20T06:00:00+00:00",
                    "validity_end_date": "2025-06-21T06:00:00+00:00",
                    "max_colors": [
                        {
                            "phenomenon_max_color_id": 3,
                            "phenomenon_max_name": "Orages"
                        }
                    ]
                }
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        alerts = fetch_warnings(42.3, 9.2)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].type, "Orages")
        self.assertEqual(alerts[0].level, 3)
        self.assertIsInstance(alerts[0].start, datetime)
        self.assertIsInstance(alerts[0].end, datetime)
        
        # Verify OAuth2 token was requested
        mock_token_post.assert_called_once()
        
        # Verify Vigilance API was called with OAuth2 token
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        headers = call_args[1]['headers']
        self.assertEqual(headers['Authorization'], 'Bearer test_oauth2_token_12345')

    @patch('wetter.warning.requests.get')
    @patch('auth.meteo_token_provider.requests.post')
    def test_fetch_warnings_no_alerts(self, mock_token_post, mock_get):
        """Test weather warnings fetching when no alerts are present."""
        # Mock OAuth2 token response
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_oauth2_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mock_token_response.status_code = 200
        mock_token_post.return_value = mock_token_response
        
        # Mock empty Vigilance API response
        mock_response = {"timelaps": []}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        alerts = fetch_warnings(42.3, 9.2)
        self.assertEqual(len(alerts), 0)

    @patch('auth.meteo_token_provider.requests.post')
    def test_fetch_warnings_oauth2_error(self, mock_token_post):
        """Test weather warnings fetching when OAuth2 token request fails."""
        # Mock OAuth2 token error
        mock_token_response = Mock()
        mock_token_response.status_code = 401
        mock_token_response.text = "Invalid client credentials"
        mock_token_post.return_value = mock_token_response

        with self.assertRaises(Exception) as context:
            fetch_warnings(42.3, 9.2)
        
        self.assertIn("Failed to obtain access token", str(context.exception))

    @patch('wetter.warning.requests.get')
    @patch('auth.meteo_token_provider.requests.post')
    def test_fetch_warnings_api_error(self, mock_token_post, mock_get):
        """Test weather warnings fetching when Vigilance API returns error."""
        # Mock OAuth2 token response
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_oauth2_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mock_token_response.status_code = 200
        mock_token_post.return_value = mock_token_response
        
        # Mock Vigilance API error
        mock_get.return_value.status_code = 500
        mock_get.return_value.raise_for_status.side_effect = Exception("Internal Server Error")

        with self.assertRaises(Exception):
            fetch_warnings(42.3, 9.2)

    @patch('wetter.warning.requests.get')
    @patch('auth.meteo_token_provider.requests.post')
    def test_fetch_warnings_low_level_filtered(self, mock_token_post, mock_get):
        """Test that low-level alerts (level < 2) are filtered out."""
        # Mock OAuth2 token response
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_oauth2_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mock_token_response.status_code = 200
        mock_token_post.return_value = mock_token_response
        
        # Mock Vigilance API response with low-level alert
        mock_response = {
            "timelaps": [
                {
                    "validity_start_date": "2025-06-20T06:00:00+00:00",
                    "validity_end_date": "2025-06-21T06:00:00+00:00",
                    "max_colors": [
                        {
                            "phenomenon_max_color_id": 1,  # Green level (filtered out)
                            "phenomenon_max_name": "Vent"
                        }
                    ]
                }
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        alerts = fetch_warnings(42.3, 9.2)
        self.assertEqual(len(alerts), 0)  # Low-level alert should be filtered out

    @patch('wetter.warning.requests.get')
    @patch('auth.meteo_token_provider.requests.post')
    def test_fetch_warnings_multiple_alerts(self, mock_token_post, mock_get):
        """Test fetching multiple weather alerts with different levels."""
        # Mock OAuth2 token response
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_oauth2_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mock_token_response.status_code = 200
        mock_token_post.return_value = mock_token_response
        
        # Mock Vigilance API response with multiple alerts
        mock_response = {
            "timelaps": [
                {
                    "validity_start_date": "2025-06-20T06:00:00+00:00",
                    "validity_end_date": "2025-06-21T06:00:00+00:00",
                    "max_colors": [
                        {
                            "phenomenon_max_color_id": 2,  # Yellow
                            "phenomenon_max_name": "Vent"
                        },
                        {
                            "phenomenon_max_color_id": 3,  # Orange
                            "phenomenon_max_name": "Orages"
                        },
                        {
                            "phenomenon_max_color_id": 4,  # Red
                            "phenomenon_max_name": "Pluie-inondation"
                        }
                    ]
                }
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        alerts = fetch_warnings(42.3, 9.2)
        self.assertEqual(len(alerts), 3)
        
        # Verify alert levels
        alert_levels = [alert.level for alert in alerts]
        self.assertIn(2, alert_levels)  # Yellow
        self.assertIn(3, alert_levels)  # Orange
        self.assertIn(4, alert_levels)  # Red
        
        # Verify alert types
        alert_types = [alert.type for alert in alerts]
        self.assertIn("Vent", alert_types)
        self.assertIn("Orages", alert_types)
        self.assertIn("Pluie-inondation", alert_types)


if __name__ == "__main__":
    unittest.main()