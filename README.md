# 🌤️ GR20 Weather Warning System

Automated weather analysis and alert system for the GR20 long-distance hiking trail in Corsica. Monitors weather conditions, evaluates risks, and sends alerts via satellite communication.

## 🎯 Purpose

This system provides automated weather monitoring and risk assessment for the GR20 trail, automatically sending weather alerts via email through satellite services when dangerous conditions are detected.

## 🏗️ Architecture Overview

### Position Detection
- **ShareMap Integration**: Fetches current position data
- **Stage Mapping**: Maps positions to GR20 trail stages
- **GPS Coordinates**: Provides precise location for weather analysis

### Weather Data Sources
- **Primary**: Météo-France API (6 weather models)
  - AROME_HR: High-resolution hourly forecasts
  - AROME_HR_NOWCAST: 15-minute short-term forecasts
  - AROME_HR_AGG: Aggregated fields (sums, averages)
  - PIAF_NOWCAST: Precipitation nowcasting (5-minute intervals)
  - VIGILANCE_API: Weather warnings by department
- **Fallback**: OpenMeteo Global API (robust backup service)

### Analysis Engine
- **Threshold-based**: Evaluates CAPE, SHEAR, precipitation, and other meteorological parameters
- **Risk Assessment**: Combines multiple weather parameters for comprehensive hazard evaluation
- **Dynamic Thresholds**: Adapts to different weather conditions and trail sections

### Alert Delivery
- **Email Processing**: Gmail SMTP for initial message creation
- **Satellite Relay**: SOTAmāt service for satellite communication
- **Final Delivery**: Garmin InReach devices for hikers on the trail

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Valid API tokens and credentials

### Environment Variables
Create a `.env` file in the project root with the following variables:

```bash
# Email Configuration
GMAIL_APP_PW=your_gmail_app_password

# ShareMap Integration
SHAREMAP_TOKEN=your_sharemap_token

# Météo-France API
METEOFRANCE_WCS_TOKEN=your_meteofrance_token
METEOFRANCE_CLIENT_ID=your_client_id
METEOFRANCE_CLIENT_SECRET=your_client_secret

# Optional: Additional configuration
LOG_LEVEL=INFO
```

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd weather_email_autobot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

4. **Start the weather monitor**
   ```bash
   python scripts/run_gr20_weather_monitor.py
   ```

## 🧪 Testing Strategy

### Running Tests
```bash
# Run all tests
pytest

# Run integration tests only
pytest tests/integration/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_arome_wcs.py
```

### Test Categories
- **Unit Tests**: Individual component testing (`tests/test_*.py`)
- **Integration Tests**: End-to-end workflow testing (`tests/integration/`)
- **Manual Tests**: Interactive testing scripts (`tests/manual/*.py`)
- **Live API Tests**: Real API connectivity verification

### Test Coverage
- Weather data fetching and parsing
- Risk assessment algorithms
- Email formatting and delivery
- Position tracking and mapping
- API authentication and token management

## 🔧 Operations & Monitoring

### Logging
- **Log File**: `logs/warning_monitor.log`
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Rotation**: Automatic log rotation for production

### Production Deployment
For production use, consider:

1. **Systemd Service** (recommended)
   ```bash
   # Create systemd service file
   sudo nano /etc/systemd/system/gr20-weather.service
   
   # Enable and start service
   sudo systemctl enable gr20-weather
   sudo systemctl start gr20-weather
   ```

2. **Cron Jobs**
   ```bash
   # Add to crontab for periodic execution
   */30 * * * * cd /opt/weather_email_autobot && python scripts/run_gr20_weather_monitor.py
   ```

### Health Monitoring
- **Status Reports**: Optional email-based health checks
- **API Connectivity**: Regular verification of weather data sources
- **Alert History**: Track sent alerts and system performance

### Troubleshooting
- Check log files for error messages
- Verify API token validity
- Test network connectivity to external services
- Validate email configuration

## 📁 Project Structure

```
weather_email_autobot/
├── src/                    # Main application code
│   ├── wetter/            # Weather data processing
│   ├── auth/              # Authentication modules
│   ├── logic/             # Business logic
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── integration/       # Integration tests
│   └── manual/           # Manual testing scripts
├── scripts/              # Executable scripts
├── docs/                 # Documentation
└── output/               # Generated reports and data
```

## 🤝 Contributing

1. Follow the existing code style and naming conventions
2. Write tests for new functionality
3. Update documentation as needed
4. Use English for all code, comments, and documentation

## 📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:
- Check the logs for error details
- Review the test suite for usage examples
- Consult the documentation in the `docs/` directory
