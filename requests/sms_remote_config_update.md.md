# Rule: Dynamische Konfigurationsanpassung per SMS (Trigger-gestützt)

## Zielsetzung
Erlaube eine gezielte Änderung definierter Konfigurationswerte in config.yaml über den Empfang spezieller SMS-Befehle. Die Änderung erfolgt ohne feste Absendernummer, ausschließlich gesteuert über ein eindeutig erkennbares Befehlsformat.

## Befehlssyntax
- Jede gültige Steuer-SMS beginnt mit ### gefolgt von einem Leerzeichen
- Format: ### <key>: <value>
- <key> entspricht exakt dem Pfad in der YAML-Struktur (Punktnotation für verschachtelte Keys)
- <value> wird typisiert geprüft und bei Gültigkeit übernommen

## Unterstützte Schlüssel (Whitelist)
Nur folgende Keys dürfen modifiziert werden:

startdatum  
sms.production_number  
sms.test_number  
thresholds.cloud_cover  
thresholds.rain_amount  
thresholds.rain_probability  
thresholds.temperature  
thresholds.thunderstorm_probability  
thresholds.wind_speed  
delta_thresholds.rain_probability  
delta_thresholds.temperature  
delta_thresholds.thunderstorm_probability  
delta_thresholds.wind_speed  
max_daily_reports  
min_interval_min

## Typprüfung

| Schlüssel enthält              | Erwarteter Typ         |
|-------------------------------|-------------------------|
| startdatum                    | Datum (YYYY-MM-DD)      |
| number, production, test      | String (Telefonnummer)  |
| thresholds.                   | Float (z. B. 30.0)       |
| delta_thresholds.             | Float (z. B. 90.0)       |
| max_daily_reports             | Integer                 |
| min_interval_min              | Integer                 |

## Verarbeitungsschritte

1. Prüfe, ob eine SMS mit ### beginnt → sonst ignorieren
2. Extrahiere key und value anhand Trennzeichen :
3. Prüfe:
   - Ist key in Whitelist enthalten?
   - Ist value dem erwarteten Datentyp zuordenbar?
   - Ist bei startdatum ein valides Datum angegeben?
4. Wenn alle Checks erfolgreich:
   - Ändere entsprechenden Eintrag in config.yaml
   - Erhalte Struktur und Formatierung der YAML-Datei
5. Logge jede Änderung mit Timestamp

## Ausschlüsse
- Keine Authentifizierung über SMS-Absender
- Keine Änderungen an API-Schlüsseln, Mail-Zugang oder File-Pfaden
- Keine Mehrfachbefehle pro SMS
- Keine YAML-Strukturanalyse oder Verschachtelung außerhalb Whitelist

## Logging & Fehlerbehandlung
- Jede Nachricht wird in logs/sms_config_updates.log gespeichert
- Bei Fehlern (z. B. falscher Key oder Datentyp):
  - Eintrag mit Hinweis INVALID FORMAT
  - Keine Änderung an Datei