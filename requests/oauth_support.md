# Feature: OAuth2-Token-Handling für Meteo France

## Ziel

Erstelle ein generisches Modul `src/util/oauth.py`, das automatisch gültige OAuth2-Tokens für Météo-France-Dienste (`AROME`, `VIGILANCE`) beschafft. Tokens werden **nicht mehr fest hinterlegt**, sondern dynamisch erzeugt.

---

## Anforderungen

### 🔐 Eingabe

- Umgebungsvariablen müssen gesetzt sein:
  - `METEOFRANCE_CLIENT_ID`
  - `METEOFRANCE_CLIENT_SECRET`
- Gültig für beide APIs: AROME & VIGILANCE

---

### 🧩 Funktion

Implementiere:
```python
def get_token(service: Literal["arome", "vigilance"]) -> str: