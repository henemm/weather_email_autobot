# SMS Polling Architecture

## Übersicht

Die SMS Polling Architecture ist eine Alternative zur Webhook-basierten Lösung für die Verarbeitung von SMS-Konfigurationsbefehlen. Statt einen öffentlich erreichbaren Webhook-Server zu betreiben, werden eingehende SMS-Nachrichten regelmäßig über die Seven.io API abgefragt.

## Vorteile

### ✅ **Sicherheit**
- Keine öffentliche IP/Port erforderlich
- Keine Firewall-Konfiguration nötig
- Reduzierte Angriffsfläche

### ✅ **Einfachheit**
- Kein Webhook-Server erforderlich
- Keine SSL-Zertifikate nötig
- Einfacher zu deployen und warten

### ✅ **Robustheit**
- Funktioniert auch bei Netzwerkproblemen
- Keine Abhängigkeit von externen Webhook-Aufrufen
- Automatische Wiederholung bei Fehlern

### ✅ **Flexibilität**
- Polling-Intervall konfigurierbar
- Einfache Integration in bestehende Cron-Jobs
- Unabhängig von Server-Uptime

## Architektur

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cron Job      │───▶│  SMS Polling     │───▶│  Seven.io API   │
│  (alle 10 Min)  │    │   Client         │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Config Processor │
                       │                  │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   config.yaml    │
                       └──────────────────┘
```

## Komponenten

### 1. **SMSPollingClient**
- Hauptkomponente für API-Kommunikation
- Verarbeitet eingehende Nachrichten
- Dedupliziert bereits verarbeitete Nachrichten

### 2. **SMSConfigProcessor**
- Verarbeitet Konfigurationsbefehle
- Validiert Whitelist und Datentypen
- Aktualisiert config.yaml

### 3. **check_sms_commands.py**
- CLI-Script für manuelle Ausführung
- Integriert in Cron-Jobs
- Konfigurierbare Logging-Level

## Installation und Setup

### 1. **Seven.io Account**
```bash
# API-Key in .env setzen
SEVEN_API_KEY=your_seven_api_key_here
```

### 2. **Cron-Job einrichten**
```bash
# Alle 10 Minuten SMS abfragen
*/10 * * * * cd /opt/weather_email_autobot && python scripts/check_sms_commands.py

# Oder alle 5 Minuten für schnellere Reaktion
*/5 * * * * cd /opt/weather_email_autobot && python scripts/check_sms_commands.py
```

### 3. **Manuelle Ausführung**
```bash
# Einmalige Ausführung
python scripts/check_sms_commands.py

# Mit Debug-Logging
python scripts/check_sms_commands.py --log-level DEBUG

# Cleanup alter Nachrichten
python scripts/check_sms_commands.py --cleanup
```

## Konfiguration

### config.yaml
```yaml
sms:
  enabled: true
  provider: seven
  api_key: "${SEVEN_API_KEY}"  # Aus Umgebungsvariable
  test_number: "+49123456789"
  production_number: "+49987654321"
  mode: "test"
  sender: "GR20-Info"
```

### .env
```bash
# Seven.io API Key
SEVEN_API_KEY=your_seven_api_key_here
```

## SMS-Befehlsformat

### Syntax
```
### <key>: <value>
```

### Beispiele
```
### thresholds.temperature: 25.0
### max_daily_reports: 5
### startdatum: 2025-07-08
### sms.test_number: +49123456789
```

### Unterstützte Keys
- `startdatum` (Datum: YYYY-MM-DD)
- `sms.production_number` (Telefonnummer)
- `sms.test_number` (Telefonnummer)
- `thresholds.*` (Float-Werte)
- `delta_thresholds.*` (Float-Werte)
- `max_daily_reports` (Integer)
- `min_interval_min` (Integer)

## Logging

### Log-Dateien
- `logs/sms_polling.log` - Hauptlog für Polling-Aktivitäten
- `logs/sms_config_updates.log` - Konfigurationsänderungen

### Log-Format
```
2025-07-08 10:30:00 | seven | +49987654321 | ### thresholds.temperature: 25.0...
2025-07-08 10:30:01 | SUCCESS | thresholds.temperature | 25.0 | Configuration updated successfully
```

## Fehlerbehandlung

### API-Fehler
- Automatische Wiederholung bei Netzwerkfehlern
- Logging aller API-Antworten
- Graceful Degradation bei Seven.io Ausfällen

### Validierungsfehler
- Detaillierte Fehlermeldungen
- Keine Konfigurationsänderung bei ungültigen Befehlen
- Logging aller Validierungsfehler

### Systemfehler
- Exception-Handling für alle Komponenten
- Rollback bei Konfigurationsfehlern
- Detaillierte Error-Logs

## Monitoring

### Health Checks
```bash
# Log-Dateien prüfen
tail -f logs/sms_polling.log

# Letzte Ausführung prüfen
grep "SMS polling completed" logs/sms_polling.log | tail -1
```

### Metriken
- Anzahl abgerufener Nachrichten
- Anzahl verarbeiteter Befehle
- API-Response-Zeiten
- Fehlerrate

## Vergleich: Polling vs Webhook

| Aspekt | Polling | Webhook |
|--------|---------|---------|
| **Setup** | Einfach (Cron-Job) | Komplex (Server + SSL) |
| **Sicherheit** | Hoch (keine öffentliche IP) | Mittel (öffentlicher Endpunkt) |
| **Latenz** | 5-10 Minuten | Sofort |
| **Zuverlässigkeit** | Hoch | Abhängig von Netzwerk |
| **Wartung** | Minimal | Regelmäßige Updates |
| **Skalierbarkeit** | Einfach | Komplex |

## Empfehlung

**Polling-Architektur empfohlen für:**
- Nicht-zeitkritische Konfigurationsänderungen
- Einfache Deployment-Umgebungen
- Hohe Sicherheitsanforderungen
- Minimale Wartungsaufwand

**Webhook-Architektur empfohlen für:**
- Zeitkritische Anwendungen
- Echtzeit-Benachrichtigungen
- Komplexe Event-basierte Systeme

## Troubleshooting

### Häufige Probleme

1. **Keine Nachrichten gefunden**
   - API-Key prüfen
   - Seven.io Account-Status prüfen
   - Log-Level auf DEBUG setzen

2. **Konfiguration wird nicht aktualisiert**
   - Befehlssyntax prüfen (### am Anfang)
   - Key in Whitelist prüfen
   - Datentyp validieren

3. **Cron-Job funktioniert nicht**
   - Pfad zur Python-Umgebung prüfen
   - Berechtigungen prüfen
   - Cron-Logs prüfen

### Debug-Modus
```bash
# Detailliertes Logging aktivieren
python scripts/check_sms_commands.py --log-level DEBUG

# API-Antworten anzeigen
grep "API response" logs/sms_polling.log
```

## Migration von Webhook zu Polling

1. **Webhook-Server stoppen**
   ```bash
   pkill -f run_sms_webhook_server.py
   ```

2. **Cron-Job einrichten**
   ```bash
   crontab -e
   # */10 * * * * cd /opt/weather_email_autobot && python scripts/check_sms_commands.py
   ```

3. **Seven.io Webhook deaktivieren**
   - Webhook-URL in Seven.io Dashboard entfernen

4. **Tests durchführen**
   ```bash
   python scripts/check_sms_commands.py --log-level DEBUG
   ``` 