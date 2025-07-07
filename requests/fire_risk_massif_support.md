# .cursor/requests/fire_risk_massif_support.md

## Ziel

Erweiterung des Systems um eine automatisierte Auswertung der tagesaktuellen Waldbrandwarnungen für Korsika, basierend auf den offiziellen Massif-Daten von https://www.risque-prevention-incendie.fr/.

Die Information soll zur Ergänzung bestehender Wetterberichte dienen.
---

## Anforderungen

### 1. Abruf der JSON-Daten
- Nutze die URL-Struktur:
  - `https://www.risque-prevention-incendie.fr/static/20/import_data/YYYYMMDD.json`
- Die Datei enthält u. a. `massif_id`, `niveau`, `libelle` und ggf. Koordinaten oder Namen.

### 2. Interpretation der Daten
- Felder im JSON:
  - `massif_id`: numerische ID des Gebiets (z. B. 1–9)
  - `niveau`: Stufe der Feuergefahr (z. B. 1–5)
  - `libelle`: Stufe als Text (z. B. „Très élevé“)

### 3. Mapping `massif_id` zu Regionen
## Ziel

Sicherstellung, dass numerische `massif_id`-Werte aus Risiko-Daten (z. B. von https://www.risque-prevention-incendie.fr) eindeutig einer geografischen Region (z. B. „Corse-du-Sud“) zugeordnet werden können. Die Zuordnung wird benötigt, um:
- Feuerwarnungen regional korrekt darzustellen,
- menschlich verständliche Berichtstexte zu generieren,
- spätere Provider-unabhängige Vergleiche oder Visualisierungen zu ermöglichen.

---

## Anforderungen

### 1. Datenquellen untersuchen
- Prüfe die vorhandene JSON-Struktur (z. B. `massifs_20.fgb` bzw. `...20250706.json`).
- Falls enthalten, nutze Felder wie `NOM_MASSIF`, `dept`, `ID`, `libelle`, um ein Mapping `massif_id → Name` zu extrahieren.
- Falls keine sprechenden Namen enthalten sind, beschaffe ein begleitendes Mapping über eine der folgenden Quellen:
  - https://geo.data.gouv.fr/
  - https://data.gouv.fr/
  - oder direkt über https://www.risque-prevention-incendie.fr/static/...

### 2. Alternative: räumliche Zuordnung
Falls kein direktes Mapping vorliegt:
- Extrahiere die Polygon-Geometrie der Massifs (z. B. aus `.fgb` Datei).
- Implementiere ein Point-in-Polygon-Verfahren:
  - Input: GPS-Koordinate eines Etappenpunkts.
  - Output: zugehörige `massif_id`.

### 3. Integration in den Systemfluss
- Stelle sicher, dass jeder Etappenpunkt (oder feste Referenzpunkt wie Corte) beim Abruf von Feuerwarnungen automatisch dem passenden `massif_id`-Gebiet zugeordnet werden kann.
- Die ID wird genutzt für den Abruf, der Name für den Bericht.

### 4. Testabdeckung
- Füge mindestens 3 Testfälle hinzu, die ein Mapping `massif_id → Region` absichern.
- Beispiel: `massif_id: 1 → Corse-du-Sud`, `massif_id: 3 → Haute-Corse` o. ä.
- Die Tests müssen bestehen, auch wenn das Mapping über Polygonanalyse erfolgt.

---

## Zielstatus

Ein `massif_id` ist technisch eindeutig einer Region zugeordnet.

- Für jeden Etappenpunkt muss ein zugehöriges Massif bestimmt werden.
- Wenn ein Warnlevel vorhanden ist soll dieser wie in email format spezifiziert als "Fire" Warnung mit einsprechenden Warnlevel ausgeben werden.

### 4. Text-Formatierung
- Aggregiere die Warnstufen zu folgendem Kurzformat:
gemäß email_format.mdc  `
MAX Waldbrand 
- Im kombinierten Bericht:
  - Optional: Schwelle definieren, ab wann die Information ausgegeben wird (z. B. ab Stufe 3)

### 5. Integration
- Ausgabe ersetzt den bisherigen Eintrag für Viligrance Warnungen in Bezug auf Waldbrand.
- Zeitlich synchronisiert mit Wetterabfragen (z. B. Tageswechsel 06:00 UTC).

---

## Tests

- Mindestens 3 Beispieldaten mit unterschiedlichen `massif_id` und `niveau` testen.
- Validierung:
  - Stufe korrekt ausgelesen
  - Name korrekt gemappt
  - Ausgabe korrekt formatiert