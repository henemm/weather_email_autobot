# Wetterwarnungen von Météo-France abrufen

## Ziel

Integriere offizielle Wetterwarnungen aus der Vigilance API von Météo-France und verknüpfe sie mit den vorhandenen `WeatherPoint`-Daten.

## Anforderungen

- Nutze den Python-Client `meteofrance-api`
- Authentifiziere dich via OAuth (nicht Bearer)
- Hole für jeden `WeatherPoint`-Ort (Koordinaten) die aktuellen Warnungen ab
- Konvertiere Warnungen in das `WeatherAlert`-Format gemäß `datatypes.py`
- Füge alle gültigen Warnungen dem jeweiligen `WeatherPoint.alerts` hinzu
- Speichere diese Informationen lokal für Offline-Analyse

## Einschränkungen

- Nutze nur öffentlich dokumentierte API-Endpunkte
- Keine parallelen Anfragen (Limitierungen der API beachten)
- Die Gültigkeit der Warnung muss mit dem Zeitpunkt des jeweiligen Wetterpunkts überschneiden (`valid_from` ≤ `time` ≤ `valid_to`)

## Tests

- Verwende Testdaten für ein Beispielgebiet in Frankreich (z. B. Korsika)
- Mindestens ein Testfall muss eine aktive Warnung enthalten