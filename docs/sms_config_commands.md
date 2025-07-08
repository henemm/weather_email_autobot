# SMS Configuration Commands

## Overview

The SMS Configuration Commands feature allows dynamic updates to the `config.yaml` file through incoming SMS messages. This enables remote configuration changes without direct access to the server.

## Architecture

The system consists of three main components:

1. **SMS Config Processor** (`src/config/sms_config_processor.py`)
   - Validates and processes SMS commands
   - Updates configuration file
   - Logs all changes

2. **SMS Webhook Handler** (`src/notification/sms_webhook_handler.py`)
   - Processes incoming webhooks from SMS providers
   - Routes configuration commands to the processor
   - Supports multiple providers (seven.io, Twilio)

3. **SMS Webhook Server** (`src/notification/sms_webhook_server.py`)
   - Flask-based HTTP server
   - Receives webhooks from SMS providers
   - Provides health check and monitoring endpoints

## Command Format

### Syntax
```
### <key>: <value>
```

### Examples
```
### thresholds.temperature: 25.0
### startdatum: 2025-07-08
### sms.test_number: +4915158450319
### max_daily_reports: 5
```

### Requirements
- Command must start with `### ` (three hash symbols followed by space)
- Key and value must be separated by `: ` (colon followed by space)
- Key must be in the whitelist
- Value must match the expected data type

## Supported Configuration Keys

### Whitelist
Only the following configuration keys can be modified via SMS:

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `startdatum` | Date (YYYY-MM-DD) | Start date for report generation | `2025-07-08` |
| `sms.production_number` | Phone Number | Production SMS recipient | `+4917717816897` |
| `sms.test_number` | Phone Number | Test SMS recipient | `+4915158450319` |
| `thresholds.cloud_cover` | Float | Cloud cover threshold (%) | `90.0` |
| `thresholds.rain_amount` | Float | Rain amount threshold (mm) | `0.5` |
| `thresholds.rain_probability` | Float | Rain probability threshold (%) | `10.0` |
| `thresholds.temperature` | Float | Temperature threshold (°C) | `30.0` |
| `thresholds.thunderstorm_probability` | Float | Thunderstorm probability threshold (%) | `10.0` |
| `thresholds.wind_speed` | Float | Wind speed threshold (km/h) | `40.0` |
| `delta_thresholds.rain_probability` | Float | Delta rain probability threshold | `1.0` |
| `delta_thresholds.temperature` | Float | Delta temperature threshold | `1.0` |
| `delta_thresholds.thunderstorm_probability` | Float | Delta thunderstorm probability threshold | `1.0` |
| `delta_thresholds.wind_speed` | Float | Delta wind speed threshold | `1.0` |
| `max_daily_reports` | Integer | Maximum daily reports | `3` |
| `min_interval_min` | Integer | Minimum interval between reports (minutes) | `60` |

## Data Type Validation

### Date Format
- Must be in `YYYY-MM-DD` format
- Example: `2025-07-08`
- Invalid: `2025/07/08`, `07-08-2025`

### Phone Number Format
- Must start with `+` followed by digits
- Example: `+49123456789`
- Invalid: `49123456789`, `+49-123-456-789`

### Float Values
- Can be integer or decimal
- Examples: `25.0`, `25`, `10.5`
- Invalid: `invalid`, `25.5.5`

### Integer Values
- Must be whole numbers
- Examples: `3`, `60`, `100`
- Invalid: `3.5`, `invalid`

## Security Features

### Whitelist Protection
- Only predefined configuration keys can be modified
- Prevents unauthorized access to sensitive settings
- No access to API keys, SMTP settings, or file paths

### Type Validation
- All values are validated against expected data types
- Prevents configuration corruption
- Ensures data integrity

### Logging
- All configuration changes are logged to `logs/sms_config_updates.log`
- Webhook receptions are logged to `logs/sms_webhook_receptions.log`
- Audit trail for all modifications

