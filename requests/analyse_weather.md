# Feature: Wetterdaten analysieren

## Ziel

Erstelle ein Modul `src/logic/analyse_weather.py`, das ein `WeatherData`-Objekt (z. B. von AROME) analysiert und potenziell gefährliche Wetterbedingungen erkennt.

---

## Eingabe

- `weather_data: WeatherData` (siehe `model/datatypes.py`)
- `config: Dict` mit Schwellenwerten aus der Konfiguration

---

## Rückgabe

Ein `WeatherAnalysis`-Objekt mit:
- `risks: List[WeatherRisk]`  
- `max_thunderstorm_probability`, `max_precipitation`, `max_wind_speed` etc.  
- `summary: str` (kompakte Zusammenfassung)

---

## Erkennungskriterien

Analysiere alle Punkte auf:
- Niederschlagsmenge über Schwellwert (z. B. 2 mm)
- Regenwahrscheinlichkeit (falls vorhanden)
- Windgeschwindigkeit (z. B. > 40 km/h)
- Bewölkung > 90 %
- Temperatur > 30 °C
- CAPE * SHEAR > definierter Schwellenwert (falls beide verfügbar)

---

## Anforderungen

- Alle Funde als `WeatherRisk` mit Typ, Schweregrad und Zeitfenster dokumentieren
- Maximalwerte extrahieren (für Report-Zusammenfassung)
- `config`-Werte flexibel überschreibbar
- Kein Logging oder I/O

---

## Ablage

- Code: `src/logic/analyse_weather.py`
- Tests: `tests/test_analyse_weather.py`  
  - Szenarien: starkes Gewitter, leichter Regen, Windwarnung, etc.

# Feature: Risikoanalyse auf Basis mehrerer Wettermodelle (Worst-Case-Prinzip)

## Ziel

Ermögliche die Risikoanalyse über mehrere Wetterdatenquellen hinweg (z. B. AROME, ECMWF), wobei immer das Maximum an Risiko bewertet wird. Ziel ist es, wetterbedingte Gefahren im Sinne des Vorsichtsprinzips niemals zu unterschätzen.

---

## Neue Anforderungen (Erweiterung)

### Eingabe

- `List[WeatherData]` (z. B. aus AROME, ECMWF)
- Typisch zwei Quellen, aber beliebig erweiterbar

### Vorgehen

- Für jeden Zeitpunkt wird der “risikoreichste” Messpunkt (z. B. höchste Regenmenge, höchste CAPE-Werte etc.) verwendet
- Gewichte, Schwellen und Scores bleiben wie bisher
- Duplizierte Zeitpunkte aus verschiedenen Quellen werden zusammengeführt zum höchsten Wert

### Ausgabe

- Weiterhin `RegenAnalyse` und `WeatherReport` (wie gehabt)

---

## Hinweise

- Quellen können sich in Zeitauflösung unterscheiden – Interpolation nicht nötig
- Doppelte Zeitstempel sind erlaubt, es zählt der “gefährlichste”
- Bei Abwesenheit von Daten einer Quelle wird diese ignoriert, aber der Worst Case bleibt gültig  