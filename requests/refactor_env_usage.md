# Refactoring: Zentrale Verwaltung von Umgebungsvariablen über `env_loader`

## Ziel
Vereinheitlichung und Absicherung des Zugriffs auf Umgebungsvariablen in Tests und Produktionscode.

## Problem
- Unterschiedliche Stellen nutzten `os.getenv()` direkt, was zu inkonsistentem Verhalten führte.
- In Tests wurde `.env` nicht korrekt geladen, wenn Variablen bereits in der Shell gesetzt waren.
- Das führte zu schwer nachvollziehbaren Fehlern (z. B. bei Token-Validierung).

## Lösung
Ein zentrales Utility wurde unter `src/utils/env_loader.py` eingeführt:
- Lädt `.env` mit `override=True` → `.env` hat immer Vorrang.
- Bietet mit `get_env_var(name, default)` eine sichere und getestete Zugriffsmethode.

## Refaktorierte Module
- `src/auth/meteo_token_provider.py`
- `src/config/config_loader.py`

## Tests
- `tests/test_env_loader_production.py`
- `tests/test_meteo_token_provider.py`

Alle Tests laufen grün. Das Verhalten bei Konflikten zwischen Shell- und .env-Werten wurde getestet.

## Vorteile
- Konsistente und nachvollziehbare Lade-Reihenfolge
- Kapselung von dotenv-Logik
- Geringeres Risiko für Fehlkonfigurationen in verschiedenen Deployments

## Weitere Schritte (optional)
- Audit: Weitere direkte `os.getenv()`-Nutzung prüfen
- Deployment-Hinweise ergänzen
- `.env`-Behandlung dokumentieren für Entwickler:innen

## Status
✅ Abgeschlossen