## Usage

### Manual Execution
```bash
# Basic usage
python scripts/check_sms_commands.py

# With debug logging
python scripts/check_sms_commands.py --log-level DEBUG

# Custom configuration file
python scripts/check_sms_commands.py --config custom_config.yaml

# Cleanup old processed messages
python scripts/check_sms_commands.py --cleanup
```

### Scheduled Execution (Cron Job)
```bash
# Add to crontab (every 10 minutes)
*/10 * * * * cd /opt/weather_email_autobot && python scripts/check_sms_commands.py

# Or every 5 minutes for faster response
*/5 * * * * cd /opt/weather_email_autobot && python scripts/check_sms_commands.py
```

### Testing the Functionality
```bash
# Run test suite
python scripts/test_sms_config_commands.py
```

## Error Handling

### Invalid Commands
- Commands not starting with `### ` are ignored
- Missing colon separators return error
- Empty values return error

### Validation Errors
- Keys not in whitelist return error
- Invalid data types return error
- Malformed values return error

### System Errors
- File I/O errors are logged and reported
- YAML parsing errors are handled gracefully
- Network errors are logged

## Log Files

### Configuration Updates Log
File: `logs/sms_config_updates.log`
Format: `timestamp | key | value | SUCCESS/FAILED | message`

Example:
```
2025-01-27 10:30:00 | thresholds.temperature | 25.0 | SUCCESS | Configuration updated successfully
2025-01-27 10:31:00 | invalid.key | invalid | FAILED | INVALID FORMAT: Key 'invalid.key' not in whitelist
```

### Webhook Receptions Log
File: `logs/sms_webhook_receptions.log`
Format: `timestamp | provider | sender -> recipient | message_text | additional_info`

Example:
```
2025-01-27 10:30:00 | seven | +49987654321 -> +49123456789 | ### thresholds.temperature: 25.0 | Received message: ### thresholds.temperature: 25.0...
```

## Integration with SMS Providers

### Seven.io Setup
1. Ensure you have a valid API key from seven.io
2. Configure the API key in your `.env` file: `SEVEN_API_KEY=your_api_key`
3. Set up a cron job to regularly check for incoming SMS
4. No webhook configuration required

### Twilio Setup
*Note: Twilio support is not implemented in the polling architecture. Only Seven.io is supported.*

## Monitoring and Health Checks

### Check Log Files
```bash
# Monitor SMS polling activity
tail -f logs/sms_polling.log

# Check configuration updates
tail -f logs/sms_config_updates.log

# Check last execution
grep "SMS polling completed" logs/sms_polling.log | tail -1
```

### Manual Health Check
```bash
# Run a manual check
python scripts/check_sms_commands.py --log-level INFO
```

## Troubleshooting

### Common Issues

1. **No messages found**
   - Check API key is valid and configured
   - Verify Seven.io account status
   - Check log files for API errors

2. **Configuration not updated**
   - Check command format (must start with `### `)
   - Verify key is in whitelist
   - Check value data type

3. **Cron job not working**
   - Check cron job is properly configured
   - Verify Python path and permissions
   - Check cron logs for errors

### Debug Mode
Enable debug mode for detailed logging:
```bash
python scripts/check_sms_commands.py --log-level DEBUG
```

## Security Considerations

1. **API Key Security**
   - Store API keys in environment variables
   - Never commit API keys to version control
   - Use separate API keys for test and production



2. **Access Control**
   - Only whitelisted keys can be modified
   - No access to sensitive configuration
   - All changes are logged

3. **Data Validation**
   - Strict type checking
   - Format validation for all data types
   - Error handling for malformed data

## Future Enhancements

1. **Authentication**
   - API key validation
   - IP whitelisting
   - Request signing

2. **Additional Providers**
   - Support for more SMS providers
   - Custom webhook formats

3. **Advanced Features**
   - Bulk configuration updates
   - Configuration templates
   - Rollback functionality 