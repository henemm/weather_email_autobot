# Funktionale Anforderung: OAuth2 Token Provider

## Ziel
Eine zentrale, wiederverwendbare Komponente zur Beschaffung, Verwaltung und Erneuerung von OAuth2 Access Tokens über den Client Credentials Flow gemäß Météo-France API.

## Funktionale Anforderungen

- [ ] Initialer Abruf eines gültigen Access Tokens über `client_id` und `client_secret`
- [ ] Token muss aus Umgebungsvariablen `METEOFRANCE_CLIENT_ID` und `METEOFRANCE_CLIENT_SECRET` stammen
- [ ] Verwendung des Token-Endpunkts: `https://portail-api.meteofrance.fr/token`
- [ ] POST-Anfrage mit Header `Content-Type: application/x-www-form-urlencoded` und Basic Auth
- [ ] Body muss `grant_type=client_credentials` enthalten
- [ ] Antwort enthält gültiges Bearer Token (mind. 3600s gültig)
- [ ] Token wird im Speicher zwischengespeichert und automatisch erneuert (60s Sicherheits-Puffer)

## Nicht-funktionale Anforderungen

- [ ] Maximal 2 Retry-Versuche bei HTTP 5xx
- [ ] Logging von Fehlern (aber keine Tokens!)
- [ ] Kein persistenter Speicher – nur Memory Cache

## Integration

- [ ] Muss durch alle forecast- und vigilance-relevanten Module importierbar sein
- [ ] Muss einfach durch Unit Tests mockbar sein
- [ ] Keine Abhängigkeiten außer `requests`

## Testszenarien

1. **Token abrufbar mit gültigen Credentials**
2. **Token wird zwischengespeichert**
3. **Token wird nach Ablauf erneuert**
4. **Fehlermeldung bei ungültigen Credentials**
5. **Rückfallverhalten bei temporären Serverfehlern**

## Ausschlüsse

- Kein Refresh Token Flow
- Kein persistentes Speichern der Tokens