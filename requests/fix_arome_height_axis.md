# 🛠️ AROME WCS: Fehlerhafte Höhenachse korrigieren

## Ziel
Die Abfrage des AROME-Hauptmodells (AROME_HR) über WCS schlägt fehl, da die Höhenachse („height“) im Request nicht korrekt spezifiziert ist. Dies führt zu einem `InvalidSubsetting`-Fehler und blockiert die Hauptquelle für Prognosewerte.

## Problem
- API-Fehler: `InvalidSubsetting - locator="height"`
- Ursache: Der WCS-Request enthält eine ungültige oder nicht unterstützte Höhenachse (z. B. „0“ oder kein Wert)
- Folge: AROME-Daten (z. B. CAPE, SHEAR, Temperatur) sind vollständig blockiert

## Lösung
### Regeln für die Höhe (aus GetCapabilities / WCS-Spezifikation):
- Höhe muss exakt dem Layerprofil entsprechen
- Häufig verwendete Höhe: `surface` oder explizit `2` für 2 m über Grund
- Höhe ist keine Pflichtachse für alle Parameter – ggf. weglassen

## Umsetzung

### Schritt 1: Dynamisches Parsen erlaubter Höhenwerte
- Die Funktion zum Parsen von Layern aus GetCapabilities soll neben TimeAxis und BBox auch Height-Axis erkennen und speichern.
- Beispiel:
  ```python
  layer['heights'] = [2.0, 10.0]  # wenn vorhanden

### Schritt 2: Validierung beim Datenabruf
	•	Vor Abfrage prüfen: Unterstützt der Layer überhaupt eine Höhenachse?
	•	Falls nicht → height-Parameter weglassen
	•	Falls ja → height=2 oder surface nur setzen, wenn exakt erlaubt

### Schritt 3: Logging und Fallback
	•	Fehlerhafte Höhenangabe mit Warnung loggen, aber nicht crashen
	•	Falls Fehler: Retry ohne Höhe

## Teststrategie
	•	Unit-Test: Höhenparser (validiert Höhenachse aus GML/WCS)
	•	Integrationstest: Live-Abruf für Layer mit und ohne Höhenachse
	•	Fehlerprüfung: AROME mit gültiger Höhe abrufbar

## Akzeptanzkriterien
	•	AROME_HR-Daten erfolgreich abrufbar für Temperatur, CAPE, SHEAR
	•	Kein Absturz bei unbekannter oder nicht vorhandener Höhe
	•	WCS-Request enthält Höhe nur wenn erforderlich und gültig

Letzte Aktualisierung: 2025-06-21