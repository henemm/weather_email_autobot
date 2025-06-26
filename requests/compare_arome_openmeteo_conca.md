---
title: Vergleich: AROME vs. Open-Meteo für Conca
status: pending
type: feature
labels:
  - integration
  - weather
---

## Ziel

Vergleich meteorologischer Parameter aus zwei verschiedenen Modellen für den Ort **Conca (Korsika)**:

- Météo-France AROME WCS: für CAPE, SHEAR etc.
- Open-Meteo Forecast API: für Temperatur, Wind, Niederschlag

## Anforderungen

- Lese Live-Daten beider APIs für die Koordinaten `lat=41.7481, lon=9.2972`.
- Erzeuge strukturierte JSON-Datei mit folgenden Informationen:
  - `timestamp` (UTC)
  - `location`-Metadaten (Name, Koordinaten)
  - `arome`:
    - alle verfügbaren Layer mit „cape“ oder „shear“ im Namen
  - `open_meteo`:
    - Live-Vorhersage für Temperatur, Wind und Niederschlag

- Fehler sollen eindeutig und nachvollziehbar protokolliert werden (z. B. Token-Fehler, Netzwerkfehler, ungültige Daten).
- Speichere das Ergebnis unter: `data/conca_weather_comparison.json`

## Hinweise

- Verwende die zentrale Token-Provider-Logik (`get_api_token("arome")`).
- AROME-WCS-GetCapabilities-Endpunkt:
  - `https://public-api.meteofrance.fr/public/arome/1.0/wcs/...`
- Open-Meteo-API-Endpunkt:
  - `https://api.open-meteo.com/v1/forecast?...`

## Teststrategie

- Teste unabhängig von .env durch manuelle Setzung der Tokens.
- Überprüfe insbesondere:
  - korrektes Filtern der Layer
  - vollständige JSON-Struktur
  - Verarbeitung von Fehlerfällen