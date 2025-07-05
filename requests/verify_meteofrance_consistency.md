# requests/verify_meteofrance_consistency.md

## Ziel
Sicherstellen, dass die aus der `meteofrance-api` bezogenen Rohdaten korrekt und nachvollziehbar in den Kurzbericht übersetzt werden. Im Fokus: Blitzrisiko, Regenwahrscheinlichkeit und Regenmenge.

## Hintergrund
Die aktuelle Ausgabe (z. B. Ascu → Gew. – | Regen 5%@ | Regen 0.2mm@14) scheint nicht im Einklang mit den offiziellen visuellen Prognosen von Météo France zu stehen, obwohl diese über dieselbe Datenbasis verfügen sollten. Es besteht der Verdacht, dass Daten entweder:
- fehlerhaft aggregiert,
- falsch interpretiert,
- nicht alle Geo-Zeitpunkte korrekt berücksichtigt oder
- Layer nicht korrekt ausgelesen werden.

## Anforderungen

### 1. Mensch-lesbare Rohdaten-Ausgabe aktivieren
Ergänze eine Debug-Option oder ein Testskript, das folgende Layer strukturiert ausgibt:

- `thunderstorm_probability` (pro Geo-Zeitpunkt)
- `precipitation_probability` (pro Geo-Zeitpunkt)
- `precipitation_amount` (pro Geo-Zeitpunkt)

Format:
[Etappe XY] @ [Uhrzeit]
 - Geo 1: Blitz 30%, RegenW 45%, RegenM 2.1mm
 - Geo 2: Blitz 10%, RegenW 20%, RegenM 0.3mm
 - Geo 3: ...

### 2. Vergleich zur Kurzbericht-Ausgabe
Ergänze Validierungspunkt in Tests:
- Stimmen die Maximalwerte aus dem Rohdatenarray mit den berichteten Werten im jeweiligen Abschnitt überein?
- Werden Schwellenwerte korrekt angewendet (laut `config.yaml`)?
- Wird bei Schwellenüberschreitung korrekte Uhrzeit ausgegeben?
- Wird *nur dann* eine Zusatzzeit (z. B. "Gew. +1 ...") ausgegeben, wenn Schwelle überschritten?

### 3. Abgleich gegen Météo-France-Website (visuelle Darstellung)
Vergleiche die tatsächlichen Layerdaten mit der offiziellen Darstellung für denselben Tag, Uhrzeit und Ort:
- Beispiel: Region Corte / Asco am 05.07.2025, 14:00 Uhr

### 4. Zielstatus
- Debug-Ausgabe vorhanden für jeden genutzten Layer
- Aussagekräftige Validierung, wann Schwellen-Trigger greifen
- Klares Mapping vom Report zurück auf Rohdatenarray möglich