# Feature: Garmin ShareMap – aktuelle GPS-Position abrufen

## Ziel

Implementiere ein Modul `src/position/fetch_sharemap.py`, das die aktuelle Position eines Benutzers aus einer öffentlichen Garmin ShareMap (z. B. https://share.garmin.com/PDFCF) ausliest und als strukturiertes Objekt zurückgibt.

---

## Quelle

- Beispiel-URL: `https://share.garmin.com/PDFCF`
- Der Dienst liefert intern Positionsdaten über eine JSON-API oder KML-Feed
- Die exakte Quelle kann über DevTools beim Laden der ShareMap ermittelt werden

---

## Ausgabeformat

Gib ein `CurrentPosition`-Objekt zurück mit folgenden Feldern:

- `latitude: float`
- `longitude: float`
- `timestamp: datetime`
- `source_url: str`

---

## Fehlerverhalten

- Wenn keine Position gefunden → `None` zurückgeben
- Bei HTTP-Fehlern → `Exception` mit Statuscode und Inhalt
- Bei ungültigem Format → `ValueError` mit Klartext

---

## Umsetzung

- Datei: `src/position/fetch_sharemap.py`
- Optional: `model/position.py` für `CurrentPosition`-Datentyp
- Nutze `requests`, `datetime`, `xml.etree` oder `json`

---

## Teststrategie

- Mock-Feed (lokal oder Snapshot von Garmin)
- Testfälle in `tests/test_fetch_position.py`:
  - Gültige Antwort → Position korrekt extrahiert
  - Leere Daten → `None`
  - Fehlerhafte URL → `requests.exceptions.RequestException`