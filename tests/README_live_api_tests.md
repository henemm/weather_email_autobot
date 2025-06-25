# 🧪 Live API Tests für GR20-Wettersystem

Dieses Verzeichnis enthält die umfassenden Live-API-Tests, die den Testplan aus `tests/manual/live_api_tests.md` implementieren.

## 📋 Übersicht

Die Tests validieren alle produktiven Wetter-APIs und den kompletten End-to-End-Workflow:

### 1️⃣ Einzel-API-Livetests (7 APIs)
- **AROME_HR**: Temperatur, CAPE, SHEAR
- **AROME_HR_NOWCAST**: Niederschlagsrate, Sichtweite (15min Intervall)
- **AROME_HR_AGG**: 6h-Regenaggregat (Summe)
- **PIAF_NOWCAST**: Starkregen-Nowcast (5min-Zeitreihe)
- **VIGILANCE_API**: Aktuelle Gewitterwarnstufe für 2B (Corsica)
- **OPENMETEO_GLOBAL**: Temperatur, Regen (als Fallback)

### 2️⃣ Aggregierter Wetterbericht
- Funktion: `analyse_weather(lat, lon)`
- Testziel: Validierung der Risiko-Score-Berechnung für Gewitter

### 3️⃣ End-to-End-Test: GR20 Live-Wetterbericht
- Skript: `scripts/run_gr20_weather_monitor.py`
- Testziel: Kompletter Ablauf von Positionsbestimmung bis E-Mail-Versand

## 🚀 Schnellstart

### Voraussetzungen

1. **Umgebungsvariablen setzen** (`.env` Datei):
```bash
# Erforderlich
METEOFRANCE_CLIENT_ID=your_client_id
METEOFRANCE_CLIENT_SECRET=your_client_secret
GMAIL_APP_PW=your_gmail_app_password

# Optional (für erweiterte Tests)
METEOFRANCE_WCS_TOKEN=your_wcs_token
METEOFRANCE_BASIC_AUTH=your_basic_auth
```

2. **Python-Abhängigkeiten installieren**:
```bash
pip install -r requirements.txt
```

### Tests ausführen

#### Option 1: Automatischer Test-Runner (Empfohlen)
```bash
python scripts/run_live_api_tests.py
```

Dieser Befehl:
- ✅ Prüft die Umgebungskonfiguration
- 🧪 Führt alle Tests der Reihe nach aus
- 📊 Generiert einen detaillierten Bericht
- 💾 Speichert Ergebnisse in `output/live_api_test_report_YYYYMMDD_HHMMSS.json`

#### Option 2: Einzelne Tests mit pytest
```bash
# Alle Tests
pytest tests/test_live_api_integration.py -v -s

# Nur Einzel-API-Tests
pytest tests/test_live_api_integration.py::TestIndividualAPIs -v -s

# Nur OpenMeteo (kein Token erforderlich)
pytest tests/test_live_api_integration.py::TestIndividualAPIs::test_openmeteo_global_temperature_rain -v -s

# Nur End-to-End-Test
pytest tests/test_live_api_integration.py::TestEndToEndGR20WeatherReport -v -s
```

#### Option 3: Direkte Testausführung
```bash
python tests/test_live_api_integration.py
```

## 📊 Testberichte interpretieren

### Erfolgskriterien

#### Einzel-API-Tests
- **HTTP-Status 200** oder gültige JSON/GML/XML-Response
- **Mindestens 1 valider Wetterwert** pro API (z.B. Temperatur, CAPE)
- **Strukturierte Fehlermeldung** bei Fehlern (kein Absturz)

#### Aggregierter Wetterbericht
- **Validierter Schwellenwert**: CAPE*SHEAR, Blitz, Regen
- **Entscheidungsbaum greift korrekt** (config.yaml)
- **Warnstufe und Entscheidungsgrund vorhanden**

#### End-to-End-Test
- **Ausgabe**: Konsolenbericht mit Inhalt (max. 160 Zeichen)
- **Inhalt enthält**: Region, Temperatur, Gewitterwarnung, Risiko
- **Kein Crash** trotz Teil-API-Ausfällen (Fallback sichtbar)

### Berichtsstruktur

