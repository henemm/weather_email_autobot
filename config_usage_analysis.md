# Konfigurationsverwendung-Analyse

## Übersicht
Diese Analyse zeigt, welche Konfigurationsabschnitte in `config.yaml` tatsächlich verwendet werden und welche möglicherweise überflüssig sind.

---

## 1. `thresholds` - ✅ AKTIV VERWENDET

### Verwendung:
- **Hauptverwendung**: `src/logic/analyse_weather.py` - Zentrale Wetteranalyse
- **Zusätzlich**: `src/wetter/analyse.py` - Regenanalyse
- **Tests**: Umfangreich getestet in `tests/test_analyse_weather.py`

### Verwendete Schlüssel:
- `rain_probability` (25%) - Regenwahrscheinlichkeit
- `rain_amount` (2.0mm) - Regenmenge
- `thunderstorm_probability` (20%) - Gewitterwahrscheinlichkeit
- `wind_speed` (20km/h) - Windgeschwindigkeit
- `temperature` (32°C) - Temperatur
- `cloud_cover` (90%) - Bewölkung

### Status: **ESSENTIELL** - Kernfunktionalität

---

## 2. `delta_thresholds` - ✅ AKTIV VERWENDET

### Verwendung:
- **Hauptverwendung**: `src/state/tracker.py` - Warning State Tracking
- **Zweck**: Erkennung signifikanter Änderungen für dynamische Warnungen

### Verwendete Schlüssel:
- `thunderstorm_probability` (20.0%) - Delta für Gewitter
- `rain_probability` (30.0%) - Delta für Regen
- `wind_speed` (10.0km/h) - Delta für Wind
- `temperature` (2.0°C) - Delta für Temperatur

### Status: **ESSENTIELL** - Für dynamische Warnungen

---

## 3. `risk_model` - ⚠️ TEILWEISE VERWENDET

### Verwendung:
- **Implementiert in**: `src/logic/analyse_weather.py` (Funktion `compute_risk`)
- **Verwendet in**: `analyze_weather_data` und `analyze_weather_data_english`
- **Tests**: Umfangreich in `tests/test_risk_model.py`

### ABER:
- **Nicht in Hauptworkflow**: Die `compute_risk` Funktion wird aufgerufen, aber das Ergebnis wird nicht für Entscheidungen verwendet
- **Nur für Tests**: Hauptsächlich in Test-Szenarien verwendet
- **Keine Produktionslogik**: Das berechnete Risiko wird nicht für Warnungen oder Berichte genutzt

### Status: **ÜBERFLÜSSIG** - Implementiert aber nicht genutzt

---

## 4. `warn_thresholds` - ⚠️ TEILWEISE VERWENDET

### Verwendung:
- **Implementiert in**: `src/wetter/warntext_generator.py`
- **Tests**: `tests/test_warntext_generator.py`
- **Demo**: `scripts/demo_warntext_generator.py`

### ABER:
- **Nicht im Hauptworkflow**: Der `warntext_generator` wird nicht in der Hauptanwendung aufgerufen
- **Nur für Tests**: Hauptsächlich in Test-Szenarien verwendet
- **Keine Integration**: Nicht in E-Mail-Berichten oder Hauptlogik integriert

### Status: **ÜBERFLÜSSIG** - Implementiert aber nicht integriert

---

## 5. `dynamic_send` - ❌ NICHT VERWENDET

### Verwendung:
- **Nur in Tests**: `tests/test_gr20_report_integration.py`, `tests/test_report_scheduler.py`
- **Keine Produktionslogik**: Nicht in der tatsächlichen Anwendung implementiert

### Status: **ÜBERFLÜSSIG** - Nur Test-Konfiguration

---

## 6. Andere Konfigurationsabschnitte

### `startdatum` - ✅ VERWENDET
- **Verwendung**: `src/config/config_loader.py` (Pflichtfeld)
- **Status**: **ESSENTIELL**

### `smtp` - ✅ VERWENDET
- **Verwendung**: `src/config/config_loader.py` (Pflichtfeld)
- **Status**: **ESSENTIELL**

---

## NEUE EMPFEHLUNG: Vereinfachte Konfiguration

Basierend auf der Analyse und dem Feedback benötigen wir eigentlich nur:

### 1. Ab wann soll ein Wert als "relevant" hervorgehoben werden
### 2. Ab welcher Veränderung soll es eine untertägige Warnung geben
### 3. Zusätzliche Parameter für das Verhalten

### Vereinfachte config.yaml:
```yaml
startdatum: "2025-06-15"
smtp:
  server: "smtp.gmail.com"
  port: 587
  username: "your-email@gmail.com"
  password: "${GMAIL_APP_PW}"

# Ab wann soll ein Wert als "relevant" hervorgehoben werden
thresholds:
  rain_probability: 25.0      # Regenwahrscheinlichkeit in %
  rain_amount: 2.0           # Regenmenge in mm
  thunderstorm_probability: 20.0  # Gewitterwahrscheinlichkeit in %
  wind_speed: 20.0           # Windgeschwindigkeit in km/h
  temperature: 32.0          # Temperatur in °C
  cloud_cover: 90.0          # Bewölkung in %

# Ab welcher Veränderung soll es eine untertägige Warnung geben
delta_thresholds:
  thunderstorm_probability: 20.0  # Delta für Gewitter in %
  rain_probability: 30.0          # Delta für Regen in %
  wind_speed: 10.0                # Delta für Wind in km/h
  temperature: 2.0                # Delta für Temperatur in °C

# Zusätzliche Parameter
min_interval_min: 30              # Minimaler Abstand zwischen Warnungen in Minuten
max_daily_reports: 3              # Maximale Anzahl Berichte pro Tag
```

### Vorteile der Vereinfachung:
- **Klarer Zweck**: Jeder Abschnitt hat eine eindeutige Funktion
- **Weniger Komplexität**: Nur 3 relevante Abschnitte statt 5
- **Bessere Wartbarkeit**: Offensichtlich, was wofür verwendet wird
- **Praktische Parameter**: `min_interval_min` und `max_daily_reports` für sinnvolle Begrenzungen

---

## Fazit

Das System ist tatsächlich **overengineered**. Von 5 Schwellenwert-Abschnitten werden nur 2 tatsächlich verwendet. Die anderen 3 sind implementiert aber nicht in den Hauptworkflow integriert.

**Neue Empfehlung**: Fokus auf die 3 essentiellen Aspekte:
1. **Relevanz-Schwellenwerte** (wann ist etwas wichtig?)
2. **Änderungs-Schwellenwerte** (wann soll gewarnt werden?)
3. **Verhaltens-Parameter** (wie oft und in welchen Abständen?)

Das reduziert die Komplexität erheblich und macht die Konfiguration viel verständlicher. 