# requests/debug_live_wcs_vigilance_openmeteo.md

---
title: Live-Wetterdaten-Diagnose für Conca (Korsika)
description: Führt eine kombinierte Analyse der Wetterlage für eine feste Geo-Position (Conca, Korsika) anhand dreier Wetter-APIs durch. Gibt strukturiertes Ergebnis als JSON-Datei aus. Dient der Prüfung der API-Erreichbarkeit, Datenkonsistenz und Fehleranalyse.
labels:
  - live
  - integration
  - debug
  - wetternetz
---

## Ziel
Das Skript soll an einem zentralen Punkt (Conca, Korsika) die aktuellen Wetterinformationen abrufen und strukturiert gegenüberstellen:

- Temperatur, Wind, Wetterzustand aus **Open-Meteo**
- WCS-Wetterdaten (Layer MF-NWP-HIGHRES-AROME-001-FRANCE-WMS) aus **Météo-France**
- Wetterwarnungen (Vigilance API) aus **Météo-France**

## Input
- Feste Koordinaten (Conca, Korsika): `lat = 41.7524`, `lon = 9.2746`
- Umgebungsvariablen aus `.env`:
  - `METEOFRANCE_CLIENT_ID`
  - `METEOFRANCE_CLIENT_SECRET`
  - Optional: Logging-Flags (z. B. DEBUG_WEATHER)

## Output
- JSON-Datei `output/live_weather_conca_<timestamp>.json`
  mit Feldern:
  - `openmeteo`: Ergebnis oder Fehler
  - `wcs`: Ergebnis oder HTTP-Fehler
  - `vigilance`: Ergebnis oder Fehler

## Anforderungen
- Robuste Fehlerbehandlung (Fallback bei Timeout, 401, 404 etc.)
- Timeouts max. 5 Sekunden pro Anfrage
- Bei Token-Fehlern automatische Erneuerung (OAuth2)
- Strukturierte Debug-Ausgabe im Terminal (Farben, Quelle, Status)
- Bei erfolgreicher WCS-Antwort: Layer-Information + Rohdaten-Link speichern

## Priorität
✅ Kritisch für Live-Integrationstest und API-Triage

## Status
Bereit zur Umsetzung. Koordinaten und Logik definiert. API-Zugänge in .env erwartet.

## Hinweise
- Die Open-Meteo API erfordert keinen Token.
- Die Météo-France WCS kann je nach Layer eingeschränkte Daten liefern.
- Vigilance-API reagiert empfindlich auf falsche Koordinaten oder Tokenfehler.