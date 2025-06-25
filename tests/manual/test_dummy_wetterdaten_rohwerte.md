# tests/manual/test_dummy_wetterdaten_rohwerte.md

## Ziel
Rohdatenbasierte Validierung der Wetterberichterstellung.
3 Etappen × 3 Tage × 2 Geopunkte pro Etappe.

## Testdefinition

### Etappe 1: Startdorf → Waldpass (Tag 1)

| Uhrzeit | Punkt | Temp (°C) | Regen % | Regen mm | CAPE | Wind (km/h) | Blitz % |
|---------|-------|-----------|----------|------------|--------|----------------|-----------|
| 05:00   | A     | 13.2      | 0        | 0          | 50     | 10             | 5         |
| 08:00   | A     | 17.0      | 10       | 1          | 150    | 15             | 10        |
| 13:00   | A     | 25.0      | 35       | 3          | 400    | 20             | 30        |
| 15:00   | B     | 27.0      | 55       | 6          | 800    | 25             | 80        |
| 17:00   | B     | 28.0      | 10       | 1          | 100    | 15             | 20        |

---

### Etappe 2: Waldpass → Almhütte (Tag 2)

| Uhrzeit | Punkt | Temp (°C) | Regen % | Regen mm | CAPE | Wind (km/h) | Blitz % |
|---------|-------|-----------|----------|------------|--------|----------------|-----------|
| 06:00   | C     | 15.5      | 5        | 0          | 100    | 8              | 5         |
| 08:00   | D     | 20.0      | 30       | 2          | 200    | 10             | 15        |
| 14:00   | D     | 30.0      | 50       | 3          | 900    | 28             | 40        |
| 16:00   | C     | 32.0      | 60       | 5          | 1200   | 35             | 90        |
| 17:00   | D     | 33.5      | 70       | 8          | 1400   | 38             | 95        |

---

### Etappe 3: Almhütte → Gipfelkreuz (Tag 3)

| Uhrzeit | Punkt | Temp (°C) | Regen % | Regen mm | CAPE | Wind (km/h) | Blitz % |
|---------|-------|-----------|----------|------------|--------|----------------|-----------|
| 06:00   | E     | 12.3      | 0        | 0          | 80     | 10             | 5         |
| 10:00   | F     | 19.0      | 10       | 0.5        | 300    | 18             | 10        |
| 12:00   | E     | 22.0      | 20       | 1.5        | 400    | 25             | 15        |
| 15:00   | E     | 27.5      | 40       | 4.0        | 600    | 31             | 35        |
| 16:00   | F     | 29.1      | 55       | 6.0        | 700    | 28             | 40        |

---

## Verwendung

Diese Daten sollen genutzt werden, um die interne Logik der Berichterstellung zu testen:

- Aggregation von Max-Werten über Zeit & Geopunkte
- Erkennung von Schwellenwertüberschreitungen (z. B. Regen > 50%, Blitz > 30%, Regenmenge > 2mm)
- Auswahl der korrekten Werte für die Berichtsformate (Schwellenwert@Zeit und Maximum@Zeit)

---

## Formatregeln (AKTUALISIERT)
- **Gewitter:** Gew.{Schwellenwert}@{Zeit}(max.{Maximum}@{MaxZeit}) - z.B. "Gew.30%@13:00(max.80%@15:00)"
- **Regen:** Regen{Schwellenwert}@{Zeit}(max.{Maximum}@{MaxZeit}) - z.B. "Regen55%@15:00(max.55%@15:00)"
- **Regenmenge:** Regen{Schwellenwert}mm@{Zeit}(max.{Maximum}mm@{MaxZeit}) - z.B. "Regen2.0mm@15:00(max.6.0mm@15:00)"
- **Hitze:** Hitze{max. Temperatur}°C
- **Wind:** Wind{max. Windgeschwindigkeit}km/h
- **Gewitter +1:** Gew.+1{max. Gewitterwahrscheinlichkeit für nächsten Tag}%
- **Etappennamen:** Abgekürzt auf max. 10 Zeichen (Format: "Startort→Zi")

**Schwellenwerte:**
- Regenwahrscheinlichkeit: 50%
- Gewitterwahrscheinlichkeit: 30%
- Regenmenge: 2.0mm

---

### Bericht für morgen (Etappe 1)
```
Startdorf→Wa|Gew.30%@13:00(max.80%@15:00)|Regen55%@15:00(max.55%@15:00)|Regen2.0mm@15:00(max.6.0mm@15:00)|Hitze28.0°C|Wind25km/h|Gew.+180%
```
Länge: 138 Zeichen

---

### Bericht für übermorgen (Etappe 2)
```
Waldpass→Al|Nacht15.5°C|Gew.40%@14:00(max.95%@17:00)|Gew.+190%|Regen50%@14:00(max.70%@17:00)|Regen2.0mm@14:00(max.8.0mm@17:00)|Hitze33.5°C|Wind38km/h
```
Länge: 149 Zeichen

---

### Bericht für überübermorgen (Etappe 3)
```
Almhütte→Gi|Update:|Gew.35%@15:00|Regen55%@16:00|Regen2.0mm@15:00|Hitze29.1°C|Wind31km/h
```
Länge: 88 Zeichen

---

## Hinweise zur Validierung
- Die Schwellenwert-Zeitpunkte zeigen, wann der Schwellenwert das erste Mal überschritten wird (>=)
- Die Maximum-Zeitpunkte zeigen, wann der höchste Wert erreicht wird
- Regenmenge wird separat von Regenwahrscheinlichkeit behandelt
- Alle Werte stammen aus den Dummy-Rohdaten (siehe Test-Setup)
- Zeichenlimit: 160 Zeichen (alle Berichte liegen unter dieser Grenze)
- Kompakte Formatierung ohne Leerzeichen zwischen Elementen