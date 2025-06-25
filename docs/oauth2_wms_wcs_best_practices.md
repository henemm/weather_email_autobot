# OAuth2 Client Credentials & WMS/WCS Best Practices

## Overview
This document summarizes the successful refactoring of Météo-France API authentication from deprecated `application_id` to OAuth2 Client Credentials flow, and the robust implementation of WMS/WCS time handling.

## OAuth2 Client Credentials Implementation

### ✅ Completed Refactoring
- **Removed**: `METEOFRANCE_APPLICATION_ID` (deprecated)
- **Added**: `METEOFRANCE_CLIENT_ID` and `METEOFRANCE_CLIENT_SECRET`
- **Implementation**: `src/auth/meteo_token_provider.py`
- **Status**: All tests passing, live integration verified

### Technical Details
```python
# Correct OAuth2 flow
POST https://portail-api.meteofrance.fr/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(client_id:client_secret)

Body: grant_type=client_credentials
```

### Environment Variables
```bash
# Required in .env
METEOFRANCE_CLIENT_ID=your_client_id
METEOFRANCE_CLIENT_SECRET=your_client_secret

# Deprecated (remove)
# METEOFRANCE_APPLICATION_ID=...
```

## WMS/WCS Time Handling Best Practices

### ❌ Common Mistake
```python
# WRONG - Using arbitrary time
params["time"] = "2024-01-15T18:00:00Z"  # May not exist in API
```

### ✅ Correct Approach
```python
# RIGHT - Always use valid times from GetCapabilities
from src.wetter.fetch_arome_wcs import get_available_wms_times

available_times = get_available_wms_times(token)
if available_times:
    latest_time = available_times[-1]  # Most recent forecast
    params["time"] = latest_time
```

### Utility Function
```python
def get_available_wms_times(token):
    """
    Fetch available WMS times from GetCapabilities.
    Args:
        token (str): OAuth2 access token
    Returns:
        list[str]: List of ISO8601 time strings
    Raises:
        RuntimeError: If the GetCapabilities request fails
    """
```

## API Status Summary

| API | Status | OAuth2 | Notes |
|-----|--------|--------|-------|
| **WCS** | ✅ Working | ✅ | GetCapabilities, GetCoverage work |
| **Vigilance** | ✅ Working | ✅ | Warning data available |
| **WMS** | ⚠️ Complex | ✅ | Requires valid time from GetCapabilities |

## Error Handling Patterns

### OAuth2 Errors
```python
if not client_id or not client_secret:
    raise RuntimeError("OAuth2 credentials missing")
```

### WMS Time Errors
```python
if not available_times:
    print("❌ Could not get available WMS times. No WMS request sent.")
    return
```

## Testing
- **Unit Tests**: `tests/test_oauth2_client_credentials.py`
- **Live Tests**: `tests/test_live_oauth2_token.py`
- **Integration**: `scripts/demo_bustanico_simple.py`

## Migration Checklist
- [x] Remove `METEOFRANCE_APPLICATION_ID` usage
- [x] Update environment variables
- [x] Implement OAuth2 Client Credentials
- [x] Add robust WMS time handling
- [x] Update all tests
- [x] Document best practices

## Future Considerations
- Cache WMS time values to reduce GetCapabilities calls
- Implement automatic token refresh
- Add monitoring for API rate limits 