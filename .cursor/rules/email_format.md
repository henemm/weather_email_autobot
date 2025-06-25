# .cursor/rules/email_format.md

## 📬 Formatregel: Wetterberichte per E-Mail (für InReach, max. 160 Zeichen)

Diese Regel beschreibt den exakten Aufbau der Wetterberichte in den drei Betriebsmodi: **Morgenbericht (z.B. 04:30)**, **Abendbericht (z.B. 19:00)** und **Zwischenbericht (dynamisch bei Risikoänderung)**.

### Technische Vorgaben

- Maximallänge: 160 Zeichen
- Zeichensatz: Nur ASCII (keine Emojis, Links, Sonderzeichen)
- Zeitformat: Alle Uhrzeiten lokal (CEST)
- Quelle: meteofrance-api, Fallback: open-meteo
- Schwellenwerte: Aus `config.yaml`
- Etappen: Bestimmung über `etappen.json` basierend auf Datum
- der Versand wird über crontab geregelt und ist nicht Teil des Programmcodes. Es muss lediglich sichergestellt werden, dass es die drei unterschiedlichen Formate gibt und dass diese per "--befehl" gesteuert werden können

---

## 🕓 Morgenbericht (z.B. 04:30 Uhr)

### Inhalt
- Gilt für den aktuellen Tag
- Zeitraum: 05:00–17:00 CEST
- Geopunkte: alle Punkte der heutigen Etappe
- Aggregierung: Maximalwerte über Zeit und Geopunkte

### Format
{EtappeHeute} | Gew.{g1}%@{t1}(max.{g1_max}%@{t1_max}) | Regen{r1}%@{t3}(max.{r1_max}%@{t3_max}) | Regen{regen_mm}mm@{t5}(max.{regen_max}mm@{t5_max}) | Hitze{temp_max}°C | Wind{wind_max}km/h | Gew.+1{g1_next}%

### Erläuterung
- {g1}@{t1}: Höchste Gewitterwahrscheinlichkeit
- {g2}@{t2}: Zeitpunkt, an dem Schwellenwert für Gewitter überschritten wird (z. B. 30%)
- {g1_next}: Gewitterwahrscheinlichkeit für morgen (nächster Tag)
- {r1}@{t3}: Höchste Regenwahrscheinlichkeit
- {r2}@{t4}: Zeitpunkt, an dem Schwellenwert für Regen überschritten wird (z. B. 50%)
- {regen_mm}: Tagesmaximalsumme Regen
- {temp_max}: Tageshöchsttemperatur
- {wind_max}: Maximaler Wind
- {vigilance_warning}: Höchste Vigilance-Warnung (z.B. "ORANGE Gewitter", "ROT Waldbrand") oder leer

---

## 🌙 Abendbericht (19:00 Uhr)

### Inhalt
- Gilt für morgen und übermorgen
- Zeitraum: jeweils 05:00–17:00 CEST
- Geopunkte: alle Punkte der jeweiligen Etappe
- Aggregierung: Maximalwerte über Zeit und Geopunkte

### Format
{EtappeMorgen}→{EtappeÜbermorgen} | Nacht{min_temp}°C | Gew.{g1}%@{t1}(max.{g1_max}%@{t1_max}) | Gew.+1{g1_next}% | Regen{r1}%@{t3}(max.{r1_max}%@{t3_max}) | Regen{regen_mm}mm@{t5}(max.{regen_max}mm@{t5_max}) | Hitze{temp_max}°C | Wind{wind_max}km/h | {vigilance_warning}

### Erläuterung
- {EtappeMorgen}: Name der morgigen Etappe
- {min_temp}: Nachttemperatur (Minimum aus Etappenstartpunkt morgen, Zeitraum 22–05 Uhr)
- {g1}@{t1}: Gewitterwahrscheinlichkeit morgen
- ({g2}@{t2}): Zeitpunkt mit Schwellenwertüberschreitung (wenn vorhanden)
- {g1_next}: Gewitterwahrscheinlichkeit für übermorgen (übernächster Tag)
- {r1}@{t3}: Regenwahrscheinlichkeit morgen
- ({r2}@{t4}): Zeitpunkt mit Schwellenwertüberschreitung (wenn vorhanden)
- {regen_mm}: Regenmenge morgen (Maximalsumme aller Geopunkte)
- {temp_max}: Höchsttemperatur morgen
- {wind_max}: Windspitze morgen
- {vigilance_warning}: Höchste Vigilance-Warnung (z.B. "ORANGE Gewitter", "ROT Waldbrand") oder leer

---

## 🚨 Zwischenbericht

### Anlass
Wird nur ausgelöst durch signifikante Änderung der Gefahrenlage für den laufenden Tag (z. B. neuer Schwellenwert überschritten um in config.yaml angegebenen Prozentwert). Er gibt ausschließlich die stark geänderten Werte aus. Es werden maximal 3 Zwischenberichte pro Tag verschickt. 

### Format
{EtappeHeute} | Update: | Gew.{g2}@{t2} | Regen{r2}@{t4} | Regen{regen_mm}mm@{t5} | Hitze{temp_max}°C | Wind{wind_max}km/h | {vigilance_warning}

---

## 📝 Abkürzungen und Formatierung

### Abkürzungen
- **Gewitter** → **Gew.**
- **Regenmenge** → **Regen** (wird über "%" bzw. "mm" unterschieden)
- **Etappennamen** → Abgekürzt auf max. 10 Zeichen (Format: "Startort→Zi" für "Startort→Zielort")

### Formatierung
- Keine Leerzeichen zwischen Elementen (kompakte Darstellung)
- Schwellenwert@Zeit (max. Maximum@Zeit) für alle Werte
- Beispiel: "Gew.30%@13:00(max.80%@15:00)"

### Schwellenwerte
- Regenwahrscheinlichkeit: 25% (aus `config.yaml` → `thresholds.regen_probability`)
- Gewitterwahrscheinlichkeit: 20% (aus `config.yaml` → `thresholds.thunderstorm_probability`)
- Regenmenge: 2.0mm (aus `config.yaml` → `thresholds.regen_amount`)
- Windgeschwindigkeit: 20 km/h (aus `config.yaml` → `thresholds.wind_speed`)
- Temperatur: 32°C (aus `config.yaml` → `thresholds.temperature`)

---

## 📊 Beispielberichte

### Morgenbericht
```
Startdorf→Wa|Gew.30%@13:00(max.80%@15:00)|Regen55%@15:00(max.55%@15:00)|Regen2.0mm@15:00(max.6.0mm@15:00)|Hitze28.0°C|Wind25km/h|Gew.+180%
```
Länge: 138 Zeichen

### Abendbericht
```
Waldpass→Al|Nacht15.5°C|Gew.40%@14:00(max.95%@17:00)|Gew.+190%|Regen50%@14:00(max.70%@17:00)|Regen2.0mm@14:00(max.8.0mm@17:00)|Hitze33.5°C|Wind38km/h
```
Länge: 149 Zeichen

### Zwischenbericht
```
Almhütte→Gi|Update:|Gew.35%@15:00|Regen55%@16:00|Regen2.0mm@15:00|Hitze29.1°C|Wind31km/h
```
Länge: 88 Zeichen 