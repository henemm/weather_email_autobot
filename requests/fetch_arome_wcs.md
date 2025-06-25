# Feature: AROME-Wetterdaten (WCS) abrufen

## Ziel

Implementiere ein Modul `src/wetter/fetch_arome_wcs.py`, das über das WCS-Protokoll meteorologische Vorhersagedaten (z. B. Temperatur, Niederschlag) für eine definierte Koordinate abruft, dekodiert und als strukturierte Objekte zurückliefert.

---

## Anforderungen

### Authentifizierung

- Verwende den OAuth2-Token aus der Umgebungsvariable `METEOFRANCE_WCS_TOKEN`
- Übergib ihn im Header als `Authorization: Bearer <TOKEN>`

---

### Abfrageparameter

- Koordinaten: `lat`, `lon`
- Zeitraum: Übergib Zeitstempel oder übernimm Standard-Zeitfenster aus GetCapabilities
- Layer: Definiere den spezifischen Layer über einen Funktionsparameter (`layer_name`)
- Beispiel-Endpoint:  
  `https://public-api.meteofrance.fr/public/arome/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS`

---

### Rückgabeformat

- Gib ein `WeatherGridData`-Objekt zurück mit:

  - `layer`: Name des abgefragten Layers (z. B. "TEMPERATURE__GROUND_OR_WATER_SURFACE")
  - `unit`: Einheit (z. B. "°C", "mm", "%")
  - `times`: Liste von Zeitstempeln (UTC)
  - `values`: Liste der Werte pro Zeitstempel
  - `lat`, `lon`: verwendete Koordinaten

---

## Fehlerverhalten

- Fehlender Token → `RuntimeError` mit Klartext-Meldung
- Fehlerhafte Layer → `ValueError`
- HTTP-Fehler → Exception mit Status und Inhalt
- Leere Antwort → leeres `WeatherGridData`-Objekt

---

## Teststrategie

- `tests/test_arome_wcs.py`
- Szenarien:
  - Erfolgreicher Abruf mit Temperatur
  - Ungültiger Layer
  - Fehlerhafte Token
  - Zeitfilterung

---

## Ablageort

- Implementierung: `src/wetter/fetch_arome_wcs.py`
- Tests: `tests/test_arome_wcs.py`

---

## Hinweise

- Verwende `python-dotenv` zur Token-Initialisierung
- Verarbeite `application/xml`-Antworten mit `xml.etree` oder `lxml`
- Nutze `datetime.fromisoformat` zur Zeitkonvertierung
- Nutze vordefinierte Layer-Namen aus `GetCapabilities_WCS.txt`