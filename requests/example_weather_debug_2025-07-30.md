# debug/example_weather_debug_2025-07-30.md

## DEBUG DATENEXPORT – Rohdatenübersicht MeteoFrance

Ziel: Vollständige und nachvollziehbare Darstellung der verwendeten Rohdaten aus der MeteoFrance API zur Risikobewertung am 2025-07-30

---

## Datenquelle: meteo_france / Substruktur: forecast
Position: 42.28647, 8.89356
Datum: 2025-07-30

| Uhrzeit | temperature | wind_speed | gusts | rain | icon | condition     | thunderstorm |
|---------|-------------|------------|-------|------|------|----------------|--------------|
| 04:00   | 9.7 °C      | 2 km/h     | 0 km/h| 0.0mm| p01n | Ciel clair     | false        |
| 06:00   | 9.6 °C      | 2 km/h     | 0 km/h| 0.0mm| p01n | Ciel clair     | false        |
| 12:00   | 18.1 °C     | 3 km/h     | 12 km/h| 0.0mm| p02j | Ensoleillé     | false        |
| 17:00   | 17.0 °C     | 4 km/h     | 14 km/h| 0.0mm| p03j | Peu nuageux    | false        |

---

## Datenquelle: meteo_france / Substruktur: daily_forecast
Position: 42.28647, 8.89356
Datum: 2025-07-30

| Tag        | temp_min | temp_max | rain_sum | wind_gust_max | uv_index |
|------------|----------|----------|----------|----------------|----------|
| 2025-07-30 | 8.9 °C   | 17.6 °C  | 1.2 mm   | 14 km/h        | 6        |

---

## Datenquelle: meteo_france / Substruktur: probability_forecast
Position: 42.28647, 8.89356
Datum: 2025-07-30

| Uhrzeit | rain_3h | snow_3h | freezing_rain_3h | storm_3h |
|---------|---------|---------|------------------|----------|
| 06:00   | -       | -       | -                | -        |
| 12:00   | -       | -       | -                | -        |
| 15:00   | -       | -       | -                | -        |

---

## Datenquelle: meteo_france / Substruktur: rain (minütlich)
Position: 42.28647, 8.89356
Datum: 2025-07-30

| Uhrzeit | rain_mm | rain_intensity |
|---------|---------|----------------|
| 12:00   | 0.0mm   | -              |
| 12:01   | 0.0mm   | -              |
| 12:02   | 0.1mm   | leicht         |

---

## Datenquelle: meteo_france / Substruktur: alerts (regional)
Region: Haute-Corse
Datum: 2025-07-30

| Phänomen   | Stufe | Farbe  | Beginn           | Ende             | Beschreibung                      |
|------------|-------|--------|------------------|------------------|-----------------------------------|
| Gewitter   | 3     | orange | 2025-07-30 14:00 | 2025-07-30 22:00 | Lokale Gewitter mit Starkregen   |
| Wind       | 2     | gelb   | 2025-07-30 12:00 | 2025-07-30 20:00 | Böen bis 60 km/h                 |

---

## Weitere Positionen

Die gleichen Datenformate sind für folgende Positionen verfügbar und müssen entsprechend der Struktur oben ausgegeben werden:

- 42.25421, 8.92553
- 42.22935, 8.97768
- 42.22026, 8.98073

Jeweils mit gleichen Tabellenfeldern und -aufbau wie oben.