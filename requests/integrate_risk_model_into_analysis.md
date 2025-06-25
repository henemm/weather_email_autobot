Feature: compute_risk in Wetteranalyse integrieren

Ziel

Die bestehende Funktion compute_risk() (aus analyse_weather.py) soll in den Analyseprozess eingebunden werden, sodass der Risiko-Score automatisch berechnet wird und im Ergebnis auftaucht.

⸻

Änderungen

Datei: logic/analyse_weather.py

Ergänzungen:
	1.	Importiere die Funktion compute_risk
	2.	Lade die risk_model-Konfiguration aus dem übergebenen Konfigobjekt
	3.	Extrahiere die Messwerte (metrics) aus den analysierten Wetterdaten
	4.	Berechne den Risiko-Wert mit compute_risk(metrics, config)
	5.	Schreibe das Ergebnis in WeatherAnalysisResult.risk

⸻

Beispielintegration

metrics = {
“thunderstorm_probability”: data.thunderstorm_probability,
“cape”: data.cape,
“lifted_index”: data.lifted_index,
“wind_speed”: data.wind_speed,
“precipitation”: data.precipitation,
“temperature”: data.temperature,
}

risk = compute_risk(metrics, config.get(“risk_model”, {}))

return WeatherAnalysisResult(
risk=risk,
…
)

⸻

Testanpassung
	•	Tests in test_analyse_weather.py um Risikoüberprüfung erweitern
	•	Dummy-Konfiguration mitgeben (für predictable outcome)
	•	Typische Schwellen überschreiten lassen

⸻

Zielzustand

Nach der Integration:
	•	analyse_weather.analyse(...) liefert stets ein risk-Feld im Ergebnis
	•	Die Berechnung ist datenbasiert, konfigurierbar und getestet