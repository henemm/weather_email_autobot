# 📡 request/analyse_meteofrance_fields.md

## 🎯 Ziel

Identifikation und Dokumentation aller systematischen Schwächen und Nicht-Funktionalitäten der MeteoFrance-API-Integration innerhalb des Systems. Ziel ist es, die Ursachen für fehlerhafte, fehlende oder nicht verwendete Felder zu analysieren und systematisch zu isolieren.

---

## 🔍 Prüfkategorien

### 1. Feldverfügbarkeit im API-Response
Für jeden API-Aufruf:
- Welche Datenfelder **sind vorhanden**, welche **fehlen vollständig**?
- Beispielhafte Felder:
  - `temperature`
  - `wind_speed`, `wind_gust`
  - `precipitation_sum`, `precipitation_probability`
  - `thunderstorm_probability`
  - `alerts` (mit Unterfeldern: type, level, zone)

### 2. Feldinhalt (Wertelogik)
- Enthaltene Felder: Sind die Werte **plausibel** (nicht `"0"`, `"null"`, `"undefined"` oder systematisch fehlerhaft)?
- Beispiel:
  - Sind `0°C`-Werte bei Hochsommer systematisch → Datenfehler oder API-Spezifikum?

### 3. Request-Parameter und API-Endpunkte
- Welche **API-Endpunkte** wurden genutzt (`forecast`, `vigilance`, etc.)?
- Welche **Parameter** wurden gesendet?
- Stimmen API-Version und Dokumentation mit der tatsächlichen Verwendung überein?

### 4. Filtersystem & Validierungslogik
- Gibt es interne Schwellenwerte oder Filter, die verhindern, dass Daten übernommen werden?
- Beispiel:
  - Temperatur < 2°C → wird als ungültig verworfen → Fallback
  - Wahrscheinlichkeitsfeld fehlt → ganzer API-Wert ignoriert

### 5. Alerts-Verarbeitung
- Ist die Alerts-Struktur seitens API konsistent?
- Parsing-Fehler: Welche Felder fehlen oder sind anders benannt?
- Mapping der Warnstufen korrekt?

---

## 🧪 Teststrategie

- Nutze real gespeicherte API-Responses der letzten 14 Tage (`logs/api/`)
- Erstelle **vergleichbare Logs** für Open-Meteo bei gleicher Zeit/Location
- Dokumentiere je Tag, GEO-Point, Report-Typ (morning/evening/update):
  - Was wurde von MeteoFrance geliefert?
  - Was wurde verworfen oder überschrieben?
  - Warum kam ein Fallback zustande?

---

## 🗃️ Output

Erstelle folgende Dateien:
- `field_matrix_meteofrance.csv`: Übersicht je Feld, Tag, GEO, verfügbar/fehlerhaft
- `fallback_reason_log.csv`: Liste aller Fallbacks mit Grund
- `alerts_parsing_issues.csv`: Mapping-Probleme bei Warnungen
- `api_usage_breakdown.md`: Übersicht genutzter Endpunkte & Parameter

---

## 🛑 Hinweis

Fehlerquellen **nicht** bei MeteoFrance suchen, sondern:
- Im Code (Parsing, Validierung, Feld-Namen)
- In der meteofrance-api-Library
- In zu restriktiven System-Regeln

---

## 🧾 Ziel der Analyse

Diese Analyse ist **nicht zur Behebung** gedacht, sondern zur **sauberen Problemabgrenzung**.