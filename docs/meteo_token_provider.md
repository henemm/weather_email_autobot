# MeteoTokenProvider - OAuth2 Token Management

## Overview

The `MeteoTokenProvider` is a centralized component that manages OAuth2 access tokens for Météo-France APIs (AROME, Vigilance, etc.). It handles token acquisition, caching, and automatic renewal using the OAuth2 Client Credentials flow.

## Features

- **Automatic token acquisition** from Météo-France OAuth2 endpoint
- **In-memory caching** for up to 60 minutes to minimize API calls
- **Automatic renewal** when tokens expire
- **Error handling** for network issues and API errors
- **Thread-safe** for concurrent usage

## Installation

The component is part of the `src/auth` package and requires the `requests` library.

## Configuration

Set the `METEOFRANCE_BASIC_AUTH` environment variable with your Base64-encoded client credentials:

```bash
export METEOFRANCE_BASIC_AUTH='your_base64_encoded_credentials'
```

## Usage

### Basic Usage

```python
from src.auth.meteo_token_provider import MeteoTokenProvider

# Create provider instance
provider = MeteoTokenProvider()

# Get access token (automatically cached and renewed)
token = provider.get_token()

# Use token in API requests
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
```

### Integration with Weather Modules

The component is already integrated into the AROME weather fetching module:

```python
# In src/wetter/fetch_arome.py
from auth.meteo_token_provider import MeteoTokenProvider

def fetch_arome_weather_data(latitude: float, longitude: float) -> WeatherData:
    # Get OAuth token using the centralized token provider
    token_provider = MeteoTokenProvider()
    token = token_provider.get_token()
    
    # Use token in API request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # ... rest of the function
```

## API Reference

### MeteoTokenProvider

#### `__init__()`
Initialize the token provider.

#### `get_token() -> str`
Get a valid access token for Météo-France APIs.

**Returns:**
- `str`: The access token to use in Authorization header

**Raises:**
- `ValueError`: If `METEOFRANCE_BASIC_AUTH` environment variable is missing
- `Exception`: If token request fails

#### `clear_cache() -> None`
Clear the cached token, forcing the next `get_token()` call to request a new token.

## Token Lifecycle

1. **First Request**: Token is requested from Météo-France OAuth2 endpoint
2. **Caching**: Token is cached in memory with expiry time
3. **Subsequent Requests**: Cached token is returned if still valid
4. **Expiration**: When token expires (or within 5 minutes), new token is requested
5. **Error Handling**: Network errors and API errors are properly handled

## Testing

Run the unit tests to verify functionality:

```bash
PYTHONPATH=. pytest tests/test_meteo_token_provider.py -v
```

## Demo

Run the demo script to see the component in action:

```bash
python scripts/demo_token_provider.py
```

## Error Handling

The component handles various error scenarios:

- **Missing Environment Variable**: Raises `ValueError` with clear message
- **Network Errors**: Wraps in descriptive exception
- **API Errors**: Includes status code and response text
- **Invalid Response Format**: Handles malformed JSON responses

## Security Considerations

- Tokens are stored in memory only (not persisted to disk)
- Tokens automatically expire after 1 hour
- 5-minute buffer ensures tokens don't expire during use
- No sensitive data is logged or exposed

## Migration from Old Token System

If you were previously using environment variables directly:

**Before:**
```python
import os
token = os.environ.get("METEOFRANCE_AROME_TOKEN")
```

**After:**
```python
from src.auth.meteo_token_provider import MeteoTokenProvider
provider = MeteoTokenProvider()
token = provider.get_token()
```

## Troubleshooting

### "METEOFRANCE_BASIC_AUTH environment variable is required"
- Ensure the environment variable is set
- Check that the value is correctly Base64-encoded
- Verify the variable name spelling

### "Failed to obtain access token"
- Check network connectivity
- Verify API endpoint is accessible
- Ensure credentials are valid and not expired

### Token not being cached
- Check that the same provider instance is being reused
- Verify that the token expiry calculation is working correctly 