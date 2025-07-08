# Release Notes: Version 2.1.0 – Dynamic Report Fixes

## Overview

This release addresses critical issues with dynamic report triggering and risk calculation. Version 2.1.0 fixes the problems where dynamic reports were sent with identical weather data and incorrect triggering logic.

## 🚨 Critical Fixes

### Dynamic Report Triggering Logic
- **Fixed Delta Thresholds**: Dynamic reports now properly use `delta_thresholds` from `config.yaml` instead of hardcoded values
- **Fixed Time Interval**: `min_interval_min` is now correctly read from the root level of `config.yaml`
- **Proper Risk Calculation**: Risk scores are now calculated per stage instead of globally
- **Stage-Specific Triggers**: Dynamic reports are now triggered based on stage-specific weather changes

### Risk Calculation Per Stage
- **Per-Stage Risk**: Risk scores are now computed using stage-specific weather data instead of global maxima
- **Consistent Data**: Email body and risk calculation now use the same stage-specific data
- **Accurate Triggers**: Dynamic reports are triggered only when the specific stage's weather changes significantly

## 🔧 Technical Improvements

### Configuration Handling
- **Delta Thresholds**: Now properly reads and applies `delta_thresholds` from config:
  ```yaml
  delta_thresholds:
    rain_probability: 10.0
    temperature: 2.0
    thunderstorm_probability: 10.0
    wind_speed: 5.0
  ```
- **Time Intervals**: Correctly reads `min_interval_min` from root level config
- **Daily Limits**: Properly enforces `max_daily_reports` limit

### Risk Computation
- **Stage-Specific Metrics**: Risk is computed using the current stage's weather data
- **Consistent Data Source**: Both risk calculation and email generation use the same data source
- **Accurate Changes**: Risk changes are now truly stage-specific

## ✅ Quality Assurance

### Testing
- **Dynamic Report Tests**: All dynamic report triggering tests pass
- **Configuration Tests**: Delta thresholds and time intervals work correctly
- **Risk Calculation Tests**: Stage-specific risk calculation verified
- **Integration Tests**: Complete workflow tested end-to-end

### Data Accuracy
- **Stage-Specific Values**: Each stage now has its own risk score and weather data
- **Proper Triggers**: Dynamic reports only trigger when stage-specific thresholds are exceeded
- **Time Compliance**: Minimum intervals between reports are properly enforced

## 🔁 Architecture Changes

### Risk Calculation Flow
- **Before**: Global weather analysis → Global risk score → Dynamic trigger
- **After**: Stage-specific weather data → Stage-specific risk score → Stage-specific trigger

### Dynamic Report Logic
- **Before**: Hardcoded 30% risk threshold, ignored config values
- **After**: Uses `delta_thresholds` from config, proper time interval enforcement

## Breaking Changes

### Configuration
- No breaking changes to existing configuration
- All existing `config.yaml` files remain compatible
- Enhanced logging shows more detailed risk calculation information

### Behavior Changes
- **Dynamic reports will be less frequent** due to proper threshold enforcement
- **Risk scores will vary by stage** instead of being identical
- **Time intervals will be properly enforced** (60 minutes minimum)

## Migration Guide

### For Existing Users
- **No Migration Required**: All existing configurations remain valid
- **Automatic Improvements**: Dynamic reports will work correctly with existing config
- **Better Accuracy**: Reports will now reflect actual stage-specific conditions

### For New Users
1. Configure `delta_thresholds` in `config.yaml` as needed
2. Set `min_interval_min` and `max_daily_reports` at root level
3. Dynamic reports will trigger based on actual weather changes

## Known Issues

- None identified in this release

## Future Roadmap

- Enhanced weather model integration
- Extended route support beyond GR20
- Additional notification channels
- Advanced weather analytics

## Support

For issues and questions related to this release, please refer to the project documentation or create an issue in the repository.

---

**Release Date**: July 2025  
**Compatibility**: Python 3.8+, All major operating systems  
**License**: Project-specific license

## Technical Details

- **Commit Base**: Latest state with dynamic report fixes
- **Branch**: `main`
- **Tag**: `v2.1.0`
- **Release Name**: `Version 2.1.0 – Dynamic Report Fixes`
- **Release Type**: Minor Release with critical fixes

## Fix Summary

### Fixed Issues:
1. **Dynamic reports triggered with identical weather data** - Now stage-specific
2. **Delta thresholds ignored** - Now properly used from config
3. **Time intervals not enforced** - Now properly enforced
4. **Global risk calculation** - Now per-stage calculation
5. **Inconsistent data sources** - Now unified stage-specific data

### Impact:
- **More accurate dynamic reports** based on actual stage-specific changes
- **Proper threshold enforcement** using configured values
- **Correct time interval compliance** preventing spam
- **Stage-specific risk assessment** instead of global assessment 