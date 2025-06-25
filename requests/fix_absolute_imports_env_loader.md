# Korrektur: Absolute Imports für env_loader sicherstellen

## Ziel
Behebe Import-Konflikte durch falsch aufgelöste Pfade zu `env_loader.py`.

## Hintergrund
Aktuell verwendet `src/auth/meteo_token_provider.py` einen relativen Import, der in bestimmten Konfigurationen (z. B. bei lokalen Tests oder Deployment-Skripten) versehentlich `tests/utils/env_loader.py` statt `src/utils/env_loader.py` lädt.

## Aufgabe
- Ersetze in `src/auth/meteo_token_provider.py` den relativen Import von `env_loader` durch einen absoluten Import:

  from src.utils.env_loader import get_required_env_var

- Prüfe alle weiteren Importe in `meteo_token_provider.py` auf inkonsistente Importpfade.
- Stelle sicher, dass alle Tests (insbesondere `test_meteo_token_provider.py`) weiterhin grün laufen.

## Qualitätskriterien
- Keine relative oder implizite Import-Auflösung, die mit `tests/` kollidieren kann.
- Robuste Ausführung in CLI, Tests und bei Deployment.