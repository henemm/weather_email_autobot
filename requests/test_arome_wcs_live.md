# Feature: Integrationstest – Live-Abruf via fetch_arome_wcs

## Ziel

Implementiere einen optionalen Integrationstest, der `fetch_arome_wcs_data` mit echten Parametern aufruft, um einen Live-Datenabruf zu prüfen.

---

## Voraussetzungen

- Die Umgebungsvariable `METEOFRANCE_WCS_TOKEN` muss gesetzt sein
- Nur ausführen, wenn Internetzugang verfügbar
- Test darf bei fehlender Umgebung still übersprungen werden

---

## Testinhalte

- Abruf von Layer `"TEMPERATURE__GROUND_OR_WATER_SURFACE"` für:
  - Koordinaten `lat=45.75`, `lon=4.85` (Lyon – garantiert im AROME-Gebiet)
- Erwartung: Rückgabe eines `WeatherGridData`-Objekts mit:
  - `times` nicht leer
  - `values` nicht leer
  - `unit` enthält `"°"` oder `"C"`

---

## Umsetzung

- Datei: `tests/test_arome_wcs_live.py`
- Framework: `pytest`
- Nutze `pytest.mark.skipif(...)` für Token-Check
- Optional: registriere `integration`-Markierung in `pytest.ini`

---

## Hinweise

- Dies ist ein Integrationstest, kein Unit-Test
- Der Test ist nicht CI-kritisch, dient nur zur manuellen Verifikation
- Verwende `-s` beim Testlauf, um Ergebnis zu sehen: `pytest -s tests/test_arome_wcs_live.py`