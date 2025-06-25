# Feature: Vigilance-Warnungen abrufen

## Ziel

Implementiere ein Modul `src/wetter/fetch_vigilance.py`, das aktuelle Unwetterwarnungen von Météo-France (Vigilance API) für eine bestimmte Koordinate abruft, auswertet und als strukturierte Objekte bereitstellt.

---

## Anforderungen

### Authentifizierung

- Verwende den OAuth2-Token aus der Umgebungsvariable `METEOFRANCE_VIGILANCE_TOKEN`
- Übergib ihn als Bearer-Token im Header `Authorization`

---

### Abfrageparameter

- Übergib Breitengrad (`lat`) und Längengrad (`lon`) als Parameter
- Verwende die offizielle Endpoint: `/vigilance/public/bulletin`
- Liefere immer die aktuelle gültige Warnsituation für diesen Punkt zurück

---

### Rückgabeformat

- Gib eine Liste von `WeatherAlert`-Objekten zurück:

  - `type`: z. B. "Orages", "Vent"
  - `level`: Warnstufe (1=grün bis 4=rot)
  - `start`: Startzeitpunkt (datetime)
  - `end`: Endzeitpunkt (datetime)

- Berücksichtige nur Warnstufen ab **Gelb** (2+)

---

## Fehlerverhalten

- Fehlender Token → `RuntimeError` mit klarer Meldung
- HTTP-Fehler (401, 500 etc.) → Exception mit Status & Inhalt
- Keine Warnungen → leere Liste (nicht None)

---

## Teststrategie

- `tests/test_warning.py`
- Szenarien:
  - Mind. eine gültige Warnung vorhanden
  - Keine Warnung vorhanden
  - Ungültiger Token
  - Serverfehler (z. B. 500)

---

## Ablageort

- Implementierung: `src/wetter/fetch_vigilance.py`
- Unit-Tests: `tests/test_warning.py`

---

## Hinweise

- Verwende `python-dotenv` zur Initialisierung der Tokens
- API liefert Zeitfenster im ISO-Format – nutze `datetime.fromisoformat`
- Halte das Modul rein funktional ohne globale Zustände