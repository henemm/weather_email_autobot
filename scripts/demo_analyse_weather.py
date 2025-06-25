import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logic.analyse_weather import analyze_weather_data
from model.risks import default_thresholds
from wetter.fetch_arome import fetch_arome
from wetter.fetch_vigilance import fetch_warnings

# Position südlich Monte Cinto
lat, lon = 42.308, 8.937

# Abrufen
weather = fetch_arome(lat, lon)
alerts = fetch_warnings(lat, lon)

# Analyse
analysis = analyze_weather_data(weather, config=default_thresholds)

print("RISIKEN:")
for risk in analysis.risks:
    print("-", risk)

print("\nZUSAMMENFASSUNG:")
print(analysis.summary)