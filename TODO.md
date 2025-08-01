# TODO List

## 🔧 Current Tasks

### Morning/Evening Report Refactor
- [x] Implement Night temperature processing
- [x] Implement Day temperature processing  
- [x] Implement Rain (mm) processing
- [x] Implement Rain (%) processing
- [x] Implement Wind processing (analog to Rain)
- [x] Implement Gust processing (analog to Rain)
- [x] Implement Thunderstorm
- [ ] Implement Thunderstorm (+1)
- [ ] Implement Risks
- [ ] Implement Risk Zonal

### 🐛 Known Issues to Fix Later

#### Wind/Gust API Data Issue
- **Problem**: Météo-France Python API returns only 11 km/h gusts for Nantes 2025-08-05, but website shows 40 km/h
- **Location**: `src/weather/core/morning_evening_refactor.py` - `process_wind_data()` and `process_gust_data()`
- **Root Cause**: Using wrong API method or field names within `meteofrance-api` library
- **Investigation Needed**:
  - Check `get_rain()` method for wind data
  - Check `get_warning_full()` method for wind warnings
  - Check `get_observation()` method for current wind data
  - Verify field names (maybe not `gust` but something else)
  - Compare with website data source
- **Status**: Blocked - need to find correct API method/fields

## ✅ Completed Tasks

### Core Implementation
- [x] Create `MorningEveningRefactor` class
- [x] Implement data fetching from `EnhancedMeteoFranceAPI`
- [x] Implement threshold-based processing logic
- [x] Implement result and debug output generation
- [x] Implement persistent storage of aggregated values
- [x] Create test scripts for Wind and Gust positions

### Weather Elements
- [x] Night temperature (daily min)
- [x] Day temperature (daily max) 
- [x] Rain (mm) - hourly data with threshold and time
- [x] Rain (%) - hourly data with threshold and time
- [x] Wind - hourly data with threshold and time (analog to Rain)
- [x] Gust - hourly data with threshold and time (analog to Rain)
- [x] Thunderstorm - hourly data with level mapping (low/med/high) and threshold logic

## 📋 Next Steps

1. **Continue with remaining weather elements**:
   - Thunderstorm (+1) - Same as Thunderstorm but for +1 day
   - Risks - Warning levels from `get_warning_full()`
   - Risk Zonal - GR20 Risk Block API

2. **Fix Wind/Gust API issue** (when time permits):
   - Investigate alternative API methods
   - Find correct field names
   - Verify data accuracy

3. **Testing and validation**:
   - Test all weather elements
   - Validate output format
   - Check threshold logic 