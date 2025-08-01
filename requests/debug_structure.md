# .cursor/rules/debug_structure.md

# Debug-Strukturregel: Rohdatenvisualisierung je API-Quelle

## Ziel

Die Debug-Ausgabe muss die zugrunde liegenden Wetter-Rohdaten strukturiert und verständlich darstellen – getrennt nach API-Endpunkt, Substruktur, GEO-Position und Zeitbezug. Ziel ist es, für jede Risikoanalyse eine nachvollziehbare Übersicht der genutzten Rohdaten zu erhalten.

## Struktur der Ausgabe

### 1. Kopfbereich je Abschnitt

Jeder Abschnitt beginnt mit einer Überschrift im folgenden Format:

```
Datenquelle: meteo_france / Substruktur: forecast
Position: 42.25421, 8.92553
Datum: 2025-07-30
```

Falls mehrere Positionen verwendet wurden, wird je Position ein separater Block erzeugt (siehe Beispiel unten).

---

### 2. Tabellenformat

#### `forecast` (Stündlich)

| Uhrzeit | temperature | wind_speed | gusts | rain | icon | condition           | thunderstorm |
|---------|-------------|------------|-------|------|------|---------------------|--------------|
| 06:00   | 10.2 °C     | 3 km/h     | 8 km/h| 0.0mm| p01j | Ciel clair          | false        |

#### `daily_forecast` (Täglich)

| Tag        | temp_min | temp_max | rain_sum | wind_gust_max | uv_index |
|------------|----------|----------|----------|----------------|----------|
| 2025-07-30 | 8.9 °C   | 17.6 °C  | 12.2 mm  | 43 km/h        | 7        |

#### `probability_forecast` (3h-Auflösung)

| Uhrzeit | rain_3h | snow_3h | freezing_rain_3h | storm_3h |
|---------|---------|---------|------------------|----------|
| 06:00   | 10 %    | -       | -                | 0 %      |

#### `rain` (Minütlich)

| Uhrzeit | rain_mm | rain_intensity |
|---------|---------|----------------|
| 12:00   | 0.2mm   | schwach        |
| 12:01   | 0.4mm   | moderat        |
| 12:02   | 1.2mm   | stark          |

> Hinweis: `get_rain()` ist nur verfügbar, wenn explizit aktiviert. Minutendaten sind je Position zu aggregieren oder als Einzelwert darstellbar.

#### `alerts` (regional, kategorisiert)

| Phänomen       | Stufe  | Farbe   | Beginn     | Ende       | Beschreibung (optional)        |
|----------------|--------|---------|------------|------------|---------------------------------|
| Gewitter       | 3      | orange  | 2025-07-30 16:00 | 2025-07-30 23:00 | Lokale Gewitter mit Starkregen |
| Hitze          | 2      | gelb    | 2025-07-31 10:00 | 2025-08-01 18:00 | Warnung vor Hitzebelastung     |

---

### 3. Darstellung bei mehreren GEO-Positionen

Wenn z. B. vier Positionen entlang einer Etappe ausgewertet werden, wird für jede Position ein Abschnitt wie folgt erzeugt:

```
Datenquelle: meteo_france / Substruktur: forecast
Position: 42.28647, 8.89356
Datum: 2025-07-30

| Uhrzeit | temperature | wind_speed | gusts | rain | icon | condition | thunderstorm |
|---------|-------------|------------|-------|------|------|-----------|--------------|
| 06:00   | 11.2 °C     | 2 km/h     | 5 km/h| 0.0mm| p01j | Ensoleillé| false        |
...
```

Danach folgt dieselbe Darstellung für:

```
Position: 42.25421, 8.92553
Position: 42.22935, 8.97768
Position: 42.22026, 8.98073
```

---

### 4. Formatierung

- Alle Daten im **Monospace-Block**
- Alle numerischen Angaben mit Einheit (°C, mm, km/h, %)
- Fehlende Daten mit `-` markieren
- Keine Bewertungen oder Ableitungen im Debug-Bereich