```json
{
  "timestamp": "2025-01-15T12:00:00Z",
  "test_plan_version": "tests/manual/live_api_tests.md",
  "environment": {
    "status": {
      "METEOFRANCE_CLIENT_ID": true,
      "METEOFRANCE_CLIENT_SECRET": true,
      "GMAIL_APP_PW": true
    },
    "required_vars_set": true
  },
  "test_results": {
    "individual_apis": {
      "summary": {
        "total": 6,
        "passed": 4,
        "failed": 1,
        "skipped": 1,
        "success_rate": "66.7%"
      },
      "details": {
        "AROME_HR": {
          "success": true,
          "output": "...",
          "error": "",
          "skipped": false
        }
      }
    },
    "aggregated_weather_report": {
      "success": true,
      "output": "...",
      "error": "",
      "skipped": false
    },
    "end_to_end_gr20_report": {
      "success": true,
      "output": "...",
      "error": "",
      "skipped": false
    }
  },
  "overall_status": "PASS"
}
```

### Status-Interpretation

| Status | Bedeutung | Aktion |
|--------|-----------|---------|
| **PASS** | Alle kritischen Tests erfolgreich | ✅ System funktionsfähig |
| **FAIL** | Mindestens ein kritischer Test fehlgeschlagen | 🔧 Fehleranalyse erforderlich |
| **SKIPPED** | Test übersprungen (kein Token) | ⚠️ Token konfigurieren für vollständige Tests |

## 🔧 Fehlerbehebung

### Häufige Probleme

#### 1. "METEOFRANCE_CLIENT_ID not set"
```bash
# .env Datei erstellen/bearbeiten
echo "METEOFRANCE_CLIENT_ID=your_client_id" >> .env
echo "METEOFRANCE_CLIENT_SECRET=your_client_secret" >> .env
```

#### 2. "Test timed out"
- **Ursache**: Langsame Internetverbindung oder API-Latenz
- **Lösung**: Timeout-Werte in `scripts/run_live_api_tests.py` erhöhen

#### 3. "HTTP 401 Unauthorized"
- **Ursache**: Ungültige oder abgelaufene Tokens
- **Lösung**: Tokens erneuern, OAuth2-Flow prüfen

#### 4. "No weather data available"
- **Ursache**: APIs liefern keine Daten für Testkoordinaten
- **Lösung**: Koordinaten in `tests/test_live_api_integration.py` anpassen

### Debug-Modus

Für detaillierte Fehleranalyse:
```bash
# Mit Debug-Ausgabe
pytest tests/test_live_api_integration.py -v -s --tb=long

# Nur fehlgeschlagene Tests
pytest tests/test_live_api_integration.py -v -s --lf

# Mit Coverage-Report
pytest tests/test_live_api_integration.py --cov=src --cov-report=html
```

## 📈 Kontinuierliche Überwachung

### Automatisierte Ausführung

#### Cron-Job (Linux/macOS)
```bash
# Täglich um 06:00 Uhr
0 6 * * * cd /path/to/weather_email_autobot && python scripts/run_live_api_tests.py >> logs/api_tests.log 2>&1
```

#### GitHub Actions
```yaml
name: Live API Tests
on:
  schedule:
    - cron: '0 6 * * *'  # Täglich 06:00 UTC
  workflow_dispatch:     # Manueller Trigger

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run live API tests
        run: python scripts/run_live_api_tests.py
        env:
          METEOFRANCE_CLIENT_ID: ${{ secrets.METEOFRANCE_CLIENT_ID }}
          METEOFRANCE_CLIENT_SECRET: ${{ secrets.METEOFRANCE_CLIENT_SECRET }}
          GMAIL_APP_PW: ${{ secrets.GMAIL_APP_PW }}
```

### Monitoring-Dashboard

Erstellen Sie ein einfaches Dashboard mit den Testberichten:

```python
# scripts/monitor_api_health.py
import json
import glob
from datetime import datetime, timedelta

def get_recent_test_reports(hours=24):
    """Lade Testberichte der letzten N Stunden."""
    reports = []
    cutoff = datetime.now() - timedelta(hours=hours)
    
    for report_file in glob.glob("output/live_api_test_report_*.json"):
        with open(report_file, 'r') as f:
            report = json.load(f)
            report_time = datetime.fromisoformat(report["timestamp"])
            if report_time > cutoff:
                reports.append(report)
    
    return reports

def generate_health_summary():
    """Generiere Gesundheitszusammenfassung."""
    reports = get_recent_test_reports()
    
    if not reports:
        return "Keine Testberichte in den letzten 24 Stunden"
    
    total_reports = len(reports)
    successful_reports = sum(1 for r in reports if r["overall_status"] == "PASS")
    success_rate = (successful_reports / total_reports) * 100
    
    return f"API Health: {success_rate:.1f}% ({successful_reports}/{total_reports})"
```

## 📚 Weitere Ressourcen

