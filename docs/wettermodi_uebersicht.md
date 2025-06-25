# Wetterbericht-Modi Übersicht

Diese Datei beschreibt, welche Wetterdaten im jeweiligen Modus verwendet werden und von welchen Etappenpunkten sie berechnet werden.

---

## 1. Abendmodus (`--modus abend`)

| Faktor                     | Quelle                                          | Beschreibung                                                                 |
|---------------------------|--------------------------------------------------|------------------------------------------------------------------------------|
| Gefühlte Nachttemperatur  | Letzter Punkt der **heutigen** Etappe           | Wie kalt es nachts am Schlafplatz wird                                      |
| Gefühlte Tageshitze       | Alle Punkte der **morgigen** Etappe             | Max. gefühlte Temperatur am nächsten Tag                                    |
| Regenrisiko               | Alle Punkte der **morgigen** Etappe             | Regenrisiko mit Zeitpunkt (z. B. `15%@10(45%@15)`)                           |
| Wind                      | Alle Punkte der **morgigen** Etappe             | Höchster Windwert                                                            |
| Gewitterrisiko morgen     | Alle Punkte der **morgigen** Etappe             | Gewitterrisiko mit Zeitpunkt (z. B. `20%@11(50%@16)`)                        |
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

> **Hinweis:** Keine Nachttemperatur, da vergangen.

---

## 3. Tageswarnung (`--modus tag`)

| Faktor                     | Quelle                                          | Beschreibung                                                                 |
|---------------------------|--------------------------------------------------|------------------------------------------------------------------------------|
| Gefühlte Tageshitze       | Alle Punkte der **heutigen** Etappe             | Wenn aktueller Wert über Schwelle gestiegen                                 |
| Regenrisiko               | Alle Punkte der **heutigen** Etappe             | Wenn aktueller Wert höher als morgens, inkl. Zeitpunkt                       |
| Wind                      | Alle Punkte der **heutigen** Etappe             | Wenn aktueller Wert höher als morgens                                        |
| Gewitterrisiko            | Alle Punkte der **heutigen** Etappe             | Wenn Schwellwert überschritten oder stärker als morgens                      |

> Diese Warnung wird **nur bei signifikanter Verschlechterung** gesendet.

---

## Beispiele

### Abendmodus – Langtext

```
Etappe: Haut Asco → Ballone  
Gefühlte Nachttemperatur: 13.7 °C  
Gefühlte Tageshitze morgen: 32.5 °C  
Regenrisiko: 15%@10(45%@15)  
Wind: 35 km/h  
Gewitterrisiko morgen: 20%@11(50%@16)  
Gewitterrisiko übermorgen: 30%@12(60%@14)
```

### Abendmodus – InReach kompakt

```
Asco→Ballone | Nacht 13.7°C | Tag 32.5°C | Regen 15%@10(45%@15) | Wind 35km/h | Gewitter 20%@11(50%@16) → 30%@12(60%@14)
```

---

### Morgenmodus – Langtext

```
Etappe: Ballone → Manganu  
Gefühlte Tageshitze: 28.9 °C  
Regenrisiko: 10%@13(55%@17)  
Wind: 28 km/h  
Gewitterrisiko heute: 15%@14(60%@16)  
Gewitterrisiko morgen: 20%@10(35%@15)
```

### Morgenmodus – InReach kompakt

```
Ballone→Manganu | Tag 28.9°C | Regen 10%@13(55%@17) | Wind 28km/h | Gewitter 15%@14(60%@16) → 20%@10(35%@15)
```

---

### Tageswarnung – Langtext

```
Wetterwarnung – Etappe: Manganu → Petra Piana  
Neue Tageshitze: 34.1 °C  
Regen gestiegen: 20%@11(50%@15)  
Wind gestiegen: 42 km/h  
Gewitterrisiko gestiegen: 30%@13(65%@16)
```

### Tageswarnung – InReach kompakt

```
Manganu→Petra Piana | Tag 34.1°C | Regen 20%@11(50%@15) | Wind 42km/h | Gewitter 30%@13(65%@16)
```

---

## Technische Hinweise

- **Schwellenwerte:** Werden ausschließlich in `config.yaml` definiert
- **Zeitformat:** Intern UTC/Europe/Paris, Darstellung vereinfacht
- **Datenquellen:** System ist offen für verschiedene Wetterdatenquellen
- **Crontab:** Modi werden über geplante Jobs gesteuert
- **Format:** InReach-Nachrichten max. 160 Zeichen, keine Emojis
