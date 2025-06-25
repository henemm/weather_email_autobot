# Integrationstest: Live-Datenanalyse (Arome + Warnungen)

## Ziel
Simuliere einen vollständigen Abruf und die Auswertung von Wetterdaten und Unwetterwarnungen für ein konkretes Gebiet mit prognostiziertem Unwetter. Verwende dazu reale Daten von Météo France (AROME HD + Vigilance API).

---

## Parameter

- **Position**: Südlich des Monte Cinto, Korsika
  - Breitengrad: `42.308`
  - Längengrad: `8.937`
- **Zeitraum**: Aktuell, 48-Stunden-Prognose
- **Datenquellen**:
  - `fetch_arome.py` (Stundenwerte)
  - `fetch_vigilance.py` (Unwetterwarnungen)

---

## Ablauf

1. **Abruf**:
   - Lade Wetterdaten (stündlich, 48h) von `fetch_arome`
   - Lade Warnungen von `fetch_vigilance`

2. **Auswertung**:
   - Analysiere CAPE, SHEAR, Regen, Wind etc.
   - Prüfe Unwetterwarnungen (insb. "Orages")

3. **Worst-Case-Strategie**:
   - Wenn mehrere Prognosen (z. B. ECMWF) vorliegen sollten, verwende stets die riskanteste

4. **Bericht**:
   - Erzeuge eine zusammengefasste, textliche Risiko-Warnung für die Region

---

## Erwartung

- AROME sollte Gewittergefahr zeigen (→ CAPE hoch, Regen >2mm, ggf. SHEAR)
- Vigilance sollte mind. gelbe Warnung enthalten
- Analyse soll Risiko als „HOCH“ oder „SEHR HOCH“ einstufen
- Ausgabe in `WeatherReport.text` soll Empfehlungen enthalten

---

## Hinweise

- API-Token müssen korrekt geladen sein
- Debug-Logging aktivieren zur Fehlersuche