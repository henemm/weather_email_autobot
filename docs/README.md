# GR20 Wetterwarnsystem

Dieses System analysiert die Wetterlage entlang des GR20 auf Korsika und verschickt automatisierte Kurzberichte an einen Garmin inReach Messenger via E-Mail-to-SMS-Weiterleitung.

Ziel: Zuverlässige, minimalistische Übermittlung von Gewitter- und Wetterwarnungen für die jeweils bevorstehende Etappe – auch bei fehlender Internetverbindung.

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
- `etappen.json`: Etappenpunkte (aktuell 6 Etappen, erweiterbar)
- `src/`
  - `auth/api_token_provider.py`: Token-Management
  - `wetter/`: API-Zugriffe (AROME, OpenMeteo, Vigilance)
  - `logic/`: Analyse (`analyse_weather.py`), Scheduler
  - `notification/email_client.py`: E-Mail-Versand
  - `position/fetch_sharemap.py`: Positionsbestimmung (optional)
  - `utils/env_loader.py`: Umgebungsvariablen-Management

## Tests

- Ausführung mit `pytest`
- Integration: `tests/test_gr20_report_integration.py`
- Manuell: `tests/manual/`

## Voraussetzungen

Folgende Variablen in `.env` oder Umgebung:

    GMAIL_APP_PW=dein_gmail_app_passwort
    METEOFRANCE_WCS_TOKEN=dein_wcs_token
    METEOFRANCE_CLIENT_ID=deine_client_id
    METEOFRANCE_CLIENT_SECRET=dein_client_secret
    EMAIL_TARGET=zieladresse@example.com

**Hinweis:** Das System unterstützt sowohl WCS-Token als auch OAuth2-Authentifizierung. Für OAuth2 werden `METEOFRANCE_CLIENT_ID` und `METEOFRANCE_CLIENT_SECRET` verwendet, für direkte API-Zugriffe `METEOFRANCE_WCS_TOKEN`.

## Hinweise

- Keine Emojis oder Links
- Nachrichtenlänge: max. 160 Zeichen
- SMTP-Retry bei Fehlern
- Garmin-Zustellung wetterabhängig (Bewölkung!)