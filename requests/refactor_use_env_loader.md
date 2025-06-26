# Refactor: Einheitliche Nutzung von env_loader für Umgebungsvariablen

## Ziel  
Sichere, konsistente und testbare Verwendung von Umgebungsvariablen durch Migration von direktem `os.getenv()` Zugriff auf ein zentrales Utility.

## Hintergrund  
In Tests trat ein schwer zu diagnostizierender Fehler auf, weil die `.env`-Datei nicht über `load_dotenv(override=True)` geladen wurde.  
Dieses Verhalten ist riskant und schwer zu debuggen, wenn `os.getenv()` im Code direkt verwendet wird.

## Aufgaben

### 1. Utility einführen (falls nicht vorhanden)

```python
# tests/utils/env_loader.py
from dotenv import load_dotenv
import os

load_dotenv(override=True)

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is not set.")
    return value
```

## 2. Refactoring

- Ersetze in allen relevanten Modulen den direkten Zugriff auf `os.getenv("...")` durch `get_env_var("...")`
- Betroffene Stellen identifizieren per:

```bash
grep -r "os\.getenv" src/
grep -r "os\.getenv" tests/
```

## 3. Ausnahmen

- Verwende `get_env_var()` **nur für eigene** `.env`-gesteuerte Konfiguration.
- **Nicht verwenden** für Systemvariablen wie `PATH`, `HOME`, `TMPDIR` etc.

## Zusätzliche Hinweise

- Das Utility lädt `.env` zentral mit `override=True`, um Shell-Werte gezielt zu überschreiben
- Das Refactoring verbessert die Testbarkeit und Transparenz massiv
- Deployment- und Produktionsumgebungen sollten `.env`-Konfiguration korrekt vorhalten, falls betroffen

## Zielstatus

- Alle Tokens (z. B. `METEOFRANCE_WCS_TOKEN`, `METEOFRANCE_BASIC_AUTH`, …) werden über `get_env_var()` bezogen
- Keine direkten `os.getenv()`-Aufrufe mehr im Projektcode für Tokens

## Tags  
refactor, env, token, dotenv, konsistenz