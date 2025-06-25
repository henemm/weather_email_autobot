# Logging-Infrastruktur für das GR20-Wettersystem

## 🎯 Ziel
Einheitliches, strukturiertes Logging für alle Hauptmodule des Systems zur besseren Fehlerdiagnose und Nachvollziehbarkeit.

## 📦 Anwendungsbereiche
Folgende Module müssen Logging verwenden:
- Wetterdatenabruf (z. B. AROME, OpenMeteo, Vigilance)
- Wetteranalyse (z. B. Schwellenwertprüfung, Risikobewertung)
- Report-Erstellung und Versand
- Scheduler (z. B. Auslösezeitpunkte, Prüfbedingungen)

## 🔧 Anforderungen

### Logging-Konfiguration
- Einrichtung zentraler Logging-Konfiguration in z. B. `src/utils/logging_setup.py`
- Ausgabeformat:
  [%(asctime)s] [%(name)s] [%(levelname)s] %(message)s
- Level: Standardmäßig `INFO`, bei Bedarf `DEBUG` aktivierbar.
- Ausgabeziel:
  - Datei: `logs/warning_monitor.log`
  - Optional: Konsole (für Entwicklung)

### Modul-Logging
- Jedes Modul initialisiert `logger = logging.getLogger(__name__)`
- Verwendung:
  - `logger.info("Normaler Ablauf ...")`
  - `logger.warning("Auffälligkeit ...")`
  - `logger.error("Fehler: ...")`

### Fehlerverfolgung
- Fehlerhafte API-Aufrufe, Parsing-Probleme, Scheduler-Konflikte etc. müssen protokolliert werden.
- Bei nicht-kritischen Fehlern `warning`, bei Abstürzen `error`.

### Testbarkeit
- Es existieren Unit-Tests, die prüfen:
  - Logging-Datei wird erstellt
  - Logging enthält erwartete Einträge bei Fehlern und normalen Abläufen

## 📁 Ergebnisstruktur
- `src/utils/logging_setup.py`: Logging-Initialisierung
- `logs/warning_monitor.log`: Logdatei
- Logging in allen relevanten Modulen integriert

## ⏱️ Deadline
Sofortige Umsetzung möglich, kritisch für Produktionsreife.