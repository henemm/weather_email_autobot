# Refactor: Automatische OAuth2-Token-Beschaffung und Erneuerung

## Ziel

Der MeteoTokenProvider soll OAuth2-konform erweitert werden:
- Token automatisch bei Bedarf per Client-Credentials abrufen
- Token zwischenspeichern (Singleton)
- Bei Ablauf (401) automatisch neuen Token holen und Request wiederholen

## Hintergrund

Derzeit wird ein manuell generierter Token aus `.env` verwendet. Dieser Ablauf ist nicht wartbar und nicht produktionsgeeignet. Météo France stellt einen standardisierten OAuth2-Flow zur Verfügung.

## Anforderungen

### 1. Token-Beschaffung

- URL: `https://portail-api.meteofrance.fr/token`
- Methode: `POST`
- Header: `Authorization: Basic <base64(client_id:client_secret)>`
- Body: `grant_type=client_credentials`
- Response: enthält `access_token` (JWT)

Die `client_id` und `client_secret` sollen aus Umgebungsvariablen bezogen werden:
- `METEOFRANCE_CLIENT_ID`
- `METEOFRANCE_CLIENT_SECRET`

Die Header-Berechnung (`Basic base64(...)`) erfolgt im Code.

### 2. Integration in MeteoTokenProvider

- Der Provider prüft beim ersten Aufruf, ob ein gültiger Token vorhanden ist
- Falls abgelaufen oder 401-Fehler: neuen Token holen, Request wiederholen
- Der Token wird für alle APIs (WCS, Vigilance etc.) gemeinsam verwendet

### 3. Fehlerbehandlung

- Bei ungültigen Credentials: eindeutige Fehlermeldung mit Hinweis auf `.env`
- Bei Timeout/Netzwerkfehler: Retry mit Exponential Backoff (max. 3 Versuche)

### 4. Tests

- Unit-Tests für Token-Generierung
- Tests für Fehlerfälle (401, ungültige Credentials)
- Integrationstest mit Mocks: Token einmal geholt, mehrere APIs angesprochen

## Dateien

- `src/auth/meteo_token_provider.py`
- `src/utils/oauth2_client.py` (neu)
- `tests/test_meteo_token_provider.py`

## Abgrenzung

Dieses Refactoring ersetzt NICHT bestehende API-Key-Authentifizierung – nur OAuth2-Flows sind betroffen.