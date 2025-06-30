# Release Notes: Version 1.1.1 – SMS & Stabilität

## Overview

This release marks a significant milestone in the weather email autobot project, introducing SMS functionality and improving overall system stability. Version 1.1.1 contains all tested and production-ready features up to and including the modularized SMS delivery with seven.io.

## 🔧 New: SMS Delivery

### SMS Integration with seven.io
- **First SMS Provider**: Integration of `seven.io` as the primary SMS provider
- **Configuration**: SMS settings configurable via `config.yaml`
- **International Support**: Full support for international destination numbers (e.g., +49...)
- **Logging**: Comprehensive send logs with proper error handling
- **Format Consistency**: SMS format identical to email output (InReach-compatible)

### Technical Implementation
- Modular SMS client architecture
- Provider factory pattern for easy extension
- Unified report generation for both email and SMS
- Robust error handling and retry mechanisms

## ✅ Improvements

### Weather Analysis Enhancements
- **Thunderstorm Logic**: Complete overhaul of thunderstorm and rain logic
- **Validation Framework**: Enhanced with dummy data for test runs
- **API Integration**: `meteofrance-api` fully replaces raw AROME access
- **Dynamic Risk Monitor**: Robust rule-based operation across all monitoring stages
- **Logging**: Differentiated logging between email, SMS, and analysis operations

### System Architecture
- **Report Separation**: Evening/Morning/Day reports tested independently
- **Configurable Thresholds**: All thresholds configurable via `config.yaml`
- **Warning Logic**: Aggregated warning logic across all stage points

## 🔁 Structure

### Modular Design
- **SMS Provider System**: Extensible provider architecture
- **Unified Reporting**: Centralized report generation for all output formats
- **Configuration Management**: Centralized configuration with environment variable support

### Testing & Validation
- **Comprehensive Test Suite**: Full test coverage for all new features
- **Integration Tests**: End-to-end testing for complete workflows
- **Validation Framework**: Dummy data support for reliable testing

## Technical Details

- **Commit Base**: Latest state before Twilio or other provider integration
- **Branch**: `main` (merged from `remove-arome-hr-agg`)
- **Tag**: `v1.1.1`
- **Release Name**: `Version 1.1.1 – SMS & Stabilität`
- **Release Type**: GitHub Release with comprehensive change log

## Breaking Changes

None. This release maintains full backward compatibility with existing email functionality.

## Migration Guide

### For Existing Users
- No migration required for email functionality
- SMS functionality is opt-in via configuration
- Existing `config.yaml` files remain compatible

### For New SMS Users
1. Add SMS configuration to `config.yaml`:
   ```yaml
   sms:
     provider: seven
     api_key: your_seven_api_key
     default_recipient: +49123456789
   ```
2. Configure recipient numbers as needed
3. Test SMS delivery with validation framework

## Known Issues

- None identified in this release

## Future Roadmap

- Additional SMS providers (Twilio, etc.)
- Enhanced weather model integration
- Extended route support beyond GR20

## Support

For issues and questions related to this release, please refer to the project documentation or create an issue in the repository.

---

**Release Date**: January 2025  
**Compatibility**: Python 3.8+, All major operating systems  
**License**: Project-specific license 