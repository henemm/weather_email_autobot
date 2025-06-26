# SMS-Funktionalität für GR20 Wetterberichte

## Übersicht

Die SMS-Funktionalität ermöglicht es, Wetterberichte zusätzlich zur E-Mail auch per SMS über den Dienst seven.io zu versenden. Die Implementierung folgt den gleichen Formaten und Regeln wie die E-Mail-Berichte.

## Konfiguration

### Umgebungsvariablen (.env)

Nur sensible Daten werden über Umgebungsvariablen konfiguriert. Erstellen Sie eine `.env` Datei im Projektverzeichnis:

```bash
# =============================================================================
# ENVIRONMENT VARIABLES FOR GR20 WEATHER AUTOMATION
# =============================================================================

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
GMAIL_APP_PW=your_gmail_app_password_here

# =============================================================================
# SMS CONFIGURATION
# =============================================================================
# API key from seven.io (https://seven.io)
SEVEN_API_KEY=your_seven_api_key_here

# =============================================================================
# OPENMETEO CONFIGURATION (optional)
# =============================================================================
OPENMETEO_API_KEY=your_openmeteo_api_key_here
```

### config.yaml

Die SMS-Konfiguration wird in der `config.yaml` Datei unter dem Abschnitt `sms` definiert:

```yaml
sms:
  enabled: true
  provider: seven
  # API-Schlüssel wird aus Umgebungsvariable SEVEN_API_KEY geladen
  api_key: "${SEVEN_API_KEY}"
  # Testnummer für Entwicklung und Tests
  test_number: "+49123456789"
  # Produktionsnummer für echte Berichte
  production_number: "+49987654321"
  # Aktuell verwendete Nummer (test oder production)
  mode: "test"  # "test" oder "production"
  sender: "GR20-Info"
```

### Parameter

- `enabled`: Aktiviert/deaktiviert die SMS-Funktionalität (true/false)
- `provider`: SMS-Provider (aktuell nur "seven" unterstützt)
- `api_key`: API-Schlüssel für seven.io (aus Umgebungsvariable)
- `test_number`: Testtelefonnummer für Entwicklung und Tests
- `production_number`: Produktionstelefonnummer für echte Berichte
- `mode`: Betriebsmodus ("test" oder "production")
- `sender`: Absendername (max. 11 Zeichen)

## Kommandozeilen-Parameter

### --sms Parameter

Der `--sms` Parameter ermöglicht es, den SMS-Modus direkt beim Aufruf zu überschreiben:

```bash
# Test-Modus verwenden (überschreibt config.yaml)
python scripts/run_gr20_weather_monitor.py --modus morning --sms test

# Produktions-Modus verwenden (überschreibt config.yaml)
python scripts/run_gr20_weather_monitor.py --modus morning --sms production

# Kombination mit anderen Parametern
python scripts/run_gr20_weather_monitor.py --modus evening --sms test
python scripts/run_gr20_weather_monitor.py --modus dynamic --sms production
```

### Verwendung

- **Entwicklung**: `--sms test` für Tests mit Testnummer
- **Produktion**: `--sms production` für echte Berichte mit Produktionsnummer
- **Flexibilität**: Ermöglicht schnellen Wechsel ohne config.yaml-Änderung
- **Sicherheit**: Verhindert versehentlichen Versand an Produktionsnummer während Tests

### Beispiel-Ausgabe

```bash
$ python scripts/run_gr20_weather_monitor.py --modus morning --sms test
Starting GR20 Weather Report Monitor...
Configuration loaded successfully
SMS mode overridden: production -> test
SMS client initialized successfully
SMS mode: test
SMS recipient: +49123456789
Components initialized successfully
...
```

## Implementierung

### SMSClient Klasse

Die Hauptimplementierung befindet sich in `src/notification/sms_client.py`:

```python
from src.notification.sms_client import SMSClient

# Initialisierung
config = load_config()
sms_client = SMSClient(config)

# SMS senden
success = sms_client.send_sms("Test message")

# GR20 Bericht senden
report_data = {
    "location": "Vizzavona",
    "report_type": "morning",
    "weather_data": {...},
    "report_time": datetime.now()
}
success = sms_client.send_gr20_report(report_data)
```

### API-Integration

Die SMS werden über die seven.io HTTP REST API versendet:

- **URL**: `https://gateway.seven.io/api/sms`
- **Methode**: POST
- **Headers**: `Authorization: Bearer <api_key>`
- **Body**: Form-encoded mit `to`, `from`, `text`

## Betriebsmodi

### Test-Modus

- **Zweck**: Entwicklung, Tests und Debugging
- **Telefonnummer**: Verwendet `test_number`
- **Verwendung**: Für Entwicklung und Testläufe
- **Kommandozeile**: `--sms test`

```yaml
sms:
  mode: "test"
  test_number: "+49123456789"
  production_number: "+49987654321"
```

