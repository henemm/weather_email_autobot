# Feature: Risikoformel modularisieren und konfigurierbar machen

## Ziel

Erweitere das Analysemodul (`analyse_weather.py`), sodass meteorologische Gefahrenindikatoren wie CAPE, CIN, LI, Thunderstorm Probability etc. in einer **gewichteten, konfigurierbaren Risikobewertung** berücksichtigt werden.

---

## Risikoquellen (Eingaben)

- thunderstorm_probability [%]
- cape [J/kg]
- lifted_index [°C]
- cin [J/kg]
- wind_speed [km/h]
- precipitation [mm/h]
- temperature [°C]

---

## Schwellen (aus `config.yaml`)

```yaml
risk_model:
  thunderstorm_probability:
    threshold: 50
    weight: 0.4
  cape:
    threshold: 800
    weight: 0.3
  lifted_index:
    threshold: -4
    weight: 0.3
  wind_speed:
    threshold: 60
    weight: 0.2 ```

## Logik

Implementiere eine Funktion:
def compute_risk(metrics: dict, config: dict) -> float

	metrics = aktuelle Wetterwerte als dict
	•	config = geladen aus config.yaml
	•	Gibt Risiko-Level zwischen 0.0 – 1.0 zurück
	•	Gewichtung und Schwellen kommen aus Konfiguration
	•	Maximalwert: 1.0

⸻

## Beispiel

metrics = {
  "thunderstorm_probability": 70,
  "cape": 1200,
  "lifted_index": -5,
  "wind_speed": 75
}

Ergibt z. B. risk = 0.4 + 0.3 + 0.3 + 0.2 = capped at 1.0

## Tests
	•	Datei: tests/test_risk_model.py
	•	Fälle:
	•	Kein Risiko (alle Werte unter Schwellen)
	•	Kombinierte Übertritte
	•	Unbekannte Parameter → ignorieren
	•	Risiko > 1.0 → begrenzen

⸻

## Integration
	•	analyse_weather.py ruft compute_risk() auf
	•	Schwellenwerte aus config.yaml
	•	Rückgabe: WeatherAnalysisResult(risk=..., details=...)