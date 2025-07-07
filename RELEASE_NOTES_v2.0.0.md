# Release Notes: Version 2.0.0 – Fire Risk & Weather Data Fixes

## Overview

This major release addresses critical issues with fire risk warnings and weather data aggregation. Version 2.0.0 introduces significant improvements in data accuracy and reliability, ensuring that weather reports provide stage-specific information rather than identical data across all stages.

## 🚨 Critical Fixes

### Fire Risk Warning System
- **Complete Overhaul**: Fire risk warnings now correctly calculated for all points of each stage
- **Dynamic Coordinate Loading**: Removed hardcoded coordinates, now dynamically loads from `etappen.json`
- **Email Integration**: Fire risk warnings now appear in both email subject and body
- **Multi-Point Aggregation**: Fire risk level calculated across all stage coordinates (max level wins)
- **Zone-Level Processing**: Fire risk warnings processed at zone level rather than massif level

### Weather Data Per Stage
- **Stage-Specific Data**: Each stage now receives its own weather data instead of identical values
- **Removed Hardcoded Values**: Eliminated hardcoded weather values that caused all evening reports to show identical data
- **Dynamic Aggregation**: Weather data properly aggregated per stage coordinates
- **Data Source Integrity**: Maintained dual API approach (MeteoFrance + OpenMeteo) for reliability

## 🔧 Technical Improvements

### Email Formatting
- **Fire Risk in Body**: Added fire risk warnings to email body format according to `email_format.mdc`
- **Consistent Formatting**: All report types (morning, evening, update) now include fire risk warnings
- **Character Count Updates**: Updated character count examples to include fire risk warnings

### Data Processing
- **Coordinate Validation**: Enhanced coordinate loading with proper error handling
- **Stage Index Calculation**: Improved stage index calculation based on start date and current date
- **Weather Data Processor**: Enhanced with better error handling and logging

### Logging & Debugging
- **Email Content Logging**: Added comprehensive logging of generated email content
- **Debug Output**: Enhanced debug output for weather data processing
- **Error Tracking**: Improved error tracking for weather data aggregation

## ✅ Quality Assurance

### Testing
- **Live Email Testing**: All fixes tested with live email delivery
- **Multi-Stage Validation**: Verified different weather data for different stages
- **Fire Risk Validation**: Confirmed fire risk warnings appear correctly for Level 3+ zones
- **Coordinate Validation**: Verified dynamic coordinate loading works for all stages

### Data Accuracy
- **Stage-Specific Values**: Confirmed each stage shows different weather values
- **Fire Risk Accuracy**: Verified fire risk warnings match actual zone data
- **API Reliability**: Maintained dual API approach for maximum reliability

## 🔁 Architecture Changes

### Weather Data Flow
- **Per-Stage Processing**: Weather data now processed individually per stage
- **Coordinate-Based Loading**: Dynamic coordinate loading from `etappen.json`
- **Aggregation Logic**: Improved aggregation logic for multi-point stages

### Email Generation
- **Unified Formatting**: Consistent formatting across all report types
- **Fire Risk Integration**: Seamless integration of fire risk warnings
- **Logging Enhancement**: Comprehensive logging for debugging

## Breaking Changes

### Configuration
- No breaking changes to existing configuration
- All existing `config.yaml` files remain compatible
- Enhanced logging may show more detailed output

### API Usage
- No changes to external API interfaces
- Internal data processing improvements only
- Maintained backward compatibility

## Migration Guide

### For Existing Users
- **No Migration Required**: All existing configurations remain valid
- **Automatic Improvements**: Fire risk warnings and stage-specific data work automatically
- **Enhanced Logging**: More detailed logs available for debugging

### For New Users
1. Configure `config.yaml` as before
2. Fire risk warnings appear automatically for Level 3+ zones
3. Each stage will show its own weather data

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

- **Commit Base**: Latest state with fire risk and weather data fixes
- **Branch**: `main`
- **Tag**: `v2.0.0`
- **Release Name**: `Version 2.0.0 – Fire Risk & Weather Data Fixes`
- **Release Type**: Major Release with critical fixes 