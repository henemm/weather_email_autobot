from meteofrance_api.client import MeteoFranceClient
import json
from datetime import datetime

lat, lon = 42.40341, 8.92205
client = MeteoFranceClient()
forecast = client.get_forecast(lat, lon)
print(f'Forecast count: {len(forecast.forecast)}')
for entry in forecast.forecast:
    dt = entry.get('dt')
    if not dt:
        continue
    entry_datetime = datetime.fromtimestamp(dt)
    if entry_datetime.date().isoformat() == '2025-07-11':
        print(json.dumps(entry, indent=2, ensure_ascii=False)) 