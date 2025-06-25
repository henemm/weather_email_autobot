# Garmin MapShare Message Sender

This module provides functionality to send messages to Garmin inReach devices via the MapShare web interface.

## ⚠️ Important Legal Notice

**This software is for experimental and technical testing purposes only.**

- No production use is intended
- No sensitive data should be sent
- This is not an official Garmin API
- Usage is purely experimental
- The software must fail gracefully if Garmin blocks the sending

## Features

- Send messages to Garmin inReach devices via MapShare web interface
- Configuration via JSON file or environment variables
- Automatic retry logic (3 attempts with 1-second delays)
- Proper HTTP headers to mimic browser requests
- Comprehensive error handling
- Integration-ready for weather alert systems

## Installation

The module requires the `requests` library:

```bash
pip install requests
```

## Configuration

### Method 1: JSON Configuration File

Create a configuration file (e.g., `config.json`):

```json
{
  "extId": "08ddb09d-0e47-974a-6045-bd7ce0170000",
  "adr": "henningemmrich@icloud.com",
  "message_text": "⚡️ Gewitterwarnung ab 15 Uhr bei Etappe 5!"
}
```

### Method 2: Environment Variables

Set the following environment variables:

```bash
export MAPSHARE_EXT_ID="08ddb09d-0e47-974a-6045-bd7ce0170000"
export MAPSHARE_ADR="henningemmrich@icloud.com"
export MAPSHARE_MESSAGE="⚡️ Gewitterwarnung ab 15 Uhr bei Etappe 5!"
```

## Usage

### Basic Usage

```python
from src.mapshare_sender.send_mapshare_message import send_mapshare_message

result = send_mapshare_message(
    ext_id="08ddb09d-0e47-974a-6045-bd7ce0170000",
    adr="henningemmrich@icloud.com",
    message_text="⚡️ Gewitterwarnung ab 15 Uhr bei Etappe 5!"
)

print(f"Success: {result.success}")
print(f"Status Code: {result.status_code}")
print(f"Response: {result.response_text}")
```

### Using Configuration Classes

```python
from src.mapshare_sender.send_mapshare_message import MapShareConfig, MapShareSender

# Load from JSON file
config = MapShareConfig.from_file("config.json")

# Or load from environment variables
config = MapShareConfig.from_environment()

# Create sender and send message
sender = MapShareSender(config)
result = sender.send_message()

if result.success:
    print("Message sent successfully!")
else:
    print(f"Failed to send message: {result.response_text}")
```

### Command Line Usage

```bash
python src/mapshare_sender/send_mapshare_message.py \
    "08ddb09d-0e47-974a-6045-bd7ce0170000" \
    "henningemmrich@icloud.com" \
    "⚡️ Gewitterwarnung ab 15 Uhr bei Etappe 5!"
```

## Integration with Weather Alert System

This module can be integrated into the weather email autobot as an alternative to email sending:

```python
from src.mapshare_sender.send_mapshare_message import send_mapshare_message

def send_weather_alert_via_mapshare(alert_message: str) -> bool:
    """
    Send weather alert via Garmin MapShare instead of email.
    
    Args:
        alert_message: The weather alert message to send
        
    Returns:
        True if message was sent successfully, False otherwise
    """
    result = send_mapshare_message(
        ext_id="YOUR_EXT_ID_HERE",
        adr="YOUR_EMAIL_HERE",
        message_text=alert_message
    )
    
    return result.success
```

## Technical Details

### HTTP Request

The module sends a POST request to:
```
https://eur.explore.garmin.com/textmessage/txtmsg
```

With the following data:
```json
{
  "extId": "<EXT_ID>",
  "adr": "<ADR>",
  "txt": "<MESSAGE_TEXT>"
}
```

### Headers

The request includes realistic browser headers:
- User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
- Content-Type: application/x-www-form-urlencoded
- Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8

### Error Handling

- **HTTP 4xx/5xx errors**: Returns failure with status code and response text
- **Network timeouts**: Retries up to 3 times with 1-second delays
- **All retries failed**: Returns failure with error message

## Testing

Run the tests with pytest:

```bash
pytest tests/test_mapshare_sender.py -v
```

## Limitations

- No CAPTCHA bypass
- No DOM scraping or HTML parsing
- No official Garmin API - experimental use only
- Must fail gracefully if Garmin blocks sending
- Limited to text messages only

## Security Considerations

- Never hardcode sensitive credentials
- Use environment variables or secure configuration files
- Monitor for rate limiting or blocking by Garmin
- Log all sending attempts for debugging

## Troubleshooting

### Common Issues

1. **HTTP 400/500 errors**: Check if the extId and adr are correct
2. **Timeout errors**: Check network connectivity
3. **Message not received**: Verify the inReach device is online and configured

### Debug Mode

Enable debug logging by setting the environment variable:
```bash
export PYTHONPATH=.
python -c "
from src.mapshare_sender.send_mapshare_message import send_mapshare_message
result = send_mapshare_message('test', 'test@example.com', 'test')
print(f'Result: {result}')
"
```

## License

This software is provided as-is for experimental purposes only. Use at your own risk. 