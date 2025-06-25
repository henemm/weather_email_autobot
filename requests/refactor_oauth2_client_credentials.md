title: Revert OAuth2 to Client Credentials Flow
scope: authentication, token-provider
type: refactor
status: ✅ COMPLETED
priority: high

## Ziel
Die aktuelle Implementierung nutzt die Variable `METEOFRANCE_APPLICATION_ID`, die jedoch nicht mit dem OAuth2-Flow von Météo-France kompatibel ist. Laut offizieller Dokumentation müssen `client_id` und `client_secret` übermittelt werden, nicht ein Base64-Header oder ein zusammengesetzter Wert.

Dieser Request stellt den OAuth2-Prozess technisch korrekt auf den von Météo-France dokumentierten Client-Credentials-Fluss um.

## ✅ IMPLEMENTATION COMPLETED

### Erfolgreich umgesetzt:
- **OAuth2 Client Credentials**: Vollständig implementiert in `src/auth/meteo_token_provider.py`
- **WMS/WCS Robustheit**: Utility-Funktion für gültige Zeitstempel in `src/wetter/fetch_arome_wcs.py`
- **Alle Tests**: Unit- und Live-Tests erfolgreich
- **Dokumentation**: Best Practices in `docs/oauth2_wms_wcs_best_practices.md`

### API-Status:
- **WCS API**: ✅ Funktioniert perfekt mit OAuth2
- **Vigilance API**: ✅ Funktioniert perfekt mit OAuth2  
- **WMS API**: ✅ OAuth2 funktioniert, aber erfordert gültige Zeitstempel aus GetCapabilities

### Technische Learnings:
1. **OAuth2 Flow**: Korrekte Implementierung mit `client_id:client_secret` Base64-Header
2. **WMS Zeitstempel**: Niemals willkürliche Zeiten verwenden - immer aus GetCapabilities extrahieren
3. **Fehlerbehandlung**: Robuste Validierung und klare Fehlermeldungen
4. **Token-Caching**: 1-Stunden-Cache funktioniert zuverlässig

## Technischer Kontext
- Aktuell wird `METEOFRANCE_APPLICATION_ID` als Token-Basis verwendet (fehlerhaft).
- Die korrekte Authentifizierung verlangt `client_id` und `client_secret` in einem HTTP-POST mit Formdaten.
- Die aktuelle Implementierung schlägt mit `401 invalid_client` fehl.

## Anforderungen

1. Entferne jegliche Nutzung der Variable `METEOFRANCE_APPLICATION_ID`.
2. Stelle den Token-Abruf so um, dass der folgende Request erzeugt wird:
   - URL: `https://portail-api.meteofrance.fr/token`
   - Methode: `POST`
   - Content-Type: `application/x-www-form-urlencoded`
   - Body:
     ```
     grant_type=client_credentials
     ```
   - Header:
     ```
     Authorization: Basic base64(client_id:client_secret)
     ```
     (d.h. `METEOFRANCE_CLIENT_ID` und `METEOFRANCE_CLIENT_SECRET` müssen verwendet werden)

3. Verwende keine Drittbibliotheken wie `requests-oauthlib` – bleibe bei `requests` und interner Logik.
4. Der erzeugte Token muss intern gespeichert und wiederverwendet werden, solange er gültig ist.
5. Es muss ein klarer Hinweis gegeben werden, wenn ein Token nicht erzeugt werden kann (inkl. Umgebungsvariablen-Check).
6. Alle Live- und Integrationstests sollen mit diesem Fluss grün durchlaufen.
7. Die `.env`-Datei soll dokumentieren, dass folgende Werte benötigt werden:
   - `METEOFRANCE_CLIENT_ID`
   - `METEOFRANCE_CLIENT_SECRET`

## Qualitätskriterien

- Keine Base64-kodierten Umgebungsvariablen mehr.
- Fehlerhafte oder fehlende Credentials führen zu klaren Fehlermeldungen.
- Integrationstests mit Live-API funktionieren ohne manuelle Token.
- Tokens werden weiterhin nur für exakt eine Stunde zwischengespeichert.
- Alle Abrufmethoden bleiben unverändert nutzbar.

## Hinweis

Die ursprüngliche `application_id`-basierte Authentifizierung war ein Missverständnis der API-Dokumentation. Bitte stelle sicher, dass alle betroffenen Module und Tests entsprechend angepasst werden.