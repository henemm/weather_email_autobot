# 📄 .cursor/rules/debug_email_append.md

## Regel: DEBUG-Ausgabe als E-Mail-Anhang (bei DEBUG=true)

### Zweck
Ermöglicht die Analyse und Verifikation der verwendeten Wetterdaten durch tabellarische Ausgabe direkt unterhalb des Mailtexts – **nur wenn `DEBUG=true`** in `config.yaml`.

---

## 🔧 Aktivierungsbedingung

Nur aktiv, wenn folgender Config-Wert gesetzt ist:

```yaml
DEBUG: true
```

---

## 📌 Ausgabeort

- Direkt **am Ende des E-Mail-Textes**, **nicht** als MIME-Anhang
- Format: Klartext (`text/plain`)
- Kein Einfluss auf SMS-Ausgabe
- Nur bei E-Mail relevant

---

## 🧾 Inhalt der Debug-Ausgabe

Für **jeden verarbeiteten Wetterpunkt** (Etappenpunkt) werden folgende Informationen dargestellt:

1. **Headerzeile**:
   ```
   <Etappenpunkt-Name> (<Latitude>, <Longitude>) (<Tageskontext>)
   ```

2. **Tabellenstruktur** (ASCII-Format, monospaced):

   ```
   +-------+--------+--------+--------+--------+--------+--------+
   | Hour  |  Temp  | RainW% | Rainmm |  Wind  | Gusts  | Thund% |
   +-------+--------+--------+--------+--------+--------+--------+
   |  04   |  14.2  |   5.0  |   0.0  |   1.0  |   0.0  |   -    |
   |  05   |  14.0  |   5.0  |   0.0  |   1.0  |   0.0  |   -    |
   ...
   +-------+--------+--------+--------+--------+--------+--------+
   |  Min  |  13.7  |   5.0  |   0.0  |   1.0  |   0.0  |   -    |
   |  Max  |  15.2  |   5.0  |   0.0  |   2.0  |   0.0  |   -    |
   +-------+--------+--------+--------+--------+--------+--------+
   ```

3. **Timestamp-Zeile (optional)**:
   ```
   [TIMESTAMP-DEBUG] <Etappenpunkt-Name> | <Datum-Zeit> | Temp: XX.X°C | ...
   ```

---

## ⏲ Zeitlogik nach Berichtstyp

| Berichtstyp   | Zeitraum (lokal) | Beschreibung                                  |
|---------------|------------------|-----------------------------------------------|
| `morning`     | 04–22 Uhr        | Alle Punkte des heutigen Tages                |
| `evening`     | 22–05 Uhr (Nacht)| Letzter Punkt der heutigen Etappe (Nachtwerte)|
| `evening`     | 04–22 Uhr (Tag)  | Alle Punkte der morgigen Etappe               |
| `update`      | 04–22 Uhr        | Wie `morning`, abhängig vom Trigger-Zeitpunkt |

→ Es dürfen jederzeit **alle Stunden geladen werden**, jedoch werden nur o. g. Zeitbereiche im Bericht und Debug-Log verwendet.

---

## ⚠️ Einschränkungen

- Kein Einfluss auf den regulären Mailtext
- Nur bei DEBUG=true aktiv
- Keine MIME-Anhänge erzeugen
- Keine API-Keys oder interne Configs anzeigen

---

## ✍️ Beispielausgabe in E-Mail (am Ende)

```
--- DEBUG INFO ---
Croci Point 1 (41.93508, 9.20595) (morgen, Tag)
+-------+--------+--------+--------+--------+--------+--------+
| Hour  |  Temp  | RainW% | Rainmm |  Wind  | Gusts  | Thund% |
+-------+--------+--------+--------+--------+--------+--------+
|  04   |  14.2  |   5.0  |   0.0  |   1.0  |   0.0  |   -    |
|  05   |  14.0  |   5.0  |   0.0  |   1.0  |   0.0  |   -    |
...
+-------+--------+--------+--------+--------+--------+--------+
|  Min  |  13.7  |   5.0  |   0.0  |   1.0  |   0.0  |   -    |
|  Max  |  15.2  |   5.0  |   0.0  |   2.0  |   0.0  |   -    |
+-------+--------+--------+--------+--------+--------+--------+
```