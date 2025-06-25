# requests/test_report_generation_corte_etappe1.md

## Titel

Live-Test: Morgen- und Abendbericht mit echten Daten

## Ziel

Validierung der Ausgabeformate für Morgen- und Abendberichte anhand realer Wetterdaten für eine feste Position (Corte) und den ersten Etappenpunkt aus `etappen.json`.

## Schritte

1. Verwende den Wettermonitor im Simulationsmodus mit zwei Positionen:
   - Corte: 42.3035,9.1440
   - Erste Etappe aus `etappen.json`

2. Generiere Berichte für beide Positionen zu folgenden Modi:
   - `morning`
   - `evening`

3. Speichere Berichte in separaten Dateien:
   - `output/report_morning_corte.txt`
   - `output/report_evening_corte.txt`
   - `output/report_morning_etappe1.txt`
   - `output/report_evening_etappe1.txt`

4. Validierungskriterien:
   - Jede Datei enthält genau einen Bericht
   - Alle Pflichtwerte enthalten:
     - Gewitterwahrscheinlichkeit (inkl. Schwellenüberschreitung)
     - Regenwahrscheinlichkeit und -menge (inkl. Schwellenüberschreitung)
     - Temperatur (Tageshöchstwert bzw. Nachttemperatur)
     - Windspitzenwert
   - Format wie spezifiziert (kompakter Einzeiler, max. 160 Zeichen)

## Erwartetes Format (Beispiele)

**Morgenbericht**  
Corte | 22.4°C | Regen 10%@10 (1.2mm) | Gewitter 15%@14 | Wind 14km/h

**Abendbericht**  
Corte | Nacht 15.1°C | Regen 20%@18 (Morgen 35%@10, 2.3mm) | Gewitter 30%@19 (Morgen 45%@12) | Wind 18km/h

## Besonderheiten

- Schwellenwerte stammen aus `config.yaml`
- Ausgabezeit ist UTC-agnostisch, aber lokal korrekt (CEST)
- Datenquellen: `meteofrance-api`, OpenMeteo als Fallback