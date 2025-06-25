# Live-Ende-zu-Ende-Test für geplanten GR20-Wetterbericht

Ziel: Simulation eines vollständigen Durchlaufs des GR20-Warnsystems unter realitätsnahen Bedingungen. Basis ist die zweite Etappe aus der `etappen.json`.

---

## 🌄 Etappen-Logik (Quelle: etappen.json)

Die aktuelle Etappe wird aus dem Tagesdatum berechnet. Für diesen Test wird **Etappe 2** verwendet. Die Datei enthält:

- Start- und Zielkoordinaten
- Routenpunkte als Liste von Koordinaten
- Tagesdatum

---

## 🧭 Geodaten-Auswertung (Quelle: Projektspezifikation.md)

Die Wetterevaluation erfolgt **nicht nur für das Etappenziel**, sondern:

- **Regenwahrscheinlichkeit, Niederschlagsmenge, Wind, Hitze, Gewitterwahrscheinlichkeit:**
  → Aggregation über **alle Punkte** der Etappe
  → Maximalwert + Uhrzeit der Schwellenüberschreitung

- **Nachttemperatur:**
  → Einzelwert des **letzten Punkts der Etappe**
  → Nur im Abendbericht

Diese Logik entspricht der Aggregationstabelle in `Projektspezifikation.md`.

---

## 🕖 Zeitpunkte und Modi

- **04:30 UTC:** Morgenbericht
- **19:00 UTC:** Abendbericht
- **Alle 30 Min (max. 3x):** Tageswarnung bei signifikanter Verschlechterung

---

## 📤 Versand

- **Kanal:** E-Mail (an SOTAmāt)
- **Zielgerät:** Garmin InReach Messenger (via Satellit)
- **Format:** Nur Kurzversion, max. 160 Zeichen, **ohne Link**, **ohne Emoji**

---

## 🔍 Ziel des Tests

- Validierung, dass Position und Etappe korrekt bestimmt werden
- Sicherstellung, dass nur erlaubte Inhalte (kein Link, kein Emoji) gesendet werden
- Korrekte Aggregation der Wetterdaten über die gesamte Etappe
- Versand zur korrekten Zeit über SMTP

---

## 🛠️ Vorbereitung

- Setze Umgebungsvariablen: GMAIL_APP_PW, METEOFRANCE_CLIENT_ID, METEOFRANCE_CLIENT_SECRET
- Stelle sicher, dass der Token-Provider aktiv ist
- Führe das Hauptskript aus:
  ```bash
  python scripts/run_gr20_weather_monitor.py --modus abend

✅ Erfolgskriterien
	•	E-Mail wird versendet
	•	Betreff enthält korrekte Etappenbezeichnung
	•	Inhalt entspricht Kurzformat ohne Link/Emoji
	•	Wetterdaten wurden korrekt aggregiert
	•	Etappe 2 wurde verwendet (nicht nur letzter Punkt)
