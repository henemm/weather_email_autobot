# Refactoring: MeteoTokenProvider als Singleton

## Ziel

Stelle sicher, dass die Klasse `MeteoTokenProvider` projektweit nur einmal instanziiert wird und alle Module denselben Token verwenden.

Vermeide, dass bei jeder API-Nutzung ein neuer OAuth2-Token erzeugt wird. Token sollen effizient wiederverwendet werden, solange sie gültig sind.

---

## Anforderungen

### Architektur

- `MeteoTokenProvider` wird als Singleton umgesetzt
- Optional: Modulweiter Cache als Alternative
- Es darf **nur eine Token-Instanz aktiv** sein (siehe Doku Meteo France)

### Integration

- Alle Aufrufe von `fetch_arome_wcs_data()`, `fetch_arome_instability_layer()` etc. sollen den Singleton verwenden
- Token wird **nicht neu angefordert**, wenn bereits ein gültiger vorliegt

### Transparenz & Debugging

- Logging bei Token-Erzeugung: Zeitstempel + abgekürzter Token
- Logging bei Wiederverwendung eines Tokens (aus Cache)

---

## Authentifizierungs-Logik (laut Meteo France)

- Token wird via POST an `https://portail-api.meteofrance.fr/token` mit `grant_type=client_credentials` und Header `Authorization: Basic <APPLICATION_ID>` erzeugt
- Token ist ca. 1 Stunde gültig
- Gültigkeit wird geprüft via HTTP-Status 401 mit Payload `{"description": "Invalid JWT token"}`
- Bei Ablauf: Token wird automatisch erneuert

---

## Zusätzliche Hinweise

- Token kann für **alle abonnierten APIs** verwendet werden (einheitlicher Zugriff)
- Achte darauf, dass **keine doppelten Anfragen parallel** ein neues Token erzeugen (Race Condition vermeiden)

---

## Tests

- `tests/test_token_provider.py`:
  - Nur 1 Instanz bei Mehrfachverwendung
  - Wiederverwendung bei mehreren Aufrufen
  - Token-Erneuerung nach Ablauf
  - Fehlverhalten bei ungültigem APPLICATION_ID

---

## Ziel

Stabiles, transparentes und effizientes Token-Handling mit nur einer aktiven Instanz pro Laufzeit.