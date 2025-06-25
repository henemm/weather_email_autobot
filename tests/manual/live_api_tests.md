# 🧪 Live-API-Testplan für GR20-Wettersystem

Dieser Testplan definiert eine manuelle Validierungsstrategie für alle produktiven Schnittstellen. Ziel ist die stufenweise Prüfung von Einzelzugriffen, Datenaggregation und End-to-End-Verarbeitung.

---

## 1️⃣ Einzel-API-Livetests (7 APIs)

Jede API wird einzeln mit einem realistischen Punkt auf Korsika (z. B. Conca) getestet.

| API-Modell           | Testziel                                       | Beispiel-Koordinaten  |
|-----------------------|-----------------------------------------------|------------------------|
| AROME_HR              | Temperatur, CAPE, SHEAR                        | 41.75, 9.35            |
| AROME_HR_NOWCAST      | Niederschlagsrate, Sichtweite (15min Intervall)| 41.75, 9.35            |
| AROME_HR_AGG          | 6h-Regenaggregat (Summe)                       | 41.75, 9.35            |
| AROME_IFS             | Prognose >42h (Langfristprüfung)              | 41.75, 9.35            |
| PIAF_NOWCAST          | Starkregen-Nowcast (5min-Zeitreihe)           | 41.75, 9.35            |
| VIGILANCE_API         | Aktuelle Gewitterwarnstufe für 2B             | Département „2B“       |
| OPENMETEO_GLOBAL      | Temperatur, Regen (als Fallback)              | 41.75, 9.35            |

### ✅ Erfolgskriterien

- HTTP-Status 200 oder gültige JSON/GML/XML-Response
- mind. 1 valider Wetterwert pro API (z. B. Temperatur, CAPE)
- bei Fehler: strukturierte Fehlermeldung (nicht Absturz)

---

## 2️⃣ Aggregierter Wetterbericht (Analysefunktion)

Funktion: `analyse_weather(lat, lon)`

### Testziel

Prüft, ob bei aktiver API-Abfrage aus den Einzeldaten ein valider Risiko-Score für Gewitter erstellt wird (inkl. Logging, Schwellen, Priorisierung).

### Erfolgskriterien

- Validierter Schwellenwert: CAPE*SHEAR, Blitz, Regen
- Entscheidungsbaum greift korrekt (config.yaml)
- Warnstufe und Entscheidungsgrund vorhanden

---

## 3️⃣ End-to-End-Test: GR20 Live-Wetterbericht

Skript: `scripts/run_gr20_weather_monitor.py`

### Testziel

Kompletter Ablauf: Positionsbestimmung ➝ API-Aufrufe ➝ Risikoanalyse ➝ E-Mail-Formulierung ➝ E-Mail-Versand (Simulation)

### Setup

- Umgebungsvariablen: alle Tokens (WCS, NOWCAST, PIAF, VIGILANCE), GMAIL_APP_PW
- Etappe: Etappe 2 in `etappen.json` (automatisch)
- config.yaml vollständig geladen

### Erfolgskriterien

- Ausgabe: Konsolenbericht mit Inhalt (max. 160 Zeichen)
- Inhalt enthält: Region, Temperatur, Gewitterwarnung, Risiko
- kein Crash trotz Teil-API-Ausfällen (Fallback sichtbar)

---

Letzte Aktualisierung: 2025-06-21