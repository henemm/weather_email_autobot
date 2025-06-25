# Entfernung von AROME_HR_AGG aus dem System

## Hintergrund

Das Modell **AROME_HR_AGG** (Aggregierte Felder, 6h-Summen etc.) war in der Codebasis als Backup-Quelle für Wetterdaten vorgesehen. Die produktive Meteo France API liefert für diesen Endpunkt jedoch dauerhaft einen 404-Fehler, obwohl die Swagger-Dokumentation entsprechende Layer beschreibt. Ein Live-Betrieb ist daher nicht möglich.

## Umsetzung

- **Alle Referenzen zu AROME_HR_AGG wurden entfernt:**
  - Modell-Mapping (`src/wetter/fetch_arome_wcs.py`)
  - Tests und Testdaten (`tests/test_arome_wcs_standardized.py`, `tests/test_arome_wcs.py`, `tests/test_live_api_integration.py`)
  - Demo- und Debug-Skripte (`scripts/debug_arome_hr_temperature.py`, `scripts/run_live_api_tests.py`, `porto_vecchio_live_data.py`)
- **Testlogik und Modell-Backups** wurden auf die tatsächlich verfügbaren APIs beschränkt:
  - AROME_HR
  - AROME_HR_NOWCAST
  - PIAF_NOWCAST
  - VIGILANCE_API (separat)
- **Alle Tests laufen grün** und spiegeln das neue Verhalten korrekt wider.

## Vorteile

- Keine toten oder irreführenden Backup-Modelle mehr im System
- Klare, wartbare Modell- und API-Logik
- Fehlerquellen und Supportaufwand reduziert

## Letzte Änderung
Juni 2025 