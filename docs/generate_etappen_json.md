# GPX to etappen.json Converter

## Overview

The `generate_etappen_json.py` script converts GPX track files into a structured JSON format (`etappen.json`) that is used by the GR20 weather monitoring system. It intelligently selects key waypoints from each stage including start points, high points, and intermediate points to ensure comprehensive weather coverage along the route.

## Purpose

This script addresses the need to convert raw GPX track data into a format that:
- Provides optimal weather monitoring points for each stage
- Reduces data complexity while maintaining route coverage
- Ensures consistent JSON structure for the weather system

## Features

### Intelligent Waypoint Selection
- **Start and End Points**: Always included for each stage
- **High Points**: Automatically identifies the highest elevation points (minimum 1km from start/end)
- **Intermediate Points**: Adds points to fill gaps larger than 8km
- **Duplicate Removal**: Eliminates redundant coordinates

### Smart Filtering
- Minimum distance between points (5km default)
- Maximum gap filling (8km default)
- Elevation-based prioritization for high points
- Route order preservation

## Usage

### Basic Usage
```bash
python generate_etappen_json.py --input-dir input_gpx/ --output etappen.json
```

### Parameters
- `--input-dir`: Directory containing GPX files (required)
- `--output`: Output JSON file (default: `etappen.json`)

### Example
```bash
# Convert GPX files from input_gpx directory
python generate_etappen_json.py --input-dir input_gpx/

# Specify custom output file
python generate_etappen_json.py --input-dir input_gpx/ --output custom_etappen.json
```

## Input Requirements

### GPX File Naming
Files should be named with stage numbers for proper ordering:
- `Etappe 1.gpx`
- `Etappe 2.gpx`
- `Etappe 3.gpx`
- etc.

### GPX File Structure
Each GPX file should contain:
- Track segments with waypoints
- Latitude, longitude, and elevation data
- Proper GPX format (version 1.1)

## Output Format

The script generates a JSON file with the following structure:

```json
[
  {
    "name": "Etappe 1.gpx",
    "punkte": [
      {"lat": 42.123456, "lon": 9.123456},
      {"lat": 42.234567, "lon": 9.234567},
      {"lat": 42.345678, "lon": 9.345678}
    ]
  },
  {
    "name": "Etappe 2.gpx",
    "punkte": [
      {"lat": 42.456789, "lon": 9.456789},
      {"lat": 42.567890, "lon": 9.567890}
    ]
  }
]
```

## Algorithm Details

### Waypoint Selection Process
1. **Extract all points** from GPX file
2. **Identify candidates** for intermediate points (excluding start/end)
3. **Sort by elevation** to find high points
4. **Apply distance filters** to ensure minimum spacing
5. **Fill large gaps** with midpoint interpolation
6. **Remove duplicates** based on coordinate precision
7. **Preserve route order** for final output

### Distance Calculations
- Uses geodesic distance calculation via `geopy.distance`
- Accounts for Earth's curvature
- Provides accurate kilometer measurements

## Dependencies

Required Python packages:
- `gpxpy`: GPX file parsing
- `geopy`: Distance calculations
- Standard library: `argparse`, `json`, `logging`, `os`, `pathlib`, `re`, `typing`

## Integration with Weather System

The generated `etappen.json` file is used by:
- `src/position/etappenlogik.py`: Determines current stage based on date
- Weather monitoring scripts: Provides coordinates for weather data collection
- Email generation: Includes stage names in weather reports

## Error Handling

- **File not found**: Script exits with error message
- **Invalid GPX**: Logs warning and continues with available data
- **Empty files**: Handled gracefully with fallback behavior
- **Missing elevation**: Uses 0.0 as default elevation

## Best Practices

1. **Backup original GPX files** before processing
2. **Verify output** by checking generated JSON structure
3. **Test with sample data** before processing full route
4. **Review waypoint selection** for optimal weather coverage
5. **Update etappen.json** when route changes occur

## Troubleshooting

### Common Issues
- **No GPX files found**: Check input directory path and file extensions
- **Incorrect stage ordering**: Ensure GPX files are named with stage numbers
- **Missing waypoints**: Verify GPX files contain valid track data
- **Large output files**: Adjust distance parameters if too many points generated

### Debug Mode
Enable detailed logging by modifying the script:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Version History

- **v1.0**: Initial implementation with basic waypoint selection
- **v1.1**: Added intelligent gap filling and duplicate removal
- **v1.2**: Improved elevation-based prioritization
- **v1.3**: Enhanced error handling and logging 