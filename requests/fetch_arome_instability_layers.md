# Feature: AROME – CAPE, CIN und Lifted Index abrufen

## Ziel

Implementiere eine Funktion, die meteorologische Instabilitäts-Indikatoren (CAPE, CIN, Lifted Index) aus dem Météo-France AROME-WCS extrahiert – zur Einschätzung von Gewitterrisiken.

---

## Unterstützte Layer

- `CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND`
- `CONVECTIVE_INHIBITION__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND`
- `LIFTED_INDEX__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND`

Diese liefern numerische Werte pro Zeitstempel (ähnlich Temperatur oder Wind).

---

## Funktion

Implementiere:

```python
fetch_arome_instability_layer(lat: float, lon: float, layer_name: str) -> WeatherGridData

Liefert:
	•	times: List[datetime]
	•	values: List[float]
	•	unit: str (je nach Layer, z. B. J/kg oder °C)
	•	layer: str = Layername
	•	lat, lon: übergebenen Koordinaten

⸻

Fehlerverhalten
	•	Unbekannter Layer → ValueError
	•	Kein Token → RuntimeError
	•	HTTP ≠ 200 → Exception mit Inhalt
	•	Leere Daten → leeres WeatherGridData

⸻

Tests
	•	Datei: tests/test_arome_instability.py
	•	Szenarien:
	•	Erfolgreiche Abrufe pro Layer
	•	Layer-Validierung
	•	HTTP-Fehler
	•	Token fehlt
	•	Leere Rückgaben

⸻

Hinweise
	•	Wiederverwendung von fetch_arome_wcs_data empfohlen
	•	Einheit je nach Layer:
	•	CAPE: J/kg
	•	CIN: J/kg (negativ)
	•	LI: °C

⸻

Erweiterung

Später kann die Analyse-Logik Schwellen nutzen wie:
	•	CAPE > 800 → hohe Instabilität
	•	CIN < -50 → wenig Hemmung
	•	LI < -4 → hohe Unwetterneigung