# GitHub Release: Version 1.1.1

## Ziel

Der aktuelle Stand des Projekts soll als Version `1.1.1` auf GitHub veröffentlicht werden. Der Stand enthält alle getesteten und produktionsreifen Funktionen bis einschließlich des modularisierten SMS-Versands mit seven.io.

## Inhalt des Releases

### 🔧 Neu: SMS-Versand

- Integration von `seven.io` als erster SMS-Provider
- Konfiguration via `config.yaml`
- Unterstützung von internationalen Zielnummern (z. B. +49…)
- Sendeprotokolle werden geloggt und Fehler behandelt
- SMS-Format identisch zur E-Mail-Ausgabe (InReach-kompatibel)

### ✅ Verbesserungen

- Gewitter- und Regenlogik vollständig überarbeitet
- Validierungs-Framework mit Dummy-Daten für Testläufe ergänzt
- `meteofrance-api` ersetzt rohe AROME-Zugriffe vollständig
- Dynamischer Risikomonitor arbeitet robust und regelbasiert
- Logging differenziert zwischen E-Mail, SMS und Analyse

### 🔁 Struktur

- Berichte für Abend/Morgen/Tag getrennt getestet
- Konfigurierbare Schwellenwerte (`config.yaml`)
- Warnlogik über alle Etappenpunkte hinweg aggregiert

## Technische Details

- Commit-Stand: letzter Stand vor Integration von Twilio oder anderen Providern
- Branch: `main` (oder stabiler Feature-Branch, wenn zutreffend)
- Tag: `v1.1.1`
- Release-Name: `Version 1.1.1 – SMS & Stabilität`
- Veröffentlichungsform: GitHub Release mit Change-Log und kurzer Beschreibung

## Akzeptanzkriterien

- Alle Commit-Daten enthalten
- Release-Tag korrekt gesetzt (`v1.1.1`)
- Change-Log reflektiert aktuelle Features und Änderungen
- Release kann als Basis für den Produktivbetrieb genutzt werden