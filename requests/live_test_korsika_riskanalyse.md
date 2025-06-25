# Integrationstest: Live-Wetterabruf für Korsika mit Risikoanalyse

## Ziel
Führe einen vollständigen Live-Test des Analyse-Workflows durch – von realem Wetterdatenabruf bis zur Generierung eines Warntextes für eine Koordinate auf Korsika.

## Testparameter

- **Koordinaten**: lat: 42.0396, lon: 9.0129 (Korsika, Nähe Corte)
- **Zeitpunkt**: aktuelle Vorhersage (Standardverhalten)
- **Wetterlayer**:
  - TEMPERATURE__GROUND_OR_WATER_SURFACE
  - TOTAL_PRECIPITATION__SURFACE
  - CAPE__SURFACE

## Erwartetes Verhalten

- `fetch_arome_wcs_data()` liefert für jeden Layer gültige Daten
- `analyse_weather_data()` berechnet einen plausiblen Risk-Score
- `generate_warntext()` liefert (abhängig vom Score) einen Warnhinweis
- Das Ergebnis wird als Datei `output/inreach_warnung.txt` gespeichert

## Hinweise

- Authentifizierung über bestehenden OAuth2-Mechanismus (Token-Provider)
- Kein Mocking! Es soll ein echter API-Call erfolgen
- Die `config.yaml` muss einen gültigen risk_model und warn_thresholds Abschnitt enthalten

## Teststrategie

- Fehlerhafte Layer / leere Daten → sauber abgefangen
- Risk-Schwelle < Info-Threshold → keine Warnung
- Risk-Schwelle ≥ Warning → Datei-Ausgabe mit Text

## Testklasse

- Ablage: `tests/test_integration_live_korsika.py`
- Verwende `pytest.mark.integration` für Markierung