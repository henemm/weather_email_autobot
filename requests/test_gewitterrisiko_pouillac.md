# 🌩️ Live-Test: Gewitterrisiko-Berechnung für Pouillac (Frankreich)

## Ziel

Dieser Test überprüft die Risikoanalyse für Gewitter an einem konkreten Punkt außerhalb des GR20, um die Logik der Modellintegration zu validieren.

## Testpunkt

- **Ort:** Pouillac, Frankreich
- **Koordinaten:** 44.8570 N, –0.1780 E

## Getestete APIs / Modelle

| Modell              | Zweck                               |
|---------------------|--------------------------------------|
| AROME_HR            | CAPE, SHEAR, Basisprognose           |
| AROME_HR_NOWCAST    | Kurzfristige Wind- und Konvektionsdaten |
| PIAF_NOWCAST        | Regenrate-Nowcasting (5min Auflösung) |
| OPENMETEO_GLOBAL    | Temperatur, Wind, Niederschlag       |

## Schritte

### 1. Einzelabfragen pro Modell

- Abruf von Rohdaten je API:
  - `fetch_arome_field(lat=44.857, lon=-0.178, field="CAPE", model="AROME_HR")`
  - `fetch_arome_field(..., field="SHEAR")`
  - `fetch_nowcast_rainrate(..., model="PIAF_NOWCAST")`
  - `fetch_openmeteo(...)`

### 2. Risikoauswertung pro Quelle

- AROME_HR: Kombiniere CAPE + SHEAR → Risikowert
- PIAF_NOWCAST: Prüfe Regenrate ≥ Schwellenwert
- OPENMETEO: Nur informativ (Fallback)

### 3. Aggregation

- Kombiniere alle verfügbaren Risikowerte zu einem Gesamt-Risiko-Score:
  - **niedrig / mittel / hoch**
  - Basierend auf konfigurierten Schwellenwerten aus `config.yaml`

### 4. Output

- Strukturierter JSON-Report für Pouillac:
  ```json
  {
    "location": "Pouillac",
    "coordinates": [44.857, -0.178],
    "timestamp": "...",
    "risks": {
      "AROME_HR": { "CAPE": ..., "SHEAR": ..., "risk": "mittel" },
      "PIAF_NOWCAST": { "rainrate": ..., "risk": "niedrig" },
      "OPENMETEO_GLOBAL": { "temp": ..., "rain": ..., "risk": "niedrig" }
    },
    "overall_risk": "mittel"
  }
 ## Akzeptanzkriterien
	•	Alle 4 APIs liefern Daten oder werden als „nicht verfügbar“ gekennzeichnet
	•	CAPE+SHEAR → führen zu nachvollziehbarem Risiko (keine leeren Werte)
	•	Regenraten → korrekt eingeordnet
	•	Endausgabe ist im JSON-Format, vollständig und maschinenlesbar