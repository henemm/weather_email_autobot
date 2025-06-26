# Erweiterung der Gewitterrisiko-Berechnung (Thunderstorm Risk Logic)

## Ziel
Die Gewitterrisikobewertung soll inhaltlich mit den offiziellen Météo-France-Prognosen übereinstimmen. Grundlage sind ausschließlich offiziell verfügbare Météo-France-APIs.

## Hintergrund
Ein Testfall in Pouillac (25.06.2025, Nachmittag) zeigte:
- Offizielle Prognose: ⚠️ Gewitterwarnung mit 80 km/h Böen
- Systembewertung: ❌ „niedriges Risiko“
→ Das System unterschätzt das Risiko trotz korrekt angebundener APIs (AROME WCS, PIAF, etc.).

## Erweiterung – Anforderung an die Risikologik

### 1. 🔥 Neue Einflussgrößen einbeziehen

| Messgröße       | Quelle (API/Feld)                     | Integration in Risiko     |
|------------------|----------------------------------------|-----------------------------|
| **Wind-Böen**     | `AROME_HR` → Feld: `WIND_GUST`         | +1 Risikostufe >40 km/h, +2 >60 km/h |
| **SHEAR (Vertikal)** | `AROME_HR` → Feld: `VERTICAL_WIND_SHEAR` | +1 Risikostufe bei >12 m/s |
| **Vigilance-Level** | `VIGILANCE_API` (départementbasiert) | Überschreibt Risiko falls ≥2 |
| **Konvergenz (Feuchte)** | (optional, nur bei Verfügbarkeit) | +1 Risikostufe bei hoher Bodenfeuchte |
| **Nowcast-Regenrate** | `PIAF_NOWCAST` → `RAIN_RATE`         | Risikoverstärkung bei >0.2 mm/h kurzfristig |

### 2. ⚙️ Schwellenwerte (aktuell)

| Parameter  | Schwellenwert     | Wirkung              |
|------------|-------------------|-----------------------|
| CAPE       | 500 / 1000 J/kg    | leicht/mittel/stark  |
| Regenrate  | >0.2 / >1 mm/h     | leicht/mittel        |
| Windböen   | >40 km/h / >60 km/h| mittel/stark         |
| SHEAR      | >12 m/s            | mittel               |
| Vigilance  | Stufe 2 oder höher | direktes Warnsignal  |

→ Diese Schwellenwerte sollen in `config.yaml` ausgelagert werden (z. B. unter `storm_risk:`).

### 3. 🧠 Entscheidungslogik (vereinfacht)

- **Start-Risiko**: Basierend auf CAPE
- **+1 Risikostufe**, wenn einer der Zusatzfaktoren überschritten ist
- **Maximalrisiko**: Wird überschrieben bei `Vigilance ≥ 2`
- Endergebnis: „niedrig“ / „mittel“ / „hoch“

### 4. 🧪 Testszenarien

- [ ] Live-Test: Pouillac 25.06.2025 – Risiko soll auf „hoch“ steigen
- [ ] Regressions-Test: Conca mit CAPE <200 → Risiko bleibt „niedrig“
- [ ] Falltest: CAPE + Windböen + SHEAR → Risiko „hoch“

## Akzeptanzkriterien

- [ ] System reagiert plausibel auf starke Böen (>40 km/h)
- [ ] Vigilance-Warnung hebt Prognose-Risiko korrekt an
- [ ] Live-Test Pouillac spiegelt Météo-France-Ergebnis
- [ ] Schwellenwerte sind dokumentiert & konfigurierbar

---

## Umsetzungshinweis

- Anpassung erfolgt in: `src/logic/analyse_weather.py`
- Schwellenwerte in: `config.yaml`
- API-Felder nutzen: `fetch_arome_wcs.py`, `fetch_vigilance.py`, `fetch_piaf_nowcast.py`