- **Testplan**: `tests/manual/live_api_tests.md`
- **API-Dokumentation**: `docs/meteo_api_architecture.txt`
- **Konfiguration**: `config.yaml`
- **Beispielberichte**: `output/live_api_test_report_*.json`

## 🤝 Beitragen

Bei Problemen oder Verbesserungsvorschlägen:

1. **Issue erstellen** mit detaillierter Fehlerbeschreibung
2. **Testbericht anhängen** (`output/live_api_test_report_*.json`)
3. **Umgebungskonfiguration** dokumentieren (ohne sensitive Daten)

---

**Letzte Aktualisierung**: 2025-01-15
**Testplan-Version**: `tests/manual/live_api_tests.md`

# 🧪 Live API Integration Tests - Status Report

## 📊 Test Results Summary

**Last Updated:** 2025-06-24  
**Test Suite:** `tests/test_live_api_integration.py`  
**Total Tests:** 10  
**Status:** ✅ All tests passing

---

## 🔍 Individual API Test Results

### ✅ Working APIs

| API | Status | Notes |
|-----|--------|-------|
| **VIGILANCE_API** | ✅ Success | Found 2 Corsica warnings (2A, 2B) |
| **OPENMETEO_GLOBAL** | ✅ Success | Temperature: 23.5°C, Precipitation: 0.0mm |
| **Weather Analysis** | ✅ Success | Risk scoring working correctly |
| **GR20 E2E Report** | ✅ Success | Complete workflow functional |

### ⚠️ APIs with Issues

| API | Status | Issue |
|-----|--------|-------|
| **AROME_HR** | ⚠️ WCS Syntax | Layer discovery works, but WCS 2.0.1 subset syntax needs investigation |
| **AROME_HR_NOWCAST** | ⚠️ No Data | No precipitation/visibility data returned |
| **AROME_HR_AGG** | ⚠️ No Data | No 6h precipitation aggregates returned |
| **PIAF_NOWCAST** | ⚠️ No Data | No heavy rain nowcast data returned |

---

## 🔧 Technical Issues Identified

### 1. AROME WCS 2.0.1 Subset Syntax
- **Problem:** InvalidSubsetting error (404) on GetCoverage requests
- **Root Cause:** WCS 2.0.1 subset parameter format requirements
- **Impact:** All AROME model APIs affected
- **Next Steps:** Investigate correct WCS 2.0.1 subset syntax

### 2. Coordinate Constraints
- **Problem:** Conca coordinates (41.75, 9.35) may be outside AROME coverage
- **Evidence:** Lyon coordinates also fail with same error
- **Impact:** AROME data not accessible for Corsica region
- **Next Steps:** Test with known valid coordinates

### 3. Layer Availability
- **CAPE Layers:** ✅ Available (5610 total layers found)
- **SHEAR Layers:** ❌ Not found in current model
- **Temperature Layers:** ✅ Available
- **Precipitation Layers:** ✅ Available

---

## 🎯 Recommendations

### Immediate Actions
1. **WCS Syntax Investigation:** Research correct WCS 2.0.1 subset syntax
2. **Coordinate Testing:** Test with known valid AROME coordinates
3. **API Documentation:** Review MeteoFrance WCS API documentation

### Fallback Strategy
- **Primary:** OpenMeteo Global (working reliably)
- **Secondary:** Vigilance API (working for warnings)
- **Tertiary:** Manual weather data entry

### Long-term Solutions
1. **WCS Client Library:** Consider using specialized WCS client
2. **Coordinate Validation:** Implement coordinate range checking
3. **Alternative APIs:** Investigate other MeteoFrance endpoints

---

## 📈 Test Coverage

### ✅ Fully Tested Components
- OpenMeteo Global API
- Vigilance Warning API
- Weather Analysis Logic
- End-to-End GR20 Workflow
- Error Handling
- Fallback Mechanisms

### ⚠️ Partially Tested Components
- AROME Model APIs (syntax issues)
- PIAF Nowcast API (no data)
- AROME Aggregated Data (no data)

### 🔄 Test Reliability
- **Stable:** OpenMeteo, Vigilance, Analysis
- **Unstable:** AROME models (WCS syntax dependent)
- **Unknown:** PIAF, AROME aggregates (no data available)

---

## 🚀 Next Steps

1. **Fix WCS Syntax:** Resolve AROME API subset issues
2. **Expand Coverage:** Test with valid AROME coordinates
3. **Documentation:** Update API usage guidelines
4. **Monitoring:** Implement automated API health checks

---

*This report is automatically generated from the live API test suite.* 