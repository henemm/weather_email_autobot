# Feature: AROME-Token automatisch verwalten

## Ziel

Die Funktion `fetch_arome_weather_data()` soll automatisch ein gültiges Token für die Météo-France-AROME-API verwenden – ohne manuelle Übergabe oder Pflege durch den Benutzer.

---

## Anforderungen

### Token-Erhalt (OAuth2)

- Verwende POST `https://portail-api.meteofrance.fr/token`
- Header:
  - `Authorization: Basic {METEOFRANCE_BASIC_AUTH}`
  - `Content-Type: application/x-www-form-urlencoded`
- Body: `grant_type=client_credentials`
- Token ist max. 1h gültig

### Speicherung

- Speichere das Ergebnis (Token + Ablaufzeitpunkt) im **Arbeitsspeicher** (kein Dateizugriff)
- Verwende Singleton oder Modul-Cache

### Wiederverwendung

- Prüfe bei erneutem Zugriff:
  - Falls Token jünger als 60 Minuten: verwende es
  - Falls abgelaufen: fordere neues Token an

---

## Integration

- Kapsle die Logik in `src/auth/meteo_token_provider.py`
- Stelle dort eine Funktion bereit:
  ```python
  def get_arome_access_token() -> str

## Fehlerbehandlung
	-	Fehlt METEOFRANCE_BASIC_AUTH → RuntimeError
	-	HTTP 401/403 → Exception mit API-Fehlermeldung
	-	Netzwerkfehler → Retry 1× nach kurzer Pause, sonst Fehler

⸻

## Tests
	•	Unit-Testdatei: tests/test_token_provider.py
	•	Szenarien:
	•	Neues Token korrekt bezogen
	•	Token wird wiederverwendet, wenn gültig
	•	Fehler bei ungültigen Zugangsdaten