# Wetterbericht-Automat

Dieses System analysiert die Wetterlage entlang beliebiger Routen (z.B. GR20, E1, Deutschlandtour) und verschickt automatisierte Kurzberichte an einen Garmin inReach Messenger via E-Mail-to-SMS-Weiterleitung.

Ziel: Zuverlässige, minimalistische Übermittlung von Gewitter- und Wetterwarnungen für die jeweils bevorstehende Etappe – auch bei fehlender Internetverbindung.

## Wichtige Regeln (ab v1.0.0)

- **Nullwertregel:** Alle Wetterwerte, die 0 oder leer sind, werden als „-” ausgegeben. Keine Zeitangaben oder Einheiten für 0-Werte.
- **Etappennamen-Logik:** Im Abendbericht steht immer die morgige Etappe im Betreff und im Text.
- **Kompaktformat:** Keine führenden Nullen, keine leeren Dezimalstellen, bei Platzmangel werden Leerzeichen entfernt.

## Ablauf

Das Hauptskript `scripts/run_gr20_weather_monitor.py` führt aus:

1. **Positionsbestimmung**
   - Ermittlung der Tagesetappe aus `etappen.json` und Startdatum (`config.yaml`)
   - Nutzung der Koordinaten von Start, Ziel und Zwischenpunkten

2. **Wetterdatenbeschaffung**
   - Primär: Météo-France (AROME, PIAF, Vigilance)
   - Sekundär: OpenMeteo (Fallback)

3. **Analyse**
   - Auswertung von CAPE, SHEAR, Regen, Wind, Temperatur, Warnungen

4. **Entscheidung**
   - Zeitpunkte: 04:30 UTC (morgens), 19:00 UTC (abends)
   - Tagsüber max. 3 Berichte bei signifikanten Änderungen

5. **Versand**
   - SMTP-Versand per Gmail
   - Max. 160 Zeichen, keine Links oder Emojis

## Projektstruktur

- `scripts/run_gr20_weather_monitor.py`: Hauptlogik
- `config.yaml`: Schwellenwerte, Startdatum, Zeitpläne
- `etappen.json`: Etappenpunkte (beliebige Route)
- `generate_etappen_json.py`: GPX zu JSON Konverter für Routendaten
- `src/`
  - `wetter/`: API-Zugriffe (MeteoFrance, OpenMeteo, Vigilance)
  - `logic/`: Analyse (`analyse_weather.py`), Scheduler
  - `notification/email_client.py`: E-Mail-Versand
  - `position/etappenlogik.py`: Etappen- und Positionslogik
  - `utils/env_loader.py`: Umgebungsvariablen-Management

## Tests

- Ausführung mit `pytest`
- Integration: `tests/test_gr20_report_integration.py`
- Manuell: `tests/manual/`

## Voraussetzungen

Siehe `.env` und `config.yaml` für alle nötigen Variablen.

## Dokumentation

- **`generate_etappen_json.md`**: GPX zu JSON Konvertierung
- **`email_format_implementation.md`**: E-Mail-Formatregeln, Nullwertregel, Etappennamen-Logik
- **`wettermodi_uebersicht.md`**: Übersicht der Wettermodi und Berichtstypen

## Hinweise

- Keine Emojis oder Links
- Nachrichtenlänge: max. 160 Zeichen
- SMTP-Retry bei Fehlern
- Garmin-Zustellung wetterabhängig (Bewölkung!)

## 📚 Dokumentation

### Verfügbare Dokumentation

- **`generate_etappen_json.md`**: Detaillierte Anleitung für GPX zu JSON Konvertierung
- **`email_format_implementation.md`**: E-Mail-Formatregeln und Implementierung
- **`wettermodi_uebersicht.md`**: Übersicht der Wettermodi und Berichtstypen
- **`oauth2_wms_wcs_best_practices.md`**: OAuth2 Authentifizierung für Météo-France
- **`meteo_token_provider.md`**: Token-Management und API-Zugriff
- **`remove_arome_hr_agg.md`**: Architekturänderungen und Modell-Updates

### Status-Dateien

- **`status_gr20_e2e.txt`**: End-to-End Test Status
- **`schedule_gr20_weather_report.txt`**: Zeitplan für Wetterberichte
- **`messaging_architecture_gr20.txt`**: Nachrichtenarchitektur
- **`meteo_api_architecture.txt`**: API-Architektur Übersicht
- **`oauth2_strategy.txt`**: OAuth2 Strategie