🧹 Temporäre Testdateien aufräumen

Ziel

Alle temporären oder nicht genutzten Testdateien, die aktuell im Projekt-Root liegen, sollen gelöscht oder korrekt einsortiert werden.

Problem

Im Projekt-Hauptverzeichnis liegen 8 Tests, die nicht in das tests/-Verzeichnis gehören:
	•	test_email_no_links.py
	•	test_lyon_warning.py
	•	test_vigilance_conca.py
	•	check_lyon_detailed.py
	•	analyze_all_hazards.py
	•	test_wcs_temperature_parsing.py
	•	test_sharemap_position.py
	•	test_warnlogic_conca.py

Diese Tests stören beim Überblick, sind teilweise veraltet oder redundant.

Lösung
	•	Jeder dieser Tests wird geprüft:
	•	🔁 Aktiv in Benutzung: In tests/integration/ oder tests/manual/ verschieben
	•	🗑️ Nicht mehr benötigt: Löschen
	•	Konventionen:
	•	Manuelle/experimentelle Tests → tests/manual/
	•	Automatisierte, stabile Tests → tests/integration/

Teststrategie
	•	Nach dem Verschieben: pytest im Projektroot ausführen
	•	Es dürfen keine Import- oder Pfadfehler auftreten

Akzeptanzkriterien
	•	Projektroot enthält keine *.py-Testdateien mehr
	•	Alle automatisierten Tests funktionieren nach dem Umbau

Letzte Aktualisierung: 2025-06-21