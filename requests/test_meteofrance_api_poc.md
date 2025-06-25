# requests/test_meteofrance_api_poc.md

## Ziel

**Proof of Concept**: Test der offiziellen Python-Bibliothek `meteofrance-api`, um zu prüfen, ob die über diese API abgerufenen Wetterdaten den öffentlichen Angaben auf der Météo-France-Webseite entsprechen – speziell für **Gewitterlagen**.

---

## Testkontext

- **Ort**: Tarbes, Frankreich  
- **Koordinaten**: `43.2333°N, 0.0833°E`  
- **Département**: `65`  
- **Vergleichszeitraum**:  
  - Heute Abend (24.06.2025)  
  - Morgen (25.06.2025)

---

## Testaufbau

### 1. Setup

Installiere die Bibliothek:

    pip install meteofrance-api

---

### 2. Testschritte

#### 2.1 Wetterprognose abrufen

    from meteofrance_api.client import MeteoFranceClient

    client = MeteoFranceClient()
    forecast = client.get_forecast(latitude, longitude)

**Validierungen:**
- Temperaturprognose für die nächsten 24h
- Niederschlagswahrscheinlichkeit
- Wetterbeschreibung (z. B. Hinweis auf Gewitter)

---

#### 2.2 Wetterwarnungen abrufen

    warnings = client.get_warning_current_phenomenons("65")

**Validierungen:**
- Enthält `phenomenon_max_color["Thunderstorms"]`
- Warnstufe (`yellow`, `orange`, `red`)
- Gültigkeitszeitraum

---

#### 2.3 Regenvorhersage abrufen (optional)

    rain = client.get_rain(latitude, longitude)

**Validierungen:**
- Niederschlagsintensität vorhanden
- Minutenbasierte Prognose korrekt verfügbar

---

## Erwartetes Ergebnis

- API liefert mindestens vergleichbare Ergebnisse zur offiziellen Website:
  - Aktive Gewitterwarnung, wenn sie öffentlich angezeigt wird
  - Ähnliche Beschreibung wie auf `meteofrance.com`
  - Temperaturverlauf plausibel
  - Regenwahrscheinlichkeit sinnvoll

---

## Vergleichsquelle

Offizielle Website:  
https://meteofrance.com/previsions-meteo-france/tarbes/65000

---

## Akzeptanzkriterien

- [ ] API funktioniert ohne Fehler
- [ ] Strukturierte Wetterdaten verfügbar
- [ ] Gewitterrisiken nachvollziehbar
- [ ] Unterschiede zur bisherigen AROME-API aufgezeigt