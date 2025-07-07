# State Management Documentation

## Overview

The GR20 weather report system uses state management to track report scheduling, dynamic report conditions, and prevent unnecessary duplicate reports.

## Current State Files

### Active State File: `data/gr20_report_state.json`

**Location:** `data/gr20_report_state.json`  
**Used by:** `ReportScheduler` class in `src/logic/report_scheduler.py`  
**Initialized in:** `scripts/run_gr20_weather_monitor.py` (hardcoded path)

**Purpose:**
- Tracks last scheduled report time
- Tracks last dynamic report time  
- Counts daily dynamic reports (max 3 per day)
- Stores last risk value for change detection
- Prevents duplicate reports within minimum intervals

**Current State (as of 2025-07-07):**
```json
{
  "last_scheduled_report": "2025-07-07T08:29:53.891279",
  "last_dynamic_report": null,
  "daily_dynamic_report_count": 0,
  "last_risk_value": 0.0,
  "last_report_date": "2025-07-07"
}
```

## Deprecated State File: `data/warning_state.json`

**Location:** `data/warning_state.json`  
**Status:** **DEPRECATED** - Not used in current production workflow  
**Config Entry:** `state_file: data/warning_state.json` (commented out in `config.yaml`)

**Current Content (Legacy):**
```json
{
  "last_check": "2025-06-24T07:10:58.875999",
  "max_thunderstorm_probability": 60.0,
  "max_precipitation": 5.0,
  "max_wind_speed": 50.0,
  "max_temperature": 35.0,
  "max_cloud_cover": 95.0,
  "last_warning_time": null
}
```

**History:**
- Previously used for warning state tracking
- Replaced by `data/gr20_report_state.json` in current architecture
- Config entry remains for backward compatibility but is ignored

**Cleanup Recommendation:**
This file can be safely deleted as it's no longer used by the production system.

## State Management Logic

### Report Scheduling

The `ReportScheduler` class determines when reports should be sent:

1. **Scheduled Reports:** Morning (04:30) and Evening (19:00) reports
2. **Dynamic Reports:** Triggered by significant weather risk changes

### Change Detection

Dynamic reports are triggered when:
- Risk change exceeds threshold (30% by default)
- Minimum interval since last report (60 minutes by default)  
- Daily limit not exceeded (max 3 dynamic reports per day)

### State Persistence

- State is automatically saved after each report
- State file is created if it doesn't exist
- Corrupted state files trigger fresh state creation
- State persists across system restarts

## Configuration

**Current Configuration (in `config.yaml`):**
```yaml
# DEPRECATED - Not used in production
# state_file: data/warning_state.json

delta_thresholds:
  rain_probability: 5.0
  temperature: 1.0
  thunderstorm_probability: 5.0
  wind_speed: 5.0

max_daily_reports: 3
min_interval_min: 60
```

**Note:** The `state_file` config entry is deprecated. The actual state file path is hardcoded in `scripts/run_gr20_weather_monitor.py`.

## Migration Notes

If you need to use a different state file location:

1. **Option 1:** Modify the hardcoded path in `scripts/run_gr20_weather_monitor.py`
2. **Option 2:** Implement config-based state file selection (requires code changes)

## Troubleshooting

**Common Issues:**
- **State file not found:** System creates new state automatically
- **Corrupted state file:** System creates fresh state and logs warning
- **Permission errors:** Check file permissions on `data/` directory

**Debug State:**
```bash
# View current state
cat data/gr20_report_state.json

# Reset state (if needed)
rm data/gr20_report_state.json

# Clean up deprecated state file (optional)
rm data/warning_state.json
```

## Future Improvements

Consider implementing:
- Configurable state file path via `config.yaml`
- State file rotation/backup
- State validation and recovery mechanisms
- Centralized state management for all system components 