### Produktions-Modus

- **Zweck**: Echte Wetterberichte an Endbenutzer
- **Telefonnummer**: Verwendet `production_number`
- **Verwendung**: Für den produktiven Einsatz
- **Kommandozeile**: `--sms production`

```yaml
sms:
  mode: "production"
  test_number: "+49123456789"
  production_number: "+49987654321"
```

## Berichtsformate

### Morgenbericht (04:30 Uhr)

```
{EtappeHeute} | Gewitter {g1}%@{t1} {g2}%@{t2} | Regen {r1}%@{t3} {r2}%@{t4} {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h | Gewitter +1 {g1_next}% | {vigilance_warning}
```

**Beispiel:**
```
Vizzavona | Gewitter 45%@14:00 30% | Regen 60%@12:00 50% 5.2mm | Hitze 28.5°C | Wind 25km/h | Gewitter +1 35% | ORANGE Gewitter
```

### Abendbericht (19:00 Uhr)

```
{EtappeMorgen}→{EtappeÜbermorgen} | Nacht {min_temp}°C | Gewitter {g1}%@{t1} ({g2}%@{t2}) | Gewitter +1 {g1_next}% | Regen {r1}%@{t3} ({r2}%@{t4}) {regen_mm}mm | Hitze {temp_max}°C | Wind {wind_max}km/h | {vigilance_warning}
```

**Beispiel:**
```
HautAsco | Nacht 12.5°C | Gewitter 35%(25%@15:00) | Gewitter +1 40% | Regen 45%(40%@13:00) 3.8mm | Hitze 26.0°C | Wind 30km/h | GELB Regen
```

### Dynamischer Bericht

```
{EtappeHeute} | Update: Gewitter {g2}%@{t2} | Regen {r2}%@{t4} | Hitze {temp_max}°C | Wind {wind_max}km/h | {vigilance_warning}
```

**Beispiel:**
```
Conca | Update: Gewitter 40%@16:00 | Regen 55%@14:00 | Hitze 29.0°C | Wind 35km/h | ROT Gewitter
```

## Zeichenbegrenzung

- **Maximallänge**: 160 Zeichen
- **Automatische Kürzung**: Bei Überschreitung wird der Text auf 160 Zeichen gekürzt
- **Priorisierung**: Wichtige Informationen werden bei der Kürzung bevorzugt

## Vigilance-Warnungen

Vigilance-Warnungen werden in den SMS-Berichten wie folgt formatiert:

- **Level 1 (Gelb)**: `GELB {Typ}`
- **Level 2 (Orange)**: `ORANGE {Typ}`
- **Level 3 (Rot)**: `ROT {Typ}`

## Integration in das Hauptsystem

Die SMS-Funktionalität ist in das Hauptsystem integriert:

1. **Automatische Initialisierung**: Der SMSClient wird beim Start des Wettermonitors initialisiert
2. **Paralleler Versand**: SMS und E-Mail werden parallel versendet
3. **Fehlerbehandlung**: Fehler beim SMS-Versand beeinträchtigen nicht den E-Mail-Versand
4. **Statusverwaltung**: Der Scheduler wird nur aktualisiert, wenn mindestens eine Nachricht erfolgreich versendet wurde
5. **Kommandozeilen-Override**: SMS-Modus kann über `--sms` Parameter überschrieben werden

## Tests

### Unit-Tests

```bash
python -m pytest tests/test_sms_client.py -v
```

### Funktionalitätstest

```bash
python scripts/test_sms_functionality.py
```

### Kommandozeilen-Parameter Test

```bash
# Test-Modus
python scripts/run_gr20_weather_monitor.py --modus morning --sms test

# Produktions-Modus
python scripts/run_gr20_weather_monitor.py --modus morning --sms production

# Hilfe anzeigen
python scripts/run_gr20_weather_monitor.py --help
```

## Fehlerbehandlung

### Häufige Fehler

1. **401 Unauthorized**: Falscher API-Schlüssel
2. **400 Bad Request**: Ungültige Telefonnummer oder Absendername
3. **Network Error**: Keine Internetverbindung
4. **Missing Environment Variable**: Umgebungsvariable nicht gesetzt

### Logging

Fehler werden in der Konsole protokolliert:

```
Failed to send SMS: HTTP 401 - Unauthorized
Failed to send SMS: Network error
Environment variable 'SEVEN_API_KEY' not found
```

## Setup

### 1. Seven.io Account

