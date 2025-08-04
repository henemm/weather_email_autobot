# requests/dynamic-report.md

## Ziel

Ein neuer Berichtstyp `Dynamic`, der regelmäßig durch ein externes System (z. B. Crontab) ausgeführt wird und automatisch erkennt, ob sich signifikante Wetteränderungen gegenüber dem letzten Bericht ergeben haben. Nur bei relevanten Änderungen wird ein neuer Report per SMS oder E-Mail verschickt.

## Kontext

- Der Dynamic-Bericht ergänzt die bestehenden Berichtsarten `morning` und `evening`
- Er nutzt dieselben Verarbeitungsmethoden (`process_night_data()`, `process_day_data()` usw.)
- Wird vom Betreiber regelmäßig aufgerufen, z. B. stündlich
- Interner Vergleich mit dem letzten versendeten Report je Etappe
- Optionaler Einsatz eines zusätzlichen Regen-Moduls mit 2h-Prognose

## Aufruf

    python run.py --modus dynamic

Der Aufruf erfolgt extern (nicht automatisch im Code), z. B. über Cron oder manuell.

## Konfiguration

Erweiterung der `config.yaml`:

    delta_thresholds:
      rain_probability: 1.0           # Änderung in %
      rain_amount: 1.5                # Änderung in mm
      temperature: 1.0                # Änderung in °C
      thunderstorm: 1                 # Stufenwechsel (low → med → high)
      wind_speed: 1.0                 # Änderung in km/h
      max_daily_reports: 4            # Maximal 4 Berichte pro Tag und Etappe
      min_interval_min: 90            # Mindestens 90 Minuten Abstand zum letzten Report

Alle anderen Konfigwerte (Thresholds, Startdatum, Etappenstruktur) wie bei `morning` und `evening`.

## Funktionsweise

1. Aufruf mit `--modus dynamic`
2. Für jede aktive Etappe wird ein vollständiger Bericht erzeugt (inkl. NIGHT, DAY, RAIN, PRAIN, WIND, GUST, TH, TH+1, HR)
3. Ergebnisse werden mit dem zuletzt verschickten Report dieser Etappe verglichen
4. Nur bei relevanten Abweichungen (siehe Vergleichslogik) wird der neue Report versendet
5. Optional: `rain_2h`-Prognose wird zusätzlich im Debug-Output angezeigt

## Vergleichslogik

Verglichen wird gegen den zuletzt verschickten Report derselben Etappe – unabhängig vom Modus.

### Vergleichsebene:

- Zahlenwerte (z. B. Temperatur, Regenmenge, Windgeschwindigkeit)
- Uhrzeiten von Threshold- und Maximalereignissen (z. B. Gewitter @ 14 → @ 9)
- Stufen (z. B. Gewitter von low → med → high)

### Änderungskriterium:

Ein neuer Report wird ausgelöst, wenn:

- Der neue Wert sich um mindestens den konfigurierten delta_threshold unterscheidet
- ODER der Zeitpunkt (Threshold oder Max) sich um ≥1 Stunde verändert

Beispiele:

- Regenmenge steigt von 0.2 mm auf 1.9 mm → **Trigger**
- Regen bleibt gleich, tritt aber 5 Stunden früher ein → **Trigger**
- Temperatur ändert sich nur um 0.4°C → **Kein Trigger**

### Zusätzliche Bedingungen:

- **max_daily_reports**: maximal 4 Dynamic-Berichte pro Tag und Etappe
- **min_interval_min**: mindestens 90 Minuten Abstand zum letzten Dynamic-Bericht

Wird eine relevante Änderung erkannt, aber liegt über diesen Grenzwerten, wird **kein Bericht gesendet**, aber das Ereignis intern gespeichert.

## Output

### Result-Output

Wie bei `morning` und `evening`, z. B.:

    Paliri: N8 D24 R0.2@6(1.40@16) PR20%@11(100%@17) W10@11(15@17) G20@11(30@17) TH:M@16(H@18) S+1:M@14(H@17) HR:M@17TH:H@17 Z:H208,217M:16,24

Länge: max. 160 Zeichen

### Debug-Output

Direkt nach dem Result-Output, getrennt durch:

    # DEBUG DATENEXPORT

Enthält alle Detailtabellen wie bei `morning` und `evening`.

Zusätzlich:
- Neue Sektion `####### RAIN 2H (R2H) #######`
- Analog zu `RAIN`, aber mit Daten aus `forecast_2h` API-Schnittstelle

## Speicher

Alle berechneten Werte und Entscheidungen werden pro Etappe unter:

    .data/weather_reports/YYYY-MM-DD/{etappenname}.json

abgelegt.

Bei ausgelöstem Bericht werden auch Delta-Änderungen protokolliert.

## Testschritte

1. Manueller Aufruf mit `--modus dynamic`
2. Keine Ausgabe bei stabilen Wetterdaten
3. Änderungen über Schwelle erzeugen neue Berichte
4. Keine doppelten Berichte bei zu kurzem Abstand
5. Ausgabeformate konsistent mit anderen Berichtsarten
6. Neuer Abschnitt `RAIN 2H` im Debug sichtbar

## Akzeptanzkriterien

- Dynamic-Modus kann jederzeit manuell ausgeführt werden
- Ein neuer Bericht wird nur bei relevanten Änderungen ausgelöst
- Kein mehrfaches Senden bei zu häufiger Ausführung
- Alle Konfigschwellen korrekt angewendet
- `rain_2h`-Werte werden korrekt dargestellt
- Ausgabeformate konsistent
- Speicherstruktur vollständig