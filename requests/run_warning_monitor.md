# Feature: Wettermonitor – positions- und etappenbasierte Warnprüfung

## Ziel

Erstelle ein Modul `scripts/run_warning_monitor.py`, das regelmäßig die aktuelle Wetterlage prüft – basierend auf:

- Der aktuellen GPS-Position (ShareMap)
- Der geplanten Etappe (Routenpunkte)
- Den bestehenden Tageswarnungen (state_tracking)

Nur bei neuer oder verschärfter Gefahr wird eine neue Warnung erzeugt.

---

## Ablauf

1. Hole aktuelle Position via `fetch_sharemap_position`
2. Hole geplante Etappe (z. B. über Konfig oder Dummy)
3. Analysiere beide Pfade mit `analyse_weather`
4. Vergleiche mit zuletzt gemeldetem Warnstatus
5. Bei neuer oder verschärfter Gefahr:
   - Erzeuge Text in `output/inreach_warnung.txt`
   - Optional: Logge Alarmzeit und Ursache

---

## Signifikante Änderung (default)

- Gewitterrisiko +20 %
- Regenrisiko +30 %
- Wind +10 km/h
- Hitze +2 °C
- Neue Wetterwarnung (Farbstufe ändert sich)

Diese Schwellen sind in `config.yaml` einstellbar

---

## Fehlerverhalten

- Wenn keine Position → nur Etappe prüfen
- Wenn keine Etappe → nur Position prüfen
- Wenn beides fehlt → Abbruch mit Log

---

## Umsetzung

- Datei: `scripts/run_warning_monitor.py`
- Hilfsmodul: `src/state/tracker.py` mit JSON-Speicher für Warnstatus

---

## Teststrategie

- Mockanalyse mit künstlichen Wetterdaten
- Vergleiche alter/neuer Zustand → nur bei Änderung erfolgt Textausgabe
- Tests: `tests/test_warning_monitor.py`