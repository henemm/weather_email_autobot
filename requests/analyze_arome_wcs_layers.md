# Datei: requests/analyze_arome_wcs_layers.md

---
title: Analyse der AROME WCS GetCapabilities-Antworten
description: Ruft die GetCapabilities-Endpunkte der drei AROME-Modelle ab und analysiert verfügbare Layer, BoundingBox, Zeitabdeckung und prüft Abdeckung für Conca/Korsika.
labels: [analysis, meteo-france, wcs, arome, capabilities]
---

## Ziel

Wir wollen die drei verfügbaren WCS-Dienste von Météo-France analysieren, um:
- Alle Layer mit Identifier, Titel, Abstract und zeitlicher Abdeckung zu extrahieren
- Die BoundingBox jedes Layers zu prüfen
- Sicherzustellen, dass die Region Conca (9.35°E, 41.75°N) abgedeckt ist

## Endpunkte

1. **AROME Model (WMS GetCapabilities)**
   - URL: `https://public-api.meteofrance.fr/public/arome/1.0/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetCapabilities?service=WMS&version=1.3.0&language=eng`

2. **AROME Immediate Forecast (WCS GetCapabilities)**
   - URL: `https://public-api.meteofrance.fr/public/arome-ifr/1.0/wcs/MF-NWP-HIGHRES-AROME-IFR-001-FRANCE-WCS?service=WCS&version=2.0.1&request=GetCapabilities`

3. **AROME Aggregated Rainrate Forecast (WCS GetCapabilities)**
   - URL: `https://public-api.meteofrance.fr/public/arome-agg/1.0/wcs/MF-NWP-HIGHRES-AROME-AGG-001-FRANCE-WCS?service=WCS&version=2.0.1&request=GetCapabilities`

## Schritte

1. Hole per GET-Anfrage die XML-Daten von jedem Endpunkt.
2. Parse die XML mit einem geeigneten Parser (z. B. `xml.etree.ElementTree` oder `lxml`).
3. Extrahiere pro Layer:
   - Layer-ID
   - Titel / Abstract
   - BoundingBox (EPSG:4326 oder äquivalent)
   - Time-Dimension (falls vorhanden)
4. Füge pro Layer eine Prüfung hinzu:
   - Ist Punkt Conca (9.35, 41.75) in der BoundingBox enthalten?

## Ausgabe

Ein JSON-Objekt pro Dienst:
- `endpoint`: URL
- `layers`: Liste von Layer-Objekten mit:
  - `id`
  - `title`
  - `bbox`
  - `time_range`
  - `covers_conca`: true/false

## Hinweise

- Verwende ein gültiges Bearer Token via Umgebungsvariable `METEOFRANCE_WCS_TOKEN`
- Falls Fehler auftreten (401, 404), sollen diese pro Endpunkt protokolliert werden
- Ausgabe: JSON-Datei `output/analyzed_arome_layers.json`

---