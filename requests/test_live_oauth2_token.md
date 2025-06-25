---
title: Live-Test der OAuth2-Authentifizierung mit Token-Neubezug
---

Ziel:
Verifiziere, dass ein neuer OAuth2-Token korrekt bezogen wird, wenn der bestehende Token fehlt oder abgelaufen ist.

Testaufbau:
- Verwende `src/auth/meteo_token_provider.py`, um mit gültigen Client-Credentials (`METEOFRANCE_CLIENT_ID` & `METEOFRANCE_CLIENT_SECRET`) einen neuen Token zu holen.
- Nutze den neuen Token für einen Live-API-Aufruf (z. B. WMS-Capabilities-Endpunkt).
- Bestätige, dass der HTTP-Status 200 und ein gültiges XML-Dokument zurückgeliefert wird.

Validierung:
- Token darf nicht aus `.env` gelesen werden (direkter Abruf)
- Token muss erfolgreich abgerufen werden
- Token muss für nachfolgenden WMS-Call gültig sein
- Fehlerhafte Client-Daten müssen korrekt abgefangen werden

Voraussetzungen:
- Gültige Météo-France OAuth2-Credentials in `.env` gesetzt:
  - `METEOFRANCE_CLIENT_ID`
  - `METEOFRANCE_CLIENT_SECRET`

Fehlerfälle:
- Ungültige Client-Daten: erwarte Status 401 + strukturierte Fehlermeldung
- Netzwerkfehler: Retry-Logik muss greifen

Abdeckung:
- End-to-End OAuth2-Fluss inkl. realem API-Zugriff
- Prüfung der zentralen Authentifizierungslogik im Live-Betrieb