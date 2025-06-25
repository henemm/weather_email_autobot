requests/schedule_gr20_weather_report.md
---

title: GR20 Wetterbericht zeitgesteuert senden
status: ✅ COMPLETED

## Ziel

Regelmäßige Wetterberichte für die aktuelle Etappe des GR20 per E-Mail versenden.

## Trigger

- Morgens: 04:30 Uhr
- Abends: 19:00 Uhr
- Tagsüber (04:30–19:00): max. 3 dynamische Berichte bei wesentlichen Änderungen

## Input

- config.yaml: Enthält Schwellenwerte, E-Mail-Konfiguration, Etappeninformationen
- etappen.json: Bestimmt die aktuelle Region durch GPS-Position oder manuelle Etappenwahl
- Wetterdaten: AROME, AROMEPI, PIAF, Open-Meteo
- Position: Via ShareMap oder festgelegter Etappenpunkt

## Verarbeitung

1. Scheduler-Modul prüft Zeit + Änderungsschwelle.
2. Analysemodul erzeugt Risikoindikatoren (Gewitter, Regen etc.)
3. E-Mail-Client generiert maximal 160 Zeichen lange Nachricht mit:
   - Region / Etappe
   - Status (Wetterwarnung, Prognoseindikatoren)
   - Link zu Detailansicht
   - ggf. Emoji für schnellen Eindruck
4. Versand via SMTP (GMail, GMAIL_APP_PW aus Umgebungsvariable)

## Tests

- Unit-Tests für Scheduler (Testzeit, Triggerlogik)
- Unit-Tests für Formatierung und Zustellung
- Integrationstest mit E-Mail-Sendeschleife

## Abhängigkeiten

- SMTP_PASSWORD (bzw. GMAIL_APP_PW) muss gesetzt sein
- Abfrage ShareMap-Position oder Etappenindex
- Zeitplan aktiviert durch `scripts/run_gr20_weather_monitor.py`

## Status

✅ COMPLETED

notes: GMail-Versand via SMTP mit GMAIL_APP_PW umgesetzt; produktiv einsatzfähig; API-Statusprüfung weiterhin sinnvoll.