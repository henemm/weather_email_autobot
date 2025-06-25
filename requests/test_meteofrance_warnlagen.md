# requests/test_meteofrance_warnlagen.md

## Titel
Validierung der meteofrance-api bei komplexen Warnlagen

## Ziel
Sicherstellen, dass das System bei instabilen oder widersprüchlichen Wetterlagen
– wie typischen Sommergewittern – zuverlässig interpretiert und korrekte Berichte erstellt.

## Vorgehen

1. **Ortsspezifischer Test:**
   Wähle französische Orte mit aktueller Wetterwarnung (gelb/orange/rot) aus folgenden Kategorien:
   - Gewitter ("thunderstorm")
   - Starkregen oder Überschwemmung
   - Wind

2. **Live-Abfrage via meteofrance-api:**
   Für jeden Ort werden folgende Daten abgefragt:
   - `forecast()` (stundenweise)
   - `daily_forecast()` (für aggregierte Tagesinformationen)
   - `risk_levels()` (Vigilance-Farbcodes)
   - `warnings()` (Textbeschreibung, falls vorhanden)

3. **Analysezeitraum:**
   - Abfragen für den aktuellen Tag (heute), morgen und übermorgen
   - Insbesondere Fokus auf Zeitfenster mit starker Änderung oder widersprüchlicher Lage

4. **Validierungskriterien:**
   - Sind die `risk_levels` konsistent mit `warnings`?
   - Wird `thunderstorm: true` korrekt gesetzt im Vergleich zur offiziellen Webseite?
   - Stimmen Tageswarnungen mit stündlichen Risiken überein?
   - Wird der Text der Warnung korrekt verarbeitet (falls Text-Ausgabe aktiv ist)?

5. **Systemprüfung:**
   Simuliere die Mailausgabe (Abend- und Morgenbericht) mit den erhaltenen Daten:
   - Wurden die Schwellenwerte korrekt erkannt?
   - Wird ein Warnhinweis generiert, falls `warning_level` ≥ `warn_thresholds.warning`?

## Testdaten
- Orte mit bekannter Sommergewitterlage (z. B. Pau, Grenoble, Lyon)
- Validierung gegen offizielle Webseite von Météo France

## Ergebnisdokumentation
- Bericht über erkannte Warnlagen und Systemreaktion
- Abgleich mit Webseite: Screenshot + API-Ausgabe
- Klarer Hinweis auf etwaige Abweichungen oder Fehlinterpretationen

## Akzeptanzkriterien
- Keine Inkonsistenz zwischen risk_levels und warnings
- "Thunderstorm" in API wird zuverlässig erkannt und ausgegeben
- Schwellenwerte aus `config.yaml` greifen wie erwartet
- Bericht spiegelt die realen Warnlagen korrekt wider

## Status
🟡 Offen – Ausführung durch Tester notwendig