# Datei: requests/demo_live_conca_summary.md

---
title: Zusammenfassung aller Météo-France APIs für Conca
description: Dieses Skript ruft Live-Daten für die Koordinaten von Conca, Korsika ab und gibt die Ergebnisse als JSON-Datei und terminalfreundliche Zusammenfassung aus.
labels: [demo, integration, live, meteofrance]
requires:
  - src/auth/meteo_token_provider.py
  - src/api/arome_wcs.py
  - src/api/vigilance_api.py
  - src/analysis/analyse_weather.py
  - src/utils/env_loader.py
output:
  - output/conca_weather_summary.json
---

## Ziel

Zeige live alle relevanten Wetterdaten und Risikoanalysen für die Region um Conca (Korsika).

## Geoposition

- Breitengrad: `41.7577`
- Längengrad: `9.3420`

## Anforderungen

- Funktionierender OAuth2-Zugang zu Météo-France (.env muss gültige Werte enthalten)
- Layer-Konfiguration ist valide
- Internetverbindung

## Was dieses Skript macht

1. Holt über die AROME-WCS API aktuelle Wetterwerte (Niederschlag, Temperatur etc.)
2. Holt verfügbare Werte über Open-Meteo API
3. Prüft über die Vigilance-API auf Wetterwarnungen
4. Führt die Risikoanalyse mit vorhandener Logik durch
5. Gibt die Ergebnisse aus:
   - als JSON-Datei: `output/conca_weather_summary.json` (auch Rohwerte)
   - als Text im Terminal (Kurzfassung)

## Umsetzung

Erzeuge eine Datei `scripts/demo_meteofrance_live_summary.py` mit folgender Funktionalität:

- Nutze `get_required_env_var()` zur Absicherung der Umgebungsvariablen
- Verwende den zentralen `TokenProvider`
- Nutze bestehende Methoden aus `src/api/arome_wcs.py` und `src/api/vigilance_api.py`
- Nutze `analyse_weather()` aus `src/analysis/analyse_weather.py`
- Fasse die Ergebnisse strukturiert in einem JSON-Objekt zusammen
- Speichere unter `output/conca_weather_summary.json`
- Gib eine gekürzte, gut lesbare Textversion in der Konsole aus (z. B. Temperatur, Niederschlag, Warnlage, Risk-Score)

## Hinweise

- Falls Token oder Koordinaten fehlen, soll das Skript eine klare Fehlermeldung ausgeben.
- Ergebnisse der Einzel-APIs (z. B. Layer-Response) können im JSON enthalten sein, die Terminalausgabe sollte aber stark komprimiert sein.

## Testbarkeit

- Das Skript darf nicht abstürzen, wenn einzelne APIs keine Daten liefern.
- Muss robuster Umgang mit Netzwerkfehlern und ungültigen Tokens enthalten (Retry oder Hinweis).

## Beispielausgabe (Terminal)
Rohdaten 
🌍 Wetterdaten für Conca, Korsika (41.7577, 9.3420)
🌦️ Temperatur: 24.3°C, Niederschlag: 0.0mm, Wind: 5.4m/s
🚨 Warnstufe: Orange (Starkregen)
🧠 Risikoanalyse: Risk-Score = 72 → Handlung empfohlen
📄 Details gespeichert in output/conca_weather_summary.json