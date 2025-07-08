import sys
import os
import yaml
import json
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.report.weather_report_generator import generate_weather_report
from src.config.config_loader import load_config
from src.config.config_preserver import update_yaml_preserving_comments
from src.notification.email_client import EmailClient
from src.position.etappenlogik import get_current_stage

ETAPPEN_PATH = os.path.join(os.path.dirname(__file__), '../etappen.json')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config.yaml')

# Load all stages
with open(ETAPPEN_PATH, 'r', encoding='utf-8') as f:
    etappen = json.load(f)

# Load config
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Save original start date
original_start = config.get('startdatum')

# Prepare email client
email_client = EmailClient(config)

for idx, stage in enumerate(etappen):
    # Set start date so that this stage is 'today'
    today = date.today()
    stage_start = today - timedelta(days=idx)
    # Update config using comment-preserving function
    update_yaml_preserving_comments(CONFIG_PATH, 'startdatum', stage_start.strftime('%Y-%m-%d'))
    # Reload config and get current stage name
    config_reload = load_config()
    current_stage = get_current_stage(config_reload, ETAPPEN_PATH)
    stage_name = current_stage['name'] if current_stage else 'Unknown'
    print(f"[DEBUG] Processing stage {idx+1}: {stage_name} (startdatum={stage_start.strftime('%Y-%m-%d')})")
    # Generate and send evening report
    result = generate_weather_report('evening')
    if result['success']:
        print(f"[OK] Sent evening report for stage {stage_name} ({stage_start})")
        email_client.send_gr20_report(result)
    else:
        print(f"[FAIL] Could not generate report for stage {stage_name}: {result.get('error')}")

# Restore original config
if original_start:
    update_yaml_preserving_comments(CONFIG_PATH, 'startdatum', original_start)
print("All evening reports sent.") 