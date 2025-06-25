# Feature: AROME Wetterdaten abrufen

## Ziel

Implementiere ein Modul `src/wetter/fetch_arome.py`, das stündliche Wetterdaten von Météo-France (AROME HD 2km) abruft, verarbeitet und als `WeatherData`-Objekt zurückgibt.

---

## Anforderungen

### Authentifizierung

- Verwende den OAuth2-Token aus der Umgebungsvariable `METEOFRANCE_AROME_TOKEN`
- Übergib ihn als Bearer-Token im Header `Authorization`

---

### Abfrageparameter

- Verwende Breitengrad (`lat`) und Längengrad (`lon`) als Eingabeparameter
- Zeitraum: 48 Stunden in 1-Stunden-Schritten
- Nutze offizielle Swagger-API (`/forecast/arome_hd`) oder Python-Client
- Alle Zeitstempel in UTC

---

### Rückgabeformat

- Liefere ein `WeatherData`-Objekt zurück
- Befülle die enthaltene Liste mit `WeatherPoint`-Objekten mit folgenden Attributen:

  - `time` (datetime)
  - `latitude`, `longitude`, `elevation`
  - `temperature`, `feels_like`
  - `precipitation` (mm)
  - `thunderstorm_probability` (direkt oder CAPE×SHEAR)
  - `wind_speed` (km/h), `wind_direction` (°)
  - `cloud_cover` (%)
  - `cape`, `shear` (optional)

---

## Fehlerverhalten

- Fehlender Token → `RuntimeError` mit Hinweismeldung
- HTTP-Fehler (z. B. 401, 500) → aussagekräftige Exception
- Keine Datenpunkte → leere Liste, mit Logging-Warnung

---

## Teststrategie

- `tests/test_arome.py`
- Szenarien:
  - Erfolgreicher Abruf mit allen Feldern
  - Unvollständige Daten (z. B. ohne SHEAR)
  - Token fehlt
  - API liefert Fehler

---

## Ablageort

- Implementierung: `src/wetter/fetch_arome.py`
- Unit-Tests: `tests/test_arome.py`

---

## Zusätzliche Hinweise

- Verwende `python-dotenv` zur Initialisierung der Tokens
- Kein CLI, keine Benutzerinteraktion
- Reine Funktionsschnittstelle, keine Dateioperationen