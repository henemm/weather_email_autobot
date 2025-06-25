# Integrationstest: Live-Wetteranalyse ausführen

## Ziel
Manueller Durchlauf des vollständigen Analyse-Pfads mit Live-Daten.

---

## Schritte

1. **Daten abrufen**
   ```python
   from wetter.fetch_arome import fetch_arome
   from wetter.fetch_vigilance import fetch_warnings

   lat, lon = 42.308, 8.937
   arome = fetch_arome(lat, lon)
   warnings = fetch_warnings(lat, lon)