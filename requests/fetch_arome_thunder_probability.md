# Feature: AROME – Gewitterwahrscheinlichkeit per WCS abrufen

## Ziel

Ergänze das System um eine Funktion, die aus dem Météo-France AROME-WCS den Layer `THUNDERSTORM_PROBABILITY__GROUND_OR_WATER_SURFACE` extrahiert – als stündliche Vorhersage für eine Koordinate.

---

## API Layer

- Layername: `THUNDERSTORM_PROBABILITY__GROUND_OR_WATER_SURFACE`
- Quelle: WCS-Schnittstelle, wie in `fetch_arome_wcs.py` bereits genutzt

---

## Funktion

Implementiere:

```python
fetch_arome_thunder_probability(lat: float, lon: float) -> WeatherGridData


Nutzt denselben Abrufmechanismus wie bestehende fetch_arome_wcs_data
	•	Liefert:
	•	times: List[datetime]
	•	values: List[int] (0–100 %)
	•	layer: str = 'THUNDERSTORM_PROBABILITY__GROUND_OR_WATER_SURFACE'
	•	unit: str = '%'

⸻

Fehlerverhalten
	•	Kein Token → RuntimeError
	•	HTTP-Code ≠ 200 → Exception mit Statuscode und Antwortinhalt
	•	Leere Daten → Rückgabe leeres WeatherGridData
	•	Falsche Koordinaten → ValueError

⸻

Tests
	•	tests/test_arome_thunder.py
	•	Fälle:
	•	Erfolgreicher Abruf mit Werten
	•	Fehlerhafte Koordinaten
	•	Token fehlt
	•	Layer nicht gefunden
	•	Leere Rückgabe

⸻

Hinweise
	•	Funktional identisch zur generischen WCS-Logik (fetch_arome_wcs_data)
	•	Wiederverwendung bestehender Parser empfohlen
	•	Nutze Konstante für Layername