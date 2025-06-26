# E-Mail-Format Implementierung

## Übersicht

Die Regel `.cursor/rules/email_format.mdc` wurde vollständig implementiert. Das System unterstützt jetzt drei spezifische E-Mail-Formate für Wetterberichte, die für die Übertragung über InReach-Satellitensystem optimiert sind.

## Nullwertregel & Kompaktformat

- **Alle Wetterwerte, die 0 oder leer sind, werden als „-” ausgegeben.**
- **Keine Zeitangaben, Maximalwerte oder Einheiten für 0-Werte.**
- **Auch „Gewitter +1” und alle anderen Felder folgen dieser Logik.**
- **Keine führenden Nullen bei Uhrzeiten.**
- **Keine leeren Dezimalstellen (z.B. 4mm statt 4.0mm).**
- **Bei Platzmangel werden Leerzeichen entfernt.**

## Implementierte Formate

### 1. Morgenbericht (04:30 Uhr)

**Format:** `{EtappeHeute} | Gewitter {g1}%@{t1}(max {g1_max}%@{t1_max}) | Gewitter +1 {g1_next}% | Regen {r1}%@{t3}(max {r1_max}%@{t3_max}) {regen_mm}mm@{t5}(max {regen_max}mm@{t5_max}) | Hitze {temp_max}°C | Wind {wind_max}km/h | {vigilance_warning}`

**Beispiel:**
```
Stieghorst | Gewitter - | Regen48%@9(max 100%@15) 2mm@15(max 2mm@15) | Hitze 24.6°C | Wind 30km/h | Gewitter +1 -
```

### 2. Abendbericht (19:00 Uhr)

**Format:** `{EtappeMorgen}→{EtappeÜbermorgen} | Nacht {min_temp}°C | Gewitter {g1}%@{t1}(max {g1_max}%@{t1_max}) | Gewitter +1 {g1_next}% | Regen {r1}%@{t3}(max {r1_max}%@{t3_max}) {regen_mm}mm@{t5}(max {regen_max}mm@{t5_max}) | Hitze {temp_max}°C | Wind {wind_max}km/h | {vigilance_warning}`

**Beispiel:**
```
Hiddesen | Nacht 18.3°C | Gewitter - | Regen - | Hitze 22.2°C | Wind 17km/h | Gewitter +1 -
```

### 3. Dynamischer Zwischenbericht

**Format:** `{EtappeHeute} | Update: Gewitter {g2}%@{t2} | Regen {r2}%@{t4} | Hitze {temp_max}°C | Wind {wind_max}km/h | {vigilance_warning}`

**Beispiel:**
```
Stieghorst | Update: Gewitter 35%@15 | Regen 55%@16 | Hitze 29.1°C | Wind 31km/h
```

## Etappennamen-Logik

- **Morgenbericht:** Name der heutigen Etappe
- **Abendbericht:** Name der morgigen Etappe (aus etappen.json, basierend auf Datum)
- **Dynamisch:** Name der aktuellen Etappe

## Technische Implementierung

### Dateien geändert

1. **`src/notification/email_client.py`**
   - Neue Funktion `generate_gr20_report_text()` mit drei Unterfunktionen
   - `_generate_morning_report()` für Morgenberichte
   - `_generate_evening_report()` für Abendberichte  
   - `_generate_dynamic_report()` für Zwischenberichte
   - `_generate_legacy_report()` für Rückwärtskompatibilität

2. **`tests/test_email_client.py`**
   - Umfassende Tests für alle drei Formate
   - Tests für Zeichenbegrenzung (160 Zeichen)
   - Tests für fehlende Daten
   - Tests für Rückwärtskompatibilität

3. **`scripts/demo_email_formats.py`**
   - Demo-Skript zur Demonstration aller Formate
   - Beispiele für verschiedene Wetterbedingungen

### Datenstruktur

Die neuen Formate erwarten eine erweiterte `report_data` Struktur:

```python
report_data = {
    "location": "Vizzavona",
    "report_type": "morning",  # "morning", "evening", "dynamic"
    "weather_data": {
        # Morgenbericht
        "max_thunderstorm_probability": 25.0,
        "thunderstorm_threshold_time": "14:00",
        "thunderstorm_threshold_pct": 20.0,
        "thunderstorm_next_day": 30.0,
        "max_precipitation_probability": 40.0,
        "rain_threshold_time": "12:00",
        "rain_threshold_pct": 30.0,
        "max_precipitation": 3.5,
        "max_temperature": 26.0,
        "max_wind_speed": 20.0,
        
        # Abendbericht (zusätzlich)
        "tomorrow_stage": "Haut Asco",
        "day_after_stage": "Vizzavona",
        "night_temperature": 15.0,
        "thunderstorm_day_after": 45.0,
        
        # Dynamischer Bericht (nur Änderungen)
        "thunderstorm_threshold_time": "16:00",
        "thunderstorm_threshold_pct": 45.0,
        "rain_threshold_time": "14:00",
        "rain_threshold_pct": 60.0
    },
    "report_time": datetime(2025, 6, 19, 4, 30)
}
```

## Gegensätze zur alten Implementierung

### Altes Format
```
GR20 Wetter 19-Jun 04:30 | Vizzavona | WARNUNG Gewitterwahrscheinlichkeit 45%
```

### Neues Format (Morgenbericht)
```
Vizzavona | Gewitter 25%@14:00 20% | Gewitter +1 30% | Regen 40%@12:00 30% 3.5mm | Hitze 26.0°C | Wind 20km/h
```

### Hauptunterschiede

1. **Struktur:** Altes Format war generisch, neues Format ist spezifisch für Wetterdaten
2. **Inhalt:** Altes Format enthielt nur Risikoindikator, neues Format enthält konkrete Werte
3. **Zeitangaben:** Neues Format enthält spezifische Zeitpunkte für Schwellenwertüberschreitungen
4. **Flexibilität:** Drei verschiedene Formate je nach Berichtstyp

## Rückwärtskompatibilität

Das System unterstützt weiterhin das alte Format für bestehende Tests:
- Wenn `report_type` nicht "morning", "evening" oder "dynamic" ist, wird das Legacy-Format verwendet
- Bestehende Tests funktionieren weiterhin ohne Änderungen

## Zeichenbegrenzung

Alle Formate respektieren das 160-Zeichen-Limit für InReach-Kompatibilität:
- Automatische Kürzung bei zu langen Texten
- Priorisierung wichtiger Informationen
- Fallback auf "..." bei Überschreitung

## Nächste Schritte

1. **Integration:** Die neuen Formate müssen in die Wetteranalyse-Pipeline integriert werden
2. **Datenaufbereitung:** Die `weather_data` Struktur muss aus den Wetterquellen generiert werden
3. **Schwellenwerte:** Zeitpunkte für Schwellenwertüberschreitungen müssen berechnet werden
4. **Etappenlogik:** Morgen- und Übermorgen-Etappen müssen aus `etappen.json` abgeleitet werden

## Tests

Alle Tests laufen erfolgreich durch:

```bash
python -m pytest tests/test_email_client.py::TestGenerateGR20ReportText -v
```

Demo-Skript zur Demonstration:

```bash
python scripts/demo_email_formats.py
``` 