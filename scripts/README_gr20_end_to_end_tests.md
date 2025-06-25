# GR20 Live End-to-End Tests

Diese Tests simulieren vollständige Durchläufe des GR20-Warnsystems unter realitätsnahen Bedingungen.

## Übersicht

Die Tests basieren auf der `requests/live_end_to_end_gr20_weather_report.md` und verwenden:

- **Etappe 2 (Carozzu)** aus `etappen.json`
- **Abendmodus** und **Morgenmodus** gemäß `docs/wettermodi_uebersicht.md`
- **Echte Wetterdaten** von AROME und OpenMeteo
- **Echte E-Mail-Versendung** über SMTP

## Vorbereitung

### 1. Umgebungsvariablen setzen

```bash
export GMAIL_APP_PW="your_gmail_app_password"
export METEOFRANCE_CLIENT_ID="your_meteofrance_client_id"
export METEOFRANCE_CLIENT_SECRET="your_meteofrance_client_secret"
```

### 2. Token-Provider aktivieren

Stellen Sie sicher, dass der METEOFRANCE_WCS_TOKEN verfügbar ist:

```bash
python scripts/demo_oauth2_token_provider.py
```

## Tests ausführen

### Abendmodus-Test

```bash
# Mit E-Mail-Versand
python scripts/test_gr20_end_to_end_abend.py

# Ohne E-Mail-Versand (nur für Entwicklung)
python scripts/test_gr20_end_to_end_abend.py --no-email
```

### Morgenmodus-Test

```bash
# Mit E-Mail-Versand
python scripts/test_gr20_end_to_end_morgen.py

# Ohne E-Mail-Versand (nur für Entwicklung)
python scripts/test_gr20_end_to_end_morgen.py --no-email
```

## Was wird getestet?

### 1. Etappen-Logik
- ✅ Korrekte Identifikation von Etappe 2 (Carozzu)
- ✅ Verwendung aller Routenpunkte der Etappe
- ✅ Koordinaten aus `etappen.json`

### 2. Wetterdaten-Aggregation
- ✅ **Abendmodus:** Alle Punkte der morgigen Etappe (Maximalwerte)
- ✅ **Morgenmodus:** Alle Punkte der heutigen Etappe (Maximalwerte)
- ✅ Worst-Case-Prinzip bei mehreren Datenquellen

### 3. Berichtsformat
- ✅ Max. 160 Zeichen
- ✅ Keine Emojis oder Links
- ✅ Kompakte InReach-Formatierung
- ✅ Korrekte Risiko-Darstellung

### 4. E-Mail-Versand
- ✅ SMTP-Verbindung zu Gmail
- ✅ Korrekte Betreffzeile mit Etappenbezeichnung
- ✅ Versand an SOTAmāt-Adresse

## Erfolgskriterien

Der Test ist erfolgreich, wenn:

1. **E-Mail wird versendet** (falls `--no-email` nicht gesetzt)
2. **Betreff enthält korrekte Etappenbezeichnung**
3. **Inhalt entspricht Kurzformat ohne Link/Emoji**
4. **Wetterdaten wurden korrekt aggregiert**
5. **Etappe 2 wurde verwendet** (nicht nur letzter Punkt)

## Beispiel-Ausgabe

```
🌄 GR20 Live End-to-End Test - Abendmodus
==================================================
Loading configuration...
✅ Configuration loaded
Loading etappen...
✅ Etappen loaded
Getting stage 2 coordinates...
Using stage: E2 Carozzu
Coordinates: [{'lat': 42.465338, 'lon': 8.906787}, ...]
✅ Using stage: E2 Carozzu
Fetching weather data...
Fetching weather data for 3 stage points...
Point 1: 42.465338, 8.906787
  Fetching AROME data for point 1...
  AROME data fetched successfully for point 1
  Fetching OpenMeteo data for point 1...
  OpenMeteo data fetched successfully for point 1
...
✅ Weather data fetched for 6 sources
Analyzing weather data...
Analyzing weather data for evening mode...
Analysis complete:
  Max temperature: 28.5°C
  Max precipitation: 2.3mm
  Max wind speed: 25 km/h
  Max thunderstorm probability: 15%
  Risk score: 0.35
  Summary: Keine kritischen Wetterbedingungen erkannt.
✅ Weather analysis complete
Generating report text...
✅ Report text: E2Carozzu | Tag 28.5°C | Regen 2.3mm | Wind 25km/h | Gewitter 15%
   Length: 67 characters
✅ Report format validation passed
Testing email sending...
✅ Email sent successfully

🎯 End-to-End Test Results:
✅ Etappe 2 (Carozzu) correctly identified
✅ Weather data aggregated over all stage points
✅ Abendmodus logic applied correctly
✅ Report text generated without emojis/links
✅ Report text within 160 character limit
✅ Email sent successfully

🎉 Live End-to-End Test PASSED!
```

## Fehlerbehebung

### Keine Wetterdaten verfügbar
- Prüfen Sie die METEOFRANCE-Token
- Prüfen Sie die Internetverbindung
- Führen Sie `python scripts/demo_oauth2_token_provider.py` aus

### E-Mail-Versand fehlgeschlagen
- Prüfen Sie GMAIL_APP_PW
- Prüfen Sie die SMTP-Konfiguration in `config.yaml`
- Verwenden Sie `--no-email` für Tests ohne E-Mail

### Etappe nicht gefunden
- Prüfen Sie `etappen.json`
- Stellen Sie sicher, dass Etappe 2 existiert

## Nächste Schritte

Nach erfolgreichem Test können Sie:

1. **Crontab einrichten** für automatische Ausführung
2. **Monitoring** der E-Mail-Versendung
3. **Erweiterte Tests** für andere Etappen
4. **Tageswarnung-Tests** implementieren 