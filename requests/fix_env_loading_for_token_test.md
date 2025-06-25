# Titel
Fix: .env wird in Tests nicht automatisch geladen

# Problem
In den Tests wird auf Umgebungsvariablen wie METEOFRANCE_WCS_TOKEN zugegriffen. Obwohl die Variable korrekt in der .env-Datei definiert ist, liefert os.getenv() in den Tests None oder einen veralteten Wert, solange dotenv nicht aktiv geladen wird.

# Ziel
Stelle sicher, dass in allen relevanten Tests (z. B. demo_check_wms_capabilities.py und test_token_validity.py) automatisch die .env-Datei geladen wird, damit alle Umgebungsvariablen zuverlässig verfügbar sind.

# Umsetzungsvorgaben
- Nutze python-dotenv
- Füge `from dotenv import load_dotenv; load_dotenv()` am Anfang jedes betroffenen Test-Skripts ein
- Alternativ: extrahiere die gemeinsame Lade-Logik in eine Hilfsfunktion (z. B. tests/utils/env_loader.py)
- Tests sollen beim Start den korrekten Token aus .env verwenden und nicht auf Fallbacks zurückgreifen
- Sicherstellen, dass bei lokalem Start via CLI `.env` zuverlässig geladen wird
- Testfall: demo_check_wms_capabilities.py muss 200 zurückgeben, wenn der Token korrekt ist

# Prüfungskriterium
Nach Umsetzung muss demo_check_wms_capabilities.py bei korrektem Token aus .env erfolgreich ausgeführt werden (HTTP 200).