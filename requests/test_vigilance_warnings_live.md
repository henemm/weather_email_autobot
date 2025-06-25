# Feature: Integrationstest – Live-Abruf von Wetterwarnungen (Vigilance)

## Ziel

Implementiere einen Integrationstest, der die Wetterwarnungen von Météo-France (Vigilance API) für eine gültige französische Postleitzahl abruft und auf Struktur und Inhalt prüft.

---

## Voraussetzungen

- Der API-Key (`METEOFRANCE_API_TOKEN`) muss als Umgebungsvariable gesetzt sein
- Der Test darf bei fehlendem Token automatisch übersprungen werden

---

## Testinhalte

- Abruf für eine reale Postleitzahl (z. B. `69000` für Lyon)
- Erwartung: Rückgabe einer Liste von `WeatherAlert`-Objekten
- Mindestens ein Element sollte die Felder enthalten:
  - `phenomenon`, `color`, `valid_from`, `valid_to`, `department`
- Alle Objekte müssen `valid_from` und `valid_to` als gültige `datetime` enthalten
- `color` sollte einer gültigen Kategorie entsprechen (z. B. "green", "yellow", "orange", "red")

---

## Umsetzung

- Datei: `tests/test_vigilance_live.py`
- Framework: `pytest`
- Marker: `@pytest.mark.integration`
- Nutze `pytest.mark.skipif(...)` für Token-Check

---

## Hinweise

- Der Test dient zur manuellen Prüfung der API-Konnektivität und Datenstruktur
- Er ist **nicht** CI-kritisch
- Optional: Ausgaben per `print()` für manuelles Debugging