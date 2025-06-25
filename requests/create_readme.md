🧭 README.md erstellen

Ziel

Das Projekt benötigt eine zentrale Einstiegspunkt-Dokumentation für Entwickler und Operatoren.

Inhalte des geplanten README.md

1. Projektübersicht
	•	Zweck: Wetterwarnsystem für den GR20-Fernwanderweg (Korsika)
	•	Funktion: Automatisierte Wetteranalyse, Gefahrenbewertung, E-Mail-Versand via Satellitendienst

2. Architekturüberblick
	•	Positionserkennung: ShareMap → Etappen → GPS
	•	Wetterdaten: Météo-France (6 Modelle) + OpenMeteo (Fallback)
	•	Analyse: Schwellenwertbasiert (CAPE, SHEAR, Niederschlag etc.)
	•	Versand: Gmail SMTP → SOTAmāt → Garmin InReach

3. Setup-Anleitung
	•	.env-Variablen: GMAIL_APP_PW, SHAREMAP_TOKEN, METEOFRANCE_*
	•	Abhängigkeiten: pip install -r requirements.txt
	•	Start: python scripts/run_gr20_weather_monitor.py

4. Teststrategie
	•	Alle Tests: pytest
	•	Integrationstests: pytest tests/integration/
	•	Manuelle Tests: tests/manual/*.py

5. Betrieb & Monitoring
	•	Logs: logs/warning_monitor.log
	•	Cronjobs oder systemd empfohlen für Produktivbetrieb
	•	Healthcheck optional via Mail/Status-Report

Akzeptanzkriterien
	•	README.md liegt im Projektroot
	•	Enthält alle o. g. Punkte
	•	Ist in Markdown formatiert
	•	Lässt sich mit less README.md gut lesen