1. Registrieren Sie sich bei [seven.io](https://seven.io)
2. Erhalten Sie Ihren API-Schlüssel
3. Testen Sie die API mit einem Test-SMS

### 2. Umgebungsvariablen konfigurieren

1. Erstellen Sie eine `.env` Datei im Projektverzeichnis
2. Fügen Sie Ihren API-Schlüssel hinzu:

```bash
SEVEN_API_KEY=your_seven_api_key_here
```

### 3. Konfiguration anpassen

1. Überprüfen Sie die `config.yaml` Datei
2. Passen Sie die Telefonnummern an:
   ```yaml
   sms:
     test_number: "+49your_test_number"
     production_number: "+49your_production_number"
   ```
3. Stellen Sie sicher, dass `mode: "test"` für Entwicklung gesetzt ist
4. Ändern Sie zu `mode: "production"` für den produktiven Einsatz

### 4. Test

```bash
# Funktionalitätstest
python scripts/test_sms_functionality.py

# Test mit Kommandozeilen-Parameter
python scripts/run_gr20_weather_monitor.py --modus morning --sms test

# Vollständiger Systemtest
python scripts/run_gr20_weather_monitor.py --modus morning
```

## Sicherheit

- **API-Schlüssel**: Sensible Daten werden über Umgebungsvariablen verwaltet
- **Test/Produktion-Trennung**: Separate Telefonnummern für Tests und Produktion
- **Kommandozeilen-Override**: Sichere Überschreibung des SMS-Modus
- **Fehlerbehandlung**: Robuste Behandlung von API-Fehlern
- **Logging**: Detaillierte Protokollierung von Fehlern
- **Validierung**: Umfassende Konfigurationsvalidierung

## Kosten

- **Seven.io**: Kostenlose Test-SMS verfügbar
- **Produktive Nutzung**: Kostenpflichtig, Preise variieren nach Land und Volumen
- **Test-Modus**: Ermöglicht kostenlose Entwicklung und Tests

## Troubleshooting

### SMS werden nicht versendet

1. Prüfen Sie die `.env` Datei und Umgebungsvariablen
2. Überprüfen Sie den API-Schlüssel
3. Testen Sie die Internetverbindung
4. Prüfen Sie die Logs auf Fehlermeldungen
5. Stellen Sie sicher, dass der richtige Modus gesetzt ist
6. Überprüfen Sie den `--sms` Parameter bei manuellen Aufrufen

### Falsche Telefonnummer

1. Überprüfen Sie die Telefonnummern in `config.yaml`
2. Prüfen Sie den `mode` in `config.yaml`
3. Überprüfen Sie den `--sms` Parameter bei manuellen Aufrufen
4. Testen Sie mit dem Funktionalitätstest

### Umgebungsvariablen-Fehler

1. Stellen Sie sicher, dass die `.env` Datei existiert
2. Überprüfen Sie die Syntax der Umgebungsvariablen
3. Prüfen Sie, dass alle erforderlichen Variablen gesetzt sind

### API-Fehler

1. Überprüfen Sie den API-Schlüssel in der `.env` Datei
2. Prüfen Sie das Seven.io Dashboard
3. Kontaktieren Sie den Seven.io Support bei anhaltenden Problemen

### Kommandozeilen-Parameter Probleme

1. Überprüfen Sie die Syntax: `--sms test` oder `--sms production`
2. Stellen Sie sicher, dass der Parameter vor anderen Argumenten steht
3. Prüfen Sie die Hilfe: `python scripts/run_gr20_weather_monitor.py --help`

## Best Practices

### Entwicklung

1. **Immer im Test-Modus entwickeln**: `mode: "test"` in config.yaml
2. **Kommandozeilen-Parameter verwenden**: `--sms test` für Tests
3. **Testnummer verwenden**: Separate Nummer für Tests
4. **Umgebungsvariablen verwenden**: Keine sensiblen Daten in Version Control
5. **Regelmäßige Tests**: Funktionalitätstest vor jedem Commit

### Produktion

1. **Produktions-Modus aktivieren**: `mode: "production"` in config.yaml
2. **Kommandozeilen-Parameter verwenden**: `--sms production` für echte Berichte
3. **Produktionsnummer verwenden**: Echte Zielnummer für Berichte
4. **Monitoring**: Überwachung der API-Nutzung und Kosten
5. **Backup-Plan**: E-Mail-Funktionalität als Fallback

### Sicherheit

1. **API-Schlüssel schützen**: Niemals in Version Control committen
2. **Regelmäßige Rotation**: API-Schlüssel regelmäßig erneuern
3. **Zugriffskontrolle**: Nur autorisierte Personen haben Zugriff auf Produktionsdaten
4. **Audit-Logs**: Protokollierung aller SMS-Versände
5. **Kommandozeilen-Sicherheit**: Vorsicht bei der Verwendung von `--sms production`

### Workflow

1. **Entwicklung**: `--sms test` für alle Tests
2. **Staging**: `--sms test` mit Produktionsnummer in config.yaml
3. **Produktion**: `--sms production` oder `mode: "production"` in config.yaml
4. **Monitoring**: Überwachung der SMS-Versände und API-Nutzung 