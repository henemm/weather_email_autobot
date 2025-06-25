import os
import yaml
try:
    from utils.env_loader import get_required_env_var
except ImportError:
    from ..utils.env_loader import get_required_env_var

def load_config(path: str = "config.yaml") -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Konfigurationsdatei '{path}' nicht gefunden.")

    with open(path, "r", encoding="utf-8") as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML konnte nicht geladen werden: {e}")

    for key in ["startdatum", "thresholds", "smtp"]:
        if key not in config:
            raise KeyError(f"Pflichtfeld '{key}' fehlt in config.yaml")

    smtp_pw = get_required_env_var("GMAIL_APP_PW")

    config["smtp"]["password"] = smtp_pw

    return config