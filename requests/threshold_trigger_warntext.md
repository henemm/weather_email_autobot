Feature: Risiko-Schwellenwert → Warntext

Ziel

Implementiere eine Funktion, die basierend auf einem numerischen Risiko-Wert entscheidet, ob und wie ein Warntext generiert wird. Die Funktion soll folgende Signale liefern:
	•	Kein Text, wenn Risiko zu niedrig
	•	Hinweistext, bei leicht erhöhtem Risiko
	•	Warntext, bei signifikantem Risiko
	•	Alarmtext, bei kritischem Risiko

Anforderungen

Funktion: generate_warntext

def generate_warntext(risk: float, config: dict) -> Optional[str]
	•	Verwendet Schwellenwerte aus config[“warn_thresholds”]
	•	Rückgabe:
	•	None → Risiko unterhalb Info-Grenze
	•	str → Text entsprechend des Risikolevels
	•	Unterstützte Level (inkl. Emojis):
	•	Info (z. B. Score ≥ 0.3): „⚠️ Leicht erhöhte Wettergefahr …“
	•	Warnung (Score ≥ 0.6): „⚠️ Warnung: Das Wetter-Risiko liegt bei …“
	•	Alarm (Score ≥ 0.9): „🚨 Alarm! Sehr hohes Wetterrisiko …“

Konfiguration (Beispiel)

warn_thresholds:
info: 0.3
warning: 0.6
critical: 0.9

Integration
	•	In run_warning_monitor.py:
	•	Rufe generate_warntext(risk, config) auf
	•	Falls Ergebnis ≠ None → schreibe Text nach output/inreach_warnung.txt

Tests

Datei: tests/test_warntext_generator.py
	•	Testfälle:
	•	risk = 0.0 → keine Ausgabe
	•	risk = 0.4 → Info-Level
	•	risk = 0.7 → Warntext
	•	risk = 0.95 → Alarmtext
	•	Leere oder fehlende Konfiguration abfangen
	•	Ungültige Risikowerte (NaN, negativ, >1)