🧪 Tests: Fehlerhafte Importe durch fehlenden PYTHONPATH korrigieren

Ziel

Die Testumgebung soll alle Dateien aus dem src/-Verzeichnis korrekt importieren können, insbesondere from src.xyz import ….

Problem
	•	Fehler: ModuleNotFoundError: No module named 'src'
	•	Ursache: Beim Testen fehlt die PYTHONPATH-Konfiguration
	•	Folge: Tests wie tests/test_arome_wcs.py schlagen fehl

Lösung

Option 1: pytest.ini mit Pfadkonfiguration erstellen

Datei pytest.ini ins Projektroot legen mit folgendem Inhalt:

[pytest]
python_paths = src

Option 2: conftest.py im tests/-Verzeichnis mit sys.path-Anpassung

import sys  
import os  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

Empfohlen: Beide Varianten kombinieren für maximale Kompatibilität

Teststrategie
	•	Lokaler Test: pytest tests/ ausführen
	•	Alle import src.* Statements sollen ohne Fehler funktionieren
	•	Auch pytest -s und CI-Ausführung muss funktionieren

Akzeptanzkriterien
	•	Keine ModuleNotFoundError bei allen Tests
	•	Tests in tests/test_arome_*.py lauffähig

Letzte Aktualisierung: 2025-06-21