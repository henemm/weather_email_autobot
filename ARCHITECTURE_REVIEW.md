# Architektur-Review: Wetterdaten-Verarbeitung und Berichtserstellung

## 1. Aktuelle Modulstruktur

### 1.1 Wetterdaten-Verarbeitung (`src/wetter/`)

#### **Hauptmodule:**
- **`weather_data_processor.py`** (74KB, 1431 Zeilen)
  - Zentrale Wetterdaten-Verarbeitung
  - Aggregation über mehrere Koordinaten
  - Debug-Ausgaben für alle Berichtstypen
  - **Verantwortlichkeiten:** Datenbeschaffung, Aggregation, Debug

- **`fetch_meteofrance.py`** (19KB, 549 Zeilen)
  - Météo-France API Client
  - **Verantwortlichkeiten:** API-Zugriff, Datenabruf

- **`fetch_openmeteo.py`** (12KB, 357 Zeilen)
  - Open-Meteo Fallback
  - **Verantwortlichkeiten:** Fallback-Datenquelle

- **`analyse.py`** (8.3KB, 231 Zeilen)
  - Wetteranalyse (vermutlich Legacy)
  - **Verantwortlichkeiten:** Analyse (veraltet)

- **`analyze_arome_layers.py`** (12KB, 330 Zeilen)
  - AROME-Modell-Analyse (vermutlich Legacy)
  - **Verantwortlichkeiten:** Modell-spezifische Analyse (veraltet)

#### **Debug/Test-Module:**
- **`report_debug.py`** (17KB, 442 Zeilen)
- **`debug_raw_data.py`** (13KB, 388 Zeilen)
- **`compare_models.py`** (8.4KB, 259 Zeilen)

#### **Warnungen:**
- **`warning.py`** (15KB, 455 Zeilen)
- **`warnlagen_validator.py`** (17KB, 443 Zeilen)
- **`warntext_generator.py`** (3.7KB, 136 Zeilen)

### 1.2 Logik (`src/logic/`)

- **`analyse_weather.py`** (29KB, 779 Zeilen)
  - **Verantwortlichkeiten:** Wetteranalyse, Risikobewertung, Zusammenfassung
  - **Überschneidung:** Mit `src/wetter/weather_data_processor.py`

- **`report_scheduler.py`** (13KB, 371 Zeilen)
  - **Verantwortlichkeiten:** Berichtsplanung, Timing

### 1.3 Berichtserstellung (`src/report/`)

- **`weather_report_generator.py`** (18KB, 491 Zeilen)
  - **Verantwortlichkeiten:** Berichtsgenerierung, Aggregation, Formatierung
  - **Überschneidung:** Mit `src/wetter/weather_data_processor.py` und `src/notification/email_client.py`

### 1.4 Benachrichtigung (`src/notification/`)

- **`email_client.py`** (27KB, 715 Zeilen)
  - **Verantwortlichkeiten:** E-Mail-Versand, Formatierung, Betreff-Generierung
  - **Überschneidung:** Mit `src/report/weather_report_generator.py`

- **`modular_sms_client.py`** (6.1KB, 170 Zeilen)
  - **Verantwortlichkeiten:** SMS-Versand

## 2. Identifizierte Probleme

### 2.1 Doppelte/Redundante Funktionalität

#### **Aggregation:**
- `weather_data_processor.py` → `_aggregate_weather_data()`
- `weather_report_generator.py` → `_aggregate_weather_data()`
- **Problem:** Zwei verschiedene Aggregationslogiken

#### **Formatierung:**
- `email_client.py` → `generate_gr20_report_text()`, `_generate_morning_report()`, etc.
- `weather_report_generator.py` → `_generate_report_text()`, `_format_*_data()`
- **Problem:** Zwei verschiedene Formatierungslogiken

#### **Analyse:**
- `analyse_weather.py` → `analyze_weather_data()`
- `weather_data_processor.py` → Aggregation und Analyse
- **Problem:** Zwei verschiedene Analyselogiken

### 2.2 Inkonsistente Datenstrukturen

#### **Feldnamen:**
- `max_wind_gusts` vs `wind_gusts`
- `thunderstorm_next_day` vs `tomorrow_max_thunderstorm_probability`
- **Problem:** Verschiedene Module verwenden verschiedene Feldnamen

#### **Datenformate:**
- `weather_data_processor.py` → Dict-basiert
- `analyse_weather.py` → Dataclass-basiert (`WeatherData`, `WeatherPoint`)
- **Problem:** Inkompatible Datenstrukturen

### 2.3 Unklare Verantwortlichkeiten

