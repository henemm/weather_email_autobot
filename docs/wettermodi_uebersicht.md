# Wetterbericht-Modi Übersicht

Diese Datei beschreibt, welche Wetterdaten im jeweiligen Modus verwendet werden und von welchen Etappenpunkten sie berechnet werden.

---

## Nullwertregel & Etappennamen

- Alle Wetterwerte, die 0 oder leer sind, werden als „-” ausgegeben (keine Zeitangaben, keine Einheiten, keine Maximalwerte).
- Im Abendmodus steht immer die morgige Etappe im Betreff und im Text.
- Keine führenden Nullen, keine leeren Dezimalstellen.

---

## 1. Abendmodus (`--modus abend`)

| Faktor                     | Quelle                                          | Beschreibung                                                                 |
|---------------------------|--------------------------------------------------|------------------------------------------------------------------------------|
| Gefühlte Nachttemperatur  | Letzter Punkt der **heutigen** Etappe           | Wie kalt es nachts am Schlafplatz wird                                      |
| Gefühlte Tageshitze       | Alle Punkte der **morgigen** Etappe             | Max. gefühlte Temperatur am nächsten Tag                                    |
| Regenrisiko               | Alle Punkte der **morgigen** Etappe             | Regenrisiko mit Zeitpunkt (z. B. `15%@10(max 45%@15)`)                      |
| Wind                      | Alle Punkte der **morgigen** Etappe             | Höchster Windwert                                                            |
| Gewitterrisiko morgen     | Alle Punkte der **morgigen** Etappe             | Gewitterrisiko mit Zeitpunkt (z. B. `20%@11(max 50%@16)`)                   |
| Gewitterrisiko übermorgen | Alle Punkte der **übernächsten** Etappe         | Früher Zeitpunkt & Max-Wert mit Uhrzeit                                     |

---

## 2. Morgenmodus (`--modus morgen`)

| Faktor                     | Quelle                                          | Beschreibung                                                                 |
|---------------------------|--------------------------------------------------|------------------------------------------------------------------------------|
| Gefühlte Tageshitze       | Alle Punkte der **heutigen** Etappe             | Max. gefühlte Temperatur des Tages                                           |
| Regenrisiko               | Alle Punkte der **heutigen** Etappe             | Regenrisiko mit Zeitpunkt                                                    |
| Wind                      | Alle Punkte der **heutigen** Etappe             | Höchster Windwert                                                            |
| Gewitterrisiko heute      | Alle Punkte der **heutigen** Etappe             | Gewitterrisiko mit Uhrzeit                                                   |
| Gewitterrisiko morgen     | Alle Punkte der **morgigen** Etappe             | Gewitterrisiko mit Uhrzeit                                                   |

> **Hinweis:** Keine Nachttemperatur, da vergangen. Nullwerte werden als „-” ausgegeben.

---

## 3. Tageswarnung (`--modus tag`)

| Faktor                     | Quelle                                          | Beschreibung                                                                 |
|---------------------------|--------------------------------------------------|------------------------------------------------------------------------------|
| Gefühlte Tageshitze       | Alle Punkte der **heutigen** Etappe             | Wenn aktueller Wert über Schwelle gestiegen                                 |
| Regenrisiko               | Alle Punkte der **heutigen** Etappe             | Wenn aktueller Wert höher als morgens, inkl. Zeitpunkt                       |
| Wind                      | Alle Punkte der **heutigen** Etappe             | Wenn aktueller Wert höher als morgens                                        |
| Gewitterrisiko            | Alle Punkte der **heutigen** Etappe             | Wenn Schwellwert überschritten oder stärker als morgens                      |

> Diese Warnung wird **nur bei signifikanter Verschlechterung** gesendet. Nullwerte werden als „-” ausgegeben.

---

## Beispiele (kompakt, Nullwertregel)

### Abendmodus – InReach kompakt

```
Hiddesen | Nacht 18.3°C | Gewitter - | Regen - | Hitze 22.2°C | Wind 17km/h | Gewitter +1 -
```

### Morgenmodus – InReach kompakt

```
Stieghorst | Gewitter - | Regen48%@9(max 100%@15) 2mm@15(max 2mm@15) | Hitze 24.6°C | Wind 30km/h | Gewitter +1 -
```

### Tageswarnung – InReach kompakt

```
Stieghorst | Update: Gewitter 35%@15 | Regen 55%@16 | Hitze 29.1°C | Wind 31km/h
```

---

## Technische Hinweise

- **Schwellenwerte:** Werden ausschließlich in `config.yaml` definiert
- **Zeitformat:** Intern UTC/Europe/Paris, Darstellung vereinfacht
- **Datenquellen:** System ist offen für verschiedene Wetterdatenquellen
- **Crontab:** Modi werden über geplante Jobs gesteuert
- **Format:** InReach-Nachrichten max. 160 Zeichen, keine Emojis
