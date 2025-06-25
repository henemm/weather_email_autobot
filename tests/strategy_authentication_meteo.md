# Teststrategie: OAuth2-Authentifizierung für Meteo France APIs

## Ziel

Verifiziere, dass das System korrekt mit einem zentralen OAuth2-Token arbeitet, dieser nur einmal erzeugt wird und für alle genutzten Meteo France APIs funktioniert.

---

## Getestete APIs (laut Swagger & Implementierung)

1. AROME WCS API (`fetch_arome_wcs_data`)
2. AROME Instability Layers (`fetch_arome_instability_layer`)
3. Vigilance Bulletins (`fetch_vigilance_warnings`)

Alle drei APIs nutzen den gleichen OAuth2-Token und sollen gemeinsam getestet werden.

---

## Testziele

- Token wird nur **einmal erzeugt**
- Token wird **korrekt für alle APIs verwendet**
- Token wird **erneuert**, wenn abgelaufen
- Token führt zu **gültigen API-Antworten**
- Fehlerhafte Token erzeugen klar definierte Fehler

---

## Testfälle

### ✅ Funktionale Authentifizierung

- [ ] Gültiger Token → Zugriff auf alle drei APIs möglich
- [ ] Token wird beim zweiten API-Aufruf **nicht neu generiert**
- [ ] Token wird nach Ablauf **erneuert und erneut verwendet**
- [ ] Alle APIs liefern **HTTP 200 oder definierte Antworten**

### ❌ Fehlerfälle

- [ ] Ungültiger APPLICATION_ID → Fehler beim Token-Abruf
- [ ] Token-Fehler (401, "Invalid JWT") → Neuanforderung und Wiederholung
- [ ] Token fehlt → `RuntimeError` mit Klartextmeldung

---

## Testmethodik

- Unit-Tests für `MeteoTokenProvider` (z. B. Singleton, Cache)
- Integrationstests mit echten API-Aufrufen (wenn verfügbar)
- Logging-Überprüfung (z. B. `Token reused`, `Token expired`)

---

## Hinweise

- Beachte: Ein Token ist nur gültig für APIs, die **zum Zeitpunkt der Token-Erzeugung abonniert** waren
- Vermeide parallele Token-Anfragen bei Ersterzeugung
- Aktiviere Debug-Logging zur Nachverfolgung

---

## Bewertungskriterium

Der Test gilt als bestanden, wenn:
- Alle drei APIs mindestens einmal erfolgreich mit demselben Token abgefragt werden
- Das System den Token exakt **einmal** erzeugt und ggf. automatisch erneuert
- Kein Zugriff durch Authentifizierungsfehler blockiert wird