# Analyse-Anforderung: MeteoFrance API – Verfügbarkeit, Qualität, Fallback-Gründe

## 🎯 Ziel
Analysiere die Verwendung und Datenqualität der `meteofrance-api` im bestehenden System. Identifiziere, wann und warum auf den Fallback `open-meteo` zurückgegriffen wird. Dokumentiere die Auswirkungen auf Prognosegenauigkeit.

## 🧩 Konkrete Analysepunkte

1. **Verfügbarkeits-Check**
   - Wie oft wurde `meteofrance-api` erfolgreich verwendet in den letzten 14 Tagen?
   - Wie oft wurde auf `open-meteo` zurückgefallen?
   - Welche Ursachen wurden dabei geloggt? (Timeouts, Auth, HTTP-Fehler, Parsing)

2. **Qualitätsanalyse**
   - Für alle erfolgreichen `meteofrance-api` Responses:
     - Welche Werte fehlen auffällig oft? (`RainW%`, `Rainmm`, `Thund%`, `Gusts`)
     - Wie oft sind alle Werte gleichzeitig leer?
     - Gibt es API-Antworten mit strukturellen Auffälligkeiten (z. B. `null`, `"-"`, `"0"` überall)?
  
3. **Vergleich mit open-meteo**
   - Zeige vergleichend, welche Felder bei open-meteo befüllt sind, die bei meteofrance leer bleiben
   - Weist open-meteo systematisch höhere Werte auf (z. B. Gewitterwahrscheinlichkeit)?

4. **Fallback-Logik**
   - Wann genau erfolgt der Wechsel zu `open-meteo`?
   - Gibt es stille Fallbacks (ohne Log)?
   - Ist das Verhalten deterministisch (immer gleiche Ursache, gleiche Schwelle)?

5. **Logging-Check**
   - Wird die verwendete Quelle (`meteofrance` oder `open-meteo`) zuverlässig geloggt?
   - Falls nein: Ergänzen!

## ✅ Zieloutput

Eine Übersichtstabelle (z. B. CSV oder Markdown-Tabelle) mit:

- Datum, Etappe, API verwendet, Auslöser Fallback, fehlende Werte
- Ggf. Heatmap oder Prozentwerte für fehlende Felder nach Quelle

## 🔒 Einschränkungen

- Keine Änderung am Produktionsverhalten
- Nur Leserechte auf Logs/API-Responses
- Kein Upload echter API-Schlüssel

## ⏱ Zeitfenster

Analysezeitraum: Letzte 14 Tage (rollierend)