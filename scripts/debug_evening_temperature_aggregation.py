import sys
import os
import yaml
import json
from datetime import date, timedelta, datetime as dt
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config_loader import load_config
from src.wetter.weather_data_processor import WeatherDataProcessor
from src.position.etappenlogik import get_current_stage, get_stage_coordinates

ETAPPEN_PATH = os.path.join(os.path.dirname(__file__), '../etappen.json')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config.yaml')

# Load all stages
with open(ETAPPEN_PATH, 'r', encoding='utf-8') as f:
    etappen = json.load(f)

# Load config
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Save original start date
original_start = config.get('startdatum')

print(f"{'Stage':<18} | {'Date':<10} | {'Raw Temps'} | {'Max Temp'} | {'Raw Regen'} | {'Max Regen'} | {'Raw RegenW'} | {'Max RegenW'}")
print("-" * 140)

for idx, stage in enumerate(etappen):
    today = date.today()
    stage_start = today - timedelta(days=idx)
    config['startdatum'] = stage_start.strftime('%Y-%m-%d')
    # Save config
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f)
    # Reload config and get current stage
    config_reload = load_config()
    current_stage = get_current_stage(config_reload, ETAPPEN_PATH)
    stage_name = current_stage['name'] if current_stage else 'Unknown'
    coords = get_stage_coordinates(current_stage) if current_stage else []
    tomorrow = today + timedelta(days=1)
    processor = WeatherDataProcessor(config_reload)
    raw_temps_all_points = []
    max_temps = []
    raw_regen_all_points = []
    max_regen = []
    raw_regenw_all_points = []
    max_regenw = []
    for lat, lon in coords:
        try:
            result = processor._calculate_weather_data_for_day(lat, lon, stage_name, tomorrow, 5, 17, return_raw=True)
            raw_temps = result.get('raw_temperatures', [])
            max_temp = result.get('max_temperature', None)
            raw_temps_all_points.append(raw_temps)
            max_temps.append(max_temp)
            # Regen (precipitation amount)
            # RegenW (rain probability)
            # We need to extract these from the time_points, so we repeat the extraction here
            client = processor
            # Re-extract all values for this point
            # (We could refactor to return all raw values, but for now, re-extract)
            # Use the same logic as in _calculate_weather_data_for_day
            from meteofrance_api.client import MeteoFranceClient
            mf_client = MeteoFranceClient()
            forecast = mf_client.get_forecast(lat, lon)
            raw_regen = []
            raw_regenw = []
            if forecast and forecast.forecast:
                for entry in forecast.forecast:
                    dt_timestamp = entry.get('dt')
                    if not dt_timestamp:
                        continue
                    entry_datetime = dt.fromtimestamp(dt_timestamp)
                    entry_date = entry_datetime.date()
                    hour = entry_datetime.hour
                    if entry_date == tomorrow and 5 <= hour <= 17:
                        # Regen
                        precipitation_amount = processor._extract_precipitation_amount(entry)
                        if precipitation_amount is not None:
                            raw_regen.append(precipitation_amount)
                        # RegenW
                        precipitation_probability = entry.get('precipitation_probability')
                        rain_prob = None
                        if precipitation_probability is not None:
                            rain_prob = float(precipitation_probability)
                        else:
                            # Try to estimate rain probability
                            weather_condition = processor._extract_weather_condition(entry)
                            rain_prob = processor._determine_rain_probability(weather_condition, precipitation_probability, precipitation_amount)
                        if rain_prob is not None:
                            raw_regenw.append(rain_prob)
            max_regen.append(max(raw_regen) if raw_regen else None)
            max_regenw.append(max(raw_regenw) if raw_regenw else None)
            raw_regen_all_points.append(raw_regen)
            raw_regenw_all_points.append(raw_regenw)
        except Exception as e:
            raw_temps_all_points.append([f"ERROR: {e}"])
            max_temps.append(None)
            raw_regen_all_points.append([f"ERROR: {e}"])
            max_regen.append(None)
            raw_regenw_all_points.append([f"ERROR: {e}"])
            max_regenw.append(None)
    # Flatten all raw values for all points
    flat_raw_temps = [t for sub in raw_temps_all_points for t in sub if isinstance(t, (int, float))]
    agg_max_temp = max([t for t in max_temps if t is not None], default=None)
    flat_raw_regen = [r for sub in raw_regen_all_points for r in sub if isinstance(r, (int, float))]
    agg_max_regen = max([r for r in max_regen if r is not None], default=None)
    flat_raw_regenw = [w for sub in raw_regenw_all_points for w in sub if isinstance(w, (int, float))]
    agg_max_regenw = max([w for w in max_regenw if w is not None], default=None)
    print(f"{stage_name:<18} | {stage_start} | {flat_raw_temps} | {agg_max_temp} | {flat_raw_regen} | {agg_max_regen} | {flat_raw_regenw} | {agg_max_regenw}")

# Restore original config
if original_start:
    config['startdatum'] = original_start
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f)
print("Debugging complete.") 