#### **Datenfluss:**
```
API → fetch_meteofrance.py → weather_data_processor.py → weather_report_generator.py → email_client.py
```
**Problem:** Zu viele Zwischenschritte, doppelte Verarbeitung

#### **Debug-Ausgaben:**
- `weather_data_processor.py` → Umfangreiche Debug-Funktionen
- `report_debug.py` → Separate Debug-Logik
- **Problem:** Doppelte Debug-Funktionalität

## 3. Vorgeschlagene Neue Architektur

### 3.1 Zentrale Module

#### **`src/weather/core/`**
```
weather_core/
├── data_fetcher.py          # Einheitlicher Datenabruf (Météo-France + Fallback)
├── aggregator.py            # Zentrale Aggregationslogik
├── formatter.py             # Zentrale Formatierungslogik
├── analyzer.py              # Zentrale Analyselogik
└── models.py                # Einheitliche Datenmodelle
```

#### **`src/weather/reports/`**
```
reports/
├── report_generator.py      # Einheitliche Berichtsgenerierung
├── email_formatter.py       # E-Mail-spezifische Formatierung
├── sms_formatter.py         # SMS-spezifische Formatierung
└── debug_formatter.py       # Debug-spezifische Formatierung
```

#### **`src/weather/notifications/`**
```
notifications/
├── email_sender.py          # E-Mail-Versand
├── sms_sender.py            # SMS-Versand
└── sender_factory.py        # Sender-Factory
```

### 3.2 Einheitliche Datenstruktur

```python
@dataclass
class WeatherReport:
    """Einheitliche Berichtsdatenstruktur"""
    report_type: str  # 'morning', 'evening', 'update'
    stage_info: Dict[str, Any]
    weather_data: Dict[str, Any]
    vigilance_data: Optional[Dict[str, Any]]
    fire_risk_data: Optional[Dict[str, Any]]
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
```

### 3.3 Vereinfachter Datenfluss

```
API → data_fetcher.py → aggregator.py → analyzer.py → report_generator.py → formatter.py → sender.py
```

## 4. Migrationsplan

### 4.1 Phase 1: Konsolidierung (Sicher)
- [ ] Erstelle neue zentrale Module
- [ ] Implementiere einheitliche Datenmodelle
- [ ] Migriere Formatierungslogik zu `formatter.py`
- [ ] Behalte bestehende Module bei (Fallback)

### 4.2 Phase 2: Migration (Vorsichtig)
- [ ] Migriere `weather_data_processor.py` → `aggregator.py`
- [ ] Migriere `email_client.py` → `email_formatter.py` + `email_sender.py`
- [ ] Migriere `weather_report_generator.py` → `report_generator.py`
- [ ] Aktualisiere alle Imports

### 4.3 Phase 3: Bereinigung (Sauber)
- [ ] Entferne veraltete Module
- [ ] Entferne doppelte Debug-Logik
- [ ] Entferne Legacy-Analyse-Module
- [ ] Aktualisiere Dokumentation

## 5. Vorteile der Neuen Architektur

### 5.1 Einheitlichkeit
- **Eine** Aggregationslogik
- **Eine** Formatierungslogik
- **Eine** Analyselogik
- **Einheitliche** Datenstrukturen

### 5.2 Wartbarkeit
- Klare Verantwortlichkeiten
- Weniger Code-Duplikation
- Einfachere Tests
- Bessere Debugging-Möglichkeiten

### 5.3 Erweiterbarkeit
- Einfache Integration neuer Datenquellen
- Einfache Integration neuer Ausgabeformate
- Modulare Architektur
- Klare Schnittstellen

## 6. Risiken und Mitigation

### 6.1 Risiken
- **Breaking Changes:** Bestehende Funktionalität könnte beeinträchtigt werden
- **Datenverlust:** Fehler bei der Migration könnten zu Datenverlust führen
- **Performance:** Neue Architektur könnte langsamer sein

### 6.2 Mitigation
- **Schrittweise Migration:** Phase-für-Phase, nicht alles auf einmal
- **Umfassende Tests:** Snapshot-Tests für alle Berichtstypen
- **Fallback-Mechanismen:** Alte Module bleiben bis zur vollständigen Migration
- **Performance-Tests:** Vergleich vor und nach der Migration

## 7. Nächste Schritte

1. **Bestätigung:** Architektur-Plan genehmigen
2. **Phase 1 starten:** Zentrale Module erstellen
3. **Tests erweitern:** Snapshot-Tests für neue Module
4. **Migration beginnen:** Schrittweise Umstellung
5. **Monitoring:** Überwachung der Funktionalität während der Migration 